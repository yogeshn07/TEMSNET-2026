# UNSW-NB15 Dataset Report

**Generated:** 2026-06-30 04:16:52  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Research Question:** Does class imbalance degrade per-class XAI explanation quality in ML-based NIDS?

---

## 1. Dataset Summary

| Property | Value |
|---|---|
| Dataset Name | UNSW-NB15 |
| Source | University of New South Wales — Cyber Range Lab |
| Year | 2015 |
| Training Rows | 175,341 |
| Test Rows | 82,332 |
| Total Rows | 257,673 |
| Feature Columns | 39 numeric, 4 categorical |
| Attack Classes | 10 |
| Label Type | Binary (0=Normal, 1=Attack) + Multi-class (attack_cat) |

---

## 2. Class Distribution (Training Set — Table 1)

| Attack Class | Count | % of Total | Imbalance Ratio (IR) | Binary Label |
|---|---|---|---|---|
| Normal | 56,000 | 31.938% | 1.0 | — |
| Generic | 40,000 | 22.813% | 1.4 | 1 |
| Exploits | 33,393 | 19.045% | 1.68 | 1 |
| Fuzzers | 18,184 | 10.371% | 3.08 | 1 |
| DoS | 12,264 | 6.994% | 4.57 | 1 |
| Reconnaissance | 10,491 | 5.983% | 5.34 | 1 |
| Analysis | 2,000 | 1.141% | 28.0 | 1 |
| Backdoor | 1,746 | 0.996% | 32.07 | 1 |
| Shellcode | 1,133 | 0.646% | 49.43 | 1 |
| Worms | 130 | 0.074% | 430.77 | 1 |

> **IR = majority class count ÷ class count.**  IR = 1 means balanced.

---

## 3. Imbalance Analysis

| Metric | Value |
|---|---|
| Most Imbalanced Class | Worms (IR = 430.77) |
| Classes with IR > 10 | 4 |
| Majority Class | Normal (56,000 instances) |
| Least Represented Class | Worms (130 instances) |

---

## 4. Feature Summary

| Property | Value |
|---|---|
| Numeric features | 39 |
| Categorical features | 4 |

### Numeric Feature Statistics (Training Set — sample)

| Feature | Min | Max | Mean | Std | 25th | 50th | 75th |
|---|---|---|---|---|---|---|---|
| dur | 0.0 | 59.999989 | 1.359389 | 6.480249 | 8e-06 | 0.001582 | 0.668069 |
| sbytes | 28.0 | 12965233.0 | 8844.843836 | 174765.644309 | 114.0 | 430.0 | 1418.0 |
| dbytes | 0.0 | 14655550.0 | 14928.918564 | 143654.217718 | 0.0 | 164.0 | 1102.0 |
| rate | 0.0 | 1000000.003 | 95406.187105 | 165400.978457 | 32.78614 | 3225.80652 | 125000.0003 |
| spkts | 1.0 | 9616.0 | 20.298664 | 136.887597 | 2.0 | 2.0 | 12.0 |
| dpkts | 0.0 | 10974.0 | 18.969591 | 110.258271 | 0.0 | 2.0 | 10.0 |
| sttl | 0.0 | 255.0 | 179.546997 | 102.940011 | 62.0 | 254.0 | 254.0 |
| dttl | 0.0 | 254.0 | 79.609567 | 110.506863 | 0.0 | 29.0 | 252.0 |
| sload | 0.0 | 5988000256.0 | 73454033.194063 | 188357447.000203 | 13053.33887 | 879674.75 | 88888888.0 |
| dload | 0.0 | 22422730.0 | 671205.574188 | 2421312.388757 | 0.0 | 1447.022705 | 27844.87109 |

---

## 5. Data Quality Report

| Check | Training Set | Test Set |
|---|---|---|
| Missing values | 0 | 0 |
| Duplicate rows | 0 | 0 |
| Infinite values | 0 | 0 |

---

## 6. Research Observations

*(Observations relevant to the research hypothesis — no solutions suggested)*

1. **Severe class imbalance confirmed:** The dataset contains attack classes with imbalance ratios up to 430.77×, meeting the study's criterion for investigating per-class XAI quality degradation.

2. **4 classes qualify as minority classes** (IR > 10), providing sufficient variation to test the correlation between imbalance ratio and XAI quality degradation (H3).

3. **The most severe minority class** is `Worms` with IR = 430.77 — this class will be the critical test for whether per-class explanation quality degrades for extreme imbalance.

4. **Per-class sample size concern:** Some minority classes in the test set may fall below the 30-instance threshold specified in the experimental blueprint. Statistical power for those classes will be limited; bootstrap CIs are required.

5. **Label duality:** UNSW-NB15 provides both binary (0/1) and multi-class (attack_cat) labels. This study uses attack_cat for per-class analysis and binary label for baseline detection metrics.

6. **No missing values detected:** Preprocessing imputation steps are still included as a safeguard but may not alter the data. This should be documented.

7. **Reviewer concern — dataset age:** UNSW-NB15 was published in 2015. Reviewers may question its realism for modern networks. The response: the dataset remains the standard benchmark in XAI-IDS literature (confirmed by P1–P15 corpus) and its imbalance properties are well-documented and well-understood.

---

## 7. Suitability for Research Contribution

UNSW-NB15 is **confirmed suitable** for the study because:

- 9 distinct attack classes spanning a wide IR range (1× to 430.77×)
- Well-documented imbalance, enabling validation against published statistics
- Small enough (~257K rows total) for CPU-only training of Random Forest
- Used in prior XAI-IDS studies, so reviewers are familiar with the dataset
- No missing values: preprocessing artefacts will not confound XAI quality results

---
*End of Dataset Report*
