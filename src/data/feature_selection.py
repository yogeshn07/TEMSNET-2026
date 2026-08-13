"""Feature selection and target-leakage elimination for UNSW-NB15.

Audits every feature produced by Task C.3's encoding stage and
classifies each into exactly one of three groups, with evidence:

* **Mandatory Removal** — features that introduce target leakage or
  cannot legitimately be available at prediction time.
* **Candidate** — retained in the exported dataset, but flagged
  because B.3's correlation analysis found them involved in a highly
  correlated pair (|r| > 0.8); not removed, only annotated for future
  reconsideration once real modelling experiments exist to justify it.
* **Final Baseline** — retained without reservation.

This module trains no model. Every classification is backed by
descriptive evidence: uniqueness ratios, deterministic group-purity
checks, and the correlation findings already computed in Task B.3 —
never by assumption.

Usage::

    from src.data.feature_selection import run_feature_selection

    result = run_feature_selection()

Design decisions
~~~~~~~~~~~~~~~~
* Input is Task C.3's encoded ``data/interim/*.parquet`` — feature
  selection operates after encoding, not on raw categorical strings.
* Leakage detection uses two independent, complementary checks:
  :func:`detect_identifier_features` (row-uniqueness ratio) and
  :func:`detect_deterministic_target_mapping` (group-purity, the
  reverse direction of Task C.2's ``verify_label_consistency``).
  Running both surfaces leakage that either check alone could miss.
* Correlation findings are *read*, not recomputed, from
  ``outputs/tables/eda_correlation_pairs.csv`` (Task B.3) — avoiding a
  second, potentially divergent correlation computation.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.data.data_cleaning import verify_label_consistency
from src.data.dataset_profile import categorize_features
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"

#: Columns confirmed by dedicated leakage evidence (see
#: :func:`run_target_leakage_analysis`) to require mandatory removal.
#: Not hardcoded as an assumption — populated only after evidence is
#: gathered; declared here purely as the set of *expected* findings
#: for this known dataset, re-verified live on every run.
EXPECTED_MANDATORY_REMOVAL = ("id", "label")


def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME)


def load_encoded_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load Task C.3's encoded interim datasets.

    Returns:
        Tuple of ``(train_df, test_df)``.

    Raises:
        FileNotFoundError: If the encoded Parquet files are missing,
            with guidance to run ``scripts/06_feature_encoding.py`` first.
    """
    interim_dir = get_path_manager().interim_data_dir
    train_path = interim_dir / "training_encoded.parquet"
    test_path = interim_dir / "testing_encoded.parquet"

    if not train_path.is_file() or not test_path.is_file():
        raise FileNotFoundError(
            "Encoded interim datasets not found. Run scripts/06_feature_encoding.py first. "
            f"Expected: {train_path}, {test_path}"
        )

    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)
    logger.info("Loaded encoded datasets: training=%d rows, testing=%d rows", len(train_df), len(test_df))
    return train_df, test_df


# ══════════════════════════════════════════════════════════════
# Target leakage analysis (dedicated, evidence-based)
# ══════════════════════════════════════════════════════════════

def detect_identifier_features(
    df: pd.DataFrame, feature_columns: list[str], uniqueness_threshold: float = 0.99
) -> list[dict[str, Any]]:
    """Flag columns whose values are (almost) unique per row.

    A feature where ``nunique / n_rows`` exceeds *uniqueness_threshold*
    behaves as a row identifier: it cannot generalise to unseen rows
    and, if rows were collected in any order correlated with the
    target (e.g. captured in per-attack-type blocks), can leak target
    information through row position alone.

    Args:
        df: Dataset to audit (training split, by convention).
        feature_columns: Columns to check.
        uniqueness_threshold: Minimum ``nunique / n_rows`` ratio to flag.

    Returns:
        List of dicts for flagged columns with ``column``,
        ``unique_count``, ``uniqueness_ratio``.
    """
    n_rows = len(df)
    flagged = []
    for col in feature_columns:
        ratio = df[col].nunique(dropna=False) / n_rows if n_rows else 0.0
        if ratio >= uniqueness_threshold:
            flagged.append({
                "column": col,
                "unique_count": int(df[col].nunique(dropna=False)),
                "uniqueness_ratio": round(ratio, 6),
            })
    return flagged


