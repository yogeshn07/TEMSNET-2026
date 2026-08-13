# Final Publication Checklist — IEEE TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality
           in Random Forest Network Intrusion Detection
**Production file:** docs/paper/final_ieee_manuscript.tex
**Date:** 2026-07-09
**Standard:** IEEEtran.cls (conference, two-column, A4)

---

## SECTION 1 — Content Integrity

| # | Item | Status | Notes |
|---|---|---|---|
| 1.1 | Title matches approved final_submission_manuscript.md | ✅ PASS | Exact match |
| 1.2 | Abstract is approved 253-word version | ✅ PASS | Reproduced verbatim |
| 1.3 | All 8 IEEE Index Terms present | ✅ PASS | All terms included |
| 1.4 | All 9 sections present (I–IX) | ✅ PASS | Introduction through Conclusion |
| 1.5 | All numerical values unchanged | ✅ PASS | Locked from final_submission_manuscript.md |
| 1.6 | All effect sizes unchanged (h, r) | ✅ PASS | Cohen's h and rank-biserial r values exact |
| 1.7 | All hypothesis test statistics unchanged | ✅ PASS | W, p, χ², thresholds exact |
| 1.8 | All bootstrap CIs unchanged | ✅ PASS | Table II values exact |
| 1.9 | Per-class metrics unchanged (Table I) | ✅ PASS | All 12 rows × 8 columns verified |
| 1.10 | No new scientific claims introduced | ✅ PASS | Production-only changes |

---

## SECTION 2 — IEEE Formatting

| # | Item | Status | Notes |
|---|---|---|---|
| 2.1 | Document class: `\documentclass[conference,a4paper]{IEEEtran}` | ✅ PASS | Correct class and options |
| 2.2 | Two-column layout active | ✅ PASS | IEEEtran conference default |
| 2.3 | 10-point body font | ✅ PASS | IEEEtran default |
| 2.4 | IEEE title formatting (`\maketitle`) | ✅ PASS | Used correctly |
| 2.5 | Abstract in `IEEEabstract` environment | ✅ PASS | Via `abstract` environment (IEEEtran maps correctly) |
| 2.6 | Index Terms in `IEEEkeywords` environment | ✅ PASS | Correct environment used |
| 2.7 | Section headings: Roman numeral, all-caps, centred | ✅ PASS | IEEEtran `\section` handles automatically |
| 2.8 | Subsection headings: letter prefix, italic | ✅ PASS | IEEEtran `\subsection` handles automatically |
| 2.9 | Table captions above tables | ✅ PASS | All 4 tables use `\caption` before `\begin{tabular}` |
| 2.10 | Figure captions below figures | ✅ PASS | All 11 figures use `\caption` after `\includegraphics` |
| 2.11 | References in `thebibliography` environment | ✅ PASS | 23 `\bibitem` entries |
| 2.12 | Equations numbered, centred, right-aligned numbers | ✅ PASS | `equation` environment (2 equations) |
| 2.13 | `\booktabs` rules (toprule, midrule, bottomrule) | ✅ PASS | Applied to all 4 tables |
| 2.14 | Full-width tables use `table*` environment | ✅ PASS | Table I uses `table*` |
| 2.15 | Full-width figures use `figure*` environment | ✅ PASS | Fig. 10, Fig. 11 use `figure*` |
| 2.16 | `\graphicspath` points to correct figure directory | ✅ PASS | `{../../outputs/figures/}` |
| 2.17 | All `\cite{}` keys match `\bibitem` entries | ✅ PASS | 23/23 keys match |
| 2.18 | Equations referenced with `\eqref{}` | ✅ PASS | Both equations cross-referenced |
| 2.19 | Figures referenced with `\ref{fig:...}` | ✅ PASS | All 11 figures use label/ref |
| 2.20 | Tables referenced with `\ref{tab:...}` | ✅ PASS | All 4 tables use label/ref |

---

## SECTION 3 — Reference List (IEEE Appearance Order)

