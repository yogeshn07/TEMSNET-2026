# Citation Plan
## IEEE TEMSMET 2026 — Manuscript Citation Map

*For each manuscript section, lists which papers to cite, what claim each citation supports, and priority (Essential / Supporting / Optional).*

*All [CITATION REQUIRED] placeholders in `docs/paper/manuscript.md` should be replaced using this plan.*

---

## Abstract

No inline citations (IEEE style: abstract is citation-free).

---

## I. Introduction

| Sentence / Claim | Paper(s) | Priority |
|-----------------|---------|---------|
| "ML-based NIDS have demonstrated strong performance on benchmark datasets" | P16 (More 2024); P10 (Alshamy 2021); P13 (Wu 2022) | Essential |
| "Severe class imbalance in real-world network traffic" | P04 (Moustafa 2015); P19 (Razavi-Far 2025) | Essential |
| "SMOTE is widely adopted for class rebalancing" | P02 (Chawla 2002); P13 (Wu 2022) | Essential |
| "SMOTE improves minority-class recall in NIDS" | P10 (Alshamy 2021); P18 (Al-madani 2024) | Essential |
| "Adoption of XAI methods in security operations" | P12 (Charmet 2022); P15 (Rjoub 2023) | Essential |
| "SHAP — SHapley Additive exPlanations" | P07 (Lundberg 2017); P08 (Lundberg 2020) | Essential |
| "LIME — Local Interpretable Model-agnostic Explanations" | P05 (Ribeiro 2016) | Essential |
| "SHAP and LIME widely applied to NIDS models" | P17 (Gaspar 2024 — MLP-based); P20 (Hermosilla 2025a — tree-based) | Essential |

---

## II. Related Work

### A. Class Imbalance in NIDS
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "Class imbalance is a well-documented challenge in NIDS" | P04 (Moustafa 2015); P19 (Razavi-Far 2025) | Essential |
| "Majority-class bias suppresses minority-class detection" | P02 (Chawla 2002); P10 (Alshamy 2021) | Essential |
| "SMOTE generates synthetic minority instances by interpolation" | P02 (Chawla 2002) | Essential |
| "ADASYN as alternative to SMOTE" | P19 (Razavi-Far 2025) | Supporting |
| "Cost-sensitive learning for imbalance" | P19 (Razavi-Far 2025) | Optional |
| "SMOTE dominant in NIDS due to simplicity and reproducibility" | P13 (Wu 2022); P18 (Al-madani 2024) | Supporting |

### B. Explainable AI for Network Security
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "XAI application to NIDS has grown" | P12 (Charmet 2022); P15 (Rjoub 2023) | Essential |
| "SHAP grounded in cooperative game theory" | P07 (Lundberg 2017); P08 (Lundberg 2020) | Essential |
| "LIME approximates model locally with surrogate" | P05 (Ribeiro 2016) | Essential |
| "Both SHAP and LIME applied to tree-based NIDS models" | P20 (Hermosilla 2025a — XGBoost on UNSW-NB15) | Essential |
| "XAI methods applied to deep-learning/MLP-based NIDS" | P17 (Gaspar 2024 — MLP) | Supporting |
| "SHAP and LIME are complementary" | P20 (Hermosilla 2025a); P21 (Hermosilla 2025b) | Supporting |

### C. XAI Stability and Explanation Quality
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "XAI stability under perturbation studied in ML" | P11 (Visani 2022) | Essential |
| "LIME produces different explanations across runs (stochastic)" | P11 (Visani 2022) | Essential |
| "Adversarial perturbations affect LIME and SHAP" | P12 (Charmet 2022) | Supporting |
| "Sensitivity to hyperparameter choices" | P11 (Visani 2022) | Optional |
| "SMOTE effect on explanation stability not addressed in NIDS" | P09 (Patil 2020); P14 (Alarab 2022) — show closest; gap is their absence | Essential |
| "SMOTE changes feature importance rankings" | P09 (Patil 2020); P14 (Alarab 2022) | Essential |

### D. UNSW-NB15 Benchmark
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "UNSW-NB15 created at UNSW Cyber Range Lab" | P04 (Moustafa 2015) | Essential |
| "Predefined training/test split for reproducibility" | P04 (Moustafa 2015) | Essential |
| "Widely adopted as NIDS benchmark" | P16 (More 2024); P20 (Hermosilla 2025a) | Supporting |

---

## III. Methodology

### Dataset
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "UNSW-NB15 dataset [REF]" | P04 (Moustafa 2015) | Essential |
| "175,341 training / 82,332 test instances; 10 classes" | P04 (Moustafa 2015) | Essential |

