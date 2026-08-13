# Literature Review
## IEEE TEMSMET 2026 — Impact of Class Imbalance on XAI Explanation Quality in ML-Based NIDS

**Status:** Evidence base complete. Do NOT write Related Work section yet. Await author approval.

**Coverage:** 21 peer-reviewed papers spanning 2001–2025.
**Search date:** 2026-07-03
**Sources searched:** IEEE Xplore, ACM Digital Library, Springer, MDPI, Elsevier, Nature, JMLR, arXiv (preprints excluded unless published or accepted)

---

## Section 1 — Foundational Papers (Pre-2021)

These are landmark papers that the field builds on; must be cited even though they pre-date the 2021–2026 priority window.

---

### [P01] Breiman, L. (2001). Random Forests.
*Machine Learning*, 45(1), 5–32. DOI: 10.1023/A:1010933404324. **Publisher:** Springer.

**Research problem:** Ensemble classification via bagged decision trees with random feature subsampling.

**Dataset:** UCI benchmark repositories.

**Models:** Random Forest (introduced).

**XAI methods:** None (Gini impurity as built-in feature ranking only).

**Balancing methods:** None.

**Evaluation metrics:** Accuracy; OOB (Out-of-Bag) error; feature importance (Gini).

**Main findings:** Random Forest consistently outperforms single decision trees and many competing algorithms across benchmark tasks. The OOB error provides an unbiased internal estimate of generalisation error without a separate validation set. Feature importance rankings via mean Gini decrease identify influential variables but are not causally interpretable.

**Limitations:** No handling of class imbalance; no formal XAI beyond Gini importance; Gini-based importance is biased toward high-cardinality features.

**Relation to our work:** Foundational model choice. Our study uses Random Forest as the classifier for both Baseline and SMOTE models. The lack of built-in XAI motivates the use of SHAP and LIME as post-hoc explanation methods.

**Possible citation locations:** Methodology (model description); Introduction (justification of RF as standard NIDS classifier).

---

### [P02] Chawla, N.V., Bowyer, K.W., Hall, L.O., & Kegelmeyer, W.P. (2002). SMOTE: Synthetic Minority Over-sampling Technique.
*Journal of Artificial Intelligence Research*, 16, 321–357. DOI: 10.1613/jair.953. **Publisher:** JAIR.

**Research problem:** Class imbalance leads to biased classifiers that ignore minority classes.

**Dataset:** UCI benchmark datasets (binary classification).

**Models:** Various (C4.5, Ripper, Naive Bayes, SVM).

**XAI methods:** None.

**Balancing methods:** SMOTE (k-nearest-neighbour interpolation for minority oversampling).

**Evaluation metrics:** F1; G-mean; ROC AUC.

**Main findings:** SMOTE interpolation between minority-class instances in feature space creates synthetic samples that improve minority-class recall. SMOTE outperforms simple random oversampling (which merely duplicates). Combined SMOTE + undersampling of majority class is effective.

**Limitations:** Validated on binary classification; multiclass NIDS not evaluated; no analysis of how synthetic samples affect model interpretability; can introduce noise by generating samples in unsafe regions of feature space.

**Relation to our work:** Algorithmic foundation of our rebalancing step. We apply SMOTE with k=5 to the 42-feature UNSW-NB15 training set, generating 384,659 synthetic minority-class samples to achieve 56,000 instances per class.

**Possible citation locations:** Methodology (SMOTE description); Introduction; Related Work (SMOTE foundations).

---

### [P03] Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python.
*Journal of Machine Learning Research*, 12, 2825–2830. DOI: 10.5555/1953048.2078195. **Publisher:** JMLR.

**Research problem:** Need for a comprehensive, unified ML library in Python.

**Dataset:** N/A (library paper).

**Main findings:** Scikit-learn provides a consistent API for classification, regression, preprocessing, and evaluation; tightly integrated with NumPy/SciPy.

**Relation to our work:** Used for Random Forest implementation, preprocessing, and evaluation metrics in our pipeline.

**Possible citation locations:** Experimental Setup.

---

### [P04] Moustafa, N., & Slay, J. (2015). UNSW-NB15: A Comprehensive Data Set for Network Intrusion Detection Systems.
*2015 Military Communications and Information Systems Conference (MilCIS)*, Canberra, Nov. 2015, pp. 1–6. DOI: 10.1109/MilCIS.2015.7348942. **Publisher:** IEEE.

**Research problem:** Existing NIDS datasets (KDD99, NSL-KDD) are outdated and lack modern attack types.

**Dataset:** UNSW-NB15 (introduced in this paper).

**Models:** N/A (dataset paper).

**XAI methods:** None.

**Balancing methods:** None.

**Evaluation metrics:** Attack categorisation; feature engineering description.

