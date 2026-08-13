"""Dual Random Forest baseline for the UNSW-NB15 imbalance study.

Trains two completely independent ``RandomForestClassifier`` models
with **identical hyperparameters**, differing only in their training
distribution:

* **Model A (baseline)** — trained on ``training_baseline.parquet``
  (the original, imbalanced training distribution).
* **Model B (SMOTE)** — trained on ``training_balanced_smote.parquet``
  (the SMOTE-balanced training distribution from Task C.5).

Both are evaluated on the exact same, never-balanced
``testing_baseline.parquet``, so any difference in their metrics is
attributable only to the training distribution, not to a confound
such as different hyperparameters or different test data.

This task trains and evaluates only — no hyperparameter tuning, no
explainability analysis. Those are explicitly out of scope here.

Usage::

    from src.models.random_forest import run_random_forest_baseline

    result = run_random_forest_baseline()

Design decisions
~~~~~~~~~~~~~~~~
* Hyperparameters are loaded once from ``configs/model.yaml`` and
  passed identically to both training calls — there is no code path
  that could let the two models diverge in configuration, which would
  confound the baseline-vs-balanced comparison this task exists to set up.
* ``random_state`` is read from ``configs/experiment.yaml`` (the
  project's single source of truth for the seed), not duplicated.
* Evaluation logic (:func:`evaluate_model`) is written once and
  called twice — for Model A and Model B — rather than duplicated,
  so both experiments are scored by identical code.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.core.reproducibility import set_global_seed
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_EXPERIMENT_CONFIG_FILENAME = "experiment.yaml"
_MODEL_CONFIG_FILENAME = "model.yaml"
_FIGURE_DPI = 300


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


def _load_model_config() -> dict[str, Any]:
    """Load ``configs/model.yaml``.

    Returns:
        Parsed model configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _MODEL_CONFIG_FILENAME)


# ══════════════════════════════════════════════════════════════
# Loading (Task C.5's processed datasets — read only)
# ══════════════════════════════════════════════════════════════

def load_experiment_datasets() -> dict[str, pd.DataFrame]:
    """Load the three datasets required for the dual-experiment design.

    Returns:
        Dict with keys ``training_baseline``, ``training_smote``,
        ``testing_baseline``, each a loaded ``DataFrame``.

    Raises:
        FileNotFoundError: If any required Parquet file is missing,
            with guidance to run ``scripts/08_class_rebalancing.py`` first.
    """
    processed_dir = get_path_manager().processed_data_dir
    paths = {
        "training_baseline": processed_dir / "training_baseline.parquet",
        "training_smote": processed_dir / "training_balanced_smote.parquet",
        "testing_baseline": processed_dir / "testing_baseline.parquet",
    }

    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "Required experiment datasets not found: " + ", ".join(missing) +
            ". Run scripts/08_class_rebalancing.py first."
        )

    datasets = {name: pd.read_parquet(path) for name, path in paths.items()}
    logger.info(
        "Dataset loaded — training_baseline=%d rows, training_smote=%d rows, testing_baseline=%d rows",
        len(datasets["training_baseline"]), len(datasets["training_smote"]), len(datasets["testing_baseline"]),
    )
    return datasets


def split_features_target(df: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, pd.Series]:
    """Separate features (X) from the target (y).

    Args:
        df: Loaded dataset.
        target_column: Column to extract as the target.

    Returns:
        Tuple of ``(X, y)``.
    """
    return df.drop(columns=[target_column]), df[target_column]


# ══════════════════════════════════════════════════════════════
# Training
# ══════════════════════════════════════════════════════════════

def train_random_forest(
    X_train: pd.DataFrame, y_train: pd.Series, params: dict[str, Any], random_state: int
) -> RandomForestClassifier:
    """Fit a ``RandomForestClassifier`` with the given configuration.

    Args:
        X_train: Training features.
        y_train: Training target.
        params: ``random_forest`` section of ``configs/model.yaml``.
        random_state: Seed for deterministic tree construction.

    Returns:
        Fitted ``RandomForestClassifier``.
    """
    model = RandomForestClassifier(
        n_estimators=params.get("n_estimators", 100),
        max_depth=params.get("max_depth"),
        min_samples_split=params.get("min_samples_split", 2),
        min_samples_leaf=params.get("min_samples_leaf", 1),
        max_features=params.get("max_features", "sqrt"),
        n_jobs=params.get("n_jobs", -1),
        random_state=random_state,
    )
    logger.info(
        "Model fitting — n_estimators=%d, max_depth=%s, max_features=%s, training rows=%d",
        model.n_estimators, model.max_depth, model.max_features, len(X_train),
    )
    model.fit(X_train, y_train)
    return model


