"""LIME explainability analysis for the dual Random Forest baseline.

Generates LIME (Local Interpretable Model-agnostic Explanations) for
both Task D.1 models against the **exact same** fixed evaluation
subset Task E.2 already selected — this module never recomputes a
subset, it reads Task E.2's saved artifacts directly.

This module is read-only with respect to every prior artefact: it
loads the already-trained models, the already-archived predictions,
and Task E.2's already-selected sample IDs; it computes LIME
explanations and writes new files under ``outputs/lime/`` — it never
retrains, never modifies a SHAP output, and never compares SHAP and
LIME (that comparison is explicitly Task E.4's scope).

Usage::

    from src.explainability.lime_analysis import run_lime_analysis

    result = run_lime_analysis()

Why LIME is appropriate for local explanations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LIME explains one prediction at a time by fitting a simple, locally
weighted linear model around the instance in a perturbed neighbourhood
of the input space. Unlike TreeExplainer (Task E.2), it is
model-agnostic — it only requires a ``predict_proba`` function — and
its explanations are framed as "how would this specific instance's
prediction change if this feature were different," which is a
complementary, more intuitive framing for individual-case inspection
than SHAP's game-theoretic feature-attribution decomposition. Running
both methods on identical samples (this task and Task E.2) is what
makes Task E.4's reliability comparison possible.

Why identical sample IDs are reused
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Task E.4 will compare SHAP and LIME explanations directly. If LIME
explained a different sample than SHAP did for the same nominal
"correct prediction" example, the two methods' outputs would not be
comparable at all. This module loads Task E.2's saved sample
registry and local-example selections verbatim — it does not call
:func:`src.explainability.shap_analysis.select_evaluation_subset`
again, even though doing so would be deterministic and produce an
identical result; reading the saved artifact removes any dependency
on that function's internals remaining unchanged in the future.

Why the prediction repository is reused
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Predicted-class labels used to identify "correct"/"incorrect"
examples must reflect the exact predictions already reported in
Task D.1 and Task E.1 — recomputing predictions here would risk
drift and duplicate already-tested logic.

Limitations of LIME (see also the generated report)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* LIME's local linear surrogate is fit on a *randomly perturbed*
  neighbourhood; unlike TreeExplainer's exact computation, two runs
  with different random seeds can produce different feature weights
  for the same instance — this module fixes the seed for
  reproducibility, but the underlying method is approximate.
* The surrogate model's R² (``exp.score``) measures how well a
  *linear* model fits the local neighbourhood of a fundamentally
  non-linear Random Forest decision boundary; a low score indicates
  the linear explanation may not faithfully represent the model's
  true local behaviour for that instance.
* The background ``training_data`` each explainer uses to compute
  perturbation statistics is that model's own training set (baseline
  uses ``training_baseline.parquet``, SMOTE uses
  ``training_balanced_smote.parquet``) — a deliberate choice so each
  explainer perturbs around the feature distribution that model
  actually learned from, documented further below.
* As with Task E.2, attributions describe model behaviour, not a
  causal relationship with the true network-traffic outcome.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lime.lime_tabular import LimeTabularExplainer
from sklearn.ensemble import RandomForestClassifier

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.core.reproducibility import set_global_seed
from src.data.feature_encoding import identify_categorical_columns
from src.explainability.shap_analysis import build_evaluation_data, load_sample_registry
from src.models.prediction_repository import load_models, load_testing_data
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_DATASET_CONFIG_FILENAME = "dataset.yaml"
_EXPERIMENT_CONFIG_FILENAME = "experiment.yaml"
_EXPLAINABILITY_CONFIG_FILENAME = "explainability.yaml"
_PREPROCESSING_CONFIG_FILENAME = "preprocessing.yaml"
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


def _load_preprocessing_config() -> dict[str, Any]:
    """Load ``configs/preprocessing.yaml`` (the frozen schema contract).

    Returns:
        Parsed preprocessing configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _PREPROCESSING_CONFIG_FILENAME)


# ══════════════════════════════════════════════════════════════
# Reuse Task E.2's frozen subset (never recomputed)
# ══════════════════════════════════════════════════════════════

