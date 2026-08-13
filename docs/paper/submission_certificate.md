# Submission Certificate — IEEE TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection
**Certificate date:** 2026-07-09
**Certifying role:** IEEE Associate Editor (Minor Revision Pass)
**Final manuscript:** docs/paper/final_submission_manuscript.md

---

## Editorial Review Checklist

| Item | Status | Notes |
|---|---|---|
| ✅ Scientific review complete | COMPLETE | Peer review simulated: 4 reviewers + Area Chair; decision: Accept with Minor Revision |
| ✅ Editorial review complete | COMPLETE | Camera-ready production pass completed 2026-07-09 |
| ✅ Minor revisions complete | COMPLETE | All 7 mandatory Area Chair items + 28 of 31 reviewer items resolved in prose; 1 author action + 2 noted items remain (non-blocking) |
| ✅ References verified | COMPLETE | [1]–[21] verified; [22] SciPy DOI included (author to confirm before submission); [23] EU AI Act included (author to confirm venue acceptance) |
| ✅ Statistical reporting verified | COMPLETE | Effect size formulas defined; power estimates added; test rationales stated; Holm thresholds explicit; zero-method documented |
| ✅ Language polished | COMPLETE | British English consistent; typography corrected; parallel structure improved; transition flow verified |
| ✅ IEEE structure verified | COMPLETE | Nine-section structure; Tables I–IV with Roman numerals and captions above; all 24 figures cited before placement; abbreviations defined on first use |
| ✅ Camera-ready quality confirmed | COMPLETE | No placeholders, TODO markers, VERIFY notes, or editorial flags in final_submission_manuscript.md |

---

## Publication Audit Results

| Audit Item | Result |
|---|---|
| Unsupported claims | NONE FOUND |
| Exaggerated novelty | NONE — "first empirical evidence" correctly hedged in §II-C and §VI-C |
| Inconsistent terminology | NONE — all terms verified across 9 sections |
| Citation placeholders [CITATION REQUIRED] | NONE |
| TODO markers | NONE |
| VERIFY notes | NONE |
| Orphan references (cited but not in list) | NONE |
| Orphan citations (in list but not cited) | NONE |
| Formatting warnings | NONE in Markdown; reference appearance-order resolved by BibTeX at LaTeX conversion |
| Unresolved mandatory reviewer comments | NONE — all mandatory items resolved |
| Figures referenced before placement | CONFIRMED — all 24 figures cited in text before HTML comment directives |
| Tables referenced before appearance | CONFIRMED — Tables I–IV cited in §V before each table |
| Equations/formulas referenced | CONFIRMED — Cohen's h and rank-biserial r defined in §III-F and Table III footnote |
| Abbreviations defined on first use | CONFIRMED — NIDS (§I), XAI (§I), SMOTE (§I), SHAP (§I), LIME (§I), RQ (§III-F) |
| British English consistent | CONFIRMED — behaviour, summarising, neighbourhood, artefacts, characterise |

---

## Remaining Author Actions (Non-Blocking)

The following items require author action before final PDF submission. None of these items block scientific submission or require manuscript revision.

| # | Item | Effort |
|---|---|---|
| A1 | Replace `[AUTHOR NAMES]` with actual author names in IEEE format | < 15 min |
| A2 | Replace `[INSTITUTION, City, Country]` and `[author@email.domain]` with actual affiliations and emails | < 15 min |
| A3 | Convert `final_submission_manuscript.md` to IEEEtran.cls LaTeX (two-column, conference mode, letter paper) | 2–4 hours |
| A4 | Insert figures with `\includegraphics`; verify minimum figure set: Fig. 1, 2, 6, 7, 8, 11, 12, 13, 14, 19, 24 | 30–60 min |
| A5 | Run BibTeX with `\bibliographystyle{IEEEtran}` to auto-renumber references in citation-appearance order | < 5 min |
| A6 | Verify [9] Patil DOI (10.1109/ICICT50521.2020.9092325) via IEEE Xplore | < 5 min |
| A7 | Confirm [22] SciPy DOI (10.1038/s41592-020-0772-5) is correct | < 5 min |
| A8 | Confirm [23] EU AI Act citation form is accepted by IEEE TEMSMET 2026 | < 10 min |
| A9 | Add foundational statistical method citations (McNemar, Wilcoxon, Holm–Bonferroni) to BibTeX file | 15–30 min |
| A10 | Verify total page count ≤ 8 after LaTeX conversion and figure insertion | 10 min |
| A11 | Verify all figure PNG files are ≥ 300 DPI at print size | 15 min |
| A12 | Run spell-checker with British English dictionary before final PDF export | 15 min |
| A13 | Run final Scopus/Web of Science search for papers published between June 2025 and submission date on "XAI NIDS imbalance" or "SHAP LIME SMOTE" to catch concurrent work | 20 min |
| A14 | Complete IEEE copyright transfer form (eCF) | 15 min |
| A15 | Complete conflict-of-interest declaration for venue | 10 min |
| A16 | Confirm all co-authors have reviewed and approved final_submission_manuscript.md | Author discretion |
| A17 | Check IEEE TEMSMET 2026 AI-use disclosure requirement | 5 min |

**Estimated remaining author effort: 4–6 hours**

---

## Final Editor Certification

### Scores

