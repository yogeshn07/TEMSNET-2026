# UNSW-NB15 Preprocessing Pipeline — Design Report

**Generated:** 2026-06-30T04:52:00.483150+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Pipeline Diagram

```
+-----------------------------------------------------------------+
|              UNSW-NB15 Preprocessing Pipeline (C.1)             |
+-----------------------------------------------------------------+
|   [TRAINING SET]                          [TESTING SET]         |
|        |                                       |                |
|        v                                       v                |
|   1. Dataset Validation  ----------------  1. Dataset Validation|
|        |                                       |                |
|        v                                       v                |
|   2. Data Loading        ----------------  2. Data Loading      |
|        |                                       |                |
|        v                                       v                |
|   3. Schema Verification ----------------  3. Schema Verification|
|        |                                       |                |
|        v                                       v                |
|   X_train, y_train                        X_test, y_test        |
|        |                                       |                |
|        v                                       v                |
|   4. Missing Value Handling          [PLANNED — C.2]            |
|   5. Duplicate Handling              [PLANNED — C.2]            |
|   6. Feature Encoding   (fit TRAIN only, transform both) [C.3]  |
|   7. Feature Scaling    (fit TRAIN only, transform both) [C.3]  |
|   8. Feature Selection  (fit TRAIN only, transform both) [C.4]  |
|   9. Class Balancing    (TRAIN only, TEST untouched)     [C.5]  |
|        |                                       |                |
|        v                                       v                |
|  10. Export Processed Dataset  ----------  10. Export Processed |
|      data/processed/train.*                data/processed/test.*|
+-----------------------------------------------------------------+
  NOTE: Training and testing data are never merged at any stage.
  NOTE: Any "fit" operation (stages 6-9) learns parameters from
        the TRAINING split only and is applied to TEST via
        transform() — never re-fit on test data.
```

---

## Execution Sequence

| Order | Stage | Status | Research Task | Description |
|---|---|---|---|---|
| 1 | Dataset Validation | implemented | C.1 (this task, reuses B.1) | Verify raw dataset files exist and pass integrity checks before loading. |
| 2 | Data Loading | implemented | C.1 (this task, reuses B.2/B.3 loader) | Load training and testing CSVs as two independent DataFrames. |
| 3 | Schema Verification | implemented | C.1 (this task) | Verify column presence, column order, dtypes, and target column against a frozen schema contract. |
| 4 | Missing Value Handling | planned | C.2 | Impute or flag missing values (UNSW-NB15 currently has none; safeguard for future data). |
| 5 | Duplicate Handling | planned | C.2 | Detect and decide how to handle duplicate rows within each split. |
| 6 | Feature Encoding | planned | C.3 | Encode categorical features (proto, service, state) into numeric representations. |
| 7 | Feature Scaling | planned | C.3 | Scale/normalise numerical features. |
| 8 | Feature Selection | planned | C.4 | Select a feature subset based on training-set statistics (e.g. variance, correlation, importance). |
| 9 | Class Balancing | planned | C.5 | Address class imbalance (e.g. oversampling, undersampling, class weighting) for model training. |
| 10 | Export Processed Dataset | planned | C.6 | Persist the fully processed train/test feature and target arrays to data/processed/. |

**Stage registry integrity check:** PASS

---

## Data Leakage Prevention Strategy

- Training and testing CSVs are loaded as two independent DataFrames and never concatenated.
- Each split is validated against the same static schema contract, never against the other split's data.
- X/y separation removes the target column only; no feature value is read, imputed, encoded, or scaled.
- Stage order is fixed by an immutable registry (PIPELINE_STAGES), making out-of-order execution a visible code change.
- Future fit-based stages (6-9) must fit on X_train only and transform both splits; class balancing (9) applies to training only.

---

## Responsibilities of Each Future Stage

**4. Missing Value Handling** (C.2)  
Impute or flag missing values (UNSW-NB15 currently has none; safeguard for future data).  
*Leakage rule:* Any imputer must be fit on X_train only and applied to X_test via transform().

**5. Duplicate Handling** (C.2)  
Detect and decide how to handle duplicate rows within each split.  
*Leakage rule:* Deduplication is evaluated independently per split; rows are never compared across splits.

**6. Feature Encoding** (C.3)  
Encode categorical features (proto, service, state) into numeric representations.  
*Leakage rule:* Encoder (e.g. OneHotEncoder, OrdinalEncoder) fit on X_train categories only; test set categories not seen during fit are handled explicitly, never used to refit.

**7. Feature Scaling** (C.3)  
Scale/normalise numerical features.  
*Leakage rule:* Scaler statistics (mean, std, min, max) computed on X_train only, applied to X_test via transform().

**8. Feature Selection** (C.4)  
Select a feature subset based on training-set statistics (e.g. variance, correlation, importance).  
*Leakage rule:* Selection criteria computed on X_train/y_train only; the same selected columns are then applied to X_test.

**9. Class Balancing** (C.5)  
Address class imbalance (e.g. oversampling, undersampling, class weighting) for model training.  
*Leakage rule:* Applied to the training split only; the test split must retain the real-world class distribution for valid evaluation.

**10. Export Processed Dataset** (C.6)  
Persist the fully processed train/test feature and target arrays to data/processed/.  
*Leakage rule:* Train and test exported as separate files; no merged artefact is ever produced.

---

## Current Validation Results (Stages 1-3)

**Target column:** `attack_cat`

| Split | Rows | Features (X) | Schema Status |
|---|---|---|---|
| Training | 175,341 | 44 | PASS |
| Testing | 82,332 | 44 | PASS |

---

## Preprocessing Pipeline Design Summary

*(Suitable for inclusion in the Methodology section)*

The preprocessing pipeline follows a fixed 10-stage sequence applied independently to the training and testing splits of UNSW-NB15. Stages 1-3 (dataset validation, loading, and schema verification) are implemented and confirmed passing for both splits. Stages 4-9 (missing value handling, duplicate handling, feature encoding, feature scaling, feature selection, and class balancing) are architecturally reserved but not yet implemented, ensuring no transformation decision is made before the exploratory analysis (B.3) is fully incorporated into the design. Data leakage is prevented structurally: the two splits are never merged, and every future parameter-learning stage is contractually required to fit on the training split only.

---
*End of Preprocessing Pipeline Design Report*
