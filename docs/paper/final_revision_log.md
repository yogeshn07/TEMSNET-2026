# Final Revision Log — TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection
**Source file:** docs/paper/camera_ready_manuscript.md
**Output file:** docs/paper/final_submission_manuscript.md
**Revision date:** 2026-07-09
**Revision type:** Minor revision (mandatory reviewer requirements only)
**Scientific content:** LOCKED — no numerical values, statistical results, or scientific claims modified

---

## Change Index

| ID | Section | Type | Revision | Reviewer(s) |
|---|---|---|---|---|
| C01 | Abstract | Wording | Removed "approximately 6.8 times the magnitude of the largest predictive effect"; replaced with qualitative asymmetry statement | R4, AC |
| C02 | Abstract | Wording | "is therefore a necessary component" → "is therefore an important component" | R1 |
| C03 | §II-C | Wording | "to our knowledge" → "to the best of the authors' knowledge" | R8 (consistency) |
| C04 | §I (contributions) | Wording | "showing LIME to be substantially more sensitive" (was "showing") | R8 (precision) |
| C05 | §III-E | Addition | Added LIME configuration details: `num_features=10`, `num_samples=5000`; local R² defined as "coefficient of determination of each local linear model" | R3, R1 |
| C06 | §III-F | Addition | Added explicit McNemar's test rationale: "the appropriate paired test for comparing two classifiers on the same test set" | R4 |
| C07 | §III-F | Addition | Added Wilcoxon zero-method documentation: "34,002 pairs with zero difference were excluded using the Wilcoxon zero-method" | R4 |
| C08 | §III-F | Addition | Added Cohen's h formula: h = 2 arcsin(√p₁) − 2 arcsin(√p₂) with magnitude thresholds | R4, R3 |
| C09 | §III-F | Addition | Added rank-biserial r formula: r = Z / √N from Wilcoxon normal approximation with magnitude thresholds | R4, R3 |
| C10 | §III-F | Addition | Added cross-metric incomparability statement: "Because Cohen's h operates on proportion data (n = 82,332) and rank-biserial r operates on feature importance ranks (n = 42 or 36)... cross-metric comparisons are therefore interpreted as qualitative indicators" | R4, R3, AC |
| C11 | §III-F | Addition | Added Holm–Bonferroni explicit thresholds: α/4, α/3, α/2, α | R4 |
| C12 | §III-F | Addition | Added power analysis paragraph: ~0.55 at n = 42 (SHAP); ~0.90 at n = 36 (LIME); interpretive guidance for SHAP result | R1, R4, AC |
| C13 | §IV | Expansion | Expanded 60-instance sampling paragraph: added "identical set of 60 instances was used for both models"; added "deterministic shared-instance protocol eliminates instance-selection variance"; added reproducibility statement | R1, R5 (revision 5), AC |
| C14 | §V-A | Addition | Added Worms caveat sentence: "The Worms test class contains only 44 instances; per-class F1 statistics at this sample size are sensitive to individual prediction outcomes and are presented as indicative results rather than stable estimates of population-level performance." | R2, R6 (revision 6), AC |
| C15 | Table I | Addition | Added dagger (†) to Worms row; added footnote "† n = 44; per-class metrics interpreted as indicative (see §V-A)" | R2, AC |
| C16 | Table II footnote | Wording | "confirming a statistically significant aggregate difference" → "corroborating the McNemar's test finding of a statistically significant aggregate predictive difference" (strengthens logical flow) | R10 |
| C17 | §V-B (LIME) | Addition | Added LIME local surrogate fidelity paragraph: "LIME local surrogate fidelity, measured by the mean coefficient of determination (R²) of each instance's local linear model, was 0.290 for the Baseline model and 0.252 for the SMOTE model... the ranking shift finding (r = 0.5947) is statistically robust; however, LIME attribution magnitudes reflect the linear surrogate under moderate fidelity conditions and should be understood as approximations of local model behaviour rather than exact attributions." | R3, AC — PRIMARY REVISION |
| C18 | §V-B Verdict (RQ2) | Wording | Updated verdict to add LIME fidelity caveat: "LIME results interpreted in light of moderate local surrogate fidelity (R² ≈ 0.25–0.29)" | R3, AC |
| C19 | §V-C | Wording | Removed "LIME's effect size is approximately 6.8× larger than the maximum predictive effect size"; replaced with: "LIME's explanatory effect size (r = 0.5947, large) substantially exceeds the maximum predictive effect size (|h| = 0.0868, negligible). As these two metrics operate on different scales and reflect different sample sizes... this comparison indicates a qualitative asymmetry... rather than a precise proportional relationship." | R4, AC — PRIMARY REVISION |
| C20 | §V-C Verdict (RQ3) | Wording | "LIME is the most affected metric" → "LIME attribution rankings exhibited the greatest sensitivity to class rebalancing of all outputs examined" | R1 |
| C21 | §V-D (§V-D body) | Wording | "confirms the secondary prediction" → "is consistent with the expectation" (proportionate to evidence) | R8 |
| C22 | Fig. 24 caption | Wording | Removed "approximately 6.8×"; added "Note: the two metrics operate on different scales and sample sizes; the figure illustrates qualitative asymmetry, not a precise proportional ratio." | R4, AC |
| C23 | Table III footnote | Addition | Added explicit formulas for Cohen's h and rank-biserial r; added "Metrics operate on different scales; cross-row comparisons are qualitative." | R4, R3, AC |
| C24 | Table IV footnote | Addition | Added power note: "SHAP result interpreted at approximate power ~0.55 (n = 42); LIME at ~0.90 (n = 36)." | R1, R4 |
| C25 | §VI-A | Wording | Added "This is consistent with LIME being more sensitive than SHAP: LIME evaluates the model on perturbed local neighbourhoods, which are directly affected by the shifted decision boundary" — mechanistic explanation added | R3 |
| C26 | §VI-B point 2 | Expansion | Added explicit b/c asymmetry: "of 82,332 test instances, SMOTE gained 1,632 (1.98%) predictions but lost 4,784 (5.81%)"; added differentiated guidance for false-positive-sensitive deployments | R2 |
| C27 | §VII-A | Expansion | Renamed "Explanation subset size" bullet to "Explanation subset size and statistical power"; added power estimates with interpretation for both SHAP (modest power) and LIME (adequate power); added caveat that non-significant SHAP result would have been inconclusive | R1, R4, AC |
| C28 | §VII-A | Addition | Added new "LIME surrogate fidelity" bullet explicitly documenting R² = 0.290 (Baseline) and 0.252 (SMOTE) as a construct validity limitation, with note that the ranking shift is statistically robust but absolute magnitudes are approximations | R3, AC |
| C29 | §VII-B | Expansion | Expanded "Single dataset" bullet to full paragraph titled "Single dataset and temporal scope": explicitly states 2015 release year, discusses evolved attack techniques, TLS 1.3, microservice traffic, cloud APIs; recommends validation on CICIDS-2017 or CSE-CIC-IDS-2018 | R2, AC — PRIMARY REVISION |
| C30 | §VII-B | Addition | Added "Concept drift" bullet: "UNSW-NB15 is a point-in-time capture. Concept drift in live network traffic may invalidate both predictive performance and explanation patterns observed in this study." | R2 |
| C31 | §VII-C | Addition | Added "SHAP vs. LIME comparability" elaboration: "the absolute magnitudes of their rank-biserial r values are not directly commensurate" | R3 |
| C32 | §VII-C | Addition | Added "Worms class sample size" bullet in Construct Validity: "The Worms test class contains only 44 instances. F1 comparisons at this scale are sensitive to individual prediction outcomes and are reported as indicative results rather than stable population estimates." | R2, AC |
| C33 | §IX Conclusion | Wording | Removed "approximately 6.8× greater"; replaced with "substantially and disproportionately exceeds predictive sensitivity across complementary effect-size measures" | R4, AC — PRIMARY REVISION |
| C34 | §IX Conclusion | Addition | Added LIME fidelity caveat in conclusion: "This finding holds even with the caveat that LIME local surrogate fidelity (R² ≈ 0.25–0.29) is moderate: the statistical evidence for a large explanatory shift is robust regardless of absolute attribution magnitudes." | R3 |
| C35 | §IX Conclusion | Addition | Expanded secondary finding sentence to include LIME surrogate fidelity and the recommendation that "surrogate fidelity should be reported alongside attribution rankings" | R3 |

