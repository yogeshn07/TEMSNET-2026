# Statistical Validation Report

**Generated:** 2026-07-03T00:36:26.657494+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Task:** F.1 — Statistical Validation & Significance Analysis  

---

## Methodology

This report validates previously generated experimental results using statistical tests applied to **existing outputs only**. No model was retrained, no SHAP values were recomputed, and no LIME explanations were regenerated. All input artefacts are verified by SHA-256 before and after the analysis.

Statistical significance threshold: α = 0.05.  
Multiple comparison correction: **Holm–Bonferroni** across all hypothesis tests.  
Effect sizes: **Cohen's h** (proportions) and **rank-biserial r** (Wilcoxon tests).  
Confidence intervals: **95% percentile bootstrap** (n=2000 resamples).

---

## Structural Assumptions

- **n_samples:** 82,332
- **Sample IDs consistent across files:** True
- **Model agreement rate:** 0.8707
- **Zero confidence-difference rate:** 0.4130

---

## Hypothesis Tests

### 1. McNemar's Test (Paired Classification Outcomes)

**Assumption:** Both models evaluated on the same 82,332 test instances.  
**Null hypothesis (H₀):** The two classifiers make symmetric errors (b = c).  
**Method:** chi2_yates  
**Statistic:** 1547.5064  
**p-value:** < 1e-300 (machine epsilon)  
**n_discordant (b+c):** 6,416 (b=1,632, c=4,784)  
**Reject H₀ (Holm-corrected):** True  

*Limitations: Tests symmetry of errors, not which model is more accurate. Does not capture per-class behaviour.*

### 2–4. Wilcoxon Signed-Rank Tests

#### Wilcoxon confidence
**n pairs:** 82332 (zero differences removed: 34002)  
**Statistic (W):** 455648243.5000  
**p-value:** < 1e-300 (machine epsilon)  
**Reject H₀ (Holm-corrected):** True  
*Assumptions: Paired confidence scores for the same 82,332 test instances. Normal approximation used (n >> 50). Zero differences removed (zero_method='wilcox'). Differences assumed symmetric.*  
*Limitations: 34002 zero differences (41.3%) removed. Discrete vote proportions are not truly continuous. Significant p-value does not imply the shift is diagnostically meaningful.*

#### Wilcoxon SHAP importance
**n pairs:** 42 (zero differences removed: 0)  
**Statistic (W):** 283.0000  
**p-value:** 0.034708  
**Reject H₀ (Holm-corrected):** True  
*Assumptions: Paired SHAP feature importances for 42 features present in both models. Differences assumed symmetric. Feature importances may be correlated.*  
*Limitations: n=42 pairs limits statistical power. Feature importances are not independent observations. Absolute importance magnitudes differ between methods.*

#### Wilcoxon LIME importance
**n pairs:** 36 (zero differences removed: 0)  
**Statistic (W):** 115.0000  
**p-value:** 3.59e-04  
**Reject H₀ (Holm-corrected):** True  
*Assumptions: Paired LIME feature importances for 36 features present in both models. Differences assumed symmetric. Feature importances may be correlated.*  
*Limitations: n=36 pairs limits statistical power. Feature importances are not independent observations. Absolute importance magnitudes differ between methods.*

---

## Bootstrap Confidence Intervals (95%)

| Model | Metric | Observed | CI Lower | CI Upper | Width |
|---|---|---|---|---|---|
| baseline | accuracy | 0.7543 | 0.7516 | 0.7574 | 0.0057 |
| baseline | macro_f1 | 0.4704 | 0.4556 | 0.4853 | 0.0298 |
| baseline | weighted_f1 | 0.7780 | 0.7754 | 0.7808 | 0.0054 |
| smote | accuracy | 0.7161 | 0.7129 | 0.7191 | 0.0062 |
| smote | macro_f1 | 0.4874 | 0.4752 | 0.4989 | 0.0237 |
| smote | weighted_f1 | 0.7631 | 0.7605 | 0.7659 | 0.0054 |

---

## Effect Sizes

| Comparison | Metric | Value | Magnitude | Direction |
|---|---|---|---|---|
| baseline_vs_smote_accuracy | cohens_h | -0.0868 | negligible | baseline_higher |
| baseline_vs_smote_macro_f1 | cohens_h | 0.0340 | negligible | smote_higher |
| baseline_vs_smote_weighted_f1 | cohens_h | -0.0354 | negligible | baseline_higher |
| Wilcoxon_confidence | rank_biserial_r | 0.1686 | small | N/A (unsigned) |
| Wilcoxon_SHAP_importance | rank_biserial_r | 0.3259 | medium | N/A (unsigned) |
| Wilcoxon_LIME_importance | rank_biserial_r | 0.5947 | large | N/A (unsigned) |

---

## Threats to Validity

- **Test-set representativeness.** The 82,332-row UNSW-NB15 test split follows the dataset's predefined partition; findings are specific to this split.
- **Class imbalance in McNemar's test.** McNemar's test does not weight classes; dominant classes (Normal, Generic) drive the discordant counts.
- **Feature dependence in Wilcoxon (explanations).** SHAP / LIME feature importances are correlated; the Wilcoxon test assumes independent observations.
- **Small n for explanation Wilcoxon.** n=42 (SHAP) and n≤40 (LIME) limit statistical power; a non-significant result does not imply equal distributions.
- **Bootstrap independence.** Bootstrap resamples each row independently; any within-sample temporal structure in network flows is not preserved.
- **No causal claims.** All findings are associative; the observed differences describe what changed in model behaviour, not why.

---

## Limitations

- Confidence scores are discrete vote proportions (not continuous); the Wilcoxon approximation is less accurate in the presence of many ties.
- Statistical significance (low p-value) does not equal practical importance. Effect sizes and CI widths should be consulted jointly.
- Holm–Bonferroni controls the family-wise error rate at α=0.05; it is conservative when tests are positively correlated.

---

## Statistical Validation Summary
*(Suitable for inclusion in the IEEE paper Results section)*

Statistical validation applied McNemar's test, three Wilcoxon signed-rank tests, 95% percentile bootstrap confidence intervals, and Cohen's h / rank-biserial effect sizes, with Holm–Bonferroni correction across 4 hypothesis tests (α = 0.05).

Baseline accuracy was 0.7543 (95% CI [0.7516, 0.7574]); SMOTE accuracy was 0.7161 (95% CI [0.7129, 0.7191]). The Cohen's h effect size for accuracy was -0.0868 (negligible). 
McNemar's test rejected H₀ (p=< 1e-300 (machine epsilon), Holm-corrected), indicating the two classifiers' error patterns are asymmetric.
The Wilcoxon test on per-sample confidence scores rejected H₀ (p=< 1e-300 (machine epsilon)), suggesting the prediction confidence distribution shifted significantly.
SHAP feature importance magnitudes differed significantly between models (Wilcoxon, p=0.034708).
LIME feature importance magnitudes differed significantly between models (Wilcoxon, p=3.59e-04).
All findings are observational; no causal claim is made. Reproducibility is guaranteed by configuration-seeded bootstrap resampling and SHA-256 verification of all upstream artefacts.

---
*End of Statistical Validation Report*