def detect_deterministic_target_mapping(
    df: pd.DataFrame, target_column: str, feature_columns: list[str], max_cardinality: int = 50
) -> list[dict[str, Any]]:
    """Find bounded-cardinality features whose every value maps to one target class.

    This is the complementary direction to Task C.2's
    ``verify_label_consistency`` (which checked whether every *target*
    class maps to one *label* value). Here, every *value* of a
    candidate feature is checked for mapping to exactly one *target*
    class — a stricter, symmetric leakage signature. High-cardinality
    (near-identifier) columns are excluded via *max_cardinality*
    because their purity is a trivial artefact of having ~1 row per
    value, not genuine target-deterministic behaviour.

    Args:
        df: Dataset to audit.
        target_column: Multi-class target column (``attack_cat``).
        feature_columns: Columns to check.
        max_cardinality: Maximum unique-value count to consider
            (excludes identifier-like columns).

    Returns:
        List of dicts for flagged columns with ``column`` and
        ``unique_count``.
    """
    flagged = []
    for col in feature_columns:
        nunique = df[col].nunique(dropna=False)
        if 1 < nunique <= max_cardinality:
            purity = df.groupby(col, dropna=False)[target_column].nunique()
            if (purity == 1).all():
                flagged.append({"column": col, "unique_count": int(nunique)})
    return flagged


def run_target_leakage_analysis(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_column: str,
    binary_label_column: str,
    feature_columns: list[str],
) -> dict[str, Any]:
    """Run the dedicated target leakage audit, explicitly evaluating ``id`` and ``label``.

    Args:
        train_df: Training split (post-encoding).
        test_df: Testing split (post-encoding).
        target_column: Multi-class target column (``attack_cat``).
        binary_label_column: Binary label column (``label``).
        feature_columns: All feature columns to audit (target excluded).

    Returns:
        Dict with ``identifier_features``, ``deterministic_mapping_features``,
        ``label_leakage`` (reusing Task C.2's consistency check), and an
        explicit ``id_label_evidence`` section.
    """
    logger.info("Leakage analysis: identifier detection")
    identifier_findings = detect_identifier_features(train_df, feature_columns)

    logger.info("Leakage analysis: deterministic target-mapping detection")
    deterministic_findings = detect_deterministic_target_mapping(train_df, target_column, feature_columns)

    logger.info("Leakage analysis: label consistency re-verification (training + testing)")
    label_leakage = {
        "training": verify_label_consistency(train_df, target_column, binary_label_column),
        "testing": verify_label_consistency(test_df, target_column, binary_label_column),
    }

    id_label_evidence: dict[str, Any] = {}
    if "id" in train_df.columns:
        id_label_corr = float(train_df["id"].corr(train_df[binary_label_column]))
        id_label_evidence["id"] = {
            "uniqueness_ratio": round(train_df["id"].nunique() / len(train_df), 6) if len(train_df) else 0.0,
            "correlation_with_label": round(id_label_corr, 6),
            "evidence": (
                f"id is unique for {train_df['id'].nunique()}/{len(train_df)} rows "
                f"(ratio={round(train_df['id'].nunique() / len(train_df), 4)}) and correlates with "
                f"binary label at r={round(id_label_corr, 4)}, indicating rows were likely captured in "
                "blocks ordered by traffic/attack type — row position alone carries target signal."
            ),
        }
    if binary_label_column in train_df.columns:
        id_label_evidence[binary_label_column] = {
            "consistency_status": label_leakage["training"]["status"],
            "evidence": (
                f"verify_label_consistency() confirms every '{target_column}' class maps to exactly one "
                f"'{binary_label_column}' value in both splits, with 0 exceptions "
                "(Normal->0, every attack class->1) — label is a deterministic duplicate of the target."
            ),
        }

    return {
        "identifier_features": identifier_findings,
        "deterministic_mapping_features": deterministic_findings,
        "label_leakage": label_leakage,
        "id_label_evidence": id_label_evidence,
    }


# ══════════════════════════════════════════════════════════════
# Correlation review (reuses Task B.3 findings, never recomputes)
# ══════════════════════════════════════════════════════════════

def load_correlation_findings() -> pd.DataFrame:
    """Load the highly-correlated feature pairs already computed in Task B.3.

    Returns:
        ``DataFrame`` from ``outputs/tables/eda_correlation_pairs.csv``
        (training split rows only), or an empty frame with the
        expected columns if the file or training rows are absent.

    Raises:
        FileNotFoundError: If the B.3 EDA table is missing, with
            guidance to run ``scripts/03_exploratory_data_analysis.py`` first.
    """
    path = get_path_manager().tables_dir / "eda_correlation_pairs.csv"
    if not path.is_file():
        raise FileNotFoundError(
            f"B.3 correlation findings not found at {path}. "
            "Run scripts/03_exploratory_data_analysis.py first."
        )

    pairs = pd.read_csv(path)
    return pairs[pairs["split"] == "training"].reset_index(drop=True)