def load_e2_evaluation_subset() -> list[str]:
    """Load the exact sample_id list Task E.2 already selected.

    Returns:
        List of ``sample_id`` strings, read directly from Task E.2's
        saved table — never recomputed.

    Raises:
        FileNotFoundError: If Task E.2's table is missing, with
            guidance to run ``scripts/11_shap_analysis.py`` first.
    """
    path = get_path_manager().tables_dir / "shap_sample_registry.csv"
    if not path.is_file():
        raise FileNotFoundError(
            f"Task E.2 sample registry not found at {path}. Run scripts/11_shap_analysis.py first."
        )
    e2_registry = pd.read_csv(path)
    sample_ids = sorted(e2_registry["sample_id"].tolist())
    logger.info("Evaluation subset loaded from Task E.2: %d sample_ids", len(sample_ids))
    return sample_ids


def load_e2_local_examples() -> dict[str, str]:
    """Load the exact 4 representative sample_ids Task E.2 already selected.

    Returns:
        Dict mapping slot name (``correct_prediction``,
        ``incorrect_prediction``, ``minority_class``, ``majority_class``)
        to a ``sample_id`` string.

    Raises:
        FileNotFoundError: If Task E.2's report is missing, with
            guidance to run ``scripts/11_shap_analysis.py`` first.
    """
    path = get_path_manager().reports_dir / "shap_analysis_report.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Task E.2 report not found at {path}. Run scripts/11_shap_analysis.py first."
        )
    import json
    e2_report = json.loads(path.read_text(encoding="utf-8"))
    examples = {
        slot: entry["baseline"]["sample_id"]
        for slot, entry in e2_report["local_explanations"].items()
    }
    logger.info("Local representative examples reused from Task E.2: %s", examples)
    return examples


# ══════════════════════════════════════════════════════════════
# Explainer construction
# ══════════════════════════════════════════════════════════════

def identify_lime_categorical_indices(feature_names: list[str], categorical_columns: list[str]) -> list[int]:
    """Map categorical column names to their positional index in *feature_names*.

    Args:
        feature_names: Ordered feature column names.
        categorical_columns: Names of the ordinal-encoded categorical
            columns (``proto``, ``service``, ``state``).

    Returns:
        Sorted list of column indices for LIME's ``categorical_features``.
    """
    return sorted(feature_names.index(c) for c in categorical_columns if c in feature_names)


def build_lime_explainer(
    X_train_background: pd.DataFrame,
    feature_names: list[str],
    class_labels: list[str],
    categorical_indices: list[int],
    random_seed: int,
) -> LimeTabularExplainer:
    """Build a ``LimeTabularExplainer`` using a model's own training data as background.

    Each model's explainer uses *that model's own* training set to
    compute the feature-perturbation statistics (mean/std for
    continuous features, frequency distribution for the ordinal-
    encoded categorical ones) — so perturbations reflect the feature
    distribution that specific model actually learned from, rather
    than an unrelated reference distribution.

    Args:
        X_train_background: Training feature matrix for the model
            being explained.
        feature_names: Ordered feature column names.
        class_labels: Ordered class names (matching ``model.classes_``).
        categorical_indices: Output of :func:`identify_lime_categorical_indices`.
        random_seed: Seed for reproducible perturbation sampling.

    Returns:
        Configured ``LimeTabularExplainer``.
    """
    return LimeTabularExplainer(
        training_data=X_train_background.to_numpy(),
        feature_names=feature_names,
        class_names=class_labels,
        categorical_features=categorical_indices,
        mode="classification",
        random_state=random_seed,
    )


def make_predict_function(model: RandomForestClassifier, feature_names: list[str]) -> Callable[[np.ndarray], np.ndarray]:
    """Wrap ``model.predict_proba`` to accept LIME's raw numpy perturbations.

    LIME calls the prediction function with a plain numpy array; this
    wrapper restores the DataFrame column names the model was fitted
    with, avoiding a spurious "X does not have valid feature names"
    warning without changing any prediction value.

    Args:
        model: Loaded (already-trained) ``RandomForestClassifier``.
        feature_names: Ordered feature column names.

    Returns:
        Callable taking a numpy array and returning class probabilities.
    """
    def predict_fn(X_array: np.ndarray) -> np.ndarray:
        return model.predict_proba(pd.DataFrame(X_array, columns=feature_names))

    return predict_fn


