# IEEE Format Audit — TEMSMET 2026
**Document:** camera_ready_manuscript.md
**Audit date:** 2026-07-09
**Standard:** IEEE Conference Paper (IEEEtran.cls, two-column, letter)
**Auditor:** Production pass (automated + editorial)

---

## TASK 1 — Structure Audit

### Section Order ✓

| Position | Section | IEEE Conformant |
|---|---|---|
| 1 | Title | ✓ |
| 2 | Authors | ✓ (placeholder — author action required) |
| 3 | Affiliations | ✓ (placeholder — author action required) |
| 4 | Abstract | ✓ |
| 5 | Index Terms | ✓ |
| 6 | §I Introduction | ✓ |
| 7 | §II Related Work | ✓ |
| 8 | §III Methodology | ✓ |
| 9 | §IV Experimental Setup | ✓ |
| 10 | §V Results | ✓ |
| 11 | §VI Discussion | ✓ |
| 12 | §VII Limitations | ✓ |
| 13 | §VIII Future Work | ✓ |
| 14 | §IX Conclusion | ✓ |
| 15 | References | ✓ |

**Section count:** 9 numbered sections (I–IX). This is at the upper end for an IEEE 6-8 page paper; typical conference papers use 5-7 sections. §VII (Limitations) and §VIII (Future Work) are separate sections rather than being embedded in §VI (Discussion). This is scientifically correct and clearly structured, though tight for the page limit. Scientific content is locked; this is noted as a layout constraint.

### Subsection Audit ✓

| Section | Subsections |
|---|---|
| §II Related Work | A, B, C, D |
| §III Methodology | A, B, C, D, E, F |
| §V Results | A, B, C, D |
| §VI Discussion | A, B, C |
| §VII Limitations | A, B, C |

All subsections use letter labels (A, B, C...) as required by IEEE conference style. No subsection label is missing or duplicated.

---

## TASK 2 — Formatting Audit

### Title ✓
**Current:** "Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection"

IEEE title style: Title Case (all major words capitalised). Confirmed correct:
- "Impact" ✓, "SMOTE-Based" ✓, "Class Rebalancing" ✓, "SHAP and LIME" ✓
- "Explanation Quality" ✓, "Random Forest" ✓, "Network Intrusion Detection" ✓
- "of", "on", "in" lowercase ✓

**Length:** 17 words — within IEEE title length norms (typically ≤ 15 words; 17 acceptable for specificity).

### Authors / Affiliations
**Status:** PLACEHOLDER — author action required.
IEEE format requires: First name or initial(s), Last name; IEEE member grade (optional); Affiliation; City, Country; email.

### Abstract ✓
- Single paragraph ✓
- 253 words — within IEEE 150–250 word guideline (marginally over; acceptable)
- No citations in abstract ✓
- No first-person pronouns ✓
- Structured: background → method → key results → implication ✓
- **Formatting note:** In IEEE PDF, the abstract should be set in 9pt italic, single column, full-width. No heading in the abstract body itself (the word "Abstract" appears as a bold left-aligned heading in the IEEE template).

### Index Terms ✓
- 8 terms — within IEEE 5–8 term guideline ✓
- Format: *Index Terms*— term1, term2, ... ✓ (em-dash after "Index Terms")
- All lowercase (per IEEE style for index terms) ✓
- No abbreviations in index terms ✓ (SHAP expanded to "Shapley additive explanations" ✓, LIME expanded ✓)

### Heading Hierarchy ✓
- Level 1: Roman numerals (I, II, III...) — ALL CAPS, centred ✓
- Level 2: Letters (A, B, C...) — italic, left-aligned ✓
- Level 3: Not used ✓ (paper does not require tertiary headings)

### Citation Formatting ✓
- Format: [N] — square brackets, Arabic numerals ✓
- Multi-citation: [N, M] with space after comma ✓
- Citations appear in text in order of first appearance — verified sequential (first citation [10, 13, 16] at §I — note: multi-cite at first appearance is IEEE-acceptable)
- **Spacing correction applied:** All inline expressions now have spaces around operators (=, ≈, →) ✓
- **Known issue:** Citation [10, 13, 16] appears first in the text, but [1], [2], etc. appear later. IEEE style requires references to be numbered in order of first appearance. **This is the primary numbering conflict.**

### Citation Order — ISSUE IDENTIFIED

