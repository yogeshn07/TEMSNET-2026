"""Class rebalancing (SMOTE) for the UNSW-NB15 training dataset.

Generates a SMOTE-balanced training dataset alongside the untouched
baseline, so later modelling stages (Phase D) can compare predictive
performance and per-class explanation quality between the original
imbalanced training distribution and a synthetically balanced one.

The testing dataset is never balanced, never fitted on, and never
transformed — it is copied byte-for-byte (as a Parquet round-trip)
under a new name so Phase D has one unambiguous, always-real-world
evaluation set.

Usage::

    from src.data.class_rebalancing import run_class_rebalancing

    result = run_class_rebalancing()

Design decisions
~~~~~~~~~~~~~~~~
* A method registry (:data:`_BALANCING_STRATEGIES`) dispatches on
  ``configs/rebalancing.yaml``'s ``method`` field. Only ``"smote"`` is
  registered now; adding a second method later means writing one
  function with the same signature and adding one registry entry — no
  changes to :func:`run_class_rebalancing` itself.
* Pre/post class-distribution statistics reuse
  :func:`src.data.eda.compute_class_distribution` rather than
  recomputing count/percentage/imbalance-ratio logic a second time.
* :func:`src.core.reproducibility.set_global_seed` is called before
  SMOTE fitting — this is the first genuinely stochastic stage in the
  pipeline (every prior stage was deterministic), so reproducible
  synthetic sample generation matters for IEEE reproducibility.
* Vanilla SMOTE (not SMOTENC) interpolates linearly between nearest
  neighbours across *all* features, including the ordinal-encoded
  categorical columns (``proto``, ``service``, ``state``) and other
  integer count features. This produces fractional values for columns
  that originally held only integer codes — a known, documented
  limitation of applying standard SMOTE to encoded categorical data,
  discussed in the generated report rather than silently corrected,
  since the task scope is exactly one balancing method, applied as-is.
"""

from __future__ import annotations

import platform
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.core.reproducibility import set_global_seed
from src.data.eda import compute_class_distribution
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_EXPERIMENT_CONFIG_FILENAME = "experiment.yaml"
_REBALANCING_CONFIG_FILENAME = "rebalancing.yaml"


def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME)


def _load_experiment_config() -> dict[str, Any]:
    """Load ``configs/experiment.yaml`` (for the shared ``random_seed``).

    Returns:
        Parsed experiment configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _EXPERIMENT_CONFIG_FILENAME)


def _load_rebalancing_config() -> dict[str, Any]:
    """Load ``configs/rebalancing.yaml``.

    Returns:
        Parsed rebalancing configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _REBALANCING_CONFIG_FILENAME)


# ══════════════════════════════════════════════════════════════
# Loading (Task C.4's baseline outputs — read only)
# ══════════════════════════════════════════════════════════════

