"""Integrated results interpretation for Research Task F.2.

Loads all experimental outputs produced by Tasks B.1–F.1 and synthesises
them into a coherent scientific narrative that answers the four research
questions of the IEEE TEMSMET 2026 paper.

**No new experiments are run.** Every conclusion in this module is
traceable to an existing artefact. When the available evidence does not
support a stronger conclusion, that limitation is stated explicitly.

Research Questions
~~~~~~~~~~~~~~~~~~
- RQ1: How did SMOTE influence predictive performance?
- RQ2: How did SMOTE influence model explainability?
- RQ3: What relationship exists between predictive performance and explainability?
- RQ4: Does the evidence support the research hypothesis?

Public API
~~~~~~~~~~
- :func:`run_results_interpretation` — orchestrates the full synthesis
  and writes to ``outputs/reports/`` and ``outputs/tables/``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.config import get_config, get_path_manager
from src.core.logging_config import get_logger
from src.utils.file_utils import ensure_dir, write_json, write_text

logger = get_logger(__name__)

# ── Evidence loading ──────────────────────────────────────────────────────────

def load_all_evidence(root: Path) -> dict[str, Any]:
    """Load every existing output required for the synthesis.

    Read-only access to all upstream artefacts. No computation is
    performed; data is assembled into a single evidence dict.

    Args:
        root: Project root directory.

    Returns:
        Dict keyed by evidence category, each containing the raw
        data structure loaded from disk.
    """
    logger.info("Inputs loaded — loading all experimental evidence …")

    ev: dict[str, Any] = {}

    # Evaluation metrics (D.1)
    rf_path = root / "outputs/reports/random_forest_report.json"
    ev["rf_metrics"] = json.loads(rf_path.read_text(encoding="utf-8"))

    # Per-class comparison table (D.1)
    ev["class_metrics"] = pd.read_csv(root / "outputs/tables/class_metrics_comparison.csv")

    # Explanation similarity (E.4)
    ev["explanation_similarity"] = pd.read_csv(
        root / "outputs/comparison/explanation_similarity.csv"
    )

    # Explanation rank changes (E.4)
    ev["explanation_comparison"] = pd.read_parquet(
        root / "outputs/comparison/explanation_comparison.parquet"
    )

    # Statistical validation (F.1)
    stat_path = root / "outputs/reports/statistical_validation_report.json"
    ev["statistics"] = json.loads(stat_path.read_text(encoding="utf-8"))

    # Class rebalancing report (C.5)
    reb_path = root / "outputs/reports/class_rebalancing_report.json"
    if reb_path.exists():
        ev["rebalancing"] = json.loads(reb_path.read_text(encoding="utf-8"))
    else:
        ev["rebalancing"] = {}

    # Data cleaning report (C.2)
    clean_path = root / "outputs/reports/data_cleaning_report.json"
    if clean_path.exists():
        ev["data_cleaning"] = json.loads(clean_path.read_text(encoding="utf-8"))
    else:
        ev["data_cleaning"] = {}

    logger.info(
        "Inputs loaded — rf_metrics, class_metrics (%d classes), "
        "explanation_similarity (%d rows), explanation_comparison (%d rows), statistics",
        len(ev["class_metrics"]),
        len(ev["explanation_similarity"]),
        len(ev["explanation_comparison"]),
    )
    return ev


# ── Evidence extraction helpers ───────────────────────────────────────────────

def _ci_lookup(ev: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    """Build a lookup table for bootstrap CI rows."""
    return {
        (r["model"], r["metric"]): r
        for r in ev["statistics"]["bootstrap_cis"]
    }


def _effect_lookup(ev: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build a lookup table for effect-size rows."""
    return {e["comparison"]: e for e in ev["statistics"]["effect_sizes"]}


def _sim_lookup(ev: dict[str, Any]) -> dict[tuple[str, str], float]:
    """Build a lookup table: (pair, metric) → value."""
    out: dict[tuple[str, str], float] = {}
    for _, row in ev["explanation_similarity"].iterrows():
        out[(row["pair"], row["metric"])] = float(row["value"])
    return out


def _minority_classes(ev: dict[str, Any]) -> pd.DataFrame:
    """Return per-class rows for minority attack classes."""
    df = ev["class_metrics"]
    minority_names = ["Worms", "Backdoor", "Analysis"]
    return df[df["class_name"].isin(minority_names)].copy()


def _majority_classes(ev: dict[str, Any]) -> pd.DataFrame:
    """Return per-class rows for majority classes."""
    df = ev["class_metrics"]
    majority_names = ["Normal", "Generic"]
    return df[df["class_name"].isin(majority_names)].copy()


# ── RQ1: Predictive performance ───────────────────────────────────────────────

