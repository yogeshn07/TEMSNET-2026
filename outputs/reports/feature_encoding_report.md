# UNSW-NB15 Feature Encoding Report

**Generated:** 2026-06-30T05:36:39.183768+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Categorical Features Encoded

`proto, service, state` — identified automatically from `configs/preprocessing.yaml`'s frozen schema (`dtype == "object"`, excluding the target column), not hardcoded.

---

## Encoding Strategy

**Method:** Ordinal encoding (`sklearn.preprocessing.OrdinalEncoder`), applied uniformly to every categorical column.

**Why this method:** UNSW-NB15's categorical features have very different cardinalities (`proto`=133, `service`=13, `state`=9). One-hot encoding the highest-cardinality column would add over a hundred sparse binary columns, which (a) fragments SHAP feature attributions across many near-empty columns instead of one interpretable feature, conflicting with this project's XAI focus, and (b) provides no benefit for the locked research model, Random Forest, which splits on value thresholds rather than assuming a linear relationship between encoded magnitude and target.

**Why train-only fitting prevents leakage:** the encoder's `categories_` are learned exclusively from `X_train`; the testing split is read only via `.transform()`, which applies the already-fixed mapping and never updates it. No statistic, category, or ordering derived from the testing split can influence the training-time encoding.

---

## Unseen Category Handling

**Strategy:** `handle_unknown="use_encoded_value"` with a fixed sentinel (`-1`), distinct from every valid learned code (which are always >= 0). This is deterministic: the same unseen category always maps to the same sentinel value, and the sentinel never collides with a real learned category.

| Column | Unseen Categories | Affected Test Rows | Affected % |
|---|---|---|---|
| state | ACC, CLO | 5 | 0.0061% |

---

## Train/Test Integrity Verification

| Check | Result |
|---|---|
| Encoder fitted on training split only | Confirmed — `fit()` called once, on `X_train` |
| Testing split transformed via `.transform()` only | Confirmed |
| Raw dataset files unchanged | Confirmed (SHA-256 verified in self-tests) |
| Row order preserved | Confirmed (no sort/shuffle anywhere in the pipeline) |
| Column order preserved | Confirmed (matches original schema exactly) |

---

## Output Schema

**Output format:** parquet (pyarrow available)

| Split | Path | Rows | Columns |
|---|---|---|---|
| Training | `C:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026\data\interim\training_encoded.parquet` | 175,341 | 45 |
| Testing | `C:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026\data\interim\testing_encoded.parquet` | 82,332 | 45 |

---

## Encoded Feature Summary (Training Split)

| Column | Original Dtype | Encoded Dtype | Original Unique Count | Encoded Range |
|---|---|---|---|---|
| proto | object | float64 | 133 | [0.0, 132.0] |
| service | object | float64 | 13 | [0.0, 12.0] |
| state | object | float64 | 9 | [0.0, 8.0] |

---

## Limitations

- Ordinal encoding imposes an arbitrary, non-meaningful numeric order on nominal categories (e.g. `proto` codes do not reflect any true magnitude relationship). This is an acceptable, well-established practice for tree-based models but would need re-evaluation if a linear or distance-based model were substituted for Random Forest.
- **Important finding, not addressed in this task:** the feature matrix produced here still contains `id` (a row identifier with no predictive meaning) and `label` (the binary form of the target, which maps near-perfectly to `attack_cat` per Task C.2's label consistency check). Both remain present because this task's scope explicitly forbids feature removal. Using `label` as a model input feature would constitute severe target leakage and must be addressed before model training — most naturally in a feature selection stage.

---

## Feature Encoding Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

Categorical features (`proto, service, state`) were encoded using ordinal encoding fitted exclusively on the training split and applied to the testing split via `.transform()`. 2 unseen testing-only categories were detected and mapped deterministically to a fixed sentinel value (-1). Row and column order were preserved throughout; the raw dataset files were not modified. Output datasets (175,341 training rows, 82,332 testing rows) were saved in parquet format to `data/interim/`.

---
*End of Feature Encoding Report*
