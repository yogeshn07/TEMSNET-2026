"""SHAP explainability analysis for the dual Random Forest baseline.

Generates SHAP (SHapley Additive exPlanations) values for both
Task D.1 models against one fixed, deterministic evaluation subset
derived from Task E.1's prediction repository, so the same exact
samples are explained for both the imbalanced-trained and
SMOTE-trained models.

This module is read-only with respect to every prior artefact: it
loads the already-trained models and already-archived predictions,
computes SHAP values, and writes new files under ``outputs/shap/`` —
it never retrains, never modifies a prediction, and never touches
LIME (Task E.3 builds on this module's fixed sample subset, but is
implemented separately).

Usage::

    from src.explainability.shap_analysis import run_shap_analysis

    result = run_shap_analysis()

Why TreeExplainer
~~~~~~~~~~~~~~~~~~
``shap.TreeExplainer`` computes *exact* Shapley values for tree
ensembles in polynomial time by exploiting the tree structure
directly (Lundberg et al., 2018) — unlike model-agnostic SHAP
explainers (e.g. ``KernelExplainer``), it requires no sampling
approximation and no background dataset, and unlike LIME's local
surrogate-model approach, its attributions are guaranteed to satisfy
the Shapley efficiency property (they sum exactly to the prediction
minus the expected value). This makes it the appropriate, standard
choice for explaining the Random Forest models trained in Task D.1.

Why identical sample IDs are required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This study compares attribution patterns between a model trained on
imbalanced data and one trained on SMOTE-balanced data. If the two
models were explained on different samples, any observed difference
in attributions could be confounded by *which rows* were explained
rather than reflecting a genuine difference caused by the training
distribution. Fixing one sample_id set — selected once, from the
Task E.1 prediction repository, before either model's SHAP values are
computed — removes that confound structurally.

Why the prediction repository is reused
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Correctness/incorrectness labels for sample selection must reflect
the exact predictions already reported in Task D.1's metrics and
Task E.1's agreement analysis — recomputing predictions here would
risk drift (e.g. a different scikit-learn thread count producing a
marginally different probability near a decision boundary) and would
duplicate logic that Task E.1 already implemented and tested.

Limitations of SHAP (see also the generated report)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* SHAP attributions are local to the specific model and dataset they
  were computed from; they describe what the model learned, not a
  causal relationship between a feature and the true outcome.
* Multi-class attributions here are summarised by averaging
  ``|SHAP value|`` across the 10 output classes for the global summary
  and bar plots — this loses per-class directionality, a deliberate,
  documented simplification for producing exactly the two plot types
  requested (see :func:`plot_shap_summary` and :func:`plot_shap_bar`).
* TreeExplainer's "tree_path_dependent" attributions assume feature
  independence implicitly encoded by the tree's split structure; for
  highly correlated features (several pairs were documented as
  "Candidate" features in Task C.4), attribution can be split between
  correlated features in a way that does not necessarily reflect a
  unique causal feature.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.core.reproducibility import set_global_seed
from src.models.prediction_repository import load_models, load_testing_data
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_EXPERIMENT_CONFIG_FILENAME = "experiment.yaml"
_EXPLAINABILITY_CONFIG_FILENAME = "explainability.yaml"
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


def _load_explainability_config() -> dict[str, Any]:
    """Load ``configs/explainability.yaml``.

    Returns:
        Parsed explainability configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _EXPLAINABILITY_CONFIG_FILENAME)


def load_sample_registry() -> pd.DataFrame:
    """Load Task E.1's sample registry.

    Returns:
        Registry ``DataFrame`` with ``sample_id``, ``row_index``,
        ``true_class``, ``predicted_class_baseline``,
        ``predicted_class_smote``.

    Raises:
        FileNotFoundError: If the registry is missing, with guidance
            to run ``scripts/10_prediction_repository.py`` first.
    """
    predictions_dir = get_path_manager().project_root / "outputs" / "predictions"
    path = predictions_dir / "sample_registry.parquet"
    if not path.is_file():
        raise FileNotFoundError(
            f"Sample registry not found at {path}. Run scripts/10_prediction_repository.py first."
        )
    registry = pd.read_parquet(path)
    logger.info("Sample registry loaded: %d rows", len(registry))
    return registry