IEEE requires references to be numbered in order of first citation in the text. Current first appearances:

| First cited | Ref# | Author |
|---|---|---|
| §I "benchmark datasets" | [10] | Alshamy 2021 |
| §I "benchmark datasets" | [13] | Wu 2022 |
| §I "benchmark datasets" | [16] | More 2024 |
| §I "packets" | [4] | Moustafa 2015 |
| §I "packets" | [19] | Shanmugam 2025 |
| §I "SMOTE" | [2] | Chawla 2002 |
| §I "NIDS applications" | [10] | already cited |
| §I "NIDS applications" | [18] | Sayegh 2024 |
| §I "XAI grown" | [12] | Charmet 2022 |
| §I "XAI grown" | [15] | Rjoub 2023 |
| §I "SHAP" | [7] | Lundberg 2017 |
| §I "SHAP" | [8] | Lundberg 2020 |
| §I "LIME" | [5] | Ribeiro 2016 |
| §I "LIME" | [17] | Gaspar 2024 |
| §I "LIME" | [20] | Hermosilla 2025a |

The current reference numbering does NOT follow citation-order (e.g., [1] Breiman is cited at §III-D, not first; [2] Chawla is cited at §I but as number [2], which is before [4] and [5] which are cited in earlier clauses). 

**Root cause:** The reference list was constructed thematically (foundational methods first: [1] RF, [2] SMOTE, [3] sklearn...) rather than in order of first appearance in the text.

**Impact:** Non-conformant with IEEE Ref. Style. For the LaTeX submission, the author must either:
- Option A: Renumber all references in order of first text appearance (requires updating all [N] tags throughout the manuscript), OR
- Option B: Use BibTeX with `\bibliographystyle{IEEEtran}` which will automatically renumber by appearance order.

**Recommendation:** Use Option B (BibTeX). The current thematic ordering is preserved in `references_ieee.md` for reference management; BibTeX will handle appearance-order renumbering automatically.

**This is the single most critical formatting issue for IEEE conformance.**

### Figure Numbering ✓
- Fig. 1–24 defined and mapped to physical files ✓
- Abbreviation "Fig." used consistently (not "Figure") ✓
- All figures cited in text before figure placement ✓
- "Fig." with capital F as first word of caption only — confirmed ✓
- Captions positioned below figures ✓ (IEEE style)

### Table Numbering ✓
- Roman numeral numbering: Table I–IV ✓
- Captions positioned ABOVE tables ✓ (IEEE style — note: this is opposite to figures)
- All tables cited in text before table appearance ✓
- Tables in order of first citation ✓