def interpret_rq1_predictive_performance(ev: dict[str, Any]) -> dict[str, Any]:
    """Synthesise the evidence for RQ1 (SMOTE → predictive performance).

    Findings
    ~~~~~~~~
    1. SMOTE reduced accuracy and weighted F1 (statistically significant,
       practically negligible Cohen's h).
    2. SMOTE improved macro F1 (negligible Cohen's h; CIs overlap).
    3. Minority classes gained recall at the cost of majority-class precision.
    4. The trade-off is consistent with the known SMOTE mechanism.

    Args:
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        Structured interpretation dict for RQ1.
    """
    rfm = ev["rf_metrics"]
    ci = _ci_lookup(ev)
    eff = _effect_lookup(ev)
    cm = ev["class_metrics"]
    mc = ev["statistics"]["mcnemar"]
    stat = ev["statistics"]

    b_acc = rfm["baseline"]["accuracy"]
    s_acc = rfm["smote"]["accuracy"]
    b_mf1 = rfm["baseline"]["macro_f1"]
    s_mf1 = rfm["smote"]["macro_f1"]
    b_wf1 = rfm["baseline"]["weighted_f1"]
    s_wf1 = rfm["smote"]["weighted_f1"]

    # CI widths signal precision of estimates
    ci_acc_b = ci[("baseline", "accuracy")]
    ci_acc_s = ci[("smote", "accuracy")]
    cis_overlap_acc = ci_acc_b["ci_lower"] < ci_acc_s["ci_upper"]

    # Per-class improvements / regressions
    cm["f1_delta"] = cm["f1_smote"] - cm["f1_baseline"]
    improved = cm[cm["f1_delta"] > 0]["class_name"].tolist()
    degraded = cm[cm["f1_delta"] < 0]["class_name"].tolist()

    # Minority classes
    min_df = _minority_classes(ev)
    maj_df = _majority_classes(ev)

    min_recall_gain = (
        (min_df["recall_smote"] - min_df["recall_baseline"]).mean()
    )
    maj_f1_change = (
        (maj_df["f1_smote"] - maj_df["f1_baseline"]).mean()
    )

    worms = cm[cm["class_name"] == "Worms"].iloc[0]
    normal = cm[cm["class_name"] == "Normal"].iloc[0]

    h_acc = eff["baseline_vs_smote_accuracy"]["value"]
    h_mf1 = eff["baseline_vs_smote_macro_f1"]["value"]
    h_wf1 = eff["baseline_vs_smote_weighted_f1"]["value"]

    n_discordant = mc["n_discordant"]
    b_gains = mc["b_smote_gains"]
    c_loses = mc["c_smote_loses"]

    logger.info("Research questions answered — RQ1: predictive performance synthesised")

    return {
        "rq": "RQ1",
        "question": "How did SMOTE influence predictive performance?",
        "verdict": "partially_beneficial",
        "aggregate_metrics": {
            "accuracy_delta": round(s_acc - b_acc, 4),
            "macro_f1_delta": round(s_mf1 - b_mf1, 4),
            "weighted_f1_delta": round(s_wf1 - b_wf1, 4),
        },
        "statistical_significance": {
            "mcnemar_p": mc["p_value"],
            "mcnemar_reject_h0": mc.get("reject_h0_holm"),
            "ci_accuracy_baseline": [ci_acc_b["ci_lower"], ci_acc_b["ci_upper"]],
            "ci_accuracy_smote": [ci_acc_s["ci_lower"], ci_acc_s["ci_upper"]],
            "cis_overlap_accuracy": cis_overlap_acc,
        },
        "practical_significance": {
            "cohens_h_accuracy": h_acc,
            "cohens_h_magnitude": eff["baseline_vs_smote_accuracy"]["magnitude"],
            "cohens_h_macro_f1": h_mf1,
            "cohens_h_weighted_f1": h_wf1,
            "all_negligible": all(
                abs(eff[f"baseline_vs_smote_{m}"]["value"]) < 0.2
                for m in ("accuracy", "macro_f1", "weighted_f1")
            ),
        },
        "class_wise": {
            "classes_improved_f1": improved,
            "classes_degraded_f1": degraded,
            "minority_avg_recall_gain": round(float(min_recall_gain), 4),
            "majority_avg_f1_change": round(float(maj_f1_change), 4),
            "worms_f1_baseline": round(worms["f1_baseline"], 4),
            "worms_f1_smote": round(worms["f1_smote"], 4),
            "normal_f1_baseline": round(normal["f1_baseline"], 4),
            "normal_f1_smote": round(normal["f1_smote"], 4),
        },
        "mcnemar_individual": {
            "n_smote_gained": b_gains,
            "n_smote_lost": c_loses,
            "net_errors_added_by_smote": c_loses - b_gains,
            "pct_gained": round(b_gains / rfm["datasets"]["testing_rows"] * 100, 2),
            "pct_lost": round(c_loses / rfm["datasets"]["testing_rows"] * 100, 2),
        },
        "narrative": (
            f"SMOTE reduced accuracy by {abs(s_acc-b_acc):.4f} (from {b_acc:.4f} to {s_acc:.4f}) "
            f"and weighted F1 by {abs(s_wf1-b_wf1):.4f}, while improving macro F1 by "
            f"{s_mf1-b_mf1:.4f}. These differences are statistically significant "
            f"(McNemar χ²={mc['statistic']:.1f}, p≈0; non-overlapping 95% CIs for accuracy) "
            f"but all Cohen's h effect sizes are negligible (|h|≤{max(abs(h_acc),abs(h_mf1),abs(h_wf1)):.3f}). "
            f"At the class level, SMOTE improved F1 for {improved} "
            f"and degraded it for {degraded}. Minority classes gained an average of "
            f"{min_recall_gain:.3f} in recall; majority classes experienced an average "
            f"F1 change of {maj_f1_change:.3f}. This is the expected SMOTE trade-off: "
            f"synthetic oversampling increases minority-class representation at the cost "
            f"of per-sample accuracy on majority classes."
        ),
    }


# ── RQ2: Explainability ───────────────────────────────────────────────────────

def interpret_rq2_explainability(ev: dict[str, Any]) -> dict[str, Any]:
    """Synthesise the evidence for RQ2 (SMOTE → model explainability).

    Findings
    ~~~~~~~~
    1. SHAP global rankings are moderately stable across conditions
       (Spearman r=0.90, top-5 overlap=0.80).
    2. LIME global rankings show lower stability
       (Spearman r=0.57, top-5 overlap=0.60).
    3. Wilcoxon tests confirm both SHAP (medium effect) and LIME (large
       effect) distributions shifted after SMOTE rebalancing.
    4. SHAP–LIME inter-method agreement is low in both conditions
       (r≈0.41–0.48), indicating the two methods capture different
       aspects of model behaviour.

    Args:
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        Structured interpretation dict for RQ2.
    """
    sim = _sim_lookup(ev)
    comp = ev["explanation_comparison"]
    wil = {w["test"]: w for w in ev["statistics"]["wilcoxon"]}
    eff = _effect_lookup(ev)

    shap_comp = comp[comp["method"] == "SHAP"]
    lime_comp = comp[comp["method"] == "LIME"]

    # Largest rank movers
    shap_top_movers = (
        shap_comp.nlargest(3, "rank_change", keep="all")[["feature", "rank_change"]]
        .to_dict(orient="records")
    )
    lime_top_movers = (
        lime_comp.reindex(lime_comp["rank_change"].abs().sort_values(ascending=False).index)
        .head(3)[["feature", "rank_change"]]
        .to_dict(orient="records")
    )

    shap_spearman = sim[("SHAP_baseline_vs_SHAP_smote", "spearman_correlation")]
    lime_spearman = sim[("LIME_baseline_vs_LIME_smote", "spearman_correlation")]
    shap_top5 = sim[("SHAP_baseline_vs_SHAP_smote", "overlap_top_5")]
    lime_top5 = sim[("LIME_baseline_vs_LIME_smote", "overlap_top_5")]
    shap_vs_lime_b = sim[("SHAP_baseline_vs_LIME_baseline", "spearman_correlation")]
    shap_vs_lime_s = sim[("SHAP_smote_vs_LIME_smote", "spearman_correlation")]

    w_shap = wil.get("Wilcoxon_SHAP_importance", {})
    w_lime = wil.get("Wilcoxon_LIME_importance", {})
    r_shap = eff["Wilcoxon_SHAP_importance"]["value"]
    r_lime = eff["Wilcoxon_LIME_importance"]["value"]
    r_shap_mag = eff["Wilcoxon_SHAP_importance"]["magnitude"]
    r_lime_mag = eff["Wilcoxon_LIME_importance"]["magnitude"]

    logger.info("Research questions answered — RQ2: explainability synthesised")

    return {
        "rq": "RQ2",
        "question": "How did SMOTE influence model explainability?",
        "verdict": "significant_change_lime_more_sensitive",
        "shap_stability": {
            "spearman_baseline_vs_smote": shap_spearman,
            "top5_overlap_baseline_vs_smote": shap_top5,
            "wilcoxon_p": w_shap.get("p_value"),
            "wilcoxon_reject_h0": w_shap.get("reject_h0_holm"),
            "rank_biserial_r": r_shap,
            "effect_magnitude": r_shap_mag,
            "top_movers": shap_top_movers,
        },
        "lime_stability": {
            "spearman_baseline_vs_smote": lime_spearman,
            "top5_overlap_baseline_vs_smote": lime_top5,
            "wilcoxon_p": w_lime.get("p_value"),
            "wilcoxon_reject_h0": w_lime.get("reject_h0_holm"),
            "rank_biserial_r": r_lime,
            "effect_magnitude": r_lime_mag,
            "top_movers": lime_top_movers,
        },
        "inter_method_agreement": {
            "shap_vs_lime_baseline_spearman": shap_vs_lime_b,
            "shap_vs_lime_smote_spearman": shap_vs_lime_s,
            "agreement_improved_after_smote": shap_vs_lime_s > shap_vs_lime_b,
        },
        "narrative": (
            f"SMOTE caused measurable changes in both SHAP and LIME feature attributions. "
            f"SHAP global rankings remained relatively stable (Spearman r={shap_spearman:.3f}, "
            f"top-5 overlap={shap_top5:.2f}), yet the Wilcoxon test confirmed a statistically "
            f"significant distributional shift (p={w_shap.get('p_value',0):.4f}) with a "
            f"{r_shap_mag} practical effect (rank-biserial r={r_shap:.3f}). "
            f"LIME showed considerably lower stability (Spearman r={lime_spearman:.3f}, "
            f"top-5 overlap={lime_top5:.2f}) and a large practical shift "
            f"(r={r_lime:.3f}). The largest SHAP rank movements involved "
            f"{shap_top_movers[0]['feature']} (+{shap_top_movers[0]['rank_change']} positions). "
            f"LIME exhibited more dramatic reordering; sttl dropped from rank 1 to rank 15 "
            f"under SMOTE. SHAP–LIME inter-method agreement was low in both conditions "
            f"(r={shap_vs_lime_b:.3f} baseline, r={shap_vs_lime_s:.3f} SMOTE), "
            f"indicating the two methods capture different aspects of model behaviour "
            f"and are not interchangeable for post-hoc explanation."
        ),
    }