**Main findings:** UNSW-NB15 contains 2.54M records (175,341 training / 82,332 test) across 10 classes (Normal + 9 attack categories: Analysis, Backdoor, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Shellcode, Worms). Dataset created in a controlled testbed at the University of New South Wales Cyber Range Lab, reflecting modern attack patterns.

**Limitations:** Controlled lab environment (not real production traffic); point-in-time capture (potential concept drift); class imbalance not addressed.

**Relation to our work:** Primary dataset. We use the predefined UNSW-NB15 train/test split throughout. The inherent imbalance (max ratio 430.77:1, Worms vs. Normal) is the central motivation for SMOTE intervention.

**Possible citation locations:** Methodology (Dataset); Introduction (NIDS benchmark motivation); Related Work (UNSW-NB15).

---

### [P05] Ribeiro, M.T., Singh, S., & Guestrin, C. (2016). "Why Should I Trust You?": Explaining the Predictions of Any Classifier.
*KDD 2016*, San Francisco, pp. 1135–1144. DOI: 10.1145/2939672.2939778. **Publisher:** ACM.

**Research problem:** Users cannot trust ML predictions without understanding model reasoning; black-box models are unacceptable in high-stakes settings.

**Dataset:** Text; image; tabular benchmarks.

**Models:** Any (model-agnostic).

**XAI methods:** LIME (introduced).

**Balancing methods:** None.

**Evaluation metrics:** Fidelity (local linear approximation accuracy); human trust (user study); simulation experiment.

**Main findings:** LIME produces locally faithful linear approximations to any classifier's decision boundary by sampling around the instance being explained and fitting a sparse linear model. LIME is model-agnostic, applies to text/image/tabular, and improves human trust in ML predictions in controlled user studies.

**Limitations:** Stochastic sampling introduces instability (different explanations on repeated runs); local linearity assumption fails in highly non-linear regions; computationally expensive for large feature sets.

**Relation to our work:** Algorithmic foundation of our LIME secondary XAI method. The instability noted by Ribeiro et al. is relevant to our finding that LIME shows larger rank shifts than SHAP under SMOTE.

**Possible citation locations:** Methodology (LIME description); Related Work (XAI methods); Introduction.

---

### [P06] Lemaître, G., Nogueira, F., & Aridas, C.K. (2017). Imbalanced-learn: A Python Toolbox to Tackle the Curse of Imbalanced Datasets in Machine Learning.
*JMLR*, 18(17), 1–5. ID: JMLR:v18:16-365. **Publisher:** JMLR.

**Main findings:** imbalanced-learn extends scikit-learn with SMOTE, ADASYN, undersampling, and ensemble methods for imbalanced datasets.

**Relation to our work:** Used for SMOTE implementation in our pipeline.

**Possible citation locations:** Experimental Setup.

---

### [P07] Lundberg, S.M., & Lee, S.-I. (2017). A Unified Approach to Interpreting Model Predictions.
*Advances in Neural Information Processing Systems (NeurIPS)*, 2017, pp. 4766–4777. **Publisher:** Curran Associates.

**Research problem:** Existing explanation methods (LIME, DeepLIFT, RISE) are inconsistent with each other; no unified framework exists.

**Dataset:** Tabular (Census income; NCI60 cancer cell); text; image.

**Models:** Any (model-agnostic); specific TreeSHAP for tree models.

**XAI methods:** SHAP (introduced); subsumes LIME, DeepLIFT, RISE, integrated gradients.

**Balancing methods:** None.

**Evaluation metrics:** Consistency; local accuracy; human agreement; computational efficiency.

**Main findings:** SHAP values, derived from cooperative game theory (Shapley values), satisfy consistency and local accuracy axioms that LIME does not. SHAP provides both local (per-instance) and global (mean |SHAP|) explanations. TreeSHAP computes exact Shapley values for tree models in polynomial time.

**Limitations:** Exact SHAP is expensive for non-tree models; correlated features can produce counter-intuitive attributions; marginalising over training data distribution mixes observational and interventional interpretations.

**Relation to our work:** Primary XAI method. We use shap.TreeExplainer (the efficient tree-specific variant) for both Baseline and SMOTE models. The game-theoretic foundations make SHAP attributions more theoretically grounded than LIME's local linear approximation.

**Possible citation locations:** Methodology (SHAP description); Related Work (XAI methods); Introduction.

---

### [P08] Lundberg, S.M., Erion, G., Chen, H. et al. (2020). From Local Explanations to Global Understanding with Explainable AI for Trees.
*Nature Machine Intelligence*, 2, 56–67. DOI: 10.1038/s42256-019-0138-9. **Publisher:** Nature.

**Research problem:** Bridging local SHAP explanations and global model understanding for tree ensembles.

