"""Explanation reliability and SHAP-LIME comparative analysis.

This is the project's primary scientific contribution: a rigorous
comparison of how class balancing (Task C.5) changes explanation
behaviour, measured two independent ways (SHAP, Task E.2; LIME,
Task E.3), at both the global (dataset-level) and local
(individual-sample) scale.

This module performs **no computation that produces a new
explanation** — it loads Task E.2's and Task E.3's already-saved
outputs and compares them. No model is retrained, no SHAP value is
recomputed, no LIME explanation is regenerated.

Usage::

    from src.explainability.explanation_comparison import run_explanation_comparison

    result = run_explanation_comparison()

Why identical samples are required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every comparison in this module — SHAP-baseline vs SHAP-SMOTE,
LIME-baseline vs LIME-SMOTE, and SHAP vs LIME within each training
condition — is only valid because Task E.2 and Task E.3 explained the
*exact same* 60 samples (verified by hash and set-equality checks in
both prior tasks' self-tests). If the compared explanation sets came
from different samples, every metric computed here (rank correlation,
top-k overlap, Jaccard similarity) would conflate "different samples"
with "different explanation behaviour" — an uncontrolled confound
this entire project's sample-selection discipline (Tasks E.1-E.3) was
built specifically to eliminate.

Why explanation comparison is meaningful
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The research question this paper investigates is whether training-set
class balance changes what a model's explanations look like — not
merely whether accuracy changes (Task D.1 already reported that). By
holding the explained samples fixed and varying only the training
distribution, a measured change in feature ranking, attribution
magnitude, or cross-method agreement is attributable to the training
distribution rather than to which rows were explained or which
explainer was used inconsistently.

Threats to validity
~~~~~~~~~~~~~~~~~~~~
* **Small subset size.** All comparisons operate on the same 60-sample
  subset Task E.2 selected for computational tractability. Findings
  describe this subset, not a population-level claim about all 82,332
  testing rows.
* **No statistical significance testing.** This task is explicitly
  scoped to descriptive comparison; Task F.1 (Statistical Validation)
  is where any significance claims belong. Observed differences here
  are reported as magnitudes and rank shifts, not as "significant" or
  "not significant."
* **Asymmetric LIME background distributions.** Task E.3 documented
  that each model's LIME explainer used that model's own training set
  as its perturbation background — so a baseline-vs-SMOTE LIME
  difference may partly reflect this background asymmetry, not only
  the trained model's behaviour. This is distinct from SHAP, where
  TreeExplainer requires no background dataset at all.
* **Feature-set mismatch between SHAP and LIME.** SHAP's global
  importance table always covers all 42 features; LIME's only
  contains features that appeared in some sample's top-K explanation
  (a strict subset — 38 of 42 in this project's run). Cross-method
  comparisons are restricted to the intersection of features present
  in both rankings, which is stated explicitly wherever it applies.

Limitations of comparing two different explanation methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SHAP's TreeExplainer values are exact Shapley decompositions; LIME's
weights come from an approximate local linear surrogate fit on
randomly perturbed data. These are different mathematical objects
measured on different scales (SHAP values are in raw model-output
units; LIME weights are coefficients of a local linear model) — a
direct numerical comparison of *magnitudes* between the two methods
is not meaningful. This module therefore compares **rankings**
(Spearman/Kendall correlation, top-k overlap, Jaccard similarity) and
*directional* observations, not raw value differences, between SHAP
and LIME.

Distinguishing observed results, interpretation, and speculation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The generated report labels every finding as either an **observed
result** (a number computed directly from the data, stated without
elaboration), a brief **interpretation** (what a reasonable reader
would conclude from that number alone), or explicitly flagged
speculation where a pattern is suggestive but not established by this
descriptive analysis. No causal language is used anywhere in this
module's output.
"""

from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from src.config import get_path_manager
from src.config.constants import VERSION
from src.core.logging_config import get_logger
from src.utils.file_utils import read_yaml, write_json, write_text

logger = get_logger(__name__)

_EXPLAINABILITY_CONFIG_FILENAME = "explainability.yaml"
_FIGURE_DPI = 300


def _load_explainability_config() -> dict[str, Any]:
    """Load ``configs/explainability.yaml``.

    Returns:
        Parsed explainability configuration dictionary.
    """
    return read_yaml(get_path_manager().configs_dir / _EXPLAINABILITY_CONFIG_FILENAME)


# ══════════════════════════════════════════════════════════════
# Loading (read-only — every input already computed by E.1-E.3)
# ══════════════════════════════════════════════════════════════