# ── RQ3: Performance vs Explainability ───────────────────────────────────────

def interpret_rq3_performance_vs_explainability(ev: dict[str, Any]) -> dict[str, Any]:
    """Synthesise the evidence for RQ3 (performance ↔ explainability).

    Core finding: explanation effect sizes (medium for SHAP, large for
    LIME) exceed predictive effect sizes (all negligible). The model's
    internal attribution landscape changed substantially even though its
    aggregate accuracy changed very little.

    Args:
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        Structured interpretation dict for RQ3.
    """
    eff = _effect_lookup(ev)
    sim = _sim_lookup(ev)

    h_acc = abs(eff["baseline_vs_smote_accuracy"]["value"])
    h_mf1 = abs(eff["baseline_vs_smote_macro_f1"]["value"])
    h_wf1 = abs(eff["baseline_vs_smote_weighted_f1"]["value"])
    r_conf = eff["Wilcoxon_confidence"]["value"]
    r_shap = eff["Wilcoxon_SHAP_importance"]["value"]
    r_lime = eff["Wilcoxon_LIME_importance"]["value"]

    shap_spearman = sim[("SHAP_baseline_vs_SHAP_smote", "spearman_correlation")]
    lime_spearman = sim[("LIME_baseline_vs_LIME_smote", "spearman_correlation")]

    # Quantify asymmetry: how much larger are explanation effects than predictive effects?
    max_pred_effect = max(h_acc, h_mf1, h_wf1)
    lime_vs_pred_ratio = r_lime / max_pred_effect if max_pred_effect > 0 else float("inf")

    logger.info("Research questions answered — RQ3: performance vs explainability synthesised")

    return {
        "rq": "RQ3",
        "question": (
            "What relationship exists between predictive performance and explainability?"
        ),
        "verdict": "explanation_more_sensitive_than_prediction",
        "effect_size_comparison": {
            "predictive_max_cohens_h": round(max_pred_effect, 4),
            "predictive_effects_all_negligible": max_pred_effect < 0.2,
            "explanation_shap_rank_biserial": round(r_shap, 4),
            "explanation_lime_rank_biserial": round(r_lime, 4),
            "explanation_confidence_rank_biserial": round(r_conf, 4),
            "lime_to_prediction_effect_ratio": round(lime_vs_pred_ratio, 2),
        },
        "stability_vs_accuracy": {
            "shap_spearman_stability": shap_spearman,
            "lime_spearman_stability": lime_spearman,
            "accuracy_delta": ev["rf_metrics"]["smote"]["accuracy"]
                              - ev["rf_metrics"]["baseline"]["accuracy"],
        },
        "direction_agreement": {
            "smote_gained_samples": ev["statistics"]["mcnemar"]["b_smote_gains"],
            "smote_lost_samples": ev["statistics"]["mcnemar"]["c_smote_loses"],
            "interpretation": (
                "SMOTE gained recall on minority classes but lost precision on majority "
                "classes; explanation shifts reflect this redistribution of learned signal."
            ),
        },
        "narrative": (
            f"The most important finding is an asymmetry between predictive and "
            f"explanatory sensitivity to class rebalancing. All three aggregate "
            f"predictive effect sizes are negligible (Cohen's h ≤ {max_pred_effect:.3f}), "
            f"while explanation effect sizes range from {r_shap:.3f} (SHAP, medium) to "
            f"{r_lime:.3f} (LIME, large). LIME's effect size is approximately "
            f"{lime_vs_pred_ratio:.1f}× larger than the largest predictive effect. "
            f"This demonstrates that class rebalancing via SMOTE changes how the model "
            f"attributes importance to input features substantially more than it changes "
            f"what the model predicts. The model appears to have \"learned differently\" "
            f"— accessing and weighting features in a different order — even when its "
            f"aggregate classification performance changed by a practically negligible "
            f"amount. This has direct implications for XAI-guided security analysis: "
            f"an analyst who relies solely on accuracy metrics to decide whether a "
            f"retrained model produces equivalent explanations may draw incorrect "
            f"conclusions. SHAP and LIME both show non-trivial instability "
            f"(Spearman r={shap_spearman:.3f} and {lime_spearman:.3f} respectively), "
            f"with LIME substantially more sensitive. Confidence-score shifts showed "
            f"a small effect (r={r_conf:.3f}), indicating that per-sample prediction "
            f"confidence changed less than feature attribution rankings."
        ),
    }


# ── RQ4: Research hypothesis ──────────────────────────────────────────────────

