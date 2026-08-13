# Editorial Change Log — TEMSMET 2026 Final Integration
**Date:** 2026-07-09
**Source file:** docs/paper/manuscript.md (pre-integration)
**Output files:** docs/paper/manuscript.md (updated), docs/paper/final_manuscript.md
**Guided by:** docs/paper/citation_cross_reference.csv, docs/paper/reference_audit_report.md, docs/paper/references_ieee.md

---

## Summary

| Category | Count |
|---|---|
| Citation placeholder replacements (C01–C37) | 37 |
| Missing citation insertions (RC-01) | 1 |
| Absolute claim softening (RC-06) | 1 |
| Title update (RC-08) | 1 |
| Abstract replacement (RC-09) | 1 |
| Keyword update (RC-13) | 1 |
| References section replacement (RC-07) | 1 |
| New references added (RC-02, RC-03) | 2 |
| Author corrections in reference list (RC-18, RC-19) | 2 |
| et al. expansions in reference list (RC-12) | 4 |
| URL / identifier additions (RC-11) | 3 |
| DOI flag addition (RC-10) | 1 |
| **Total editorial changes** | **55** |

---

## RC-08 — Title Update

| Field | Value |
|---|---|
| Location | Line 7 |
| Change type | Replacement |

**Old:**
> Impact of Class Imbalance Correction on Explainability of Random Forest–Based Network Intrusion Detection

**New:**
> Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection

**Rationale:** The approved title from the Title/Abstract/Keywords session is more specific, names both XAI methods explicitly, and uses the term "rebalancing" consistently with the paper's scope (SMOTE only, not general imbalance correction).

---

## RC-09 — Abstract Replacement

| Field | Value |
|---|---|
| Location | Lines 21–44 |
| Change type | Full replacement |
| Word count | 253 words (approved) |

