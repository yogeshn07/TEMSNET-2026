# Page Count Report — IEEE TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality
           in Random Forest Network Intrusion Detection
**Production file:** docs/paper/final_ieee_manuscript.tex
**Template:** IEEEtran.cls — conference, two-column, A4, 10-point
**Date:** 2026-07-09
**Target:** ≤ 6 pages (IEEE TEMSMET 2026 regular paper)

---

## 1. IEEEtran Layout Parameters (A4, Conference Mode)

| Parameter | Value |
|---|---|
| Paper size | A4 (210 × 297 mm) |
| Text area | 172 mm × 241 mm (6.77″ × 9.49″) |
| Column width | 83.0 mm (3.27″) each |
| Inter-column gap | 6 mm (0.24″) |
| Body font | 10 pt Computer Modern Serif |
| Baseline skip | 12 pt |
| Lines per column | ~57–60 (usable text column) |
| Characters per line | ~43–46 (body text) |
| Body-text word density | ~1,050–1,150 words per page |

---

## 2. Body Text Word Count by Section

| Section | Words (approx.) | Column-inches (approx.) |
|---|---|---|
| Title block (title + authors + affiliations) | — | ~1.2 col-in |
| Abstract (253 words, single-column span) | 253 | ~1.4 col-in |
| Index Terms | 22 | ~0.2 col-in |
| §I Introduction | 375 | ~3.0 col-in |
| §II Related Work (A–D) | 365 | ~2.9 col-in |
| §III Methodology (A–F) | 580 | ~4.6 col-in |
| §IV Experimental Setup | 245 | ~2.0 col-in |
| §V Results (A–D) | 540 | ~4.3 col-in |
| §VI Discussion (A–C) | 395 | ~3.2 col-in |
| §VII Limitations (A–C) | 390 | ~3.1 col-in |
| §VIII Future Work | 95 | ~0.8 col-in |
| §IX Conclusion | 200 | ~1.6 col-in |
| **Body text subtotal** | **~3,460 words** | **~27.5 col-in** |
| References (23 entries) | — | ~11.0 col-in |
| **All prose + references** | — | **~38.5 col-in** |

One printed page = ~18.0 column-inches (2 columns × ~9 col-in each).

**Prose + references:** 38.5 / 18.0 ≈ **2.14 pages**

---

## 3. Figure Space Estimates (11-Figure Minimum Set)

Figure heights are estimated for readable rendering at IEEEtran column width.

| Fig. | Description | Width | Height (est.) | Space |
|---|---|---|---|---|
| Fig. 1 | Class distribution (bar, log) | Half-col | 1.4 in | 0.17 pg |
| Fig. 2 | Imbalance ratio (bar) | Half-col | 1.4 in | 0.17 pg |
| Fig. 3 | Confusion matrix — Baseline | Half-col | 1.6 in | 0.19 pg |
| Fig. 4 | Confusion matrix — SMOTE | Half-col | 1.6 in | 0.19 pg |
| Fig. 5 | Minority class F1 comparison | Half-col | 1.5 in | 0.18 pg |
| Fig. 6 | SHAP bar — Baseline | Half-col | 1.5 in | 0.18 pg |
| Fig. 7 | SHAP bar — SMOTE | Half-col | 1.5 in | 0.18 pg |
| Fig. 8 | LIME importance — Baseline | Half-col | 1.5 in | 0.18 pg |
| Fig. 9 | LIME importance — SMOTE | Half-col | 1.5 in | 0.18 pg |
| Fig. 10 | Ranking comparison (full-width) | Full-width | 2.2 in | 0.24 pg |
| Fig. 11 | Effect sizes (full-width) | Full-width | 2.0 in | 0.22 pg |
| **Total** | | | | **~1.98 pages** |

*Note: Paired half-column figures (Figs. 1+2, 3+4, 6+7, 8+9) may be placed
side-by-side in LaTeX using `minipage` or `subfig`, each taking one column width
at half the page. If placed individually in separate float environments they
will alternate across columns — the LaTeX typesetter should verify final
placement during compilation.*

---

## 4. Table Space Estimates