def load_comparison_inputs() -> dict[str, Any]:
    """Load every Task E.1-E.3 artefact this comparison needs, unmodified.

    Returns:
        Dict with ``sample_registry`` (Task E.2's frozen 60-sample
        subset metadata), ``shap_long`` and ``lime_long`` (per
        baseline/smote, the long-format explanation exports),
        ``shap_importance`` and ``lime_importance`` (per
        baseline/smote, the already-computed global importance
        tables), and ``local_examples`` (Task E.2's 4 representative
        sample IDs, reused verbatim).

    Raises:
        FileNotFoundError: If any required upstream artefact is
            missing, with guidance to run the relevant prior script.
    """
    pm = get_path_manager()
    tables_dir = pm.tables_dir
    reports_dir = pm.reports_dir
    shap_dir = pm.project_root / "outputs" / "shap"
    lime_dir = pm.project_root / "outputs" / "lime"

    required = {
        "sample_registry": tables_dir / "shap_sample_registry.csv",
        "shap_importance_baseline": tables_dir / "shap_global_importance_baseline.csv",
        "shap_importance_smote": tables_dir / "shap_global_importance_smote.csv",
        "lime_importance_baseline": tables_dir / "lime_feature_importance_baseline.csv",
        "lime_importance_smote": tables_dir / "lime_feature_importance_smote.csv",
        "shap_values_baseline": shap_dir / "shap_values_baseline.parquet",
        "shap_values_smote": shap_dir / "shap_values_smote.parquet",
        "lime_values_baseline": lime_dir / "lime_explanations_baseline.parquet",
        "lime_values_smote": lime_dir / "lime_explanations_smote.parquet",
        "shap_report": reports_dir / "shap_analysis_report.json",
    }
    missing = [str(p) for p in required.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "Required Task E.2/E.3 artefacts missing: " + ", ".join(missing) +
            ". Run scripts/11_shap_analysis.py and scripts/12_lime_analysis.py first."
        )

    sample_registry = pd.read_csv(required["sample_registry"])
    shap_importance = {
        "baseline": pd.read_csv(required["shap_importance_baseline"]),
        "smote": pd.read_csv(required["shap_importance_smote"]),
    }
    lime_importance = {
        "baseline": pd.read_csv(required["lime_importance_baseline"]),
        "smote": pd.read_csv(required["lime_importance_smote"]),
    }
    shap_long = {
        "baseline": pd.read_parquet(required["shap_values_baseline"]),
        "smote": pd.read_parquet(required["shap_values_smote"]),
    }
    lime_long = {
        "baseline": pd.read_parquet(required["lime_values_baseline"]),
        "smote": pd.read_parquet(required["lime_values_smote"]),
    }
    shap_report = json.loads(required["shap_report"].read_text(encoding="utf-8"))
    local_examples = {
        slot: entry["baseline"]["sample_id"]
        for slot, entry in shap_report["local_explanations"].items()
    }

    logger.info(
        "Inputs loaded — %d subset samples, SHAP/LIME long-format and importance tables for both models",
        len(sample_registry),
    )
    return {
        "sample_registry": sample_registry,
        "shap_long": shap_long,
        "lime_long": lime_long,
        "shap_importance": shap_importance,
        "lime_importance": lime_importance,
        "local_examples": local_examples,
    }


# ══════════════════════════════════════════════════════════════
# Global ranking comparison (generic — reused for every pair)
# ══════════════════════════════════════════════════════════════

def build_feature_ranking(importance_df: pd.DataFrame, value_col: str) -> pd.Series:
    """Build a feature -> rank Series from an importance table (rank 1 = most important).

    Args:
        importance_df: Importance table with a ``feature`` column and
            *value_col* (already sorted or not — re-sorted here).
        value_col: Column to rank by, descending.

    Returns:
        ``Series`` indexed by feature name, values are integer ranks.
    """
    sorted_df = importance_df.sort_values(value_col, ascending=False).reset_index(drop=True)
    return pd.Series(sorted_df.index + 1, index=sorted_df["feature"])


def compare_global_rankings(
    importance_a: pd.DataFrame,
    importance_b: pd.DataFrame,
    value_col_a: str,
    value_col_b: str,
    label_a: str,
    label_b: str,
    top_n: int = 10,
) -> dict[str, Any]:
    """Compare two global feature-importance rankings.

    Restricted to the intersection of features present in both
    tables — stated explicitly in the returned dict, since SHAP's
    and LIME's importance tables do not always cover the same
    feature set (see module docstring).

    Args:
        importance_a: First importance table (``feature`` + *value_col_a*).
        importance_b: Second importance table (``feature`` + *value_col_b*).
        value_col_a: Value column name in *importance_a*.
        value_col_b: Value column name in *importance_b*.
        label_a: Human-readable label for the first condition.
        label_b: Human-readable label for the second condition.
        top_n: Size of the "top features" set used for newly-/reduced-
            importance detection.

    Returns:
        Dict with ``common_feature_count``, ``rank_changes`` (list of
        per-feature dicts), ``newly_important`` (entered top_n in B
        but not A), and ``reduced_importance`` (left top_n from A to B).
    """
    rank_a = build_feature_ranking(importance_a, value_col_a)
    rank_b = build_feature_ranking(importance_b, value_col_b)
    common_features = sorted(set(rank_a.index) & set(rank_b.index))

    value_map_a = dict(zip(importance_a["feature"], importance_a[value_col_a]))
    value_map_b = dict(zip(importance_b["feature"], importance_b[value_col_b]))

    rank_changes = [
        {
            "feature": f,
            f"{label_a}_rank": int(rank_a[f]),
            f"{label_b}_rank": int(rank_b[f]),
            "rank_change": int(rank_a[f]) - int(rank_b[f]),
            f"{label_a}_value": round(float(value_map_a[f]), 6),
            f"{label_b}_value": round(float(value_map_b[f]), 6),
        }
        for f in common_features
    ]
    rank_changes.sort(key=lambda r: abs(r["rank_change"]), reverse=True)

    top_a = set(rank_a[rank_a <= top_n].index)
    top_b = set(rank_b[rank_b <= top_n].index)
    newly_important = sorted(top_b - top_a)
    reduced_importance = sorted(top_a - top_b)

    return {
        "label_a": label_a,
        "label_b": label_b,
        "common_feature_count": len(common_features),
        "rank_changes": rank_changes,
        "newly_important": newly_important,
        "reduced_importance": reduced_importance,
    }


# ══════════════════════════════════════════════════════════════
# Agreement metrics (descriptive only — no hypothesis testing)
# ══════════════════════════════════════════════════════════════

def compute_topk_overlap(rank_a: pd.Series, rank_b: pd.Series, k: int) -> float:
    """Compute the fraction of the smaller top-k set found in the other's top-k set.

    Args:
        rank_a: Output of :func:`build_feature_ranking`.
        rank_b: Same, for the second condition.
        k: Top-k size.

    Returns:
        Overlap fraction in [0, 1]: ``|top_k(A) ∩ top_k(B)| / k``.
    """
    top_a = set(rank_a[rank_a <= k].index)
    top_b = set(rank_b[rank_b <= k].index)
    return round(len(top_a & top_b) / k, 6) if k else 0.0


def compute_jaccard_similarity(rank_a: pd.Series, rank_b: pd.Series, k: int) -> float:
    """Compute Jaccard similarity of the two top-k important-feature sets.

    Args:
        rank_a: Output of :func:`build_feature_ranking`.
        rank_b: Same, for the second condition.
        k: Top-k size.

    Returns:
        Jaccard similarity in [0, 1]: ``|A ∩ B| / |A ∪ B|``.
    """
    top_a = set(rank_a[rank_a <= k].index)
    top_b = set(rank_b[rank_b <= k].index)
    union = top_a | top_b
    return round(len(top_a & top_b) / len(union), 6) if union else 0.0


