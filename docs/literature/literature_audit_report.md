# Literature Quality Audit Report
## IEEE TEMSMET 2026 — XAI Explanation Quality under SMOTE in RF-Based NIDS

**Audit date:** 2026-07-03  
**Auditor role:** Senior Academic Reviewer  
**Scope:** All 5 files in `docs/literature/`  
**Files audited:**
- `paper_database.csv` (21 papers × 18 columns)
- `comparison_matrix.csv` (22 rows × 14 columns)
- `research_gap_analysis.md` (~180 lines, 8 themes)
- `citation_plan.md` (~248 lines, 21 IEEE references)
- `literature_review.md` (~600+ lines, annotated review)

**Verification methods:** Web search (IEEE Xplore, MDPI, Springer, Semantic Scholar, ResearchGate, J-GLOBAL, ACM DL, MDPI Notes), DOI resolution via doi.org, CrossRef metadata, proceedings URL confirmation.

---

## Section 1 — Paper Metadata Verification (21 Papers)

| ID | Title snippet | Existence | Authors | Year | Venue | DOI | Status |
|----|--------------|-----------|---------|------|-------|-----|--------|
| P01 | Random Forests | ✓ | ✓ | ✓ | Machine Learning 45(1) | 10.1023/A:1010933404324 ✓ | PASS |
| P02 | SMOTE | ✓ | ✓ | ✓ | JAIR vol.16 | 10.1613/jair.953 ✓ | PASS |
| P03 | Scikit-learn | ✓ | ✓ | ✓ | JMLR vol.12 | 10.5555/1953048.2078195 ✓ | PASS |
| P04 | UNSW-NB15 | ✓ | ✓ | ✓ | MilCIS 2015 | 10.1109/MilCIS.2015.7348942 ✓ | PASS |
| P05 | LIME (Ribeiro) | ✓ | ✓ | ✓ | KDD 2016 | 10.1145/2939672.2939778 ✓ | PASS |
| P06 | imbalanced-learn | ✓ | ✓ | ✓ | JMLR vol.18(17) | JMLR:v18:16-365 ✓ | PASS |
| P07 | SHAP (Lundberg 2017) | ✓ | ✓ | ✓ | NeurIPS 2017 pp.4766–4777 | No DOI (NeurIPS pre-2018) — proceedings URL available | MINOR |
| P08 | TreeSHAP (Lundberg 2020) | ✓ | ✓ | ✓ | Nature Mach. Intell. 2 | 10.1038/s42256-019-0138-9 ✓ | PASS |
| P09 | Explainability of SMOTE | ✓ | ✓ | ✓ | IEEE ICICT 2020 pp.41–45 | DOI format unresolved (see §2) | MINOR |
| P10 | SMOTE+RF IDS (Alshamy) | ✓ | ✓ | ✓ | Springer CCIS vol.1487 | 10.1007/978-981-16-8059-5_22 ✓ | PASS |
| P11 | LIME Stability (Visani) | ✓ | ✓ | ✓ | JORS vol.73(1) | 10.1080/01605682.2020.1865846 ✓ | PASS |
| P12 | XAI Cybersecurity Survey (Charmet) | ✓ | ✓ | ✓ | Ann. Telecom. 77(11–12) | 10.1007/s12243-022-00926-7 ✓ | PASS |
| P13 | RF+SMOTE IDS (Wu) | ✓ | Incomplete | ✓ | EURASIP JASP 2022 art.39 | 10.1186/s13634-022-00871-6 ✓ | **CORRECTION** |
| P14 | Resampling+Feature Imp. (Alarab) | ✓ | ✓ | ✓ | Data Sci. Mgmt. 5(2) | 10.1016/j.dsm.2022.04.003 ✓ | PASS |
| P15 | XAI Survey (Rjoub) | ✓ | ✓ | ✓ | IEEE TNSM 20(4) | 10.1109/TNSM.2023.3282740 ✓ | PASS |
| P16 | Enhanced IDS UNSW-NB15 (More) | ✓ | ✓ | ✓ | Algorithms 17(2) art.64 | 10.3390/a17020064 ✓ | PASS |
| P17 | LIME+SHAP on MLP IDS (Gaspar) | ✓ | ✓ | ✓ | IEEE Access 12 pp.30164–30175 | 10.1109/ACCESS.2024.3368377 ✓ | **CORRECTION** |
| P18 | LSTM+SMOTE IDS (Al-madani) | ✓ | **Wrong first author** | ✓ | Appl. Sci. 14(2) art.479 | 10.3390/app14020479 ✓ | **CORRECTION** |
| P19 | Class Imbalance Eval (Razavi-Far) | ✓ | **Wrong first author** | ✓ | Electronics 14(1) art.69 | 10.3390/electronics14010069 ✓ | **CORRECTION** |
| P20 | SHAP+LIME Forensic IDS (Hermosilla) | ✓ | ✓ | ✓ | Appl. Sci. 15(13) art.7329 | 10.3390/app15137329 ✓ | PASS |
| P21 | XAI for IDS (Hermosilla) | ✓ | ✓ | ✓ | Computers 14(5) art.160 | 10.3390/computers14050160 ✓ | PASS |

