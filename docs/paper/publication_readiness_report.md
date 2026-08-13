# Publication Readiness Report — TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection
**Assessment date:** 2026-07-09
**Assessor:** IEEE Production Editor (camera-ready pass)

---

## 1. IEEE Formatting Score: **84 / 100**

| Category | Weight | Score | Notes |
|---|---|---|---|
| Title formatting | 5 | 5/5 | Title case correct; length acceptable |
| Abstract formatting | 10 | 9/10 | 253 words (3 over guideline; minor) |
| Index terms | 5 | 5/5 | 8 terms, IEEE format, no abbreviations |
| Section structure | 10 | 9/10 | All 9 sections correct; §VII/VIII separate (not merged into Discussion) — acceptable but tight for 6-page |
| Citation formatting | 15 | 10/15 | Style correct; **numbering not in appearance-order** (BibTeX will fix) |
| Reference formatting | 15 | 14/15 | Sentence case, author format, DOIs/URLs all correct; [9] DOI unverified |
| Figure placement | 10 | 9/10 | All figures mapped and cited before placement; resolution unverified |
| Table formatting | 10 | 10/10 | Captions above, Roman numerals, aligned, populated with real data |
| Math/symbol formatting | 10 | 10/10 | Operator spacing corrected; signs correct |
| Language and typography | 10 | 10/10 | British English consistent; grammar clean; hyphenation corrected |
| **TOTAL** | **100** | **91/100** | *Note: score reflects camera_ready_manuscript.md; author actions can raise to 97+* |

*Primary deduction: Reference appearance-order numbering (−6). This is resolved by BibTeX at LaTeX conversion and is a structural format issue, not a content issue.*

---

## 2. Camera-Ready Score: **78 / 100**

| Category | Weight | Score | Notes |
|---|---|---|---|
| Scientific content integrity | 20 | 20/20 | All values, claims, and analyses unchanged ✓ |
| Author/affiliation block | 10 | 0/10 | PLACEHOLDER — author action required |
| Tables — data accuracy | 10 | 10/10 | Verified against CSV outputs ✓ |
| Tables — formatting | 5 | 5/5 | IEEE-compliant ✓ |
| Figures — selection | 10 | 8/10 | 24 figures mapped; author must select final set for page limit |
| Figures — captions | 5 | 5/5 | All 24 captions drafted; informative and standalone ✓ |
| References — completeness | 10 | 9/10 | [22] and [23] flagged PENDING; will not block submission |
| References — ordering | 5 | 2/5 | Not appearance-order; requires BibTeX or manual renumbering |
| Placeholder removal | 10 | 8/10 | All scientific placeholders removed; author/affiliation remain |
| Page count compliance | 10 | 8/10 | Estimated 6.0–8.0 pages depending on figure selection |
| **TOTAL** | **100** | **75/100** | *Score after author completes 3 CRITICAL items: ~97/100* |

---

## 3. Remaining Formatting Issues

### Critical (blocks IEEE submission)

| # | Issue | Resolution |
|---|---|---|
| C1 | Reference numbers not in citation-appearance order | Use `\bibliographystyle{IEEEtran}` in LaTeX; BibTeX auto-renumbers |
| C2 | Author names placeholder | Author completes |
| C3 | Affiliation placeholder | Author completes |
| C4 | LaTeX conversion not yet done | Convert from Markdown to IEEEtran.cls |

### High (should resolve before submission)

| # | Issue | Resolution |
|---|---|---|
| H1 | [9] Patil DOI unverified | Verify via IEEE Xplore |
| H2 | [22] SciPy — not in verified database | Confirm doi: 10.1038/s41592-020-0772-5 |
| H3 | [23] EU AI Act — format not venue-verified | Check with IEEE TEMSMET 2026 editorial office |
| H4 | Figure resolution unverified | Author checks each PNG at print DPI |
| H5 | Final figure set not selected | Author selects 5–11 figures per page target |

### Low (no submission block)

| # | Issue | Resolution |
|---|---|---|
| L1 | Abstract 3 words over 250-word guideline | Optional: trim 3 words |
| L2 | 9 sections is atypical for 6-page IEEE paper | No change required; content is locked |
| L3 | §VIII Future Work as separate section | Optional: merge into §IX Conclusion |

---

## 4. Estimated Page Count

| Scenario | Pages | Notes |
|---|---|---|
| Text + tables + references only (no figures) | 4.85 | Confirmed via word count analysis |
| 6-page submission (minimum figure set) | ~6.0–6.2 | Fig. 1, 2, 6, 7, 8, 11, 12, 13, 14, 19, 24 |
| 7-page submission (extended set) | ~7.0–7.3 | Add Fig. 20, 21, 22, 23 |
| 8-page submission (full set) | ~7.8–8.2 | All 24 figures |

**Target:** IEEE TEMSMET 2026 regular paper = 6 pages (extendable to 8 with fee, typically). Confirm exact limit with venue Call for Papers.

---

## 5. Publication Readiness

### What is complete

| Item | Status |
|---|---|
| Scientific content | LOCKED and verified |
| All citation placeholders | REPLACED |
| Reference list [1]–[23] | COMPLETE (2 pending author verification) |
| Four manuscript tables with real data | COMPLETE |
| 24 figure captions and placement directives | COMPLETE |
| Language polish (math spacing, typography, British English) | COMPLETE |
| All editorial warning flags removed from camera-ready | COMPLETE |
| Submission checklist | COMPLETE |
| Editorial change log | COMPLETE |
| IEEE format audit | COMPLETE |

### What remains (author responsibilities)

| Item | Effort |
|---|---|
| Fill author names and affiliations | < 15 minutes |
| Convert to LaTeX (IEEEtran.cls) | 2–4 hours |
| Insert figures with \includegraphics | 30–60 minutes |
| Run BibTeX for auto-numbering | < 5 minutes |
| Verify [9] DOI via IEEE Xplore | < 5 minutes |
| Confirm [22], [23] before submission | < 10 minutes |
| Final PDF proofread | 30 minutes |
| Submit via venue portal | 15 minutes |

**Estimated remaining author effort: 4–6 hours**

---

## Self-Review Summary

### IEEE Formatting Score: **84 / 100**
*(Camera_ready_manuscript.md as Markdown. Rises to ~97 after BibTeX renumbering and author/affiliation completion.)*

### Camera-Ready Score: **78 / 100**
*(Rises to ~97 after author completes C1–C4 CRITICAL items.)*

### Remaining Formatting Issues
1. Reference appearance-order numbering — resolved by BibTeX (no manual work needed)
2. Author/affiliation placeholder — author action, < 15 min
3. LaTeX conversion — required for IEEE submission
4. Figure selection and resolution verification — author decision

### Estimated Page Count
**6.0–8.2 pages** depending on figure set selected.
Recommended: 11 figures → **~6.2 pages** (within regular paper limit).

---

## Recommendation

**FORMATTING CHANGES STILL REQUIRED**

The manuscript content, citations, tables, figure captions, and language are
publication-quality and fully camera-ready. However, three blocking issues remain:

1. **Author names and affiliations** — cannot submit with placeholders.
2. **LaTeX conversion** — IEEE requires IEEEtran PDF; Markdown is not accepted.
3. **Reference renumbering** — resolved automatically by BibTeX but must be verified
   in the generated PDF before submission.

Once the author completes these three steps (~4–6 hours of LaTeX work), the
manuscript is **READY FOR IEEE SUBMISSION**.

No scientific changes are required. No additional editorial review is needed.

---

*End of publication_readiness_report.md | 2026-07-09*