# ══════════════════════════════════════════════════════════════
# Evaluation (single implementation, called for both experiments)
# ══════════════════════════════════════════════════════════════

def evaluate_model(
    model: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series, class_labels: list[str]
) -> dict[str, Any]:
    """Evaluate a fitted model on the (shared, untouched) testing set.

    Args:
        model: Fitted ``RandomForestClassifier``.
        X_test: Testing features.
        y_test: Testing target.
        class_labels: Ordered class names, used consistently for the
            confusion matrix and per-class metric ordering.

    Returns:
        Dict with ``accuracy``, ``macro``/``weighted`` precision-recall-f1,
        ``per_class`` metrics, and ``confusion_matrix`` (as a nested list).
    """
    y_pred = model.predict(X_test)
    logger.info("Prediction completed — %d test rows scored", len(y_pred))

    # classification_report's return type is a str|dict union in sklearn's
    # stubs; output_dict=True guarantees a dict at runtime (verified
    # empirically), so this cast resolves the stub's overload ambiguity.
    report = cast(
        dict[str, Any],
        classification_report(y_test, y_pred, labels=class_labels, output_dict=True, zero_division=0),
    )

    per_class = [
        {
            "class_name": cls,
            "precision": round(report[cls]["precision"], 6),
            "recall": round(report[cls]["recall"], 6),
            "f1_score": round(report[cls]["f1-score"], 6),
            "support": int(report[cls]["support"]),
        }
        for cls in class_labels
    ]

    cm = confusion_matrix(y_test, y_pred, labels=class_labels)

    result = {
        "accuracy": round(report["accuracy"], 6),
        "macro_precision": round(report["macro avg"]["precision"], 6),
        "macro_recall": round(report["macro avg"]["recall"], 6),
        "macro_f1": round(report["macro avg"]["f1-score"], 6),
        "weighted_precision": round(report["weighted avg"]["precision"], 6),
        "weighted_recall": round(report["weighted avg"]["recall"], 6),
        "weighted_f1": round(report["weighted avg"]["f1-score"], 6),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "class_labels": class_labels,
    }
    logger.info(
        "Evaluation completed — accuracy=%.4f, macro_f1=%.4f, weighted_f1=%.4f",
        result["accuracy"], result["macro_f1"], result["weighted_f1"],
    )
    return result


# ══════════════════════════════════════════════════════════════
# Model persistence
# ══════════════════════════════════════════════════════════════

def save_model(model: RandomForestClassifier, filename: str) -> Path:
    """Save a fitted model to ``outputs/models/`` via joblib.

    Args:
        model: Fitted ``RandomForestClassifier``.
        filename: Filename including extension (e.g. ``"random_forest_baseline.joblib"``).

    Returns:
        Resolved path of the saved model file.
    """
    models_dir = get_path_manager().models_dir
    models_dir.mkdir(parents=True, exist_ok=True)
    path = models_dir / filename
    joblib.dump(model, path)
    logger.info("Model saved: %s", path.name)
    return path


# ══════════════════════════════════════════════════════════════
# Confusion matrix figure (publication quality)
# ══════════════════════════════════════════════════════════════

def _set_publication_style() -> None:
    """Apply consistent, IEEE-ready matplotlib defaults."""
    plt.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelweight": "bold",
        "savefig.dpi": _FIGURE_DPI,
        "savefig.bbox": "tight",
    })


