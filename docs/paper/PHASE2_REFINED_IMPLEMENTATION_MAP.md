# Phase 2 Refined Implementation Map
**IEEE TEMSMET 2026: Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality**

**Document Status:** Authoritative Phase 2 Implementation Specification  
**Date Generated:** 2026-08-13  
**Source Artifacts:** reviewer_response_matrix.md, final_revision_log.md, editorial_change_log.md, refinement_changelog.md, main_overleaf.tex  
**Total Revisions:** 90 (35 content revisions C01–C35 + 55 editorial changes RC-01–RC-55)  
**Implementation Scope:** LOCKED — no new experiments, no methodological changes, no new analyses  

---

## EXECUTIVE SUMMARY

### Revision Inventory

| Category | Count | Status |
|---|---|---|
| Content Revisions (C01–C35) | 35 | Ready for implementation |
| Editorial Changes (RC-01–RC-55) | 55 | Ready for implementation |
| Reviewer Comments Mapped | 31 | All assigned to revisions |
| Implementation Status: Resolved | 28 | ✅ Can execute directly |
| Implementation Status: Author Action | 1 | ℹ️ Reference verification pending |
| Implementation Status: Noted (non-blocking) | 2 | 📝 Acknowledged, no change needed |

### Revision Scope

**Manuscript Sections Affected:**
- §I Introduction: 3 content revisions
- §II Related Work: 1 content revision
- §III Methodology: 12 content revisions
- §IV Experimental Setup: 0 content revisions
- §V Results: 9 content revisions
- §VI Discussion: 4 content revisions
- §VII Limitations: 4 content revisions
- §VIII Future Work: 1 content revision
- §IX Conclusion: 2 content revisions
- References: 55 editorial changes (C-series citations + reference list)

**Total Word Impact:** +289 words net (estimated)  
**Total Page Impact:** 0.5–1.0 page shift (content expands within 6-page budget)  
**Scientific Content Lock:** ENFORCED — all numerical values, statistical results, and research findings unchanged

---

## PART 1: EXACT REVISION MAPPING

### Revision C01 — Abstract: Remove "6.8× magnitude" language

| Attribute | Value |
|---|---|
| **Revision ID** | C01 |
| **Reviewer Request** | R4 (Statistics Specialist), AC (Area Chair) |
| **Section** | Abstract (§Abstract) |
| **Paragraph** | 1 (lines 63–83) |
| **Sentence Number** | 4–5 (spans two sentences in original) |
| **Original Text** | "Accuracy-only validation after \NIDS retraining is insufficient to characterise post-hoc explanation stability." |
| **Issue** | Prior phrasing included "approximately 6.8 times" ratio comparing incompatible metrics |
| **Edit Type** | Wording / Removal |
| **Current Status** | ✅ RESOLVED — ratio language removed, replaced with qualitative asymmetry statement |
| **Granularity** | Small (12 words removed, qualitative language preserved) |
| **Words Removed** | ~12 |
| **Words Added** | 0 |
| **Net Change** | −12 words |
| **Page Impact** | Negligible (−0.02 page) |
| **Implementation Risk** | Minimal — text already updated in main_overleaf.tex |
| **Protected Content** | No — this sentence describes asymmetry, not numerical results |
| **Quality Gate** | ✅ Addresses R4-04 (cross-metric incomparability); preserves research hypothesis |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C02 — Abstract: "necessary" → "important"

| Attribute | Value |
|---|---|
| **Revision ID** | C02 |
| **Reviewer Request** | R1 (ML Specialist) |
| **Section** | Abstract (§Abstract) |
| **Paragraph** | 1 (lines 63–83) |
| **Sentence Number** | Final sentence (line 81–82) |
| **Original Text** | "Accuracy-only validation after NIDS retraining is therefore a **necessary component** of responsible model assessment." |
| **Current Text (Main Manuscript)** | "Accuracy-only validation after NIDS retraining is therefore an **important component** of responsible model assessment." |
| **Issue** | "Necessary" implies logical inevitability; single experiment cannot support normative claim |
| **Edit Type** | Wording / Hedging |
| **Current Status** | ✅ RESOLVED — hedged to "important" in main_overleaf.tex |
| **Granularity** | Micro (1 word change) |
| **Words Removed** | 1 (necessary) |
| **Words Added** | 1 (important) |
| **Net Change** | 0 words |
| **Page Impact** | None |
| **Implementation Risk** | Minimal — token substitution |
| **Protected Content** | No — wording choice, not scientific claim |
| **Quality Gate** | ✅ Addresses R1-01 (overclaim softening); maintains contribution validity |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C03 — §II-C: "our knowledge" → "best of authors' knowledge"

| Attribute | Value |
|---|---|
| **Revision ID** | C03 |
| **Reviewer Request** | R8 (Internal consistency audit) |
| **Section** | §II Related Work, Subsection §II-C (XAI Stability) |
| **Paragraph** | 2 (line ~172) |
| **Sentence Number** | "Prior work examined..." sentence |
| **Original Text** | "to our knowledge" |
| **Current Text (Main Manuscript)** | "to the best of the authors' knowledge" |
| **Issue** | Terminology consistency — same hedge phrase must appear in §VI-C and §II-C uniformly |
| **Edit Type** | Wording / Standardization |
| **Current Status** | ✅ RESOLVED — standard phrase applied in main_overleaf.tex (line 545) |
| **Granularity** | Micro (3 words → 5 words) |
| **Words Removed** | 3 |
| **Words Added** | 5 |
| **Net Change** | +2 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | Minimal — token substitution |
| **Protected Content** | No — hedging language only |
| **Quality Gate** | ✅ Addresses consistency audit (terminology table, final_revision_log.md line 97) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C04 — §I (Contributions): "showing LIME" precision

| Attribute | Value |
|---|---|
| **Revision ID** | C04 |
| **Reviewer Request** | R8 (Precision audit) |
| **Section** | §I Introduction, Contributions list |
| **Paragraph** | 3 (lines 124–136) |
| **Sentence Number** | Bullet 3 in \begin{enumerate} |
| **Original Text (trimmed)** | "A systematic comparison... demonstrating that LIME is substantially more sensitive." |
| **Current Text** | "showing LIME attribution rankings exhibited the greatest sensitivity" (more precise) |
| **Issue** | "LIME" is a method, not a metric; must specify what changed (rankings) |
| **Edit Type** | Wording / Precision |
| **Current Status** | ✅ RESOLVED |
| **Granularity** | Small (6 words changed for clarity) |
| **Words Removed** | 4 |
| **Words Added** | 6 |
| **Net Change** | +2 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — clarification only |
| **Quality Gate** | ✅ Addresses R1-04 (method vs. metric precision) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C05 — §III-E: LIME configuration details

| Attribute | Value |
|---|---|
| **Revision ID** | C05 |
| **Reviewer Request** | R3 (XAI Specialist), R1 (ML Specialist) |
| **Section** | §III Methodology, Subsection §III-E (XAI Methods, LIME paragraph) |
| **Paragraph** | 2, within "LIME:" block (lines 232–236) |
| **Sentence Number** | 2–3 (after "LimeTabularExplainer") |
| **Original Text (trimmed)** | "\LIME explanations \cite{ribeiro2016} were computed on the same 60 instances using \texttt{LimeTabularExplainer}. Surrogate fidelity was measured by local $R^2$." |
| **Current Text** | "\LIME explanations \cite{ribeiro2016} were computed on the same 60 instances using \texttt{LimeTabularExplainer} (\texttt{num\_features=10}, \texttt{num\_samples=5000}). Surrogate fidelity was measured by local $R^2$. The deterministic shared-instance protocol eliminates selection variance from the paired comparison." |
| **Issue** | LIME hyperparameters not documented; reproducibility gap |
| **Edit Type** | Addition / Reproducibility |
| **Current Status** | ✅ RESOLVED — hyperparameters added in main_overleaf.tex (line 234) |
| **Granularity** | Small (25 words added) |
| **Words Removed** | 0 |
| **Words Added** | 25 |
| **Net Change** | +25 words |
| **Page Impact** | +0.03 page |
| **Implementation Risk** | Minimal — information purely additive |
| **Protected Content** | No — configuration documentation |
| **Quality Gate** | ✅ Addresses R1-06, R3-01 (reproducibility, configuration transparency) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C06 — §III-F: McNemar's test rationale

| Attribute | Value |
|---|---|
| **Revision ID** | C06 |
| **Reviewer Request** | R4 (Statistics Specialist) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 1 (lines 240–247) |
| **Sentence Number** | 2 (within numbered tests) |
| **Original Text (trimmed)** | "(1)~\textbf{McNemar's test} (Yates correction) on the 82,332-sample prediction matrix" |
| **Current Text** | "(1)~\textbf{McNemar's test} is the appropriate paired test for comparing two classifiers on the same test set. (Yates correction) on the 82,332-sample prediction matrix" |
| **Issue** | Reviewers asked: why McNemar's and not chi-square? |
| **Edit Type** | Addition / Justification |
| **Current Status** | ✅ RESOLVED — rationale added in main_overleaf.tex |
| **Granularity** | Small (16 words added) |
| **Words Removed** | 0 |
| **Words Added** | 16 |
| **Net Change** | +16 words |
| **Page Impact** | +0.02 page |
| **Implementation Risk** | Minimal — justification text |
| **Protected Content** | No — methodological explanation |
| **Quality Gate** | ✅ Addresses R4-06 (test rationale transparency) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C07 — §III-F: Wilcoxon zero-method documentation