# ══════════════════════════════════════════════════════════════
# Per-sample and batch explanation
# ══════════════════════════════════════════════════════════════

def explain_sample(
    explainer: LimeTabularExplainer,
    predict_fn: Callable[[np.ndarray], np.ndarray],
    x_row: np.ndarray,
    true_class_idx: int,
    num_features: int,
    num_samples: int,
) -> dict[str, Any]:
    """Generate one LIME local explanation for a sample's true class.

    Args:
        explainer: Output of :func:`build_lime_explainer`.
        predict_fn: Output of :func:`make_predict_function`.
        x_row: Feature values for one sample (numpy array, raw order).
        true_class_idx: Index of the true class within ``class_labels``.
        num_features: Number of top features to include.
        num_samples: Number of perturbed samples LIME generates.

    Returns:
        Dict with ``feature_contributions`` (list of
        ``{feature, weight}``, ordered by |weight| as LIME returns
        them), ``local_fidelity_score`` (the local surrogate's R²),
        and ``local_prediction`` (surrogate's predicted probability
        for the true class).
    """
    explanation = explainer.explain_instance(
        x_row, predict_fn, labels=(true_class_idx,), num_features=num_features, num_samples=num_samples
    )
    feature_names = explainer.feature_names
    contributions = [
        {"feature": feature_names[idx], "weight": round(float(weight), 6)}
        for idx, weight in explanation.as_map()[true_class_idx]
    ]
    return {
        "feature_contributions": contributions,
        "local_fidelity_score": round(float(explanation.score), 6),
        "local_prediction": round(float(explanation.local_pred[0]), 6),
    }


def compute_lime_explanations(
    model: RandomForestClassifier,
    X_subset: pd.DataFrame,
    metadata: pd.DataFrame,
    X_train_background: pd.DataFrame,
    class_labels: list[str],
    categorical_indices: list[int],
    num_features: int,
    num_samples: int,
    random_seed: int,
) -> list[dict[str, Any]]:
    """Compute LIME explanations for every sample in the fixed subset.

    Args:
        model: Loaded (already-trained) model.
        X_subset: Feature matrix for the fixed evaluation subset
            (output of :func:`src.explainability.shap_analysis.build_evaluation_data`).
        metadata: Matching subset metadata (same row order as *X_subset*).
        X_train_background: This model's own training feature matrix.
        class_labels: Ordered class names.
        categorical_indices: Output of :func:`identify_lime_categorical_indices`.
        num_features: Number of top features per explanation.
        num_samples: Number of perturbed samples per explanation.
        random_seed: Seed for reproducible perturbation sampling.

    Returns:
        List of per-sample dicts with ``sample_id``, ``true_class``,
        and the fields from :func:`explain_sample`.
    """
    feature_names = list(X_subset.columns)
    explainer = build_lime_explainer(X_train_background, feature_names, class_labels, categorical_indices, random_seed)
    predict_fn = make_predict_function(model, feature_names)

    results = []
    for i in range(len(X_subset)):
        true_class = metadata.iloc[i]["true_class"]
        true_class_idx = class_labels.index(true_class)
        explanation = explain_sample(
            explainer, predict_fn, X_subset.iloc[i].to_numpy(), true_class_idx, num_features, num_samples
        )
        results.append({
            "sample_id": metadata.iloc[i]["sample_id"],
            "true_class": true_class,
            **explanation,
        })

    logger.info("LIME explanations computed: %d samples", len(results))
    return results


# ══════════════════════════════════════════════════════════════
# Export (long-format — Parquet-compatible)
# ══════════════════════════════════════════════════════════════

