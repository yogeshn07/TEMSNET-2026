# Research Gap Analysis
## IEEE TEMSMET 2026 — XAI Explanation Quality under SMOTE in RF-Based NIDS

*Generated: 2026-07-03. Based on 21 verified peer-reviewed papers. All gap claims are traceable to the comparison_matrix.csv.*

---

## 1. Theme-by-Theme Gap Inventory

### Theme 1: UNSW-NB15 Benchmark Studies

**What prior work solved:**
- Established UNSW-NB15 as a credible NIDS benchmark with modern attack categories [P04 — Moustafa & Slay 2015]
- Demonstrated Random Forest achieves strong overall accuracy (F1 ≈ 97.8%) on UNSW-NB15 without balancing [P16 — More et al. 2024]

**What prior work did NOT solve:**
- None of the UNSW-NB15 studies (P04, P16) combined class balancing with explainability analysis
- No prior work on UNSW-NB15 reported paired statistical tests comparing a balanced vs. imbalanced model
- Minority-class performance on UNSW-NB15 (Worms, Backdoor, Analysis) under SMOTE has not been systematically reported with effect sizes

**How our work differs:**
- We use UNSW-NB15's predefined train/test split and report all 10 per-class metrics for both Baseline and SMOTE models, with paired statistical validation (McNemar, bootstrap CIs) on the full 82,332-sample test set

---

### Theme 2: SMOTE for Network Intrusion Detection

**What prior work solved:**
- SMOTE improves minority-class recall in NIDS across multiple datasets (NSL-KDD, IoT) [P10, P13, P18]
- Combined SMOTE + RF achieves high accuracy on NSL-KDD [P10, P13]
- SMOTE + LSTM effective for IoT NIDS [P18]