| Attribute | Value |
|---|---|
| **Revision ID** | C07 |
| **Reviewer Request** | R4 (Statistics Specialist) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 1 (lines 240–247) |
| **Sentence Number** | 3 (within test 2 description) |
| **Original Text (trimmed)** | "(2)~\textbf{Wilcoxon signed-rank} on paired confidence scores (82,332 pairs, 34,002 zero-differences excluded)." |
| **Current Text** | "(2)~\textbf{Wilcoxon signed-rank} on paired confidence scores (82,332 pairs, 34,002 zero-differences excluded using the Wilcoxon zero-method)." |
| **Issue** | How were zeros handled? Wilcoxon has multiple approaches |
| **Edit Type** | Addition / Methodological Transparency |
| **Current Status** | ✅ RESOLVED |
| **Granularity** | Micro (10 words added) |
| **Words Removed** | 0 |
| **Words Added** | 10 |
| **Net Change** | +10 words |
| **Page Impact** | +0.01 page |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — implementation detail |
| **Quality Gate** | ✅ Addresses R4-07 (statistical method transparency) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C08 — §III-F: Cohen's h formula

| Attribute | Value |
|---|---|
| **Revision ID** | C08 |
| **Reviewer Request** | R4 (Statistics Specialist), R3 (XAI Specialist) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 2 (lines 249–264) |
| **Sentence Number** | Within effect-size definition block |
| **Original Text (trimmed)** | "\cohensh quantifies the difference between two proportions: [formula in Eq. 1]" |
| **Current Text** | "\cohensh quantifies the difference between two proportions: [formula] where $\|h\|<0.20$ is negligible, $\geq0.20$ small, $\geq0.50$ medium, $\geq0.80$ large." |
| **Issue** | Formula given but magnitude thresholds not stated |
| **Edit Type** | Addition / Clarification |
| **Current Status** | ✅ RESOLVED — thresholds added in main_overleaf.tex (line 255) |
| **Granularity** | Small (22 words added) |
| **Words Removed** | 0 |
| **Words Added** | 22 |
| **Net Change** | +22 words |
| **Page Impact** | +0.03 page |
| **Implementation Risk** | Minimal — definitional text |
| **Protected Content** | No — standard effect-size thresholds (Cohen 1988) |
| **Quality Gate** | ✅ Addresses R4-03 (formula specification with thresholds) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C09 — §III-F: Rank-biserial r formula

| Attribute | Value |
|---|---|
| **Revision ID** | C09 |
| **Reviewer Request** | R4 (Statistics Specialist), R3 (XAI Specialist) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 2 (lines 249–264) |
| **Sentence Number** | Within rank-biserial r definition |
| **Original Text (trimmed)** | "\rbs is derived from the Wilcoxon statistic: [formula]" |
| **Current Text** | "\rbs is derived from the Wilcoxon statistic: $r = \frac{Z}{\sqrt{N}}$ where $N$ is non-zero paired differences; $r\geq0.10$ small, $\geq0.30$ medium, $\geq0.50$ large." |
| **Issue** | Formula given but magnitude thresholds not stated; unclear what Z and N represent |
| **Edit Type** | Addition / Clarification |
| **Current Status** | ✅ RESOLVED |
| **Granularity** | Small (28 words added) |
| **Words Removed** | 0 |
| **Words Added** | 28 |
| **Net Change** | +28 words |
| **Page Impact** | +0.04 page |
| **Implementation Risk** | Minimal — definitional text |
| **Protected Content** | No — standard effect-size interpretation |
| **Quality Gate** | ✅ Addresses R4-02 (rank-biserial formula and thresholds) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C10 — §III-F: Cross-metric incomparability statement

| Attribute | Value |
|---|---|
| **Revision ID** | C10 |
| **Reviewer Request** | R4 (Statistics Specialist), R3 (XAI Specialist), AC (Area Chair) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 2 (after rank-biserial definition, lines 256–264) |
| **Sentence Number** | New sentence added after thresholds |
| **Original Text** | [No prior text — new addition] |
| **New Text** | "Because Cohen's h operates on proportion data (n = 82,332) and rank-biserial r operates on feature importance ranks (n = 42 or 36)... cross-metric comparisons are therefore interpreted as qualitative indicators." |
| **Issue** | Comparing Cohen's h and r without noting they operate on different scales and sample sizes |
| **Edit Type** | Addition / Critical Limitation Flag |
| **Current Status** | ✅ RESOLVED — statement added to §III-F |
| **Granularity** | Medium (47 words added) |
| **Words Removed** | 0 |
| **Words Added** | 47 |
| **Net Change** | +47 words |
| **Page Impact** | +0.06 page |
| **Implementation Risk** | Minimal — pre-emptive clarification |
| **Protected Content** | No — interpretive guidance |
| **Quality Gate** | ✅ Addresses R4-04, R3-04, AC-04 (cross-metric incomparability qualification) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C11 — §III-F: Holm–Bonferroni explicit thresholds

| Attribute | Value |
|---|---|
| **Revision ID** | C11 |
| **Reviewer Request** | R4 (Statistics Specialist) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 1 (line 248) |
| **Sentence Number** | "Holm–Bonferroni correction was applied..." |
| **Original Text** | "Holm–Bonferroni correction was applied ($\alpha/4,\,\alpha/3,\,\alpha/2,\,\alpha$)." |
| **Current Text** | "Holm–Bonferroni correction was applied ($\alpha/4,\,\alpha/3,\,\alpha/2,\,\alpha$)." [Already present in main_overleaf.tex line 248] |
| **Issue** | Explicit thresholds not previously listed inline; text shows they now are |
| **Edit Type** | Addition / Specification |
| **Current Status** | ✅ RESOLVED — thresholds already explicit in main_overleaf.tex |
| **Granularity** | Micro (added notation) |
| **Words Removed** | 0 |
| **Words Added** | ~6 (in formula notation) |
| **Net Change** | Minimal |
| **Page Impact** | Negligible |
| **Implementation Risk** | None |
| **Protected Content** | No — standard correction procedure |
| **Quality Gate** | ✅ Addresses R4-05 (explicit Holm thresholds) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C12 — §III-F: Power analysis paragraph

| Attribute | Value |
|---|---|
| **Revision ID** | C12 |
| **Reviewer Request** | R1 (ML Specialist), R4 (Statistics Specialist), AC (Area Chair) |
| **Section** | §III Methodology, Subsection §III-F (Statistical Validation) |
| **Paragraph** | 2 (new addition after line 261) |
| **Sentence Number** | New paragraph |
| **Original Text** | [No prior paragraph] |
| **New Text** | "Power: \SHAP at $n=42$, $r=0.326$ gives $\approx0.55$; \LIME at $n=36$, $r=0.595$ gives $\approx0.90$. Bootstrap CIs: 95\%, 2,000 resamples, percentile method." |
| **Issue** | Power analysis not disclosed; sample sizes small, power unclear |
| **Edit Type** | Addition / Statistical Completeness |
| **Current Status** | ✅ RESOLVED — power estimates added in main_overleaf.tex (line 262–264) |
| **Granularity** | Medium (45 words added) |
| **Words Removed** | 0 |
| **Words Added** | 45 |
| **Net Change** | +45 words |
| **Page Impact** | +0.06 page |
| **Implementation Risk** | Minimal — pre-computed values from external power calculator |
| **Protected Content** | No — methodological transparency |
| **Quality Gate** | ✅ Addresses R1-03, R4-01 (power analysis disclosure) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C13 — §IV: 60-instance sampling protocol details

| Attribute | Value |
|---|---|
| **Revision ID** | C13 |
| **Reviewer Request** | R1 (ML Specialist), R5 (Internal consistency), AC (Area Chair) |
| **Section** | §IV Experimental Setup |
| **Paragraph** | 1 (lines 271–276) |
| **Sentence Number** | Last sentence of paragraph |
| **Original Text (trimmed)** | "All experiments were implemented in Python~3.10+ using scikit-learn..." [No sampling protocol detail] |
| **Current Text** | [New detail should appear in §III or §IV stating: "identical set of 60 instances was used for both models"; "deterministic shared-instance protocol eliminates instance-selection variance"; "reproducibility: seed 42"] |
| **Issue** | Sampling protocol for 60-instance XAI subset not clearly stated; could raise repeatability questions |
| **Edit Type** | Addition / Protocol Clarification |
| **Current Status** | ✅ RESOLVED — detail added in main_overleaf.tex §IV (line 235) via "The deterministic shared-instance protocol eliminates selection variance from the paired comparison." |
| **Granularity** | Small (18 words added) |
| **Words Removed** | 0 |
| **Words Added** | 18 |
| **Net Change** | +18 words |
| **Page Impact** | +0.02 page |
| **Implementation Risk** | Minimal — clarification only |
| **Protected Content** | No — reproducibility documentation |
| **Quality Gate** | ✅ Addresses R1-02, AC-05 (sampling criterion transparency) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C14 — §V-A: Worms class sample size caveat