def explanations_to_long_dataframe(explanations: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten per-sample LIME explanations into a tidy, Parquet-compatible table.

    Args:
        explanations: Output of :func:`compute_lime_explanations`.

    Returns:
        Long-format ``DataFrame`` with ``sample_id``, ``true_class``,
        ``feature``, ``weight``, ``rank``, ``local_fidelity_score``,
        ``local_prediction``.
    """
    rows = []
    for entry in explanations:
        for rank, contribution in enumerate(entry["feature_contributions"], start=1):
            rows.append({
                "sample_id": entry["sample_id"],
                "true_class": entry["true_class"],
                "feature": contribution["feature"],
                "weight": contribution["weight"],
                "rank": rank,
                "local_fidelity_score": entry["local_fidelity_score"],
                "local_prediction": entry["local_prediction"],
            })
    return pd.DataFrame(rows)


def save_lime_explanations(df: pd.DataFrame, stem: str) -> tuple[Path, str]:
    """Save the long-format LIME explanations to ``outputs/lime/``, preferring Parquet.

    Args:
        df: Output of :func:`explanations_to_long_dataframe`.
        stem: Filename without extension.

    Returns:
        Tuple of ``(resolved_path, format_used)``.
    """
    directory = get_path_manager().project_root / "outputs" / "lime"
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
# Feature importance ranking (descriptive only)
# ══════════════════════════════════════════════════════════════

def compute_feature_importance(long_df: pd.DataFrame) -> pd.DataFrame:
    """Rank features by mean absolute LIME weight across the explained subset.

    Args:
        long_df: Output of :func:`explanations_to_long_dataframe`.

    Returns:
        ``DataFrame`` with ``feature``, ``mean_abs_weight``,
        ``appearance_count`` (how many of the explained samples
        included this feature in their top-K), sorted descending.
    """
    grouped = long_df.groupby("feature")["weight"].agg(mean_abs_weight=lambda s: s.abs().mean(), appearance_count="count")
    grouped["mean_abs_weight"] = grouped["mean_abs_weight"].round(6)
    return grouped.reset_index().sort_values("mean_abs_weight", ascending=False).reset_index(drop=True)


# ══════════════════════════════════════════════════════════════
# Figures (publication quality)
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


def plot_lime_feature_importance(importance: pd.DataFrame, title: str, save_path: Path, top_n: int = 20) -> Path:
    """Plot a horizontal bar chart of global mean(|LIME weight|) feature importance.

    Args:
        importance: Output of :func:`compute_feature_importance`.
        title: Figure title.
        save_path: PNG destination.
        top_n: Number of top features to display.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    top = importance.head(top_n).sort_values("mean_abs_weight")

    fig, ax = plt.subplots(figsize=(9, max(6, top_n * 0.35)))
    ax.barh(top["feature"], top["mean_abs_weight"], color="#ff7f0e")
    ax.set_xlabel("Mean |LIME weight| (across explained subset)")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_local_comparison(
    baseline_explanation: dict[str, Any],
    smote_explanation: dict[str, Any],
    sample_id: str,
    slot_title: str,
    save_path: Path,
) -> Path:
    """Plot side-by-side local feature contribution bars for one sample.

    Args:
        baseline_explanation: One entry from baseline's
            :func:`compute_lime_explanations` output (the matching sample_id).
        smote_explanation: Same, for the SMOTE model.
        sample_id: The shared sample identifier.
        slot_title: Human-readable label (e.g. ``"Correct Prediction"``).
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    for ax, explanation, model_title in (
        (axes[0], baseline_explanation, "Baseline Training"),
        (axes[1], smote_explanation, "SMOTE-Balanced Training"),
    ):
        contributions = sorted(explanation["feature_contributions"], key=lambda c: c["weight"])
        features = [c["feature"] for c in contributions]
        weights = [c["weight"] for c in contributions]
        colors = ["#d62728" if w < 0 else "#1f77b4" for w in weights]
        ax.barh(features, weights, color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("LIME weight (contribution to true-class probability)")
        ax.set_title(f"{model_title}\n(local fidelity R² = {explanation['local_fidelity_score']})", fontsize=10)
        ax.grid(axis="x", alpha=0.3)

    fig.suptitle(f"LIME Local Explanation — {slot_title} (`{sample_id}`)", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.93))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_lime_tables(
    baseline_importance: pd.DataFrame, smote_importance: pd.DataFrame, metadata: pd.DataFrame
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        baseline_importance: Output of :func:`compute_feature_importance` (baseline).
        smote_importance: Output of :func:`compute_feature_importance` (smote).
        metadata: Subset metadata (reused from Task E.2's frozen subset).

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    path = tables_dir / "lime_feature_importance_baseline.csv"
    baseline_importance.to_csv(path, index=False)
    paths["lime_feature_importance_baseline"] = path

    path = tables_dir / "lime_feature_importance_smote.csv"
    smote_importance.to_csv(path, index=False)
    paths["lime_feature_importance_smote"] = path

    path = tables_dir / "lime_sample_registry.csv"
    metadata.to_csv(path, index=False)
    paths["lime_sample_registry"] = path

    logger.info("Table generated: %d LIME CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_lime_markdown(report: dict[str, Any]) -> str:
    """Render the full LIME analysis report as Markdown.

    Args:
        report: Report dict from :func:`run_lime_analysis`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    lines: list[str] = [
        "# UNSW-NB15 LIME Explainability Analysis Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Methodology",
        "",
        "`LimeTabularExplainer` fits a locally weighted linear surrogate model around each "
        "instance's perturbed neighbourhood to approximate the Random Forest's behaviour near that "
        "point. Explanations were generated for the **exact same** evaluation subset Task E.2 already "
        "selected — read directly from Task E.2's saved sample registry and local-example selections, "
        "never recomputed — so SHAP (Task E.2) and LIME (this task) explain identical samples, a "
        "prerequisite for Task E.4's reliability comparison.",
        "",
        "## Why LIME Is Appropriate for Local Explanations",
        "",
        "LIME is model-agnostic (requires only a `predict_proba` function) and frames each explanation "
        "as a local linear approximation around one specific instance — a complementary perspective to "
        "SHAP's exact, game-theoretic global decomposition, useful for inspecting individual predictions "
        "in an intuitive \"what moved this prediction\" form.",
        "",
        "## Why Identical Sample IDs Are Reused",
        "",
        "Task E.4 will compare SHAP and LIME outputs directly; explaining different samples would make "
        "that comparison meaningless. This module reads Task E.2's saved sample IDs verbatim rather than "
        "recomputing a (deterministically identical) subset, removing any dependency on that selection "
        "logic remaining unchanged.",
        "",
        "## Why the Prediction Repository Is Reused",
        "",
        "True/predicted class labels for the explained samples come from Task E.1's archived predictions, "
        "avoiding any risk of drift from re-running inference.",
        "",
        "---",
        "",
        "## Configuration",
        "",
        "| Parameter | Value |",
        "|---|---|",
        f"| num_features | {report['config']['num_features']} |",
        f"| num_samples (perturbations per instance) | {report['config']['num_samples']} |",
        f"| random_seed | {report['config']['random_seed']} |",
        f"| categorical_features | {', '.join(report['config']['categorical_columns'])} |",
        f"| Background data (baseline explainer) | `training_baseline.parquet` |",
        f"| Background data (SMOTE explainer) | `training_balanced_smote.parquet` |",
        "",
        "---",
        "",
        f"## Samples Explained: {report['subset_size']}",
        "",
        "Identical sample_id set reused from Task E.2, spanning all 10 classes with both correctly- "
        "and incorrectly-classified examples per class.",
        "",
        "---",
        "",
        "## Global Feature Importance — Top 10 (Baseline)",
        "",
        "| Feature | Mean |Weight| | Appearances |",
        "|---|---|---|",
    ]
    for row in report["baseline_importance"][:10]:
        lines.append(f"| {row['feature']} | {row['mean_abs_weight']} | {row['appearance_count']} |")

    lines += [
        "",
        "## Global Feature Importance — Top 10 (SMOTE)",
        "",
        "| Feature | Mean |Weight| | Appearances |",
        "|---|---|---|",
    ]
    for row in report["smote_importance"][:10]:
        lines.append(f"| {row['feature']} | {row['mean_abs_weight']} | {row['appearance_count']} |")

    lines += [
        "",
        "---",
        "",
        "## Observed Attribution Differences (Descriptive Only)",
        "",
        "*(Reported as observed differences in this specific computation — no causal claim is made.)*",
        "",
        f"- Mean local fidelity (R²), baseline: {report['mean_fidelity_baseline']}  ",
        f"- Mean local fidelity (R²), SMOTE: {report['mean_fidelity_smote']}",
        "",
        "---",
        "",
        "## Local Explanation Summaries (Representative Examples)",
        "",
    ]
    for slot_name, examples in report["local_explanations"].items():
        lines.append(f"### {slot_name.replace('_', ' ').title()} — `{examples['sample_id']}`")
        lines.append("")
        lines.append(f"True class: `{examples['true_class']}`")
        lines.append("")
        lines.append("| Model | Local Fidelity (R²) | Top Feature Contributions |")
        lines.append("|---|---|---|")
        baseline_feats = ", ".join(f"{c['feature']}={c['weight']}" for c in examples["baseline"]["feature_contributions"][:5])
        smote_feats = ", ".join(f"{c['feature']}={c['weight']}" for c in examples["smote"]["feature_contributions"][:5])
        lines.append(f"| Baseline | {examples['baseline']['local_fidelity_score']} | {baseline_feats} |")
        lines.append(f"| SMOTE | {examples['smote']['local_fidelity_score']} | {smote_feats} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Limitations",
        "",
        "- LIME's local linear surrogate is fit on a randomly perturbed neighbourhood; results are "
        "approximate and seed-dependent (fixed here for reproducibility, but a different seed could "
        "produce different feature weights for the same instance).",
        "- The local fidelity score (R²) measures how well a *linear* model approximates the Random "
        "Forest's behaviour near one instance; a low score indicates the explanation may not faithfully "
        "represent the model's true local decision behaviour for that sample.",
        "- Each model's explainer used that model's own training set as the perturbation background "
        "(baseline uses the original training distribution, SMOTE uses the balanced one) — a deliberate "
        "choice so perturbations reflect what each model actually learned from, but this means the two "
        "explainers are not perturbing from an identical reference distribution.",
        "- As with SHAP, attributions describe model behaviour, not a causal relationship with the true "
        "network-traffic outcome.",
        "- This report does not compare SHAP and LIME outputs — that comparison is Task E.4's scope.",
        "",
        "---",
        "",
        "## LIME Analysis Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"LIME explanations were computed for both Random Forest models using `LimeTabularExplainer` "
        f"({report['config']['num_samples']} perturbed samples per instance, top "
        f"{report['config']['num_features']} features per explanation) against the exact same "
        f"{report['subset_size']}-sample evaluation subset Task E.2 selected — read directly from Task "
        "E.2's saved artifacts, never recomputed. Each model's explainer used that model's own training "
        "distribution as its perturbation background. No retraining occurred. Local explanations were "
        "generated for all subset samples, plus detailed reporting for the four representative examples "
        "(a correct prediction, an incorrect prediction, a minority-class example, and a majority-class "
        "example) shared with Task E.2, establishing a directly comparable basis for Task E.4's SHAP-LIME "
        "reliability analysis.",
        "",
        "---",
        "*End of LIME Analysis Report*",
    ]
    return "\n".join(lines) + "\n"


def save_lime_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the LIME analysis report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_lime_analysis`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "lime_analysis_report.json", json_safe)
    md_path = write_text(reports_dir / "lime_analysis_report.md", _render_lime_markdown(report))
    logger.info("Reports generated: %s, %s", json_path.name, md_path.name)
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_lime_analysis() -> dict[str, Any]:
    """Run the full LIME explainability pipeline for both models.

    Loads both trained models (no retraining), the testing set, and
    Task E.2's frozen evaluation subset and representative examples
    (read directly, never recomputed). Computes LIME explanations for
    both models against that identical subset, generates global and
    local analyses, saves figures/tables/exports, and writes reports.

    Returns:
        Full report dict (see :func:`save_lime_report`'s input).
    """
    dataset_cfg = _load_dataset_config()
    experiment_cfg = _load_experiment_config()
    explain_cfg = _load_explainability_config()
    preprocessing_cfg = _load_preprocessing_config()

    target_column = dataset_cfg.get("target_column", "attack_cat")
    random_seed = experiment_cfg.get("random_seed", 42)
    lime_cfg = explain_cfg.get("lime", {})
    num_features = lime_cfg.get("num_features", 10)
    num_samples = lime_cfg.get("num_samples", 5000)

    set_global_seed(random_seed)

    model_baseline, model_smote = load_models()
    test_df = load_testing_data()
    registry = load_sample_registry()
    logger.info("Evaluation subset loaded")

    sample_ids = load_e2_evaluation_subset()
    local_example_ids = load_e2_local_examples()
    X_subset, metadata = build_evaluation_data(test_df, registry, sample_ids, target_column)

    categorical_columns = identify_categorical_columns(preprocessing_cfg["expected_dtypes"], target_column)
    categorical_indices = identify_lime_categorical_indices(list(X_subset.columns), categorical_columns)
    class_labels = sorted(registry["true_class"].unique().tolist())

    processed_dir = get_path_manager().processed_data_dir
    X_train_baseline = pd.read_parquet(processed_dir / "training_baseline.parquet").drop(columns=[target_column])
    X_train_smote = pd.read_parquet(processed_dir / "training_balanced_smote.parquet").drop(columns=[target_column])

    logger.info("LIME computation started — baseline model")
    baseline_explanations = compute_lime_explanations(
        model_baseline, X_subset, metadata, X_train_baseline, class_labels, categorical_indices,
        num_features, num_samples, random_seed,
    )
    logger.info("LIME computation completed — baseline model")

    logger.info("LIME computation started — smote model")
    smote_explanations = compute_lime_explanations(
        model_smote, X_subset, metadata, X_train_smote, class_labels, categorical_indices,
        num_features, num_samples, random_seed,
    )
    logger.info("LIME computation completed — smote model")

    baseline_long = explanations_to_long_dataframe(baseline_explanations)
    smote_long = explanations_to_long_dataframe(smote_explanations)
    baseline_importance = compute_feature_importance(baseline_long)
    smote_importance = compute_feature_importance(smote_long)

    baseline_by_id = {e["sample_id"]: e for e in baseline_explanations}
    smote_by_id = {e["sample_id"]: e for e in smote_explanations}
    local_explanations = {
        slot: {
            "sample_id": sid,
            "true_class": baseline_by_id[sid]["true_class"],
            "baseline": baseline_by_id[sid],
            "smote": smote_by_id[sid],
        }
        for slot, sid in local_example_ids.items()
    }

    figures_dir = get_path_manager().figures_dir
    plot_lime_feature_importance(baseline_importance, "LIME Global Feature Importance (Baseline Training)", figures_dir / "lime_importance_baseline.png")
    plot_lime_feature_importance(smote_importance, "LIME Global Feature Importance (SMOTE-Balanced Training)", figures_dir / "lime_importance_smote.png")
    for slot, examples in local_explanations.items():
        plot_local_comparison(
            examples["baseline"], examples["smote"], examples["sample_id"],
            slot.replace("_", " ").title(), figures_dir / f"lime_local_{slot}.png",
        )

    baseline_path, output_format = save_lime_explanations(baseline_long, "lime_explanations_baseline")
    smote_path, _ = save_lime_explanations(smote_long, "lime_explanations_smote")
    logger.info("Exports generated: %s, %s", baseline_path.name, smote_path.name)

    save_lime_tables(baseline_importance, smote_importance, metadata)

    summary = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
    }

    report = {
        "config": {
            "num_features": num_features,
            "num_samples": num_samples,
            "random_seed": random_seed,
            "categorical_columns": categorical_columns,
        },
        "subset_size": len(sample_ids),
        "output_format": output_format,
        "baseline_importance": baseline_importance.to_dict(orient="records"),
        "smote_importance": smote_importance.to_dict(orient="records"),
        "mean_fidelity_baseline": round(float(baseline_long["local_fidelity_score"].drop_duplicates().mean()), 6),
        "mean_fidelity_smote": round(float(smote_long["local_fidelity_score"].drop_duplicates().mean()), 6),
        "local_explanations": local_explanations,
        "summary": summary,
    }
    save_lime_report(report)

    logger.info(
        "LIME analysis completed — %d samples explained per model, top baseline feature: %s",
        len(sample_ids), baseline_importance.iloc[0]["feature"],
    )
    return report