def compute_rank_correlations(rank_a: pd.Series, rank_b: pd.Series) -> dict[str, Any]:
    """Compute Spearman and Kendall Tau rank correlation over the common feature set.

    Args:
        rank_a: Output of :func:`build_feature_ranking`.
        rank_b: Same, for the second condition.

    Returns:
        Dict with ``spearman_correlation``, ``spearman_p_value``,
        ``kendall_tau``, ``kendall_p_value``, and ``common_feature_count``.
        Computed only over features present in both rankings.
    """
    common = sorted(set(rank_a.index) & set(rank_b.index))
    a_values = [rank_a[f] for f in common]
    b_values = [rank_b[f] for f in common]

    if len(common) < 3:
        return {
            "spearman_correlation": None, "spearman_p_value": None,
            "kendall_tau": None, "kendall_p_value": None,
            "common_feature_count": len(common),
        }

    spearman_corr, spearman_p = spearmanr(a_values, b_values)
    kendall_corr, kendall_p = kendalltau(a_values, b_values)
    return {
        "spearman_correlation": round(float(spearman_corr), 6),
        "spearman_p_value": round(float(spearman_p), 6),
        "kendall_tau": round(float(kendall_corr), 6),
        "kendall_p_value": round(float(kendall_p), 6),
        "common_feature_count": len(common),
    }


def compute_agreement_metrics(
    importance_a: pd.DataFrame,
    importance_b: pd.DataFrame,
    value_col_a: str,
    value_col_b: str,
    pair_label: str,
    top_k_values: list[int],
) -> dict[str, Any]:
    """Compute the full agreement-metric suite for one comparison pair.

    Args:
        importance_a: First importance table.
        importance_b: Second importance table.
        value_col_a: Value column in *importance_a*.
        value_col_b: Value column in *importance_b*.
        pair_label: Human-readable label (e.g. ``"SHAP_baseline_vs_SHAP_smote"``).
        top_k_values: Top-k sizes to report overlap/Jaccard for.

    Returns:
        Dict with ``pair``, ``topk_overlap`` (per k), ``jaccard``
        (per k), and the rank-correlation fields.
    """
    rank_a = build_feature_ranking(importance_a, value_col_a)
    rank_b = build_feature_ranking(importance_b, value_col_b)

    result: dict[str, Any] = {
        "pair": pair_label,
        "topk_overlap": {f"top_{k}": compute_topk_overlap(rank_a, rank_b, k) for k in top_k_values},
        "jaccard": {f"top_{k}": compute_jaccard_similarity(rank_a, rank_b, k) for k in top_k_values},
    }
    result.update(compute_rank_correlations(rank_a, rank_b))
    return result


# ══════════════════════════════════════════════════════════════
# Local comparison (the 4 representative examples, reused from E.2/E.3)
# ══════════════════════════════════════════════════════════════

def extract_sample_shap_top_features(
    shap_long: pd.DataFrame, sample_id: str, true_class: str, top_k: int
) -> list[dict[str, Any]]:
    """Extract a sample's top-K SHAP features for its true class.

    Args:
        shap_long: Long-format SHAP export (one model's).
        sample_id: Sample to extract.
        true_class: Restrict to this class's SHAP values (consistent
            with Task E.2's local-explanation convention).
        top_k: Number of top |SHAP value| features to return.

    Returns:
        List of ``{feature, value}`` dicts, sorted by |value| descending.
    """
    rows = shap_long[(shap_long["sample_id"] == sample_id) & (shap_long["class_name"] == true_class)]
    rows = rows.reindex(rows["shap_value"].abs().sort_values(ascending=False).index).head(top_k)
    return [{"feature": r["feature"], "value": round(float(r["shap_value"]), 6)} for _, r in rows.iterrows()]


def extract_sample_lime_top_features(lime_long: pd.DataFrame, sample_id: str, top_k: int) -> list[dict[str, Any]]:
    """Extract a sample's top-K LIME features (already restricted to the true class by Task E.3).

    Args:
        lime_long: Long-format LIME export (one model's).
        sample_id: Sample to extract.
        top_k: Number of top-ranked features to return.

    Returns:
        List of ``{feature, value}`` dicts, in LIME's reported rank order.
    """
    rows = lime_long[lime_long["sample_id"] == sample_id].sort_values("rank").head(top_k)
    return [{"feature": r["feature"], "value": round(float(r["weight"]), 6)} for _, r in rows.iterrows()]


def compare_local_explanations(
    inputs: dict[str, Any], top_k: int
) -> dict[str, Any]:
    """Compare baseline-vs-SMOTE local explanations for the 4 representative examples.

    Args:
        inputs: Output of :func:`load_comparison_inputs`.
        top_k: Number of top features to compare per sample.

    Returns:
        Dict keyed by slot name (``correct_prediction``, etc.), each
        with ``sample_id``, ``true_class``, and ``shap``/``lime``
        sub-dicts (each with ``baseline``, ``smote`` feature lists
        and a top-k ``overlap`` fraction between them).
    """
    registry = inputs["sample_registry"]
    results = {}

    for slot, sample_id in inputs["local_examples"].items():
        true_class = registry.loc[registry["sample_id"] == sample_id, "true_class"].iloc[0]

        shap_base = extract_sample_shap_top_features(inputs["shap_long"]["baseline"], sample_id, true_class, top_k)
        shap_smote = extract_sample_shap_top_features(inputs["shap_long"]["smote"], sample_id, true_class, top_k)
        lime_base = extract_sample_lime_top_features(inputs["lime_long"]["baseline"], sample_id, top_k)
        lime_smote = extract_sample_lime_top_features(inputs["lime_long"]["smote"], sample_id, top_k)

        shap_overlap = len({f["feature"] for f in shap_base} & {f["feature"] for f in shap_smote}) / top_k
        lime_overlap = len({f["feature"] for f in lime_base} & {f["feature"] for f in lime_smote}) / top_k

        results[slot] = {
            "sample_id": sample_id,
            "true_class": true_class,
            "shap": {"baseline": shap_base, "smote": shap_smote, "overlap": round(shap_overlap, 6)},
            "lime": {"baseline": lime_base, "smote": lime_smote, "overlap": round(lime_overlap, 6)},
        }

    logger.info("Local comparison computed for %d representative examples", len(results))
    return results