### SMOTE
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "SMOTE [REF] with k_neighbors=5; sampling_strategy='auto'" | P02 (Chawla 2002) | Essential |
| "SMOTE implementation via imbalanced-learn [REF]" | P06 (Lemaître 2017) | Essential |

### Model
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "Random Forest [REF]" | P01 (Breiman 2001) | Essential |
| "RF implemented via scikit-learn [REF]" | P03 (Pedregosa 2011) | Essential |

### XAI Methods
| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "SHAP (TreeExplainer) [REF]" | P07 (Lundberg 2017); P08 (Lundberg 2020) | Essential |
| "LIME (LimeTabularExplainer) [REF]" | P05 (Ribeiro 2016) | Essential |

---

## IV. Experimental Setup

| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "scikit-learn [REF] for Random Forest and metrics" | P03 (Pedregosa 2011) | Essential |
| "imbalanced-learn [REF] for SMOTE" | P06 (Lemaître 2017) | Essential |
| "shap library [REF]" | P07 (Lundberg 2017) | Essential |
| "lime library [REF]" | P05 (Ribeiro 2016) | Essential |
| "scipy [REF] for statistical tests" | [VERIFY — no paper in our database; cite scipy directly] | Essential |

---

## V. Results

No new citation requirements beyond methodology (methods already cited). Reference tables/figures only.

---

## VI. Discussion

| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "Trustworthy AI frameworks in cybersecurity" | P12 (Charmet 2022); P15 (Rjoub 2023) | Supporting |
| "Regulatory guidance on AI transparency" | [FIND REGULATION/GDPR/EU-AI-ACT reference — not in current database] | Essential |
| "Explanation-consistency monitoring as a practical need" | P11 (Visani 2022); P15 (Rjoub 2023) | Supporting |

---

## VII. Limitations

| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "Other rebalancing techniques (ADASYN, cost-sensitive)" | P19 (Razavi-Far 2025) | Supporting |
| "Single model family (Random Forest)" | P01 (Breiman 2001) | Optional |
| "Single dataset (UNSW-NB15)" | P04 (Moustafa 2015) | Optional |
| "SHAP TreeExplainer is model-specific" | P08 (Lundberg 2020) | Supporting |

---

## VIII. Future Work

| Claim | Paper(s) | Priority |
|-------|---------|---------|
| "ADASYN, random undersampling, ensemble methods" | P19 (Razavi-Far 2025) | Supporting |
| "Gradient-based SHAP for neural networks" | P08 (Lundberg 2020) | Supporting |
| "Multi-dataset validation (CICIDS-2017, NSL-KDD)" | P10 (Alshamy 2021); P19 (Razavi-Far 2025) | Supporting |
| "Concept drift in live network traffic" | P04 (Moustafa 2015) | Optional |

---

## Complete Citation List (IEEE Format — verify all before submission)

