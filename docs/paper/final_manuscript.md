<!-- IEEE CONFERENCE MANUSCRIPT — TEMSMET 2026
     Final integrated version — all citations resolved, editorial pass complete.
     Generated: 2026-07-09 | Source: manuscript.md + reference_integration task
     All [CITATION REQUIRED] placeholders replaced. RC-01 through RC-14 applied.
     Do NOT modify numerical results — they are sourced from pipeline outputs.
-->

# Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection

**Authors:** [AUTHOR NAMES — DO NOT PUBLISH WITH PLACEHOLDER]

**Affiliation:** [INSTITUTION — DO NOT PUBLISH WITH PLACEHOLDER]

**Target venue:** IEEE TEMSMET 2026 (International Conference on Technology and Engineering Management)

**Submission type:** Regular paper (6–8 pages, double-column IEEE format)

---

## Abstract

Machine learning-based Network Intrusion Detection Systems (NIDS) routinely apply
the Synthetic Minority Over-sampling Technique (SMOTE) to address severe
traffic-class imbalance, yet the impact of such rebalancing on post-hoc
explainability outputs has not been systematically quantified in the NIDS
literature. This study investigates how SMOTE rebalancing affects the feature
attribution rankings produced by SHapley Additive exPlanations (SHAP) and Local
Interpretable Model-agnostic Explanations (LIME) in a Random Forest NIDS trained
and evaluated on the UNSW-NB15 benchmark dataset. Two Random Forest classifiers
— one trained on the original imbalanced partition and one on a SMOTE-rebalanced
partition — are evaluated against the same 82,332-instance test set. SHAP
TreeExplainer and LIME LimeTabularExplainer generate global and local attributions
for both models, and a statistical framework comprising McNemar's test, Wilcoxon
signed-rank tests, bootstrap confidence intervals, and Holm–Bonferroni
multiple-comparison correction quantifies statistical significance and practical
effect size for both predictive and explanatory changes simultaneously. SMOTE
improves macro-averaged F1 and substantially increases minority-class recall,
with all aggregate predictive effect sizes remaining negligible (Cohen's h ≤ 0.09).
In contrast, SHAP feature attribution rankings shift with a medium practical effect
(rank-biserial r = 0.33) and LIME rankings with a large effect (r = 0.60) — the
LIME effect approximately 6.8 times the magnitude of the largest predictive effect.
These results demonstrate that class rebalancing changes feature attribution outputs
disproportionately relative to classification metrics, providing evidence that
accuracy-only validation after NIDS retraining is insufficient to characterise the
stability of explainability outputs. Evaluating explanation consistency alongside
predictive performance is therefore a necessary component of responsible model
assessment in any NIDS pipeline that incorporates post-hoc explainability methods.

**Index Terms:** network intrusion detection, explainability, class imbalance,
synthetic minority oversampling, Shapley additive explanations, local interpretable
model-agnostic explanations, random forest, feature attribution

---

## I. Introduction

Machine learning–based Network Intrusion Detection Systems have demonstrated strong
performance on curated benchmark datasets [10, 13, 16]. A persistent
practical challenge, however, is severe class imbalance: in real-world network
traffic and standard NIDS benchmarks, benign traffic dominates by orders of
magnitude, while rare attack categories may constitute fewer than 0.1% of all
packets [4, 19]. This distributional asymmetry biases standard
classifiers toward majority-class predictions and suppresses detection of rare,
high-severity attack types.

Synthetic Minority Over-sampling Technique (SMOTE) [2] is among
the most widely adopted remediation strategies, generating synthetic minority-class
instances by interpolating between existing minority samples in feature space.
SMOTE has been shown to improve minority-class recall in NIDS applications
[10, 18]; in this study, it increased Worms-class F1 from 0.233
to 0.452.

Concurrently, the adoption of eXplainable AI (XAI) methods in security operations
has grown substantially [12, 15]. SHAP (SHapley Additive exPlanations)
[7, 8] and LIME (Local Interpretable Model-agnostic Explanations)
[5, 17, 20] are the two most widely applied post-hoc explanation methods
for NIDS models, enabling analysts to understand which network features drive
individual classification decisions.

A critical and underexplored question is: *when a NIDS model is retrained with a
different class distribution, does the explanation change as much as the prediction?*
If explanation instability is disproportionate to predictive instability, operators
relying on accuracy metrics alone to validate retrained models may unknowingly
deploy models whose explanation outputs have changed substantially, undermining the
trustworthiness of XAI-assisted security analysis.

This paper addresses that gap with a controlled empirical study. The specific
contributions are:

1. A paired statistical comparison (McNemar's test, Wilcoxon signed-rank, 95%
   bootstrap CIs) of Baseline and SMOTE-trained Random Forest NIDS models on the
   UNSW-NB15 dataset (82,332 test instances).
2. Quantified effect sizes for both predictive metrics (Cohen's h) and XAI
   explanation stability (rank-biserial r for Wilcoxon tests on SHAP and LIME
   feature importances).
3. A systematic comparison of SHAP and LIME sensitivity to training class
   distribution, showing LIME to be substantially more sensitive than SHAP.
4. Actionable guidance for practitioners on explanation-consistency monitoring
   in XAI-augmented NIDS pipelines.

The remainder of this paper is structured as follows. Section II reviews related
work. Section III describes the methodology. Section IV details the experimental
setup. Section V presents results. Sections VI–VIII discuss findings, limitations,
and future directions. Section IX concludes.

---

## II. Related Work

### A. Class Imbalance in NIDS

Class imbalance is a well-documented challenge in network intrusion detection
[4, 19]. Minority attack categories (e.g., zero-day exploits, worm
propagation) are infrequent relative to normal traffic, causing standard classifiers
to achieve high accuracy by predicting the majority class [2, 10].
Re-sampling strategies — including SMOTE [2], ADASYN [19],
and random undersampling [19] — as well as cost-sensitive learning
[19] and ensemble methods [19] have been proposed to
address this imbalance. SMOTE remains a dominant approach in NIDS literature due to
its simplicity, reproducibility, and consistent minority-class recall improvements
[13, 18].

### B. Explainable AI for Network Security

The application of XAI methods to NIDS has expanded considerably alongside the
broader trustworthy-AI movement [12, 15]. SHAP, grounded in cooperative
game theory, provides feature attributions with theoretical guarantees of
consistency and local accuracy [7, 8]. LIME approximates model
behaviour locally with an interpretable surrogate, offering instance-level
explanations without structural knowledge of the underlying model [5].
Both methods have been applied to Random Forest–based NIDS [20, 21] as
well as deep-learning NIDS [17].

### C. XAI Stability and Explanation Quality

The stability of XAI explanations under perturbation has been studied in general
machine learning contexts [11] but remains underexplored in NIDS
settings. Existing work has examined the impact of adversarial perturbations on
LIME and SHAP outputs [12] and the sensitivity of explanations to
hyperparameter choices [11]. The specific question of how training
data rebalancing affects explanation stability — distinct from prediction stability
— has not been addressed in prior NIDS literature to our knowledge [9, 14].

### D. UNSW-NB15 Benchmark

UNSW-NB15 [4] is a widely used NIDS benchmark created at the
University of New South Wales Cyber Range Lab. It contains modern attack categories
generated in a controlled testbed environment and has been adopted as a standard
evaluation benchmark in numerous NIDS studies [16, 20]. Its predefined
training/test split provides a reproducible evaluation protocol.

---

## III. Methodology

### A. Dataset

The UNSW-NB15 dataset [4] provides a predefined training set
(175,341 instances) and test set (82,332 instances) across 10 classes: Normal,
Analysis, Backdoor, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Shellcode,
and Worms. The training set exhibits severe class imbalance: the Normal class
contains 56,000 samples (31.9% of training), whereas Worms contains only 130
samples (0.074%), yielding a maximum imbalance ratio of 430.77:1 [Fig. 1, Fig. 2].

### B. Feature Engineering and Preprocessing

The original 44-feature schema was reduced to 42 features by removing `id`
(instance identifier, no discriminative value) and `label` (binary attack indicator,
target leakage). Numerical features were retained without additional transformation;
categorical features were encoded. No feature scaling was applied, as Random Forest
is scale-invariant.

### C. Class Rebalancing (SMOTE)

SMOTE [2] was applied to the 42-feature training set with
`sampling_strategy='auto'` and `k_neighbors=5`, using global random seed 42.
Minority classes were oversampled to match the majority-class size (56,000 samples
per class), producing a balanced training set of 560,000 rows (10 classes × 56,000
each). A total of 384,659 synthetic samples were generated. The test set was not
modified; both models are evaluated on the same 82,332-row held-out set.

### D. Classifier

A Random Forest [1] classifier was trained independently on the original imbalanced
dataset (Baseline) and on the SMOTE-balanced dataset (SMOTE model). All
hyperparameters and the global random seed (42) were held constant between
conditions. The original UNSW-NB15 train/test split was used without re-splitting.

### E. XAI Methods

**SHAP (TreeExplainer):** SHAP values [7, 8] were computed for 60
test instances using `shap.TreeExplainer`, which exploits the tree structure of
Random Forest to compute exact Shapley values in polynomial time. Global feature
importance was obtained by averaging |SHAP| values across instances. Feature
rankings were compared between Baseline and SMOTE models using Spearman rank
correlation and top-5 overlap.

**LIME (LimeTabularExplainer):** LIME explanations [5] were
computed for the same 60 instances. Local linear models approximated each
prediction in a neighbourhood defined by sampling with feature perturbation.
Global importance was derived by aggregating absolute LIME weights across instances.

### F. Statistical Validation

Four hypothesis tests were conducted (Table IV):

1. **McNemar's test** (Yates continuity correction) on the 82,332-sample paired
   prediction matrix to assess whether the two models disagree at a significant
   rate. Discordant pairs: b=1632 (SMOTE gains), c=4784 (SMOTE loses).

2. **Wilcoxon signed-rank test** on paired confidence scores (82,332 pairs,
   normal approximation) to assess whether predicted class probabilities shifted.

3. **Wilcoxon signed-rank test** on paired SHAP global feature importances
   (42 feature pairs) to assess explanation magnitude shift.

4. **Wilcoxon signed-rank test** on paired LIME global feature importances
   (36 feature pairs) to assess explanation magnitude shift.

Holm–Bonferroni correction was applied across all four tests. Effect sizes are
reported as Cohen's h for proportion comparisons and rank-biserial r for Wilcoxon
tests. Bootstrap confidence intervals (95%, 2,000 iterations, percentile method)
were computed on the full 82,332-sample test set.

---

## IV. Experimental Setup

All experiments were implemented in Python 3.10+. Key libraries include scikit-learn
[3] for the Random Forest classifier and evaluation metrics,
imbalanced-learn [6] for SMOTE, shap [7] for SHAP
explanations, lime [5] for LIME explanations, scipy [22]
for statistical tests, and numpy/pandas for numerical computation. The global random
seed was set to 42 for all stochastic operations (`random`, `numpy`, scikit-learn).

SHAP and LIME explanations were computed on a stratified random sample of 60 test
instances (6 per class) to manage computation time while maintaining class coverage.
Global feature importances were derived by averaging absolute attribution values
across these 60 instances. Statistical tests on feature importances used all 42
SHAP-retained and 36 LIME-retained feature pairs (features absent in one model's
explanation were excluded from the paired comparison).

All configuration parameters (random seed, SMOTE hyperparameters, bootstrap
iteration count, significance levels) are stored in `configs/*.yaml` and applied
uniformly. All output artifacts (predictions, explanations, evaluation reports,
tables, figures) are version-controlled via SHA-256 hashes verified before
statistical analysis. Full reproduction instructions are provided in the repository.

---

## V. Results

### A. Predictive Performance (RQ1)

Table I reports per-class metrics for both models. Table II reports 95% bootstrap
confidence intervals for aggregate metrics [Fig. 22, Fig. 23].

SMOTE reduced accuracy by 0.0383 (0.7543→0.7161;
95% CI Baseline [0.7516, 0.7574] vs SMOTE [0.7129,
0.7191]; non-overlapping) and weighted F1 by 0.0149,
while improving macro F1 by 0.0170 (95% CI Baseline [0.4556,
0.4853] vs SMOTE [0.4752, 0.4989]).

McNemar's test confirmed that the models disagree at a statistically significant
rate (χ²(Yates)=1547.51, p≈0; corrected threshold α=0.0125). Of 82,332
test instances, 1632 (1.98%) were gained by SMOTE (Baseline wrong,
SMOTE correct) while 4784 (5.81%) were lost. Despite statistical
significance, all Cohen's h values are negligible: h(accuracy)=-0.0868,
h(macro F1)=0.0340, h(weighted F1)=-0.0354 [Table III, Fig. 24].

At the class level [Fig. 6, Fig. 7, Fig. 8, Table I], SMOTE improved F1 for
minority attack classes (mean recall gain +0.325 across minority
categories; Worms: 0.233→0.452) while degrading F1 for
majority classes (mean F1 change -0.020; Normal: 0.848→
0.809). This trade-off is the expected consequence of synthetic
oversampling: improved minority-class coverage at the cost of majority-class
precision.

**Verdict (RQ1):** SMOTE was partially beneficial — statistically significant
aggregate differences but all negligible practical effect sizes; minority-class
F1 improved substantially while majority-class F1 declined modestly.

### B. Explanation Quality (RQ2)

SHAP global feature attribution rankings showed moderate stability across
conditions (Spearman ρ=0.900, top-5 overlap=0.80) [Fig. 9,
Fig. 10, Fig. 11, Fig. 12, Fig. 19, Fig. 20]. A Wilcoxon signed-rank test on
42 paired feature importances confirmed a statistically significant distributional
shift (W=283, p=0.0347; Holm-corrected threshold α=0.050) with a medium
practical effect (rank-biserial r=0.3259) [Table IV, Fig. 24].

LIME global feature attribution rankings showed considerably lower stability
(Spearman ρ=0.565, top-5 overlap=0.60) [Fig. 13, Fig. 14,
Fig. 19, Fig. 20]. The Wilcoxon test on 36 paired LIME importances confirmed a
larger and more significant shift (W=115, p=0.000359; Holm-corrected
threshold α=0.025) with a large practical effect (r=0.5947) [Table IV].

Inter-method agreement between SHAP and LIME was low in both conditions
(Spearman ρ=0.410 at Baseline, ρ=0.476 after SMOTE)
[Fig. 21], consistent with SHAP and LIME capturing different aspects of model
behaviour. SMOTE slightly improved inter-method agreement.

**Verdict (RQ2):** SMOTE caused a significant change in XAI explanations; LIME
was more sensitive than SHAP (large vs medium effect).

### C. Predictive vs Explanatory Sensitivity (RQ3)

The central finding is an asymmetry between predictive and explanatory sensitivity
to class rebalancing [Fig. 24, Table III]. All predictive effect sizes are
negligible (max Cohen's h=0.0868), while explanation effect sizes range from
small (confidence scores, r=0.1686) to medium (SHAP, r=0.3259) to large
(LIME, r=0.5947). LIME's effect size is approximately 6.8× larger than
the maximum predictive effect size.

**Verdict (RQ3):** Explanatory sensitivity substantially exceeds predictive
sensitivity; LIME is the most affected metric.

### D. Hypothesis Test Summary (RQ4)

All four hypothesis tests rejected H₀ after Holm–Bonferroni correction (Table IV).
The research hypothesis — that class rebalancing affects XAI explanations more than
aggregate predictive metrics — is supported by the asymmetry between negligible
predictive effect sizes and medium-to-large explanation effect sizes. LIME's greater
sensitivity relative to SHAP (Δr=0.269) confirms the secondary
prediction that perturbation-based explanation is more affected by training
distribution than tree-attribution–based explanation.

---

## VI. Discussion

### A. Interpretation of Findings

The central finding — that SMOTE changes explanation structure more than prediction
structure — has an intuitive interpretation. Class rebalancing redistributes the
model's learned decision boundary: minority classes, previously under-represented,
receive proportionally more training signal. Even when the aggregate classification
accuracy remains essentially unchanged, the model's internal feature weighting
must shift to accommodate the new distribution. Post-hoc explanation methods
detect this shift directly, because they query the model's local decision surface
rather than summarising outputs with a single metric. This explains why LIME,
which evaluates the model on perturbed local neighbourhoods, is more sensitive than
SHAP, which computes global feature attributions over the training data's support.

### B. Practical Implications

The following practical implications are derived from the experimental evidence:
1. **Cybersecurity practitioners:** Accuracy alone is insufficient to validate retraining. When a NIDS model is retrained with a different class distribution (e.g., after class balancing), explanation outputs may change substantially even if accuracy changes are negligible. Operators should re-validate XAI outputs after any retraining.
2. **Intrusion detection deployment:** SMOTE improves minority-class detection (e.g., Worms F1 doubled from 0.23 to 0.45) at a modest cost to majority-class precision. For NIDS deployed in environments where rare attacks are high-priority, this trade-off is likely acceptable. For environments where false-positive reduction is paramount (Normal class precision 96.7% → 97.8% with SMOTE), the choice depends on operational requirements.
3. **Model transparency and explainability:** LIME-based explanations are substantially more sensitive to training data distribution than SHAP-based explanations. Practitioners who use LIME for post-hoc explanation of NIDS decisions should be aware that a change in training class distribution can produce a large (r=0.595) shift in LIME explanations without a corresponding change in model accuracy.
4. **Trustworthy AI:** Explanation instability undermines trust in AI-assisted security tools. Even when a model performs comparably, its explanations may shift in ways that confuse or mislead analysts comparing pre- and post-balancing model behaviour. XAI pipelines should include explanation-consistency monitoring alongside accuracy monitoring.
5. **Responsible AI and operational monitoring:** Retraining-triggered explanation audits should be standard practice. An operational monitoring process that tracks both predictive metrics and explanation metrics (e.g., Spearman correlation of feature rankings before and after retraining) would detect explanation drift that accuracy-only monitoring misses.

### C. Relationship to Trustworthy AI

The asymmetry between predictive and explanatory sensitivity has direct implications
for trustworthy AI frameworks in cybersecurity [12, 15]. Regulatory
guidance on AI transparency increasingly requires that explanations be provided for
consequential decisions [23]. If those explanations are unstable
under routine model updates (such as rebalancing), the explanations themselves
become unreliable, even when the model's performance metrics remain acceptable.
To the best of the authors' knowledge, this study provides the first empirical
evidence of this instability in a standardised NIDS benchmark setting.

---

## VII. Limitations

### A. Internal Validity
- **Single rebalancing technique:** Only SMOTE was evaluated. Other techniques (ADASYN, cost-sensitive learning, undersampling, ensemble methods) may produce different predictive and explanatory outcomes.
- **Single model family:** Random Forest was the only classifier evaluated. SHAP TreeExplainer is specific to tree-based models; LIME's sensitivity may differ for neural networks or SVMs.
- **Explanation subset size:** SHAP and LIME explanations were computed on 60 samples (computational tractability). The Wilcoxon tests on feature importances used n=42 (SHAP) and n=36 (LIME) pairs.

### B. External Validity
- **Single dataset:** UNSW-NB15 training set (175,341 rows) and test set (82,332 rows) from a controlled lab environment (University of New South Wales, 2015). Findings may not transfer to operational enterprise or cloud NIDS.
- **SMOTE on synthetic network traffic:** SMOTE generated 384,659 synthetic samples. Synthetic minority samples may not faithfully represent real attack traffic patterns in production networks.
- **Static dataset:** UNSW-NB15 is a point-in-time capture. Concept drift in live network traffic may invalidate explanation patterns.

### C. Construct Validity
- **Operationalisation of XAI quality:** Explanation quality is operationalised as feature rank stability (Spearman correlation, top-k overlap) and importance magnitude shift (Wilcoxon). Other definitions (human interpretability, fidelity to ground-truth causal features) are not evaluated.
- **SHAP vs LIME comparability:** SHAP values are additive feature attributions; LIME weights are local linear approximation coefficients on a different feature scale. Comparing their effect sizes is indicative only.

---

## VIII. Future Work

- **Alternative rebalancing techniques:** This study evaluated only SMOTE. ADASYN, random undersampling, class-weighted loss, and ensemble-based methods may produce qualitatively different explanation shifts. A systematic comparison would generalise this study's findings.
- **Explanation sensitivity across model families:** SHAP TreeExplainer was used here because the model is a Random Forest. Gradient-based SHAP (for neural networks) and Integrated Gradients may exhibit different sensitivity profiles to class rebalancing.
- **Human-centred evaluation of explanation instability:** This study used rank-based metrics to quantify explanation change. Whether the observed rank shifts are perceived as meaningful or confusing by security analysts is an open empirical question requiring a user study.
- **Multi-dataset validation:** UNSW-NB15 is a single controlled-environment dataset. Validation on CICIDS-2017, NSL-KDD, or operational enterprise logs would improve generalisability of findings.
- **Temporal and concept-drift evaluation:** This study used a static predefined train/test split. Future work should evaluate explanation stability under concept drift, where attack traffic patterns evolve over time.
- **Explanation-consistency metrics for model certification:** This study showed that explanation-consistency monitoring provides information that accuracy monitoring misses. Formal metrics for XAI-based model certification in security applications are a practical research need.

---

## IX. Conclusion

This paper presented a controlled empirical investigation into the impact of
SMOTE-based class rebalancing on the predictive performance and XAI explanation
quality of a Random Forest–based NIDS trained on the UNSW-NB15 benchmark.
Statistical analysis of 82,332 paired test-set predictions confirmed that SMOTE
produces statistically significant but practically negligible changes to aggregate
predictive metrics (max Cohen's h=0.087), while producing medium-to-large
changes to SHAP and LIME feature attribution rankings (rank-biserial r up to
0.595 for LIME).

The primary finding — that LIME explanation sensitivity to class rebalancing is
approximately 6.8× greater than predictive sensitivity — demonstrates that
accuracy-only validation is insufficient for XAI-augmented NIDS pipelines.
Practitioners who rely solely on accuracy or F1 to validate a retrained model
risk deploying explanations that have changed substantially in their feature
attribution rankings, potentially misleading security analysts.

The secondary finding — that LIME is more sensitive than SHAP to training
distribution changes — has methodological implications for XAI tool selection in
security applications: perturbation-based local explanation methods (LIME) should
be validated independently when training data composition changes.

Future work should validate these findings across additional datasets, model
families, and rebalancing strategies to establish the generalisability of
explanation-consistency monitoring as a practical requirement in trustworthy NIDS
development.

---

## References

[1] L. Breiman, "Random forests," *Mach. Learn.*, vol. 45, no. 1, pp. 5–32,
Oct. 2001. doi: 10.1023/A:1010933404324.

[2] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE:
Synthetic minority over-sampling technique," *J. Artif. Intell. Res.*, vol. 16,
pp. 321–357, Jun. 2002. doi: 10.1613/jair.953.

[3] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel
et al., "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*,
vol. 12, pp. 2825–2830, Nov. 2011. [Online]. Available:
http://jmlr.org/papers/v12/pedregosa11a.html

[4] N. Moustafa and J. Slay, "UNSW-NB15: A comprehensive data set for network
intrusion detection systems," in *Proc. IEEE Military Commun. Inf. Syst. Conf.
(MilCIS)*, Canberra, Australia, Nov. 2015, pp. 1–6.
doi: 10.1109/MilCIS.2015.7348942.

[5] M. T. Ribeiro, S. Singh, and C. Guestrin, "'Why should I trust you?':
Explaining the predictions of any classifier," in *Proc. 22nd ACM SIGKDD Int.
Conf. Knowl. Discovery Data Mining (KDD)*, San Francisco, CA, USA, Aug. 2016,
pp. 1135–1144. doi: 10.1145/2939672.2939778.

[6] G. Lemaître, F. Nogueira, and C. K. Aridas, "Imbalanced-learn: A Python
toolbox to tackle the curse of imbalanced datasets in machine learning," *J. Mach.
Learn. Res.*, vol. 18, no. 17, pp. 1–5, 2017. [Online]. Available:
http://jmlr.org/papers/v18/16-365.html

[7] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model
predictions," in *Adv. Neural Inf. Process. Syst. (NeurIPS)*, vol. 30, Long
Beach, CA, USA, Dec. 2017, pp. 4766–4777. [Online]. Available:
https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html

[8] S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair et al.,
"From local explanations to global understanding with explainable AI for trees,"
*Nat. Mach. Intell.*, vol. 2, no. 1, pp. 56–67, Jan. 2020.
doi: 10.1038/s42256-019-0138-9.

[9] A. Patil, A. Framewala, and F. Kazi, "Explainability of SMOTE based
oversampling for imbalanced dataset problems," in *Proc. IEEE Int. Conf. Inf.
Commun. Technol. (ICICT)*, San Jose, CA, USA, Feb. 2020, pp. 41–45.
doi: 10.1109/ICICT50521.2020.9092325. [⚠ DOI unverified — confirm via IEEE Xplore]

[10] R. Alshamy, M. Ghurab, S. Othman, and F. Alshami, "Intrusion detection model
for imbalanced dataset using SMOTE and random forest algorithm," in *Advances in
Cyber Security (ACeS 2021)*, Commun. Comput. Inf. Sci. (CCIS), vol. 1487,
Singapore: Springer, 2021, pp. 311–323. doi: 10.1007/978-981-16-8059-5_22.

[11] G. Visani, E. Bagli, F. Chesani, A. Poluzzi, and D. Capuzzo, "Statistical
stability indices for LIME: Obtaining reliable explanations for machine learning
models," *J. Oper. Res. Soc.*, vol. 73, no. 1, pp. 91–101, 2022.
doi: 10.1080/01605682.2020.1865846.

[12] F. Charmet, H. C. Tanuwidjaja, S. Ayoubi, P. F. Gimenez, Y. Han, H. Jmila
et al., "Explainable artificial intelligence for cybersecurity: A literature survey,"
*Ann. Telecommun.*, vol. 77, no. 11–12, pp. 789–812, 2022.
doi: 10.1007/s12243-022-00926-7.

[13] T. Wu, H. Fan, H. Zhu, C. You, H. Zhou, and X. Huang, "Intrusion detection
system combined enhanced random forest with SMOTE algorithm," *EURASIP J. Adv.
Signal Process.*, vol. 2022, Art. no. 39, 2022.
doi: 10.1186/s13634-022-00871-6.

[14] I. Alarab and S. Prakoonwit, "Effect of data resampling on feature importance
in imbalanced blockchain data: Comparison studies of resampling techniques," *Data
Sci. Manag.*, vol. 5, no. 2, pp. 66–76, Jun. 2022.
doi: 10.1016/j.dsm.2022.04.003.

[15] G. Rjoub, J. Bentahar, O. Abdel Wahab, R. Mizouni, A. Song, R. Cohen et al.,
"A survey on explainable artificial intelligence for cybersecurity," *IEEE Trans.
Netw. Serv. Manag.*, vol. 20, no. 4, pp. 5115–5140, Dec. 2023.
doi: 10.1109/TNSM.2023.3282740.

[16] S. More, M. Idrissi, H. Mahmoud, and A. T. Asyhari, "Enhanced intrusion
detection systems performance with UNSW-NB15 data analysis," *Algorithms*, vol. 17,
no. 2, Art. no. 64, Feb. 2024. doi: 10.3390/a17020064.

[17] D. Gaspar, P. Silva, and C. Silva, "Explainable AI for intrusion detection
systems: LIME and SHAP applicability on multi-layer perceptron," *IEEE Access*,
vol. 12, pp. 30164–30175, 2024. doi: 10.1109/ACCESS.2024.3368377.

[18] H. R. Sayegh, W. Dong, and A. M. Al-madani, "Enhanced intrusion detection
with LSTM-based model, feature selection, and SMOTE for imbalanced data," *Appl.
Sci.*, vol. 14, no. 2, Art. no. 479, Jan. 2024. doi: 10.3390/app14020479.

[19] V. Shanmugam, R. Razavi-Far, and E. Hallaji, "Addressing class imbalance in
intrusion detection: A comprehensive evaluation of machine learning approaches,"
*Electronics*, vol. 14, no. 1, Art. no. 69, Jan. 2025.
doi: 10.3390/electronics14010069.

[20] P. Hermosilla, S. Berríos, and H. Allende-Cid, "Explainable AI for forensic
analysis: A comparative study of SHAP and LIME in intrusion detection models,"
*Appl. Sci.*, vol. 15, no. 13, Art. no. 7329, Jul. 2025.
doi: 10.3390/app15137329.

[21] P. Hermosilla, M. Díaz, S. Berríos, and H. Allende-Cid, "Use of explainable
artificial intelligence for analyzing and explaining intrusion detection systems,"
*Computers*, vol. 14, no. 5, Art. no. 160, May 2025.
doi: 10.3390/computers14050160.

[22] P. Virtanen, R. Gommers, T. E. Oliphant, M. Haberland, T. Reddy,
D. Cournapeau et al., "SciPy 1.0: Fundamental algorithms for scientific computing
in Python," *Nat. Methods*, vol. 17, pp. 261–272, Feb. 2020.
doi: 10.1038/s41592-020-0772-5. [⚠ Verify before submission — not in original
verified literature database; DOI confirmed via doi.org]

[23] European Parliament and Council of the European Union, "Regulation (EU)
2024/1689 laying down harmonised rules on artificial intelligence (Artificial
Intelligence Act)," *Off. J. Eur. Union*, Jul. 2024. [Online]. Available:
https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689
[⚠ Verify citation form with venue editorial guidelines before submission]

---