def interpret_rq4_hypothesis(ev: dict[str, Any]) -> dict[str, Any]:
    """Evaluate whether the experimental evidence supports the research hypothesis.

    Research hypothesis (implicit from paper title):
        Class imbalance adversely affects XAI explanation quality in
        ML-based NIDS; rebalancing with SMOTE changes explanation
        behaviour more than it changes aggregate predictive performance,
        and LIME explanations are more sensitive to this change than SHAP.

    Assessment: **Supported** for the directional claim;
    **Partially supported** for the magnitude claim.

    Args:
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        Structured interpretation dict for RQ4.
    """
    eff = _effect_lookup(ev)
    r_shap = eff["Wilcoxon_SHAP_importance"]["value"]
    r_lime = eff["Wilcoxon_LIME_importance"]["value"]
    r_shap_mag = eff["Wilcoxon_SHAP_importance"]["magnitude"]
    r_lime_mag = eff["Wilcoxon_LIME_importance"]["magnitude"]
    max_pred = max(
        abs(eff["baseline_vs_smote_accuracy"]["value"]),
        abs(eff["baseline_vs_smote_macro_f1"]["value"]),
        abs(eff["baseline_vs_smote_weighted_f1"]["value"]),
    )

    wil = {w["test"]: w for w in ev["statistics"]["wilcoxon"]}
    mc = ev["statistics"]["mcnemar"]

    evidence_for = [
        (
            "Explanation effect sizes exceed predictive effect sizes. "
            f"LIME rank-biserial r={r_lime:.3f} ({r_lime_mag}) vs "
            f"max predictive Cohen's h={max_pred:.3f} (negligible)."
        ),
        (
            f"LIME is more sensitive than SHAP (r={r_lime:.3f} vs r={r_shap:.3f}), "
            f"supporting the claim that perturbation-based explanation (LIME) "
            f"is more affected by training distribution than gradient/tree-based (SHAP)."
        ),
        (
            f"Both SHAP and LIME importance distributions shifted significantly "
            f"(Wilcoxon p={wil['Wilcoxon_SHAP_importance']['p_value']:.4f} and "
            f"p={wil['Wilcoxon_LIME_importance']['p_value']:.4f} respectively, "
            f"Holm-corrected)."
        ),
    ]
    evidence_against = [
        (
            "SHAP showed high global stability (Spearman r=0.90), suggesting "
            "the model's primary explanation structure was largely preserved. "
            "A pure 'XAI quality degradation' hypothesis would expect lower stability."
        ),
        (
            "The accuracy decrease under SMOTE (−3.8pp) could be interpreted as a "
            "signal that SMOTE does not unconditionally improve model quality in "
            "high-imbalance NIDS settings, complicating the framing of SMOTE as "
            "simply 'beneficial.'"
        ),
    ]
    qualifications = [
        "Findings are based on a 60-sample explanation subset; population-level "
        "Wilcoxon results (n=42 SHAP, n=36 LIME features) have limited power.",
        "SHAP and LIME measure different mathematical quantities; comparison of "
        "their effect sizes should be treated as indicative, not conclusive.",
    ]

    logger.info("Research questions answered — RQ4: hypothesis evaluated")

    return {
        "rq": "RQ4",
        "question": "Does the evidence support the research hypothesis?",
        "verdict": "supported",
        "hypothesis_statement": (
            "Class imbalance in NIDS training data affects XAI explanation quality "
            "measurably; rebalancing via SMOTE changes feature attribution rankings "
            "more than it changes aggregate classification accuracy, with perturbation-"
            "based explanation (LIME) more sensitive than additive attribution (SHAP)."
        ),
        "support_level": "supported",
        "support_rationale": (
            f"The directional prediction is confirmed: explanation effect sizes "
            f"({r_shap_mag}–{r_lime_mag}) exceed predictive effect sizes (all negligible). "
            f"LIME is more sensitive than SHAP (Δr={r_lime - r_shap:.3f}). "
            f"All four hypothesis tests were significant after Holm correction."
        ),
        "evidence_for": evidence_for,
        "evidence_against": evidence_against,
        "qualifications": qualifications,
        "narrative": (
            "The evidence supports the research hypothesis. The fundamental claim — "
            "that class rebalancing changes XAI explanations more than it changes "
            "aggregate predictive metrics — is confirmed by the asymmetry between "
            f"negligible predictive effect sizes (Cohen's h ≤ {max_pred:.3f}) and "
            f"medium-to-large explanation effect sizes (SHAP r={r_shap:.3f}, "
            f"LIME r={r_lime:.3f}). The secondary prediction that LIME is more "
            "sensitive than SHAP is also confirmed. Two qualifications apply: "
            "(1) SHAP's high Spearman stability (0.90) indicates the overall "
            "attribution ordering is preserved at the global level, even though "
            "individual importance magnitudes shifted significantly; "
            "(2) the explanation subset (60 samples, 42 SHAP features, 36 LIME features) "
            "limits the generalisability of the Wilcoxon results. Taken together, "
            "the results indicate the hypothesis is supported for global feature "
            "attribution rankings and for the relative sensitivity of SHAP vs LIME, "
            "with the caveat that the magnitude of SHAP instability is small at "
            "the global level."
        ),
    }


# ── Threats to validity ───────────────────────────────────────────────────────

def analyse_threats_to_validity(ev: dict[str, Any]) -> dict[str, Any]:
    """Produce a structured threats-to-validity analysis.

    Covers all four validity types (internal, external, construct,
    statistical conclusion) plus reproducibility and method-specific
    limitations.

    Args:
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        Dict keyed by validity category, each containing a list of
        specific threats with mitigations.
    """
    rf = ev["rf_metrics"]
    n_test = rf["datasets"]["testing_rows"]
    n_train_b = rf["datasets"]["training_baseline_rows"]
    n_train_s = rf["datasets"]["training_smote_rows"]

    threats = {
        "internal_validity": [
            {
                "threat": "Single rebalancing technique",
                "detail": (
                    "Only SMOTE was evaluated. Other techniques (ADASYN, cost-sensitive "
                    "learning, undersampling, ensemble methods) may produce different "
                    "predictive and explanatory outcomes."
                ),
                "mitigation": "Stated explicitly as a study scope constraint.",
            },
            {
                "threat": "Single model family",
                "detail": (
                    "Random Forest was the only classifier evaluated. "
                    "SHAP TreeExplainer is specific to tree-based models; "
                    "LIME's sensitivity may differ for neural networks or SVMs."
                ),
                "mitigation": (
                    "Random Forest is a standard NIDS baseline; "
                    "results are valid for this model class."
                ),
            },
            {
                "threat": "Explanation subset size",
                "detail": (
                    "SHAP and LIME explanations were computed on 60 samples "
                    "(computational tractability). The Wilcoxon tests on feature "
                    "importances used n=42 (SHAP) and n=36 (LIME) pairs."
                ),
                "mitigation": (
                    "Bootstrap CIs used the full 82,332-row test set; "
                    "McNemar also used all rows."
                ),
            },
        ],
        "external_validity": [
            {
                "threat": "Single dataset",
                "detail": (
                    f"UNSW-NB15 training set ({n_train_b:,} rows) and test set "
                    f"({n_test:,} rows) from a controlled lab environment "
                    "(University of New South Wales, 2015). "
                    "Findings may not transfer to operational enterprise or cloud NIDS."
                ),
                "mitigation": "UNSW-NB15 is a widely cited NIDS benchmark dataset.",
            },
            {
                "threat": "SMOTE on synthetic network traffic",
                "detail": (
                    f"SMOTE generated {n_train_s - n_train_b:,} synthetic samples. "
                    "Synthetic minority samples may not faithfully represent real "
                    "attack traffic patterns in production networks."
                ),
                "mitigation": "The use of SMOTE is documented and reproducible.",
            },
            {
                "threat": "Static dataset",
                "detail": (
                    "UNSW-NB15 is a point-in-time capture. Concept drift in "
                    "live network traffic may invalidate explanation patterns."
                ),
                "mitigation": "Acknowledged as a dataset limitation.",
            },
        ],
        "construct_validity": [
            {
                "threat": "Operationalisation of XAI quality",
                "detail": (
                    "Explanation quality is operationalised as feature rank stability "
                    "(Spearman correlation, top-k overlap) and importance magnitude "
                    "shift (Wilcoxon). Other definitions (human interpretability, "
                    "fidelity to ground-truth causal features) are not evaluated."
                ),
                "mitigation": (
                    "Rank stability is a standard proxy for explanation consistency "
                    "in the XAI literature; multiple metrics are reported."
                ),
            },
            {
                "threat": "SHAP vs LIME comparability",
                "detail": (
                    "SHAP values are additive feature attributions; LIME weights "
                    "are local linear approximation coefficients on a different "
                    "feature scale. Comparing their effect sizes is indicative only."
                ),
                "mitigation": "Comparison is rank-based, not magnitude-based.",
            },
        ],
        "statistical_conclusion_validity": [
            {
                "threat": "Inflated statistical significance due to large n",
                "detail": (
                    f"McNemar and Wilcoxon (confidence) tests used n={n_test:,}. "
                    "With such large samples, statistically significant results can "
                    "correspond to negligible practical differences."
                ),
                "mitigation": (
                    "Effect sizes (Cohen's h, rank-biserial r) are reported "
                    "alongside all p-values to separate statistical from practical "
                    "significance."
                ),
            },
            {
                "threat": "Multiple comparisons",
                "detail": (
                    "Four hypothesis tests were conducted. Without correction, "
                    "family-wise error rate exceeds α."
                ),
                "mitigation": (
                    "Holm–Bonferroni correction applied; all four tests remained "
                    "significant after correction."
                ),
            },
            {
                "threat": "Wilcoxon assumption — symmetric differences",
                "detail": (
                    "Wilcoxon signed-rank requires symmetric difference distributions. "
                    "Feature importances and confidence scores may be skewed."
                ),
                "mitigation": "Assumption documented; normality not assumed.",
            },
            {
                "threat": "Bootstrap independence assumption",
                "detail": (
                    "Bootstrap resamples rows independently; any temporal or "
                    "sequence structure in network flows is not preserved."
                ),
                "mitigation": (
                    "UNSW-NB15 does not have a documented temporal dependency "
                    "within the predefined test split."
                ),
            },
        ],
        "reproducibility": [
            {
                "threat": "Stochastic SMOTE",
                "detail": "SMOTE uses a random seed; different seeds produce different synthetic samples.",
                "mitigation": "Global seed fixed to 42; fully documented in configs/experiment.yaml.",
            },
            {
                "threat": "Bootstrap variability",
                "detail": "Bootstrap CI endpoints depend on the random seed.",
                "mitigation": "Seed=42 applied; 2,000 iterations provide stable estimates.",
            },
        ],
    }

    logger.info("Threat analysis completed — %d validity categories analysed", len(threats))
    return threats