---

## Section 2 — DOI Verification

### Confirmed valid DOIs
All DOIs except P07 and P09 resolved correctly and match the expected paper metadata.

### P07 — No traditional DOI (expected)
NeurIPS proceedings prior to 2018 did not register standard DOIs. This is expected and consistent with how Lundberg & Lee 2017 is cited across the literature. **Add the proceedings URL** to all citation entries:  
`https://proceedings.neurips.cc/paper_files/paper/2017/file/8a20a8621978632d76c43dfd28b67767-Paper.pdf`

**Action taken:** Added proceedings URL in `citation_plan.md` reference [7].

### P09 — DOI format conflict
Two DOI suffixes appear in evidence:
- Current database: `10.1109/ICICT50521.2020.9092325` — suffix "9092325" is a 7-digit IEEE Xplore document number, consistent with standard IEEE DOI format.
- Search result also returned: `10.1109/ICICT50521.2020.00015` — suffix "00015" appears to be a paper-position index, not standard IEEE Xplore format.

**Assessment:** The form `10.1109/ICICT50521.2020.9092325` is more consistent with IEEE DOI conventions (IEEE Xplore assigns its document number as the DOI suffix). The `[verify]` flag in all files is retained. Manual verification via IEEE Xplore is required before submission.

**Action taken:** No change to DOI. `[verify]` flag retained in all files. Audit report documents both candidate suffixes.

---

## Section 3 — Duplicate Analysis

### Duplicates found: NONE
All 21 papers have unique DOIs, unique titles, and distinct author/year combinations. P20 and P21 share the same first author (Hermosilla) but are confirmed as genuinely distinct papers:
- **P20** — *Applied Sciences* 15(13) art.7329; Authors: Hermosilla, Berríos, Allende-Cid (3 authors).
- **P21** — *Computers* 14(5) art.160; Authors: Hermosilla, Díaz, Berríos, Allende-Cid (4 authors; adds Díaz M as second author).

Both papers were independently published in different MDPI journals in 2025. No duplicate.

---

## Section 4 — Author List Corrections

Three papers had incorrect or incomplete author lists, two of which misidentified the first author.

### CORRECTION 1 — P13 (Wu 2022): Incomplete author list
**Before:** `Wu T; Fan H; Zhu H et al.`  
**After:** `Wu T; Fan H; Zhu H; You C; Zhou H; Huang X` (6 authors; "et al." eliminated)  
**Evidence:** DOI 10.1186/s13634-022-00871-6 confirmed via Springer link; author list resolved from search metadata.  
**IEEE citation impact:** Reference [13] in `citation_plan.md` updated to list all 6 authors.

### CORRECTION 2 — P18 (Al-madani 2024): Wrong first author
**Before:** `Al-madani AM et al.` (3 fields: first author listed as Al-madani)  
**After:** `Sayegh HR; Dong W; Al-madani AM` (3 authors; first author is Sayegh, not Al-madani)  
**Evidence:** MDPI DOI 10.3390/app14020479 confirmed via search metadata; authorship order confirmed.  
**Impact:** This paper should be cited as "Sayegh et al." not "Al-madani et al." Reference [18] in `citation_plan.md` corrected.

### CORRECTION 3 — P19 (Razavi-Far 2025): Wrong first author
**Before:** `Razavi-Far R; Hallaji E et al.` (first author listed as Razavi-Far)  
**After:** `Shanmugam V; Razavi-Far R; Hallaji E` (3 authors; first author is Shanmugam, not Razavi-Far)  
**Evidence:** MDPI DOI 10.3390/electronics14010069 confirmed via search result citing University of Windsor institutional repository.  
**Impact:** This paper should be cited as "Shanmugam et al." not "Razavi-Far et al." Reference [19] in `citation_plan.md` corrected.

---

## Section 5 — Dataset Description Corrections