# ══════════════════════════════════════════════════════════════
# Deterministic sample selection
# ══════════════════════════════════════════════════════════════

def select_evaluation_subset(
    registry: pd.DataFrame,
    correct_per_class: int,
    incorrect_per_class: int,
    random_seed: int,
) -> list[str]:
    """Select one fixed, reproducible sample_id subset for both models.

    For every true class, selects up to *correct_per_class*
    correctly-classified and up to *incorrect_per_class*
    misclassified samples, using the **baseline model's** predictions
    as the single correctness criterion (so the resulting sample_id
    set is unambiguous and identical when later used to explain the
    SMOTE model too). Selection within each bucket uses a seeded
    shuffle, not file order, then takes a deterministic prefix — so
    the subset is reproducible but not biased toward rows that happen
    to appear first in the testing set.

    Because every true class is visited, the subset structurally
    includes both minority classes (e.g. ``Worms``, 44 total testing
    samples) and majority classes (e.g. ``Normal``, 37,000 samples).

    Args:
        registry: Output of :func:`load_sample_registry`.
        correct_per_class: Maximum correctly-classified samples per class.
        incorrect_per_class: Maximum misclassified samples per class.
        random_seed: Seed for the within-bucket shuffle.

    Returns:
        Sorted list of selected ``sample_id`` strings (sorted for a
        stable, inspectable final ordering).
    """
    rng = np.random.RandomState(random_seed)
    selected: list[str] = []

    for true_class in sorted(registry["true_class"].unique()):
        class_rows = registry[registry["true_class"] == true_class]
        correct_mask = class_rows["predicted_class_baseline"] == true_class
        correct_ids = class_rows.loc[correct_mask, "sample_id"].to_numpy()
        incorrect_ids = class_rows.loc[~correct_mask, "sample_id"].to_numpy()

        rng.shuffle(correct_ids)
        rng.shuffle(incorrect_ids)

        selected.extend(correct_ids[:correct_per_class].tolist())
        selected.extend(incorrect_ids[:incorrect_per_class].tolist())

        logger.debug(
            "Class %s: selected %d correct, %d incorrect (available: %d correct, %d incorrect)",
            true_class, min(correct_per_class, len(correct_ids)), min(incorrect_per_class, len(incorrect_ids)),
            len(correct_ids), len(incorrect_ids),
        )

    selected = sorted(set(selected))
    logger.info("Subset selected: %d sample_ids across %d classes", len(selected), registry["true_class"].nunique())
    return selected