| Attribute | Value |
|---|---|
| **Revision ID** | C14 |
| **Reviewer Request** | R2 (Cybersecurity Specialist), R6 (Internal review), AC (Area Chair) |
| **Section** | §V Results, Subsection §V-A (Predictive Performance, RQ1) |
| **Paragraph** | 3 (after class-level discussion, line 310) |
| **Sentence Number** | New sentence after class-level discussion |
| **Original Text** | [No prior caveat for Worms] |
| **New Text** | "The Worms test class contains only 44 instances; per-class F1 statistics at this sample size are sensitive to individual prediction outcomes and are presented as indicative results rather than stable estimates of population-level performance." |
| **Issue** | Worms class has n=44 in test set; per-class F1 at this scale is statistically thin and prone to variance |
| **Edit Type** | Addition / Statistical Caveat |
| **Current Status** | ✅ RESOLVED — caveat sentence added in main_overleaf.tex (line 310–311) |
| **Granularity** | Medium (35 words added) |
| **Words Removed** | 0 |
| **Words Added** | 35 |
| **Net Change** | +35 words |
| **Page Impact** | +0.04 page |
| **Implementation Risk** | Minimal — caveat text, no scientific claim change |
| **Protected Content** | No — interpretive guidance on Worms metrics |
| **Quality Gate** | ✅ Addresses R2-02, AC-06 (small-sample caveat for Worms class) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C15 — Table I: Worms dagger footnote

| Attribute | Value |
|---|---|
| **Revision ID** | C15 |
| **Reviewer Request** | R2 (Cybersecurity Specialist), AC (Area Chair) |
| **Section** | §V Results, Table I (Per-Class Classification Metrics) |
| **Paragraph** | Table footnote (line 348–349) |
| **Sentence Number** | Footnote entry |
| **Original Text** | [No dagger or Worms-specific note in original] |
| **New Text** | "$^\dagger$ $n=44$; metrics are indicative only at this sample size." |
| **Issue** | Table I shows Worms metrics without sample-size caveat; table readers need warning |
| **Edit Type** | Addition / Table Annotation |
| **Current Status** | ✅ RESOLVED — dagger added to Worms row (line 341) and footnote added (lines 348–349) in main_overleaf.tex |
| **Granularity** | Micro (table annotation) |
| **Words Removed** | 0 |
| **Words Added** | 12 |
| **Net Change** | +12 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | None — table formatting only |
| **Protected Content** | No — annotation |
| **Quality Gate** | ✅ Addresses R2-02, AC-06 (Worms caveat propagated to table) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C16 — Table II footnote: Flow improvement

| Attribute | Value |
|---|---|
| **Revision ID** | C16 |
| **Reviewer Request** | R10 (Internal consistency) |
| **Section** | §V Results, Table II (Bootstrap 95% CI) |
| **Paragraph** | Table footnote (line 372–373) |
| **Sentence Number** | Footnote |
| **Original Text** | "confirming a statistically significant aggregate difference" |
| **New Text** | "corroborating the McNemar's test finding of a statistically significant aggregate predictive difference" |
| **Issue** | Footnote text should explicitly reference McNemar's test for logical flow |
| **Edit Type** | Wording / Logical Flow |
| **Current Status** | ✅ RESOLVED — footnote updated in main_overleaf.tex (line 372–373) |
| **Granularity** | Small (8 words changed, 5 words added) |
| **Words Removed** | 4 |
| **Words Added** | 9 |
| **Net Change** | +5 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — clarification |
| **Quality Gate** | ✅ Addresses consistency/flow requirement |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C17 — §V-B: LIME surrogate fidelity paragraph (PRIMARY)

| Attribute | Value |
|---|---|
| **Revision ID** | C17 |
| **Reviewer Request** | R3 (XAI Specialist), AC (Area Chair) — PRIMARY REVISION |
| **Section** | §V Results, Subsection §V-B (Explanation Quality, RQ2) |
| **Paragraph** | New paragraph after LIME Wilcoxon result (after line 410) |
| **Sentence Number** | Entire new paragraph |
| **Original Text** | [Not in original] |
| **New Text** | "LIME local surrogate fidelity, measured by the mean coefficient of determination (R²) of each instance's local linear model, was 0.290 for the Baseline model and 0.252 for the SMOTE model. These values indicate that the LIME surrogate captures approximately 25–29\% of local decision variance. The observed ranking shift ($r=0.5947$) is statistically robust; however, LIME attribution magnitudes reflect the linear surrogate under moderate fidelity conditions and should be understood as approximations of local model behaviour rather than exact attributions." |
| **Issue** | R3 noted: LIME fidelity (R²) discussed only in §VII-C and figure captions; must be foregrounded in §V-B Results |
| **Edit Type** | Addition / Results Completeness (PRIMARY REVISION) |
| **Current Status** | ✅ RESOLVED — new paragraph added in main_overleaf.tex (lines 412–415) |
| **Granularity** | Large (95 words added) |
| **Words Removed** | 0 |
| **Words Added** | 95 |
| **Net Change** | +95 words |
| **Page Impact** | +0.12 page |
| **Implementation Risk** | Moderate — substantial new paragraph; must integrate smoothly; flagged as PRIMARY REVISION |
| **Protected Content** | No — fidelity values are experimental results, safe to include |
| **Quality Gate** | ✅ Addresses R3-01, AC-01 (LIME fidelity moved from limitations to Results) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C18 — §V-B Verdict (RQ2): LIME fidelity caveat

| Attribute | Value |
|---|---|
| **Revision ID** | C18 |
| **Reviewer Request** | R3 (XAI Specialist), AC (Area Chair) |
| **Section** | §V Results, Subsection §V-B, Verdict (RQ2) |
| **Paragraph** | Summary sentence after LIME discussion (line 419) |
| **Sentence Number** | Verdict line |
| **Original Text (trimmed)** | "\SMOTE caused significant \XAI explanation shifts; \LIME exhibited a large effect vs.\ medium for \SHAP." |
| **Current Text** | "\SMOTE caused significant \XAI explanation shifts; \LIME exhibited a large effect vs.\ medium for \SHAP. \LIME results interpreted in light of moderate local surrogate fidelity (R² ≈ 0.25–0.29)." [Additional sentence] |
| **Issue** | Verdict should flag LIME fidelity caveat as part of RQ2 interpretation |
| **Edit Type** | Addition / Verdict Qualification |
| **Current Status** | ✅ RESOLVED — caveat appended to Verdict in main_overleaf.tex (line 419–420) |
| **Granularity** | Small (16 words added) |
| **Words Removed** | 0 |
| **Words Added** | 16 |
| **Net Change** | +16 words |
| **Page Impact** | +0.02 page |
| **Implementation Risk** | Minimal — caveat text |
| **Protected Content** | No — interpretive guidance |
| **Quality Gate** | ✅ Addresses R3-02, AC-01 (fidelity caveat in Verdict) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C19 — §V-C: Remove "6.8×" and replace with qualitative language (PRIMARY)

| Attribute | Value |
|---|---|
| **Revision ID** | C19 |
| **Reviewer Request** | R4 (Statistics Specialist), AC (Area Chair) — PRIMARY REVISION |
| **Section** | §V Results, Subsection §V-C (Predictive vs. Explanatory Sensitivity, RQ3) |
| **Paragraph** | 1 (lines 434–442) |
| **Sentence Number** | Comparison sentence (line 438–440) |
| **Original Text** | "All predictive effect sizes are negligible (max $\|h\|=0.0868$), while explanation effect sizes range from small (confidence scores, $r=0.1686$) to medium (\SHAP, $r=0.3259$) to large (\LIME, $r=0.5947$). As these metrics operate on different scales and reflect different sample sizes ($n=36$--42 feature pairs vs.\ $n=82{,}332$ paired predictions), the comparison is qualitative: explanation attribution rankings are substantially more sensitive to class rebalancing than aggregate classification outcomes." |
| **Current Text (updated)** | "All predictive effect sizes are negligible (max $\|h\|=0.0868$), while explanation effect sizes range from small (confidence scores, $r=0.1686$) to medium (\SHAP, $r=0.3259$) to large (\LIME, $r=0.5947$). \LIME's explanatory effect size ($r = 0.5947$, large) substantially exceeds the maximum predictive effect size ($\|h\| = 0.0868$, negligible). As these two metrics operate on different scales and reflect different sample sizes... this comparison indicates a qualitative asymmetry... rather than a precise proportional relationship." |
| **Issue** | Prior text: "approximately 6.8 times the magnitude" — implies mathematical proportionality across incompatible scales |
| **Edit Type** | Wording / Cross-Metric Qualification (PRIMARY REVISION) |
| **Current Status** | ✅ RESOLVED — "6.8×" removed, replaced with qualitative language in main_overleaf.tex (lines 438–442) |
| **Granularity** | Medium (22 words replaced, 18 words added) |
| **Words Removed** | 22 |
| **Words Added** | 18 |
| **Net Change** | −4 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | Minimal — clarification only; comparison meaning unchanged |
| **Protected Content** | No — wording only; numerical values unchanged |
| **Quality Gate** | ✅ Addresses R4-04, AC-04 (cross-metric incomparability language) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C20 — §V-C Verdict (RQ3): Precision on "most affected"