---

## Changes NOT Made (with Justification)

| Item | Requested By | Reason Not Implemented |
|---|---|---|
| LIME repeatability control (same model, different seed) | R3 | New experiment — content lock prohibits new analyses; acknowledged in §VII-A and §VII-C as future work |
| Second dataset (CICIDS-2017) | R2 | New experiment — out of scope for minor revision; acknowledged in §VIII Future Work |
| Multiple model families | R1 | New experiment — out of scope for minor revision; acknowledged in §VII-A |
| Foundational statistical citations (Holm 1979, Wilcoxon 1945) | R4 | Not in verified [1]–[23] reference list; requires author verification; flagged as author action in reviewer_response_matrix.md |
| Hyperparameter ablation (k_neighbors, n_estimators) | R1 | New experiment — out of scope; acknowledged as limitation |
| Per-class XAI stability metrics for minority classes | R3 | New analysis — content lock prohibits; acknowledged in §VIII Future Work |

---

## Terminology Consistency Audit (Revision 9)

All occurrences verified across all sections:

| Term | Uses | Consistent? |
|---|---|---|
| eXplainable AI (XAI) | Defined §I; used throughout | ✅ |
| SMOTE | Defined §I with citation [2]; "SMOTE model" / "SMOTE-rebalanced" consistent | ✅ |
| SHAP (SHapley Additive exPlanations) | Defined §I; abbreviated SHAP throughout | ✅ |
| LIME (Local Interpretable Model-agnostic Explanations) | Defined §I; abbreviated LIME throughout | ✅ |
| UNSW-NB15 | Consistent capitalisation throughout | ✅ |
| Random Forest | Capitalised as proper noun throughout | ✅ |
| Baseline model | Capitalised "Baseline" when referring to the specific trained model | ✅ |
| SMOTE model | Capitalised "SMOTE" throughout | ✅ |
| rank-biserial r | Consistent hyphenation throughout | ✅ |
| Cohen's h | Consistent throughout | ✅ |
| Network Intrusion Detection System(s) / NIDS | NIDS defined §I; consistent | ✅ |
| McNemar's test | Consistent capitalisation and possessive | ✅ |
| Holm–Bonferroni | En-dash consistently used | ✅ |
| British English | behaviour, summarising, neighbourhood, artefacts, characterise, generalise | ✅ |
| "demonstrates" (not "proves") | All claims use "demonstrate", "show", "indicate", "support" | ✅ |
| "to the best of the authors' knowledge" | Used in §II-C and §VI-C | ✅ |