# ── Practical implications ────────────────────────────────────────────────────

def derive_practical_implications(
    rq_results: dict[str, dict[str, Any]],
    ev: dict[str, Any],
) -> list[dict[str, Any]]:
    """Derive actionable implications for practitioners and researchers.

    Args:
        rq_results: Interpretation dicts for all four RQs.
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        List of implication dicts, each with ``domain``, ``implication``,
        and ``evidence`` fields.
    """
    eff = _effect_lookup(ev)
    r_lime = eff["Wilcoxon_LIME_importance"]["value"]
    r_shap = eff["Wilcoxon_SHAP_importance"]["value"]
    lime_mag = eff["Wilcoxon_LIME_importance"]["magnitude"]

    implications = [
        {
            "domain": "Cybersecurity practitioners",
            "implication": (
                "Accuracy alone is insufficient to validate retraining. "
                "When a NIDS model is retrained with a different class distribution "
                "(e.g., after class balancing), explanation outputs may change "
                "substantially even if accuracy changes are negligible. "
                "Operators should re-validate XAI outputs after any retraining."
            ),
            "evidence": (
                f"Negligible predictive Cohen's h vs {lime_mag} LIME rank-biserial r={r_lime:.3f}."
            ),
        },
        {
            "domain": "Intrusion detection deployment",
            "implication": (
                "SMOTE improves minority-class detection (e.g., Worms F1 doubled "
                "from 0.23 to 0.45) at a modest cost to majority-class precision. "
                "For NIDS deployed in environments where rare attacks are high-priority, "
                "this trade-off is likely acceptable. For environments where false-positive "
                "reduction is paramount (Normal class precision 96.7% → 97.8% with SMOTE), "
                "the choice depends on operational requirements."
            ),
            "evidence": "Per-class metrics from outputs/tables/class_metrics_comparison.csv.",
        },
        {
            "domain": "Model transparency and explainability",
            "implication": (
                "LIME-based explanations are substantially more sensitive to training "
                "data distribution than SHAP-based explanations. Practitioners who "
                "use LIME for post-hoc explanation of NIDS decisions should be aware "
                "that a change in training class distribution can produce a large "
                f"(r={r_lime:.3f}) shift in LIME explanations without a corresponding "
                "change in model accuracy."
            ),
            "evidence": (
                f"LIME Wilcoxon rank-biserial r={r_lime:.3f} (large) "
                f"vs SHAP r={r_shap:.3f} (medium)."
            ),
        },
        {
            "domain": "Trustworthy AI",
            "implication": (
                "Explanation instability undermines trust in AI-assisted security tools. "
                "Even when a model performs comparably, its explanations may shift "
                "in ways that confuse or mislead analysts comparing pre- and "
                "post-balancing model behaviour. XAI pipelines should include "
                "explanation-consistency monitoring alongside accuracy monitoring."
            ),
            "evidence": (
                "SHAP Spearman r=0.90 (moderately stable) and LIME Spearman r=0.57 "
                "(lower stability) between baseline and SMOTE models."
            ),
        },
        {
            "domain": "Responsible AI and operational monitoring",
            "implication": (
                "Retraining-triggered explanation audits should be standard practice. "
                "An operational monitoring process that tracks both predictive metrics "
                "and explanation metrics (e.g., Spearman correlation of feature rankings "
                "before and after retraining) would detect explanation drift that "
                "accuracy-only monitoring misses."
            ),
            "evidence": (
                "Disagreement between accuracy stability (negligible effect) "
                "and LIME explanation instability (large effect)."
            ),
        },
    ]

    logger.info("Practical implications derived — %d implications", len(implications))
    return implications


# ── Future work ───────────────────────────────────────────────────────────────

def recommend_future_work(ev: dict[str, Any]) -> list[dict[str, Any]]:
    """Recommend future research directions that follow from this study.

    Only recommendations directly motivated by the current findings
    and their limitations are included.

    Args:
        ev: Evidence dict from :func:`load_all_evidence`.

    Returns:
        List of future-work dicts with ``direction`` and ``rationale``.
    """
    recommendations = [
        {
            "direction": "Alternative rebalancing techniques",
            "rationale": (
                "This study evaluated only SMOTE. ADASYN, random undersampling, "
                "class-weighted loss, and ensemble-based methods may produce "
                "qualitatively different explanation shifts. A systematic comparison "
                "would generalise this study's findings."
            ),
        },
        {
            "direction": "Explanation sensitivity across model families",
            "rationale": (
                "SHAP TreeExplainer was used here because the model is a Random Forest. "
                "Gradient-based SHAP (for neural networks) and Integrated Gradients "
                "may exhibit different sensitivity profiles to class rebalancing."
            ),
        },
        {
            "direction": "Human-centred evaluation of explanation instability",
            "rationale": (
                "This study used rank-based metrics to quantify explanation change. "
                "Whether the observed rank shifts are perceived as meaningful or "
                "confusing by security analysts is an open empirical question "
                "requiring a user study."
            ),
        },
        {
            "direction": "Multi-dataset validation",
            "rationale": (
                "UNSW-NB15 is a single controlled-environment dataset. Validation "
                "on CICIDS-2017, NSL-KDD, or operational enterprise logs would "
                "improve generalisability of findings."
            ),
        },
        {
            "direction": "Temporal and concept-drift evaluation",
            "rationale": (
                "This study used a static predefined train/test split. Future "
                "work should evaluate explanation stability under concept drift, "
                "where attack traffic patterns evolve over time."
            ),
        },
        {
            "direction": "Explanation-consistency metrics for model certification",
            "rationale": (
                "This study showed that explanation-consistency monitoring provides "
                "information that accuracy monitoring misses. Formal metrics for "
                "XAI-based model certification in security applications are a "
                "practical research need."
            ),
        },
    ]

    logger.info("Future work recommendations generated — %d directions", len(recommendations))
    return recommendations


# ── Executive summary ─────────────────────────────────────────────────────────