**Rationale:** The pipeline-generated abstract was replaced with the approved 253-word IEEE-style abstract. The new abstract: (a) opens with the research gap rather than the dataset, (b) states the two XAI methods explicitly in the first sentence, (c) quantifies all key effect sizes (Cohen's h ≤ 0.09, r = 0.33 SHAP, r = 0.60 LIME, 6.8× ratio), and (d) ends with the practical implication as a conclusion sentence.

---

## RC-13 — Keywords Update

| Field | Value |
|---|---|
| Location | Lines 46–48 |
| Change type | Replacement |

**Old (10 terms):**
> network intrusion detection, class imbalance, SMOTE, explainable artificial intelligence, SHAP, LIME, Random Forest, UNSW-NB15, feature attribution stability, trustworthy AI

**New (8 terms):**
> network intrusion detection, explainability, class imbalance, synthetic minority oversampling, Shapley additive explanations, local interpretable model-agnostic explanations, random forest, feature attribution

**Rationale:** Reduced from 10 to 8 terms per IEEE keyword-count conventions (typically 5–8 terms). Removed UNSW-NB15 (dataset-specific, low indexing value) and "trustworthy AI" (too generic). Expanded abbreviations to full IEEE index terms. Reordered by conceptual primacy.

---

## RC-04 — Citation Placeholder Replacements (37 slots)

All 37 functional `[CITATION REQUIRED]` tokens replaced per `citation_cross_reference.csv`.

| Slot | Section | Location | Old | New |
|---|---|---|---|---|
| C01 | §I | "benchmark datasets" | [CITATION REQUIRED] | [10, 13, 16] |
| C02 | §I | "packets" | [CITATION REQUIRED] | [4, 19] |
| C03 | §I | "SMOTE) [CITATION REQUIRED]" | [CITATION REQUIRED] | [2] |
| C04 | §I | "NIDS applications" | [CITATION REQUIRED] | [10, 18] |
| C05 | §I | "grown substantially" | [CITATION REQUIRED] | [12, 15] |
| C06 | §I | "exPlanations)" | [CITATION REQUIRED] | [7, 8] |
| C07 | §I | "Explanations)" | [CITATION REQUIRED] | [5, 17, 20] |
| C08 | §II-A | "intrusion detection" | [CITATION REQUIRED] | [4, 19] |
| C09 | §II-A | "majority class" | [CITATION REQUIRED] | [2, 10] |
| C10 | §II-A | "SMOTE [inline]" | [CITATION REQUIRED] | [2] |
| C11 | §II-A | "ADASYN [inline]" | [CITATION REQUIRED] | [19] |
| C12 | §II-A | "undersampling [inline]" | [CITATION REQUIRED] | [19] |
| C13 | §II-A | "cost-sensitive learning [inline]" | [CITATION REQUIRED] | [19] |
| C14 | §II-A | "ensemble methods [inline]" | [CITATION REQUIRED] | [19] |
| C15 | §II-A | "recall improvements" | [CITATION REQUIRED] | [13, 18] |
| C16 | §II-B | "trustworthy-AI movement" | [CITATION REQUIRED] | [12, 15] |
| C17 | §II-B | "local accuracy" | [CITATION REQUIRED] | [7, 8] |
| C18 | §II-B | "underlying model" | [CITATION REQUIRED] | [5] |
| C19 | §II-B | "RF-based NIDS" | [CITATION REQUIRED] | [20, 21] |
| C20 | §II-B | "deep-learning NIDS" | [CITATION REQUIRED] | [17] |
| C21 | §II-C | "general ML contexts" | [CITATION REQUIRED] | [11] |
| C22 | §II-C | "LIME and SHAP outputs" | [CITATION REQUIRED] | [12] |
| C23 | §II-C | "hyperparameter choices" | [CITATION REQUIRED] | [11] |
| C24 | §II-C | "our knowledge" | [CITATION REQUIRED] | [9, 14] |
| C25 | §II-D | "UNSW-NB15 [inline]" | [CITATION REQUIRED] | [4] |
| C26 | §II-D | "NIDS studies" | [CITATION REQUIRED] | [16, 20] |
| C27 | §III-A | "dataset [inline]" | [CITATION REQUIRED] | [4] |
| C28 | §III-C | "SMOTE [inline]" | [CITATION REQUIRED] | [2] |
| C29 | §III-E | "SHAP values" | [CITATION REQUIRED] | [7, 8] |
| C30 | §III-E | "LIME explanations" | [CITATION REQUIRED] | [5] |
| C31 | §IV | "scikit-learn" | [CITATION REQUIRED] | [3] |
| C32 | §IV | "imbalanced-learn" | [CITATION REQUIRED] | [6] |
| C33 | §IV | "shap library" | [CITATION REQUIRED] | [7] |
| C34 | §IV | "lime library" | [CITATION REQUIRED] | [5] |
| C35 | §IV | "scipy" | [CITATION REQUIRED] | [22] |
| C36 | §VI-C | "cybersecurity [citation]" | [CITATION REQUIRED] | [12, 15] |
| C37 | §VI-C | "consequential decisions" | [CITATION REQUIRED] | [23] |

**Notes:**
- C19: Set to `[20, 21]` per RC-05 (not `[20]` alone) to prevent [21] Hermosilla 2025b from being an orphan reference.
- C35: scipy [22] is a PENDING reference — not in the original verified literature database. Author must verify before submission.
- C37: EU AI Act [23] is a PENDING reference. Author must verify citation form with venue editorial guidelines.

---

## RC-01 — Breiman Citation Insertion (§III-D)

| Field | Value |
|---|---|
| Location | §III-D, "Classifier" paragraph |
| Change type | Insertion (no placeholder existed) |

**Old:**
> A Random Forest classifier was trained independently on...

**New:**
> A Random Forest [1] classifier was trained independently on...

**Rationale:** Breiman (2001) [1] is listed in the reference database and is the canonical citation for Random Forest. No `[CITATION REQUIRED]` placeholder had been inserted for this claim. RC-01 identified this as a critical missing citation.

---

## RC-06 — Absolute Claim Softened (§VI-C)

| Field | Value |
|---|---|
| Location | §VI-C, final sentence of Discussion |
| Change type | Hedging / language correction |

**Old:**
> This study provides the first empirical evidence of this instability in a standardised NIDS benchmark setting.

**New:**
> To the best of the authors' knowledge, this study provides the first empirical evidence of this instability in a standardised NIDS benchmark setting.

**Rationale:** The literature audit noted that absolute novelty claims ("the first") require hedging per IEEE scholarly convention, as exhaustive literature search cannot be guaranteed. The hedge phrase is consistent with language used in docs/literature/research_gap_analysis.md.

---

## RC-07 — References Section Replaced

| Field | Value |
|---|---|
| Location | Lines 423–438 (former placeholder block) |
| Change type | Full replacement |

**Old content:** 8-line placeholder block with "NOTE TO AUTHORS" comment and partial citation hints.

**New content:** Complete formatted reference list [1]–[23] sourced from `docs/paper/references_ieee.md`, with all author corrections, URL additions, et al. expansions, and DOI flags applied inline.

---

## RC-02 — scipy Reference Added as [22]

**Entry added:**
> P. Virtanen, R. Gommers, T. E. Oliphant, M. Haberland, T. Reddy, D. Cournapeau et al., "SciPy 1.0: Fundamental algorithms for scientific computing in Python," *Nat. Methods*, vol. 17, pp. 261–272, Feb. 2020. doi: 10.1038/s41592-020-0772-5. [⚠ Verify before submission]

**Status:** PENDING — not in the original verified literature database. This is the standard citation for SciPy (Virtanen et al. 2020, Nature Methods, doi verified via doi.org). Author should confirm before submission.

---

## RC-03 — EU AI Act Reference Added as [23]

**Entry added:**
> European Parliament and Council of the European Union, "Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)," *Off. J. Eur. Union*, Jul. 2024. [Online]. Available: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689 [⚠ Verify citation form]

**Status:** PENDING — not in the original verified literature database. Author must verify the citation form is acceptable to the venue. If the venue does not accept regulatory documents, replace with an academic survey of AI transparency regulation.

---

## RC-10 — DOI Unverified Flag Added to [9]

Reference [9] (Patil et al. 2020) has a flagged DOI. The in-text entry now reads:
> doi: 10.1109/ICICT50521.2020.9092325. [⚠ DOI unverified — confirm via IEEE Xplore]

---

## RC-11 — URLs Added for [3], [6], [7]

- **[3] scikit-learn (Pedregosa 2011):** JMLR does not assign CrossRef DOIs. URL added: `http://jmlr.org/papers/v12/pedregosa11a.html`
- **[6] imbalanced-learn (Lemaître 2017):** JMLR identifier. URL added: `http://jmlr.org/papers/v18/16-365.html`
- **[7] SHAP (Lundberg & Lee 2017):** NeurIPS 2017 proceedings have no registered DOI. URL added: `https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html`

---

## RC-12 — Author Lists Expanded (et al.)

Four references with truncated author lists were expanded to first-6-authors + et al.:

- **[3] Pedregosa 2011:** 16 authors → F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel et al.
- **[8] Lundberg 2020:** 10 authors → S. M. Lundberg, G. Erion, H. Chen, A. DeGrave, J. M. Prutkin, B. Nair et al.
- **[12] Charmet 2022:** 9 authors → F. Charmet, H. C. Tanuwidjaja, S. Ayoubi, P. F. Gimenez, Y. Han, H. Jmila et al.
- **[15] Rjoub 2023:** 6+ authors → G. Rjoub, J. Bentahar, O. Abdel Wahab, R. Mizouni, A. Song, R. Cohen et al.

---

## Author Corrections Applied in References

These corrections were made during the literature audit session (2026-07-03) and are reflected in the reference list:

- **[18] Sayegh 2024:** First author corrected from "Al-madani" to "Sayegh" (H. R. Sayegh, W. Dong, and A. M. Al-madani).
- **[19] Shanmugam 2025:** First author corrected from "Razavi-Far" to "Shanmugam" (V. Shanmugam, R. Razavi-Far, and E. Hallaji).

---

## Unchanged Sections

The following sections were NOT modified beyond citation replacement:

- §I Introduction — structure, wording, and all numerical results unchanged
- §II Related Work — structure, wording, and all claims unchanged
- §III Methodology — structure, wording, and all numerical results unchanged
- §IV Experimental Setup — structure, wording unchanged
- §V Results — structure, wording, and all numerical results unchanged
- §VI Discussion (§VI-A Interpretation, §VI-B Practical Implications) — unchanged
- §VII Limitations — unchanged
- §VIII Future Work — unchanged
- §IX Conclusion — unchanged

No experimental results were altered. No interpretations were changed. The research hypothesis, research questions, and all statistical findings are identical to the pipeline-generated manuscript.

---

*End of editorial_change_log.md | 55 changes | 2026-07-09*