---

## Language Polish Audit (Revision 10)

Corrections applied during final polish pass:

| Location | Type | Original | Corrected |
|---|---|---|---|
| §II-C | Hedging | "to our knowledge" | "to the best of the authors' knowledge" |
| §V-B Verdict | Parallel structure | "LIME was more sensitive than SHAP" | "LIME attribution rankings exhibited a larger shift than SHAP" |
| §V-C Verdict | Imprecision | "LIME is the most affected metric" | "LIME attribution rankings exhibited the greatest sensitivity" |
| §VI-A | Transition | "This explains why" | "This is consistent with LIME being more sensitive than SHAP:" (hedged) |
| §VI-B pt.1 | Prescriptive | "Operators should" | "Practitioners should" |
| Table II footnote | Flow | "confirming a statistically significant" | "corroborating the McNemar's test finding of a statistically significant" |
| §VII-A bullet | Title | "Explanation subset size" | "Explanation subset size and statistical power" |
| §VII-B bullet | Title | "Single dataset" | "Single dataset and temporal scope" |
| §IX para. 2 | Overclaim | "approximately 6.8× greater" | "substantially and disproportionately exceeds" |
| §IX para. 2 | Active voice | "risk deploying explanations" → | Added "may unknowingly deploy models whose explanation attribution rankings have changed substantially" |

---

*End of final_revision_log.md | 2026-07-09*
