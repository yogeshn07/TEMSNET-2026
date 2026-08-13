"""Prediction repository — the shared foundation for SHAP and LIME.

Loads the two trained Random Forest models from Task D.1 and the
shared testing set, generates predictions (no retraining, no
hyperparameter changes), and archives them as a frozen, reproducible
record. This repository — not a fresh call to ``model.predict()`` —
is what every future explainability task (E.2 SHAP, E.3 LIME) must
read from.

Usage::

    from src.models.prediction_repository import run_prediction_repository

    result = run_prediction_repository()

Why a prediction archive, not live inference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Comparing SHAP and LIME explanation quality requires holding the
explained predictions constant. If SHAP and LIME each called
``model.predict()`` independently, any difference between them could
be confounded by floating-point non-determinism, library version
drift, or accidental row reordering — not a genuine difference in
explanation fidelity. Archiving predictions once, here, and having
both downstream tasks read the same Parquet files removes that
confound structurally: SHAP and LIME explain literally the same
``sample_id`` -> prediction pairs, sourced from one file, not two
separate inference runs that merely *should* agree.

Why no retraining
~~~~~~~~~~~~~~~~~~
Retraining (even with the same hyperparameters and seed) would risk
producing different trees due to environment-level nondeterminism
(thread scheduling in scikit-learn's parallel tree building can affect
floating-point summation order). Loading the exact joblib artifacts
Task D.1 already produced and evaluated guarantees the models being
explained in Phase E are byte-identical to the ones whose metrics are
already reported — not a refit that merely approximates them.

Reproducibility guarantee
~~~~~~~~~~~~~~~~~~~~~~~~~~
``sample_id``/``row_index`` are derived from ``testing_baseline.parquet``'s
row position, which has been provably stable (never sorted, shuffled,
or filtered) since Task C.1 first separated X/y. The same row always
gets the same ``sample_id`` on every run, so SHAP and LIME tasks can
join their explanation outputs back to this repository by ID with no
ambiguity.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"


def _load_dataset_config() -> dict[str, Any]:
    """Load ``configs/dataset.yaml``.

    Returns:
        Parsed dataset configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _DATASET_CONFIG_FILENAME)


# ══════════════════════════════════════════════════════════════
# Loading (Task D.1's models, Task C.5's testing set — read only)
# ══════════════════════════════════════════════════════════════

def load_models() -> tuple[RandomForestClassifier, RandomForestClassifier]:
    """Load the two trained Random Forest models from Task D.1, without retraining.

    Returns:
        Tuple of ``(model_baseline, model_smote)``.

    Raises:
        FileNotFoundError: If either ``.joblib`` file is missing, with
            guidance to run ``scripts/09_random_forest_baseline.py`` first.
    """
    models_dir = get_path_manager().models_dir
    baseline_path = models_dir / "random_forest_baseline.joblib"
    smote_path = models_dir / "random_forest_smote.joblib"

    missing = [str(p) for p in (baseline_path, smote_path) if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "Required trained models not found: " + ", ".join(missing) +
            ". Run scripts/09_random_forest_baseline.py first."
        )

    model_baseline = joblib.load(baseline_path)
    model_smote = joblib.load(smote_path)
    logger.info("Models loaded — baseline and smote, no retraining performed")
    return model_baseline, model_smote


def load_testing_data() -> pd.DataFrame:
    """Load the shared, untouched testing set from Task C.5.

    Returns:
        Testing ``DataFrame`` (features + target).

    Raises:
        FileNotFoundError: If the Parquet file is missing, with
            guidance to run ``scripts/08_class_rebalancing.py`` first.
    """
    path = get_path_manager().processed_data_dir / "testing_baseline.parquet"
    if not path.is_file():
        raise FileNotFoundError(
            f"Testing dataset not found at {path}. Run scripts/08_class_rebalancing.py first."
        )
    test_df = pd.read_parquet(path)
    logger.info("Testing dataset loaded: %d rows x %d columns", len(test_df), len(test_df.columns))
    return test_df


# ══════════════════════════════════════════════════════════════
# Prediction generation (read-only — never modifies a prediction)
# ══════════════════════════════════════════════════════════════

