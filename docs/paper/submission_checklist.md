# Pre-Submission Checklist — TEMSMET 2026
**Paper:** Impact of SMOTE-Based Class Rebalancing on SHAP and LIME Explanation Quality in Random Forest Network Intrusion Detection
**Venue:** IEEE TEMSMET 2026
**Date prepared:** 2026-07-09
**Status key:** [x] DONE | [ ] AUTHOR ACTION REQUIRED | [~] VERIFY BEFORE SUBMISSION

---

## 1. Manuscript Content

- [x] Title updated to approved version (RC-08)
- [x] Abstract replaced with approved 253-word IEEE-style version (RC-09)
- [x] Keywords reduced to 8 IEEE index terms (RC-13)
- [x] All 37 `[CITATION REQUIRED]` placeholders replaced (RC-04)
- [x] Missing Breiman [1] citation inserted in §III-D (RC-01)
- [x] C19 cites `[20, 21]` to prevent Hermosilla 2025b orphan (RC-05)
- [x] "first empirical evidence" claim hedged with "To the best of the authors' knowledge" (RC-06)
- [x] References section replaced with full formatted list [1]–[23] (RC-07)
- [x] scipy added as [22] (RC-02)
- [x] EU AI Act added as [23] (RC-03)
- [ ] **AUTHOR:** Replace `[AUTHOR NAMES — DO NOT PUBLISH WITH PLACEHOLDER]` with actual author names
- [ ] **AUTHOR:** Replace `[INSTITUTION — DO NOT PUBLISH WITH PLACEHOLDER]` with actual affiliation(s)

---

## 2. Reference Verification

- [~] **[9] Patil 2020:** Verify DOI `10.1109/ICICT50521.2020.9092325` via IEEE Xplore before submission. Two candidate DOI forms were identified during audit. Flag `[⚠ DOI unverified]` will appear in the final PDF if not resolved.
- [~] **[17] Gaspar 2024:** Dataset used in cited paper is IoT traffic (specific dataset unverified). The citation is used only to establish "LIME+SHAP applied to IDS," which is independent of dataset. No correction required, but note this in the camera-ready if queried.
- [~] **[22] scipy (Virtanen 2020):** Not in verified literature database. DOI `10.1038/s41592-020-0772-5` appears correct based on Nature Methods. Verify before submission and remove the `[⚠ Verify before submission]` flag.
- [~] **[23] EU AI Act:** Not in verified literature database. Verify citation form is acceptable to the venue. If venue requires peer-reviewed publications only, replace with an academic survey of AI regulation (e.g., Corrêa et al. 2023 or equivalent).
- [~] **[7] Lundberg & Lee 2017 (NeurIPS):** NeurIPS 2017 proceedings have no registered DOI. URL is provided. Confirm with venue whether URL-only citation is acceptable or whether an arXiv DOI should be used.
- [x] Author corrections applied: [18] Sayegh as first author; [19] Shanmugam as first author
- [x] Author list expansions applied: [3], [8], [12], [15] expanded to first-6 + et al.
- [x] JMLR URLs added for [3] (Pedregosa) and [6] (Lemaître)
- [x] NeurIPS proceedings URL added for [7] (Lundberg & Lee 2017)

---

## 3. IEEE Formatting

- [ ] **AUTHOR:** Convert manuscript from Markdown to IEEE double-column LaTeX (IEEEtran.cls) or Word template
- [ ] **AUTHOR:** Verify total page count is within 6–8 pages for regular paper
- [ ] **AUTHOR:** Insert actual figure files (all 24+ figures referenced in text are in `outputs/figures/`)
- [ ] **AUTHOR:** Insert actual tables (Table I: per-class metrics; Table II: bootstrap CIs; Table III: effect sizes; Table IV: hypothesis test summary) — source data in `outputs/tables/` and `outputs/reports/`
- [ ] **AUTHOR:** Verify all cross-references (Fig. N, Table N) match inserted figure/table numbers
- [ ] **AUTHOR:** Apply IEEE sentence-case to all reference titles (not title-case): e.g., "Random forests" not "Random Forests"
- [ ] **AUTHOR:** Convert reference hyperlinks to `https://doi.org/[DOI]` format for final PDF
- [ ] **AUTHOR:** Remove all `[⚠ ...]` editorial flags from the final submitted PDF — these are author-action notes only

