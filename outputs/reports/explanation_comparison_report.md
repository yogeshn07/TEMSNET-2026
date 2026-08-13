# UNSW-NB15 Explanation Reliability & Comparative Analysis Report

**Generated:** 2026-06-30T13:06:38.849388+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Methodology

This analysis compares Task E.2's SHAP outputs and Task E.3's LIME outputs across the two Random Forest models (baseline, SMOTE-balanced), using the identical 60-sample evaluation subset both prior tasks explained. No model was retrained, no SHAP value was recomputed, and no LIME explanation was regenerated — every number in this report derives from Task E.2's and Task E.3's already-saved Parquet/CSV outputs, loaded read-only.

**Why identical samples are required:** every comparison below is only valid because SHAP and LIME explained the exact same rows (verified by Task E.2/E.3's own self-tests). Comparing explanations from different samples would confound "different rows" with "different explanation behaviour."

**Why explanation comparison is meaningful:** Task D.1 already reported that class balancing changes predictive metrics. This task asks the complementary question — does it also change *what the model's explanations look like* — by holding the explained samples fixed and varying only the training distribution.

---

## Comparison Metrics

Four comparison pairs were evaluated, each using top-k feature overlap (k=5, k=10), Jaccard similarity of the top-k important-feature sets, Spearman rank correlation, and Kendall Tau rank correlation, computed over the intersection of features present in both rankings being compared:

1. **SHAP_baseline vs SHAP_smote** — does balancing change what SHAP considers important, within the same method?
2. **LIME_baseline vs LIME_smote** — same question, for LIME.
3. **SHAP_baseline vs LIME_baseline** — do the two methods agree on the baseline model's behaviour?
4. **SHAP_smote vs LIME_smote** — do the two methods agree on the SMOTE model's behaviour?

SHAP's global importance table covers all 42 features; LIME's covers only the 40 features that appeared in some sample's top-K explanation (Task E.3's `num_features` config). Cross-method pairs (3 and 4 above) are therefore restricted to their 38-feature intersection — stated here explicitly as the assumption underlying those two comparisons.

---

## Agreement Analysis (Observed Results)

| Pair | Top-5 Overlap | Top-10 Overlap | Jaccard (top-10) | Spearman r | Kendall τ |
|---|---|---|---|---|---|
| SHAP_baseline_vs_SHAP_smote | 0.8 | 0.8 | 0.666667 | 0.900008 | 0.732869 |
| LIME_baseline_vs_LIME_smote | 0.6 | 0.6 | 0.428571 | 0.564994 | 0.390476 |
| SHAP_baseline_vs_LIME_baseline | 0.2 | 0.5 | 0.333333 | 0.409563 | 0.271693 |
| SHAP_smote_vs_LIME_smote | 0.2 | 0.6 | 0.428571 | 0.476091 | 0.334282 |