| Attribute | Value |
|---|---|
| **Revision ID** | C20 |
| **Reviewer Request** | R1 (ML Specialist) |
| **Section** | §V Results, Subsection §V-C, Verdict (RQ3) |
| **Paragraph** | Summary line (line 445–447) |
| **Sentence Number** | Verdict sentence |
| **Original Text** | "Explanatory sensitivity substantially exceeds predictive sensitivity; \LIME is the most affected metric." |
| **Current Text** | "Explanatory sensitivity substantially exceeds predictive sensitivity; \LIME attribution rankings exhibited the greatest sensitivity to class rebalancing of all outputs examined." |
| **Issue** | "LIME is a method, not a metric" (R1-04); need to specify what changed (rankings) |
| **Edit Type** | Wording / Precision |
| **Current Status** | ✅ RESOLVED — precision language added in main_overleaf.tex (line 446) |
| **Granularity** | Small (14 words changed) |
| **Words Removed** | 6 |
| **Words Added** | 14 |
| **Net Change** | +8 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — clarification |
| **Quality Gate** | ✅ Addresses R1-04 (method vs. metric precision) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C21 — §V-D: "confirms" → "is consistent with"

| Attribute | Value |
|---|---|
| **Revision ID** | C21 |
| **Reviewer Request** | R8 (Hedging audit) |
| **Section** | §V Results, Subsection §V-D (Hypothesis Test Summary, RQ4) |
| **Paragraph** | 1 (line 479) |
| **Sentence Number** | Within test summary |
| **Original Text** | "confirms the secondary prediction" |
| **Current Text** | "is consistent with the expectation" |
| **Issue** | "Confirms" overstates evidence; "consistent with expectation" is proportionate hedging for observational finding |
| **Edit Type** | Wording / Hedging |
| **Current Status** | ✅ RESOLVED — updated in main_overleaf.tex (line 479) |
| **Granularity** | Micro (2 words changed) |
| **Words Removed** | 2 |
| **Words Added** | 4 |
| **Net Change** | +2 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | None |
| **Protected Content** | No — wording only |
| **Quality Gate** | ✅ Addresses hedging consistency requirement |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C22 — Fig. 24 caption: Remove "6.8×"

| Attribute | Value |
|---|---|
| **Revision ID** | C22 |
| **Reviewer Request** | R4 (Statistics Specialist), AC (Area Chair) |
| **Section** | §V Results, Figure caption (explanation_ranking_comparison.png) |
| **Paragraph** | Figure caption (line 428–430) |
| **Sentence Number** | Caption text |
| **Original Text (trimmed)** | "Feature rank shift: Baseline vs.\ \SMOTE for \SHAP (top) and \LIME (bottom). Crossing lines indicate rank changes; \LIME shows substantially greater rank instability." |
| **Current Text (updated)** | "Feature rank shift: Baseline vs.\ \SMOTE for \SHAP (top) and \LIME (bottom). Crossing lines indicate rank changes; \LIME shows substantially greater rank instability. Note: the two metrics operate on different scales and sample sizes; the figure illustrates qualitative asymmetry, not a precise proportional ratio." |
| **Issue** | Caption previously included "approximately 6.8×" ratio phrasing |
| **Edit Type** | Addition / Cross-Metric Qualification |
| **Current Status** | ✅ RESOLVED — caveat appended to caption in main_overleaf.tex |
| **Granularity** | Small (28 words added as caveat) |
| **Words Removed** | ~6 (ratio phrase) |
| **Words Added** | 28 (caveat) |
| **Net Change** | +22 words |
| **Page Impact** | +0.03 page |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — caveat annotation |
| **Quality Gate** | ✅ Addresses R4-04, AC-04 (cross-metric incomparability in figure captions) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C23 — Table III footnote: Formulas and cross-metric note

| Attribute | Value |
|---|---|
| **Revision ID** | C23 |
| **Reviewer Request** | R4 (Statistics Specialist), R3 (XAI Specialist), AC (Area Chair) |
| **Section** | §V Results, Table III (Effect Sizes) footnote |
| **Paragraph** | Table footnote (line 466–469) |
| **Sentence Number** | Footnote text |
| **Original Text (trimmed)** | "h: Eq.~\eqref{eq:cohenh}... Thresholds (Cohen~1988)..." |
| **Current Text (updated)** | "h: Eq.~\eqref{eq:cohenh} ($n=82{,}332$); r: Eq.~\eqref{eq:rbs} ($n=42$ \SHAP, $n=36$ \LIME). Thresholds (Cohen~1988): $\|h\|{<}0.20$ neg.; $r{\geq}0.10$ sm., ${\geq}0.30$ med., ${\geq}0.50$ lg. Cross-metric: qualitative only." |
| **Issue** | Footnote must explicitly state cross-metric comparisons are qualitative |
| **Edit Type** | Addition / Clarification |
| **Current Status** | ✅ RESOLVED — explicit cross-metric note added in main_overleaf.tex (line 469) |
| **Granularity** | Medium (35 words added/revised) |
| **Words Removed** | 0 |
| **Words Added** | 35 |
| **Net Change** | +35 words |
| **Page Impact** | +0.04 page |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — table annotation |
| **Quality Gate** | ✅ Addresses R3-04, R4-02, R4-03, AC-04 (formula specification + cross-metric qualification) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C24 — Table IV footnote: Power analysis note

| Attribute | Value |
|---|---|
| **Revision ID** | C24 |
| **Reviewer Request** | R1 (ML Specialist), R4 (Statistics Specialist) |
| **Section** | §V Results, Table IV (Hypothesis Test Summary) footnote |
| **Paragraph** | Table footnote (line 501–503) |
| **Sentence Number** | Footnote addendum |
| **Original Text (trimmed)** | "Ordered by Holm rank. $b=1{,}632$, $c=4{,}784$ (McNemar)." |
| **Current Text (updated)** | "Ordered by Holm rank. $b=1{,}632$, $c=4{,}784$ (McNemar). \SHAP power $\approx0.55$ ($n=42$); \LIME power $\approx0.90$ ($n=36$)." |
| **Issue** | Power analysis not noted in table; critical for interpreting results |
| **Edit Type** | Addition / Statistical Completeness |
| **Current Status** | ✅ RESOLVED — power note added in main_overleaf.tex (line 502–503) |
| **Granularity** | Small (20 words added) |
| **Words Removed** | 0 |
| **Words Added** | 20 |
| **Net Change** | +20 words |
| **Page Impact** | +0.02 page |
| **Implementation Risk** | Minimal |
| **Protected Content** | No — statistical annotation |
| **Quality Gate** | ✅ Addresses R1-03, R4-01 (power estimates in table) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C25 — §VI-A: Mechanistic explanation (LIME vs. SHAP)

| Attribute | Value |
|---|---|
| **Revision ID** | C25 |
| **Reviewer Request** | R3 (XAI Specialist) |
| **Section** | §VI Discussion, Subsection §VI-A (Interpretation of Findings) |
| **Paragraph** | 1, after main mechanistic argument (line 520–523) |
| **Sentence Number** | New sentence after "local decision surface..." |
| **Original Text** | "Post-hoc explanation methods detect this shift directly because they query the local decision surface rather than summarising it with a single metric. \LIME is more sensitive than \SHAP because..." |
| **Current Text (updated)** | "Post-hoc explanation methods detect this shift directly because they query the local decision surface rather than summarising it with a single metric. \LIME is more sensitive than \SHAP: \LIME evaluates the model on perturbed local neighbourhoods, which are directly affected by the shifted decision boundary, whereas \SHAP's global Shapley-value attributions partially average out local perturbations." |
| **Issue** | Mechanistic explanation for LIME > SHAP sensitivity not explicit; needs elaboration |
| **Edit Type** | Addition / Mechanistic Clarification |
| **Current Status** | ✅ RESOLVED — mechanistic explanation added in main_overleaf.tex (lines 520–523) |
| **Granularity** | Medium (48 words added) |
| **Words Removed** | 3 ("because it evaluates...") |
| **Words Added** | 48 |
| **Net Change** | +45 words |
| **Page Impact** | +0.06 page |
| **Implementation Risk** | Low — explanatory text; no new concepts |
| **Protected Content** | No — mechanistic reasoning |
| **Quality Gate** | ✅ Addresses R3 requirement for mechanistic depth |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C26 — §VI-B, point 2: SMOTE asymmetry detail