| Table | Description | Environment | Height (est.) | Space |
|---|---|---|---|---|
| Table I | Per-class metrics (12 data rows + header + footers) | `table*` (full-width) | 1.6 in | 0.17 pg |
| Table II | Bootstrap CIs (6 rows) | `table` (single column) | 0.9 in | 0.10 pg |
| Table III | Effect sizes (6 rows) | `table` (single column) | 0.9 in | 0.10 pg |
| Table IV | Hypothesis tests (4 rows) | `table` (single column) | 0.8 in | 0.09 pg |
| **Total** | | | | **~0.46 pages** |

---

## 5. Page Count Summary

| Component | Pages |
|---|---|
| Title + abstract + index terms | 0.42 |
| Body text (§I–§IX) | 1.72 |
| References | 0.61 |
| Figures (11-figure set) | 1.98 |
| Tables (4 tables) | 0.46 |
| Float overhead (captions, spacing, float gaps) | 0.25 |
| **ESTIMATED TOTAL** | **5.44 pages** |

### Target Assessment

| Target | Estimate | Status |
|---|---|---|
| ≤ 6 pages | **~5.4 pages** | ✅ WITHIN LIMIT |
| ≥ 5 pages (avoid very short papers) | **~5.4 pages** | ✅ APPROPRIATE LENGTH |

**The manuscript is estimated to compile within 6 pages with the 11-figure minimum set.**

---

## 6. Sensitivity Analysis

| Scenario | Page Count | Feasibility |
|---|---|---|
| 11 figures (minimum set) | ~5.4 pages | ✅ Target |
| 11 figures + Fig. 22+23 (bootstrap/CI plots) | ~5.9 pages | ✅ Tight but fits |
| 15 figures (extended set: +Fig. 20, 21, 22, 23) | ~6.8 pages | ❌ Exceeds 6 pages |
| Full 24-figure set | ~9.2 pages | ❌ Requires 8-page format |
| Drop §VIII Future Work (merge into §IX) | −0.06 pages | Minor saving |
| Reduce §VII Limitations to bullet summary | −0.15 pages | Available if needed |

---

## 7. If the Compiled PDF Exceeds 6 Pages

Apply the following interventions in priority order:

### Step 1 — Figure size reduction (saves 0.2–0.4 pages)
Reduce figure heights by 15–20% via `\includegraphics[width=\columnwidth,height=1.2in]`.
Do not crop content — only reduce height if the figure remains fully readable.

### Step 2 — Float placement optimisation (saves 0–0.2 pages)
Add `\vspace{-3pt}` before figure captions. Use `[!t]` or `[!b]` to force tight
float placement. In IEEEtran, `\IEEEtriggeratref{20}` can trigger a column break
near the references to improve balance.

### Step 3 — Remove §VIII Future Work (saves ~0.06 pages)
Merge the five future work bullets into the final paragraph of §IX Conclusion as
"Future work should address: (i)...(v)...". This reduces one full section heading
and its paragraph.

### Step 4 — Condense §VII Limitations (saves ~0.15 pages)
Convert the three subsections (Internal, External, Construct Validity) into a
single subsection with 7 concise bullets. No scientific content removed.

### Step 5 — Figures 22 and 23 to supplemental (saves ~0.2 pages)
Move bootstrap_distributions.png and confidence_interval_comparison.png to
an appendix or online supplement. The bootstrap CI results are fully reported
in Table II; the figures provide visual corroboration only.

**Maximum potential saving from Steps 1–5: ~0.65 pages.**
If the baseline is ≤ 6.65 pages after compilation, all five steps together
will bring it within 6 pages without removing any scientific content.

---

## 8. Compilation Verification Procedure

After compiling `final_ieee_manuscript.tex`:

1. Open `final_ieee_manuscript.pdf` and check page count displayed in PDF reader.
2. Check `final_ieee_manuscript.log` for:
   - `Overfull \hbox` warnings > 10pt (fix with `\allowbreak` or reword)
   - Underfull `\vbox` on last page (harmless but check column balance)
   - `?? citation undefined` (indicates missing `\bibitem`)
3. Cross-reference check: Ctrl+F for `??` in the PDF (broken `\ref` or `\cite`)
4. Verify all 11 figures are rendered (not placeholder boxes)
5. Verify Tables I–IV are not split across pages

---

*End of page_count_report.md | 2026-07-09*