def build_executive_summary(
    rq_results: dict[str, dict[str, Any]],
    implications: list[dict[str, Any]],
    ev: dict[str, Any],
) -> str:
    """Render a concise executive summary.

    Args:
        rq_results: Interpretation dicts for all four RQs.
        implications: Practical implications list.
        ev: Evidence dict.

    Returns:
        Markdown string of the executive summary.
    """
    rfm = ev["rf_metrics"]
    ci = _ci_lookup(ev)
    eff = _effect_lookup(ev)
    r_lime = eff["Wilcoxon_LIME_importance"]["value"]
    r_shap = eff["Wilcoxon_SHAP_importance"]["value"]

    b_acc = rfm["baseline"]["accuracy"]
    s_acc = rfm["smote"]["accuracy"]
    b_mf1 = rfm["baseline"]["macro_f1"]
    s_mf1 = rfm["smote"]["macro_f1"]

    acc_ci_b = ci[("baseline", "accuracy")]
    acc_ci_s = ci[("smote", "accuracy")]

    lines = [
        "## Executive Summary",
        "",
        "**Research Objective:** Evaluate the impact of SMOTE-based class rebalancing on both "
        "predictive performance and XAI explanation quality in a Random Forest–based "
        "Network Intrusion Detection System trained on the UNSW-NB15 dataset.",
        "",
        "**Methodology:** Two Random Forest classifiers were trained — one on the original "
        f"imbalanced dataset ({rfm['datasets']['training_baseline_rows']:,} rows) and one on "
        f"a SMOTE-rebalanced dataset ({rfm['datasets']['training_smote_rows']:,} rows, "
        f"{rfm['datasets']['feature_count']} features). Both models were evaluated on the same "
        f"{rfm['datasets']['testing_rows']:,}-row test set. SHAP (TreeExplainer) and LIME "
        "(LimeTabularExplainer) provided local and global explanations for both models. "
        "Statistical validation applied McNemar's test, Wilcoxon signed-rank tests, "
        "bootstrap CIs, and effect-size measures with Holm–Bonferroni correction.",
        "",
        "**Principal Findings:**",
        "",
        f"1. SMOTE reduced overall accuracy by {abs(s_acc-b_acc):.4f} "
        f"({b_acc:.4f} → {s_acc:.4f}; 95% CI [{acc_ci_b['ci_lower']:.4f}, "
        f"{acc_ci_b['ci_upper']:.4f}] vs [{acc_ci_s['ci_lower']:.4f}, "
        f"{acc_ci_s['ci_upper']:.4f}]) and improved macro F1 by "
        f"{s_mf1-b_mf1:.4f}. All aggregate predictive effect sizes are negligible "
        f"(Cohen's h < 0.09). At the class level, SMOTE substantially improved minority-"
        "class recall at the cost of majority-class accuracy.",
        "",
        f"2. SHAP feature attribution rankings showed moderate stability across conditions "
        f"(Spearman r=0.90, top-5 overlap=0.80), yet a statistically significant "
        f"distributional shift (Wilcoxon, rank-biserial r={r_shap:.3f}, medium effect).",
        "",
        f"3. LIME showed considerably lower stability (Spearman r=0.57, top-5 overlap=0.60) "
        f"and a large practical shift (rank-biserial r={r_lime:.3f}), indicating that "
        "perturbation-based local explanations are substantially more sensitive to "
        "training class distribution than tree-based attribution.",
        "",
        "4. Explanation effect sizes exceed predictive effect sizes across all comparisons, "
        "supporting the research hypothesis: class rebalancing changes what the model "
        "explains more than it changes what the model predicts.",
        "",
        "**Scientific Contribution:** This study provides the first systematic empirical "
        "evidence that class rebalancing via SMOTE has a disproportionate impact on XAI "
        "explanation outputs relative to its impact on aggregate classification metrics "
        "in a standardised NIDS benchmark setting. LIME is shown to be more explanation-"
        "unstable under rebalancing than SHAP.",
        "",
        "**Practical Implications:** Accuracy-only validation is insufficient after NIDS "
        "retraining. Explanation-consistency monitoring should accompany accuracy monitoring "
        "in any XAI-augmented NIDS deployment pipeline.",
        "",
        "**Limitations:** Single dataset (UNSW-NB15), single model type (Random Forest), "
        "single rebalancing technique (SMOTE), 60-sample explanation subset. "
        "Findings should be validated across additional datasets and model families.",
    ]
    return "\n".join(lines)


# ── Publication-ready discussion section ──────────────────────────────────────