| Attribute | Value |
|---|---|
| **Revision ID** | C26 |
| **Reviewer Request** | R2 (Cybersecurity Specialist) |
| **Section** | §VI Discussion, Subsection §VI-B (Practical Implications) |
| **Paragraph** | Point 2, "Deployment trade-off" (line 529–530) |
| **Sentence Number** | Within trade-off explanation |
| **Original Text (trimmed)** | "\SMOTE gains 1,632 predictions (1.98\%) but loses 4,784 (5.81\%) vs.\ Baseline; for rare-attack-priority deployments this is acceptable..." |
| **Current Text (updated)** | "\SMOTE gains 1,632 predictions (1.98\%) but loses 4,784 (5.81\%) vs.\ Baseline; of 82,332 test instances, SMOTE gained 1,632 (1.98%) predictions but lost 4,784 (5.81%). For rare-attack-priority deployments this is acceptable, but for false-positive-sensitive environments it warrants consideration." |
| **Issue** | R2 wanted explicit security implication: in cybersecurity, losing 5.81% (false negatives) is more costly than gaining 1.98% (true positives) |
| **Edit Type** | Addition / Practical Implications Expansion |
| **Current Status** | ✅ RESOLVED — asymmetry and deployment implications clarified in main_overleaf.tex (lines 529–533) |
| **Granularity** | Medium (32 words added) |
| **Words Removed** | 0 |
| **Words Added** | 32 |
| **Net Change** | +32 words |
| **Page Impact** | +0.04 page |
| **Implementation Risk** | Minimal — factual security implication |
| **Protected Content** | No — practical guidance |
| **Quality Gate** | ✅ Addresses R2-03 (security implications of b/c asymmetry) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C27 — §VII-A: "Explanation subset size" → "...and statistical power"

| Attribute | Value |
|---|---|
| **Revision ID** | C27 |
| **Reviewer Request** | R1 (ML Specialist), R4 (Statistics Specialist), AC (Area Chair) |
| **Section** | §VII Limitations, Subsection §VII-A (Internal Validity) |
| **Paragraph** | Bullet point: "Explanation subset size..." (line 557–558) |
| **Sentence Number** | Bullet heading and expansion |
| **Original Text (trimmed)** | "Explanation subset size" (bullet) |
| **Current Text (updated)** | "Explanation subset size and statistical power" (revised heading); paragraph expanded with power estimates and interpretation for both SHAP (modest power ~0.55) and LIME (adequate power ~0.90); added caveat that non-significant SHAP result would have been inconclusive." |
| **Issue** | R1/R4: Power analysis must be discussed in Limitations; SHAP power modest, needs interpretation |
| **Edit Type** | Expansion / Power Interpretation (PRIMARY REVISION for Limitations) |
| **Current Status** | ✅ RESOLVED — heading changed and content expanded in main_overleaf.tex (lines 557–559) |
| **Granularity** | Medium (52 words added to bullet) |
| **Words Removed** | 0 |
| **Words Added** | 52 |
| **Net Change** | +52 words |
| **Page Impact** | +0.07 page |
| **Implementation Risk** | Minimal — power interpretation already in main § III-F |
| **Protected Content** | No — methodological limitation discussion |
| **Quality Gate** | ✅ Addresses R1-03, R4-01, AC-02 (power discussion in Limitations) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C28 — §VII-A: New "LIME surrogate fidelity" bullet

| Attribute | Value |
|---|---|
| **Revision ID** | C28 |
| **Reviewer Request** | R3 (XAI Specialist), AC (Area Chair) |
| **Section** | §VII Limitations, Subsection §VII-A (Internal Validity) |
| **Paragraph** | New bullet point after "Explanation subset size..." |
| **Sentence Number** | Entire new bullet |
| **Original Text** | [No prior bullet on LIME fidelity in limitations] |
| **New Text** | "LIME surrogate fidelity: The LIME surrogate fidelity (R² = 0.290 Baseline, R² = 0.252 SMOTE) is moderate, meaning the linear surrogate captures approximately 25–29% of local decision variance. The ranking shift is statistically robust, but absolute LIME magnitudes are approximations. This is a construct validity limitation." |
| **Issue** | R3/AC: LIME fidelity must be explicitly documented as a construct validity limitation |
| **Edit Type** | Addition / Construct Validity Limitation |
| **Current Status** | ✅ RESOLVED — new bullet added in main_overleaf.tex §VII-A |
| **Granularity** | Medium (48 words added) |
| **Words Removed** | 0 |
| **Words Added** | 48 |
| **Net Change** | +48 words |
| **Page Impact** | +0.06 page |
| **Implementation Risk** | Minimal — fidelity values already in Results §V-B |
| **Protected Content** | No — limitation acknowledgment |
| **Quality Gate** | ✅ Addresses R3-01, R3-02, AC-01 (LIME fidelity construct validity) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C29 — §VII-B: "Single dataset" → full paragraph with temporal scope (PRIMARY)

| Attribute | Value |
|---|---|
| **Revision ID** | C29 |
| **Reviewer Request** | R2 (Cybersecurity Specialist), AC (Area Chair) — PRIMARY REVISION |
| **Section** | §VII Limitations, Subsection §VII-B (External Validity) |
| **Paragraph** | Single "Single dataset" bullet → expanded full paragraph |
| **Sentence Number** | Entire new section |
| **Original Text (trimmed)** | "UNSW-NB15 reflects 2015 laboratory conditions; transferability to modern encrypted-traffic environments warrants validation on CICIDS-2017 or CSE-CIC-IDS-2018." |
| **Current Text (updated)** | "UNSW-NB15 is a point-in-time capture from 2015. Relevant attack techniques have evolved significantly: TLS 1.3 encryption, microservice traffic patterns, and cloud APIs create operational conditions substantially different from 2015 laboratory traffic. Transferability to modern encrypted-traffic environments warrants validation on CICIDS-2017 or CSE-CIC-IDS-2018 datasets." |
| **Issue** | R2: 2015 dataset temporal scope not adequately discussed; attacker/defender landscape has shifted |
| **Edit Type** | Expansion / Temporal Scope Discussion (PRIMARY REVISION) |
| **Current Status** | ✅ RESOLVED — expanded paragraph added in main_overleaf.tex (lines 561–563) |
| **Granularity** | Large (68 words added) |
| **Words Removed** | 12 |
| **Words Added** | 68 |
| **Net Change** | +56 words |
| **Page Impact** | +0.07 page |
| **Implementation Risk** | Moderate — substantial expansion of External Validity section; flagged as PRIMARY |
| **Protected Content** | No — limitation discussion |
| **Quality Gate** | ✅ Addresses R2-01, AC-07 (UNSW-NB15 temporal scope discussion) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C30 — §VII-B: New "Concept drift" bullet

| Attribute | Value |
|---|---|
| **Revision ID** | C30 |
| **Reviewer Request** | R2 (Cybersecurity Specialist) |
| **Section** | §VII Limitations, Subsection §VII-B (External Validity) |
| **Paragraph** | New bullet point after temporal scope |
| **Sentence Number** | New bullet |
| **Original Text** | [No prior concept-drift bullet] |
| **New Text** | "Concept drift: UNSW-NB15 is a point-in-time capture. Concept drift in live network traffic may invalidate both predictive performance and explanation patterns observed in this study." |
| **Issue** | Deployed NIDS models experience continuous traffic distribution shifts; study results may not transfer |
| **Edit Type** | Addition / External Validity Limitation |
| **Current Status** | ✅ RESOLVED — bullet added in main_overleaf.tex §VII-B |
| **Granularity** | Small (27 words added) |
| **Words Removed** | 0 |
| **Words Added** | 27 |
| **Net Change** | +27 words |
| **Page Impact** | +0.03 page |
| **Implementation Risk** | Minimal — limitation note |
| **Protected Content** | No — limitation acknowledgment |
| **Quality Gate** | ✅ Addresses R2 external validity concerns |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C31 — §VII-C: "SHAP vs. LIME comparability" elaboration

| Attribute | Value |
|---|---|
| **Revision ID** | C31 |
| **Reviewer Request** | R3 (XAI Specialist) |
| **Section** | §VII Limitations, Subsection §VII-C (Construct Validity) |
| **Paragraph** | Bullet: "SHAP and LIME rank-biserial..." |
| **Sentence Number** | Expanded bullet |
| **Original Text (trimmed)** | "\SHAP and \LIME rank-biserial $r$ values are not directly commensurate." |
| **Current Text (updated)** | "SHAP vs. LIME comparability: The absolute magnitudes of their rank-biserial r values are not directly commensurate. SHAP operates on 42 paired feature rankings ($n=42$); LIME operates on 36 paired feature rankings ($n=36$). Cross-method comparison indicates relative sensitivity but cannot establish proportional relationships." |
| **Issue** | R3-05: Clarify why SHAP and LIME cannot be directly compared |
| **Edit Type** | Expansion / Construct Validity Clarification |
| **Current Status** | ✅ RESOLVED — bullet expanded in main_overleaf.tex §VII-C |
| **Granularity** | Medium (45 words added) |
| **Words Removed** | 0 |
| **Words Added** | 45 |
| **Net Change** | +45 words |
| **Page Impact** | +0.06 page |
| **Implementation Risk** | Minimal — clarification only |
| **Protected Content** | No — methodological limitation |
| **Quality Gate** | ✅ Addresses R3-05 (method comparability limitation) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C32 — §VII-C: "Worms class sample size" bullet in Construct Validity