| New # | Old # | First Author | Venue | In-Text First Cite | Status |
|---|---|---|---|---|---|
| [1] | [10] | Alshamy | ACeS Springer 2021 | §I "benchmark datasets" | ✅ |
| [2] | [13] | Wu | EURASIP 2022 | §I "benchmark datasets" | ✅ |
| [3] | [16] | More | Algorithms 2024 | §I "benchmark datasets" | ✅ |
| [4] | [4] | Moustafa | MilCIS 2015 | §I "packets" | ✅ |
| [5] | [19] | Shanmugam | Electronics 2025 | §I "packets" | ✅ |
| [6] | [2] | Chawla | JAIR 2002 | §I "SMOTE [6]" | ✅ |
| [7] | [18] | Sayegh | Appl. Sci. 2024 | §I "NIDS applications" | ✅ |
| [8] | [12] | Charmet | Ann. Telecommun. 2022 | §I "grown substantially" | ✅ |
| [9] | [15] | Rjoub | IEEE TNSM 2023 | §I "grown substantially" | ✅ |
| [10] | [7] | Lundberg 2017 | NeurIPS 2017 | §I "SHAP" | ✅ |
| [11] | [8] | Lundberg 2020 | Nat. Mach. Intell. | §I "SHAP" | ✅ |
| [12] | [5] | Ribeiro | KDD 2016 | §I "LIME" | ✅ |
| [13] | [17] | Gaspar | IEEE Access 2024 | §I "LIME" | ✅ |
| [14] | [20] | Hermosilla 2025a | Appl. Sci. 2025 | §I "LIME" | ✅ |
| [15] | [21] | Hermosilla 2025b | Computers 2025 | §II-B "RF-based NIDS" | ✅ |
| [16] | [11] | Visani | J. Oper. Res. Soc. 2022 | §II-C "ML contexts" | ✅ |
| [17] | [9] | Patil | ICICT 2020 | §II-C "our knowledge" | ✅ |
| [18] | [14] | Alarab | Data Sci. Manag. 2022 | §II-C "our knowledge" | ✅ |
| [19] | [1] | Breiman | Mach. Learn. 2001 | §III-D "Random Forest [19]" | ✅ |
| [20] | [22] | Virtanen | Nat. Methods 2020 | §III-F "McNemar" | ✅ |
| [21] | [3] | Pedregosa | JMLR 2011 | §IV "scikit-learn" | ✅ |
| [22] | [6] | Lemaître | JMLR 2017 | §IV "imbalanced-learn" | ✅ |
| [23] | [23] | EU Parliament | Off. J. EU 2024 | §VI-C "regulatory" | ✅ |

**All 23 references verified in appearance order. BibTeX key mapping complete.**

---

## SECTION 4 — Figure Audit (Minimum 11-Figure Set)

| LaTeX Fig. | Source File | Section | Float | Width | Cited Before? |
|---|---|---|---|---|---|
| Fig. 1 | class_distribution.png | §III-A | `[t]` | `\columnwidth` | ✅ §III-A |
| Fig. 2 | imbalance_ratio.png | §III-A | `[t]` | `\columnwidth` | ✅ §III-A |
| Fig. 3 | confusion_matrix_baseline.png | §V-A | `[t]` | `\columnwidth` | ✅ §V-A |
| Fig. 4 | confusion_matrix_smote.png | §V-A | `[t]` | `\columnwidth` | ✅ §V-A |
| Fig. 5 | minority_class_comparison.png | §V-A | `[b]` | `\columnwidth` | ✅ §V-A |
| Fig. 6 | shap_bar_baseline.png | §V-B | `[t]` | `\columnwidth` | ✅ §V-B |
| Fig. 7 | shap_bar_smote.png | §V-B | `[t]` | `\columnwidth` | ✅ §V-B |
| Fig. 8 | lime_importance_baseline.png | §V-B | `[b]` | `\columnwidth` | ✅ §V-B |
| Fig. 9 | lime_importance_smote.png | §V-B | `[b]` | `\columnwidth` | ✅ §V-B |
| Fig. 10 | explanation_ranking_comparison.png | §V-B | `[t]` (figure*) | `\textwidth` | ✅ §V-B |
| Fig. 11 | effect_sizes.png | §V-C | `[b]` (figure*) | `\textwidth` | ✅ §V-C |