```
[1]  L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.
     DOI: 10.1023/A:1010933404324

[2]  N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE: Synthetic
     Minority Over-sampling Technique," J. Artif. Intell. Res., vol. 16, pp. 321–357, 2002.
     DOI: 10.1613/jair.953

[3]  F. Pedregosa et al., "Scikit-learn: Machine Learning in Python," J. Mach. Learn.
     Res., vol. 12, pp. 2825–2830, 2011. DOI: 10.5555/1953048.2078195

[4]  N. Moustafa and J. Slay, "UNSW-NB15: A Comprehensive Data Set for Network Intrusion
     Detection Systems," in Proc. MilCIS 2015, Canberra, Australia, Nov. 2015, pp. 1–6.
     DOI: 10.1109/MilCIS.2015.7348942

[5]  M. T. Ribeiro, S. Singh, and C. Guestrin, "'Why Should I Trust You?': Explaining the
     Predictions of Any Classifier," in Proc. KDD 2016, San Francisco, USA, pp. 1135–1144.
     DOI: 10.1145/2939672.2939778

[6]  G. Lemaître, F. Nogueira, and C. K. Aridas, "Imbalanced-learn: A Python Toolbox to
     Tackle the Curse of Imbalanced Datasets in Machine Learning," J. Mach. Learn. Res.,
     vol. 18, no. 17, pp. 1–5, 2017. ID: JMLR:v18:16-365

[7]  S. M. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting Model Predictions,"
     in Advances in Neural Information Processing Systems (NeurIPS), 2017, pp. 4766–4777.

[8]  S. M. Lundberg, G. Erion, H. Chen et al., "From Local Explanations to Global
     Understanding with Explainable AI for Trees," Nature Mach. Intell., vol. 2, pp. 56–67,
     2020. DOI: 10.1038/s42256-019-0138-9

[9]  A. Patil, A. Framewala, and F. Kazi, "Explainability of SMOTE Based Oversampling for
     Imbalanced Dataset Problems," in Proc. IEEE ICICT 2020, San Jose, CA, pp. 41–45.
     DOI: 10.1109/ICICT50521.2020.9092325 [verify DOI before submission]

[10] R. Alshamy, M. Ghurab, S. Othman, and F. Alshami, "Intrusion Detection Model for
     Imbalanced Dataset Using SMOTE and Random Forest Algorithm," in Advances in Cyber
     Security (ACeS 2021), CCIS vol. 1487, Springer, Singapore, 2021, pp. 311–323.
     DOI: 10.1007/978-981-16-8059-5_22

[11] G. Visani, E. Bagli, F. Chesani, A. Poluzzi, and D. Capuzzo, "Statistical Stability
     Indices for LIME: Obtaining Reliable Explanations for Machine Learning Models," J. Oper.
     Res. Soc., vol. 73, no. 1, pp. 91–101, 2022.
     DOI: 10.1080/01605682.2020.1865846

[12] F. Charmet et al., "Explainable Artificial Intelligence for Cybersecurity: A Literature
     Survey," Ann. Telecommun., vol. 77, no. 11–12, pp. 789–812, 2022.
     DOI: 10.1007/s12243-022-00926-7

[13] T. Wu, H. Fan, H. Zhu, C. You, H. Zhou, and X. Huang, "Intrusion Detection System
     Combined Enhanced Random Forest with SMOTE Algorithm," EURASIP J. Adv. Signal
     Process., vol. 2022, art. 39, 2022. DOI: 10.1186/s13634-022-00871-6

[14] I. Alarab and S. Prakoonwit, "Effect of Data Resampling on Feature Importance in
     Imbalanced Blockchain Data: Comparison Studies of Resampling Techniques," Data Sci.
     Manag., vol. 5, no. 2, pp. 66–76, 2022.
     DOI: 10.1016/j.dsm.2022.04.003

[15] G. Rjoub et al., "A Survey on Explainable Artificial Intelligence for Cybersecurity,"
     IEEE Trans. Netw. Serv. Manag., vol. 20, no. 4, pp. 5115–5140, Dec. 2023.
     DOI: 10.1109/TNSM.2023.3282740

[16] S. More, M. Idrissi, H. Mahmoud, and A. T. Asyhari, "Enhanced Intrusion Detection
     Systems Performance with UNSW-NB15 Data Analysis," Algorithms, vol. 17, no. 2,
     art. 64, 2024. DOI: 10.3390/a17020064

[17] D. Gaspar, P. Silva, and C. Silva, "Explainable AI for Intrusion Detection Systems:
     LIME and SHAP Applicability on Multi-Layer Perceptron," IEEE Access, vol. 12,
     pp. 30164–30175, 2024. DOI: 10.1109/ACCESS.2024.3368377

[18] H. R. Sayegh, W. Dong, and A. M. Al-madani, "Enhanced Intrusion Detection with LSTM-Based
     Model, Feature Selection, and SMOTE for Imbalanced Data," Appl. Sci., vol. 14, no. 2,
     art. 479, 2024. DOI: 10.3390/app14020479

[19] V. Shanmugam, R. Razavi-Far, and E. Hallaji, "Addressing Class Imbalance in Intrusion
     Detection: A Comprehensive Evaluation of Machine Learning Approaches," Electronics,
     vol. 14, no. 1, art. 69, 2025. DOI: 10.3390/electronics14010069

[20] P. Hermosilla, S. Berríos, and H. Allende-Cid, "Explainable AI for Forensic Analysis:
     A Comparative Study of SHAP and LIME in Intrusion Detection Models," Appl. Sci.,
     vol. 15, no. 13, art. 7329, 2025. DOI: 10.3390/app15137329

[21] P. Hermosilla, M. Díaz, S. Berríos, and H. Allende-Cid, "Use of Explainable
     Artificial Intelligence for Analyzing and Explaining Intrusion Detection Systems,"
     Computers, vol. 14, no. 5, art. 160, 2025. DOI: 10.3390/computers14050160
```

---

## Pre-Submission Citation Checklist

- [ ] Verify DOI for P09 (Patil 2020): 10.1109/ICICT50521.2020.9092325
- [ ] Confirm all author lists are complete (check via DOI.org or IEEE Xplore)
- [ ] Add NeurIPS 2017 proceedings URL for Lundberg & Lee [7] (no registered DOI)
- [ ] Find EU AI Act / GDPR / trustworthy-AI regulation citation for Discussion section
- [ ] Confirm imbalanced-learn JMLR ID: JMLR:v18:16-365 (no numeric DOI; cite as JMLR identifier)
- [ ] Run a final Scopus / Web of Science search before camera-ready to catch any 2025–2026 publications that post-date this review