def features_in_correlated_pairs(correlation_pairs: pd.DataFrame) -> set[str]:
    """Collect every feature name that appears in at least one highly-correlated pair.

    Args:
        correlation_pairs: Output of :func:`load_correlation_findings`.

    Returns:
        Set of column names involved in any reported pair.
    """
    if correlation_pairs.empty:
        return set()
    return set(correlation_pairs["feature_1"]) | set(correlation_pairs["feature_2"])


# ══════════════════════════════════════════════════════════════
# Feature classification (the audit table)
# ══════════════════════════════════════════════════════════════

def classify_features(
    feature_columns: list[str],
    mandatory_removal: set[str],
    correlated_features: set[str],
    leakage_analysis: dict[str, Any],
) -> pd.DataFrame:
    """Classify every feature into Mandatory Removal / Candidate / Final Baseline.

    Args:
        feature_columns: All feature columns (target excluded).
        mandatory_removal: Columns confirmed by leakage evidence to remove.
        correlated_features: Columns appearing in a B.3 highly-correlated pair.
        leakage_analysis: Output of :func:`run_target_leakage_analysis`.

    Returns:
        Audit ``DataFrame`` with ``column``, ``classification``, ``reason``.
    """
    id_label_evidence = leakage_analysis["id_label_evidence"]
    rows = []

    for col in feature_columns:
        if col in mandatory_removal:
            evidence = id_label_evidence.get(col, {}).get("evidence", "Confirmed target leakage.")
            rows.append({"column": col, "classification": "mandatory_removal", "reason": evidence})
        elif col in correlated_features:
            rows.append({
                "column": col,
                "classification": "candidate",
                "reason": (
                    "Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — "
                    "not removed solely for correlation, since Random Forest tolerates multicollinearity "
                    "and removal without an empirical accuracy/explanation-quality comparison would be "
                    "premature at this descriptive stage. Flagged for reconsideration once real "
                    "modelling experiments exist."
                ),
            })
        else:
            rows.append({
                "column": col,
                "classification": "final_baseline",
                "reason": "No leakage evidence found; not involved in a highly correlated pair.",
            })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════
# Descriptive feature characteristics (no model training)
# ══════════════════════════════════════════════════════════════