def plot_confusion_matrix(
    cm: list[list[int]], class_labels: list[str], title: str, save_path: Path
) -> Path:
    """Plot a publication-quality confusion matrix heatmap.

    Args:
        cm: Confusion matrix as a nested list (rows = true class,
            columns = predicted class), in *class_labels* order.
        class_labels: Ordered class names for tick labels.
        title: Figure title.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    cm_array = np.array(cm)
    n = len(class_labels)

    fig, ax = plt.subplots(figsize=(max(8, n * 0.9), max(7, n * 0.8)))
    im = ax.imshow(cm_array, cmap="Blues")

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(class_labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(class_labels, fontsize=9)
    ax.set_xlabel("Predicted Class")
    ax.set_ylabel("True Class")
    ax.set_title(title)

    threshold = cm_array.max() / 2 if cm_array.max() > 0 else 0
    for i in range(n):
        for j in range(n):
            value = cm_array[i, j]
            color = "white" if value > threshold else "black"
            ax.text(j, i, f"{value:,}", ha="center", va="center", color=color, fontsize=8)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Instance Count")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def _metrics_to_dataframe(result: dict[str, Any]) -> pd.DataFrame:
    """Flatten one experiment's evaluation result into a tidy table.

    Args:
        result: Output of :func:`evaluate_model`.

    Returns:
        ``DataFrame`` with one overall-metrics row followed by one row
        per class.
    """
    rows = [{
        "scope": "overall",
        "class_name": "ALL",
        "accuracy": result["accuracy"],
        "precision": result["macro_precision"],
        "recall": result["macro_recall"],
        "f1_score": result["macro_f1"],
        "support": sum(c["support"] for c in result["per_class"]),
        "average_type": "macro",
    }, {
        "scope": "overall",
        "class_name": "ALL",
        "accuracy": result["accuracy"],
        "precision": result["weighted_precision"],
        "recall": result["weighted_recall"],
        "f1_score": result["weighted_f1"],
        "support": sum(c["support"] for c in result["per_class"]),
        "average_type": "weighted",
    }]
    for c in result["per_class"]:
        rows.append({
            "scope": "per_class",
            "class_name": c["class_name"],
            "accuracy": None,
            "precision": c["precision"],
            "recall": c["recall"],
            "f1_score": c["f1_score"],
            "support": c["support"],
            "average_type": None,
        })
    return pd.DataFrame(rows)


def save_experiment_tables(
    baseline_result: dict[str, Any], smote_result: dict[str, Any]
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        baseline_result: Output of :func:`evaluate_model` for Model A.
        smote_result: Output of :func:`evaluate_model` for Model B.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    path = tables_dir / "metrics_baseline.csv"
    _metrics_to_dataframe(baseline_result).to_csv(path, index=False)
    paths["metrics_baseline"] = path

    path = tables_dir / "metrics_smote.csv"
    _metrics_to_dataframe(smote_result).to_csv(path, index=False)
    paths["metrics_smote"] = path

    comparison_rows = []
    baseline_by_class = {c["class_name"]: c for c in baseline_result["per_class"]}
    smote_by_class = {c["class_name"]: c for c in smote_result["per_class"]}
    for class_name in baseline_result["class_labels"]:
        b, s = baseline_by_class[class_name], smote_by_class[class_name]
        comparison_rows.append({
            "class_name": class_name,
            "precision_baseline": b["precision"], "precision_smote": s["precision"],
            "recall_baseline": b["recall"], "recall_smote": s["recall"],
            "f1_baseline": b["f1_score"], "f1_smote": s["f1_score"],
            "support_baseline": b["support"], "support_smote": s["support"],
        })
    path = tables_dir / "class_metrics_comparison.csv"
    pd.DataFrame(comparison_rows).to_csv(path, index=False)
    paths["class_metrics_comparison"] = path

    logger.info("Table generated: %d Random Forest CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_rf_markdown(report: dict[str, Any]) -> str:
    """Render the full Random Forest baseline report as Markdown.

    Args:
        report: Report dict from :func:`run_random_forest_baseline`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    cfg = report["model_config"]
    lines: list[str] = [
        "# UNSW-NB15 Random Forest Baseline Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Why Random Forest",
        "",
        "Random Forest is the locked model choice for this study (established in the research design "
        "prior to this implementation phase): it handles the mixed numeric/ordinal-encoded feature space "
        "without requiring scaling, tolerates the multicollinearity documented in Task C.4's correlation "
        "review without instability, and supports SHAP's TreeExplainer for exact, efficient explanation "
        "computation in the upcoming Phase E — a combination linear models and most other classifiers "
        "do not offer simultaneously.",
        "",
        "## Why Identical Hyperparameters",
        "",
        "Both models are configured from the exact same `configs/model.yaml` dictionary, loaded once and "
        "passed unchanged to both training calls. This isolates the training distribution (original vs. "
        "SMOTE-balanced) as the only experimental variable — any difference in Model A's and Model B's "
        "metrics is therefore attributable to class balancing alone, not to a hyperparameter confound.",
        "",
        "## Why the Testing Dataset Remains Unchanged",
        "",
        "Both models are evaluated on the identical `testing_baseline.parquet` (Task C.5's untouched, "
        "never-balanced copy of the real-world test distribution). Using any other test set, or balancing "
        "it, would invalidate the comparison this experiment exists to produce.",
        "",
        "## Why Two Independent Models",
        "",
        "A single model cannot answer \"does class balancing change predictive behaviour and (later) "
        "explanation quality?\" — that requires training two models that differ in exactly one respect "
        "(their training data) and comparing them under identical evaluation conditions.",
        "",
        "---",
        "",
        "## Model Configuration",
        "",
        "| Parameter | Value |",
        "|---|---|",
    ]
    for key, value in cfg.items():
        lines.append(f"| {key} | {value} |")

    lines += [
        "",
        "---",
        "",
        "## Dataset Sizes",
        "",
        "| Dataset | Rows | Columns |",
        "|---|---|---|",
        f"| Training (baseline) | {report['datasets']['training_baseline_rows']:,} | {report['datasets']['feature_count'] + 1} |",
        f"| Training (SMOTE-balanced) | {report['datasets']['training_smote_rows']:,} | {report['datasets']['feature_count'] + 1} |",
        f"| Testing (shared, untouched) | {report['datasets']['testing_rows']:,} | {report['datasets']['feature_count'] + 1} |",
        "",
        "---",
        "",
        "## Experiment A — Baseline Model Metrics",
        "",
        "| Metric | Macro | Weighted |",
        "|---|---|---|",
        f"| Precision | {report['baseline']['macro_precision']} | {report['baseline']['weighted_precision']} |",
        f"| Recall | {report['baseline']['macro_recall']} | {report['baseline']['weighted_recall']} |",
        f"| F1-score | {report['baseline']['macro_f1']} | {report['baseline']['weighted_f1']} |",
        "",
        f"**Accuracy:** {report['baseline']['accuracy']}",
        "",
        "### Per-Class Metrics (Baseline)",
        "",
        "| Class | Precision | Recall | F1-score | Support |",
        "|---|---|---|---|---|",
    ]
    for c in report["baseline"]["per_class"]:
        lines.append(f"| {c['class_name']} | {c['precision']} | {c['recall']} | {c['f1_score']} | {c['support']} |")

    lines += [
        "",
        "---",
        "",
        "## Experiment B — SMOTE-Balanced Model Metrics",
        "",
        "| Metric | Macro | Weighted |",
        "|---|---|---|",
        f"| Precision | {report['smote']['macro_precision']} | {report['smote']['weighted_precision']} |",
        f"| Recall | {report['smote']['macro_recall']} | {report['smote']['weighted_recall']} |",
        f"| F1-score | {report['smote']['macro_f1']} | {report['smote']['weighted_f1']} |",
        "",
        f"**Accuracy:** {report['smote']['accuracy']}",
        "",
        "### Per-Class Metrics (SMOTE)",
        "",
        "| Class | Precision | Recall | F1-score | Support |",
        "|---|---|---|---|---|",
    ]
    for c in report["smote"]["per_class"]:
        lines.append(f"| {c['class_name']} | {c['precision']} | {c['recall']} | {c['f1_score']} | {c['support']} |")

    lines += [
        "",
        "---",
        "",
        "## High-Level Comparison",
        "",
        "| Metric | Baseline | SMOTE | Delta |",
        "|---|---|---|---|",
        f"| Accuracy | {report['baseline']['accuracy']} | {report['smote']['accuracy']} | "
        f"{round(report['smote']['accuracy'] - report['baseline']['accuracy'], 6)} |",
        f"| Macro F1 | {report['baseline']['macro_f1']} | {report['smote']['macro_f1']} | "
        f"{round(report['smote']['macro_f1'] - report['baseline']['macro_f1'], 6)} |",
        f"| Weighted F1 | {report['baseline']['weighted_f1']} | {report['smote']['weighted_f1']} | "
        f"{round(report['smote']['weighted_f1'] - report['baseline']['weighted_f1'], 6)} |",
        "",
        "*(No claim of \"better\"/\"worse\" is made here — accuracy optimisation and model comparison "
        "are explicitly out of scope for this task; per-class explanation quality, the actual research "
        "question, is addressed in Phase E.)*",
        "",
        "---",
        "",
        "## Random Forest Baseline Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"Two `RandomForestClassifier` models were trained with identical hyperparameters "
        f"(n_estimators={cfg.get('n_estimators')}, max_depth={cfg.get('max_depth')}, "
        f"max_features={cfg.get('max_features')}, random_state={cfg.get('random_state')}): "
        f"Model A on the original imbalanced training set ({report['datasets']['training_baseline_rows']:,} rows) "
        f"and Model B on the SMOTE-balanced training set ({report['datasets']['training_smote_rows']:,} rows). "
        f"Both were evaluated on the identical, untouched testing set "
        f"({report['datasets']['testing_rows']:,} rows). Model A achieved {report['baseline']['accuracy']:.4f} "
        f"accuracy (macro F1 = {report['baseline']['macro_f1']:.4f}); Model B achieved "
        f"{report['smote']['accuracy']:.4f} accuracy (macro F1 = {report['smote']['macro_f1']:.4f}). "
        "No hyperparameter tuning, accuracy optimisation, or explainability analysis was performed at "
        "this stage; per-class explanation quality is addressed in Phase E.",
        "",
        "---",
        "*End of Random Forest Baseline Report*",
    ]
    return "\n".join(lines) + "\n"