**Optional figures (not included in 6-page build):**
Fig. 12–22 (shap_summary, lime_local, explanation_similarity, explanation_agreement,
bootstrap_distributions, confidence_interval_comparison) — available for extended 8-page build.

---

## SECTION 5 — Table Audit

| LaTeX Table | Title | Rows | Cols | Environment | Caption Position | Cited Before? |
|---|---|---|---|---|---|---|
| Table I | Per-Class Metrics | 14 (incl. header, rules) | 8 | `table*` | ✅ Above | ✅ §V-A |
| Table II | Bootstrap CIs | 8 (incl. header) | 6 | `table` | ✅ Above | ✅ §V-A |
| Table III | Effect Sizes | 8 (incl. header) | 4 | `table` | ✅ Above | ✅ §V-C |
| Table IV | Hypothesis Tests | 6 (incl. header) | 5 | `table` | ✅ Above | ✅ §V-D |

---

## SECTION 6 — Equation Audit

| Eq. # | Label | Formula | Defined variables | Cross-referenced? |
|---|---|---|---|---|
| (1) | `\label{eq:cohenh}` | Cohen's h = 2arcsin(√p₁) − 2arcsin(√p₂) | p₁, p₂ defined in text | ✅ `\eqref{eq:cohenh}` in Table III footnote |
| (2) | `\label{eq:rbs}` | r = Z / √N | Z = normal approx., N defined in text | ✅ `\eqref{eq:rbs}` in Table III footnote |

---

## SECTION 7 — Abbreviation Audit

| Abbreviation | Defined at | First section |
|---|---|---|
| NIDS | First sentence of §I | §I |
| SMOTE | §I paragraph 2 | §I |
| XAI | §I paragraph 3 | §I |
| SHAP | §I paragraph 3 (full expansion) | §I |
| LIME | §I paragraph 3 (full expansion) | §I |
| RQ | §III-F "Research Questions RQ1–RQ4" | §III-F |
| R² | §III-E "coefficient of determination" | §III-E |

---

## SECTION 8 — Outstanding Author Actions

| # | Action | Blocking? | Effort |
|---|---|---|---|
| A1 | Replace `Author One`, `Author Two`, `Author Three` with actual names | **YES** | < 5 min |
| A2 | Replace `[DEPARTMENT]`, `[INSTITUTION]`, `[City]`, `[Country]`, `[domain]` with actual affiliations | **YES** | < 10 min |
| A3 | Replace email placeholders with actual emails | **YES** | < 5 min |
| A4 | Verify figure PNG files are present in `outputs/figures/` at ≥ 300 DPI | **YES** | 15 min |
| A5 | Compile: `pdflatex → pdflatex` (two passes for cross-references) | **YES** | < 2 min |
| A6 | Verify compiled PDF page count ≤ 6 pages | **YES** | < 1 min |
| A7 | Confirm [9] Patil DOI correct via IEEE Xplore | Recommended | 5 min |
| A8 | Confirm [20] SciPy DOI correct (10.1038/s41592-020-0772-5) | Recommended | 3 min |
| A9 | Confirm [23] EU AI Act citation accepted by venue | Recommended | 5 min |
| A10 | Add ORCID iDs to author block if required by venue | Optional | 5 min |
| A11 | Run final Scopus search for June–July 2026 competitor papers | Recommended | 20 min |
| A12 | Submit PDF via IEEE TEMSMET 2026 portal | Final step | 15 min |

---

## SECTION 9 — Compilation Instructions

```bash
# From the project root (c:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026)
cd docs/paper

# Two-pass compilation (required for cross-references)
pdflatex final_ieee_manuscript.tex
pdflatex final_ieee_manuscript.tex

# Verify output
# Open final_ieee_manuscript.pdf and check:
# 1. Page count ≤ 6
# 2. No "??" cross-reference warnings in log
# 3. No overfull \hbox > 5pt (check .log file)
# 4. All figures appear correctly
# 5. Tables do not overflow columns
```

**Note:** IEEEtran.cls must be installed. It is included in:
- TeX Live 2020+ (`tlmgr install ieeetran`)
- MiKTeX 2.9+ (auto-installed on first compile)
- Overleaf (pre-installed)

---

*End of final_publication_checklist.md | 2026-07-09*