# ══════════════════════════════════════════════════════════════
# Minority class analysis (descriptive only — no overstated claims)
# ══════════════════════════════════════════════════════════════

def build_class_specific_shap_importance(shap_long: pd.DataFrame, sample_ids: list[str], true_class: str) -> pd.DataFrame:
    """Build a feature-importance ranking restricted to one class's samples.

    Args:
        shap_long: Long-format SHAP export (one model's).
        sample_ids: Sample IDs belonging to *true_class*.
        true_class: The class whose SHAP dimension to use.

    Returns:
        ``DataFrame`` with ``feature``, ``mean_abs_shap``, sorted descending.
    """
    rows = shap_long[shap_long["sample_id"].isin(sample_ids) & (shap_long["class_name"] == true_class)]
    grouped = rows.groupby("feature")["shap_value"].apply(lambda s: s.abs().mean()).reset_index()
    grouped.columns = ["feature", "mean_abs_shap"]
    return grouped.sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)


def build_class_specific_lime_importance(lime_long: pd.DataFrame, sample_ids: list[str]) -> pd.DataFrame:
    """Build a feature-importance ranking restricted to one class's samples.

    Args:
        lime_long: Long-format LIME export (one model's).
        sample_ids: Sample IDs belonging to the target class.

    Returns:
        ``DataFrame`` with ``feature``, ``mean_abs_weight``, sorted descending.
    """
    rows = lime_long[lime_long["sample_id"].isin(sample_ids)]
    grouped = rows.groupby("feature")["weight"].apply(lambda s: s.abs().mean()).reset_index()
    grouped.columns = ["feature", "mean_abs_weight"]
    return grouped.sort_values("mean_abs_weight", ascending=False).reset_index(drop=True)


def analyze_minority_classes(
    inputs: dict[str, Any], minority_classes: list[str], top_k_values: list[int]
) -> dict[str, Any]:
    """Run class-restricted explanation-consistency analysis for each minority class.

    For each class, builds class-specific SHAP and LIME importance
    rankings (baseline and SMOTE), then runs the same agreement-metric
    suite used for the global comparison, restricted to that class's
    samples. Purely descriptive — explicitly does not claim the
    observed pattern generalises beyond this subset.

    Args:
        inputs: Output of :func:`load_comparison_inputs`.
        minority_classes: Class names to analyse (e.g. ``["Worms",
            "Backdoor", "Analysis"]``).
        top_k_values: Top-k sizes for the agreement metrics.

    Returns:
        Dict keyed by class name, each with ``sample_count``,
        per-method top-5 feature lists (baseline/SMOTE), and
        ``shap_agreement``/``lime_agreement`` metric dicts.
    """
    registry = inputs["sample_registry"]
    results: dict[str, Any] = {}

    for cls in minority_classes:
        class_samples = registry.loc[registry["true_class"] == cls, "sample_id"].tolist()
        if not class_samples:
            results[cls] = {"sample_count": 0, "note": "No samples of this class in the evaluation subset."}
            logger.info("Minority class analysis: %s has 0 samples in the subset — skipped", cls)
            continue

        shap_base_imp = build_class_specific_shap_importance(inputs["shap_long"]["baseline"], class_samples, cls)
        shap_smote_imp = build_class_specific_shap_importance(inputs["shap_long"]["smote"], class_samples, cls)
        lime_base_imp = build_class_specific_lime_importance(inputs["lime_long"]["baseline"], class_samples)
        lime_smote_imp = build_class_specific_lime_importance(inputs["lime_long"]["smote"], class_samples)

        shap_agreement = compute_agreement_metrics(
            shap_base_imp, shap_smote_imp, "mean_abs_shap", "mean_abs_shap",
            f"SHAP_{cls}_baseline_vs_smote", top_k_values,
        )
        lime_agreement = compute_agreement_metrics(
            lime_base_imp, lime_smote_imp, "mean_abs_weight", "mean_abs_weight",
            f"LIME_{cls}_baseline_vs_smote", top_k_values,
        )

        results[cls] = {
            "sample_count": len(class_samples),
            "sample_ids": class_samples,
            "shap_top_features_baseline": shap_base_imp.head(5).to_dict(orient="records"),
            "shap_top_features_smote": shap_smote_imp.head(5).to_dict(orient="records"),
            "lime_top_features_baseline": lime_base_imp.head(5).to_dict(orient="records"),
            "lime_top_features_smote": lime_smote_imp.head(5).to_dict(orient="records"),
            "shap_agreement": shap_agreement,
            "lime_agreement": lime_agreement,
        }

    logger.info("Minority class analysis computed for %s", list(results.keys()))
    return results


# ══════════════════════════════════════════════════════════════
# Export
# ══════════════════════════════════════════════════════════════

def build_comparison_long_dataframe(
    shap_comparison: dict[str, Any], lime_comparison: dict[str, Any]
) -> pd.DataFrame:
    """Flatten the global SHAP and LIME rank-change comparisons into one long table.

    Args:
        shap_comparison: Output of :func:`compare_global_rankings` (SHAP baseline vs SMOTE).
        lime_comparison: Output of :func:`compare_global_rankings` (LIME baseline vs SMOTE).

    Returns:
        Long-format ``DataFrame`` with ``method``, ``feature``,
        ``baseline_rank``, ``smote_rank``, ``rank_change``,
        ``baseline_value``, ``smote_value``.
    """
    rows = []
    for method, comparison in (("SHAP", shap_comparison), ("LIME", lime_comparison)):
        label_a, label_b = comparison["label_a"], comparison["label_b"]
        for entry in comparison["rank_changes"]:
            rows.append({
                "method": method,
                "feature": entry["feature"],
                "baseline_rank": entry[f"{label_a}_rank"],
                "smote_rank": entry[f"{label_b}_rank"],
                "rank_change": entry["rank_change"],
                "baseline_value": entry[f"{label_a}_value"],
                "smote_value": entry[f"{label_b}_value"],
            })
    return pd.DataFrame(rows)


