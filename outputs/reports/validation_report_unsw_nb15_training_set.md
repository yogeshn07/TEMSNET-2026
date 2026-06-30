# Data Validation Report — UNSW_NB15_training-set.csv

**Generated:** 2026-06-29 04:05:35  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  

---

## 1. File Overview

| Property | Value |
|---|---|
| File | `UNSW_NB15_training-set.csv` |
| Total Rows | 122,738 |
| Total Columns | 52 |
| Numeric Features | 46 |
| Categorical Features | 6 |

---

## 2. Missing Values

✅ **No missing values detected.**

---

## 3. Duplicate Rows

| Property | Value |
|---|---|
| Duplicate Rows | 0 |
| Duplicate % | 0.0% |

✅ No duplicates.

---

## 4. Label Consistency

**Binary label values found:** [0, 1]  
**Label consistent:** ✅ Yes  


---

## 5. Numeric Anomalies

✅ **No infinite or NaN values detected in numeric columns.**

---

## 6. Class Distribution

| Attack Class   | Count  | % of Total | Imbalance Ratio (IR) | Binary Label |
| -------------- | ------ | ---------- | -------------------- | ------------ |
| Normal         | 39,200 | 31.938%    | 1.0                  | 0            |
| Generic        | 28,000 | 22.813%    | 1.4                  | 1            |
| Exploits       | 23,375 | 19.045%    | 1.68                 | 1            |
| Fuzzers        | 12,729 | 10.371%    | 3.08                 | 1            |
| DoS            | 8,585  | 6.995%     | 4.57                 | 1            |
| Reconnaissance | 7,343  | 5.983%     | 5.34                 | 1            |
| Analysis       | 1,400  | 1.141%     | 28.0                 | 1            |
| Backdoors      | 1,222  | 0.996%     | 32.08                | 1            |
| Shellcode      | 793    | 0.646%     | 49.43                | 1            |
| Worms          | 91     | 0.074%     | 430.77               | 1            |

> **Imbalance Ratio (IR):** majority class count ÷ class count.  
> IR = 1 means balanced; higher IR = more severe imbalance.

---

## 7. Validation Summary

✅ **All validation checks passed. Dataset is ready for preprocessing.**