**Dataset:** Clinical (sepsis ICU); Census income; NHANES II.

**Models:** Random Forest; XGBoost; LightGBM.

**XAI methods:** SHAP (TreeExplainer).

**Balancing methods:** None.

**Evaluation metrics:** Consistency; fidelity; feature interaction detection.

**Main findings:** TreeExplainer computes exact SHAP values for tree ensembles in O(T L D²) time (T = trees, L = leaves, D = depth). Global feature importance from TreeSHAP is more reliable than Gini impurity. Local explanations can be combined into global dependence plots, interaction effects, and hierarchical clustering of explanations.

**Limitations:** Specific to tree-based models; SHAP values depend on feature correlation structure which can distort attributions for correlated features.

**Relation to our work:** Direct algorithmic basis for our shap.TreeExplainer usage. The ability to go from local to global explanations underpins our global ranking comparison (mean |SHAP| across 60 instances).

**Possible citation locations:** Methodology (SHAP description); Related Work (XAI methods).

---

## Section 2 — Network Intrusion Detection (2021–2025)

---

### [P10] Alshamy, R., Ghurab, M., Othman, S., & Alshami, F. (2021). Intrusion Detection Model for Imbalanced Dataset Using SMOTE and Random Forest Algorithm.
*Advances in Cyber Security (ACeS 2021)*, Communications in Computer and Information Science, vol. 1487, Springer, pp. 311–323. DOI: 10.1007/978-981-16-8059-5_22. **Publisher:** Springer.

**Research problem:** Multi-class NIDS on imbalanced datasets.

**Dataset:** NSL-KDD.

**Models:** Random Forest; Logistic Regression; SVM; AdaBoost.

**XAI methods:** None.

**Balancing methods:** SMOTE.

**Evaluation metrics:** Accuracy; precision; recall; F1; computation time.

**Main findings:** IDS-SMOTE-RF achieves high accuracy on NSL-KDD, outperforming LR/SVM/AdaBoost for multi-class classification. SMOTE effectively addresses class imbalance in NIDS. RF is the strongest base classifier in this comparison.

**Limitations:** NSL-KDD dataset (older, binary-centric); no XAI; no explanation stability analysis; no UNSW-NB15.

**Gap addressed:** SMOTE + RF for NIDS is validated — but the effect on model explanations is untouched.

**Relation to our work:** Directly supports our SMOTE + RF methodology choice, but on a different dataset and without XAI analysis. Demonstrates the gap: SMOTE+RF IDS is well-studied; explanation effects are not.

**Possible citation locations:** Related Work — SMOTE + NIDS; Methodology (justification of RF).

---

### [P13] Wu, T., Fan, H., Zhu, H., You, C., Zhou, H., & Huang, X. (2022). Intrusion Detection System Combined Enhanced Random Forest with SMOTE Algorithm.
*EURASIP Journal on Advances in Signal Processing*, 2022, Art. 39. DOI: 10.1186/s13634-022-00871-6. **Publisher:** Springer (open access).

**Research problem:** High class imbalance in NSL-KDD reduces minority-class detection in RF-based IDS.

**Dataset:** NSL-KDD.

**Models:** Random Forest (enhanced with K-means clustering).

**XAI methods:** None.

**Balancing methods:** K-means SMOTE (cluster before oversampling).

**Evaluation metrics:** Accuracy (99.72% training; 78.47% test); precision; recall; F1.

**Main findings:** K-means SMOTE + enhanced RF improves minority-class recall. Large gap between training and test accuracy (99.72% vs 78.47%) suggests overfitting on synthetic samples.

**Limitations:** Large train/test gap; no XAI; no UNSW-NB15; potential overfitting on synthetic data.

**Gap addressed:** Does not measure how SMOTE changes the model's explanation output.

**Relation to our work:** Supports SMOTE + RF methodology; the overfitting risk motivates careful evaluation of SMOTE's effect on both predictive and explanatory outputs in our study.

**Possible citation locations:** Related Work — SMOTE + NIDS.

---

### [P16] More, S., Idrissi, M., Mahmoud, H., & Asyhari, A.T. (2024). Enhanced Intrusion Detection Systems Performance with UNSW-NB15 Data Analysis.
*Algorithms*, 17(2), Art. 64. DOI: 10.3390/a17020064. **Publisher:** MDPI.

**Research problem:** Comparative ML evaluation on the UNSW-NB15 dataset.

**Dataset:** UNSW-NB15.

**Models:** Logistic Regression; SVM; Decision Tree; Random Forest.

**XAI methods:** None (basic feature importance mentioned).

**Balancing methods:** None.

**Evaluation metrics:** Accuracy (98.63%); F1 (97.80%); False Alarm Rate (1.36%).