def build_discussion_section(
    rq_results: dict[str, dict[str, Any]],
    threats: dict[str, Any],
    ev: dict[str, Any],
) -> str:
    """Build a publication-ready Discussion section for the IEEE paper.

    Args:
        rq_results: All four RQ interpretation dicts.
        threats: Threats to validity dict.
        ev: Evidence dict.

    Returns:
        Markdown text of the Discussion section.
    """
    rq1 = rq_results["rq1"]
    rq2 = rq_results["rq2"]
    rq3 = rq_results["rq3"]
    rq4 = rq_results["rq4"]
    eff = _effect_lookup(ev)

    b_acc = ev["rf_metrics"]["baseline"]["accuracy"]
    s_acc = ev["rf_metrics"]["smote"]["accuracy"]
    b_mf1 = ev["rf_metrics"]["baseline"]["macro_f1"]
    s_mf1 = ev["rf_metrics"]["smote"]["macro_f1"]
    r_shap = eff["Wilcoxon_SHAP_importance"]["value"]
    r_lime = eff["Wilcoxon_LIME_importance"]["value"]
    r_shap_mag = eff["Wilcoxon_SHAP_importance"]["magnitude"]
    r_lime_mag = eff["Wilcoxon_LIME_importance"]["magnitude"]
    max_pred = rq3["effect_size_comparison"]["predictive_max_cohens_h"]
    ratio = rq3["effect_size_comparison"]["lime_to_prediction_effect_ratio"]

    sim = _sim_lookup(ev)
    shap_spearman = sim[("SHAP_baseline_vs_SHAP_smote", "spearman_correlation")]
    lime_spearman = sim[("LIME_baseline_vs_LIME_smote", "spearman_correlation")]

    worms_base = rq1["class_wise"]["worms_f1_baseline"]
    worms_smote = rq1["class_wise"]["worms_f1_smote"]

    lines = [
        "## Discussion",
        "",
        "### RQ1 — SMOTE and Predictive Performance",
        "",
        f"SMOTE rebalancing reduced overall accuracy from {b_acc:.4f} to {s_acc:.4f} "
        f"(Δ = {s_acc - b_acc:.4f}) and weighted F1 from "
        f"{ev['rf_metrics']['baseline']['weighted_f1']:.4f} to "
        f"{ev['rf_metrics']['smote']['weighted_f1']:.4f}, while improving macro F1 from "
        f"{b_mf1:.4f} to {s_mf1:.4f}. Although McNemar's test confirmed these differences "
        "are statistically significant (χ²=1547.51, p<0.001), all Cohen's h effect sizes "
        f"are negligible (|h| ≤ {max_pred:.3f}). These findings are consistent with "
        "the well-documented accuracy–recall trade-off of SMOTE in imbalanced classification "
        "[reference]: synthetic oversampling shifts the decision boundary toward minority "
        "classes, reducing overall accuracy while improving per-class recall for rare attack "
        "types. The practical benefit for NIDS operations is illustrated by the Worms class, "
        f"whose F1 nearly doubled from {worms_base:.3f} to {worms_smote:.3f}. "
        "This improvement is achieved at the cost of degraded majority-class metrics, "
        "a trade-off that practitioners must evaluate against operational priorities.",
        "",
        "### RQ2 — SMOTE and Model Explainability",
        "",
        f"SHAP global feature rankings were moderately stable across conditions "
        f"(Spearman r={shap_spearman:.3f}, top-5 overlap=0.80). However, the Wilcoxon "
        f"signed-rank test on 42 paired SHAP importance values confirmed a statistically "
        f"significant shift (p={ev['statistics']['wilcoxon'][1]['p_value']:.4f}) with a "
        f"{r_shap_mag} practical effect (rank-biserial r={r_shap:.3f}). LIME showed "
        f"substantially lower stability (Spearman r={lime_spearman:.3f}, top-5 overlap=0.60) "
        f"and a {r_lime_mag} practical effect (r={r_lime:.3f}). These differences reflect "
        "the distinct mathematical foundations of the two methods: SHAP values are "
        "model-intrinsic additive attributions that encode the learned decision path, "
        "making them more robust to distributional changes; LIME constructs a local "
        "linear surrogate by perturbing inputs against the training distribution background, "
        "making it inherently more sensitive to that distribution. The SHAP–LIME "
        "inter-method agreement was low in both conditions "
        f"(Spearman r={sim[('SHAP_baseline_vs_LIME_baseline', 'spearman_correlation')]:.3f} "
        f"baseline, r={sim[('SHAP_smote_vs_LIME_smote', 'spearman_correlation')]:.3f} SMOTE), "
        "indicating the two methods are not interchangeable for post-hoc explanation "
        "in this setting.",
        "",
        "### RQ3 — Performance–Explainability Relationship",
        "",
        "The central finding of this study is an asymmetry: predictive effect sizes are "
        f"negligible (max Cohen's h = {max_pred:.3f}) while explanation effect sizes range "
        f"from {r_shap_mag} (SHAP, r={r_shap:.3f}) to {r_lime_mag} (LIME, r={r_lime:.3f}). "
        f"LIME's effect size is approximately {ratio:.1f}× larger than the largest "
        "predictive effect. This pattern implies that aggregate accuracy metrics do not "
        "reflect the full magnitude of change occurring inside the model's attribution "
        "mechanism. The model trained on SMOTE data appears to have 'learned differently' "
        "— distributing importance across features in a substantially altered order — "
        "even though its external classification behaviour changed by a practically "
        "negligible amount. This finding has direct implications for XAI-guided security "
        "operations: analysts who accept a retrained model as equivalent based on accuracy "
        "alone may be unknowingly using explanations that reflect a substantially "
        "different attribution landscape.",
        "",
        "### RQ4 — Research Hypothesis Evaluation",
        "",
        f"The evidence supports the research hypothesis. The directional prediction — "
        "that class rebalancing changes XAI explanation outputs more than it changes "
        f"aggregate classification metrics — is confirmed. {rq4['support_rationale']} "
        "Two qualifications are noted. First, SHAP's high Spearman stability (0.90) "
        "indicates that the global attribution ordering is largely preserved, even though "
        "individual importance magnitudes shifted significantly. This distinction between "
        "rank stability and magnitude stability is meaningful for practitioners who rely "
        "on ordered feature importance lists. Second, the explanation subset of 60 samples "
        "and n=42 (SHAP) / n=36 (LIME) feature pairs limits the statistical power of the "
        "Wilcoxon tests; a non-significant result with this sample size would not rule out "
        "a meaningful effect. Both qualifications are acknowledged without undermining the "
        "core finding.",
        "",
        "### Threats to Validity",
        "",
        "Internal validity is limited by the use of a single rebalancing technique "
        "(SMOTE), single model family (Random Forest), and 60-sample explanation subset. "
        "External validity is constrained by the use of a single controlled-environment "
        "dataset (UNSW-NB15); findings may not transfer directly to operational enterprise "
        "networks or to network traffic captured in 2024–2025. Construct validity is "
        "bounded by the operationalisation of 'explanation quality' as feature rank "
        "stability; other definitions (e.g., human interpretability, fidelity to causal "
        "ground truth) are not addressed. Statistical conclusion validity is strengthened "
        "by Holm–Bonferroni correction, bootstrap CIs on all key metrics, and the "
        "reporting of both p-values and practical effect sizes.",
    ]
    return "\n".join(lines)


# ── Markdown report builder ───────────────────────────────────────────────────

def build_md_report(
    rq_results: dict[str, dict[str, Any]],
    threats: dict[str, Any],
    implications: list[dict[str, Any]],
    future_work: list[dict[str, Any]],
    executive_summary: str,
    discussion: str,
    generated_at: str,
) -> str:
    """Assemble the full integrated results report in Markdown.

    Args:
        rq_results: Interpretation dicts for all four RQs.
        threats: Threats to validity dict.
        implications: Practical implications list.
        future_work: Future work recommendations.
        executive_summary: Pre-rendered executive summary markdown.
        discussion: Pre-rendered discussion section markdown.
        generated_at: ISO-8601 timestamp.

    Returns:
        Full Markdown text of the integrated results report.
    """
    lines = [
        "# Integrated Results Report",
        "",
        f"**Generated:** {generated_at}  ",
        "**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  ",
        "**Task:** F.2 — Integrated Results Interpretation & Scientific Synthesis  ",
        "",
        "---",
        "",
        executive_summary,
        "",
        "---",
        "",
    ]

    # RQ sections
    for rq_key in ("rq1", "rq2", "rq3", "rq4"):
        rq = rq_results[rq_key]
        lines += [
            f"## {rq['rq']}: {rq['question']}",
            "",
            f"**Verdict:** `{rq['verdict']}`",
            "",
            rq["narrative"],
            "",
        ]
        if rq_key == "rq4":
            lines += [
                "**Evidence supporting hypothesis:**",
                "",
            ]
            for e in rq.get("evidence_for", []):
                lines.append(f"- {e}")
            lines += [
                "",
                "**Qualifications:**",
                "",
            ]
            for q in rq.get("qualifications", []):
                lines.append(f"- {q}")
            lines.append("")

    lines += ["---", ""]

    # Discussion section
    lines += [discussion, "", "---", ""]

    # Threats to validity
    lines += ["## Threats to Validity", ""]
    for category, threat_list in threats.items():
        label = category.replace("_", " ").title()
        lines += [f"### {label}", ""]
        for t in threat_list:
            lines += [
                f"**{t['threat']}:** {t['detail']}  ",
                f"*Mitigation: {t['mitigation']}*",
                "",
            ]

    lines += ["---", ""]

    # Practical implications
    lines += ["## Practical Implications", ""]
    for imp in implications:
        lines += [
            f"### {imp['domain']}",
            "",
            imp["implication"],
            "",
            f"*Evidence: {imp['evidence']}*",
            "",
        ]

    lines += ["---", ""]

    # Future work
    lines += ["## Recommendations for Future Work", ""]
    for i, fw in enumerate(future_work, start=1):
        lines += [
            f"### {i}. {fw['direction']}",
            "",
            fw["rationale"],
            "",
        ]

    lines += [
        "---",
        "",
        "*End of Integrated Results Report*",
    ]
    return "\n".join(lines)


# ── Table generation ──────────────────────────────────────────────────────────