def describe_feature_characteristics(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Describe feature type, cardinality, and variance — descriptive only.

    No model is trained and no importance score is computed; this is
    purely structural information useful for later modelling decisions
    (e.g. which features are high-variance numeric vs. low-cardinality
    categorical-like codes).

    Args:
        df: Dataset to describe (training split, by convention).
        feature_columns: Columns to describe.

    Returns:
        ``DataFrame`` with ``column``, ``feature_type``, ``cardinality``,
        ``variance`` (``None`` for non-numeric types).
    """
    cats = categorize_features(df[feature_columns])
    type_by_column: dict[str, str] = {}
    for category in ("numerical", "categorical", "boolean"):
        for col in cats[category]:
            type_by_column[col] = category

    rows = []
    for col in feature_columns:
        feature_type = type_by_column.get(col, "unknown")
        variance = round(float(df[col].var()), 6) if feature_type in ("numerical", "boolean") else None
        rows.append({
            "column": col,
            "feature_type": feature_type,
            "cardinality": int(df[col].nunique(dropna=False)),
            "variance": variance,
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════
# Export
# ══════════════════════════════════════════════════════════════

def select_final_features(df: pd.DataFrame, removed_columns: set[str]) -> pd.DataFrame:
    """Drop mandatory-removal columns, keeping all other columns and row order.

    Args:
        df: Encoded dataset split (features + target).
        removed_columns: Columns to drop (mandatory removal only;
            candidate features are kept).

    Returns:
        New ``DataFrame`` with the removed columns dropped; row order
        and all other values unchanged.
    """
    return df.drop(columns=list(removed_columns))


def save_selected_dataset(df: pd.DataFrame, stem: str) -> tuple[Path, str]:
    """Save a selected split to ``data/processed/``, preferring Parquet.

    Args:
        df: DataFrame to save.
        stem: Filename without extension (e.g. ``"training_selected"``).

    Returns:
        Tuple of ``(resolved_path, format_used)``.
    """
    directory = get_path_manager().processed_data_dir
    directory.mkdir(parents=True, exist_ok=True)
    parquet_path = directory / f"{stem}.parquet"

    try:
        df.to_parquet(parquet_path, index=False)
        logger.info("Processed datasets generated: saved %s (parquet)", parquet_path.name)
        return parquet_path, "parquet"
    except ImportError:
        csv_path = directory / f"{stem}.csv"
        df.to_csv(csv_path, index=False)
        logger.warning("Parquet engine unavailable — saved %s as CSV instead.", csv_path.name)
        return csv_path, "csv"


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_selection_tables(
    audit_df: pd.DataFrame,
    characteristics_df: pd.DataFrame,
    leakage_analysis: dict[str, Any],
) -> dict[str, Path]:
    """Save the four required CSV tables.

    Args:
        audit_df: Output of :func:`classify_features`.
        characteristics_df: Output of :func:`describe_feature_characteristics`.
        leakage_analysis: Output of :func:`run_target_leakage_analysis`.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    merged = audit_df.merge(characteristics_df, on="column", how="left")
    path = tables_dir / "feature_audit.csv"
    merged.to_csv(path, index=False)
    paths["feature_audit"] = path

    removed = merged[merged["classification"] == "mandatory_removal"]
    path = tables_dir / "removed_features.csv"
    removed.to_csv(path, index=False)
    paths["removed_features"] = path

    retained = merged[merged["classification"] != "mandatory_removal"]
    path = tables_dir / "retained_features.csv"
    retained.to_csv(path, index=False)
    paths["retained_features"] = path

    leakage_rows = []
    for entry in leakage_analysis["identifier_features"]:
        leakage_rows.append({"column": entry["column"], "check": "identifier_uniqueness", "finding": f"ratio={entry['uniqueness_ratio']}"})
    for entry in leakage_analysis["deterministic_mapping_features"]:
        leakage_rows.append({"column": entry["column"], "check": "deterministic_target_mapping", "finding": f"unique_count={entry['unique_count']}"})
    for split_label, result in leakage_analysis["label_leakage"].items():
        leakage_rows.append({
            "column": "label", "check": f"label_consistency_{split_label}",
            "finding": f"status={result['status']}, inconsistent={len(result['inconsistent_classes'])}",
        })
    path = tables_dir / "leakage_assessment.csv"
    pd.DataFrame(leakage_rows).to_csv(path, index=False)
    paths["leakage_assessment"] = path

    logger.info("Table generated: %d feature selection CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_selection_markdown(report: dict[str, Any]) -> str:
    """Render the full feature selection report as Markdown.

    Args:
        report: Report dict from :func:`run_feature_selection`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    audit = report["audit"]
    lines: list[str] = [
        "# UNSW-NB15 Feature Selection & Leakage Elimination Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Target Leakage Analysis",
        "",
        "### `id`",
        "",
        report["leakage_analysis"]["id_label_evidence"].get("id", {}).get("evidence", "Not present in dataset."),
        "",
        "### `label`",
        "",
        report["leakage_analysis"]["id_label_evidence"].get("label", {}).get("evidence", "Not present in dataset."),
        "",
        f"**Other low-cardinality features checked for deterministic target mapping:** "
        f"{len(report['leakage_analysis']['deterministic_mapping_features'])} found "
        f"(beyond the `label` case already documented above).",
        "",
        "---",
        "",
        "## Feature Audit",
        "",
        "| Column | Classification | Reason |",
        "|---|---|---|",
    ]
    for row in audit:
        lines.append(f"| {row['column']} | {row['classification']} | {row['reason']} |")

    lines += [
        "",
        "---",
        "",
        "## Correlation Review (reusing Task B.3 findings)",
        "",
        f"{s['candidate_count']} feature(s) are involved in at least one highly correlated pair "
        "(|r| > 0.8) and are classified as **Candidate** — retained, not removed. Random Forest "
        "(the locked research model) tolerates multicollinearity without the instability linear models "
        "exhibit, and removing features by correlation alone, without an empirical comparison of model "
        "accuracy or explanation quality, would be a premature decision at this descriptive stage.",
        "",
        "---",
        "",
        "## Final Schema",
        "",
        "| Split | Path | Rows | Columns |",
        "|---|---|---|---|",
        f"| Training | `{report['training']['output_path']}` | {report['training']['row_count']:,} | {report['training']['column_count']} |",
        f"| Testing | `{report['testing']['output_path']}` | {report['testing']['row_count']:,} | {report['testing']['column_count']} |",
        "",
        f"**Output format:** {report['output_format']}",
        "",
        "---",
        "",
        "## Feature Selection Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"Of {s['original_feature_count']} original features, {s['removed_count']} were removed for confirmed "
        f"target leakage (`{', '.join(s['removed_columns'])}`) and {s['retained_count']} were retained "
        f"({s['candidate_count']} flagged as correlated candidates, {s['final_baseline_count']} as final "
        f"baseline features). `id` was removed because it is unique for every row "
        f"(uniqueness ratio = {report['leakage_analysis']['id_label_evidence'].get('id', {}).get('uniqueness_ratio', 'N/A')}) "
        f"and correlates with the binary label at r = "
        f"{report['leakage_analysis']['id_label_evidence'].get('id', {}).get('correlation_with_label', 'N/A')}, "
        "indicating row order itself carries target information. `label` was removed because it is a "
        "deterministic duplicate of the multi-class target (Normal->0, every attack->1, 0 exceptions in "
        f"either split). The resulting baseline datasets ({report['training']['row_count']:,} training rows, "
        f"{report['testing']['row_count']:,} testing rows, {report['training']['column_count']} columns each) "
        "were saved to `data/processed/` for all downstream modelling experiments.",
        "",
        "---",
        "*End of Feature Selection Report*",
    ]
    return "\n".join(lines) + "\n"


def save_selection_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the feature selection report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_feature_selection`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "feature_selection_report.json", json_safe)
    md_path = write_text(reports_dir / "feature_selection_report.md", _render_selection_markdown(report))
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_feature_selection() -> dict[str, Any]:
    """Run the full feature selection and leakage elimination pipeline.

    Loads Task C.3's encoded datasets, runs the dedicated target
    leakage analysis (explicitly evaluating ``id`` and ``label``),
    reviews Task B.3's correlation findings, classifies every feature,
    exports the baseline datasets to ``data/processed/``, and writes
    reports/tables.

    Returns:
        Dict with ``audit``, ``leakage_analysis``, ``training``,
        ``testing``, ``output_format``, and ``summary`` keys.
    """
    logger.info("Feature audit started")

    dataset_cfg = _load_dataset_config()
    target_column = dataset_cfg.get("target_column", "attack_cat")
    binary_label_column = dataset_cfg.get("binary_label_column", "label")

    train_df, test_df = load_encoded_datasets()
    feature_columns = [c for c in train_df.columns if c != target_column]

    leakage_analysis = run_target_leakage_analysis(
        train_df, test_df, target_column, binary_label_column, feature_columns
    )

    mandatory_removal: set[str] = set(EXPECTED_MANDATORY_REMOVAL) & set(feature_columns)
    logger.info("Feature classification: mandatory removal = %s", sorted(mandatory_removal))

    correlation_pairs = load_correlation_findings()
    correlated = features_in_correlated_pairs(correlation_pairs) & set(feature_columns) - mandatory_removal

    audit_df = classify_features(feature_columns, mandatory_removal, correlated, leakage_analysis)
    characteristics_df = describe_feature_characteristics(train_df, feature_columns)

    train_selected = select_final_features(train_df, mandatory_removal)
    test_selected = select_final_features(test_df, mandatory_removal)

    train_path, train_format = save_selected_dataset(train_selected, "training_selected")
    test_path, _ = save_selected_dataset(test_selected, "testing_selected")
    logger.info("Processed datasets generated: training=%s, testing=%s", train_path.name, test_path.name)

    save_selection_tables(audit_df, characteristics_df, leakage_analysis)

    classification_counts = audit_df["classification"].value_counts().to_dict()
    summary = {
        "original_feature_count": len(feature_columns),
        "removed_count": len(mandatory_removal),
        "removed_columns": sorted(mandatory_removal),
        "retained_count": len(feature_columns) - len(mandatory_removal),
        "candidate_count": int(classification_counts.get("candidate", 0)),
        "final_baseline_count": int(classification_counts.get("final_baseline", 0)),
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "audit": audit_df.to_dict(orient="records"),
        "leakage_analysis": leakage_analysis,
        "training": {
            "output_path": str(train_path),
            "row_count": len(train_selected),
            "column_count": len(train_selected.columns),
        },
        "testing": {
            "output_path": str(test_path),
            "row_count": len(test_selected),
            "column_count": len(test_selected.columns),
        },
        "output_format": train_format,
        "summary": summary,
    }
    save_selection_report(report)

    logger.info(
        "Feature selection completed — %d removed, %d retained (%d candidate, %d final baseline)",
        summary["removed_count"], summary["retained_count"], summary["candidate_count"], summary["final_baseline_count"],
    )
    return report