def save_rf_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the Random Forest baseline report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_random_forest_baseline`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "random_forest_report.json", json_safe)
    md_path = write_text(reports_dir / "random_forest_report.md", _render_rf_markdown(report))
    logger.info("Reports generated: %s, %s", json_path.name, md_path.name)
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_random_forest_baseline() -> dict[str, Any]:
    """Train and evaluate both Random Forest experiments.

    Trains Model A on the original imbalanced training set and
    Model B on the SMOTE-balanced training set, using identical
    hyperparameters. Both are evaluated on the same, untouched
    testing set, loaded exactly once and reused for both evaluation
    calls — structurally preventing any test-set divergence between
    the two experiments.

    Returns:
        Dict with ``model_config``, ``datasets``, ``baseline``,
        ``smote`` (evaluation results), and ``summary`` keys.
    """
    logger.info("Training started")

    dataset_cfg = _load_dataset_config()
    experiment_cfg = _load_experiment_config()
    model_cfg = _load_model_config()

    target_column = dataset_cfg.get("target_column", "attack_cat")
    random_seed = experiment_cfg.get("random_seed", 42)
    rf_params = model_cfg.get("random_forest", {})

    set_global_seed(random_seed)

    datasets = load_experiment_datasets()
    X_train_baseline, y_train_baseline = split_features_target(datasets["training_baseline"], target_column)
    X_train_smote, y_train_smote = split_features_target(datasets["training_smote"], target_column)
    X_test, y_test = split_features_target(datasets["testing_baseline"], target_column)

    class_labels = sorted(y_test.unique().tolist())

    model_a = train_random_forest(X_train_baseline, y_train_baseline, rf_params, random_seed)
    model_b = train_random_forest(X_train_smote, y_train_smote, rf_params, random_seed)

    baseline_result = evaluate_model(model_a, X_test, y_test, class_labels)
    smote_result = evaluate_model(model_b, X_test, y_test, class_labels)

    models_dir = get_path_manager().models_dir
    save_model(model_a, "random_forest_baseline.joblib")
    save_model(model_b, "random_forest_smote.joblib")

    figures_dir = get_path_manager().figures_dir
    plot_confusion_matrix(
        baseline_result["confusion_matrix"], class_labels,
        "Random Forest (Baseline Training) — Confusion Matrix",
        figures_dir / "confusion_matrix_baseline.png",
    )
    plot_confusion_matrix(
        smote_result["confusion_matrix"], class_labels,
        "Random Forest (SMOTE-Balanced Training) — Confusion Matrix",
        figures_dir / "confusion_matrix_smote.png",
    )

    save_experiment_tables(baseline_result, smote_result)

    summary = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "model_config": {**rf_params, "random_state": random_seed},
        "datasets": {
            "training_baseline_rows": len(X_train_baseline),
            "training_smote_rows": len(X_train_smote),
            "testing_rows": len(X_test),
            "feature_count": X_test.shape[1],
        },
        "baseline": baseline_result,
        "smote": smote_result,
        "summary": summary,
    }
    save_rf_report(report)

    logger.info(
        "Training completed — baseline accuracy=%.4f, smote accuracy=%.4f, models saved to %s",
        baseline_result["accuracy"], smote_result["accuracy"], models_dir,
    )
    return report