def generate_predictions(
    model: RandomForestClassifier, test_df: pd.DataFrame, target_column: str, model_label: str
) -> pd.DataFrame:
    """Run inference once and archive every output field, unmodified.

    Args:
        model: Loaded (already-trained) ``RandomForestClassifier``.
        test_df: Testing set (features + target).
        target_column: Name of the target column.
        model_label: ``"baseline"`` or ``"smote"`` (for logging only).

    Returns:
        ``DataFrame`` with ``sample_id``, ``row_index``, ``true_label``,
        ``predicted_class``, ``confidence``, and one ``prob_<class>``
        column per class (ordered by ``model.classes_``).
    """
    X_test = test_df.drop(columns=[target_column])
    y_test = test_df[target_column]

    predicted_class = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    confidence = probabilities.max(axis=1)
    logger.info("Predictions generated (%s): %d rows scored", model_label, len(predicted_class))

    n_rows = len(test_df)
    records: dict[str, Any] = {
        "sample_id": [f"SAMPLE_{i:06d}" for i in range(n_rows)],
        "row_index": np.arange(n_rows),
        "true_label": y_test.to_numpy(),
        "predicted_class": predicted_class,
        "confidence": np.round(confidence, 6),
    }
    for class_idx, class_name in enumerate(model.classes_):
        records[f"prob_{class_name}"] = np.round(probabilities[:, class_idx], 6)

    return pd.DataFrame(records)


# ══════════════════════════════════════════════════════════════
# Sample registry (the cross-reference SHAP/LIME must reuse)
# ══════════════════════════════════════════════════════════════

def create_sample_registry(
    baseline_predictions: pd.DataFrame, smote_predictions: pd.DataFrame
) -> pd.DataFrame:
    """Build the stable sample registry shared by SHAP and LIME.

    Args:
        baseline_predictions: Output of :func:`generate_predictions` for Model A.
        smote_predictions: Output of :func:`generate_predictions` for Model B.

    Returns:
        ``DataFrame`` with ``sample_id``, ``row_index``, ``true_class``,
        ``predicted_class_baseline``, ``predicted_class_smote``.

    Raises:
        ValueError: If the two prediction sets do not share identical
            ``sample_id``/``true_label`` values (which would indicate
            they were not scored against the same testing rows).
    """
    if not (baseline_predictions["sample_id"] == smote_predictions["sample_id"]).all():
        raise ValueError("Baseline and SMOTE predictions do not share identical sample_id ordering")
    if not (baseline_predictions["true_label"] == smote_predictions["true_label"]).all():
        raise ValueError("Baseline and SMOTE predictions do not share identical true labels — different test sets?")

    return pd.DataFrame({
        "sample_id": baseline_predictions["sample_id"],
        "row_index": baseline_predictions["row_index"],
        "true_class": baseline_predictions["true_label"],
        "predicted_class_baseline": baseline_predictions["predicted_class"],
        "predicted_class_smote": smote_predictions["predicted_class"],
    })


# ══════════════════════════════════════════════════════════════
# Export
# ══════════════════════════════════════════════════════════════

def save_prediction_dataset(df: pd.DataFrame, stem: str) -> tuple[Path, str]:
    """Save a prediction dataset to ``outputs/predictions/``, preferring Parquet.

    Args:
        df: DataFrame to save.
        stem: Filename without extension.

    Returns:
        Tuple of ``(resolved_path, format_used)``.
    """
    directory = get_path_manager().project_root / "outputs" / "predictions"
    directory.mkdir(parents=True, exist_ok=True)
    parquet_path = directory / f"{stem}.parquet"

    try:
        df.to_parquet(parquet_path, index=False)
        return parquet_path, "parquet"
    except ImportError:
        csv_path = directory / f"{stem}.csv"
        df.to_csv(csv_path, index=False)
        logger.warning("Parquet engine unavailable — saved %s as CSV instead.", csv_path.name)
        return csv_path, "csv"


# ══════════════════════════════════════════════════════════════
# Analysis (descriptive only — no SHAP/LIME, no feature importance)
# ══════════════════════════════════════════════════════════════

def compute_confidence_statistics(predictions: pd.DataFrame, model_label: str) -> dict[str, Any]:
    """Compute overall and per-class confidence-score statistics.

    Args:
        predictions: Output of :func:`generate_predictions`.
        model_label: ``"baseline"`` or ``"smote"``.

    Returns:
        Dict with ``model``, ``overall`` stats, and ``per_class`` stats.
    """
    overall = {
        "mean": round(float(predictions["confidence"].mean()), 6),
        "median": round(float(predictions["confidence"].median()), 6),
        "std": round(float(predictions["confidence"].std()), 6),
        "min": round(float(predictions["confidence"].min()), 6),
        "max": round(float(predictions["confidence"].max()), 6),
    }

    per_class = []
    for class_name, group in predictions.groupby("predicted_class"):
        per_class.append({
            "class_name": class_name,
            "count": int(len(group)),
            "mean_confidence": round(float(group["confidence"].mean()), 6),
            "min_confidence": round(float(group["confidence"].min()), 6),
            "max_confidence": round(float(group["confidence"].max()), 6),
        })

    return {"model": model_label, "overall": overall, "per_class": per_class}