def build_similarity_table(agreement_results: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten the agreement-metric results into one tidy table.

    Args:
        agreement_results: List of :func:`compute_agreement_metrics` outputs.

    Returns:
        Long-format ``DataFrame`` with ``pair``, ``metric``, ``value``.
    """
    rows = []
    for result in agreement_results:
        pair = result["pair"]
        for k, v in result["topk_overlap"].items():
            rows.append({"pair": pair, "metric": f"overlap_{k}", "value": v})
        for k, v in result["jaccard"].items():
            rows.append({"pair": pair, "metric": f"jaccard_{k}", "value": v})
        rows.append({"pair": pair, "metric": "spearman_correlation", "value": result["spearman_correlation"]})
        rows.append({"pair": pair, "metric": "kendall_tau", "value": result["kendall_tau"]})
    return pd.DataFrame(rows)


def save_comparison_outputs(
    comparison_long: pd.DataFrame, similarity_table: pd.DataFrame
) -> dict[str, tuple[Path, str]]:
    """Save the two required ``outputs/comparison/`` files, preferring Parquet.

    Args:
        comparison_long: Output of :func:`build_comparison_long_dataframe`.
        similarity_table: Output of :func:`build_similarity_table`.

    Returns:
        Mapping of output name to ``(resolved_path, format_used)``.
    """
    directory = get_path_manager().project_root / "outputs" / "comparison"
    directory.mkdir(parents=True, exist_ok=True)
    results: dict[str, tuple[Path, str]] = {}

    parquet_path = directory / "explanation_comparison.parquet"
    try:
        comparison_long.to_parquet(parquet_path, index=False)
        results["explanation_comparison"] = (parquet_path, "parquet")
    except ImportError:
        csv_path = directory / "explanation_comparison.csv"
        comparison_long.to_csv(csv_path, index=False)
        logger.warning("Parquet engine unavailable — saved %s as CSV instead.", csv_path.name)
        results["explanation_comparison"] = (csv_path, "csv")

    similarity_path = directory / "explanation_similarity.csv"
    similarity_table.to_csv(similarity_path, index=False)
    results["explanation_similarity"] = (similarity_path, "csv")

    return results


# ══════════════════════════════════════════════════════════════
# Figures (IEEE quality, 300 DPI)
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


def plot_ranking_comparison(shap_comparison: dict[str, Any], lime_comparison: dict[str, Any], save_path: Path) -> Path:
    """Plot baseline-rank vs SMOTE-rank scatter for SHAP and LIME side by side.

    Args:
        shap_comparison: Output of :func:`compare_global_rankings` (SHAP).
        lime_comparison: Output of :func:`compare_global_rankings` (LIME).
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    for ax, comparison, title in ((axes[0], shap_comparison, "SHAP"), (axes[1], lime_comparison, "LIME")):
        label_a, label_b = comparison["label_a"], comparison["label_b"]
        x = [r[f"{label_a}_rank"] for r in comparison["rank_changes"]]
        y = [r[f"{label_b}_rank"] for r in comparison["rank_changes"]]
        max_rank = max(max(x, default=1), max(y, default=1))
        ax.plot([1, max_rank], [1, max_rank], color="grey", linestyle="--", linewidth=1, label="No change")
        ax.scatter(x, y, color="#1f77b4", alpha=0.7, s=40)
        ax.set_xlabel("Baseline Rank")
        ax.set_ylabel("SMOTE Rank")
        ax.set_title(f"{title} Feature Ranking: Baseline vs. SMOTE")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_similarity_metrics(agreement_results: list[dict[str, Any]], save_path: Path) -> Path:
    """Plot a grouped bar chart comparing agreement metrics across all comparison pairs.

    Args:
        agreement_results: List of :func:`compute_agreement_metrics` outputs.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    pairs = [r["pair"] for r in agreement_results]
    metrics = {
        "Top-5 Overlap": [r["topk_overlap"].get("top_5", 0) for r in agreement_results],
        "Top-10 Overlap": [r["topk_overlap"].get("top_10", 0) for r in agreement_results],
        "Spearman": [r["spearman_correlation"] or 0 for r in agreement_results],
        "Kendall Tau": [r["kendall_tau"] or 0 for r in agreement_results],
    }

    x = np.arange(len(pairs))
    width = 0.2
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (label, values) in enumerate(metrics.items()):
        ax.bar(x + i * width, values, width, label=label)

    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(pairs, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Metric Value")
    ax.set_title("Explanation Agreement Metrics Across Comparison Pairs")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_minority_class_comparison(minority_results: dict[str, Any], save_path: Path) -> Path:
    """Plot SHAP top-feature mean |value| per minority class, baseline vs SMOTE.

    Args:
        minority_results: Output of :func:`analyze_minority_classes`.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    classes = [c for c, r in minority_results.items() if r.get("sample_count", 0) > 0]
    fig, axes = plt.subplots(1, len(classes), figsize=(6 * len(classes), 5.5))
    if len(classes) == 1:
        axes = [axes]

    for ax, cls in zip(axes, classes):
        entry = minority_results[cls]
        base_feats = {f["feature"]: f["mean_abs_shap"] for f in entry["shap_top_features_baseline"]}
        smote_feats = {f["feature"]: f["mean_abs_shap"] for f in entry["shap_top_features_smote"]}
        all_feats = list(dict.fromkeys(list(base_feats.keys()) + list(smote_feats.keys())))[:6]

        x = np.arange(len(all_feats))
        width = 0.35
        ax.bar(x - width / 2, [base_feats.get(f, 0) for f in all_feats], width, label="Baseline", color="#1f77b4")
        ax.bar(x + width / 2, [smote_feats.get(f, 0) for f in all_feats], width, label="SMOTE", color="#ff7f0e")
        ax.set_xticks(x)
        ax.set_xticklabels(all_feats, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("Mean |SHAP value|")
        ax.set_title(f"{cls} (n={entry['sample_count']})")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Minority Class SHAP Attribution — Baseline vs. SMOTE", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.93))
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


def plot_agreement_heatmap(agreement_results: list[dict[str, Any]], save_path: Path) -> Path:
    """Plot a heatmap of Spearman correlation across all comparison pairs.

    Args:
        agreement_results: List of :func:`compute_agreement_metrics` outputs.
        save_path: PNG destination.

    Returns:
        Resolved path of the saved figure.
    """
    _set_publication_style()
    pairs = [r["pair"] for r in agreement_results]
    values = np.array([[r["spearman_correlation"] or 0 for r in agreement_results]])

    fig, ax = plt.subplots(figsize=(max(8, len(pairs) * 1.2), 3))
    im = ax.imshow(values, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(pairs)))
    ax.set_xticklabels(pairs, rotation=20, ha="right", fontsize=8)
    ax.set_yticks([0])
    ax.set_yticklabels(["Spearman r"])
    for i, v in enumerate(values[0]):
        ax.text(i, 0, f"{v:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Explanation Agreement Heatmap (Spearman Correlation)")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Spearman Correlation")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close(fig)
    logger.info("Figure generated: %s", save_path.name)
    return save_path


# ══════════════════════════════════════════════════════════════
# CSV tables
# ══════════════════════════════════════════════════════════════

def save_comparison_tables(
    comparison_long: pd.DataFrame,
    similarity_table: pd.DataFrame,
    minority_results: dict[str, Any],
) -> dict[str, Path]:
    """Save the three required CSV tables.

    Args:
        comparison_long: Output of :func:`build_comparison_long_dataframe`.
        similarity_table: Output of :func:`build_similarity_table`.
        minority_results: Output of :func:`analyze_minority_classes`.

    Returns:
        Mapping of table name to the resolved path it was written to.
    """
    tables_dir = get_path_manager().tables_dir
    paths: dict[str, Path] = {}

    path = tables_dir / "feature_rank_changes.csv"
    comparison_long.sort_values("rank_change", key=abs, ascending=False).to_csv(path, index=False)
    paths["feature_rank_changes"] = path

    path = tables_dir / "explanation_overlap.csv"
    similarity_table.to_csv(path, index=False)
    paths["explanation_overlap"] = path

    minority_rows = []
    for cls, entry in minority_results.items():
        if entry.get("sample_count", 0) == 0:
            minority_rows.append({"class": cls, "sample_count": 0})
            continue
        minority_rows.append({
            "class": cls,
            "sample_count": entry["sample_count"],
            "shap_top5_overlap": entry["shap_agreement"]["topk_overlap"].get("top_5"),
            "shap_spearman": entry["shap_agreement"]["spearman_correlation"],
            "lime_top5_overlap": entry["lime_agreement"]["topk_overlap"].get("top_5"),
            "lime_spearman": entry["lime_agreement"]["spearman_correlation"],
        })
    path = tables_dir / "minority_class_analysis.csv"
    pd.DataFrame(minority_rows).to_csv(path, index=False)
    paths["minority_class_analysis"] = path

    logger.info("Table generated: %d explanation comparison CSV tables saved", len(paths))
    return paths


# ══════════════════════════════════════════════════════════════
# Report rendering
# ══════════════════════════════════════════════════════════════

def _render_comparison_markdown(report: dict[str, Any]) -> str:
    """Render the full explanation comparison report as Markdown.

    Args:
        report: Report dict from :func:`run_explanation_comparison`.

    Returns:
        Markdown document as a string.
    """
    s = report["summary"]
    lines: list[str] = [
        "# UNSW-NB15 Explanation Reliability & Comparative Analysis Report",
        "",
        f"**Generated:** {s['generated_utc']}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        f"**Project Version:** {s['project_version']}",
        "",
        "---",
        "",
        "## Methodology",
        "",
        f"This analysis compares Task E.2's SHAP outputs and Task E.3's LIME outputs across the two "
        f"Random Forest models (baseline, SMOTE-balanced), using the identical {report['subset_size']}-"
        "sample evaluation subset both prior tasks explained. No model was retrained, no SHAP value was "
        "recomputed, and no LIME explanation was regenerated — every number in this report derives from "
        "Task E.2's and Task E.3's already-saved Parquet/CSV outputs, loaded read-only.",
        "",
        "**Why identical samples are required:** every comparison below is only valid because SHAP and "
        "LIME explained the exact same rows (verified by Task E.2/E.3's own self-tests). Comparing "
        "explanations from different samples would confound \"different rows\" with \"different "
        "explanation behaviour.\"",
        "",
        "**Why explanation comparison is meaningful:** Task D.1 already reported that class balancing "
        "changes predictive metrics. This task asks the complementary question — does it also change "
        "*what the model's explanations look like* — by holding the explained samples fixed and varying "
        "only the training distribution.",
        "",
        "---",
        "",
        "## Comparison Metrics",
        "",
        "Four comparison pairs were evaluated, each using top-k feature overlap (k=5, k=10), Jaccard "
        "similarity of the top-k important-feature sets, Spearman rank correlation, and Kendall Tau rank "
        "correlation, computed over the intersection of features present in both rankings being compared:",
        "",
        "1. **SHAP_baseline vs SHAP_smote** — does balancing change what SHAP considers important, within the same method?",
        "2. **LIME_baseline vs LIME_smote** — same question, for LIME.",
        "3. **SHAP_baseline vs LIME_baseline** — do the two methods agree on the baseline model's behaviour?",
        "4. **SHAP_smote vs LIME_smote** — do the two methods agree on the SMOTE model's behaviour?",
        "",
        f"SHAP's global importance table covers all {report['shap_feature_count']} features; LIME's "
        f"covers only the {report['lime_feature_count']} features that appeared in some sample's top-K "
        "explanation (Task E.3's `num_features` config). Cross-method pairs (3 and 4 above) are therefore "
        f"restricted to their {report['intersection_feature_count']}-feature intersection — stated here "
        "explicitly as the assumption underlying those two comparisons.",
        "",
        "---",
        "",
        "## Agreement Analysis (Observed Results)",
        "",
        "| Pair | Top-5 Overlap | Top-10 Overlap | Jaccard (top-10) | Spearman r | Kendall τ |",
        "|---|---|---|---|---|---|",
    ]
    for r in report["agreement_results"]:
        lines.append(
            f"| {r['pair']} | {r['topk_overlap'].get('top_5')} | {r['topk_overlap'].get('top_10')} | "
            f"{r['jaccard'].get('top_10')} | {r['spearman_correlation']} | {r['kendall_tau']} |"
        )

    lines += [
        "",
        "**Interpretation:** higher overlap/Jaccard/correlation values indicate the two compared "
        "rankings agree more on which features matter; values near 0 (correlation) or 0 (overlap) "
        "indicate little agreement. These are observed magnitudes from this specific 60-sample subset, "
        "not statistical significance claims (Task F.1's scope).",
        "",
        "---",
        "",
        "## Global Comparison — Newly Important / Reduced Importance Features",
        "",
        "### SHAP (Baseline → SMOTE)",
        "",
        f"- **Newly important (entered top-{report['global_top_n']}):** "
        f"{', '.join(report['shap_global']['newly_important']) or 'none'}",
        f"- **Reduced importance (left top-{report['global_top_n']}):** "
        f"{', '.join(report['shap_global']['reduced_importance']) or 'none'}",
        "",
        "### LIME (Baseline → SMOTE)",
        "",
        f"- **Newly important (entered top-{report['global_top_n']}):** "
        f"{', '.join(report['lime_global']['newly_important']) or 'none'}",
        f"- **Reduced importance (left top-{report['global_top_n']}):** "
        f"{', '.join(report['lime_global']['reduced_importance']) or 'none'}",
        "",
        "---",
        "",
        "## Local Comparison (Representative Examples)",
        "",
    ]
    for slot, entry in report["local_comparison"].items():
        lines.append(f"### {slot.replace('_', ' ').title()} — `{entry['sample_id']}` (true class: `{entry['true_class']}`)")
        lines.append("")
        lines.append(f"- **SHAP top-5 overlap (baseline vs SMOTE):** {entry['shap']['overlap']}")
        lines.append(f"- **LIME top-5 overlap (baseline vs SMOTE):** {entry['lime']['overlap']}")
        lines.append("")

    lines += [
        "---",
        "",
        f"## Minority Class Analysis ({', '.join(report['minority_classes'])})",
        "",
        "*Descriptive only — observed patterns in this subset, not a generalisable claim.*",
        "",
    ]
    for cls, entry in report["minority_class_results"].items():
        if entry.get("sample_count", 0) == 0:
            lines.append(f"### {cls}: 0 samples in the evaluation subset — not analysed.")
            lines.append("")
            continue
        lines.append(f"### {cls} (n={entry['sample_count']})")
        lines.append("")
        lines.append(
            f"- **SHAP top-5 overlap, baseline vs SMOTE:** {entry['shap_agreement']['topk_overlap'].get('top_5')} "
            f"(Spearman r = {entry['shap_agreement']['spearman_correlation']})"
        )
        lines.append(
            f"- **LIME top-5 overlap, baseline vs SMOTE:** {entry['lime_agreement']['topk_overlap'].get('top_5')} "
            f"(Spearman r = {entry['lime_agreement']['spearman_correlation']})"
        )
        lines.append("")

    lines += [
        "---",
        "",
        "## Threats to Validity",
        "",
        "- **Small subset size (60 samples).** Findings describe this specific subset, selected for "
        "computational tractability in Task E.2; they are not a population-level claim about all 82,332 "
        "testing rows.",
        "- **No statistical significance testing.** This task reports observed magnitudes and rank shifts "
        "only. Significance testing is explicitly Task F.1's scope.",
        "- **Asymmetric LIME background distributions.** Each model's LIME explainer used that model's own "
        "training set as its perturbation background (Task E.3), so a baseline-vs-SMOTE LIME difference "
        "may partly reflect this background asymmetry rather than only the trained model's behaviour.",
        "- **Feature-set mismatch between SHAP and LIME.** Cross-method comparisons are restricted to the "
        f"{report['intersection_feature_count']}-feature intersection of both methods' importance tables, "
        "as stated in the Comparison Metrics section.",
        "",
        "---",
        "",
        "## Limitations",
        "",
        "- SHAP values and LIME weights are different mathematical objects on different scales; this "
        "report compares **rankings**, never raw magnitudes, between the two methods.",
        "- No causal claim is made anywhere in this report: an observed rank shift or attribution change "
        "describes what changed in the model's explanation behaviour when trained on a different "
        "distribution, not why the underlying network traffic produces that pattern.",
        "- Class-restricted minority-class metrics (3-9 samples per class) have wide uncertainty; small "
        "common-feature counts can make rank correlations unstable, noted directly in this report's tables "
        "where the common feature count is low.",
        "",
        "---",
        "",
        "## Explanation Comparison Summary (Methodology Section)",
        "",
        "*(Suitable for inclusion in the Methodology section)*",
        "",
        f"Explanation reliability was assessed by comparing Task E.2's SHAP and Task E.3's LIME outputs "
        f"across the baseline and SMOTE-balanced Random Forest models (Task D.1), using the identical "
        f"{report['subset_size']}-sample evaluation subset both methods explained. No model was retrained "
        "and no explanation was regenerated. Four comparison pairs were evaluated — SHAP baseline-vs-SMOTE, "
        "LIME baseline-vs-SMOTE, and SHAP-vs-LIME within each training condition — using top-k feature "
        "overlap (k=5, k=10), Jaccard similarity, Spearman rank correlation, and Kendall Tau rank "
        f"correlation. {s['key_observation']} Dedicated analysis of the three rarest classes "
        f"({', '.join(report['minority_classes'])}) examined whether class balancing changes explanation "
        "consistency specifically for minority classes. All comparisons are descriptive; no statistical "
        "significance testing or causal claims are made (Task F.1 addresses statistical validation).",
        "",
        "---",
        "*End of Explanation Comparison Report*",
    ]
    return "\n".join(lines) + "\n"


def save_comparison_report(report: dict[str, Any]) -> tuple[Path, Path]:
    """Save the explanation comparison report as JSON and Markdown.

    Args:
        report: Report dict from :func:`run_explanation_comparison`.

    Returns:
        Tuple of ``(json_path, markdown_path)``.
    """
    reports_dir = get_path_manager().reports_dir
    json_safe = {**report, "platform": platform.platform()}
    json_path = write_json(reports_dir / "explanation_comparison_report.json", json_safe)
    md_path = write_text(reports_dir / "explanation_comparison_report.md", _render_comparison_markdown(report))
    logger.info("Reports generated: %s, %s", json_path.name, md_path.name)
    return json_path, md_path


# ══════════════════════════════════════════════════════════════
# Master orchestration
# ══════════════════════════════════════════════════════════════

def run_explanation_comparison() -> dict[str, Any]:
    """Run the full explanation reliability and comparative analysis.

    Loads Task E.2's SHAP outputs and Task E.3's LIME outputs
    read-only, computes global and local comparisons, an agreement-
    metric suite across four comparison pairs, and a dedicated
    minority-class analysis, then saves exports/figures/tables/reports.
    No model is retrained and no explanation is regenerated.

    Returns:
        Full report dict (see :func:`save_comparison_report`'s input).
    """
    logger.info("Comparison started")

    explain_cfg = _load_explainability_config()
    comparison_cfg = explain_cfg.get("comparison", {})
    top_k_values = comparison_cfg.get("top_k_values", [5, 10])
    minority_classes = comparison_cfg.get("minority_classes", ["Worms", "Backdoor", "Analysis"])
    global_top_n = top_k_values[-1] if top_k_values else 10

    inputs = load_comparison_inputs()

    shap_global = compare_global_rankings(
        inputs["shap_importance"]["baseline"], inputs["shap_importance"]["smote"],
        "mean_abs_shap", "mean_abs_shap", "baseline", "smote", global_top_n,
    )
    lime_global = compare_global_rankings(
        inputs["lime_importance"]["baseline"], inputs["lime_importance"]["smote"],
        "mean_abs_weight", "mean_abs_weight", "baseline", "smote", global_top_n,
    )

    agreement_results = [
        compute_agreement_metrics(
            inputs["shap_importance"]["baseline"], inputs["shap_importance"]["smote"],
            "mean_abs_shap", "mean_abs_shap", "SHAP_baseline_vs_SHAP_smote", top_k_values,
        ),
        compute_agreement_metrics(
            inputs["lime_importance"]["baseline"], inputs["lime_importance"]["smote"],
            "mean_abs_weight", "mean_abs_weight", "LIME_baseline_vs_LIME_smote", top_k_values,
        ),
        compute_agreement_metrics(
            inputs["shap_importance"]["baseline"], inputs["lime_importance"]["baseline"],
            "mean_abs_shap", "mean_abs_weight", "SHAP_baseline_vs_LIME_baseline", top_k_values,
        ),
        compute_agreement_metrics(
            inputs["shap_importance"]["smote"], inputs["lime_importance"]["smote"],
            "mean_abs_shap", "mean_abs_weight", "SHAP_smote_vs_LIME_smote", top_k_values,
        ),
    ]
    logger.info("Metrics computed: %d global comparisons, %d agreement pairs", 2, len(agreement_results))

    local_comparison = compare_local_explanations(inputs, top_k=5)
    minority_results = analyze_minority_classes(inputs, minority_classes, top_k_values)

    comparison_long = build_comparison_long_dataframe(shap_global, lime_global)
    similarity_table = build_similarity_table(agreement_results)
    export_paths = save_comparison_outputs(comparison_long, similarity_table)
    logger.info(
        "Exports generated: %s, %s",
        export_paths["explanation_comparison"][0].name, export_paths["explanation_similarity"][0].name,
    )

    figures_dir = get_path_manager().figures_dir
    plot_ranking_comparison(shap_global, lime_global, figures_dir / "explanation_ranking_comparison.png")
    plot_similarity_metrics(agreement_results, figures_dir / "explanation_similarity_metrics.png")
    plot_minority_class_comparison(minority_results, figures_dir / "minority_class_comparison.png")
    plot_agreement_heatmap(agreement_results, figures_dir / "explanation_agreement_heatmap.png")

    save_comparison_tables(comparison_long, similarity_table, minority_results)

    shap_pair = agreement_results[0]
    lime_pair = agreement_results[1]
    key_observation = (
        f"SHAP's baseline-vs-SMOTE top-5 feature overlap was {shap_pair['topk_overlap'].get('top_5')} "
        f"(Spearman r = {shap_pair['spearman_correlation']}); LIME's was "
        f"{lime_pair['topk_overlap'].get('top_5')} (Spearman r = {lime_pair['spearman_correlation']})."
    )

    summary = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_version": VERSION,
        "key_observation": key_observation,
    }

    report = {
        "subset_size": len(inputs["sample_registry"]),
        "shap_feature_count": len(inputs["shap_importance"]["baseline"]),
        "lime_feature_count": len(
            set(inputs["lime_importance"]["baseline"]["feature"]) | set(inputs["lime_importance"]["smote"]["feature"])
        ),
        "intersection_feature_count": len(
            set(inputs["shap_importance"]["baseline"]["feature"]) & set(inputs["lime_importance"]["baseline"]["feature"])
        ),
        "global_top_n": global_top_n,
        "minority_classes": minority_classes,
        "shap_global": shap_global,
        "lime_global": lime_global,
        "agreement_results": agreement_results,
        "local_comparison": local_comparison,
        "minority_class_results": minority_results,
        "summary": summary,
    }
    save_comparison_report(report)

    logger.info("Comparison completed — 4 agreement pairs, %d minority classes analysed", len(minority_classes))
    return report