**Interpretation:** higher overlap/Jaccard/correlation values indicate the two compared rankings agree more on which features matter; values near 0 (correlation) or 0 (overlap) indicate little agreement. These are observed magnitudes from this specific 60-sample subset, not statistical significance claims (Task F.1's scope).

---

## Global Comparison — Newly Important / Reduced Importance Features

### SHAP (Baseline → SMOTE)

- **Newly important (entered top-10):** dmean, proto
- **Reduced importance (left top-10):** ct_state_ttl, dttl

### LIME (Baseline → SMOTE)

- **Newly important (entered top-10):** ct_dst_src_ltm, ct_srv_dst, sbytes, state
- **Reduced importance (left top-10):** is_sm_ips_ports, sjit, spkts, sttl

---

## Local Comparison (Representative Examples)

### Correct Prediction — `SAMPLE_001421` (true class: `Backdoor`)

- **SHAP top-5 overlap (baseline vs SMOTE):** 0.6
- **LIME top-5 overlap (baseline vs SMOTE):** 0.0

### Incorrect Prediction — `SAMPLE_001322` (true class: `Shellcode`)

- **SHAP top-5 overlap (baseline vs SMOTE):** 0.8
- **LIME top-5 overlap (baseline vs SMOTE):** 0.6

### Minority Class — `SAMPLE_003662` (true class: `Worms`)

- **SHAP top-5 overlap (baseline vs SMOTE):** 0.8
- **LIME top-5 overlap (baseline vs SMOTE):** 0.6

### Majority Class — `SAMPLE_028142` (true class: `Normal`)

- **SHAP top-5 overlap (baseline vs SMOTE):** 0.8
- **LIME top-5 overlap (baseline vs SMOTE):** 0.6

---

## Minority Class Analysis (Worms, Backdoor, Analysis)

*Descriptive only — observed patterns in this subset, not a generalisable claim.*

### Worms (n=6)

- **SHAP top-5 overlap, baseline vs SMOTE:** 0.8 (Spearman r = 0.759663)
- **LIME top-5 overlap, baseline vs SMOTE:** 0.4 (Spearman r = 0.619048)

### Backdoor (n=6)

- **SHAP top-5 overlap, baseline vs SMOTE:** 1.0 (Spearman r = 0.876833)
- **LIME top-5 overlap, baseline vs SMOTE:** 0.4 (Spearman r = 0.543956)

### Analysis (n=6)

- **SHAP top-5 overlap, baseline vs SMOTE:** 0.6 (Spearman r = 0.807795)
- **LIME top-5 overlap, baseline vs SMOTE:** 0.4 (Spearman r = 0.52381)

---

## Threats to Validity

- **Small subset size (60 samples).** Findings describe this specific subset, selected for computational tractability in Task E.2; they are not a population-level claim about all 82,332 testing rows.
- **No statistical significance testing.** This task reports observed magnitudes and rank shifts only. Significance testing is explicitly Task F.1's scope.
- **Asymmetric LIME background distributions.** Each model's LIME explainer used that model's own training set as its perturbation background (Task E.3), so a baseline-vs-SMOTE LIME difference may partly reflect this background asymmetry rather than only the trained model's behaviour.
- **Feature-set mismatch between SHAP and LIME.** Cross-method comparisons are restricted to the 38-feature intersection of both methods' importance tables, as stated in the Comparison Metrics section.

---

## Limitations

- SHAP values and LIME weights are different mathematical objects on different scales; this report compares **rankings**, never raw magnitudes, between the two methods.
- No causal claim is made anywhere in this report: an observed rank shift or attribution change describes what changed in the model's explanation behaviour when trained on a different distribution, not why the underlying network traffic produces that pattern.
- Class-restricted minority-class metrics (3-9 samples per class) have wide uncertainty; small common-feature counts can make rank correlations unstable, noted directly in this report's tables where the common feature count is low.

---

## Explanation Comparison Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

Explanation reliability was assessed by comparing Task E.2's SHAP and Task E.3's LIME outputs across the baseline and SMOTE-balanced Random Forest models (Task D.1), using the identical 60-sample evaluation subset both methods explained. No model was retrained and no explanation was regenerated. Four comparison pairs were evaluated — SHAP baseline-vs-SMOTE, LIME baseline-vs-SMOTE, and SHAP-vs-LIME within each training condition — using top-k feature overlap (k=5, k=10), Jaccard similarity, Spearman rank correlation, and Kendall Tau rank correlation. SHAP's baseline-vs-SMOTE top-5 feature overlap was 0.8 (Spearman r = 0.900008); LIME's was 0.6 (Spearman r = 0.564994). Dedicated analysis of the three rarest classes (Worms, Backdoor, Analysis) examined whether class balancing changes explanation consistency specifically for minority classes. All comparisons are descriptive; no statistical significance testing or causal claims are made (Task F.1 addresses statistical validation).

---
*End of Explanation Comparison Report*
