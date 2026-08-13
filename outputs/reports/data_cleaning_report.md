# UNSW-NB15 Data Cleaning Report

**Generated:** 2026-06-30T05:14:40.421594+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Required Validations (Re-verified)

| Check | Training | Testing |
|---|---|---|
| Missing Values | 0 | 0 |
| Duplicate Rows | 0 | 0 |
| Infinite Values | 0 | 0 |
| Invalid Numeric (negative) | 0 | 0 |
| Label Consistency | PASS | PASS |

---

## Cleaning Decisions (Training Split)

### imputation — NOT PERFORMED
- **Reason:** No missing values detected in this split.
- **Evidence:** profile_missing_data() total_missing = 0 (re-verified live, consistent with Task B.2)
- **Expected impact:** None — no data altered.

### deduplication — NOT PERFORMED
- **Reason:** No duplicate rows detected in this split.
- **Evidence:** profile_duplicates() duplicate_count = 0 (re-verified live, consistent with Task B.2)
- **Expected impact:** None — no rows removed.

### categorical_whitespace_cleaning — NOT PERFORMED
- **Reason:** No leading/trailing whitespace detected in categorical columns.
- **Evidence:** validate_categorical_values() total_whitespace_issues = 0, total_empty_strings = 0
- **Expected impact:** None — categorical values already clean.

### infinite_value_handling — NOT PERFORMED
- **Reason:** No infinite values detected in numeric columns.
- **Evidence:** detect_infinite_values() total_infinite = 0
- **Expected impact:** None.

### invalid_numeric_correction — NOT PERFORMED
- **Reason:** No negative values detected in semantically non-negative numeric columns.
- **Evidence:** detect_invalid_numeric_values() total_invalid = 0
- **Expected impact:** None.

---

## Cleaning Decisions (Testing Split)

### imputation — NOT PERFORMED
- **Reason:** No missing values detected in this split.
- **Evidence:** profile_missing_data() total_missing = 0 (re-verified live, consistent with Task B.2)
- **Expected impact:** None — no data altered.

### deduplication — NOT PERFORMED
- **Reason:** No duplicate rows detected in this split.
- **Evidence:** profile_duplicates() duplicate_count = 0 (re-verified live, consistent with Task B.2)
- **Expected impact:** None — no rows removed.

### categorical_whitespace_cleaning — NOT PERFORMED
- **Reason:** No leading/trailing whitespace detected in categorical columns.
- **Evidence:** validate_categorical_values() total_whitespace_issues = 0, total_empty_strings = 0
- **Expected impact:** None — categorical values already clean.

### infinite_value_handling — NOT PERFORMED
- **Reason:** No infinite values detected in numeric columns.
- **Evidence:** detect_infinite_values() total_infinite = 0
- **Expected impact:** None.

### invalid_numeric_correction — NOT PERFORMED
- **Reason:** No negative values detected in semantically non-negative numeric columns.
- **Evidence:** detect_invalid_numeric_values() total_invalid = 0
- **Expected impact:** None.

---

## Unseen Categories (Test vs. Training)

*Categories present in the testing split's categorical columns that were never observed in training — relevant for the future encoding stage (Research Task C.3); reported only, not acted on here.*

- `state`: ACC, CLO

---

## Data Cleaning Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

**No cleaning actions were performed.** Re-verification of missing values, duplicate rows, infinite values, invalid numeric values, and categorical formatting confirmed the dataset requires no correction beyond what was already established in Research Tasks B.1-B.3.

**Actions intentionally not performed:** categorical_whitespace_cleaning, deduplication, imputation, infinite_value_handling, invalid_numeric_correction, because no supporting evidence was found for any of them in either split.

---
*End of Data Cleaning Report*