**Main findings:** Random Forest achieves best F1 (97.80%) and accuracy (98.63%) among all tested models on UNSW-NB15. Feature correlation analysis identifies key predictive features.

**Limitations:** No class imbalance treatment; no minority-class-specific analysis; no XAI; no statistical testing.

**Gap addressed:** Establishes RF as dominant baseline on UNSW-NB15 — but does not investigate class imbalance or explainability.

**Relation to our work:** Directly validates our model choice. Our Baseline RF accuracy (75.43%) is lower because we evaluate on a 10-class multi-class setting with the full test set including severely underrepresented minority attack types; More et al. may have used different preprocessing.

**Possible citation locations:** Related Work — UNSW-NB15 studies; Methodology (model choice justification).

---

### [P18] Sayegh, H.R., Dong, W., & Al-madani, A.M. (2024). Enhanced Intrusion Detection with LSTM-Based Model, Feature Selection, and SMOTE for Imbalanced Data.
*Applied Sciences*, 14(2), Art. 479. DOI: 10.3390/app14020479. **Publisher:** MDPI.

**Research problem:** IoT NIDS with severe class imbalance; rare attack-type detection.

**Dataset:** IoT NIDS dataset.

**Models:** LSTM.

**XAI methods:** None.

**Balancing methods:** SMOTE.

**Evaluation metrics:** Accuracy; precision; recall; F1.

**Main findings:** SMOTE + LSTM improves rare-class detection; SMOTE-ENN (SMOTE + edited nearest neighbour) further reduces noise introduced by pure SMOTE.

**Limitations:** No XAI; no UNSW-NB15; no explanation analysis.

**Gap addressed:** SMOTE improves NIDS performance — but no one has measured how it affects SHAP/LIME explanations.

**Relation to our work:** Confirms SMOTE utility in NIDS context with a recent study; the absence of XAI analysis in SMOTE-based NIDS studies is a central motivation for our work.

**Possible citation locations:** Related Work — SMOTE + NIDS; Introduction.

---

### [P19] Shanmugam, V., Razavi-Far, R., & Hallaji, E. (2025). Addressing Class Imbalance in Intrusion Detection: A Comprehensive Evaluation of Machine Learning Approaches.
*Electronics*, 14(1), Art. 69. DOI: 10.3390/electronics14010069. **Publisher:** MDPI.

**Research problem:** Systematic evaluation of resampling strategies across multiple imbalance levels for NIDS.

**Dataset:** NSL-KDD; CIC-IDS.

**Models:** Random Forest; SVM; KNN; Naive Bayes; and others.

**XAI methods:** None.

**Balancing methods:** SMOTE; ADASYN; Random Oversampling (ROS); Random Undersampling (RUS); cost-sensitive learning.

**Evaluation metrics:** F1; G-mean.

**Main findings:** Resampling strategies vary in effectiveness depending on the degree of imbalance; RF with SMOTE performs consistently across imbalance levels; ADASYN is competitive but less stable; RUS degrades F1 at high imbalance levels.

**Limitations:** No XAI; no UNSW-NB15; no feature attribution analysis.

**Gap addressed:** Comprehensive predictive evaluation of resampling — but no one has measured the downstream explanation effect.

**Relation to our work:** Provides the strongest recent empirical support for SMOTE+RF as the appropriate methodology; motivates why our study focuses on the explanation effect rather than the predictive effect (already well-studied).

**Possible citation locations:** Related Work — Class Imbalance + NIDS; Introduction; Future Work (ADASYN comparison).

---

## Section 3 — XAI Applied to Cybersecurity / NIDS (2022–2025)

---

### [P12] Charmet, F. et al. (2022). Explainable Artificial Intelligence for Cybersecurity: A Literature Survey.
*Annals of Telecommunications*, 77(11–12), 789–812. DOI: 10.1007/s12243-022-00926-7. **Publisher:** Springer.

**Research problem:** Survey of XAI methods applied to cybersecurity tasks including NIDS, malware detection, and intrusion response.

**Dataset:** Survey (multiple).

**Models:** Survey (many including RF, DNN, LSTM).

**XAI methods:** SHAP; LIME; Anchors; DeepLIFT; Integrated Gradients; counterfactuals.

**Balancing methods:** Survey mentions class imbalance as a challenge but does not evaluate balancing methods.

**Evaluation metrics:** Coverage; citation analysis; XAI taxonomy.

**Main findings:** SHAP and LIME are the dominant post-hoc explanation methods for NIDS. Explanation evaluation (fidelity, robustness, stability) remains an open challenge. XAI improves analyst trust but its robustness under distribution shift is not well studied. 

**Limitations:** Survey — no empirical comparison; no quantitative stability evaluation; class imbalance impact on XAI is identified as a gap but not addressed.