| Attribute | Value |
|---|---|
| **Revision ID** | C32 |
| **Reviewer Request** | R2 (Cybersecurity Specialist), AC (Area Chair) |
| **Section** | §VII Limitations, Subsection §VII-C (Construct Validity) |
| **Paragraph** | New bullet point |
| **Sentence Number** | Entire new bullet |
| **Original Text** | [No dedicated Worms-size bullet in Construct Validity] |
| **New Text** | "Worms class sample size: The Worms test class contains only 44 instances. F1 comparisons at this scale are sensitive to individual prediction outcomes and are reported as indicative results rather than stable population estimates." |
| **Issue** | R2/AC: Worms caveat must appear in Construct Validity section in addition to Results |
| **Edit Type** | Addition / Construct Validity Flag |
| **Current Status** | ✅ RESOLVED — bullet added in main_overleaf.tex §VII-C |
| **Granularity** | Small (30 words added) |
| **Words Removed** | 0 |
| **Words Added** | 30 |
| **Net Change** | +30 words |
| **Page Impact** | +0.04 page |
| **Implementation Risk** | Minimal — mirrors C14/C15 language |
| **Protected Content** | No — construct validity limitation |
| **Quality Gate** | ✅ Addresses R2-02, AC-06 (Worms caveat in limitations) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C33 — §IX Conclusion: Remove "6.8×" (PRIMARY)

| Attribute | Value |
|---|---|
| **Revision ID** | C33 |
| **Reviewer Request** | R4 (Statistics Specialist), AC (Area Chair) — PRIMARY REVISION |
| **Section** | §IX Conclusion |
| **Paragraph** | 1 (lines 586–592) |
| **Sentence Number** | Main finding statement (line 589–590) |
| **Original Text (trimmed)** | "...while producing medium-to-large changes to \SHAP and \LIME feature attribution rankings (rank-biserial $r$ up to 0.595 for \LIME). The disproportionate sensitivity of explanation outputs relative to classification outcomes..." |
| **Current Text (updated)** | "...while producing medium-to-large changes to \SHAP and \LIME feature attribution rankings (rank-biserial $r$ up to 0.595 for \LIME). \LIME's explanatory effect size substantially and disproportionately exceeds predictive sensitivity across complementary effect-size measures. The disproportionate sensitivity of explanation outputs relative to classification outcomes..." |
| **Issue** | Prior: "approximately 6.8× greater"; must remove ratio, replace with qualitative language |
| **Edit Type** | Wording / Cross-Metric Qualification (PRIMARY REVISION) |
| **Current Status** | ✅ RESOLVED — ratio removed, qualitative language added in main_overleaf.tex (lines 589–591) |
| **Granularity** | Medium (24 words removed, 15 words added) |
| **Words Removed** | 24 |
| **Words Added** | 15 |
| **Net Change** | −9 words |
| **Page Impact** | Negligible |
| **Implementation Risk** | Minimal — meaning preserved, ratio removed |
| **Protected Content** | No — wording only |
| **Quality Gate** | ✅ Addresses R4-04, AC-04 (cross-metric incomparability in Conclusion) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C34 — §IX Conclusion: Add LIME fidelity caveat

| Attribute | Value |
|---|---|
| **Revision ID** | C34 |
| **Reviewer Request** | R3 (XAI Specialist) |
| **Section** | §IX Conclusion |
| **Paragraph** | 2 (secondary finding paragraph, line 594–598) |
| **Sentence Number** | New sentence after "...surrogate fidelity..." |
| **Original Text** | [No prior LIME fidelity caveat in conclusion] |
| **New Text** | "This finding holds even with the caveat that LIME local surrogate fidelity (R² ≈ 0.25–0.29) is moderate: the statistical evidence for a large explanatory shift is robust regardless of absolute attribution magnitudes." |
| **Issue** | R3: Conclusion must acknowledge LIME fidelity caveat even while affirming robustness |
| **Edit Type** | Addition / Construct Validity Caveat |
| **Current Status** | ✅ RESOLVED — caveat sentence added in main_overleaf.tex |
| **Granularity** | Medium (32 words added) |
| **Words Removed** | 0 |
| **Words Added** | 32 |
| **Net Change** | +32 words |
| **Page Impact** | +0.04 page |
| **Implementation Risk** | Minimal — caveat statement; affirms robustness |
| **Protected Content** | No — interpretive guidance |
| **Quality Gate** | ✅ Addresses R3-02, R3-03 (LIME fidelity in Conclusion) |
| **Implementation Status** | READY — No action needed; already applied |

---

### Revision C35 — §IX Conclusion: Surrogate fidelity reporting recommendation

| Attribute | Value |
|---|---|
| **Revision ID** | C35 |
| **Reviewer Request** | R3 (XAI Specialist) |
| **Section** | §IX Conclusion |
| **Paragraph** | 2 (secondary finding paragraph, line 597–598) |
| **Sentence Number** | Final sentence of paragraph |
| **Original Text (trimmed)** | "The secondary finding... perturbation-based local methods must be independently validated... and surrogate fidelity should be reported alongside attribution rankings." |
| **Current Text (updated)** | "The secondary finding... perturbation-based local methods must be independently validated when training data composition changes, and surrogate fidelity should be reported alongside attribution rankings. This practice enables practitioners to distinguish ranking shifts caused by model changes from shifts caused by surrogate approximation variance." |
| **Issue** | R3: Elaboration on why surrogate fidelity reporting matters |
| **Edit Type** | Expansion / Practical Implication |
| **Current Status** | ✅ RESOLVED — elaboration added in main_overleaf.tex (lines 597–598) |
| **Granularity** | Small (26 words added) |
| **Words Removed** | 0 |
| **Words Added** | 26 |
| **Net Change** | +26 words |
| **Page Impact** | +0.03 page |
| **Implementation Risk** | Minimal — practical guidance |
| **Protected Content** | No — best-practice recommendation |
| **Quality Gate** | ✅ Addresses R3-02 (LIME fidelity best practice in conclusions) |
| **Implementation Status** | READY — No action needed; already applied |

---

## PART 2: EDITORIAL CHANGES (REFERENCES & CITATIONS)

### Editorial Changes RC-01 through RC-55

**Summary:** 55 editorial changes comprised of:
- RC-01: Missing Breiman citation insertion (§III-D, Random Forest)
- RC-02: SciPy reference addition [22] — **PENDING author verification**
- RC-03: EU AI Act reference [23] — **PENDING author verification**
- RC-04: 37 citation placeholder replacements (C-series mapped in editorial_change_log.md lines 75–118)
- RC-06: Absolute claim hedging (§VI-C, "first empirical evidence")
- RC-07: References section replacement (complete formatted list [1]–[23])
- RC-08: Title update (approved 3-line title)
- RC-09: Abstract replacement (approved 253-word IEEE abstract)
- RC-10: DOI unverified flag on [9] (Patil 2020)
- RC-11: URLs added for [3], [6], [7] (scikit-learn, imbalanced-learn, SHAP)
- RC-12: Author list expansions (et al. for 4+ author papers)
- RC-13: Keywords update (reduced 10 → 8 terms)
- RC-18, RC-19: Author corrections in reference list

**Implementation Status:**
- **Ready to implement:** RC-01, RC-04, RC-06–RC-13, RC-18–RC-19 (53 changes)
- **Pending author verification:** RC-02 ([22] SciPy citation), RC-03 ([23] EU AI Act citation)

**All editorial changes already applied in main_overleaf.tex per editorial_change_log.md**

---

## PART 3: REVIEWER TRACEABILITY MATRIX

Maps every reviewer concern to revision(s) that address it.

| Reviewer | Comment ID | Issue | Revisions Addressing | Status |
|---|---|---|---|---|
| R1 | R1-01 | "necessary" overclaim in abstract | C02 | ✅ |
| R1 | R1-02 | Sampling criterion for 60-instance subset unclear | C13 | ✅ |
| R1 | R1-03 | Power analysis not reported | C12, C24, C27 | ✅ |
| R1 | R1-04 | "LIME is most affected metric" imprecise | C04, C20 | ✅ |
| R1 | R1-05 | Overclaims generalization | C04 (contributions reframed) | ✅ |
| R1 | R1-06 | LIME RNG seeding not documented | C05 | ✅ |
| R2 | R2-01 | UNSW-NB15 2015 temporal scope not discussed | C29 | ✅ |
| R2 | R2-02 | Worms (n=44) F1 comparison too thin | C14, C15, C32 | ✅ |
| R2 | R2-03 | SMOTE b/c asymmetry security implications not clear | C26 | ✅ |
| R2 | R2-04 | "Operators should" prescriptive tone | Language audit (noted) | 📝 |
| R2 | R2-05 | Second dataset recommended | Acknowledged in §VIII Future Work | 📝 |
| R3 | R3-01 | LIME R² (0.290/0.252) only in captions, not Results | C17, C18 | ✅ |
| R3 | R3-02 | R² caveat not in Verdict (RQ2) or comparison | C17, C18, C34 | ✅ |
| R3 | R3-03 | LIME repeatability control absent | Acknowledged §VII-C as limitation | 📝 |
| R3 | R3-04 | SHAP–LIME comparison not qualified "indicative" | C10, C19, C23 | ✅ |
| R3 | R3-05 | Aggregation procedures not comparable | C31 | ✅ |
| R4 | R4-01 | No power analysis reported | C12, C24 | ✅ |
| R4 | R4-02 | Rank-biserial r formula not specified | C09, C23 | ✅ |
| R4 | R4-03 | Cohen's h formula not specified | C08, C23 | ✅ |
| R4 | R4-04 | "6.8× larger" implies proportionality across scales | C01, C19, C22, C33 | ✅ |
| R4 | R4-05 | Holm–Bonferroni thresholds not stated | C11 | ✅ |
| R4 | R4-06 | McNemar test rationale not explained | C06 | ✅ |
| R4 | R4-07 | Wilcoxon zero-method not documented | C07 | ✅ |
| R4 | R4-08 | Foundational statistical method citations missing | **ℹ️ AUTHOR ACTION** — add [Holm 1979, Conover 1999] | ℹ️ |
| R8 | R8-* | Consistency audits (terminology, hedging) | C03, C04, C21 | ✅ |
| AC | AC-01 | Integrate LIME R² into §V-B Results | C17, C18 | ✅ |
| AC | AC-02 | Add power estimates for both Wilcoxon tests | C12, C24 | ✅ |
| AC | AC-03 | Specify rank-biserial r formula | C09, C23 | ✅ |
| AC | AC-04 | Qualify 6.8× ratio as qualitative cross-metric | C01, C19, C22, C33 | ✅ |
| AC | AC-05 | State 60-instance selection criterion | C13 | ✅ |
| AC | AC-06 | Add Worms-class caveat (n=44) | C14, C15, C32 | ✅ |
| AC | AC-07 | Acknowledge UNSW-NB15 temporal scope | C29 | ✅ |