---

## 4. Data and Reproducibility

- [x] Global random seed 42 set via `configs/*.yaml` and applied before all stochastic operations
- [x] UNSW-NB15 predefined train/test split used without re-splitting
- [x] All pipeline outputs SHA-256 verified before statistical analysis
- [x] Full pipeline configuration stored in `configs/*.yaml`
- [ ] **AUTHOR:** Confirm whether the repository will be made public (recommended for IEEE reproducibility standards)
- [ ] **AUTHOR:** If public repo: add DOI via Zenodo or equivalent and cite in the paper

---

## 5. Ethics and Compliance

- [x] Only publicly available benchmark dataset used (UNSW-NB15)
- [x] No human subjects data; no IRB required
- [ ] **AUTHOR:** Confirm with IEEE TEMSMET 2026 whether an AI-use disclosure statement is required (some IEEE venues require disclosure of AI-assisted writing tools)
- [ ] **AUTHOR:** Confirm all co-authors have reviewed and approved the final manuscript

---

## 6. Novelty and Claim Verification

- [x] Absolute "first" claim hedged: "To the best of the authors' knowledge..." (§VI-C)
- [x] P17 (Gaspar 2024) cited only for "LIME+SHAP applied to IDS" claim, not for UNSW-NB15 use
- [x] scipy [22] included but flagged for verification
- [x] [21] Hermosilla 2025b bundled into C19 to prevent orphan reference
- [ ] **AUTHOR (optional):** Run final Scopus/Web of Science search for papers published between June 2025 and submission date to catch any new competitor work on XAI stability in NIDS

---

## 7. Final Read-Through

- [ ] **AUTHOR:** Read full manuscript aloud for grammatical errors and tense consistency (present tense for contributions; past tense for methodology and results)
- [ ] **AUTHOR:** Verify all section cross-references in §I ("Section II reviews related work ... Section IX concludes") remain correct after LaTeX conversion
- [ ] **AUTHOR:** Confirm "Sections VI–VIII discuss findings" is correct (§VI Discussion, §VII Limitations, §VIII Future Work, §IX Conclusion)
- [ ] **AUTHOR:** Verify all figure caption text and table captions are complete
- [ ] **AUTHOR:** Run spell-checker with British English dictionary (the manuscript uses British spellings: "behaviour", "rebalancing", "summarising", "neighbourhood")

---

## 8. Submission Portal

- [ ] **AUTHOR:** Create submission account at IEEE TEMSMET 2026 submission portal
- [ ] **AUTHOR:** Upload: (a) manuscript PDF, (b) cover letter (if required), (c) list of suggested reviewers (if required)
- [ ] **AUTHOR:** Confirm author information matches IEEE membership details for each co-author
- [ ] **AUTHOR:** Complete conflict-of-interest declaration

---

## Quick Reference — Key Numbers for Cover Letter / Author Statement

| Metric | Value |
|---|---|
| Training set (Baseline) | 175,341 instances, 10 classes |
| Training set (SMOTE) | 560,000 instances, 10 classes balanced |
| Test set | 82,332 instances (unchanged) |
| Max imbalance ratio | 430.77:1 (Worms: 130 vs Normal: 56,000) |
| Baseline accuracy | 0.7543 (95% CI [0.7516, 0.7574]) |
| SMOTE accuracy | 0.7161 (95% CI [0.7129, 0.7191]) |
| Accuracy effect size (Cohen's h) | −0.0868 (negligible) |
| SHAP effect size (rank-biserial r) | 0.3259 (medium) |
| LIME effect size (rank-biserial r) | 0.5947 (large) |
| LIME/predictive effect ratio | 6.8× |
| All 4 hypothesis tests | Reject H₀ after Holm–Bonferroni |
| Verified references | [1]–[21] (21 entries) |
| Pending references | [22] scipy, [23] EU AI Act |
| Total references | 23 |

---

*End of submission_checklist.md | 2026-07-09*