def compute_prediction_agreement(
    baseline_predictions: pd.DataFrame, smote_predictions: pd.DataFrame
) -> dict[str, Any]:
    """Compute how often the two models predict the same class for the same sample.

    Args:
        baseline_predictions: Output of :func:`generate_predictions` for Model A.
        smote_predictions: Output of :func:`generate_predictions` for Model B.

    Returns:
        Dict with overall agreement rate and a per-true-class breakdown.
    """
    agree_mask = baseline_predictions["predicted_class"].to_numpy() == smote_predictions["predicted_class"].to_numpy()
    n_total = len(agree_mask)
    overall_agreement = round(float(agree_mask.sum() / n_total), 6) if n_total else 0.0

    per_class = []
    true_labels = baseline_predictions["true_label"]
    for class_name in sorted(true_labels.unique()):
        class_mask = (true_labels == class_name).to_numpy()
        class_total = int(class_mask.sum())
        class_agree = int((agree_mask & class_mask).sum())
        per_class.append({
            "true_class": class_name,
            "total_samples": class_total,
            "agreement_count": class_agree,
            "agreement_rate": round(class_agree / class_total, 6) if class_total else 0.0,
        })

    return {
        "overall_agreement_rate": overall_agreement,
        "total_samples": n_total,
        "agreement_count": int(agree_mask.sum()),
        "disagreement_count": int(n_total - agree_mask.sum()),
        "per_class": per_class,
    }


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_repository_tables(
    baseline_predictions: pd.DataFrame,
    smote_predictions: pd.DataFrame,
    baseline_confidence: dict[str, Any],
    smote_confidence: dict[str, Any],
    agreement: dict[str, Any],
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        baseline_predictions: Output of :func:`generate_predictions` for Model A.
        smote_predictions: Output of :func:`generate_predictions` for Model B.
        baseline_confidence: Output of :func:`compute_confidence_statistics` (baseline).
        smote_confidence: Output of :func:`compute_confidence_statistics` (smote).
        agreement: Output of :func:`compute_prediction_agreement`.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    summary_rows = []
    for label, preds in (("baseline", baseline_predictions), ("smote", smote_predictions)):
        for class_name, group in preds.groupby("predicted_class"):
            summary_rows.append({
                "model": label, "predicted_class": class_name, "count": int(len(group)),
                "mean_confidence": round(float(group["confidence"].mean()), 6),
            })
    path = tables_dir / "prediction_summary.csv"
    pd.DataFrame(summary_rows).to_csv(path, index=False)
    paths["prediction_summary"] = path

    path = tables_dir / "prediction_agreement.csv"
    pd.DataFrame(agreement["per_class"]).to_csv(path, index=False)
    paths["prediction_agreement"] = path

    conf_rows = []
    for stats in (baseline_confidence, smote_confidence):
        for entry in stats["per_class"]:
            conf_rows.append({"model": stats["model"], **entry})
    path = tables_dir / "confidence_statistics.csv"
    pd.DataFrame(conf_rows).to_csv(path, index=False)
    paths["confidence_statistics"] = path

    logger.info("Table generated: %d prediction repository CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_repository_markdown(report: dict[str, Any]) -> str:
    """Render the full prediction repository report as Markdown.

    Args:
        report: Report dict from :func:`run_prediction_repository`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    agreement = report["agreement"]
    lines: list[str] = [
        "# UNSW-NB15 Prediction Repository Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Why Predictions Are Archived",
        "",
        "SHAP (Task E.2) and LIME (Task E.3) must explain *exactly* the same predictions to make their "
        "explanation-quality comparison valid. Archiving inference output once, here, removes any "
        "possibility that the two methods silently explain different samples due to independent "
        "inference calls, library version drift, or row-order differences.",
        "",
        "## Why No Retraining Was Performed",
        "",
        "Both models are loaded via `joblib.load()` from Task D.1's saved artifacts and used only for "
        "`.predict()` / `.predict_proba()` calls. Retraining — even with identical hyperparameters and "
        "seed — risks producing different trees due to environment-level floating-point nondeterminism "
        "in parallel tree construction. Loading the exact saved models guarantees Phase E explains the "
        "same models whose metrics are already reported in Task D.1.",
        "",
        "## Reproducibility Guarantee",
        "",
        "`sample_id` and `row_index` are derived from `testing_baseline.parquet`'s row position, which "
        "has been stable and unmodified since Task C.1. The same `sample_id` always refers to the same "
        "underlying network-flow record on every run, so SHAP and LIME outputs (produced in later tasks) "
        "can be joined back to this repository unambiguously.",
        "",
        "---",
        "",
        "## Repository Contents",
        "",
        "| File | Rows | Description |",
        "|---|---|---|",
        f"| `baseline_predictions.{report['output_format']}` | {report['baseline_count']:,} | Model A predictions |",
        f"| `smote_predictions.{report['output_format']}` | {report['smote_count']:,} | Model B predictions |",
        f"| `sample_registry.{report['output_format']}` | {report['baseline_count']:,} | Cross-reference for SHAP/LIME |",
        "",
        "---",
        "",
        "## Class Distribution (Testing Set, shared by both models)",
        "",
        "| Class | Count |",
        "|---|---|",
    ]
    for row in report["class_distribution"]:
        lines.append(f"| {row['class_name']} | {row['count']:,} |")

    lines += [
        "",
        "---",
        "",
        "## Confidence Statistics",
        "",
        "| Model | Mean | Median | Std | Min | Max |",
        "|---|---|---|---|---|---|",
    ]
    for stats in (report["baseline_confidence"], report["smote_confidence"]):
        o = stats["overall"]
        lines.append(f"| {stats['model']} | {o['mean']} | {o['median']} | {o['std']} | {o['min']} | {o['max']} |")

    lines += [
        "",
        "---",
        "",
        "## Prediction Agreement Between Models",
        "",
        f"**Overall agreement rate:** {agreement['overall_agreement_rate']} "
        f"({agreement['agreement_count']:,} / {agreement['total_samples']:,} samples)  ",
        f"**Disagreement count:** {agreement['disagreement_count']:,}",
        "",
        "| True Class | Total | Agreement Count | Agreement Rate |",
        "|---|---|---|---|",
    ]
    for row in agreement["per_class"]:
        lines.append(
            f"| {row['true_class']} | {row['total_samples']:,} | {row['agreement_count']:,} | {row['agreement_rate']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Prediction Repository Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"Predictions from both Random Forest models (Task D.1) were archived against the shared, "
        f"untouched testing set ({report['baseline_count']:,} samples), without retraining either model. "
        f"Each archived record includes the predicted class, full per-class probability vector, "
        f"confidence score (maximum predicted probability), true label, and a stable sample identifier. "
        f"The two models agreed on {agreement['agreement_count']:,} of {agreement['total_samples']:,} "
        f"predictions ({agreement['overall_agreement_rate']:.4f} agreement rate). This repository — not "
        "live inference — is the single source of truth subsequent SHAP (Task E.2) and LIME (Task E.3) "
        "explainability analyses will read from, ensuring both methods explain identical predictions.",
        "",
        "---",
        "*End of Prediction Repository Report*",
    ]
    return "\n".join(lines) + "\n"


def save_repository_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the prediction repository report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_prediction_repository`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "prediction_repository_report.json", json_safe)
    md_path = write_text(reports_dir / "prediction_repository_report.md", _render_repository_markdown(report))
    logger.info("Reports generated: %s, %s", json_path.name, md_path.name)
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_prediction_repository() -> dict[str, Any]:
    """Run the full prediction repository pipeline.

    Loads both trained models (no retraining) and the shared testing
    set, generates predictions for both, builds the sample registry,
    exports everything to ``outputs/predictions/``, and writes
    reports/tables.

    Returns:
        Dict with ``baseline_count``, ``smote_count``, ``output_format``,
        ``class_distribution``, ``baseline_confidence``,
        ``smote_confidence``, ``agreement``, and ``summary`` keys.
    """
    dataset_cfg = _load_dataset_config()
    target_column = dataset_cfg.get("target_column", "attack_cat")

    model_baseline, model_smote = load_models()
    test_df = load_testing_data()

    baseline_predictions = generate_predictions(model_baseline, test_df, target_column, "baseline")
    smote_predictions = generate_predictions(model_smote, test_df, target_column, "smote")

    registry = create_sample_registry(baseline_predictions, smote_predictions)

    baseline_path, output_format = save_prediction_dataset(baseline_predictions, "baseline_predictions")
    smote_path, _ = save_prediction_dataset(smote_predictions, "smote_predictions")
    registry_path, _ = save_prediction_dataset(registry, "sample_registry")
    logger.info(
        "Repository exported: %s, %s, %s", baseline_path.name, smote_path.name, registry_path.name,
    )

    class_distribution = [
        {"class_name": name, "count": int(count)}
        for name, count in test_df[target_column].value_counts().sort_values(ascending=False).items()
    ]

    baseline_confidence = compute_confidence_statistics(baseline_predictions, "baseline")
    smote_confidence = compute_confidence_statistics(smote_predictions, "smote")
    agreement = compute_prediction_agreement(baseline_predictions, smote_predictions)

    save_repository_tables(baseline_predictions, smote_predictions, baseline_confidence, smote_confidence, agreement)

    summary = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "baseline_count": len(baseline_predictions),
        "smote_count": len(smote_predictions),
        "output_format": output_format,
        "class_distribution": class_distribution,
        "baseline_confidence": baseline_confidence,
        "smote_confidence": smote_confidence,
        "agreement": agreement,
        "summary": summary,
    }
    save_repository_report(report)

    logger.info(
        "Prediction repository completed — %d predictions archived per model, agreement=%.4f",
        len(baseline_predictions), agreement["overall_agreement_rate"],
    )
    return report