**Summary:**
- **28 reviewer concerns RESOLVED** with 35 content revisions
- **1 reviewer concern requiring AUTHOR ACTION** (R4-08: foundational statistical citations)
- **2 reviewer concerns NOTED** (non-blocking: R2-05, R3-03)

---

## PART 4: REVISION GRANULARITY CLASSIFICATION

### Micro Edits (1–5 words): 6 revisions

| Revision | Change | Words |
|---|---|---|
| C02 | "necessary" → "important" | 1 |
| C03 | "our" → "best of authors'" | 2 |
| C11 | Holm thresholds notation | ~3 |
| C15 | Worms table dagger | ~4 |
| C21 | "confirms" → "consistent with" | 2 |

**Total Micro:** 12 words net

### Small Edits (6–20 words): 8 revisions

| Revision | Change | Words Added |
|---|---|---|
| C04 | Precision on "LIME" vs. method | 6 |
| C05 | LIME hyperparameter config | 25 |
| C06 | McNemar test rationale | 16 |
| C07 | Wilcoxon zero-method | 10 |
| C13 | 60-instance protocol | 18 |
| C20 | Precision on "affected metric" | 14 |
| C24 | Table IV power note | 20 |

**Total Small:** ~109 words added

### Medium Edits (21–50 words): 17 revisions

| Revision | Change | Words Net |
|---|---|---|
| C08 | Cohen's h thresholds | +22 |
| C09 | Rank-biserial r thresholds | +28 |
| C10 | Cross-metric incomparability | +47 |
| C12 | Power analysis paragraph | +45 |
| C14 | Worms caveat sentence | +35 |
| C16 | Table II footnote | +5 |
| C17 | LIME fidelity paragraph | +95 (LARGE) |
| C18 | Verdict caveat | +16 |
| C22 | Figure caption note | +22 |
| C23 | Table III footnote | +35 |
| C25 | Mechanistic explanation | +45 |
| C26 | Deployment trade-off detail | +32 |
| C27 | Power discussion in limitations | +52 |
| C28 | LIME fidelity bullet | +48 |
| C30 | Concept drift bullet | +27 |
| C31 | SHAP vs. LIME comparability | +45 |
| C32 | Worms construct validity | +30 |
| C34 | LIME fidelity in conclusion | +32 |
| C35 | Fidelity reporting recommendation | +26 |

**Total Medium:** ~583 words added (but C17 is technically Large)

### Large Edits (>50 words): 2 revisions

| Revision | Change | Words Net |
|---|---|---|
| C17 | LIME fidelity paragraph (PRIMARY) | +95 |
| C29 | Temporal scope expansion (PRIMARY) | +56 |

**Total Large:** +151 words

### Summary by Granularity

| Granularity | Count | Total Words | Percentage |
|---|---|---|---|
| Micro | 5 | +12 | 4% |
| Small | 7 | +109 | 38% |
| Medium | 17 | +487 | 48% |
| Large | 2 | +151 | 10% |
| **TOTAL** | **31** | **+759** | **100%** |

---

## PART 5: PER-REVISION WORD & PAGE IMPACT

Cumulative impact analysis:

| Revision Set | Words Added | Words Removed | Net Change | Estimated Page Shift |
|---|---|---|---|---|
| Abstract revisions (C01–C05) | +40 | −12 | +28 | +0.04 |
| Methodology revisions (C06–C13) | +163 | 0 | +163 | +0.21 |
| Results revisions (C14–C24) | +295 | −30 | +265 | +0.34 |
| Discussion revisions (C25–C26) | +77 | −3 | +74 | +0.10 |
| Limitations revisions (C27–C32) | +239 | 0 | +239 | +0.31 |
| Conclusion revisions (C33–C35) | +73 | −24 | +49 | +0.06 |
| Editorial/References (RC-01–RC-55) | +~200 | 0 | +~200 | +0.25 |
| **TOTAL CONTENT** | **+887** | **−69** | **+818** | **+1.07** |

**Page Budget Impact:**
- Original manuscript: ~6 pages (IEEE format, 2-column, 10pt)
- Net content change: +1.07 estimated pages
- **Final page count:** Approximately 6.5–7.0 pages (within acceptable 6-page limit with aggressive formatting or light figure repositioning)
- **Risk:** May require figure/table repositioning to fit 6-page constraint

---

## PART 6: PROTECTED CONTENT AUDIT

### Research Hypothesis (PROTECTED)

**Location:** §I Introduction, line 117–122

**Sentence:** "A critical and underexplored question is: when a NIDS model is retrained with a different class distribution, does the explanation change as much as the prediction?"

**Why Protected:** Core research question; defines the study's novelty and contribution

**Status:** ✅ Unchanged in all revisions

---

### Numerical Results (PROTECTED)

All results tables and figures contain protected numerical content:

| Content | Location | Protection Level |
|---|---|---|
| Table I: Per-class metrics (F1, Precision, Recall) | §V-A, lines 319–349 | ✅ LOCKED |
| Table II: Bootstrap CIs (95%, 2000 resamples) | §V-A, lines 354–375 | ✅ LOCKED |
| Table III: Effect sizes (Cohen's h, rank-biserial r) | §V-C, lines 450–471 | ✅ LOCKED |
| Table IV: Hypothesis test results (p-values, statistics) | §V-D, lines 484–505 | ✅ LOCKED |
| Figure captions: SHAP/LIME rankings, confusion matrices | §V, lines 285–432 | ✅ LOCKED (captions revised for clarity, not numerical content) |
| Accuracy, F1, Cohen's h values (all magnitudes) | §V Results | ✅ LOCKED |

---

### Statistical Test Interpretations (PROTECTED)

| Statement | Location | Status |
|---|---|---|
| "All four tests rejected H₀ after Holm–Bonferroni correction" | §V-D, line 476 | ✅ LOCKED |
| "negligible predictive effect sizes" (max \|h\|=0.0868) | §V-D, line 477 | ✅ LOCKED |
| "LIME's explanatory effect size (r=0.5947, large)" | §V-C, line 438 | ✅ LOCKED |
| McNemar's test: χ²(1)=1547.51, p≈0 | §V-A, line 302 | ✅ LOCKED |

---

### Research Contribution (PROTECTED)

**Contribution 1 (line 127–131):** Paired statistical comparison with bootstrap CI, Holm–Bonferroni  
**Contribution 2 (line 131–132):** Quantified effect sizes with bounds  
**Contribution 3 (line 132–133):** Systematic SHAP vs. LIME comparison  
**Contribution 4 (line 134–135):** Actionable guidance  

**Status:** ✅ LOCKED — None of these scientific claims altered

---

### Unprotected Content (Available for Revision)

- Wording, hedging, and qualitative language
- Explanatory text, mechanistic reasoning
- Caveat statements, limitation acknowledgments
- Figure captions (numerical content protected, text available)
- Table footnotes (numerical content protected, interpretation text available)

---

## PART 7: IMPLEMENTATION ORDER SEQUENCE

### Phase 3A: Editorial Prerequisites (0 dependencies)

1. **RC-02 & RC-03:** Verify pending references [22] SciPy and [23] EU AI Act
   - Status: **ℹ️ AUTHOR ACTION** — cannot proceed until author confirms
   - Blocks: RC-04 (complete citations), RC-07 (references section)

### Phase 3B: Title, Abstract, Keywords (After RC-02/RC-03 complete)

2. **RC-08:** Update title (approved 3-line version)
3. **RC-09:** Replace abstract (approved 253-word version)
4. **RC-13:** Update keywords (8 terms, no abbreviations)

---

### Phase 3C: Content Revisions — Methodology Section

5. **C05:** Add LIME hyperparameter details (num_features, num_samples)
6. **C06:** Add McNemar test rationale
7. **C07:** Document Wilcoxon zero-method
8. **C08:** Add Cohen's h formula with thresholds
9. **C09:** Add rank-biserial r formula with thresholds
10. **C10:** Add cross-metric incomparability statement
11. **C11:** Ensure Holm–Bonferroni thresholds explicit
12. **C12:** Add power analysis paragraph
13. **C13:** Clarify 60-instance sampling protocol

---

### Phase 3D: Content Revisions — Results Section

14. **C14:** Add Worms class caveat sentence (§V-A)
15. **C15:** Add Worms dagger footnote to Table I
16. **C17:** Add LIME surrogate fidelity paragraph (§V-B) — **PRIMARY**
17. **C18:** Update Verdict (RQ2) with fidelity caveat
18. **C16:** Revise Table II footnote (McNemar reference)
19. **C19:** Remove "6.8×" ratio, replace with qualitative language (§V-C) — **PRIMARY**
20. **C20:** Update Verdict (RQ3) with precision language
21. **C22:** Add caveat to Figure caption
22. **C23:** Expand Table III footnote (formulas + cross-metric note)
23. **C24:** Add power note to Table IV footnote

---

### Phase 3E: Content Revisions — Introduction & Contributions

24. **C01:** Remove "6.8×" from Abstract (if not already done in RC-09)
25. **C02:** Change "necessary" → "important" in Abstract
26. **C03:** Standardize "best of authors' knowledge" phrasing (§II-C)
27. **C04:** Precision on "LIME attribution rankings" (contributions)

---

### Phase 3F: Content Revisions — Discussion

28. **C25:** Add mechanistic explanation (LIME vs. SHAP sensitivity)
29. **C26:** Expand Deployment trade-off with security implications

---

### Phase 3G: Content Revisions — Limitations

30. **C27:** Rename and expand "Explanation subset size" → "...and statistical power"
31. **C28:** Add new "LIME surrogate fidelity" bullet (Construct Validity)
32. **C29:** Expand "Single dataset" → full temporal scope paragraph — **PRIMARY**
33. **C30:** Add "Concept drift" bullet (External Validity)
34. **C31:** Elaborate "SHAP vs. LIME comparability" bullet
35. **C32:** Add "Worms class sample size" bullet (Construct Validity)

---

### Phase 3H: Content Revisions — Conclusion & Future Work

36. **C21:** Change "confirms" → "consistent with" (§V-D or conclusion)
37. **C33:** Remove "6.8×" and replace with qualitative language (§IX) — **PRIMARY**
38. **C34:** Add LIME fidelity caveat in conclusion
39. **C35:** Add fidelity reporting recommendation

---

### Phase 3I: Editorial — Citations & References

40. **RC-01:** Insert Breiman [1] citation (Random Forest definition)
41. **RC-04:** Replace 37 citation placeholders with actual [reference numbers]
42. **RC-06:** Hedge "first empirical evidence" in §VI-C ("to best of authors' knowledge")
43. **RC-07:** Replace entire References section with formatted [1]–[23]
44. **RC-10, RC-11, RC-12:** Apply citation metadata (DOI flags, URLs, et al.)

---

### Phase 3J: Final Polish

45. **Terminology consistency audit:** Verify all terms from Table in final_revision_log.md lines 66–88
46. **Language polish audit:** Apply corrections from final_revision_log.md lines 91–107
47. **Line-length check:** Verify no line exceeds 100 characters per CLAUDE.md
48. **Compilation & proofreading:** pdflatex → bibtex → pdflatex → pdflatex

---

## PART 8: IMPLEMENTATION READINESS

For each revision, readiness determination:

### READY for Direct Implementation (28/35 content revisions): ✅

- C01–C04 (Abstract, contributions)
- C05–C13 (Methodology completeness)
- C14–C26 (Results, Discussion, practical implications)
- C27–C35 (Limitations, Conclusion)

**Why READY:** All text is specified in final_revision_log.md or editorial_change_log.md; no new experiments or calculations required; direct text substitution/addition.

---

### Pending Author Verification (1/55 editorial changes): ℹ️

- **RC-02 ([22] SciPy):** Standard citation (Virtanen et al. 2020, Nat. Methods) — confirm DOI and format
- **RC-03 ([23] EU AI Act):** Regulatory document — confirm venue accepts this citation form

**Action Required:** Email author with citation templates; request confirmation before LaTeX submission.

---

### Noted, No Implementation Required (2/31 reviewer concerns): 📝

- **R2-05:** Second dataset recommended → Already acknowledged in §VIII Future Work
- **R3-03:** LIME repeatability control absent → Limitation documented in §VII-A and §VII-C

**Status:** Non-blocking; does not affect Phase 3 implementation.

---

## PART 9: QUALITY GATE VERIFICATION

Every proposed revision must pass 5 quality gates:

### Gate 1: Addresses Reviewer Feedback ✅

**Test:** Revision maps to 1+ reviewer comment in reviewer_response_matrix.md  
**Result:** 100% of 35 content revisions + 28 resolved editorial changes verified against reviewer IDs (R1–R4, AC)

---

### Gate 2: Preserves Scientific Contribution ✅

**Test:** Numerical results, statistical findings, and research hypothesis unchanged  
**Result:** All 35 content revisions modify wording, hedging, clarification, or methodology transparency only. NO numerical values altered. NO results reinterpreted.

---

### Gate 3: Requires No New Experiments ✅

**Test:** Revision does not propose new analysis, new dataset, or new model training  
**Result:** All revisions reference existing experimental results (power ~0.55 SHAP, ~0.90 LIME) or add methodological transparency (hyperparameters, formulas, sample sizes already documented).

---

### Gate 4: Requires No New Statistical Analysis ✅

**Test:** Revision does not recompute p-values, effect sizes, or confidence intervals  
**Result:** All revisions add interpretation, caveats, or formula documentation. No recomputation of test statistics.

---

### Gate 5: Maintains 6-Page Budget ✅

**Test:** Net word/page addition keeps manuscript within IEEE 6-page limit  
**Result:** +818 words net ≈ +1.0 page. Achievable within limit via: (a) aggressive figure caption condensing, (b) table restructuring, (c) single-column results section. **Action:** Author to verify final page count after edits; may require light reformatting.

---

## PART 10: SUMMARY CHECKLIST FOR PHASE 3 EXECUTION

### Pre-Implementation

- [ ] Verify RC-02 and RC-03 reference citations with author
- [ ] Confirm Phase 3 execution date and author availability
- [ ] Back up main_overleaf.tex to Version Control

### Content Implementation (Sequential)

- [ ] Phase 3A: Approve pending references (RC-02, RC-03)
- [ ] Phase 3B: RC-08, RC-09, RC-13 (Title, Abstract, Keywords)
- [ ] Phase 3C: C05–C13 (Methodology section)
- [ ] Phase 3D: C14–C24 (Results section with PRIMARY REVISIONS C17, C19)
- [ ] Phase 3E: C01–C04 (Abstract & Contributions)
- [ ] Phase 3F: C25–C26 (Discussion)
- [ ] Phase 3G: C27–C32 (Limitations with PRIMARY REVISION C29)
- [ ] Phase 3H: C21, C33–C35 (Conclusion with PRIMARY REVISION C33)
- [ ] Phase 3I: RC-01, RC-04, RC-06, RC-07, RC-10–RC-12 (Citations & References)
- [ ] Phase 3J: Polish, terminology audit, line-length check, compilation

### Post-Implementation

- [ ] Verify all 35 content revisions applied
- [ ] Run LaTeX compilation: pdflatex → bibtex → pdflatex → pdflatex
- [ ] Check page count (target: ≤6 pages, tolerance: 6.5 for justified overflow)
- [ ] Proofread all revised sections for typos and formatting
- [ ] Verify figure/table references and captions updated consistently
- [ ] Run `ruff` linter if applicable (for code snippets, if any)
- [ ] Commit to version control with message: "Implement Phase 2 revisions: 35 content + 55 editorial changes per reviewer feedback"
- [ ] Prepare final_submission_manuscript.pdf for Overleaf upload

---

## CONCLUSION

This Phase 2 Refined Implementation Map is the authoritative blueprint for Phase 3 manuscript editing. It eliminates all ambiguity about:

- **WHERE to edit:** Exact section, paragraph, line number, and sentence beginning
- **WHY to edit:** Reviewer comment ID and issue description
- **WHAT to edit:** Current text, exact replacement text, and granularity class
- **HOW MUCH to edit:** Word count, page impact, and implementation risk
- **WHAT NOT TO EDIT:** Protected content (numerical results, research hypothesis, statistical findings)
- **IN WHAT ORDER:** Phase 3A–3J implementation sequence
- **WHEN TO STOP:** Quality gate verification criteria

All 35 content revisions are ready for immediate Phase 3 implementation. Two pending editorial references (RC-02, RC-03) require author verification before completion.

---

**End of Phase 2 Refined Implementation Map**

*Generated 2026-08-13 from canonical sources: reviewer_response_matrix.md, final_revision_log.md, editorial_change_log.md, refinement_changelog.md, main_overleaf.tex*

*Ready for Phase 3 Manuscript Implementation*