**Gap addressed:** Identifies XAI reliability under distribution shift as an open problem — directly motivating our study.

**Relation to our work:** This survey is our primary contextualisation source. Its identification of "XAI evaluation under distribution change" as an open problem provides strong motivation for our research question.

**Possible citation locations:** Introduction; Related Work — XAI Cybersecurity; Discussion (trustworthy AI).

---

### [P15] Rjoub, G. et al. (2023). A Survey on Explainable Artificial Intelligence for Cybersecurity.
*IEEE Transactions on Network and Service Management*, 20(4), 5115–5140. DOI: 10.1109/TNSM.2023.3282740. **Publisher:** IEEE.

**Research problem:** Systematic survey of XAI methods and evaluation frameworks for cybersecurity applications.

**Dataset:** Survey.

**Models:** Survey.

**XAI methods:** SHAP; LIME; Anchors; counterfactuals; and others.

**Balancing methods:** Survey.

**Evaluation metrics:** Coverage; robustness; fidelity; trust.

**Main findings:** XAI methods broadly improve NIDS transparency; SHAP and LIME dominate; explanation evaluation metrics are under-standardised; explanation stability under training data changes is specifically identified as under-studied.

**Limitations:** Survey — no empirical evaluation.

**Gap addressed:** Strongest single source for our motivation. Explicitly identifies "explanation quality under data distribution change" as an open problem.

**Relation to our work:** Cited to establish the broader survey context of XAI for cybersecurity; cited in motivation for our specific research question.

**Possible citation locations:** Introduction; Related Work — XAI Cybersecurity survey; Discussion.

---

### [P17] Gaspar, D., Silva, P., & Silva, C. (2024). Explainable AI for Intrusion Detection Systems: LIME and SHAP Applicability on Multi-Layer Perceptron.
*IEEE Access*, 12, 30164–30175. DOI: 10.1109/ACCESS.2024.3368377. **Publisher:** IEEE.

**Research problem:** Applying LIME and SHAP to explain MLP-based IDS for IoT.

**Dataset:** IoT traffic (specific dataset unverified — access full text at DOI 10.1109/ACCESS.2024.3368377 to confirm).

**Models:** MLP (Multi-Layer Perceptron).

**XAI methods:** LIME; SHAP.

**Balancing methods:** None.

**Evaluation metrics:** Fidelity; local accuracy; interpretability; IoT detection rate.

**Main findings:** LIME provides visually intuitive local explanations for security analysts; SHAP provides theoretically grounded global feature rankings. Both improve IDS transparency. The two methods are complementary — LIME for local decision-making, SHAP for global audit.

**Limitations:** No class imbalance treatment; no SMOTE; MLP only (not RF); no measurement of explanation stability under distribution change; no statistical tests on explanations.

**Gap addressed:** SHAP+LIME on NIDS is proven effective — but effects of rebalancing on these explanations are not studied.

**Relation to our work:** Most direct prior application of LIME+SHAP to an IDS context. Confirms that our XAI tool choices are well-established. Our study extends this work by asking: what happens to these explanations when the training data distribution changes?

**Possible citation locations:** Related Work — XAI + NIDS; Methodology (XAI method justification).

---

### [P20] Hermosilla, P., Berríos, S., & Allende-Cid, H. (2025). Explainable AI for Forensic Analysis: A Comparative Study of SHAP and LIME in Intrusion Detection Models.
*Applied Sciences*, 15(13), Art. 7329. DOI: 10.3390/app15137329. **Publisher:** MDPI.

**Research problem:** Comparative evaluation of SHAP and LIME for forensic analysis in IDS using UNSW-NB15.

**Dataset:** UNSW-NB15.

**Models:** XGBoost; TabNet.

**XAI methods:** SHAP; LIME.

**Balancing methods:** None.

**Evaluation metrics:** Accuracy (XGBoost 97.8%); fidelity; explanation consistency; forensic relevance.

**Main findings:** XGBoost outperforms TabNet in explanation stability and global coherence. SHAP produces globally coherent rankings; LIME is more locally variable. Combined SHAP+LIME deployment recommended for cybersecurity audit. UNSW-NB15 has inherent class imbalance noted as a limitation.

**Limitations:** No class imbalance correction; no SMOTE; no RF model; no paired statistical tests on explanation vectors; no Wilcoxon or McNemar tests; no effect-size analysis.

**Gap addressed:** SHAP+LIME on UNSW-NB15 validated — but the impact of class rebalancing on these explanations is not investigated.

**Relation to our work:** Closest single prior paper to our study in terms of: (a) UNSW-NB15, (b) SHAP and LIME, (c) explanation comparison. The key gap: they do not apply SMOTE or any balancing, do not compare explanations between balanced/imbalanced models, and do not apply statistical tests to explanation vectors. Our work fills exactly this gap.

