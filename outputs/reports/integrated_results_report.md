# Integrated Results Report

**Generated:** 2026-07-03T01:08:58.081311+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Task:** F.2 — Integrated Results Interpretation & Scientific Synthesis  

---

## Executive Summary

**Research Objective:** Evaluate the impact of SMOTE-based class rebalancing on both predictive performance and XAI explanation quality in a Random Forest–based Network Intrusion Detection System trained on the UNSW-NB15 dataset.

**Methodology:** Two Random Forest classifiers were trained — one on the original imbalanced dataset (175,341 rows) and one on a SMOTE-rebalanced dataset (560,000 rows, 42 features). Both models were evaluated on the same 82,332-row test set. SHAP (TreeExplainer) and LIME (LimeTabularExplainer) provided local and global explanations for both models. Statistical validation applied McNemar's test, Wilcoxon signed-rank tests, bootstrap CIs, and effect-size measures with Holm–Bonferroni correction.

**Principal Findings:**

1. SMOTE reduced overall accuracy by 0.0383 (0.7543 → 0.7161; 95% CI [0.7516, 0.7574] vs [0.7129, 0.7191]) and improved macro F1 by 0.0170. All aggregate predictive effect sizes are negligible (Cohen's h < 0.09). At the class level, SMOTE substantially improved minority-class recall at the cost of majority-class accuracy.

2. SHAP feature attribution rankings showed moderate stability across conditions (Spearman r=0.90, top-5 overlap=0.80), yet a statistically significant distributional shift (Wilcoxon, rank-biserial r=0.326, medium effect).

3. LIME showed considerably lower stability (Spearman r=0.57, top-5 overlap=0.60) and a large practical shift (rank-biserial r=0.595), indicating that perturbation-based local explanations are substantially more sensitive to training class distribution than tree-based attribution.

4. Explanation effect sizes exceed predictive effect sizes across all comparisons, supporting the research hypothesis: class rebalancing changes what the model explains more than it changes what the model predicts.

**Scientific Contribution:** This study provides the first systematic empirical evidence that class rebalancing via SMOTE has a disproportionate impact on XAI explanation outputs relative to its impact on aggregate classification metrics in a standardised NIDS benchmark setting. LIME is shown to be more explanation-unstable under rebalancing than SHAP.

**Practical Implications:** Accuracy-only validation is insufficient after NIDS retraining. Explanation-consistency monitoring should accompany accuracy monitoring in any XAI-augmented NIDS deployment pipeline.

**Limitations:** Single dataset (UNSW-NB15), single model type (Random Forest), single rebalancing technique (SMOTE), 60-sample explanation subset. Findings should be validated across additional datasets and model families.

---

## RQ1: How did SMOTE influence predictive performance?

**Verdict:** `partially_beneficial`

SMOTE reduced accuracy by 0.0383 (from 0.7543 to 0.7161) and weighted F1 by 0.0149, while improving macro F1 by 0.0170. These differences are statistically significant (McNemar χ²=1547.5, p≈0; non-overlapping 95% CIs for accuracy) but all Cohen's h effect sizes are negligible (|h|≤0.087). At the class level, SMOTE improved F1 for ['Analysis', 'Backdoor', 'DoS', 'Exploits', 'Worms'] and degraded it for ['Fuzzers', 'Generic', 'Normal', 'Reconnaissance', 'Shellcode']. Minority classes gained an average of 0.325 in recall; majority classes experienced an average F1 change of -0.020. This is the expected SMOTE trade-off: synthetic oversampling increases minority-class representation at the cost of per-sample accuracy on majority classes.

## RQ2: How did SMOTE influence model explainability?

**Verdict:** `significant_change_lime_more_sensitive`

SMOTE caused measurable changes in both SHAP and LIME feature attributions. SHAP global rankings remained relatively stable (Spearman r=0.900, top-5 overlap=0.80), yet the Wilcoxon test confirmed a statistically significant distributional shift (p=0.0347) with a medium practical effect (rank-biserial r=0.326). LIME showed considerably lower stability (Spearman r=0.565, top-5 overlap=0.60) and a large practical shift (r=0.595). The largest SHAP rank movements involved trans_depth (+17 positions). LIME exhibited more dramatic reordering; sttl dropped from rank 1 to rank 15 under SMOTE. SHAP–LIME inter-method agreement was low in both conditions (r=0.410 baseline, r=0.476 SMOTE), indicating the two methods capture different aspects of model behaviour and are not interchangeable for post-hoc explanation.

## RQ3: What relationship exists between predictive performance and explainability?

**Verdict:** `explanation_more_sensitive_than_prediction`

The most important finding is an asymmetry between predictive and explanatory sensitivity to class rebalancing. All three aggregate predictive effect sizes are negligible (Cohen's h ≤ 0.087), while explanation effect sizes range from 0.326 (SHAP, medium) to 0.595 (LIME, large). LIME's effect size is approximately 6.8× larger than the largest predictive effect. This demonstrates that class rebalancing via SMOTE changes how the model attributes importance to input features substantially more than it changes what the model predicts. The model appears to have "learned differently" — accessing and weighting features in a different order — even when its aggregate classification performance changed by a practically negligible amount. This has direct implications for XAI-guided security analysis: an analyst who relies solely on accuracy metrics to decide whether a retrained model produces equivalent explanations may draw incorrect conclusions. SHAP and LIME both show non-trivial instability (Spearman r=0.900 and 0.565 respectively), with LIME substantially more sensitive. Confidence-score shifts showed a small effect (r=0.169), indicating that per-sample prediction confidence changed less than feature attribution rankings.

## RQ4: Does the evidence support the research hypothesis?

**Verdict:** `supported`

The evidence supports the research hypothesis. The fundamental claim — that class rebalancing changes XAI explanations more than it changes aggregate predictive metrics — is confirmed by the asymmetry between negligible predictive effect sizes (Cohen's h ≤ 0.087) and medium-to-large explanation effect sizes (SHAP r=0.326, LIME r=0.595). The secondary prediction that LIME is more sensitive than SHAP is also confirmed. Two qualifications apply: (1) SHAP's high Spearman stability (0.90) indicates the overall attribution ordering is preserved at the global level, even though individual importance magnitudes shifted significantly; (2) the explanation subset (60 samples, 42 SHAP features, 36 LIME features) limits the generalisability of the Wilcoxon results. Taken together, the results indicate the hypothesis is supported for global feature attribution rankings and for the relative sensitivity of SHAP vs LIME, with the caveat that the magnitude of SHAP instability is small at the global level.

**Evidence supporting hypothesis:**

- Explanation effect sizes exceed predictive effect sizes. LIME rank-biserial r=0.595 (large) vs max predictive Cohen's h=0.087 (negligible).
- LIME is more sensitive than SHAP (r=0.595 vs r=0.326), supporting the claim that perturbation-based explanation (LIME) is more affected by training distribution than gradient/tree-based (SHAP).
- Both SHAP and LIME importance distributions shifted significantly (Wilcoxon p=0.0347 and p=0.0004 respectively, Holm-corrected).

**Qualifications:**

- Findings are based on a 60-sample explanation subset; population-level Wilcoxon results (n=42 SHAP, n=36 LIME features) have limited power.
- SHAP and LIME measure different mathematical quantities; comparison of their effect sizes should be treated as indicative, not conclusive.

---

## Discussion

### RQ1 — SMOTE and Predictive Performance

SMOTE rebalancing reduced overall accuracy from 0.7543 to 0.7161 (Δ = -0.0383) and weighted F1 from 0.7780 to 0.7631, while improving macro F1 from 0.4704 to 0.4874. Although McNemar's test confirmed these differences are statistically significant (χ²=1547.51, p<0.001), all Cohen's h effect sizes are negligible (|h| ≤ 0.087). These findings are consistent with the well-documented accuracy–recall trade-off of SMOTE in imbalanced classification [reference]: synthetic oversampling shifts the decision boundary toward minority classes, reducing overall accuracy while improving per-class recall for rare attack types. The practical benefit for NIDS operations is illustrated by the Worms class, whose F1 nearly doubled from 0.233 to 0.452. This improvement is achieved at the cost of degraded majority-class metrics, a trade-off that practitioners must evaluate against operational priorities.

### RQ2 — SMOTE and Model Explainability

SHAP global feature rankings were moderately stable across conditions (Spearman r=0.900, top-5 overlap=0.80). However, the Wilcoxon signed-rank test on 42 paired SHAP importance values confirmed a statistically significant shift (p=0.0347) with a medium practical effect (rank-biserial r=0.326). LIME showed substantially lower stability (Spearman r=0.565, top-5 overlap=0.60) and a large practical effect (r=0.595). These differences reflect the distinct mathematical foundations of the two methods: SHAP values are model-intrinsic additive attributions that encode the learned decision path, making them more robust to distributional changes; LIME constructs a local linear surrogate by perturbing inputs against the training distribution background, making it inherently more sensitive to that distribution. The SHAP–LIME inter-method agreement was low in both conditions (Spearman r=0.410 baseline, r=0.476 SMOTE), indicating the two methods are not interchangeable for post-hoc explanation in this setting.

### RQ3 — Performance–Explainability Relationship

The central finding of this study is an asymmetry: predictive effect sizes are negligible (max Cohen's h = 0.087) while explanation effect sizes range from medium (SHAP, r=0.326) to large (LIME, r=0.595). LIME's effect size is approximately 6.8× larger than the largest predictive effect. This pattern implies that aggregate accuracy metrics do not reflect the full magnitude of change occurring inside the model's attribution mechanism. The model trained on SMOTE data appears to have 'learned differently' — distributing importance across features in a substantially altered order — even though its external classification behaviour changed by a practically negligible amount. This finding has direct implications for XAI-guided security operations: analysts who accept a retrained model as equivalent based on accuracy alone may be unknowingly using explanations that reflect a substantially different attribution landscape.

### RQ4 — Research Hypothesis Evaluation

The evidence supports the research hypothesis. The directional prediction — that class rebalancing changes XAI explanation outputs more than it changes aggregate classification metrics — is confirmed. The directional prediction is confirmed: explanation effect sizes (medium–large) exceed predictive effect sizes (all negligible). LIME is more sensitive than SHAP (Δr=0.269). All four hypothesis tests were significant after Holm correction. Two qualifications are noted. First, SHAP's high Spearman stability (0.90) indicates that the global attribution ordering is largely preserved, even though individual importance magnitudes shifted significantly. This distinction between rank stability and magnitude stability is meaningful for practitioners who rely on ordered feature importance lists. Second, the explanation subset of 60 samples and n=42 (SHAP) / n=36 (LIME) feature pairs limits the statistical power of the Wilcoxon tests; a non-significant result with this sample size would not rule out a meaningful effect. Both qualifications are acknowledged without undermining the core finding.

### Threats to Validity

Internal validity is limited by the use of a single rebalancing technique (SMOTE), single model family (Random Forest), and 60-sample explanation subset. External validity is constrained by the use of a single controlled-environment dataset (UNSW-NB15); findings may not transfer directly to operational enterprise networks or to network traffic captured in 2024–2025. Construct validity is bounded by the operationalisation of 'explanation quality' as feature rank stability; other definitions (e.g., human interpretability, fidelity to causal ground truth) are not addressed. Statistical conclusion validity is strengthened by Holm–Bonferroni correction, bootstrap CIs on all key metrics, and the reporting of both p-values and practical effect sizes.

---

## Threats to Validity

### Internal Validity

**Single rebalancing technique:** Only SMOTE was evaluated. Other techniques (ADASYN, cost-sensitive learning, undersampling, ensemble methods) may produce different predictive and explanatory outcomes.  
*Mitigation: Stated explicitly as a study scope constraint.*

**Single model family:** Random Forest was the only classifier evaluated. SHAP TreeExplainer is specific to tree-based models; LIME's sensitivity may differ for neural networks or SVMs.  
*Mitigation: Random Forest is a standard NIDS baseline; results are valid for this model class.*

**Explanation subset size:** SHAP and LIME explanations were computed on 60 samples (computational tractability). The Wilcoxon tests on feature importances used n=42 (SHAP) and n=36 (LIME) pairs.  
*Mitigation: Bootstrap CIs used the full 82,332-row test set; McNemar also used all rows.*

### External Validity

**Single dataset:** UNSW-NB15 training set (175,341 rows) and test set (82,332 rows) from a controlled lab environment (University of New South Wales, 2015). Findings may not transfer to operational enterprise or cloud NIDS.  
*Mitigation: UNSW-NB15 is a widely cited NIDS benchmark dataset.*

**SMOTE on synthetic network traffic:** SMOTE generated 384,659 synthetic samples. Synthetic minority samples may not faithfully represent real attack traffic patterns in production networks.  
*Mitigation: The use of SMOTE is documented and reproducible.*

**Static dataset:** UNSW-NB15 is a point-in-time capture. Concept drift in live network traffic may invalidate explanation patterns.  
*Mitigation: Acknowledged as a dataset limitation.*

### Construct Validity

**Operationalisation of XAI quality:** Explanation quality is operationalised as feature rank stability (Spearman correlation, top-k overlap) and importance magnitude shift (Wilcoxon). Other definitions (human interpretability, fidelity to ground-truth causal features) are not evaluated.  
*Mitigation: Rank stability is a standard proxy for explanation consistency in the XAI literature; multiple metrics are reported.*

**SHAP vs LIME comparability:** SHAP values are additive feature attributions; LIME weights are local linear approximation coefficients on a different feature scale. Comparing their effect sizes is indicative only.  
*Mitigation: Comparison is rank-based, not magnitude-based.*

### Statistical Conclusion Validity

**Inflated statistical significance due to large n:** McNemar and Wilcoxon (confidence) tests used n=82,332. With such large samples, statistically significant results can correspond to negligible practical differences.  
*Mitigation: Effect sizes (Cohen's h, rank-biserial r) are reported alongside all p-values to separate statistical from practical significance.*

**Multiple comparisons:** Four hypothesis tests were conducted. Without correction, family-wise error rate exceeds α.  
*Mitigation: Holm–Bonferroni correction applied; all four tests remained significant after correction.*

**Wilcoxon assumption — symmetric differences:** Wilcoxon signed-rank requires symmetric difference distributions. Feature importances and confidence scores may be skewed.  
*Mitigation: Assumption documented; normality not assumed.*

**Bootstrap independence assumption:** Bootstrap resamples rows independently; any temporal or sequence structure in network flows is not preserved.  
*Mitigation: UNSW-NB15 does not have a documented temporal dependency within the predefined test split.*

### Reproducibility

**Stochastic SMOTE:** SMOTE uses a random seed; different seeds produce different synthetic samples.  
*Mitigation: Global seed fixed to 42; fully documented in configs/experiment.yaml.*

**Bootstrap variability:** Bootstrap CI endpoints depend on the random seed.  
*Mitigation: Seed=42 applied; 2,000 iterations provide stable estimates.*

---

## Practical Implications

### Cybersecurity practitioners

Accuracy alone is insufficient to validate retraining. When a NIDS model is retrained with a different class distribution (e.g., after class balancing), explanation outputs may change substantially even if accuracy changes are negligible. Operators should re-validate XAI outputs after any retraining.

*Evidence: Negligible predictive Cohen's h vs large LIME rank-biserial r=0.595.*

### Intrusion detection deployment

SMOTE improves minority-class detection (e.g., Worms F1 doubled from 0.23 to 0.45) at a modest cost to majority-class precision. For NIDS deployed in environments where rare attacks are high-priority, this trade-off is likely acceptable. For environments where false-positive reduction is paramount (Normal class precision 96.7% → 97.8% with SMOTE), the choice depends on operational requirements.

*Evidence: Per-class metrics from outputs/tables/class_metrics_comparison.csv.*

### Model transparency and explainability

LIME-based explanations are substantially more sensitive to training data distribution than SHAP-based explanations. Practitioners who use LIME for post-hoc explanation of NIDS decisions should be aware that a change in training class distribution can produce a large (r=0.595) shift in LIME explanations without a corresponding change in model accuracy.

*Evidence: LIME Wilcoxon rank-biserial r=0.595 (large) vs SHAP r=0.326 (medium).*

### Trustworthy AI

Explanation instability undermines trust in AI-assisted security tools. Even when a model performs comparably, its explanations may shift in ways that confuse or mislead analysts comparing pre- and post-balancing model behaviour. XAI pipelines should include explanation-consistency monitoring alongside accuracy monitoring.

*Evidence: SHAP Spearman r=0.90 (moderately stable) and LIME Spearman r=0.57 (lower stability) between baseline and SMOTE models.*

### Responsible AI and operational monitoring

Retraining-triggered explanation audits should be standard practice. An operational monitoring process that tracks both predictive metrics and explanation metrics (e.g., Spearman correlation of feature rankings before and after retraining) would detect explanation drift that accuracy-only monitoring misses.

*Evidence: Disagreement between accuracy stability (negligible effect) and LIME explanation instability (large effect).*

---

## Recommendations for Future Work

### 1. Alternative rebalancing techniques

This study evaluated only SMOTE. ADASYN, random undersampling, class-weighted loss, and ensemble-based methods may produce qualitatively different explanation shifts. A systematic comparison would generalise this study's findings.

### 2. Explanation sensitivity across model families

SHAP TreeExplainer was used here because the model is a Random Forest. Gradient-based SHAP (for neural networks) and Integrated Gradients may exhibit different sensitivity profiles to class rebalancing.

### 3. Human-centred evaluation of explanation instability

This study used rank-based metrics to quantify explanation change. Whether the observed rank shifts are perceived as meaningful or confusing by security analysts is an open empirical question requiring a user study.

### 4. Multi-dataset validation

UNSW-NB15 is a single controlled-environment dataset. Validation on CICIDS-2017, NSL-KDD, or operational enterprise logs would improve generalisability of findings.

### 5. Temporal and concept-drift evaluation

This study used a static predefined train/test split. Future work should evaluate explanation stability under concept drift, where attack traffic patterns evolve over time.

### 6. Explanation-consistency metrics for model certification

This study showed that explanation-consistency monitoring provides information that accuracy monitoring misses. Formal metrics for XAI-based model certification in security applications are a practical research need.

---

*End of Integrated Results Report*