**What prior work did NOT solve:**
- No paper applied SMOTE to UNSW-NB15 with the original predefined split and reported paired per-class comparison
- No paper measured the effect of SMOTE on SHAP or LIME feature attribution in NIDS
- No paper reported effect sizes (Cohen's h, rank-biserial r) for SMOTE's impact in NIDS

**How our work differs:**
- We apply SMOTE to UNSW-NB15 and measure both predictive and explanatory effects, computing effect sizes for both

---

### Theme 3: Class Imbalance Evaluation in NIDS

**What prior work solved:**
- Comprehensive comparison of resampling strategies (SMOTE, ADASYN, ROS, RUS) for NIDS across multiple imbalance levels [P19 — Razavi-Far et al. 2025]
- Established F1 and G-mean as appropriate metrics for imbalanced NIDS

**What prior work did NOT solve:**
- No study examined how class imbalance correction changes the model's explanation output (feature attribution rankings)
- No paper measured explanation-level effect sizes alongside predictive effect sizes

**How our work differs:**
- To our knowledge, no prior study has compared predictive effect sizes against explanation effect sizes under SMOTE in any NIDS setting; we show they are asymmetric

---

### Theme 4: Explainable AI Foundations (SHAP, LIME)

**What prior work solved:**
- LIME [P05 — Ribeiro et al. 2016]: local model-agnostic explanation via surrogate linear models
- SHAP [P07 — Lundberg & Lee 2017]: Shapley-value-based unified attribution
- TreeSHAP [P08 — Lundberg et al. 2020]: exact polynomial-time SHAP for tree ensembles
- LIME stability quantification: CSI/VSI indices [P11 — Visani et al. 2022]

**What prior work did NOT solve:**
- No prior work measured SHAP or LIME instability specifically caused by training data rebalancing (vs. repeated sampling or adversarial perturbation)
- No prior work compared SHAP and LIME sensitivity to the same distribution intervention (SMOTE)

**How our work differs:**
- We quantify and compare how SMOTE shifts SHAP and LIME feature attribution rankings using the same paired statistical framework, reporting rank-biserial r for both methods

---

### Theme 5: XAI Applied to Network Intrusion Detection

**What prior work solved:**
- LIME and SHAP both applicable to MLP-based IDS [P17 — Gaspar et al. 2024]
- SHAP and LIME are complementary; combined use recommended for IDS forensic analysis [P20 — Hermosilla et al. 2025]
- SHAP provides globally coherent rankings; LIME is more locally variable [P20, P21 — Hermosilla et al. 2025]

**What prior work did NOT solve:**
- P17: No SMOTE; no RF; no stability comparison between models trained on different distributions
- P20/P21: No SMOTE; no paired comparison of baseline vs. balanced model; no Wilcoxon or McNemar tests; no effect sizes
- No prior work quantified the rank-biserial effect size for SHAP or LIME explanation shifts under training distribution change in NIDS

**How our work differs:**
- We systematically compare SHAP and LIME feature attribution rankings BEFORE and AFTER SMOTE rebalancing using paired Wilcoxon tests with effect sizes, on the same UNSW-NB15 dataset
- We show LIME is ~6.8× more sensitive than predictive metrics — a new empirical finding

---

### Theme 6: XAI Stability and Evaluation

**What prior work solved:**
- LIME stability can be quantified via CSI/VSI indices (variance across repeated runs) [P11 — Visani et al. 2022]
- SHAP is generally more stable than LIME due to its deterministic Shapley formulation [P20]

**What prior work did NOT solve:**
- Stability under TRAINING DATA DISTRIBUTION CHANGE is distinct from stability under repeated sampling at inference time
- No prior work measured Spearman rank correlation of SHAP/LIME importance vectors between two models trained on different distributions and applied effect-size analysis

**How our work differs:**
- We measure explanation stability under a specific intervention (SMOTE) rather than repeated inference; we use Wilcoxon signed-rank test + rank-biserial r + Spearman ρ + top-k overlap as a multi-metric stability battery

---

### Theme 7: SMOTE Effects on Explainability (closest prior work)

**What prior work solved:**
- P09 [Patil et al. 2020]: Demonstrated that SMOTE changes feature importance and decision boundaries in generic imbalanced datasets; showed LIME explanations differ post-SMOTE
- P14 [Alarab & Prakoonwit 2022]: Showed resampling (including SMOTE) changes feature ranking overlap in blockchain imbalanced data

**What prior work did NOT solve:**
- P09: No NIDS context; no UNSW-NB15; no SHAP; no statistical tests; no effect-size analysis; n=1 dataset (UCI generic)
- P14: No NIDS; no SHAP/LIME; no Wilcoxon; no paired statistical analysis; no predictive vs. explanatory effect comparison

**How our work differs:**
- We operate in the NIDS domain (UNSW-NB15), use both SHAP and LIME, apply paired statistical tests with Holm correction, and report effect sizes for both predictive and explanation changes — enabling direct comparison of predictive vs. explanatory sensitivity

---

### Theme 8: XAI for Cybersecurity Surveys

**What surveys identified as open problems:**
- "Explanation quality and robustness under distribution shift is under-studied" [P15 — Rjoub et al. 2023]
- "XAI evaluation metrics for NIDS remain an open challenge" [P12 — Charmet et al. 2022]
- Both surveys identify the intersection of class imbalance and XAI reliability as a gap

**How our work addresses the survey-identified gaps:**
- We provide, to our knowledge, the first empirical evidence (in the NIDS context) that class rebalancing introduces asymmetric shifts in explanation quality vs. predictive quality
- Our statistical framework (McNemar + Wilcoxon + bootstrap CI + effect sizes) operationalises the "explanation evaluation" gap identified by both surveys

---

## 2. Composite Gap Statement

No existing study:
1. Applies SMOTE to UNSW-NB15 (predefined split, 10-class multiclass)
2. Evaluates BOTH SHAP and LIME attribution stability before/after rebalancing
3. Uses paired statistical tests (McNemar + Wilcoxon + bootstrap CIs + Holm correction)
4. Reports effect sizes for BOTH predictive metrics (Cohen's h) AND explanation metrics (rank-biserial r)
5. Directly compares predictive sensitivity vs. explanatory sensitivity to SMOTE in any NIDS setting

The gap is confirmed in 7 of 8 surveyed themes and directly identified as an open problem in both cybersecurity XAI surveys (P12, P15).

---

## 3. Novelty Assessment

| Dimension | Assessment | Evidence |
|-----------|-----------|---------|
| Topic novelty: SMOTE effect on SHAP/LIME in NIDS | **Strongly novel** | No prior paper combines these three elements |
| Methodological novelty: paired statistics + effect sizes for explanation stability | **Moderately novel** | Statistical approach is established; its application to this comparison is new |
| Dataset: UNSW-NB15 with predefined split | **Incremental** | UNSW-NB15 widely used; our specific split usage follows standard protocol |
| Model: Random Forest | **Incremental** | RF is a standard NIDS baseline; not a new contribution |
| Finding: LIME ~6.8× more sensitive than predictive metrics | **Strongly novel** | No prior paper reports this asymmetry in any domain |
| Finding: Explanation sensitivity > predictive sensitivity to SMOTE | **Moderately to Strongly novel** | P09 and P14 hint at this but do not quantify it with effect sizes or in NIDS |

**Overall novelty verdict: Moderately to Strongly Novel**

**Justification:**
The combination of (a) NIDS domain, (b) SMOTE intervention, (c) SHAP+LIME comparison, (d) paired statistical tests with effect sizes, and (e) the predictive-vs-explanatory sensitivity asymmetry is not present in any prior published work identified in this review. The specific empirical finding — that LIME explanation shifts are ~6.8× larger in practical effect size than the largest predictive metric shift — is a new contribution to the literature.

**Caveat on "first paper" claims:**
The search covered IEEE Xplore, MDPI, Springer, ACM, Elsevier, and arXiv through 2026-07. However, a comprehensive database search (Scopus, Web of Science) is recommended before making definitive "first ever" claims in the manuscript. The available evidence strongly supports "first study to…" framing for the specific combination.

---

## 4. Recommended Citation Framing by Claim

| Claim in manuscript | Supported by |
|--------------------|-------------|
| "Class imbalance is pervasive in NIDS" | P04, P10, P13, P18, P19 |
| "SMOTE improves minority-class recall in NIDS" | P02, P10, P13, P18 |
| "SHAP and LIME are widely applied to NIDS" | P07, P08, P12, P15, P17, P20 |
| "XAI explanation stability under distribution shift is under-studied" | P11, P12, P15 |
| "SMOTE changes feature importance rankings" | P09, P14 |
| "LIME is inherently less stable than SHAP" | P11, P20 |
| "No prior work compares SMOTE effect on SHAP vs LIME in NIDS with effect sizes" | Gap: absence of such work across P01–P21 |
| "Accuracy-only validation misses explanation shifts" | Implied by P12, P15, P09, P14; directly demonstrated by our results |
