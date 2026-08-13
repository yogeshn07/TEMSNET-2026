# UNSW-NB15 Class Rebalancing Report

**Generated:** 2026-06-30T08:21:35.578878+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Balancing Strategy

**Method:** SMOTE  
**Parameters:** `{'sampling_strategy': 'auto', 'k_neighbors': 5}`  
**Random seed:** 42 (from `configs/experiment.yaml`)

**Why SMOTE:** SMOTE generates synthetic minority-class samples by interpolating between real nearest neighbours within the same class, rather than duplicating existing rows (random oversampling) or discarding majority-class information (undersampling). This preserves the full training signal from the majority class while giving minority classes (down to 130 real `Worms` samples) enough synthetic density for the Phase D models to learn from, directly supporting this study's comparison of explanation quality between imbalanced and balanced training conditions.

---

## Why Balancing Is Applied Only to the Training Set

Balancing the training set lets the model learn from a less skewed class distribution. Balancing the **testing** set would corrupt evaluation: the testing distribution must reflect the real-world class frequencies the model will face, including the genuine rarity of classes like `Worms`. Synthetically inflating test-set minority classes would make per-class metrics and SHAP explanation quality comparisons meaningless, since they would no longer measure performance against real, naturally-occurring traffic patterns.

---

## Pre-Balancing Analysis

| Class | Count | % of Total | Imbalance Ratio |
|---|---|---|---|
| Normal | 56,000 | 31.9378% | 1.0 |
| Generic | 40,000 | 22.8127% | 1.4 |
| Exploits | 33,393 | 19.0446% | 1.677 |
| Fuzzers | 18,184 | 10.3706% | 3.0796 |
| DoS | 12,264 | 6.9944% | 4.5662 |
| Reconnaissance | 10,491 | 5.9832% | 5.3379 |
| Analysis | 2,000 | 1.1406% | 28.0 |
| Backdoor | 1,746 | 0.9958% | 32.0733 |
| Shellcode | 1,133 | 0.6462% | 49.4263 |
| Worms | 130 | 0.0741% | 430.7692 |

**Total training samples (before):** 175,341

---

## Post-Balancing Analysis

| Class | Count | % of Total | Imbalance Ratio |
|---|---|---|---|
| Normal | 56,000 | 10.0% | 1.0 |
| Backdoor | 56,000 | 10.0% | 1.0 |
| Analysis | 56,000 | 10.0% | 1.0 |
| Fuzzers | 56,000 | 10.0% | 1.0 |
| Shellcode | 56,000 | 10.0% | 1.0 |
| Reconnaissance | 56,000 | 10.0% | 1.0 |
| Exploits | 56,000 | 10.0% | 1.0 |
| DoS | 56,000 | 10.0% | 1.0 |
| Worms | 56,000 | 10.0% | 1.0 |
| Generic | 56,000 | 10.0% | 1.0 |

**Total training samples (after):** 560,000  
**Achieved balance (max imbalance ratio post-balancing):** 1.0  
**Total synthetic samples generated:** 384,659

### Synthetic Samples Per Class

| Class | Count Before | Count After | Synthetic Generated |
|---|---|---|---|
| Normal | 56,000 | 56,000 | 0 |
| Generic | 40,000 | 56,000 | 16,000 |
| Exploits | 33,393 | 56,000 | 22,607 |
| Fuzzers | 18,184 | 56,000 | 37,816 |
| DoS | 12,264 | 56,000 | 43,736 |
| Reconnaissance | 10,491 | 56,000 | 45,509 |
| Analysis | 2,000 | 56,000 | 54,000 |
| Backdoor | 1,746 | 56,000 | 54,254 |
| Shellcode | 1,133 | 56,000 | 54,867 |
| Worms | 130 | 56,000 | 55,870 |

---

## Testing Dataset Integrity

| Check | Result |
|---|---|
| SMOTE fit on testing data | Never — `fit_resample()` called only on training X/y |
| Testing dataset row count | Unchanged (verified in self-tests) |
| Testing dataset content | Byte-identical copy of `testing_selected.parquet` (verified via SHA-256 in self-tests) |

---

## Output Datasets

| File | Rows | Columns | Description |
|---|---|---|---|
| `training_baseline.parquet` | 175,341 | 43 | Untouched copy of Task C.4's training_selected.parquet |
| `training_balanced_smote.parquet` | 560,000 | 43 | SMOTE-balanced training set |
| `testing_baseline.parquet` | 82,332 | 43 | Untouched copy of Task C.4's testing_selected.parquet (never balanced) |

---

## Limitations of Synthetic Oversampling

- **Fractional encoded-categorical values:** vanilla SMOTE (not SMOTENC) interpolates linearly across *all* features, including the ordinal-encoded `proto`/`service`/`state` columns and integer count features. Synthetic rows can therefore contain fractional values for columns that originally held only integer codes (e.g. a synthetic `proto` value between two real category codes), which do not correspond to any real category. This is a known property of applying standard SMOTE to encoded categorical data, not a defect in this implementation.
- **Extreme oversampling ratio for the rarest class:** `Worms` is synthesised from only 130 real training examples up to the majority class count, an oversampling factor of roughly 430.8x. With so few real neighbours, SMOTE's interpolated samples span a much smaller region of feature space than the true population likely occupies, risking overly narrow synthetic diversity for this class.
- **No guarantee of semantic realism:** SMOTE operates purely in encoded feature space; it has no awareness of valid network-flow semantics, so synthetic samples are not guaranteed to represent physically plausible traffic, only statistically plausible interpolations.

---

## Class Rebalancing Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

The training set (175,341 rows, imbalance ratio up to 430.7692x) was balanced using SMOTE (sampling_strategy="auto", k_neighbors=5, random_state=42), generating 384,659 synthetic samples and producing a final balanced training set of 560,000 rows (imbalance ratio = 1.0). The testing set (82,332 rows) was never balanced, fitted on, or transformed, preserving its real-world class distribution for unbiased evaluation. Both the original imbalanced training set and the SMOTE-balanced training set are retained as parallel experimental conditions for Phase D's predictive performance and explanation-quality comparison.

---
*End of Class Rebalancing Report*