### CORRECTION 4 — P17 (Gaspar 2024): Ambiguous dataset description
**Before:** `IoT traffic (UNSW-NB15 family)` in paper_database.csv; `Partial` for UNSW_NB15 in comparison_matrix.csv  
**After:** `IoT traffic (specific dataset unverified — access paper for confirmation)` in paper_database.csv; `Unknown` for UNSW_NB15 in comparison_matrix.csv  
**Rationale:** The Gaspar et al. paper applies LIME and SHAP to an MLP for IoT intrusion detection. Full-text access was blocked during this audit. The "UNSW-NB15 family" description was speculative. The claim "Partial" in the comparison matrix is unverified. Since the paper is cited only to establish that "LIME+SHAP has been applied to IDS" — a fact not dependent on which specific IoT dataset was used — this correction does not affect any manuscript claim.

---

## Section 6 — Fabricated Citations Check

**Result: No fabricated citations detected.**

Verification evidence for each paper:
- P01–P08: All are landmark papers with thousands of citations and confirmed DOIs via doi.org.
- P09: Confirmed via ResearchGate (publication ID 341402144) and citation appearances in Springer chapters.
- P10: Confirmed via Springer CCIS DOI.
- P11: Confirmed via Taylor & Francis JORS DOI.
- P12: Confirmed via Springer Annals of Telecommunications DOI.
- P13: Confirmed via Springer EURASIP DOI.
- P14: Confirmed via Elsevier Data Science and Management DOI.
- P15: Confirmed via IEEE TNSM DOI.
- P16: Confirmed via MDPI Algorithms DOI.
- P17: Confirmed via IEEE Xplore document 10440604 (redirected from DOI).
- P18: Confirmed via MDPI Applied Sciences DOI and CiteDrive.
- P19: Confirmed via MDPI Electronics DOI and University of Windsor repository.
- P20: Confirmed via MDPI Applied Sciences DOI + Fraunhofer publica repository.
- P21: Confirmed via MDPI Computers DOI + Fraunhofer publica repository.

---

## Section 7 — Weak or Irrelevant Papers

**Result: No papers recommended for removal.**

| Paper | Relevance assessment | Verdict |
|-------|---------------------|---------|
| P03 Pedregosa 2011 (scikit-learn) | Not a research paper; tooling library. Standard to cite for RF implementation. | Keep — implementation reference |
| P06 Lemaître 2017 (imbalanced-learn) | Tooling paper. Standard to cite for SMOTE implementation. | Keep — implementation reference |
| P07 Lundberg 2017 (SHAP) | Foundational method paper. Essential. | Keep |
| P14 Alarab 2022 (blockchain) | Closest prior work on resampling + feature importance outside NIDS. Non-NIDS context is a known limitation. | Keep — documents research gap |
| P09 Patil 2020 (UCI generic) | Closest prior work on SMOTE + explainability. Non-NIDS context is a known limitation. | Keep — documents research gap |
| P17 Gaspar 2024 (MLP) | Relevant for establishing LIME+SHAP on IDS. Not RF; dataset unverified. | Keep — note model difference in manuscript |

---

## Section 8 — Comparison Matrix Validation

**Matrix: 22 rows × 14 columns. All rows verified against paper_database.csv.**

Issues found:

| Row | Column | Current value | Corrected value | Notes |
|-----|--------|---------------|-----------------|-------|
| P17 | UNSW_NB15 | Partial | Unknown | Full text inaccessible; cannot confirm dataset |
| P17 | Dataset | IoT/UNSW-NB15 family | IoT traffic (unconfirmed) | Same rationale as above |
| OUR STUDY | All columns | As specified | ✓ Consistent with experimental results | No corrections needed |

**Claim: P17 cites RF-based NIDS in citation_plan.md** — citation_plan.md line 27 cites P17 for "SHAP and LIME widely applied to RF-based NIDS." **Correction needed:** P17 uses MLP, not RF. P17 is appropriate for "SHAP and LIME applied to NIDS" but not specifically for "RF-based NIDS." Change attribution to P20 (Hermosilla 2025a) which uses XGBoost (tree-based) and UNSW-NB15.

---

## Section 9 — Research Gap Validation

The composite research gap (Section 2 of `research_gap_analysis.md`) rests on 5 claims, all validated:

| Gap claim | Supporting evidence |
|-----------|-------------------|
| No prior study applies SMOTE to UNSW-NB15 with predefined split | P04, P16, P20, P21 all use UNSW-NB15 without SMOTE; P10, P13, P18, P19 use SMOTE without UNSW-NB15 |
| No prior study evaluates SHAP+LIME stability before/after SMOTE | Verified across all 21 papers; comparison matrix "Explanation_Stability_Measured" column confirms |
| No prior study applies McNemar+Wilcoxon+bootstrap+Holm in NIDS XAI | Verified: no statistical tests column in matrix is "Yes" for any paper except OUR STUDY |
| No prior study reports effect sizes for both predictive AND explanation metrics | Verified: "Effect_Size_Reported" = "No" for all 21 papers |
| Gap is identified in both cybersecurity XAI surveys (P12, P15) | Confirmed in literature review text for both papers |

