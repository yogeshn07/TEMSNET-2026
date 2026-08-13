# Reviewer Response Matrix — TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection
**Revision date:** 2026-07-09
**Decision:** Accept with Minor Revision

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ RESOLVED | Revision fully implemented in final_submission_manuscript.md |
| ℹ️ AUTHOR ACTION | Requires author input; not addressable in prose revision |
| 📝 NOTED | Concern acknowledged; no manuscript change required per Area Chair |

---

## Reviewer 1 — Machine Learning Specialist

| # | Reviewer Comment | Action Taken | Manuscript Location | Status |
|---|---|---|---|---|
| R1-01 | Soften "necessary component" in abstract — single-experiment evidence base does not support normative claim | Changed "is therefore a necessary component" to "is therefore an important component" | Abstract, final sentence | ✅ RESOLVED |
| R1-02 | State the exact within-class instance selection criterion for the 60-sample XAI subsample | Expanded §IV to state that a stratified random sample (six per class, deterministic, identical across models) was used; explained that the shared instance set eliminates selection variance from the paired comparison | §IV, paragraph 2 | ✅ RESOLVED |
| R1-03 | Report approximate statistical power for Wilcoxon tests at n = 42 and n = 36 | Power estimates added: ~0.55 at n = 42 (SHAP, r = 0.326); ~0.90 at n = 36 (LIME, r = 0.595); interpretation guidance added | §III-F (last paragraph); §VII-A (explanation subset bullet); Table IV footnote | ✅ RESOLVED |
| R1-04 | "LIME is most affected metric" — imprecise, LIME is a method not a metric | Changed Verdict (RQ3) to "LIME attribution rankings exhibited the greatest sensitivity to class rebalancing of all outputs examined" | §V-C, Verdict (RQ3) | ✅ RESOLVED |
| R1-05 | Single model, single dataset, single seed — overclaims generalisation | Contributions list now states "demonstrating" (not "proving") LIME sensitivity; Limitations §VII-A and §VII-B retain full scope acknowledgement; no generalisation claims added | §I (contributions), §VII | ✅ RESOLVED |
| R1-06 | Add reproducibility detail: LIME RNG seeding | LIME configuration (num_features=10, num_samples=5000) now stated in §III-E; deterministic seeding via global seed 42 noted in §IV | §III-E, §IV | ✅ RESOLVED |

---

## Reviewer 2 — Cybersecurity / Network Intrusion Detection Specialist

| # | Reviewer Comment | Action Taken | Manuscript Location | Status |
|---|---|---|---|---|
| R2-01 | UNSW-NB15 is from 2015; temporal scope not discussed | Expanded §VII-B "Single dataset" bullet to full paragraph: explicitly states 2015 release, discusses evolved attack techniques, encryption, microservice traffic, and calls for validation on more recent captures (CICIDS-2017, CSE-CIC-IDS-2018) | §VII-B | ✅ RESOLVED |
| R2-02 | Worms test class has only n = 44; F1 comparison is statistically thin | Added explicit caveat sentence in §V-A body text; added dagger (†) and footnote to Table I; added bullet in §VII-C Construct Validity section | §V-A (body), Table I (footnote †), §VII-C | ✅ RESOLVED |
| R2-03 | SMOTE loses 5.81% of predictions vs. gains 1.98%; security implication not emphasised | Expanded §VI-B point 2 to include the b/c asymmetry (1,632 gained, 4,784 lost) and its implications for false-positive-sensitive deployments | §VI-B, point 2 | ✅ RESOLVED |
| R2-04 | "Operators should re-validate" — soften from prescriptive | Changed "Operators should re-validate" to "Practitioners should re-validate" (already in camera-ready); maintained "should" (not "must") throughout §VI-B | §VI-B, point 1 | ✅ RESOLVED |
| R2-05 | Second dataset recommended for validation | Acknowledged in §VIII Future Work (multi-dataset validation already listed); no additional experiment conducted per scope constraints | §VIII | 📝 NOTED |

---

## Reviewer 3 — Explainable AI Specialist

| # | Reviewer Comment | Action Taken | Manuscript Location | Status |
|---|---|---|---|---|
| R3-01 | LIME local R² (0.290 / 0.252) not discussed in §V-B Results — only in figure captions and §VII-C | Added dedicated paragraph in §V-B body: reports R² values, contextualises them as ~25–29% local variance explained, notes that ranking shift is statistically robust but absolute magnitudes are approximations | §V-B (new paragraph after LIME Wilcoxon result) | ✅ RESOLVED |
| R3-02 | R² caveat not integrated into §V-C comparison or Verdict (RQ2) | Updated Verdict (RQ2) to explicitly reference "LIME results interpreted in light of moderate local surrogate fidelity (R² ≈ 0.25–0.29)"; Fig. 24 caption updated to note qualitative nature of cross-metric comparison | §V-B Verdict (RQ2); Fig. 24 caption | ✅ RESOLVED |
| R3-03 | LIME repeatability control (same model, different seed) — absence means LIME variance cannot be separated from SMOTE-induced shift | Area Chair determination: not mandatory for this venue scope. Limitation explicitly acknowledged in §VII-A (LIME surrogate fidelity bullet) and §VII-C; the R² caveat in §V-B now flags this interpretive boundary. No new experiment conducted per content-lock constraints | §VII-A, §VII-C | 📝 NOTED (acknowledged; not blocking per Area Chair) |
| R3-04 | SHAP–LIME cross-metric comparison qualified as "indicative only" | Table III footnote now states "Metrics operate on different scales; cross-row comparisons are qualitative"; §V-C body text explicitly states that cross-metric comparison indicates "qualitative asymmetry rather than a precise proportional relationship" | §V-C body; Table III footnote | ✅ RESOLVED |
| R3-05 | SHAP aggregation (60 × 42 × 10 mean) vs. LIME aggregation (60 × 10-feature mean) are not comparable procedures | Limitation acknowledged in §VII-C "SHAP vs. LIME comparability" bullet (already present); §V-C now explicitly states "these two metrics operate on different scales and reflect different sample sizes" | §V-C; §VII-C | ✅ RESOLVED |