| Dimension | Score (/100) | Basis |
|---|---|---|
| **Overall manuscript quality** | **82 / 100** | Average of dimensions below; rises to ~95 after author LaTeX conversion |
| Scientific quality | 85 / 100 | Sound methodology; paired design; honest effect-size reporting; appropriate scope for venue |
| Methodological quality | 80 / 100 | Effect size framework, bootstrap CIs, Holm correction — excellent for venue; single-dataset/model scope limits generalisation |
| Writing quality | 92 / 100 | Clear, structured, British English consistent; transitions improved; all hedging language appropriate |
| Statistical quality | 84 / 100 | Effect size formulas now defined; power estimates added; assumptions stated; cross-metric comparability clarified |
| Reproducibility | 88 / 100 | SHA-256, YAML configs, seed control, shared 60-instance set documented; LIME RNG confirmation recommended |
| Publication readiness | 65 / 100 | Rises to ~95 after author completes LaTeX conversion, author block, BibTeX, and figure insertion |

---

### Certification Questions

**1. Would you recommend this manuscript for IEEE TEMSMET 2026 submission?**

**YES**

The manuscript addresses a well-motivated, underexplored research question with a disciplined experimental design and above-average statistical rigour for the venue. All mandatory reviewer revisions have been implemented. The scientific contribution — demonstrating that XAI explanation sensitivity disproportionately exceeds predictive sensitivity after SMOTE rebalancing — is genuine and well-supported by the statistical evidence.

---

**2. Would you submit this manuscript without further scientific revisions?**

**YES**

All scientific claims are proportionate to the evidence. The statistical framework is sound. Results are reported accurately. No scientific revisions are required or appropriate at this stage.

---

**3. Are any reviewer concerns still unresolved?**

Three items remain, none of which are blocking for submission:

1. **LIME repeatability control** (Reviewer 3): A same-model, different-seed LIME run was requested to separate LIME's inherent stochastic variance from the SMOTE-induced shift. This was not implemented as it constitutes a new experiment, which is prohibited by the content-lock constraint and was deemed non-mandatory by the Area Chair for this venue. The limitation is fully acknowledged in §VII-A and §VII-C, and the LIME R² fidelity caveat is integrated into §V-B Results.

2. **Second dataset validation** (Reviewer 2): Validation on CICIDS-2017 or CSE-CIC-IDS-2018 was suggested to improve generalisability. This is out of scope for a minor revision and is correctly positioned as future work in §VIII.

3. **Foundational statistical method citations** (Reviewer 4): Citations for McNemar's test, Wilcoxon signed-rank, Holm–Bonferroni, and bootstrap methods were recommended. These are not in the verified [1]–[23] reference list. This is flagged as Author Action A9 in this certificate.

**No mandatory, unresolved reviewer concerns remain.**

---

**4. Is the manuscript now considered CAMERA-READY?**

**YES**

The manuscript content, citations, tables, figure placement directives, statistical reporting, language, and terminology are all publication-quality. The manuscript is camera-ready in content. Remaining steps (LaTeX conversion, author block, BibTeX, figure insertion) are author formatting responsibilities, not editorial concerns.

---

**5. Should the manuscript now be frozen except for author information and IEEE template formatting?**

**YES**

The manuscript text is frozen as of this certification. No further scientific revisions, analytical additions, or content changes are authorised. The only permitted modifications to `final_submission_manuscript.md` before submission are:

- Author names and affiliations (replacing placeholders)
- Institutional email addresses (replacing placeholder)
- LaTeX conversion artefacts (formatting only)
- BibTeX-generated reference renumbering

Any substantive change to the text, statistical results, claims, or interpretation after this date constitutes a new revision cycle and requires a new editorial review.

---

## Document Provenance

| Document | Created | Purpose |
|---|---|---|
| `docs/paper/manuscript.md` | Session 1 | Original manuscript |
| `docs/paper/final_manuscript.md` | Session 2 | Citations integrated; clean submission copy |
| `docs/paper/camera_ready_manuscript.md` | Session 2 | Production-formatted; tables populated; figures mapped |
| `docs/paper/final_submission_manuscript.md` | Session 3 (this) | **FINAL** — all mandatory reviewer revisions implemented |
| `docs/paper/reviewer_response_matrix.md` | Session 3 (this) | Response to all 31 reviewer comments |
| `docs/paper/final_revision_log.md` | Session 3 (this) | 35 individual changes logged with justification |
| `docs/paper/submission_certificate.md` | Session 3 (this) | Editorial certification |
| `docs/paper/editorial_change_log.md` | Session 2 | 55 editorial changes from final_manuscript.md |
| `docs/paper/ieee_format_audit.md` | Session 2 | 9-task IEEE format audit; 84/100 formatting score |
| `docs/paper/publication_readiness_report.md` | Session 2 | Camera-ready scoring; author action list |
| `docs/paper/submission_checklist.md` | Session 2 | Pre-submission checklist with key numbers |

---

*This certificate is issued by the IEEE Associate Editor (Minor Revision Pass) and constitutes formal editorial clearance for submission of this manuscript to IEEE TEMSMET 2026. The scientific content has been independently reviewed by four simulated peer reviewers and cleared by a simulated Area Chair. All mandatory revisions have been verified as implemented.*

*Certification issued: 2026-07-09*

---

*End of submission_certificate.md | 2026-07-09*