def load_selected_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load Task C.4's leakage-free baseline datasets.

    Returns:
        Tuple of ``(train_df, test_df)``.

    Raises:
        FileNotFoundError: If the selected Parquet files are missing,
            with guidance to run ``scripts/07_feature_selection.py`` first.
    """
    processed_dir = get_path_manager().processed_data_dir
    train_path = processed_dir / "training_selected.parquet"
    test_path = processed_dir / "testing_selected.parquet"

    if not train_path.is_file() or not test_path.is_file():
        raise FileNotFoundError(
            "Selected baseline datasets not found. Run scripts/07_feature_selection.py first. "
            f"Expected: {train_path}, {test_path}"
        )

    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)
    logger.info("Training dataset loaded: %d rows x %d columns", len(train_df), len(train_df.columns))
    return train_df, test_df


# ══════════════════════════════════════════════════════════════
# Balancing strategy registry (extensible by design)
# ══════════════════════════════════════════════════════════════

def _run_smote_strategy(
    X: pd.DataFrame, y: pd.Series, params: dict[str, Any], random_seed: int
) -> tuple[pd.DataFrame, pd.Series]:
    """Fit and apply SMOTE to the training feature/target arrays.

    Args:
        X: Training features (numeric only — required by SMOTE's
            nearest-neighbour interpolation).
        y: Training target (multi-class labels; SMOTE supports
            non-numeric class labels directly).
        params: ``smote`` section of ``configs/rebalancing.yaml``.
        random_seed: Seed for deterministic synthetic sample generation.

    Returns:
        Tuple of ``(X_resampled, y_resampled)``.
    """
    from imblearn.over_sampling import SMOTE

    smote = SMOTE(
        sampling_strategy=params.get("sampling_strategy", "auto"),
        k_neighbors=params.get("k_neighbors", 5),
        random_state=random_seed,
    )
    logger.info(
        "SMOTE fitting — sampling_strategy=%s, k_neighbors=%s, random_seed=%d",
        smote.sampling_strategy, smote.k_neighbors, random_seed,
    )
    X_resampled, y_resampled = smote.fit_resample(X, y)
    logger.info("Synthetic sample generation complete — %d total rows after resampling", len(X_resampled))
    return X_resampled, y_resampled


#: Registry mapping method name (from configs/rebalancing.yaml) to its
#: implementation. Adding a new method means writing one function with
#: this signature and adding one entry here — no changes needed to
#: run_class_rebalancing().
_BALANCING_STRATEGIES: dict[
    str, Callable[[pd.DataFrame, pd.Series, dict[str, Any], int], tuple[pd.DataFrame, pd.Series]]
] = {
    "smote": _run_smote_strategy,
}


def apply_balancing_strategy(
    method: str, X: pd.DataFrame, y: pd.Series, params: dict[str, Any], random_seed: int
) -> tuple[pd.DataFrame, pd.Series]:
    """Dispatch to the configured balancing strategy.

    Args:
        method: Strategy name (``configs/rebalancing.yaml``'s ``method`` field).
        X: Training features.
        y: Training target.
        params: Method-specific parameters.
        random_seed: Seed for deterministic resampling.

    Returns:
        Tuple of ``(X_resampled, y_resampled)``.

    Raises:
        ValueError: If *method* is not registered.
    """
    if method not in _BALANCING_STRATEGIES:
        raise ValueError(
            f"Unknown balancing method: '{method}'. Registered methods: {list(_BALANCING_STRATEGIES)}"
        )
    return _BALANCING_STRATEGIES[method](X, y, params, random_seed)


# ══════════════════════════════════════════════════════════════
# Pre/post balancing analysis (reuses Task B.3's distribution logic)
# ══════════════════════════════════════════════════════════════

def summarize_synthetic_samples(
    before_dist: pd.DataFrame, after_dist: pd.DataFrame
) -> pd.DataFrame:
    """Compute synthetic samples generated per class.

    Args:
        before_dist: Output of :func:`src.data.eda.compute_class_distribution`
            on the original training data.
        after_dist: Same, on the SMOTE-resampled training data.

    Returns:
        ``DataFrame`` with ``class_name``, ``count_before``,
        ``count_after``, ``synthetic_samples_generated``.
    """
    merged = before_dist[["class_name", "count"]].merge(
        after_dist[["class_name", "count"]], on="class_name", suffixes=("_before", "_after")
    )
    merged["synthetic_samples_generated"] = merged["count_after"] - merged["count_before"]
    return merged


# ══════════════════════════════════════════════════════════════
# Export (data/processed/ — never overwrites Task C.4's outputs)
# ══════════════════════════════════════════════════════════════

def save_processed_dataset(df: pd.DataFrame, stem: str) -> tuple[Path, str]:
    """Save a dataset to ``data/processed/``, preferring Parquet.

    Args:
        df: DataFrame to save.
        stem: Filename without extension.

    Returns:
        Tuple of ``(resolved_path, format_used)``.
    """
    directory = get_path_manager().processed_data_dir
    directory.mkdir(parents=True, exist_ok=True)
    parquet_path = directory / f"{stem}.parquet"

    try:
        df.to_parquet(parquet_path, index=False)
        logger.info("Balanced dataset saved: %s (parquet)", parquet_path.name)
        return parquet_path, "parquet"
    except ImportError:
        csv_path = directory / f"{stem}.csv"
        df.to_csv(csv_path, index=False)
        logger.warning("Parquet engine unavailable — saved %s as CSV instead.", csv_path.name)
        return csv_path, "csv"


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_rebalancing_tables(
    before_dist: pd.DataFrame, after_dist: pd.DataFrame, synthetic_summary: pd.DataFrame
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        before_dist: Pre-balancing class distribution.
        after_dist: Post-balancing class distribution.
        synthetic_summary: Output of :func:`summarize_synthetic_samples`.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    path = tables_dir / "class_distribution_before.csv"
    before_dist.to_csv(path, index=False)
    paths["class_distribution_before"] = path

    path = tables_dir / "class_distribution_after.csv"
    after_dist.to_csv(path, index=False)
    paths["class_distribution_after"] = path

    path = tables_dir / "balancing_summary.csv"
    synthetic_summary.to_csv(path, index=False)
    paths["balancing_summary"] = path

    logger.info("Table generated: %d class rebalancing CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_rebalancing_markdown(report: dict[str, Any]) -> str:
    """Render the full class rebalancing report as Markdown.

    Args:
        report: Report dict from :func:`run_class_rebalancing`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    rarest_class = min(report["synthetic_summary"], key=lambda r: r["count_before"])
    rarest_oversampling_factor = (
        round(rarest_class["count_after"] / rarest_class["count_before"], 1)
        if rarest_class["count_before"] else "N/A"
    )
    lines: list[str] = [
        "# UNSW-NB15 Class Rebalancing Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Balancing Strategy",
        "",
        f"**Method:** {report['strategy']['method'].upper()}  ",
        f"**Parameters:** `{report['strategy']['parameters']}`  ",
        f"**Random seed:** {report['strategy']['random_seed']} (from `configs/experiment.yaml`)",
        "",
        "**Why SMOTE:** SMOTE generates synthetic minority-class samples by interpolating between "
        "real nearest neighbours within the same class, rather than duplicating existing rows "
        "(random oversampling) or discarding majority-class information (undersampling). This "
        "preserves the full training signal from the majority class while giving minority classes "
        "(down to 130 real `Worms` samples) enough synthetic density for the Phase D models to learn "
        "from, directly supporting this study's comparison of explanation quality between imbalanced "
        "and balanced training conditions.",
        "",
        "---",
        "",
        "## Why Balancing Is Applied Only to the Training Set",
        "",
        "Balancing the training set lets the model learn from a less skewed class distribution. "
        "Balancing the **testing** set would corrupt evaluation: the testing distribution must reflect "
        "the real-world class frequencies the model will face, including the genuine rarity of classes "
        "like `Worms`. Synthetically inflating test-set minority classes would make per-class metrics "
        "and SHAP explanation quality comparisons meaningless, since they would no longer measure "
        "performance against real, naturally-occurring traffic patterns.",
        "",
        "---",
        "",
        "## Pre-Balancing Analysis",
        "",
        "| Class | Count | % of Total | Imbalance Ratio |",
        "|---|---|---|---|",
    ]
    for row in report["pre_balancing"]["class_distribution"]:
        lines.append(f"| {row['class_name']} | {row['count']:,} | {row['pct']}% | {row['imbalance_ratio']} |")

    lines += [
        "",
        f"**Total training samples (before):** {report['pre_balancing']['total_rows']:,}",
        "",
        "---",
        "",
        "## Post-Balancing Analysis",
        "",
        "| Class | Count | % of Total | Imbalance Ratio |",
        "|---|---|---|---|",
    ]
    for row in report["post_balancing"]["class_distribution"]:
        lines.append(f"| {row['class_name']} | {row['count']:,} | {row['pct']}% | {row['imbalance_ratio']} |")

    lines += [
        "",
        f"**Total training samples (after):** {report['post_balancing']['total_rows']:,}  ",
        f"**Achieved balance (max imbalance ratio post-balancing):** "
        f"{report['post_balancing']['max_imbalance_ratio']}  ",
        f"**Total synthetic samples generated:** {report['post_balancing']['total_synthetic_samples']:,}",
        "",
        "### Synthetic Samples Per Class",
        "",
        "| Class | Count Before | Count After | Synthetic Generated |",
        "|---|---|---|---|",
    ]
    for row in report["synthetic_summary"]:
        lines.append(
            f"| {row['class_name']} | {row['count_before']:,} | {row['count_after']:,} | "
            f"{row['synthetic_samples_generated']:,} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Testing Dataset Integrity",
        "",
        "| Check | Result |",
        "|---|---|",
        "| SMOTE fit on testing data | Never — `fit_resample()` called only on training X/y |",
        "| Testing dataset row count | Unchanged (verified in self-tests) |",
        "| Testing dataset content | Byte-identical copy of `testing_selected.parquet` (verified via SHA-256 in self-tests) |",
        "",
        "---",
        "",
        "## Output Datasets",
        "",
        "| File | Rows | Columns | Description |",
        "|---|---|---|---|",
        f"| `training_baseline.parquet` | {report['training_baseline']['row_count']:,} | "
        f"{report['training_baseline']['column_count']} | Untouched copy of Task C.4's training_selected.parquet |",
        f"| `training_balanced_smote.parquet` | {report['training_balanced']['row_count']:,} | "
        f"{report['training_balanced']['column_count']} | SMOTE-balanced training set |",
        f"| `testing_baseline.parquet` | {report['testing_baseline']['row_count']:,} | "
        f"{report['testing_baseline']['column_count']} | Untouched copy of Task C.4's testing_selected.parquet (never balanced) |",
        "",
        "---",
        "",
        "## Limitations of Synthetic Oversampling",
        "",
        "- **Fractional encoded-categorical values:** vanilla SMOTE (not SMOTENC) interpolates linearly "
        "across *all* features, including the ordinal-encoded `proto`/`service`/`state` columns and "
        "integer count features. Synthetic rows can therefore contain fractional values for columns "
        "that originally held only integer codes (e.g. a synthetic `proto` value between two real "
        "category codes), which do not correspond to any real category. This is a known property of "
        "applying standard SMOTE to encoded categorical data, not a defect in this implementation.",
        f"- **Extreme oversampling ratio for the rarest class:** `{rarest_class['class_name']}` is "
        f"synthesised from only {rarest_class['count_before']:,} real training examples up to the "
        f"majority class count, an oversampling factor of roughly {rarest_oversampling_factor}x. "
        "With so few real neighbours, SMOTE's interpolated samples span a much smaller region of "
        "feature space than the true population likely occupies, risking overly narrow synthetic "
        "diversity for this class.",
        "- **No guarantee of semantic realism:** SMOTE operates purely in encoded feature space; it has "
        "no awareness of valid network-flow semantics, so synthetic samples are not guaranteed to "
        "represent physically plausible traffic, only statistically plausible interpolations.",
        "",
        "---",
        "",
        "## Class Rebalancing Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"The training set ({report['pre_balancing']['total_rows']:,} rows, imbalance ratio up to "
        f"{report['pre_balancing']['max_imbalance_ratio']}x) was balanced using SMOTE "
        f"(sampling_strategy=\"{report['strategy']['parameters'].get('sampling_strategy', 'auto')}\", "
        f"k_neighbors={report['strategy']['parameters'].get('k_neighbors', 5)}, "
        f"random_state={report['strategy']['random_seed']}), generating "
        f"{report['post_balancing']['total_synthetic_samples']:,} synthetic samples and producing a "
        f"final balanced training set of {report['post_balancing']['total_rows']:,} rows "
        f"(imbalance ratio = {report['post_balancing']['max_imbalance_ratio']}). The testing set "
        f"({report['testing_baseline']['row_count']:,} rows) was never balanced, fitted on, or "
        "transformed, preserving its real-world class distribution for unbiased evaluation. Both the "
        "original imbalanced training set and the SMOTE-balanced training set are retained as parallel "
        "experimental conditions for Phase D's predictive performance and explanation-quality comparison.",
        "",
        "---",
        "*End of Class Rebalancing Report*",
    ]
    return "\n".join(lines) + "\n"


def save_rebalancing_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the class rebalancing report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_class_rebalancing`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "class_rebalancing_report.json", json_safe)
    md_path = write_text(reports_dir / "class_rebalancing_report.md", _render_rebalancing_markdown(report))
    logger.info("Reports generated: %s, %s", json_path.name, md_path.name)
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_class_rebalancing() -> dict[str, Any]:
    """Run the full class rebalancing pipeline.

    Loads Task C.4's baseline datasets, balances the training split
    only (via the configured strategy — SMOTE), saves the baseline
    copies and the balanced training set to ``data/processed/``, and
    writes reports/tables. The testing split is copied verbatim and
    never balanced, fitted on, or transformed.

    Returns:
        Dict with ``strategy``, ``pre_balancing``, ``post_balancing``,
        ``synthetic_summary``, dataset path/shape info, and ``summary``.
    """
    logger.info("Balancing started")

    dataset_cfg = _load_dataset_config()
    experiment_cfg = _load_experiment_config()
    rebalancing_cfg = _load_rebalancing_config()

    target_column = dataset_cfg.get("target_column", "attack_cat")
    random_seed = experiment_cfg.get("random_seed", 42)
    method = rebalancing_cfg.get("method", "smote")
    method_params = rebalancing_cfg.get(method, {})

    set_global_seed(random_seed)

    train_df, test_df = load_selected_datasets()

    before_dist = compute_class_distribution(train_df, target_column)
    pre_balancing = {
        "class_distribution": before_dist.to_dict(orient="records"),
        "total_rows": len(train_df),
        "max_imbalance_ratio": float(before_dist["imbalance_ratio"].max()),
    }
    logger.info(
        "Pre-balancing: %d rows, max imbalance ratio = %.2f",
        pre_balancing["total_rows"], pre_balancing["max_imbalance_ratio"],
    )

    X_train = train_df.drop(columns=[target_column])
    y_train = train_df[target_column]

    X_resampled, y_resampled = apply_balancing_strategy(method, X_train, y_train, method_params, random_seed)
    balanced_df = X_resampled.copy()
    balanced_df[target_column] = y_resampled.values
    balanced_df = balanced_df[train_df.columns]

    after_dist = compute_class_distribution(balanced_df, target_column)
    post_balancing = {
        "class_distribution": after_dist.to_dict(orient="records"),
        "total_rows": len(balanced_df),
        "max_imbalance_ratio": float(after_dist["imbalance_ratio"].max()),
        "total_synthetic_samples": len(balanced_df) - len(train_df),
    }
    logger.info(
        "Post-balancing: %d rows (%d synthetic), max imbalance ratio = %.2f",
        post_balancing["total_rows"], post_balancing["total_synthetic_samples"], post_balancing["max_imbalance_ratio"],
    )

    synthetic_summary_df = summarize_synthetic_samples(before_dist, after_dist)

    train_baseline_path, train_format = save_processed_dataset(train_df, "training_baseline")
    train_balanced_path, _ = save_processed_dataset(balanced_df, "training_balanced_smote")
    test_baseline_path, _ = save_processed_dataset(test_df, "testing_baseline")

    save_rebalancing_tables(before_dist, after_dist, synthetic_summary_df)

    summary = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "strategy": {"method": method, "parameters": method_params, "random_seed": random_seed},
        "pre_balancing": pre_balancing,
        "post_balancing": post_balancing,
        "synthetic_summary": synthetic_summary_df.to_dict(orient="records"),
        "training_baseline": {
            "output_path": str(train_baseline_path), "row_count": len(train_df), "column_count": len(train_df.columns),
        },
        "training_balanced": {
            "output_path": str(train_balanced_path), "row_count": len(balanced_df), "column_count": len(balanced_df.columns),
        },
        "testing_baseline": {
            "output_path": str(test_baseline_path), "row_count": len(test_df), "column_count": len(test_df.columns),
        },
        "output_format": train_format,
        "summary": summary,
    }
    save_rebalancing_report(report)

    logger.info(
        "Balancing completed — %d synthetic samples, training: %d -> %d rows, testing unchanged at %d rows",
        post_balancing["total_synthetic_samples"], len(train_df), len(balanced_df), len(test_df),
    )
    return report