---

## Reviewer 4 — Statistics & Experimental Methodology Specialist

| # | Reviewer Comment | Action Taken | Manuscript Location | Status |
|---|---|---|---|---|
| R4-01 | No statistical power analysis reported for Wilcoxon tests | Power estimates computed and added (n = 42: ~0.55; n = 36: ~0.90) with interpretation guidance | §III-F (final paragraph); §VII-A; Table IV footnote | ✅ RESOLVED |
| R4-02 | Rank-biserial r formula not specified — which formula was used? | Explicitly defined as r = Z / √N from the Wilcoxon normal approximation in §III-F; formula also stated in Table III footnote | §III-F; Table III footnote | ✅ RESOLVED |
| R4-03 | Cohen's h formula not specified | Explicitly defined as h = 2 arcsin(√p₁) − 2 arcsin(√p₂) in §III-F; formula also stated in Table III footnote | §III-F; Table III footnote | ✅ RESOLVED |
| R4-04 | "6.8× larger" implies mathematical proportionality across incompatible scales | Removed "6.8× larger" from Abstract, §V-C, §IX, and Fig. 24 caption; replaced with explicit statements that the comparison is qualitative, that the two metrics differ in scale and sample size, and that the finding indicates asymmetry rather than a precise ratio | Abstract; §V-C; Fig. 24 caption; §IX Conclusion | ✅ RESOLVED |
| R4-05 | Holm–Bonferroni thresholds not explicitly stated in §III-F | Added explicit adjusted thresholds (α/4, α/3, α/2, α) in §III-F paragraph on Holm–Bonferroni correction | §III-F | ✅ RESOLVED |
| R4-06 | McNemar's test rationale not stated — why not a chi-square test? | Added rationale in §III-F point 1: "McNemar's test is the appropriate paired test for comparing two classifiers on the same test set" | §III-F, test 1 | ✅ RESOLVED |
| R4-07 | Wilcoxon zero-method not documented | Added documentation of zero-method in §III-F test 2: "34,002 pairs with zero difference were excluded using the Wilcoxon zero-method" | §III-F, test 2 | ✅ RESOLVED |
| R4-08 | Add citations for foundational statistical methods (McNemar, Wilcoxon, Holm, bootstrap) | McNemar and Wilcoxon tests are cited via scipy [22] (the implementation library). Dedicated method citations (e.g., Holm 1979, Conover 1999) are not in the verified [1]–[23] reference list and require author action to add before LaTeX conversion. | §III-F; author action | ℹ️ AUTHOR ACTION — add foundational statistical method citations |

---

## Area Chair — Consolidated Actions

| # | Area Chair Requirement | Action Taken | Status |
|---|---|---|---|
| AC-01 | Integrate LIME R² caveat into §V-B Results (not only §VII-C) | Done — dedicated R² paragraph added to §V-B body | ✅ RESOLVED |
| AC-02 | Add power estimates for both Wilcoxon tests | Done — §III-F and §VII-A | ✅ RESOLVED |
| AC-03 | Specify rank-biserial r formula | Done — §III-F and Table III footnote | ✅ RESOLVED |
| AC-04 | Qualify 6.8× ratio as cross-metric order-of-magnitude comparison | Done — all instances replaced with qualitative language | ✅ RESOLVED |
| AC-05 | State 60-instance within-class selection criterion | Done — §IV expanded | ✅ RESOLVED |
| AC-06 | Add Worms-class caveat (n = 44) | Done — §V-A, Table I footnote, §VII-C | ✅ RESOLVED |
| AC-07 | Acknowledge UNSW-NB15 2015 temporal scope in §VII-B | Done — full paragraph added | ✅ RESOLVED |

---

## Summary

| Category | Total Comments | Resolved | Author Action | Noted (not blocking) |
|---|---|---|---|---|
| Reviewer 1 | 6 | 6 | 0 | 0 |
| Reviewer 2 | 5 | 4 | 0 | 1 |
| Reviewer 3 | 5 | 4 | 0 | 1 |
| Reviewer 4 | 8 | 7 | 1 | 0 |
| Area Chair | 7 | 7 | 0 | 0 |
| **TOTAL** | **31** | **28** | **1** | **2** |

**Outstanding author action:** Add citations for foundational statistical methods (McNemar, Wilcoxon, Holm–Bonferroni, bootstrap) before LaTeX conversion. These are not in the verified [1]–[23] reference list. Suggested additions: Holm (1979) for Bonferroni correction and a standard nonparametric statistics reference for Wilcoxon.

---

*End of reviewer_response_matrix.md | 2026-07-09*