**Possible citation locations:** Related Work — XAI + NIDS; Discussion; Gap motivation.

---

### [P21] Hermosilla, P., Díaz, M., Berríos, S., & Allende-Cid, H. (2025). Use of Explainable Artificial Intelligence for Analyzing and Explaining Intrusion Detection Systems.
*Computers*, 14(5), Art. 160. DOI: 10.3390/computers14050160. **Publisher:** MDPI.

**Research problem:** XAI framework evaluation for IDS explanation quality on UNSW-NB15.

**Dataset:** UNSW-NB15.

**Models:** XGBoost; TabNet.

**XAI methods:** SHAP; LIME.

**Balancing methods:** None.

**Evaluation metrics:** Accuracy; explanation consistency; fidelity.

**Main findings:** SHAP is more globally coherent; LIME is more locally variable. XAI methods improve analyst understanding. UNSW-NB15 class imbalance is noted as a limitation not addressed.

**Limitations:** No balancing; no statistical hypothesis testing; no effect sizes.

**Gap addressed:** Same as P20 — companion paper from the same team, reinforcing that the rebalancing gap exists and is unaddressed.

**Relation to our work:** Companion work to P20. Collectively, P20 and P21 represent the state of the art in SHAP+LIME on UNSW-NB15 — and our study directly addresses the imbalance gap they leave open.

**Possible citation locations:** Related Work — XAI + NIDS.

---

## Section 4 — SMOTE Effects on Explainability (2020–2022)

---

### [P09] Patil, A., Framewala, A., & Kazi, F. (2020). Explainability of SMOTE Based Oversampling for Imbalanced Dataset Problems.
*IEEE ICICT 2020*, San Jose, CA, pp. 41–45. DOI: 10.1109/ICICT50521.2020.9092325 [verify before submission]. **Publisher:** IEEE.

**Research problem:** Does SMOTE-based oversampling produce interpretable models? Do explanations change post-SMOTE?

**Dataset:** Generic imbalanced tabular datasets (UCI).

**Models:** Decision Tree; SVM.

**XAI methods:** LIME; basic feature importance.

**Balancing methods:** SMOTE.

**Evaluation metrics:** Accuracy; per-class metrics; LIME explanation comparison.

**Main findings:** SMOTE oversampling shifts decision boundaries; LIME explanations show different feature importances before and after SMOTE. Feature importance can change substantially post-balancing. Interpretable models may behave differently after oversampling.

**Limitations:** No NIDS context; no UNSW-NB15; no SHAP; no formal statistical tests; no effect-size analysis; no paired comparison framework; single dataset type; qualitative comparison only.

**Gap addressed:** Shows that SMOTE changes explanations — but does not quantify by how much, does not use SHAP, does not operate in NIDS, and does not compare SHAP vs LIME sensitivity.

**Relation to our work:** Closest prior work to our study in terms of the SMOTE + explainability research question. We extend it to: (a) NIDS domain, (b) UNSW-NB15, (c) SHAP + LIME, (d) formal paired statistical tests, (e) effect-size analysis.

**Possible citation locations:** Related Work — SMOTE + Explainability; Introduction (gap motivation).

---

### [P14] Alarab, I., & Prakoonwit, S. (2022). Effect of Data Resampling on Feature Importance in Imbalanced Blockchain Data.
*Data Science and Management*, 5(2), 66–76. DOI: 10.1016/j.dsm.2022.04.003. **Publisher:** Elsevier.

**Research problem:** How do resampling techniques (SMOTE, ADASYN, ROS, RUS) change feature importance rankings in imbalanced classification?

**Dataset:** Elliptic (Bitcoin blockchain transactions).

**Models:** Random Forest; XGBoost.

**XAI methods:** Gini feature importance; permutation importance.

**Balancing methods:** SMOTE; ADASYN; Random Oversampling; Random Undersampling.

**Evaluation metrics:** Feature ranking overlap (top-k); accuracy; AUC.

**Main findings:** Resampling techniques change feature importance rankings; SMOTE produces the largest rank shifts in this domain; different resampling strategies produce different explanation profiles; the direction of change depends on which features are enriched by synthetic samples.

**Limitations:** Blockchain domain only (not NIDS); no SHAP/LIME (Gini and permutation importance only); no formal statistical tests (Wilcoxon, McNemar); no effect-size analysis; no confidence intervals; single domain.

**Gap addressed:** Shows resampling changes feature rankings — but does not use post-hoc XAI methods, does not use NIDS data, and does not quantify statistical significance or practical effect sizes.

**Relation to our work:** Second-closest prior work. Directly motivates our study by showing feature ranking shifts under SMOTE exist in a different domain. We extend to: (a) NIDS/UNSW-NB15, (b) SHAP and LIME post-hoc XAI, (c) Wilcoxon signed-rank tests, (d) rank-biserial effect sizes.

