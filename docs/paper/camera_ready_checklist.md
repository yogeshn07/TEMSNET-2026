# Camera-Ready Checklist — TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection
**Date:** 2026-07-09
**Status key:** [x] COMPLETE | [ ] AUTHOR ACTION | [~] VERIFY

---

## CRITICAL — Must resolve before submission

- [ ] **Reference numbering:** Renumber [1]–[23] in order of first citation appearance
  (or use BibTeX `IEEEtran` style to auto-renumber).
  Current ordering is thematic, not appearance-order. IEEE requires appearance-order.

- [ ] **Author names:** Replace `[AUTHOR NAMES]` with actual names in IEEE format:
  `First M. Surname, Second M. Surname, ...`

- [ ] **Author affiliations:** Replace `[INSTITUTION]` with actual institution(s).
  IEEE format: Department (if applicable), Institution Name, City, Country.
  Each author's email address on a separate line.

- [ ] **LaTeX conversion:** Convert `camera_ready_manuscript.md` to IEEEtran.cls
  (two-column, conference mode, letter paper). Markdown is for internal review only.

- [ ] **Figure embedding:** Insert all figures into the LaTeX document at the
  annotated positions (see Figure Placement Guide at end of camera_ready_manuscript.md).
  Minimum set for 6-page target: Fig. 1, 2, 6, 7, 8, 11, 12, 13, 14, 19, 24.

---

## HIGH — Should resolve before submission

- [~] **[9] Patil 2020 DOI verification:** Confirm
  `doi: 10.1109/ICICT50521.2020.9092325` via IEEE Xplore.
  Two candidate DOI suffixes were identified during audit.

- [~] **[22] SciPy reference verification:** Confirm Virtanen et al. 2020
  (`doi: 10.1038/s41592-020-0772-5`) is correct before adding to submission.
  Not in original verified literature database.

- [~] **[23] EU AI Act citation form:** Confirm the regulation citation format
  is accepted by IEEE TEMSMET 2026. If the venue requires only peer-reviewed
  publications, select an alternative AI regulation/transparency survey.

- [ ] **Page count check:** After LaTeX conversion and figure insertion, verify
  total pages ≤ 8 (regular paper limit). If > 8: remove optional figures
  (Fig. 3–5, 9, 10, 15–18, 20–23) until within limit.

- [ ] **Figure resolution:** Verify all figures are ≥ 300 DPI at print size.
  Half-column figures (≈ 8.5 cm): minimum 1000 × 800 px.
  Full-column figures (≈ 17.5 cm): minimum 2000 × 1500 px.

- [ ] **PDF generation:** Generate PDF via IEEEtran LaTeX; verify no text
  overflow, no bad line breaks, no hyphenation errors.

---

## MEDIUM — Should verify before submission

- [~] **Abstract word count:** Current abstract is 253 words. IEEE guideline
  is 150–250 words. If venue enforces 250-word limit strictly, trim 3 words
  from the final sentence of the abstract.

- [ ] **IEEE membership IDs:** If required by venue, include IEEE member numbers
  for each co-author with membership.

- [ ] **Copyright form:** Complete IEEE copyright transfer form (eCF) for all
  authors after final PDF is approved.

- [ ] **Conflict of interest:** Complete venue COI declaration.

- [~] **AI-use disclosure:** Check whether IEEE TEMSMET 2026 requires a
  statement disclosing use of AI-assisted tools during manuscript preparation.

- [ ] **Final Scopus/WoS search:** Run a search for papers published June–
  July 2026 on "XAI NIDS imbalance" or "SHAP LIME SMOTE" to catch any
  concurrent work published after the literature audit (2026-07-03).

---

## LOW — Nice to have before submission

- [ ] **Appendix figures (optional):** If venue allows supplemental material,
  consider placing Fig. 9–18 (SHAP/LIME summary and local explanation plots)
  in an online appendix for reproducibility without impacting page count.

- [ ] **Repository DOI:** Archive the repository via Zenodo or equivalent
  and add the DOI to the paper as a reproducibility footnote.

- [ ] **Section merge (optional, 6-page only):** If page count is tight after
  figure insertion, consider merging §VIII Future Work into the last paragraph
  of §IX Conclusion. This saves ≈ 0.25 pages. Scientific content is preserved.

- [ ] **Abstract trim (optional):** If abstract must be ≤ 250 words, change
  "is therefore a necessary component of responsible model assessment" to
  "is a necessary component of responsible model assessment" (−3 words, 250 exactly).

---

## Completed Items (from previous editorial passes)

- [x] All 37 `[CITATION REQUIRED]` tokens replaced (RC-04)
- [x] Breiman [1] citation inserted in §III-D (RC-01)
- [x] "first empirical evidence" claim hedged (RC-06)
- [x] Title updated to approved version (RC-08)
- [x] Abstract replaced with 253-word IEEE version (RC-09)
- [x] Keywords reduced to 8 IEEE index terms (RC-13)
- [x] Full reference list [1]–[23] populated (RC-07)
- [x] scipy added as [22] (RC-02)
- [x] EU AI Act added as [23] (RC-03)
- [x] Author corrections: [18] Sayegh, [19] Shanmugam (RC-18/19)
- [x] et al. expansions: [3], [8], [12], [15] (RC-12)
- [x] JMLR/NeurIPS URLs added: [3], [6], [7] (RC-11)
- [x] Math operator spacing corrected throughout (typography pass)
- [x] RQ abbreviation defined on first use in §III-F
- [x] "tree-attribution-based" hyphenation corrected
- [x] "deep learning–based NIDS" corrected from "deep-learning NIDS"
- [x] Thousands separators in discordant pair counts
- [x] Tables I–IV populated with data from outputs/tables/ CSVs
- [x] All 24 figure placement directives added to camera_ready_manuscript.md
- [x] All 23 editorial warning flags removed from camera_ready_manuscript.md
- [x] British English consistency verified

---

*End of camera_ready_checklist.md | 2026-07-09*
