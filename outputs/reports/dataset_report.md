# UNSW-NB15 Dataset Report

**Generated:** 2026-06-29 04:07:30  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Research Question:** Does class imbalance degrade per-class XAI explanation quality in ML-based NIDS?

---

## 1. Dataset Summary

| Property | Value |
|---|---|
| Dataset Name | UNSW-NB15 |
| Source | University of New South Wales — Cyber Range Lab |
| Year | 2015 |
| Training Rows | 122,738 |
| Test Rows | 52,603 |
| Total Rows | 175,341 |
| Feature Columns | 44 numeric |
| Attack Classes | 10 |
| Label Type | Binary (0=Normal, 1=Attack) + Multi-class (attack_cat) |

---

## 2. Class Distribution (Training Set — Table 1)

| Attack Class | Count | % of Total | Imbalance Ratio (IR) | Binary Label |
|---|---|---|---|---|
| Normal | 39,200 | 31.938% | 1.0 | — |
| Generic | 28,000 | 22.813% | 1.4 | — |
| Exploits | 23,375 | 19.045% | 1.68 | — |
| Fuzzers | 12,729 | 10.371% | 3.08 | — |
| DoS | 8,585 | 6.995% | 4.57 | — |
| Reconnaissance | 7,343 | 5.983% | 5.34 | — |
| Analysis | 1,400 | 1.141% | 28.0 | — |
| Backdoors | 1,222 | 0.996% | 32.08 | — |
| Shellcode | 793 | 0.646% | 49.43 | — |
| Worms | 91 | 0.074% | 430.77 | — |

> **IR = majority class count ÷ class count.**  IR = 1 means balanced.

---

## 3. Imbalance Analysis

| Metric | Value |
|---|---|
| Most Imbalanced Class | Worms (IR = 430.8) |
| Classes with IR > 10 | 4 |
| Majority Class | Normal (39,200 instances) |
| Least Represented Class | Worms (91 instances) |

---

## 4. Feature Summary

| Property | Value |
|---|---|
| Numeric features | 44 |
| Categorical features | 6 |

### Numeric Feature Statistics (Training Set — sample)

| Feature | Min | Max | Mean | Std | 25th | 50th | 75th |
|---|---|---|---|---|---|---|---|
| dur | 0.0 | 18.247 | 1.188 | 1.449 | 0.272 | 0.697 | 1.538 |
| sbytes | 50.0 | 99997.0 | 19406.682 | 25557.12 | 2983.0 | 8601.0 | 19246.75 |
| dbytes | 0.0 | 19999.0 | 5037.927 | 5783.022 | 95.0 | 2854.0 | 8157.75 |
| rate | 0.1 | 499.999 | 94.141 | 128.57 | 7.051 | 43.191 | 96.057 |
| spkts | 1.0 | 499.0 | 249.704 | 144.347 | 125.0 | 250.0 | 375.0 |
| dpkts | 0.0 | 499.0 | 249.886 | 144.092 | 126.0 | 251.0 | 375.0 |
| sttl | 64.0 | 255.0 | 149.045 | 79.335 | 64.0 | 128.0 | 255.0 |
| dttl | 64.0 | 255.0 | 149.325 | 79.43 | 64.0 | 128.0 | 255.0 |
| sload | 0.0 | 387.585 | 41.18 | 42.244 | 9.498 | 24.864 | 62.024 |
| dload | 0.001 | 362.622 | 48.008 | 43.158 | 16.028 | 35.529 | 66.942 |

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

1. **Severe class imbalance confirmed:** The dataset contains attack classes with imbalance ratios up to 431×, meeting the study's criterion for investigating per-class XAI quality degradation.

2. **4 classes qualify as minority classes** (IR > 10), providing sufficient variation to test the correlation between imbalance ratio and XAI quality degradation (H3).

3. **The most severe minority class** is `Worms` with IR = 430.8 — this class will be the critical test for whether per-class explanation quality degrades for extreme imbalance.

4. **Per-class sample size concern:** Some minority classes in the test set may fall below the 30-instance threshold specified in the experimental blueprint. Statistical power for those classes will be limited; bootstrap CIs are required.

5. **Label duality:** UNSW-NB15 provides both binary (0/1) and multi-class (attack_cat) labels. This study uses attack_cat for per-class analysis and binary label for baseline detection metrics.

6. **No missing values detected:** Preprocessing imputation steps are still included as a safeguard but may not alter the data. This should be documented.

7. **Reviewer concern — dataset age:** UNSW-NB15 was published in 2015. Reviewers may question its realism for modern networks. The response: the dataset remains the standard benchmark in XAI-IDS literature (confirmed by P1–P15 corpus) and its imbalance properties are well-documented and well-understood.

---

## 7. Suitability for Research Contribution

UNSW-NB15 is **confirmed suitable** for the study because:

- 9 distinct attack classes spanning a wide IR range (1× to 431×)
- Well-documented imbalance, enabling validation against published statistics
- Small enough (~175K rows) for CPU-only training of Random Forest
- Used in prior XAI-IDS studies, so reviewers are familiar with the dataset
- No missing values: preprocessing artefacts will not confound XAI quality results

---
*End of Dataset Report*