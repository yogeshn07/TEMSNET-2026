# UNSW-NB15 LIME Explainability Analysis Report

**Generated:** 2026-06-30T09:32:01.688715+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Methodology

`LimeTabularExplainer` fits a locally weighted linear surrogate model around each instance's perturbed neighbourhood to approximate the Random Forest's behaviour near that point. Explanations were generated for the **exact same** evaluation subset Task E.2 already selected — read directly from Task E.2's saved sample registry and local-example selections, never recomputed — so SHAP (Task E.2) and LIME (this task) explain identical samples, a prerequisite for Task E.4's reliability comparison.

## Why LIME Is Appropriate for Local Explanations

LIME is model-agnostic (requires only a `predict_proba` function) and frames each explanation as a local linear approximation around one specific instance — a complementary perspective to SHAP's exact, game-theoretic global decomposition, useful for inspecting individual predictions in an intuitive "what moved this prediction" form.

## Why Identical Sample IDs Are Reused

Task E.4 will compare SHAP and LIME outputs directly; explaining different samples would make that comparison meaningless. This module reads Task E.2's saved sample IDs verbatim rather than recomputing a (deterministically identical) subset, removing any dependency on that selection logic remaining unchanged.

## Why the Prediction Repository Is Reused

True/predicted class labels for the explained samples come from Task E.1's archived predictions, avoiding any risk of drift from re-running inference.

---

## Configuration

| Parameter | Value |
|---|---|
| num_features | 10 |
| num_samples (perturbations per instance) | 5000 |
| random_seed | 42 |
| categorical_features | proto, service, state |
| Background data (baseline explainer) | `training_baseline.parquet` |
| Background data (SMOTE explainer) | `training_balanced_smote.parquet` |

---

## Samples Explained: 60

Identical sample_id set reused from Task E.2, spanning all 10 classes with both correctly- and incorrectly-classified examples per class.

---

## Global Feature Importance — Top 10 (Baseline)

| Feature | Mean |Weight| | Appearances |
|---|---|---|
| sttl | 0.042042 | 53 |
| dttl | 0.029139 | 28 |
| ct_dst_sport_ltm | 0.022349 | 24 |
| spkts | 0.022067 | 3 |
| proto | 0.020402 | 30 |
| service | 0.020309 | 53 |
| ct_state_ttl | 0.01943 | 34 |
| swin | 0.017911 | 16 |
| is_sm_ips_ports | 0.014108 | 20 |
| sjit | 0.013497 | 7 |

## Global Feature Importance — Top 10 (SMOTE)

| Feature | Mean |Weight| | Appearances |
|---|---|---|
| service | 0.027653 | 60 |
| dttl | 0.026008 | 24 |
| proto | 0.02582 | 22 |
| ct_dst_sport_ltm | 0.023141 | 23 |
| swin | 0.022985 | 7 |
| state | 0.022356 | 2 |
| ct_dst_src_ltm | 0.020945 | 41 |
| ct_state_ttl | 0.020094 | 9 |
| sbytes | 0.01958 | 24 |
| ct_srv_dst | 0.019299 | 29 |

---

## Observed Attribution Differences (Descriptive Only)

*(Reported as observed differences in this specific computation — no causal claim is made.)*

- Mean local fidelity (R²), baseline: 0.290211  
- Mean local fidelity (R²), SMOTE: 0.251881

---

## Local Explanation Summaries (Representative Examples)

### Correct Prediction — `SAMPLE_001421`

True class: `Backdoor`

| Model | Local Fidelity (R²) | Top Feature Contributions |
|---|---|---|
| Baseline | 0.157743 | dinpkt=0.012352, dbytes=0.012115, ct_dst_src_ltm=0.009684, dttl=0.008238, sttl=0.008198 |
| SMOTE | 0.265373 | service=0.027097, proto=-0.024787, ct_srv_dst=0.021453, sbytes=0.020498, ct_ftp_cmd=-0.017298 |

### Incorrect Prediction — `SAMPLE_001322`

True class: `Shellcode`

| Model | Local Fidelity (R²) | Top Feature Contributions |
|---|---|---|
| Baseline | 0.361483 | ct_dst_src_ltm=0.022101, service=0.015481, sttl=0.011637, ct_srv_dst=0.011264, ct_dst_sport_ltm=0.010651 |
| SMOTE | 0.327781 | service=0.040823, ct_dst_src_ltm=0.030261, ct_src_dport_ltm=0.01866, ct_dst_sport_ltm=0.016077, is_sm_ips_ports=-0.015836 |

### Minority Class — `SAMPLE_003662`

True class: `Worms`

| Model | Local Fidelity (R²) | Top Feature Contributions |
|---|---|---|
| Baseline | 0.04058 | trans_depth=0.002383, ct_flw_http_mthd=0.001958, service=0.001685, ct_dst_src_ltm=0.001631, sttl=0.001409 |
| SMOTE | 0.221109 | service=0.021287, ct_dst_src_ltm=0.017852, ct_flw_http_mthd=0.009904, ct_srv_src=0.009857, response_body_len=-0.008016 |

### Majority Class — `SAMPLE_028142`

True class: `Normal`

| Model | Local Fidelity (R²) | Top Feature Contributions |
|---|---|---|
| Baseline | 0.598421 | sttl=0.187922, ct_state_ttl=0.064721, dttl=0.051764, is_sm_ips_ports=-0.041725, service=0.041618 |
| SMOTE | 0.226708 | dttl=-0.043506, sloss=0.033878, service=0.028074, ct_state_ttl=0.027835, swin=0.026885 |

---

## Limitations

- LIME's local linear surrogate is fit on a randomly perturbed neighbourhood; results are approximate and seed-dependent (fixed here for reproducibility, but a different seed could produce different feature weights for the same instance).
- The local fidelity score (R²) measures how well a *linear* model approximates the Random Forest's behaviour near one instance; a low score indicates the explanation may not faithfully represent the model's true local decision behaviour for that sample.
- Each model's explainer used that model's own training set as the perturbation background (baseline uses the original training distribution, SMOTE uses the balanced one) — a deliberate choice so perturbations reflect what each model actually learned from, but this means the two explainers are not perturbing from an identical reference distribution.
- As with SHAP, attributions describe model behaviour, not a causal relationship with the true network-traffic outcome.
- This report does not compare SHAP and LIME outputs — that comparison is Task E.4's scope.

---

## LIME Analysis Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

LIME explanations were computed for both Random Forest models using `LimeTabularExplainer` (5000 perturbed samples per instance, top 10 features per explanation) against the exact same 60-sample evaluation subset Task E.2 selected — read directly from Task E.2's saved artifacts, never recomputed. Each model's explainer used that model's own training distribution as its perturbation background. No retraining occurred. Local explanations were generated for all subset samples, plus detailed reporting for the four representative examples (a correct prediction, an incorrect prediction, a minority-class example, and a majority-class example) shared with Task E.2, establishing a directly comparable basis for Task E.4's SHAP-LIME reliability analysis.

---
*End of LIME Analysis Report*
