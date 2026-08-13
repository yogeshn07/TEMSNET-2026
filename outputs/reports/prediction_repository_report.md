# UNSW-NB15 Prediction Repository Report

**Generated:** 2026-06-30T08:47:52.044141+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Why Predictions Are Archived

SHAP (Task E.2) and LIME (Task E.3) must explain *exactly* the same predictions to make their explanation-quality comparison valid. Archiving inference output once, here, removes any possibility that the two methods silently explain different samples due to independent inference calls, library version drift, or row-order differences.

## Why No Retraining Was Performed

Both models are loaded via `joblib.load()` from Task D.1's saved artifacts and used only for `.predict()` / `.predict_proba()` calls. Retraining — even with identical hyperparameters and seed — risks producing different trees due to environment-level floating-point nondeterminism in parallel tree construction. Loading the exact saved models guarantees Phase E explains the same models whose metrics are already reported in Task D.1.

## Reproducibility Guarantee

`sample_id` and `row_index` are derived from `testing_baseline.parquet`'s row position, which has been stable and unmodified since Task C.1. The same `sample_id` always refers to the same underlying network-flow record on every run, so SHAP and LIME outputs (produced in later tasks) can be joined back to this repository unambiguously.

---

## Repository Contents

| File | Rows | Description |
|---|---|---|
| `baseline_predictions.parquet` | 82,332 | Model A predictions |
| `smote_predictions.parquet` | 82,332 | Model B predictions |
| `sample_registry.parquet` | 82,332 | Cross-reference for SHAP/LIME |

---

## Class Distribution (Testing Set, shared by both models)

| Class | Count |
|---|---|
| Normal | 37,000 |
| Generic | 18,871 |
| Exploits | 11,132 |
| Fuzzers | 6,062 |
| DoS | 4,089 |
| Reconnaissance | 3,496 |
| Analysis | 677 |
| Backdoor | 583 |
| Shellcode | 378 |
| Worms | 44 |

---

## Confidence Statistics

| Model | Mean | Median | Std | Min | Max |
|---|---|---|---|---|---|
| baseline | 0.814778 | 0.96 | 0.226161 | 0.19 | 1.0 |
| smote | 0.83185 | 0.96 | 0.215928 | 0.18 | 1.0 |

---

## Prediction Agreement Between Models

**Overall agreement rate:** 0.870743 (71,690 / 82,332 samples)  
**Disagreement count:** 10,642

| True Class | Total | Agreement Count | Agreement Rate |
|---|---|---|---|
| Analysis | 677 | 278 | 0.410635 |
| Backdoor | 583 | 160 | 0.274443 |
| DoS | 4,089 | 2,523 | 0.617021 |
| Exploits | 11,132 | 8,811 | 0.791502 |
| Fuzzers | 6,062 | 4,412 | 0.727813 |
| Generic | 18,871 | 18,691 | 0.990462 |
| Normal | 37,000 | 33,350 | 0.901351 |
| Reconnaissance | 3,496 | 3,148 | 0.900458 |
| Shellcode | 378 | 292 | 0.772487 |
| Worms | 44 | 25 | 0.568182 |

---

## Prediction Repository Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

Predictions from both Random Forest models (Task D.1) were archived against the shared, untouched testing set (82,332 samples), without retraining either model. Each archived record includes the predicted class, full per-class probability vector, confidence score (maximum predicted probability), true label, and a stable sample identifier. The two models agreed on 71,690 of 82,332 predictions (0.8707 agreement rate). This repository — not live inference — is the single source of truth subsequent SHAP (Task E.2) and LIME (Task E.3) explainability analyses will read from, ensuring both methods explain identical predictions.

---
*End of Prediction Repository Report*
