# UNSW-NB15 Exploratory Data Analysis Report

**Generated:** 2026-06-30T04:37:05.832599+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## 1. Class Distribution Analysis

See `class_distribution.png`, `class_percentage.png`, `imbalance_ratio.png` and `outputs/tables/eda_class_distribution.csv`.

- Maximum imbalance ratio: **430.7692x** (`Worms`)
- Classes with severe imbalance (IR > 10): **4**

---

## 2 & 6. Numerical Feature Exploration & Distribution Characteristics

See `numerical_distributions.png` and `outputs/tables/eda_distribution_characteristics.csv`.

- Highly skewed features (|skewness| > 1.0): **33**
- Most skewed feature: `trans_depth` (skewness = 167.34)
- Heavy-tailed features (excess kurtosis > 3): **28**

---

## 3. Categorical Feature Exploration

See `categorical_distributions.png` and `outputs/tables/eda_categorical_frequency.csv`.

- Dominant category for `service`: `-`

---

## 4. Correlation Analysis

See `correlation_heatmap.png` and `outputs/tables/eda_correlation_pairs.csv`.

- Highly correlated pairs (|r| > 0.8): **29**
- Strongest pair: `is_ftp_login` & `ct_ftp_cmd` (r = 1.0)

---

## 5. Outlier Analysis

See `outlier_summary.png` and `outputs/tables/eda_outlier_summary.csv` (Tukey's IQR method).

- Highest outlier rate: `dload` (21.75% of rows)

---

## 7. Feature Relationship Exploration

See `feature_relationships.png` — scatter plots of the most highly correlated feature pairs, coloured by binary label (Normal vs. Attack), training set 5,000-row sample.

---

## 8. Research Observations

1. Severe class imbalance is confirmed in the training set: imbalance ratios range from 1.0 (Normal) to 430.8x (Worms), with 4 of 10 classes exceeding an imbalance ratio of 10.
2. 33 of 38 numerical features are highly skewed (|skewness| > 1.0); the most skewed feature is `trans_depth` (skewness = 167.34).
3. 28 of 38 numerical features are heavy-tailed (excess kurtosis > 3), indicating traffic-volume features contain extreme values far more frequently than a normal distribution would predict.
4. The `service` feature is dominated by a single category: `-`.
5. 29 numerical feature pairs exceed |Pearson r| = 0.8, indicating redundant traffic statistics; the strongest pair is `is_ftp_login` and `ct_ftp_cmd` (r = 1.00).
6. The feature with the highest outlier rate (Tukey's 1.5x IQR method) is `dload` at 21.75% of rows flagged as outliers.

---

## EDA Summary (Methodology Section)

| Property | Value |
|---|---|
| Maximum Imbalance Ratio | 430.7692x (`Worms`) |
| Classes with Severe Imbalance | 4 |
| Highly Skewed Features | 33 |
| Heavy-Tailed Features | 28 |
| Highly Correlated Pairs | 29 |
| Feature with Highest Outlier Rate | `dload` (21.75%) |

---
*End of Exploratory Data Analysis Report*
