# UNSW-NB15 Random Forest Baseline Report

**Generated:** 2026-06-30T08:35:48.959574+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Why Random Forest

Random Forest is the locked model choice for this study (established in the research design prior to this implementation phase): it handles the mixed numeric/ordinal-encoded feature space without requiring scaling, tolerates the multicollinearity documented in Task C.4's correlation review without instability, and supports SHAP's TreeExplainer for exact, efficient explanation computation in the upcoming Phase E — a combination linear models and most other classifiers do not offer simultaneously.

## Why Identical Hyperparameters

Both models are configured from the exact same `configs/model.yaml` dictionary, loaded once and passed unchanged to both training calls. This isolates the training distribution (original vs. SMOTE-balanced) as the only experimental variable — any difference in Model A's and Model B's metrics is therefore attributable to class balancing alone, not to a hyperparameter confound.

## Why the Testing Dataset Remains Unchanged

Both models are evaluated on the identical `testing_baseline.parquet` (Task C.5's untouched, never-balanced copy of the real-world test distribution). Using any other test set, or balancing it, would invalidate the comparison this experiment exists to produce.

## Why Two Independent Models

A single model cannot answer "does class balancing change predictive behaviour and (later) explanation quality?" — that requires training two models that differ in exactly one respect (their training data) and comparing them under identical evaluation conditions.

---

## Model Configuration

| Parameter | Value |
|---|---|
| n_estimators | 100 |
| max_depth | None |
| min_samples_split | 2 |
| min_samples_leaf | 1 |
| max_features | sqrt |
| n_jobs | -1 |
| random_state | 42 |

---

## Dataset Sizes

| Dataset | Rows | Columns |
|---|---|---|
| Training (baseline) | 175,341 | 43 |
| Training (SMOTE-balanced) | 560,000 | 43 |
| Testing (shared, untouched) | 82,332 | 43 |

---

## Experiment A — Baseline Model Metrics

| Metric | Macro | Weighted |
|---|---|---|
| Precision | 0.522398 | 0.841144 |
| Recall | 0.4977 | 0.754348 |
| F1-score | 0.470425 | 0.778033 |

**Accuracy:** 0.754348

### Per-Class Metrics (Baseline)

| Class | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Analysis | 0.004695 | 0.008863 | 0.006138 | 677 |
| Backdoor | 0.017274 | 0.092624 | 0.029118 | 583 |
| DoS | 0.607868 | 0.117144 | 0.196432 | 4089 |
| Exploits | 0.625416 | 0.777219 | 0.693103 | 11132 |
| Fuzzers | 0.292655 | 0.592214 | 0.391729 | 6062 |
| Generic | 0.998528 | 0.970855 | 0.984497 | 18871 |
| Normal | 0.966765 | 0.75473 | 0.847689 | 37000 |
| Reconnaissance | 0.931343 | 0.803204 | 0.86254 | 3496 |
| Shellcode | 0.341935 | 0.701058 | 0.45967 | 378 |
| Worms | 0.4375 | 0.159091 | 0.233333 | 44 |

---

## Experiment B — SMOTE-Balanced Model Metrics

| Metric | Macro | Weighted |
|---|---|---|
| Precision | 0.509583 | 0.860869 |
| Recall | 0.600983 | 0.716064 |
| F1-score | 0.487432 | 0.76314 |

**Accuracy:** 0.716064

### Per-Class Metrics (SMOTE)

| Class | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Analysis | 0.034461 | 0.163959 | 0.056952 | 677 |
| Backdoor | 0.049956 | 0.48199 | 0.090528 | 583 |
| DoS | 0.531767 | 0.149425 | 0.233295 | 4089 |
| Exploits | 0.787512 | 0.637891 | 0.704849 | 11132 |
| Fuzzers | 0.275136 | 0.627021 | 0.382452 | 6062 |
| Generic | 0.998907 | 0.968947 | 0.983699 | 18871 |
| Normal | 0.977754 | 0.690162 | 0.809164 | 37000 |
| Reconnaissance | 0.887206 | 0.821224 | 0.852941 | 3496 |
| Shellcode | 0.186937 | 0.878307 | 0.308264 | 378 |
| Worms | 0.366197 | 0.590909 | 0.452174 | 44 |

---

## High-Level Comparison

| Metric | Baseline | SMOTE | Delta |
|---|---|---|---|
| Accuracy | 0.754348 | 0.716064 | -0.038284 |
| Macro F1 | 0.470425 | 0.487432 | 0.017007 |
| Weighted F1 | 0.778033 | 0.76314 | -0.014893 |

*(No claim of "better"/"worse" is made here — accuracy optimisation and model comparison are explicitly out of scope for this task; per-class explanation quality, the actual research question, is addressed in Phase E.)*

---

## Random Forest Baseline Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

Two `RandomForestClassifier` models were trained with identical hyperparameters (n_estimators=100, max_depth=None, max_features=sqrt, random_state=42): Model A on the original imbalanced training set (175,341 rows) and Model B on the SMOTE-balanced training set (560,000 rows). Both were evaluated on the identical, untouched testing set (82,332 rows). Model A achieved 0.7543 accuracy (macro F1 = 0.4704); Model B achieved 0.7161 accuracy (macro F1 = 0.4874). No hyperparameter tuning, accuracy optimisation, or explainability analysis was performed at this stage; per-class explanation quality is addressed in Phase E.

---
*End of Random Forest Baseline Report*