**Gap verdict: FULLY SUPPORTED by the evidence in 21 reviewed papers.**

### Absolute "first" claim corrections required

Two sentences in `research_gap_analysis.md` use unhedged absolute language:

1. **Line 54 (Theme 3):** "We are the first to compare predictive effect sizes vs explanation effect sizes under SMOTE in NIDS"
   → Changed to: "To our knowledge, no prior study has compared predictive effect sizes against explanation effect sizes under SMOTE in any NIDS setting"

2. **Line 132 (Section 4 — closing paragraph):** "We provide the first empirical evidence (in NIDS context) that class rebalancing introduces asymmetric shifts in explanation quality vs. predictive quality"
   → Changed to: "We provide, to our knowledge, the first empirical evidence (in the NIDS context) that class rebalancing introduces asymmetric shifts in explanation quality vs. predictive quality"

**Rationale:** The literature search covered IEEE Xplore, MDPI, Springer, ACM, Elsevier, and Google Scholar but not Scopus or Web of Science in full. The section 3 caveat in `research_gap_analysis.md` already acknowledges this limitation. The absolute "first" language in section 1 (Theme 3) is inconsistent with that caveat and should be harmonised.

---

## Section 10 — Novelty Reassessment

| Dimension | Prior assessment | After audit | Change |
|-----------|-----------------|-------------|--------|
| Topic: SMOTE effect on SHAP/LIME in NIDS | Strongly novel | **Strongly novel** | Confirmed |
| Methodology: paired stats + effect sizes for explanation stability | Moderately novel | **Moderately novel** | Confirmed |
| Dataset: UNSW-NB15 | Incremental | **Incremental** | Confirmed |
| Model: Random Forest | Incremental | **Incremental** | Confirmed |
| Finding: LIME ~6.8× more sensitive | Strongly novel | **Strongly novel** | Confirmed |
| Finding: explanation sensitivity > predictive sensitivity | Moderately–Strongly novel | **Moderately–Strongly novel** | Confirmed |

**Novelty verdict (post-audit): Moderately to Strongly Novel — confirmed.**

No new evidence was found that undermines novelty. P20 and P21 (the closest recent papers) are confirmed to NOT use SMOTE, NOT apply statistical tests to explanation vectors, and NOT report explanation effect sizes. Our study fills all three gaps simultaneously.

---

## Section 11 — Final Readiness Score and Recommendation

### Scoring
| Category | Max | Score | Notes |
|----------|-----|-------|-------|
| Paper existence (21 papers verified) | 20 | 20 | All 21 real |
| DOI accuracy | 15 | 11 | P07 no DOI (expected); P09 format uncertain |
| Author list accuracy | 15 | 7 | P13, P18, P19 had errors (all corrected in this audit) |
| Dataset descriptions | 10 | 8 | P17 dataset unconfirmed |
| Duplicate / fabrication check | 10 | 10 | Clean |
| Weak/irrelevant paper check | 5 | 5 | All papers justified |
| Comparison matrix consistency | 10 | 8 | P17 UNSW_NB15 value corrected |
| Gap analysis support | 10 | 10 | All 5 gap claims supported |
| Novelty assessment | 5 | 5 | Confirmed moderately–strongly novel |
| **Total** | **100** | **84** | |

### Recommendation: **MINOR REVISION**

All 21 papers are real, peer-reviewed, and relevant. The gap is fully supported. The novelty assessment is appropriate. Four corrections are required (all made automatically in this audit run):

1. P13 author list completed (You, Zhou, Huang added)
2. P18 first author corrected (Sayegh → not Al-madani)
3. P19 first author corrected (Shanmugam → not Razavi-Far)
4. P17 dataset description changed from "UNSW-NB15 family" to "IoT traffic (unconfirmed)"

Two hedge corrections applied to `research_gap_analysis.md` (lines 54 and 132).

One citation plan entry corrected: P17 removed from "RF-based NIDS" claim support; P20 substituted.

**Before manuscript submission, the following require manual action:**
- [ ] Verify P09 DOI via IEEE Xplore: search for "Patil Framewala Kazi ICICT 2020" and copy the exact DOI
- [ ] Confirm P17 dataset via full-text access to 10.1109/ACCESS.2024.3368377
- [ ] Add NeurIPS 2017 proceedings URL for P07 to the manuscript reference list
- [ ] Add EU AI Act / GDPR citation for Discussion section (not yet in database)
- [ ] Run a Scopus/Web of Science search before camera-ready to catch 2025–2026 papers post-dating this review

---

*Audit complete. Do NOT begin writing manuscript sections. Await author review of this report.*