**Possible citation locations:** Related Work — SMOTE + Explainability; Introduction (gap motivation).

---

## Section 5 — XAI Stability and Evaluation (2022–2025)

---

### [P11] Visani, G., Bagli, E., Chesani, F., Poluzzi, A., & Capuzzo, D. (2022). Statistical Stability Indices for LIME: Obtaining Reliable Explanations for Machine Learning Models.
*Journal of the Operational Research Society*, 73(1), 91–101. DOI: 10.1080/01605682.2020.1865846. **Publisher:** Taylor & Francis.

**Research problem:** LIME explanations vary stochastically across repeated runs; there is no standard way to quantify this instability.

**Dataset:** Credit risk (tabular, proprietary).

**Models:** Logistic Regression; Random Forest (as explainee).

**XAI methods:** LIME.

**Balancing methods:** None.

**Evaluation metrics:** CSI (Coefficients Stability Index); VSI (Variables Stability Index).

**Main findings:** LIME explanations for the same instance differ substantially across runs due to random perturbation sampling. CSI measures variability of coefficient magnitudes; VSI measures variability of which features are selected. Both indices allow practitioners to report LIME reliability alongside explanations.

**Limitations:** Evaluated only on credit risk; not cybersecurity/NIDS; no comparison with SHAP; no SMOTE; stability under model change (retraining) not addressed.

**Gap addressed:** LIME run-to-run instability is quantified — but instability caused by training distribution change (SMOTE) is not studied.

**Relation to our work:** Provides the theoretical and methodological context for our stability measurement. Our Spearman rank correlation and top-5 overlap metrics are philosophically aligned with CSI/VSI but applied to measure model-to-model stability rather than within-model run-to-run variation.

**Possible citation locations:** Related Work — XAI Stability; Discussion (stability metrics).

---

## Section 6 — Tooling and Methodology Foundations

---

### Summary of Tooling Papers

| Paper | Tool | Used in Our Study For |
|-------|------|----------------------|
| P01 (Breiman 2001) | Random Forest algorithm | Classifier (both conditions) |
| P02 (Chawla 2002) | SMOTE algorithm | Training data rebalancing |
| P03 (Pedregosa 2011) | scikit-learn | RF; preprocessing; evaluation |
| P05 (Ribeiro 2016) | LIME | Secondary XAI explanation |
| P06 (Lemaître 2017) | imbalanced-learn | SMOTE implementation |
| P07 (Lundberg 2017) | SHAP | Primary XAI explanation |
| P08 (Lundberg 2020) | TreeSHAP | Efficient tree SHAP computation |

---

## Section 7 — Paper Summary by Theme

### Theme 1: Network Intrusion Detection
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P04 (Moustafa 2015) | UNSW-NB15 dataset | No ML/XAI |
| P10 (Alshamy 2021) | SMOTE+RF for IDS on NSL-KDD | No XAI; no UNSW-NB15 |
| P13 (Wu 2022) | K-means SMOTE + enhanced RF IDS | No XAI; NSL-KDD only |
| P16 (More 2024) | RF best model on UNSW-NB15 | No imbalance; no XAI |
| P18 (Al-madani 2024) | LSTM + SMOTE for IoT NIDS | No XAI; no UNSW-NB15 |
| P19 (Razavi-Far 2025) | Comprehensive imbalance evaluation | No XAI |

### Theme 2: UNSW-NB15
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P04 (Moustafa 2015) | Dataset creation | No ML |
| P16 (More 2024) | RF dominates on UNSW-NB15 | No imbalance/XAI |
| P20 (Hermosilla 2025a) | SHAP+LIME on UNSW-NB15 | No SMOTE |
| P21 (Hermosilla 2025b) | XAI framework on UNSW-NB15 | No SMOTE; no statistics |

### Theme 3: Class Imbalance
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P02 (Chawla 2002) | SMOTE algorithm | No XAI |
| P06 (Lemaître 2017) | imbalanced-learn library | Library only |
| P10 (Alshamy 2021) | SMOTE+RF for NSL-KDD | No XAI |
| P13 (Wu 2022) | K-means SMOTE+RF | No XAI; overfitting |
| P18 (Al-madani 2024) | SMOTE+LSTM | No XAI |
| P19 (Razavi-Far 2025) | Imbalance evaluation | No XAI |

### Theme 4: SMOTE
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P02 (Chawla 2002) | Algorithm | No XAI; binary only |
| P09 (Patil 2020) | SMOTE + explainability (qualitative) | No NIDS; no SHAP; no statistics |
| P14 (Alarab 2022) | SMOTE + feature importance (blockchain) | No NIDS; no SHAP/LIME |