def build_evaluation_data(
    test_df: pd.DataFrame, registry: pd.DataFrame, sample_ids: list[str], target_column: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extract the feature matrix and metadata for the fixed subset, in sample_id order.

    Args:
        test_df: Full testing set (features + target), row order
            matching the registry's ``row_index``.
        registry: Output of :func:`load_sample_registry`.
        sample_ids: Output of :func:`select_evaluation_subset`.
        target_column: Name of the target column.

    Returns:
        Tuple of ``(X_subset, metadata)``: ``X_subset`` is the feature
        matrix for the selected rows; ``metadata`` is the matching
        registry rows, both ordered identically by ``sample_id``.
    """
    metadata = registry[registry["sample_id"].isin(sample_ids)].sort_values("sample_id").reset_index(drop=True)
    row_indices = metadata["row_index"].to_numpy()
    X_subset = test_df.drop(columns=[target_column]).iloc[row_indices].reset_index(drop=True)
    return X_subset, metadata


# ══════════════════════════════════════════════════════════════
# SHAP computation (TreeExplainer)
# ══════════════════════════════════════════════════════════════

def compute_shap_values(
    model: RandomForestClassifier, X_subset: pd.DataFrame, check_additivity: bool
) -> dict[str, Any]:
    """Compute exact SHAP values for the fixed subset via TreeExplainer.

    Args:
        model: Loaded (already-trained) ``RandomForestClassifier``.
        X_subset: Feature matrix for the fixed evaluation subset.
        check_additivity: Whether to verify SHAP values sum to the
            model's raw output minus the expected value.

    Returns:
        Dict with ``shap_values`` (array, shape
        ``(n_samples, n_features, n_classes)``), ``expected_value``
        (per-class base value), ``class_labels``, and ``feature_names``.
    """
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_subset, check_additivity=check_additivity)
    logger.info(
        "SHAP values computed — shape=%s, classes=%d, features=%d",
        shap_values.shape, shap_values.shape[2], shap_values.shape[1],
    )
    return {
        "shap_values": shap_values,
        "expected_value": np.asarray(explainer.expected_value),
        "class_labels": list(model.classes_),
        "feature_names": list(X_subset.columns),
    }


# ══════════════════════════════════════════════════════════════
# Global feature importance (descriptive only)
# ══════════════════════════════════════════════════════════════

def compute_global_importance(shap_result: dict[str, Any]) -> pd.DataFrame:
    """Rank features by mean absolute SHAP value, averaged across all classes and samples.

    Args:
        shap_result: Output of :func:`compute_shap_values`.

    Returns:
        ``DataFrame`` with ``feature``, ``mean_abs_shap`` (overall
        ranking), sorted descending. Per-class mean absolute SHAP
        values are also included as ``mean_abs_shap_<class>`` columns
        for transparency.
    """
    sv = shap_result["shap_values"]
    feature_names = shap_result["feature_names"]
    class_labels = shap_result["class_labels"]

    overall = np.abs(sv).mean(axis=(0, 2))
    per_class = np.abs(sv).mean(axis=0)

    data = {"feature": feature_names, "mean_abs_shap": np.round(overall, 6)}
    for class_idx, class_name in enumerate(class_labels):
        data[f"mean_abs_shap_{class_name}"] = np.round(per_class[:, class_idx], 6)

    return pd.DataFrame(data).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)


# ══════════════════════════════════════════════════════════════
# Local explanations (representative examples)
# ══════════════════════════════════════════════════════════════

def select_local_examples(metadata: pd.DataFrame, registry: pd.DataFrame) -> dict[str, str]:
    """Pick four named representative sample_ids from the fixed subset.

    Args:
        metadata: Output of :func:`build_evaluation_data` (the subset's metadata).
        registry: Full Task E.1 registry, used to determine which
            class is majority/minority across the entire testing set.

    Returns:
        Dict with keys ``correct_prediction``, ``incorrect_prediction``,
        ``minority_class``, ``majority_class``, each mapping to a
        ``sample_id``.
    """
    class_counts = registry["true_class"].value_counts()
    majority_class = class_counts.idxmax()
    minority_class = class_counts.idxmin()

    correct_mask = metadata["predicted_class_baseline"] == metadata["true_class"]
    incorrect_mask = ~correct_mask

    examples = {}
    examples["correct_prediction"] = metadata.loc[correct_mask, "sample_id"].iloc[0]
    examples["incorrect_prediction"] = metadata.loc[incorrect_mask, "sample_id"].iloc[0]

    minority_rows = metadata[metadata["true_class"] == minority_class]
    examples["minority_class"] = (
        minority_rows["sample_id"].iloc[0] if len(minority_rows) > 0
        else metadata.loc[incorrect_mask, "sample_id"].iloc[0]
    )

    majority_rows = metadata[metadata["true_class"] == majority_class]
    examples["majority_class"] = (
        majority_rows["sample_id"].iloc[0] if len(majority_rows) > 0
        else metadata["sample_id"].iloc[0]
    )

    logger.info("Local examples selected: %s", examples)
    return examples


def build_local_explanation(
    shap_result: dict[str, Any], metadata: pd.DataFrame, sample_id: str, predicted_class_column: str, top_k: int
) -> dict[str, Any]:
    """Build the top-K feature attribution breakdown for one sample's true class.

    Args:
        shap_result: Output of :func:`compute_shap_values`.
        metadata: Output of :func:`build_evaluation_data` (subset metadata).
        sample_id: Sample to explain (must be in *metadata*).
        predicted_class_column: Which metadata column holds this
            model's prediction (``"predicted_class_baseline"`` or
            ``"predicted_class_smote"``).
        top_k: Number of top-magnitude features to report.

    Returns:
        Dict with ``sample_id``, ``true_class``, ``predicted_class``,
        and ``top_features`` (list of ``{feature, shap_value}``,
        sorted by absolute magnitude descending).
    """
    idx = metadata.index[metadata["sample_id"] == sample_id][0]
    row = metadata.loc[idx]
    class_idx = shap_result["class_labels"].index(row["true_class"])
    sample_shap = shap_result["shap_values"][idx, :, class_idx]

    order = np.argsort(-np.abs(sample_shap))[:top_k]
    top_features = [
        {"feature": shap_result["feature_names"][i], "shap_value": round(float(sample_shap[i]), 6)}
        for i in order
    ]

    return {
        "sample_id": sample_id,
        "true_class": row["true_class"],
        "predicted_class": row[predicted_class_column],
        "top_features": top_features,
    }


# ══════════════════════════════════════════════════════════════
# Export (long-format — Parquet-compatible for a 3D array)
# ══════════════════════════════════════════════════════════════

def shap_values_to_long_dataframe(shap_result: dict[str, Any], metadata: pd.DataFrame) -> pd.DataFrame:
    """Flatten the 3D SHAP value array into a tidy, Parquet-compatible table.

    Parquet (and CSV) require 2D tabular data; a raw
    ``(samples, features, classes)`` array cannot be written directly.
    This produces one row per (sample, feature, class) combination —
    fully reloadable and queryable (e.g. filter to one class or one
    sample without deserialising the whole array).

    Args:
        shap_result: Output of :func:`compute_shap_values`.
        metadata: Output of :func:`build_evaluation_data` (subset metadata).

    Returns:
        Long-format ``DataFrame`` with ``sample_id``, ``true_class``,
        ``feature``, ``class_name``, ``shap_value``.
    """
    sv = shap_result["shap_values"]
    feature_names = shap_result["feature_names"]
    class_labels = shap_result["class_labels"]
    sample_ids = metadata["sample_id"].to_numpy()
    true_classes = metadata["true_class"].to_numpy()

    n_samples, n_features, n_classes = sv.shape
    records = {
        "sample_id": np.repeat(sample_ids, n_features * n_classes),
        "true_class": np.repeat(true_classes, n_features * n_classes),
        "feature": np.tile(np.repeat(feature_names, n_classes), n_samples),
        "class_name": np.tile(class_labels, n_samples * n_features),
        "shap_value": np.round(sv.flatten(), 6),
    }
    return pd.DataFrame(records)


def save_shap_values(df: pd.DataFrame, stem: str) -> tuple[Path, str]:
    """Save the long-format SHAP values to ``outputs/shap/``, preferring Parquet.

    Args:
        df: Output of :func:`shap_values_to_long_dataframe`.
        stem: Filename without extension.

    Returns:
        Tuple of ``(resolved_path, format_used)``.
    """
    directory = get_path_manager().project_root / "outputs" / "shap"
    directory.mkdir(parents=True, exist_ok=True)
    parquet_path = directory / f"{stem}.parquet"

    try:
        df.to_parquet(parquet_path, index=False)
        return parquet_path, "parquet"
    except ImportError:
        csv_path = directory / f"{stem}.csv"
        df.to_csv(csv_path, index=False)
        logger.warning(
            "Parquet engine unavailable — saved %s as CSV instead. "
            "Documented alternative: CSV preserves the same long-format schema.",
            csv_path.name,
        )
        return csv_path, "csv"


# ══════════════════════════════════════════════════════════════
# Global figures (publication quality)
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


def plot_shap_summary(shap_result: dict[str, Any], X_subset: pd.DataFrame, title: str, save_path: Path) -> Path:
    """Plot a SHAP beeswarm summary plot, aggregated across classes.

    Multi-class SHAP values have no single, model-agnostic notion of
    "high"/"low" output direction shared across unordered categories,
    so this aggregates by taking the mean absolute SHAP value across
    the class dimension per (sample, feature) — producing one
    magnitude-of-impact value per cell, which is what the standard
    beeswarm visualises (feature value still colours each point).
    This is a documented simplification (see module docstring).

    Args:
        shap_result: Output of :func:`compute_shap_values`.
        X_subset: Feature matrix matching *shap_result*'s sample order.
        title: Figure title.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    sv_aggregated = np.abs(shap_result["shap_values"]).mean(axis=2)

    shap.summary_plot(sv_aggregated, X_subset, show=False)
    fig = plt.gcf()
    fig.suptitle(title, fontsize=13, fontweight="bold", y=1.02)
    fig.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_shap_bar(global_importance: pd.DataFrame, title: str, save_path: Path, top_n: int = 20) -> Path:
    """Plot a horizontal bar chart of global mean(|SHAP|) feature importance.

    Args:
        global_importance: Output of :func:`compute_global_importance`.
        title: Figure title.
        save_path: PNG destination.
        top_n: Number of top features to display.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    top = global_importance.head(top_n).sort_values("mean_abs_shap")

    fig, ax = plt.subplots(figsize=(9, max(6, top_n * 0.35)))
    ax.barh(top["feature"], top["mean_abs_shap"], color="#1f77b4")
    ax.set_xlabel("Mean |SHAP value| (averaged across classes)")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_shap_tables(
    baseline_importance: pd.DataFrame, smote_importance: pd.DataFrame, metadata: pd.DataFrame
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        baseline_importance: Output of :func:`compute_global_importance` (baseline).
        smote_importance: Output of :func:`compute_global_importance` (smote).
        metadata: Output of :func:`build_evaluation_data` (subset metadata).

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    path = tables_dir / "shap_global_importance_baseline.csv"
    baseline_importance.to_csv(path, index=False)
    paths["shap_global_importance_baseline"] = path

    path = tables_dir / "shap_global_importance_smote.csv"
    smote_importance.to_csv(path, index=False)
    paths["shap_global_importance_smote"] = path

    path = tables_dir / "shap_sample_registry.csv"
    metadata.to_csv(path, index=False)
    paths["shap_sample_registry"] = path

    logger.info("Table generated: %d SHAP CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_shap_markdown(report: dict[str, Any]) -> str:
    """Render the full SHAP analysis report as Markdown.

    Args:
        report: Report dict from :func:`run_shap_analysis`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    lines: list[str] = [
        "# UNSW-NB15 SHAP Explainability Analysis Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Why TreeExplainer",
        "",
        "`shap.TreeExplainer` computes exact Shapley values for tree ensembles in polynomial time by "
        "exploiting the tree structure directly, requiring no background dataset and no sampling "
        "approximation — the appropriate, standard choice for explaining Random Forest models, and the "
        "only SHAP explainer that guarantees attributions sum exactly to (prediction − expected value).",
        "",
        "## Why Identical Sample IDs Are Required",
        "",
        "This study compares attribution patterns between a model trained on imbalanced data and one "
        "trained on SMOTE-balanced data. Explaining different samples for each model would confound any "
        "observed attribution difference with *which rows* were explained, rather than isolating the "
        "effect of the training distribution.",
        "",
        "## Why the Prediction Repository Is Reused",
        "",
        "Correctness/incorrectness labels for sample selection must reflect the exact predictions already "
        "reported in Task D.1 and Task E.1 — recomputing predictions here would risk drift and duplicate "
        "already-tested logic.",
        "",
        "---",
        "",
        "## Sample Selection Methodology",
        "",
        f"For every one of the 10 true classes, up to {report['config']['correct_per_class']} correctly-"
        f"classified and up to {report['config']['incorrect_per_class']} misclassified samples (per the "
        "**baseline model's** predictions) were selected via a seeded shuffle, then deterministically "
        f"truncated. This produced a fixed subset of **{report['subset_size']} samples** spanning all 10 "
        "classes, including both the rarest class (`Worms`, 44 total testing samples) and the most "
        "frequent (`Normal`, 37,000 total testing samples). The exact same `sample_id` set was used to "
        "compute SHAP values for both models.",
        "",
        "---",
        "",
        "## Computation Details",
        "",
        f"- **Explainer:** `shap.TreeExplainer`",
        f"- **check_additivity:** {report['config']['check_additivity']}",
        f"- **Samples explained:** {report['subset_size']} (identical for both models)",
        f"- **Output shape per model:** ({report['subset_size']}, {report['feature_count']}, {report['class_count']}) "
        "(samples x features x classes)",
        "",
        "---",
        "",
        "## Global Feature Importance — Top 10 (Baseline)",
        "",
        "| Feature | Mean |SHAP| |",
        "|---|---|",
    ]
    for row in report["baseline_importance"][:10]:
        lines.append(f"| {row['feature']} | {row['mean_abs_shap']} |")

    lines += [
        "",
        "## Global Feature Importance — Top 10 (SMOTE)",
        "",
        "| Feature | Mean |SHAP| |",
        "|---|---|",
    ]
    for row in report["smote_importance"][:10]:
        lines.append(f"| {row['feature']} | {row['mean_abs_shap']} |")

    lines += [
        "",
        "---",
        "",
        "## Notable Attribution Differences (Descriptive Only)",
        "",
        "*(Reported as observed differences in this specific computation — no causal claim is made.)*",
        "",
    ]
    for entry in report["attribution_differences"]:
        lines.append(
            f"- `{entry['feature']}`: rank {entry['baseline_rank']} (baseline) vs. rank {entry['smote_rank']} "
            f"(SMOTE), mean |SHAP| {entry['baseline_value']} vs. {entry['smote_value']}"
        )

    lines += [
        "",
        "---",
        "",
        "## Local Explanations (Representative Examples)",
        "",
    ]
    for slot_name, examples in report["local_explanations"].items():
        lines.append(f"### {slot_name.replace('_', ' ').title()} — `{examples['baseline']['sample_id']}`")
        lines.append("")
        lines.append(
            f"True class: `{examples['baseline']['true_class']}` | "
            f"Baseline predicted: `{examples['baseline']['predicted_class']}` | "
            f"SMOTE predicted: `{examples['smote']['predicted_class']}`"
        )
        lines.append("")
        lines.append("| Model | Top Features (by |SHAP|, for the true class) |")
        lines.append("|---|---|")
        baseline_feats = ", ".join(f"{f['feature']}={f['shap_value']}" for f in examples["baseline"]["top_features"])
        smote_feats = ", ".join(f"{f['feature']}={f['shap_value']}" for f in examples["smote"]["top_features"])
        lines.append(f"| Baseline | {baseline_feats} |")
        lines.append(f"| SMOTE | {smote_feats} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Limitations",
        "",
        "- SHAP attributions describe what the model learned from the data, not a causal relationship "
        "between a feature and the true network-traffic outcome.",
        "- Global summary and bar plots aggregate 10-class SHAP values via mean absolute value, losing "
        "per-class directionality — a deliberate simplification to produce the two requested plot types; "
        "the full per-class breakdown remains available in the per-feature CSV tables and the long-format "
        "Parquet export.",
        "- TreeExplainer's path-dependent attributions can split credit between highly correlated features "
        "(several pairs were retained as \"Candidate\" features in Task C.4); a high or low attribution for "
        "one such feature does not rule out a shared signal with its correlated partner.",
        "- The fixed evaluation subset (60 samples or fewer) is intentionally small for computational "
        "tractability (TreeExplainer on these deep, unbounded trees takes over a second per sample); global "
        "importance rankings from this subset are descriptive of these specific samples, not a claim about "
        "the full 82,332-row testing population.",
        "",
        "---",
        "",
        "## SHAP Analysis Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"SHAP values were computed for both Random Forest models using `shap.TreeExplainer` against a "
        f"fixed, deterministic evaluation subset of {report['subset_size']} samples, selected once from the "
        "Task E.1 prediction repository to span all 10 classes with both correctly- and incorrectly-"
        "classified examples, and reused identically for both models. No retraining occurred. Global "
        f"feature importance (mean |SHAP| across classes) and local explanations for four representative "
        "samples (a correct prediction, an incorrect prediction, a minority-class example, and a "
        "majority-class example) were generated for both models under identical conditions, producing a "
        "directly comparable basis for examining how training-distribution balancing affects feature "
        "attribution patterns.",
        "",
        "---",
        "*End of SHAP Analysis Report*",
    ]
    return "\n".join(lines) + "\n"


def save_shap_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the SHAP analysis report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_shap_analysis`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "shap_analysis_report.json", json_safe)
    md_path = write_text(reports_dir / "shap_analysis_report.md", _render_shap_markdown(report))
    logger.info("Reports generated: %s, %s", json_path.name, md_path.name)
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Attribution comparison (descriptive only — no hypothesis testing)
# ══════════════════════════════════════════════════════════════

def compute_attribution_differences(
    baseline_importance: pd.DataFrame, smote_importance: pd.DataFrame, top_n: int = 10
) -> list[dict[str, Any]]:
    """Report rank/value differences for the top features in either model.

    Purely descriptive — no statistical test, no causal claim.

    Args:
        baseline_importance: Output of :func:`compute_global_importance` (baseline).
        smote_importance: Output of :func:`compute_global_importance` (smote).
        top_n: Number of top baseline-ranked features to report on.

    Returns:
        List of dicts with ``feature``, ``baseline_rank``,
        ``smote_rank``, ``baseline_value``, ``smote_value``.
    """
    baseline_rank = {f: i + 1 for i, f in enumerate(baseline_importance["feature"])}
    smote_rank = {f: i + 1 for i, f in enumerate(smote_importance["feature"])}
    baseline_value = dict(zip(baseline_importance["feature"], baseline_importance["mean_abs_shap"]))
    smote_value = dict(zip(smote_importance["feature"], smote_importance["mean_abs_shap"]))

    top_features = baseline_importance["feature"].head(top_n).tolist()
    return [
        {
            "feature": f,
            "baseline_rank": baseline_rank.get(f),
            "smote_rank": smote_rank.get(f),
            "baseline_value": baseline_value.get(f),
            "smote_value": smote_value.get(f),
        }
        for f in top_features
    ]


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_shap_analysis() -> dict[str, Any]:
    """Run the full SHAP explainability pipeline for both models.

    Loads both trained models (no retraining) and the testing set,
    selects one fixed deterministic sample subset from the Task E.1
    prediction repository, computes SHAP values for both models
    against that identical subset, generates global and local
    analyses, saves figures/tables/exports, and writes reports.

    Returns:
        Full report dict (see :func:`save_shap_report`'s input).
    """
    dataset_cfg = _load_dataset_config()
    experiment_cfg = _load_experiment_config()
    explain_cfg = _load_explainability_config()

    target_column = dataset_cfg.get("target_column", "attack_cat")
    random_seed = experiment_cfg.get("random_seed", 42)
    sel_cfg = explain_cfg.get("sample_selection", {})
    shap_cfg = explain_cfg.get("shap", {})
    correct_per_class = sel_cfg.get("correct_samples_per_class", 3)
    incorrect_per_class = sel_cfg.get("incorrect_samples_per_class", 3)
    check_additivity = shap_cfg.get("check_additivity", False)
    top_k = shap_cfg.get("local_top_k_features", 5)

    set_global_seed(random_seed)

    model_baseline, model_smote = load_models()
    test_df = load_testing_data()
    registry = load_sample_registry()

    sample_ids = select_evaluation_subset(registry, correct_per_class, incorrect_per_class, random_seed)
    X_subset, metadata = build_evaluation_data(test_df, registry, sample_ids, target_column)

    logger.info("SHAP computation started — baseline model")
    baseline_shap = compute_shap_values(model_baseline, X_subset, check_additivity)
    logger.info("SHAP computation completed — baseline model")

    logger.info("SHAP computation started — smote model")
    smote_shap = compute_shap_values(model_smote, X_subset, check_additivity)
    logger.info("SHAP computation completed — smote model")

    baseline_importance = compute_global_importance(baseline_shap)
    smote_importance = compute_global_importance(smote_shap)
    attribution_differences = compute_attribution_differences(baseline_importance, smote_importance)

    local_slots = select_local_examples(metadata, registry)
    local_explanations = {
        slot: {
            "baseline": build_local_explanation(baseline_shap, metadata, sid, "predicted_class_baseline", top_k),
            "smote": build_local_explanation(smote_shap, metadata, sid, "predicted_class_smote", top_k),
        }
        for slot, sid in local_slots.items()
    }

    figures_dir = get_path_manager().figures_dir
    plot_shap_summary(baseline_shap, X_subset, "SHAP Summary (Baseline Training)", figures_dir / "shap_summary_baseline.png")
    plot_shap_summary(smote_shap, X_subset, "SHAP Summary (SMOTE-Balanced Training)", figures_dir / "shap_summary_smote.png")
    plot_shap_bar(baseline_importance, "SHAP Global Feature Importance (Baseline Training)", figures_dir / "shap_bar_baseline.png")
    plot_shap_bar(smote_importance, "SHAP Global Feature Importance (SMOTE-Balanced Training)", figures_dir / "shap_bar_smote.png")

    baseline_long = shap_values_to_long_dataframe(baseline_shap, metadata)
    smote_long = shap_values_to_long_dataframe(smote_shap, metadata)
    baseline_path, output_format = save_shap_values(baseline_long, "shap_values_baseline")
    smote_path, _ = save_shap_values(smote_long, "shap_values_smote")
    logger.info("Repository exported: %s, %s", baseline_path.name, smote_path.name)

    save_shap_tables(baseline_importance, smote_importance, metadata)

    summary = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "config": {
            "correct_per_class": correct_per_class,
            "incorrect_per_class": incorrect_per_class,
            "check_additivity": check_additivity,
            "random_seed": random_seed,
        },
        "subset_size": len(sample_ids),
        "feature_count": len(baseline_shap["feature_names"]),
        "class_count": len(baseline_shap["class_labels"]),
        "output_format": output_format,
        "baseline_importance": baseline_importance.to_dict(orient="records"),
        "smote_importance": smote_importance.to_dict(orient="records"),
        "attribution_differences": attribution_differences,
        "local_explanations": local_explanations,
        "summary": summary,
    }
    save_shap_report(report)

    logger.info(
        "SHAP analysis completed — %d samples explained per model, top baseline feature: %s",
        len(sample_ids), baseline_importance.iloc[0]["feature"],
    )
    return report
