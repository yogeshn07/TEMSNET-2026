# UNSW-NB15 SHAP Explainability Analysis Report

**Generated:** 2026-06-30T09:18:11.970730+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Why TreeExplainer

`shap.TreeExplainer` computes exact Shapley values for tree ensembles in polynomial time by exploiting the tree structure directly, requiring no background dataset and no sampling approximation — the appropriate, standard choice for explaining Random Forest models, and the only SHAP explainer that guarantees attributions sum exactly to (prediction − expected value).

## Why Identical Sample IDs Are Required

This study compares attribution patterns between a model trained on imbalanced data and one trained on SMOTE-balanced data. Explaining different samples for each model would confound any observed attribution difference with *which rows* were explained, rather than isolating the effect of the training distribution.

## Why the Prediction Repository Is Reused

Correctness/incorrectness labels for sample selection must reflect the exact predictions already reported in Task D.1 and Task E.1 — recomputing predictions here would risk drift and duplicate already-tested logic.

---

## Sample Selection Methodology

For every one of the 10 true classes, up to 3 correctly-classified and up to 3 misclassified samples (per the **baseline model's** predictions) were selected via a seeded shuffle, then deterministically truncated. This produced a fixed subset of **60 samples** spanning all 10 classes, including both the rarest class (`Worms`, 44 total testing samples) and the most frequent (`Normal`, 37,000 total testing samples). The exact same `sample_id` set was used to compute SHAP values for both models.

---

## Computation Details

- **Explainer:** `shap.TreeExplainer`
- **check_additivity:** False
- **Samples explained:** 60 (identical for both models)
- **Output shape per model:** (60, 42, 10) (samples x features x classes)

---

## Global Feature Importance — Top 10 (Baseline)

| Feature | Mean |SHAP| |
|---|---|
| sbytes | 0.018471 |
| sttl | 0.017435 |
| smean | 0.014983 |
| service | 0.012591 |
| ct_srv_dst | 0.011754 |
| ct_dst_src_ltm | 0.011541 |
| ct_dst_sport_ltm | 0.010009 |
| dttl | 0.008575 |
| ct_state_ttl | 0.008312 |
| ct_srv_src | 0.007731 |

## Global Feature Importance — Top 10 (SMOTE)

| Feature | Mean |SHAP| |
|---|---|
| ct_dst_src_ltm | 0.020378 |
| sbytes | 0.019053 |
| service | 0.016707 |
| smean | 0.014972 |
| ct_srv_dst | 0.013307 |
| sttl | 0.011852 |
| proto | 0.010289 |
| ct_dst_sport_ltm | 0.009412 |
| dmean | 0.008054 |
| ct_srv_src | 0.00729 |

---

## Notable Attribution Differences (Descriptive Only)

*(Reported as observed differences in this specific computation — no causal claim is made.)*

- `sbytes`: rank 1 (baseline) vs. rank 2 (SMOTE), mean |SHAP| 0.018471 vs. 0.019053
- `sttl`: rank 2 (baseline) vs. rank 6 (SMOTE), mean |SHAP| 0.017435 vs. 0.011852
- `smean`: rank 3 (baseline) vs. rank 4 (SMOTE), mean |SHAP| 0.014983 vs. 0.014972
- `service`: rank 4 (baseline) vs. rank 3 (SMOTE), mean |SHAP| 0.012591 vs. 0.016707
- `ct_srv_dst`: rank 5 (baseline) vs. rank 5 (SMOTE), mean |SHAP| 0.011754 vs. 0.013307
- `ct_dst_src_ltm`: rank 6 (baseline) vs. rank 1 (SMOTE), mean |SHAP| 0.011541 vs. 0.020378
- `ct_dst_sport_ltm`: rank 7 (baseline) vs. rank 8 (SMOTE), mean |SHAP| 0.010009 vs. 0.009412
- `dttl`: rank 8 (baseline) vs. rank 19 (SMOTE), mean |SHAP| 0.008575 vs. 0.003967
- `ct_state_ttl`: rank 9 (baseline) vs. rank 17 (SMOTE), mean |SHAP| 0.008312 vs. 0.004873
- `ct_srv_src`: rank 10 (baseline) vs. rank 10 (SMOTE), mean |SHAP| 0.007731 vs. 0.00729

---

## Local Explanations (Representative Examples)

### Correct Prediction — `SAMPLE_001421`

True class: `Backdoor` | Baseline predicted: `Backdoor` | SMOTE predicted: `Backdoor`

| Model | Top Features (by |SHAP|, for the true class) |
|---|---|
| Baseline | smean=0.115667, sbytes=0.105666, dttl=0.071627, sttl=0.063088, dbytes=0.051631 |
| SMOTE | smean=0.094901, sbytes=0.081034, dmean=0.079751, ct_state_ttl=0.066867, dttl=0.053876 |

### Incorrect Prediction — `SAMPLE_001322`

True class: `Shellcode` | Baseline predicted: `Fuzzers` | SMOTE predicted: `Shellcode`

| Model | Top Features (by |SHAP|, for the true class) |
|---|---|
| Baseline | ct_dst_src_ltm=0.052771, smean=0.024836, service=0.019666, sbytes=0.017886, dbytes=0.012404 |
| SMOTE | ct_dst_src_ltm=0.103099, service=0.072203, dbytes=0.046556, sjit=-0.036295, sbytes=0.029756 |

### Minority Class — `SAMPLE_003662`

True class: `Worms` | Baseline predicted: `Exploits` | SMOTE predicted: `Worms`

| Model | Top Features (by |SHAP|, for the true class) |
|---|---|
| Baseline | sbytes=0.082474, smean=0.065899, service=0.031918, dbytes=0.018489, ct_flw_http_mthd=0.017878 |
| SMOTE | service=0.136831, sbytes=0.127078, smean=0.112124, trans_depth=0.094982, ct_flw_http_mthd=0.05438 |

### Majority Class — `SAMPLE_028142`

True class: `Normal` | Baseline predicted: `Normal` | SMOTE predicted: `Normal`

| Model | Top Features (by |SHAP|, for the true class) |
|---|---|
| Baseline | sttl=0.133271, ct_state_ttl=0.125114, dttl=0.064724, dload=0.041097, rate=0.028194 |
| SMOTE | sttl=0.234117, ct_state_ttl=0.197831, dload=0.062524, dttl=0.061223, sloss=0.030564 |

---

## Limitations

- SHAP attributions describe what the model learned from the data, not a causal relationship between a feature and the true network-traffic outcome.
- Global summary and bar plots aggregate 10-class SHAP values via mean absolute value, losing per-class directionality — a deliberate simplification to produce the two requested plot types; the full per-class breakdown remains available in the per-feature CSV tables and the long-format Parquet export.
- TreeExplainer's path-dependent attributions can split credit between highly correlated features (several pairs were retained as "Candidate" features in Task C.4); a high or low attribution for one such feature does not rule out a shared signal with its correlated partner.
- The fixed evaluation subset (60 samples or fewer) is intentionally small for computational tractability (TreeExplainer on these deep, unbounded trees takes over a second per sample); global importance rankings from this subset are descriptive of these specific samples, not a claim about the full 82,332-row testing population.

---

## SHAP Analysis Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

SHAP values were computed for both Random Forest models using `shap.TreeExplainer` against a fixed, deterministic evaluation subset of 60 samples, selected once from the Task E.1 prediction repository to span all 10 classes with both correctly- and incorrectly-classified examples, and reused identically for both models. No retraining occurred. Global feature importance (mean |SHAP| across classes) and local explanations for four representative samples (a correct prediction, an incorrect prediction, a minority-class example, and a majority-class example) were generated for both models under identical conditions, producing a directly comparable basis for examining how training-distribution balancing affects feature attribution patterns.

---
*End of SHAP Analysis Report*