### Theme 5: Explainable AI
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P05 (Ribeiro 2016) | LIME method | No NIDS; no imbalance |
| P07 (Lundberg 2017) | SHAP method | No NIDS; no imbalance |
| P08 (Lundberg 2020) | TreeSHAP | No NIDS; no imbalance |
| P11 (Visani 2022) | LIME run-to-run stability | No NIDS; no SMOTE |

### Theme 6: SHAP in NIDS
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P17 (Gaspar 2024) | LIME+SHAP on MLP-IDS | No RF; no SMOTE |
| P20 (Hermosilla 2025a) | SHAP+LIME on UNSW-NB15 | No SMOTE; no statistics |
| P21 (Hermosilla 2025b) | XAI for IDS analysis | No SMOTE; no statistics |

### Theme 7: Cybersecurity Explainability (Surveys)
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P12 (Charmet 2022) | XAI cybersecurity survey | Identifies our gap |
| P15 (Rjoub 2023) | XAI cybersecurity survey | Identifies our gap |

### Theme 8: Explainability Evaluation
| Paper | Key Contribution | Gap |
|-------|----------------|-----|
| P11 (Visani 2022) | LIME stability indices (CSI/VSI) | No SMOTE; no NIDS |
| P14 (Alarab 2022) | Resampling + feature rank stability | No NIDS; no SHAP/LIME |

---

## Section 8 — Coverage Summary

| Theme | Papers Found | Coverage Quality |
|-------|-------------|-----------------|
| Network Intrusion Detection | P04; P10; P13; P16; P18; P19 | Comprehensive |
| UNSW-NB15 | P04; P16; P20; P21 | Good |
| Class Imbalance | P02; P06; P10; P13; P18; P19 | Comprehensive |
| SMOTE | P02; P09; P13; P14; P18 | Good |
| Explainable AI (foundations) | P05; P07; P08; P11 | Comprehensive |
| SHAP for NIDS | P07; P08; P17; P20; P21 | Good |
| LIME for NIDS | P05; P17; P20; P21 | Good |
| Random Forest + NIDS | P01; P10; P13; P16 | Good |
| Cybersecurity Explainability | P12; P15; P17; P20; P21 | Comprehensive |
| Explainability Evaluation | P11; P14 | Moderate (expand in Scopus search) |
| SMOTE + Explainability interaction | P09; P14 | Thin (only 2 papers — confirms novelty) |

---

## Section 9 — Recommended Papers by Manuscript Section

### Introduction (cite to establish motivation)
**Priority:** P04; P07; P08; P05; P02; P12; P15; P17

### Related Work — NIDS background
**Priority:** P04; P16; P10; P13; P18; P19

### Related Work — SMOTE
**Priority:** P02; P10; P13; P18; P19

### Related Work — XAI Methods
**Priority:** P05; P07; P08; P11

### Related Work — XAI for NIDS
**Priority:** P12; P15; P17; P20; P21

### Related Work — SMOTE + Explainability (gap papers)
**Priority:** P09; P14

### Methodology
**Essential:** P01; P02; P03; P04; P05; P06; P07; P08

### Experimental Setup
**Essential:** P03; P06

### Discussion
**Priority:** P12; P15; P11; P14; P09

### Limitations
**Supporting:** P19; P01; P04

### Future Work
**Supporting:** P19; P08

---

## Section 10 — Novelty Assessment Summary

**Verdict: Moderately to Strongly Novel**

The combination of elements present in our study — (1) UNSW-NB15 multiclass NIDS, (2) SMOTE rebalancing, (3) SHAP + LIME dual XAI, (4) paired statistical validation with Holm correction and effect sizes, (5) direct comparison of predictive vs explanatory sensitivity — is not present in any single prior paper in this review.

The specific finding that explanation effect sizes (LIME rank-biserial r=0.595) exceed predictive effect sizes (max Cohen's h=0.087) by a factor of ~6.8× is a new empirical result.

Two XAI cybersecurity surveys (P12, P15) explicitly identify the type of analysis we perform as an open research problem, providing strong external validation of the contribution's relevance.

**Recommended novelty claim framing:**
> *"To our knowledge, no prior study has systematically compared SHAP and LIME explanation stability before and after SMOTE rebalancing in a multiclass RF-based NIDS setting using paired statistical tests and effect-size measures."*

**Avoid:**
- "first paper ever to study XAI in NIDS" — incorrect (P17, P20, P21 predate this)
- "first to apply SMOTE to NIDS" — incorrect (P10, P13, P18 predate this)
- "first to study explanation stability" — incorrect (P11 studies LIME stability; P14 studies resampling + feature importance)

---

*Do NOT write the Related Work section yet. Await approval.*