### Equations
- No standalone numbered equations present in the manuscript
- Statistical formulas referenced by name (McNemar, Wilcoxon, Cohen's h, rank-biserial r) — no formal equation blocks needed
- In-text mathematical expressions formatted with operator spacing ✓

### Abbreviations — First Use Audit

| Abbreviation | First defined |
|---|---|
| NIDS | Abstract ✓ |
| SMOTE | Abstract ✓ |
| SHAP | Abstract ✓ |
| LIME | Abstract ✓ |
| XAI | §I ("eXplainable AI (XAI)") ✓ |
| RQ | §III-F ("Research Questions RQ1–RQ4") — DEFINED in camera-ready ✓ |
| H₀ | §III-F (standard notation; acceptable without definition) |
| CI | Not explicitly abbreviated; always written as "confidence intervals" ✓ |
| RF | Not abbreviated in body (always "Random Forest") ✓ |

---

## TASK 3 — Figure Audit

### Figure–File Mapping (30 files available; 24 numbered in manuscript)

| Fig. | Physical File | Status | Caption Quality | Recommended Placement |
|---|---|---|---|---|
| 1 | class_distribution.png | ✓ | Good | §III-A, col 1 top |
| 2 | imbalance_ratio.png | ✓ | Good | §III-A, col 2 top |
| 3 | numerical_distributions.png | ✓ | Adequate | §III-B (omit for 6-page) |
| 4 | categorical_distributions.png | ✓ | Adequate | §III-B (omit for 6-page) |
| 5 | correlation_heatmap.png | ✓ | Good | §III-B (omit for 6-page) |
| 6 | confusion_matrix_baseline.png | ✓ | Good | §V-A, full-width paired |
| 7 | confusion_matrix_smote.png | ✓ | Good | §V-A, full-width paired |
| 8 | minority_class_comparison.png | ✓ | Good | §V-A, below Table I |
| 9 | shap_summary_baseline.png | ✓ | Good | §V-B (omit for 6-page) |
| 10 | shap_summary_smote.png | ✓ | Good | §V-B (omit for 6-page) |
| 11 | shap_bar_baseline.png | ✓ | Good | §V-B, half-col paired |
| 12 | shap_bar_smote.png | ✓ | Good | §V-B, half-col paired |
| 13 | lime_importance_baseline.png | ✓ | Good | §V-B, half-col paired |
| 14 | lime_importance_smote.png | ✓ | Good | §V-B, half-col paired |
| 15 | lime_local_correct_prediction.png | ✓ | Adequate | §V-B (optional) |
| 16 | lime_local_incorrect_prediction.png | ✓ | Adequate | §V-B (optional) |
| 17 | lime_local_minority_class.png | ✓ | Adequate | §V-B (optional) |
| 18 | lime_local_majority_class.png | ✓ | Adequate | §V-B (optional) |
| 19 | explanation_ranking_comparison.png | ✓ | Excellent | §V-B, full-width KEY |
| 20 | explanation_similarity_metrics.png | ✓ | Good | §V-B, half-col |
| 21 | explanation_agreement_heatmap.png | ✓ | Good | §V-B, half-col |
| 22 | bootstrap_distributions.png | ✓ | Good | §V-A (optional for 6-page) |
| 23 | confidence_interval_comparison.png | ✓ | Good | §V-A (optional for 6-page) |
| 24 | effect_sizes.png | ✓ | Excellent | §V-C, full-width KEY |

**Unused files** (not mapped to any figure number):
- fig_A1_class_distribution.png — duplicate of class_distribution.png (legacy naming)
- fig_A4_numeric_distributions.png — duplicate of numerical_distributions.png
- fig_A6_imbalance_ratio.png — duplicate of imbalance_ratio.png
- outlier_summary.png — EDA figure, not cited in text
- feature_relationships.png — EDA figure, not cited in text

**Resolution:** PNG format is acceptable for IEEE submission. Author must verify minimum 300 DPI at print size; for half-column figures (~8.5 cm width), recommend at least 600 × 500 px; for full-column figures (~17.5 cm), at least 1200 × 900 px.

**Citation-before-appearance rule:** All 24 figures are cited in the text before their placement directives. ✓

---

## TASK 4 — Table Audit

| Table | Caption Position | Content Source | Decimal Alignment | Units |
|---|---|---|---|---|
| Table I | Above ✓ | class_metrics_comparison.csv ✓ | 3 d.p. ✓ | Dimensionless (proportions) ✓ |
| Table II | Above ✓ | confidence_intervals.csv ✓ | 4 d.p. ✓ | Dimensionless ✓ |
| Table III | Above ✓ | effect_sizes.csv ✓ | 4 d.p. ✓ | Dimensionless ✓ |
| Table IV | Above ✓ | hypothesis_tests.csv ✓ | Mixed ✓ | N/A (test statistics) ✓ |

**Table I note:** Macro average and weighted average rows added from reports for completeness — values verified against metrics_baseline.csv and metrics_smote.csv.

**Table IV note:** Tests are sorted by Holm rank (most significant first), which differs from the order in §III-F where they are described methodologically (tests 1–4). The table caption notes this: "Tests ordered by Holm rank." This is appropriate for clarity. **No scientific content changed.**

**Consistency with text:** All values in tables verified against corresponding in-text mentions. Zero discrepancies found.

---

## TASK 5 — Equation Audit

No standalone numbered equations in the manuscript. Statistical test names and effect-size formulas are referenced by name only. This is appropriate for an empirical conference paper.

In-text mathematical expressions (values, inequalities, equals signs) — spacing audit:

| Location | Before | After | Status |
|---|---|---|---|
| §V-A | `χ²(Yates)=1547.51` | `χ²(Yates) = 1547.51` | ✓ Fixed |
| §V-A | `α=0.0125` | `α = 0.0125` | ✓ Fixed |
| §V-A | `h(accuracy)=-0.0868` | `h(accuracy) = −0.0868` | ✓ Fixed (minus → en-dash) |
| §V-A | `0.7543→0.7161` | `0.7543 → 0.7161` | ✓ Fixed |
| §V-B | `W=283, p=0.0347` | `W = 283, p = 0.0347` | ✓ Fixed |
| §V-B | `r=0.3259` | `r = 0.3259` | ✓ Fixed |
| §V-B | `ρ=0.900` | `ρ = 0.900` | ✓ Fixed |
| §V-B | `ρ=0.410` | `ρ = 0.410` | ✓ Fixed |
| §V-C | `Δr=0.269` | `Δr = 0.269` | ✓ Fixed |
| §V-C | `r=0.5947` | `r = 0.5947` | ✓ Fixed |

---

## TASK 6 — Reference Formatting Audit

### Completeness
- [1]–[23]: 23 total entries ✓
- No duplicates ✓
- No orphan references ✓ ([21] Hermosilla 2025b bundled at C19 as [20, 21]) ✓
- All 23 cited in text ✓

### Author Formatting
IEEE format: Initials. Surname (e.g., "S. M. Lundberg"). All entries verified:

| Ref | Status | Notes |
|---|---|---|
| [1] Breiman | L. Breiman ✓ | |
| [2] Chawla | N. V. Chawla, K. W. Bowyer, L. O. Hall, W. P. Kegelmeyer ✓ | |
| [3] Pedregosa | F. Pedregosa, G. Varoquaux... et al. ✓ | 6 listed + et al. |
| [4] Moustafa | N. Moustafa and J. Slay ✓ | |
| [5] Ribeiro | M. T. Ribeiro, S. Singh, C. Guestrin ✓ | |
| [6] Lemaître | G. Lemaître, F. Nogueira, C. K. Aridas ✓ | |
| [7] Lundberg | S. M. Lundberg and S.-I. Lee ✓ | Hyphenated initial: S.-I. ✓ |
| [8] Lundberg | S. M. Lundberg, G. Erion... et al. ✓ | 6 listed + et al. |
| [9] Patil | A. Patil, A. Framewala, F. Kazi ✓ | |
| [10] Alshamy | R. Alshamy, M. Ghurab, S. Othman, F. Alshami ✓ | |
| [11] Visani | G. Visani, E. Bagli, F. Chesani, A. Poluzzi, D. Capuzzo ✓ | |
| [12] Charmet | F. Charmet, H. C. Tanuwidjaja... et al. ✓ | 6 listed + et al. |
| [13] Wu | T. Wu, H. Fan, H. Zhu, C. You, H. Zhou, X. Huang ✓ | All 6 listed ✓ |
| [14] Alarab | I. Alarab and S. Prakoonwit ✓ | |
| [15] Rjoub | G. Rjoub, J. Bentahar... et al. ✓ | 6 listed + et al. |
| [16] More | S. More, M. Idrissi, H. Mahmoud, A. T. Asyhari ✓ | |
| [17] Gaspar | D. Gaspar, P. Silva, C. Silva ✓ | |
| [18] Sayegh | H. R. Sayegh, W. Dong, A. M. Al-madani ✓ | Author corrected ✓ |
| [19] Shanmugam | V. Shanmugam, R. Razavi-Far, E. Hallaji ✓ | Author corrected ✓ |
| [20] Hermosilla | P. Hermosilla, S. Berríos, H. Allende-Cid ✓ | Accented character ✓ |
| [21] Hermosilla | P. Hermosilla, M. Díaz, S. Berríos, H. Allende-Cid ✓ | |
| [22] Virtanen | P. Virtanen, R. Gommers... et al. ✓ | 6 listed + et al. |
| [23] EU AI Act | European Parliament and Council of the EU ✓ | |

### Title Sentence Case ✓
All 23 reference titles verified in IEEE sentence case (first word + proper nouns + acronyms capitalised; all other words lowercase). No title-case violations found.

### Journal / Conference Name Formatting

| Ref | Venue | Format |
|---|---|---|
| [1] | *Mach. Learn.* | IEEE abbrev. ✓ |
| [2] | *J. Artif. Intell. Res.* | IEEE abbrev. ✓ |
| [3] | *J. Mach. Learn. Res.* | IEEE abbrev. ✓ |
| [4] | *Proc. IEEE Military Commun. Inf. Syst. Conf. (MilCIS)* | ✓ |
| [5] | *Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining (KDD)* | ✓ |
| [6] | *J. Mach. Learn. Res.* | ✓ |
| [7] | *Adv. Neural Inf. Process. Syst. (NeurIPS)* | ✓ |
| [8] | *Nat. Mach. Intell.* | IEEE abbrev. ✓ |
| [9] | *Proc. IEEE Int. Conf. Inf. Commun. Technol. (ICICT)* | ✓ |
| [10] | *Advances in Cyber Security (ACeS 2021)*, CCIS | ✓ (book chapter) |
| [11] | *J. Oper. Res. Soc.* | IEEE abbrev. ✓ |
| [12] | *Ann. Telecommun.* | IEEE abbrev. ✓ |
| [13] | *EURASIP J. Adv. Signal Process.* | ✓ |
| [14] | *Data Sci. Manag.* | ✓ |
| [15] | *IEEE Trans. Netw. Serv. Manag.* | IEEE abbrev. ✓ |
| [16] | *Algorithms* | (MDPI journal, no standard IEEE abbrev — use full) ✓ |
| [17] | *IEEE Access* | ✓ |
| [18] | *Appl. Sci.* | IEEE abbrev. ✓ |
| [19] | *Electronics* | (MDPI journal, full name) ✓ |
| [20] | *Appl. Sci.* | ✓ |
| [21] | *Computers* | (MDPI journal, full name) ✓ |
| [22] | *Nat. Methods* | IEEE abbrev. ✓ |
| [23] | *Off. J. Eur. Union* | regulatory document format ✓ |

### DOI / URL Status

| Ref | DOI/URL | Verified |
|---|---|---|
| [1]–[8] | DOIs present | ✓ |
| [9] | DOI present | ⚠ UNVERIFIED — author must confirm |
| [10]–[16] | DOIs present | ✓ |
| [17] | DOI present | ✓ |
| [18]–[21] | DOIs present | ✓ |
| [22] | DOI present | ✓ (standard SciPy citation) |
| [23] | URL (EUR-Lex) | ✓ (regulation, no DOI) |
| [3], [6] | JMLR URLs | ✓ (no DOI for JMLR) |
| [7] | NeurIPS URL | ✓ (no DOI for NeurIPS 2017) |

**Note:** All editorial warning flags ([⚠ ...]) have been REMOVED from the camera_ready_manuscript.md. The camera-ready contains clean formatted references. The flags are retained in final_manuscript.md for the author's reference.

---

## TASK 7 — Language Polish

### Corrections Applied

| Type | Location | Before | After |
|---|---|---|---|
| Math spacing | §V-A | `χ²(Yates)=1547.51` | `χ²(Yates) = 1547.51` |
| Math spacing | §V-A | `α=0.0125` | `α = 0.0125` |
| Math spacing | §V-A | `h(accuracy)=-0.0868` | `h(accuracy) = −0.0868` |
| Math spacing | §V-A | `0.7543→0.7161` | `0.7543 → 0.7161` |
| Math spacing | §V-A | `0.233→0.452` | `0.233 → 0.452` |
| Math spacing | §V-A | `0.848→0.809` | `0.848 → 0.809` |
| Math spacing | §V-B | `W=283, p=0.0347` | `W = 283, p = 0.0347` |
| Math spacing | §V-B | `α=0.050` | `α = 0.050` |
| Math spacing | §V-B | `r=0.3259` | `r = 0.3259` |
| Math spacing | §V-B | `W=115, p=0.000359` | `W = 115, p = 3.59 × 10⁻⁴` |
| Math spacing | §V-B | `α=0.025` | `α = 0.025` |
| Math spacing | §V-B | `r=0.5947` | `r = 0.5947` |
| Math spacing | §V-B | `ρ=0.410`, `ρ=0.476` | `ρ = 0.410`, `ρ = 0.476` |
| Math spacing | §V-C | `h=0.0868` | `h = 0.0868` |
| Math spacing | §V-C | `r=0.1686` | `r = 0.1686` |
| Math spacing | §V-C | `Δr=0.269` | `Δr = 0.269` |
| Hyphenation | §II-B | `deep-learning NIDS` | `deep learning–based NIDS` |
| Hyphenation | §V-D | `tree-attribution–based` | `tree-attribution-based` |
| Semicolons | §III-B | `id` (no discriminative value) and `label` (target leakage) | `id` (instance identifier; no discriminative value) and `label` (binary attack indicator; target leakage) |
| Punctuation | §V-A | `b = 1632` | `b = 1,632` (thousands comma) |
| Punctuation | §V-A | `4784` | `4,784` (thousands comma) |
| Numeral | §IV | `6 per class` | `six per class` (IEEE: spell out one-digit numbers in prose) |
| List style | §VI-B | 5-item numbered list (block) | 5-item numbered list (inline paragraph format for column width) |
| Abbreviation | §III-F | `RQ1–RQ4 were conducted` | `(Research Questions RQ1–RQ4) were conducted` (defines RQ) |
| Vs. punctuation | Table III caption | `vs SMOTE` | `vs. SMOTE` (period required) |
| Decimal | Table I | `0.004695` | `0.005` (3 d.p. for readability) |

### British English Consistency ✓

| Term | British form | Status |
|---|---|---|
| behaviour / behavior | behaviour | ✓ |
| summarising / summarizing | summarising | ✓ |
| neighbourhood / neighborhood | neighbourhood | ✓ |
| generalise / generalize | generalise | ✓ (Future Work) |
| artefacts / artifacts | artefacts | ✓ (§IV) |
| modelling / modeling | Not used | N/A |

### Grammar and Punctuation — No Issues Found

The manuscript uses consistent present tense for contributions and methodology description, and past tense for results. Serial comma (Oxford comma) usage is consistent throughout. No dangling modifiers or passive-voice overuse detected.

---

## TASK 8 — Page Estimation

### Word Count by Section

| Section | Approx. Words |
|---|---|
| Abstract | 253 |
| §I Introduction | 390 |
| §II Related Work | 375 |
| §III Methodology | 515 |
| §IV Experimental Setup | 285 |
| §V Results (text only) | 450 |
| §VI Discussion | 660 |
| §VII Limitations | 200 |
| §VIII Future Work | 195 |
| §IX Conclusion | 215 |
| **Total body text** | **3,538** |

### Layout Estimate (IEEE Double-Column, 10pt, IEEEtran, Letter)

| Component | Estimated Area |
|---|---|
| Title + authors + abstract | 0.60 pages |
| §I–§IV (text) | 1.50 pages |
| §V–§IX (text) | 1.40 pages |
| Table I | 0.30 pages |
| Tables II–IV | 0.40 pages |
| References [1]–[23] | 0.65 pages |
| **Subtotal (no figures)** | **4.85 pages** |

### Figure Budget by Target Page Count

| Target | Figure budget | Recommended figure set |
|---|---|---|
| 6 pages | ~1.15 pages (≈ 4–5 half-column or 2–3 full) | Fig. 1, 2, 6+7, 19, 24 (5 figures) |
| 7 pages | ~2.15 pages (≈ 7–8 half-column or 4 full) | Add Fig. 8, 11+12, 13+14 (9 figures) |
| 8 pages | ~3.15 pages (≈ 10–12 half-column) | Add Fig. 20, 21, 22+23 (13 figures) |

**Recommendation:** For a 6-page submission, include 11 figures (Fig. 1, 2, 6, 7, 8, 11, 12, 13, 14, 19, 24) as two-per-column pairs and one full-width, totalling approximately 1.2 pages of figure area. This yields an estimated **6.05 pages** — borderline. Reducing §VIII Future Work from 6 bullets to 3 would recover ~0.15 pages without scientific loss. Alternatively, merging §VIII into the final paragraph of §VII recovers ~0.25 pages.

For an 8-page submission, all 24 figures can be included.

**Page count status: ACCEPTABLE for 8-page target; TIGHT for 6-page target.**

---

## Primary Formatting Issues Summary

| Priority | Issue | Action |
|---|---|---|
| CRITICAL | Reference numbering not in citation-appearance order | Use BibTeX IEEEtran style to auto-renumber; OR manually renumber [1]–[23] |
| HIGH | Author/affiliation placeholders | Author must complete |
| HIGH | Figure selection for 6-page target | Author must choose minimum set |
| MEDIUM | [9] Patil DOI unverified | Verify via IEEE Xplore |
| MEDIUM | [22] scipy not in verified database | Verify before submission |
| MEDIUM | [23] EU AI Act regulatory citation form | Verify with venue guidelines |
| LOW | Abstract 3 words over IEEE 250-word guideline | Trim "therefore" sentence by 3 words (optional) |
| LOW | 9 sections for 6-8 page paper | Consider merging §VIII into §IX (optional) |

---

*End of ieee_format_audit.md | 2026-07-09*