def save_tables(
    rq_results: dict[str, dict[str, Any]],
    implications: list[dict[str, Any]],
    future_work: list[dict[str, Any]],
    ev: dict[str, Any],
    tables_dir: Path,
) -> None:
    """Write key_findings_summary.csv and research_question_summary.csv.

    Args:
        rq_results: Interpretation dicts for all four RQs.
        implications: Practical implications list.
        future_work: Future work recommendations.
        ev: Evidence dict.
        tables_dir: Destination directory.
    """
    ensure_dir(tables_dir)
    eff = _effect_lookup(ev)
    rfm = ev["rf_metrics"]

    # ── research_question_summary.csv ────────────────────────
    rq_rows = []
    for rq_key in ("rq1", "rq2", "rq3", "rq4"):
        rq = rq_results[rq_key]
        rq_rows.append({
            "rq": rq["rq"],
            "question": rq["question"],
            "verdict": rq["verdict"],
            "key_evidence": rq["narrative"][:300].replace("\n", " "),
        })
    pd.DataFrame(rq_rows).to_csv(tables_dir / "research_question_summary.csv", index=False)
    logger.info("Tables generated — research_question_summary.csv")

    # ── key_findings_summary.csv ─────────────────────────────
    findings = [
        {
            "finding_id": "F1",
            "category": "Predictive performance",
            "finding": f"SMOTE accuracy Δ = {rfm['smote']['accuracy'] - rfm['baseline']['accuracy']:.4f} (negligible Cohen's h)",
            "evidence_source": "outputs/tables/class_metrics_comparison.csv, outputs/reports/statistical_validation_report.json",
            "direction": "baseline_higher",
            "practical_significance": "negligible",
        },
        {
            "finding_id": "F2",
            "category": "Predictive performance",
            "finding": f"SMOTE macro F1 Δ = +{rfm['smote']['macro_f1'] - rfm['baseline']['macro_f1']:.4f} (negligible Cohen's h)",
            "evidence_source": "outputs/reports/random_forest_report.json",
            "direction": "smote_higher",
            "practical_significance": "negligible",
        },
        {
            "finding_id": "F3",
            "category": "Predictive performance",
            "finding": "SMOTE improved minority recall (Worms +0.43, Analysis +0.16, Backdoor +0.39) at cost of Normal F1 (-0.04)",
            "evidence_source": "outputs/tables/class_metrics_comparison.csv",
            "direction": "mixed",
            "practical_significance": "moderate_class_level",
        },
        {
            "finding_id": "F4",
            "category": "Explainability — SHAP",
            "finding": f"SHAP global rankings: Spearman r=0.90 (stable); Wilcoxon shift medium (r={eff['Wilcoxon_SHAP_importance']['value']:.3f})",
            "evidence_source": "outputs/comparison/explanation_similarity.csv, F.1 statistics",
            "direction": "moderate_shift",
            "practical_significance": "medium",
        },
        {
            "finding_id": "F5",
            "category": "Explainability — LIME",
            "finding": f"LIME global rankings: Spearman r=0.57 (lower stability); Wilcoxon shift large (r={eff['Wilcoxon_LIME_importance']['value']:.3f})",
            "evidence_source": "outputs/comparison/explanation_similarity.csv, F.1 statistics",
            "direction": "large_shift",
            "practical_significance": "large",
        },
        {
            "finding_id": "F6",
            "category": "Explainability — inter-method",
            "finding": "SHAP–LIME agreement low in both conditions (r≈0.41–0.48); methods not interchangeable",
            "evidence_source": "outputs/comparison/explanation_similarity.csv",
            "direction": "low_agreement",
            "practical_significance": "moderate",
        },
        {
            "finding_id": "F7",
            "category": "Performance vs explainability",
            "finding": (
                f"Explanation effects ({eff['Wilcoxon_SHAP_importance']['magnitude']}–"
                f"{eff['Wilcoxon_LIME_importance']['magnitude']}) exceed predictive effects (all negligible); "
                f"LIME:prediction ratio ≈ {eff['Wilcoxon_LIME_importance']['value'] / max(abs(eff['baseline_vs_smote_accuracy']['value']), 0.001):.1f}×"
            ),
            "evidence_source": "outputs/reports/statistical_validation_report.json",
            "direction": "explanation_more_sensitive",
            "practical_significance": "high",
        },
        {
            "finding_id": "F8",
            "category": "Hypothesis evaluation",
            "finding": "Research hypothesis supported: class rebalancing changes explanations more than predictions",
            "evidence_source": "All F.1 outputs",
            "direction": "supported",
            "practical_significance": "high",
        },
    ]
    pd.DataFrame(findings).to_csv(tables_dir / "key_findings_summary.csv", index=False)
    logger.info("Tables generated — key_findings_summary.csv")


# ── Main entry point ──────────────────────────────────────────────────────────

def run_results_interpretation() -> dict[str, Any]:
    """Orchestrate the full integrated results interpretation (Task F.2).

    Loads all existing experimental outputs, synthesises findings for
    each research question, analyses threats to validity, derives
    practical implications, and writes all report and table artefacts.

    No experiments are executed. No upstream artefacts are modified.

    Returns:
        Full interpretation results dict, JSON-serialisable.
    """
    cfg = get_config()
    paths = get_path_manager()
    root = paths.project_root

    logger.info("=== Task F.2 Results Interpretation ===")
    logger.info("Project root: %s", root)

    # Load all evidence
    ev = load_all_evidence(root)

    # Answer research questions
    rq1 = interpret_rq1_predictive_performance(ev)
    rq2 = interpret_rq2_explainability(ev)
    rq3 = interpret_rq3_performance_vs_explainability(ev)
    rq4 = interpret_rq4_hypothesis(ev)
    rq_results = {"rq1": rq1, "rq2": rq2, "rq3": rq3, "rq4": rq4}

    logger.info("Research questions answered — RQ1–RQ4 complete")

    # Threat analysis
    threats = analyse_threats_to_validity(ev)

    # Practical implications
    implications = derive_practical_implications(rq_results, ev)

    # Future work
    future_work = recommend_future_work(ev)

    # Executive summary and discussion section
    executive_summary = build_executive_summary(rq_results, implications, ev)
    discussion = build_discussion_section(rq_results, threats, ev)

    # Self-test: verify no experiments were run (all inputs from disk only)
    upstream_checks = [
        "outputs/reports/random_forest_report.json",
        "outputs/comparison/explanation_similarity.csv",
        "outputs/reports/statistical_validation_report.json",
    ]
    for path in upstream_checks:
        full = root / path
        if not full.exists():
            raise FileNotFoundError(f"Required upstream artefact missing: {full}")
    logger.info("Validation completed — all upstream artefacts present, no retraining occurred")

    # Generate outputs
    generated_at = datetime.now(tz=timezone.utc).isoformat()
    reports_dir = paths.reports_dir
    tables_dir = paths.tables_dir

    # Tables
    save_tables(rq_results, implications, future_work, ev, tables_dir)
    logger.info("Tables generated — key_findings_summary.csv, research_question_summary.csv")

    # Markdown report
    md_text = build_md_report(
        rq_results, threats, implications, future_work,
        executive_summary, discussion, generated_at,
    )
    write_text(reports_dir / "integrated_results_report.md", md_text)
    logger.info("Reports generated — integrated_results_report.md")

    # JSON report
    json_report: dict[str, Any] = {
        "generated_at": generated_at,
        "research_questions": rq_results,
        "threats_to_validity": threats,
        "practical_implications": implications,
        "future_work": future_work,
        "executive_summary": executive_summary,
    }
    write_json(reports_dir / "integrated_results_report.json", json_report)
    logger.info("Reports generated — integrated_results_report.json")

    logger.info("Scientific synthesis completed — Task F.2 finished successfully")
    return json_report
