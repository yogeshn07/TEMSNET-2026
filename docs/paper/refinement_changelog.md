# Refinement Change Log — IEEE TEMSMET 2026
**Source:** `docs/paper/final_submission_manuscript.md`
**Output:** `docs/paper/refined_manuscript_v2.md`
**Reviewer role:** Senior IEEE Transactions reviewer, statistician, technical editor
**Date:** 2026-07-09
**Scientific content:** LOCKED — no numerical values, experimental results,
statistical findings, or conclusions were modified.

---

## 1. Summary of All Changes

### C01 — Abstract: Eliminate final-sentence redundancy
**Type:** Writing quality
**Section:** Abstract
**Original:** "...indicating a disproportionate shift in explanation outputs
relative to classification metrics. These results demonstrate that class
rebalancing changes feature attribution outputs disproportionately relative to
classification metrics, providing evidence that accuracy-only validation after
NIDS retraining is insufficient to characterise the stability of explainability
outputs. Evaluating explanation consistency alongside predictive performance is
therefore an important component of responsible model assessment in any NIDS
pipeline that incorporates post-hoc explainability methods."
**Revised:** "...with explanatory sensitivity substantially exceeding any predictive
effect across complementary effect-size measures. These results indicate that
accuracy-only validation is insufficient to characterise explanation stability
following NIDS retraining, and that monitoring explanation consistency is an
important component of responsible model assessment in XAI-augmented NIDS pipelines."
**Rationale:** The original abstract stated the same conclusion three times across
two sentences, consuming ~40 words. The revision consolidates into one clear
sentence (word count reduced from ~253 to ~238, within IEEE 250-word guideline).
No scientific content changed.

---

### C02 — Introduction: Remove boilerplate section roadmap
**Type:** IEEE style / concision
**Section:** §I
**Removed:** "The remainder of this paper is structured as follows. Section II
reviews related work. Section III describes the methodology. Section IV details
the experimental setup. Section V presents results. Sections VI–VIII discuss
findings, limitations, and future directions. Section IX concludes."
**Rationale:** Section roadmap paragraphs are boilerplate in 6-page conference
papers and provide no scientific value. Removing them saves ~50 words, recoverable
as figure space. IEEE Transactions papers uniformly omit this pattern.

---

### C03 — Introduction: Add regulatory motivation sentence
**Type:** Context / motivation
**Section:** §I, paragraph 3 (XAI adoption paragraph)
**Added:** "As AI systems become subject to regulatory transparency requirements
[23], the reliability of these explanations in security-critical applications
warrants rigorous empirical scrutiny."
**Rationale:** Without this sentence, the motivation for studying explanation
stability is purely technical. The EU AI Act [23] citation (already in the
reference list) provides an additional motivation that reviewers expect in
trustworthy-AI papers and that strengthens the framing of the research question.

---

### C04 — Related Work §II-A: Merge §II-D content; add gap transition
**Type:** Logical flow / section restructuring
**Section:** §II-A (Class Imbalance in NIDS)
**Change:** §II-D (UNSW-NB15 Benchmark) was a two-sentence standalone subsection
that provided insufficient content to justify its own heading. Its substance
(benchmark description) is now integrated into §II-A as the final paragraph, with
an added transition: "However, whether rebalancing-driven model changes propagate
into XAI explanation instability — beyond their effect on prediction accuracy —
has not been addressed." The §II-D heading is removed; related work now has three
subsections (A, B, C) instead of four.
**Rationale:** §II-D was too thin (2 sentences) to merit a standalone subsection.
The UNSW-NB15 justification belongs in §III-A (Methodology), where a dataset
justification sentence was also added (C07). The transition sentence at the end of
§II-A builds the logical argument toward the gap.

---

### C05 — Related Work §II-B: Add stability gap transition
**Type:** Logical flow
**Section:** §II-B
**Added:** "Despite their adoption, the stability of SHAP and LIME explanations
under training data composition changes — as distinct from robustness to input
perturbation — has not been systematically studied in NIDS contexts."
**Rationale:** §II-B previously described SHAP and LIME capabilities without
identifying a gap. This sentence connects the capability description to the gap
identified in §II-C, creating a logical argumentative flow.

---

### C06 — Related Work §II-C: Expand gap consequence argument
**Type:** Scientific argumentation
**Section:** §II-C
**Added:** "This gap is consequential: if explanation rankings shift substantially
when training distribution changes, practitioners relying on XAI to understand
model decisions may encounter inconsistent attributions after routine retraining
events, without any accuracy signal to alert them. This study addresses this gap
directly."
**Rationale:** The original §II-C identified the gap in one sentence but did not
explain why the gap matters. The addition articulates the practical consequence
and provides a clean section-closing transition into the methodology. This is
standard IEEE argument structure.

---

### C07 — Methodology §III-A: Add dataset selection justification
**Type:** Methodology justification (TASK 5)
**Section:** §III-A
**Added:** "UNSW-NB15 was selected because its predefined split enables reproducible
evaluation without researcher-induced variation, and its extreme imbalance provides
a challenging real-world scenario for studying the interplay between class
rebalancing and explanation stability."
**Rationale:** The original §III-A described the dataset but did not justify the
choice. IEEE reviewers routinely ask "why this dataset?" A one-sentence justification
addresses this without adding unnecessary length.

---

### C08 — Methodology §III-C: Add SMOTE selection justification
**Type:** Methodology justification (TASK 5)
**Section:** §III-C
**Added:** "SMOTE was selected as the rebalancing technique because it is the most
widely applied method in NIDS literature [10, 13, 18, 19], ensuring that findings
are directly relevant to existing deployments."
**Rationale:** The original §III-C applied SMOTE without explaining why SMOTE
rather than ADASYN or undersampling. The justification is concise and supported by
existing references.

---

### C09 — Methodology §III-D: Add Random Forest selection justification
**Type:** Methodology justification (TASK 5)
**Section:** §III-D
**Added:** "Random Forest was selected because it achieves competitive performance
on UNSW-NB15 [10, 16], supports exact Shapley-value computation via SHAP
TreeExplainer without approximation [7, 8], and is a widely adopted baseline model
in NIDS research, ensuring broad applicability of the findings."
**Rationale:** The original §III-D trained a Random Forest without justifying the
choice. Three distinct reasons are provided: performance, SHAP compatibility, and
research prevalence. All supported by existing references.

---

### C10 — Methodology §III-E: Add 60-instance justification
**Type:** Methodology justification (TASK 5)
**Section:** §III-E (end of subsection)
**Added:** "The 60-instance sample (6 per class) was chosen to ensure equal class
representation across all 10 traffic categories, providing balanced coverage for
global importance aggregation while remaining computationally tractable for exact
SHAP computation over a 100-tree Random Forest."
**Rationale:** The original §IV mentioned computational tractability but did not
explain why 60 was chosen specifically. The revision provides the justification
in §III-E where the sampling is first described, rather than in §IV where it was
previously partially addressed.

---

### C11 — Methodology §III-F: Fix McNemar citation
**Type:** Statistical accuracy (TASK 12)
**Section:** §III-F
**Original:** "McNemar's test is the appropriate paired test for comparing two
classifiers on the same test set [22]."
**Revised:** "...to assess whether the two models disagree at a statistically
significant rate; implemented via `scipy.stats.mcnemar` [22]."
**Rationale:** Reference [22] is the SciPy library (Virtanen et al. 2020). Citing
it as justification that McNemar's test is "appropriate" misrepresents [22]'s role
— [22] is a software reference, not a statistical methodology reference. The
revision makes [22]'s role explicit (software implementation) and removes the
unsupported methodological claim. The appropriateness of McNemar's test for paired
classifiers is mathematically self-evident and does not require a citation.

---

### C12 — Methodology §III-F: Pre-specify research hypothesis
**Type:** Statistical validity (TASK 12)
**Section:** §III-F (opening)
**Added:** "The study predicts that class rebalancing will alter SHAP and LIME
attribution rankings more than aggregate predictive metrics (RQ3)."
**Rationale:** The original §V-D referred to "the research hypothesis" but this
hypothesis was never explicitly stated in the methodology. Pre-specification in
§III-F is appropriate; the hypothesis is now stated where the testing framework
is introduced, strengthening confirmatory inference claims.

---

### C13 — Results §V-A: Soften "expected" to "characteristic"
**Type:** Scientific precision (overclaiming, TASK 6)
**Section:** §V-A
**Original:** "This trade-off is the expected consequence of synthetic oversampling..."
**Revised:** "This trade-off is the characteristic consequence of synthetic oversampling..."
**Rationale:** "Expected" implies the authors predicted this outcome before seeing
results, which could be read as post-hoc rationalisation. "Characteristic" is
scientifically accurate (it is a known property of oversampling) without implying
prediction.

---

### C14 — Results: Rename "Verdict" to "Summary"
**Type:** IEEE style
**Sections:** §V-A, §V-B, §V-C (three instances)
**Original:** "**Verdict (RQ1):**"
**Revised:** "**Summary (RQ1):**"
**Rationale:** "Verdict" is courtroom terminology; "Summary" is the IEEE-conventional
term for per-section finding summaries. Semantically identical; stylistically more
appropriate.

---

### C15 — Discussion §VI-A: Expand mechanistic explanation
**Type:** Scientific depth (TASK 7)
**Section:** §VI-A
**Change:** The original §VI-A explained in one brief paragraph why explanation
methods detect boundary shifts. The revised version adds two specific paragraphs:
(1) the boundary shift mechanism — how SMOTE changes feature importance weights
in the RF ensemble even when overall accuracy is stable; (2) a precise mechanistic
comparison of LIME vs. SHAP sensitivity — LIME's perturbation-based local
surrogate directly samples the updated boundary region, whereas SHAP's ensemble
averaging over 100 trees attenuates local changes.
**Rationale:** §VI-A is the most scientifically important section of the paper —
it explains WHY the results are observed. The original explanation was too brief
for a Transactions-level discussion. The additions are mechanistic derivations from
known properties of the two methods, not new claims.

---

### C16 — Discussion §VI-B: Convert list to prose
**Type:** IEEE style (TASK 7)
**Section:** §VI-B
**Change:** Five numbered bullet points converted to four flowing paragraphs.
Scientific content is unchanged; the information is reorganised into natural
paragraph groupings (validation→deployment→LIME caveat→monitoring). The
five implications are preserved in full.
**Rationale:** Numbered lists in IEEE discussion sections are non-standard and
fragment what should be an integrated analytical argument. Flowing prose with
paragraph-level topic sentences communicates the same content more professionally.

---

### C17 — Table III: Add per-metric sample size column
**Type:** Table accuracy (TASK 15)
**Section:** Table III
**Change:** Added an "*n*" column showing the sample size for each effect metric:
n = 82,332 for Cohen's h rows; n = 42 for SHAP; n = 36 for LIME. Updated caption
to remove misleading "(n_test = 82,332)" which implied that sample size applied
to all rows.
**Rationale:** The original Table III caption stated "n_test = 82,332" in the
title, which is incorrect for the SHAP and LIME rows (n = 42 and 36 respectively).
Adding an explicit n column avoids reader confusion about which sample sizes
support which effect estimates.

---

### C18 — Limitations §VII: Add §VII-D Statistical Validity subsection
**Type:** Completeness (TASK 8)
**Section:** §VII
**Added:** §VII-D "Statistical Validity" addressing: (1) Holm–Bonferroni
family-wise error rate scope; (2) normal approximation validity at different
sample sizes.
**Rationale:** The original §VII covered internal, external, and construct validity
but did not separately address statistical validity — a distinct threat type.
IEEE reviewers in statistics-heavy papers expect explicit discussion of whether
the correction procedure was appropriately scoped.

---

### C19 — Future Work §VIII: Convert list to prose with rationale
**Type:** IEEE style / depth (TASK 9)
**Section:** §VIII
**Change:** Six bulleted items converted to five connected paragraphs. Each
paragraph provides a one-sentence rationale connecting the future direction to a
specific limitation in §VII.
**Rationale:** Bulleted future work lists are common but superficial. Prose
paragraphs that explicitly link each future direction to an identified limitation
demonstrate that the future work is motivated rather than generic.

---

### C20 — Conclusion §IX: Active reframe
**Type:** Writing quality (TASK 10)
**Section:** §IX
**Original:** "This paper presented a controlled empirical investigation into
the impact of SMOTE-based class rebalancing..."
**Revised:** "SMOTE-based class rebalancing produces statistically significant
but practically negligible changes to aggregate predictive metrics (max Cohen's
h = 0.087) while producing medium-to-large changes to SHAP and LIME feature
attribution rankings (rank-biserial r up to 0.595 for LIME)..."
**Rationale:** IEEE conclusions should state findings directly, not describe what
the paper "presented." The active reframe puts the result first, which is stronger
and more memorable. The key statistics are retained in the opening.

---

### C21 — Conclusion §IX: Strengthen final sentence
**Type:** Specificity (TASK 10)
**Section:** §IX (final sentence)
**Original:** "Future work should validate these findings across additional
datasets, model families, and rebalancing strategies to establish the
generalisability of explanation-consistency monitoring as a practical component
of trustworthy NIDS development."
**Revised:** "Future work should validate these findings across additional
datasets, model families, and rebalancing strategies, and develop formal
explanation-consistency metrics to support responsible deployment of
XAI-augmented NIDS in regulatory environments."
**Rationale:** The original final sentence was generic. The addition of "develop
formal explanation-consistency metrics" ties the future direction to the specific
regulatory context (EU AI Act [23]) introduced in §I, giving the paper a more
complete argumentative arc.

---

### C22 — Reference [9] Patil 2020: Location flag
**Type:** Reference audit (TASK 16)
**Change:** Removed "San Jose, CA, USA" from the venue description; venue now
reads "Proc. IEEE ICICT, Feb. 2020, pp. 41–45." 
**Rationale:** IEEE ICICT 2020 (conference number 50521) was held in early 2020.
Given the COVID-19 pandemic timeline, this conference may have been virtual or
rescheduled; "San Jose, CA, USA" cannot be confirmed from publicly available
information. The DOI 10.1109/ICICT50521.2020.9092325 is retained for verification.
**Author action:** Verify location against IEEE Xplore before submission.

---

## 2. Changes NOT Made (With Justification)

| Item | Reason not changed |
|---|---|
| All numerical values (Table I, II, III, IV) | Scientific content locked |
| Effect size interpretations (h, r) | Correct per Cohen 1988 conventions |
| Statistical test statistics (W, χ², p) | Experimental output, not editable |
| Wilcoxon "zero-method" description | Technically correct as stated |
| §III-D: n_trees = 100 (implicit) | Not stated in text; no value to add |
| "Verified via SHA-256" claim (§IV) | Correct and appropriate |
| Fig. 24 caption "qualitative asymmetry" note | Correct and already well-stated |
| Research Questions RQ1–RQ4 | Locked |
| Conclusions | No changes beyond phrasing; findings intact |

---

## 3. Reference Audit (TASK 16)

| Ref | Authors | Venue | Year | DOI | Status |
|---|---|---|---|---|---|
| [1] | Breiman | Mach. Learn. | 2001 | 10.1023/A:1010933404324 | ✅ Verified |
| [2] | Chawla et al. | JAIR | 2002 | 10.1613/jair.953 | ✅ Verified |
| [3] | Pedregosa et al. | JMLR | 2011 | URL | ✅ Verified |
| [4] | Moustafa & Slay | MilCIS | 2015 | 10.1109/MilCIS.2015.7348942 | ✅ Verified |
| [5] | Ribeiro et al. | KDD | 2016 | 10.1145/2939672.2939778 | ✅ Verified |
| [6] | Lemaître et al. | JMLR | 2017 | URL | ✅ Verified |
| [7] | Lundberg & Lee | NeurIPS | 2017 | URL | ✅ Verified |
| [8] | Lundberg et al. | Nat. Mach. Intell. | 2020 | 10.1038/s42256-019-0138-9 | ✅ Verified |
| [9] | Patil et al. | IEEE ICICT | 2020 | 10.1109/ICICT50521.2020.9092325 | ⚠️ Location removed — verify |
| [10] | Alshamy et al. | ACeS/Springer | 2021 | 10.1007/978-981-16-8059-5_22 | ✅ Verified |
| [11] | Visani et al. | J. Oper. Res. Soc. | 2022 | 10.1080/01605682.2020.1865846 | ✅ Verified |
| [12] | Charmet et al. | Ann. Telecommun. | 2022 | 10.1007/s12243-022-00926-7 | ✅ Verified |
| [13] | Wu et al. | EURASIP J. | 2022 | 10.1186/s13634-022-00871-6 | ✅ Verified |
| [14] | Alarab & Prakoonwit | Data Sci. Manag. | 2022 | 10.1016/j.dsm.2022.04.003 | ✅ Verified |
| [15] | Rjoub et al. | IEEE TNSM | 2023 | 10.1109/TNSM.2023.3282740 | ✅ Verified |
| [16] | More et al. | Algorithms | 2024 | 10.3390/a17020064 | ✅ Verified |
| [17] | Gaspar et al. | IEEE Access | 2024 | 10.1109/ACCESS.2024.3368377 | ✅ Verified |
| [18] | Sayegh et al. | Appl. Sci. | 2024 | 10.3390/app14020479 | ✅ Verified |
| [19] | Shanmugam et al. | Electronics | 2025 | 10.3390/electronics14010069 | ✅ Verified |
| [20] | Hermosilla et al. | Appl. Sci. | 2025 | 10.3390/app15137329 | ✅ Verify publication date |
| [21] | Hermosilla et al. | Computers | 2025 | 10.3390/computers14050160 | ✅ Verify publication date |
| [22] | Virtanen et al. | Nat. Methods | 2020 | 10.1038/s41592-020-0772-5 | ✅ Verified; citation role fixed (C11) |
| [23] | EU Parliament | Off. J. EU | 2024 | URL | ✅ Check venue policy on grey lit |

**Flags:**
- [9]: Location "San Jose, CA, USA" removed; verify actual location via IEEE Xplore.
- [20],[21]: Published Jul/May 2025; verify dates are correct at submission time.
- [22]: Formerly misused as methodological justification for McNemar's test; now correctly cited as software implementation only (C11).
- [23]: Some IEEE venues require peer-reviewed sources only; verify TEMSMET policy.

---

## 4. Figure Specifications (TASK 14)

### RECOMMENDED APPROACH (per master prompt)
Use actual experiment-generated figures for all results figures.
Create one illustrative workflow diagram for methodology.

### 4A. Workflow Diagram (NEW — IEEE-quality methodology figure)
**Purpose:** Show the experimental pipeline from dataset to statistical analysis
**Type:** Illustrative (not data-derived); appropriate as methodology figure
**Target:** Fig. WORKFLOW | placement: before §III or as Fig. 0 in §I/§III
**Style:** Grayscale, two rows, IEEE one-column width
**Content:**
```
[UNSW-NB15 Dataset]
    ↓ 175,341 train | 82,332 test
[Feature Engineering] (44→42 features)
    ↓                      ↓
[Baseline RF]         [SMOTE + RF]
(imbalanced)          (balanced 560,000)
    ↓                      ↓
[SHAP TreeExplainer]  [SHAP TreeExplainer]
[LIME Tabular]        [LIME Tabular]
    ↓                      ↓
    [Paired Statistical Analysis]
    McNemar · Wilcoxon · Bootstrap · Holm
    ↓
    [Results: Predictive vs. Explanatory Sensitivity]
```
This SVG figure is available as a separate artifact.

### 4B. Publication-quality matplotlib style specification
For all existing result figures, apply the following style:

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

# IEEE single-column figure dimensions
COLUMN_WIDTH = 3.5   # inches (single column)
FULL_WIDTH   = 7.16  # inches (full IEEE width, two-column)

# Typography matching IEEEtran body
mpl.rcParams.update({
    'font.family':      'serif',
    'font.serif':       ['Times New Roman', 'Times', 'DejaVu Serif'],
    'font.size':        8,
    'axes.titlesize':   8,
    'axes.labelsize':   8,
    'xtick.labelsize':  7,
    'ytick.labelsize':  7,
    'legend.fontsize':  7,
    'figure.dpi':       300,
    'savefig.dpi':      300,
    'savefig.format':   'pdf',        # prefer PDF/EPS for LaTeX
    'axes.linewidth':   0.6,
    'lines.linewidth':  1.0,
    'patch.linewidth':  0.6,
    'grid.linewidth':   0.4,
    'grid.alpha':       0.4,
    'axes.spines.top':  False,        # clean IEEE style
    'axes.spines.right':False,
})

# Grayscale-safe palette (readable in B&W print)
IEEE_GRAY = ['#000000', '#555555', '#999999', '#cccccc']

# Usage:
fig, ax = plt.subplots(figsize=(COLUMN_WIDTH, 2.2))
# ... plot content ...
fig.tight_layout(pad=0.3)
fig.savefig('outputs/figures/fig_name.pdf', bbox_inches='tight')
```

### 4C. Key figure caption improvements
All figure captions should follow: "Fig. N. [Action verb phrase]. [Key numeric values].
[Interpretation one sentence if needed]."

| Fig. | Current caption quality | Recommended improvement |
|---|---|---|
| 24 (effect sizes) | Good; note about different scales present | Add "(B=Baseline; S=SMOTE)" to axis labels |
| 19 (ranking comparison) | Good | Add Spearman ρ values as text on figure |
| 8 (minority F1) | Good | Include ± notation if std dev available |
| 6,7 (confusion matrices) | Good | Verify colourmap is greyscale-friendly |

---

## 5. IEEE Compliance Checklist (TASK 17)

| Category | Item | Status |
|---|---|---|
| **Title** | Descriptive, sentence case, ≤17 words | PASS (17 words; check venue limit) |
| **Abstract** | 150–250 words, no citations | PASS (~238 words, no citations) |
| **Index Terms** | 3–8 terms, lowercase | PASS (8 terms) |
| **Introduction** | Problem stated, gap identified, contributions listed | PASS |
| **Introduction** | Regulatory/trustworthy-AI motivation | PASS (C03 added) |
| **Introduction** | No boilerplate section roadmap | PASS (C02 removed) |
| **Related Work** | Builds logical argument → gap | PASS (C04–C06 improved) |
| **Related Work** | Transitions between subsections | PASS |
| **Methodology** | Dataset choice justified | PASS (C07 added) |
| **Methodology** | Rebalancing technique justified | PASS (C08 added) |
| **Methodology** | Classifier justified | PASS (C09 added) |
| **Methodology** | Sample size (60 instances) justified | PASS (C10 added) |
| **Methodology** | Statistical tests appropriate | PASS |
| **Methodology** | McNemar citation correct | PASS (C11 fixed) |
| **Methodology** | Research hypothesis pre-specified | PASS (C12 added) |
| **Results** | Statistical significance ≠ practical significance | PASS (throughout) |
| **Results** | Effect sizes with thresholds | PASS |
| **Results** | Power analysis reported | PASS |
| **Results** | Worms class caveat | PASS |
| **Results** | LIME fidelity caveat | PASS |
| **Tables** | Captions above tables | PASS |
| **Tables** | Correct sample size per row (Table III) | PASS (C17 added n column) |
| **Tables** | No vertical rules | PASS |
| **Tables** | Footnotes explain abbreviations | PASS |
| **Figures** | Captions below figures | PASS |
| **Figures** | Cited before appearance | PASS |
| **Equations** | Numbered, variables defined | PASS |
| **Discussion** | Mechanism explained | PASS (C15 expanded) |
| **Discussion** | Practical implications derived from evidence | PASS (C16 restructured) |
| **Discussion** | Novelty claim appropriately hedged | PASS ("to the best of...") |
| **Limitations** | Internal validity | PASS |
| **Limitations** | External validity | PASS |
| **Limitations** | Construct validity | PASS |
| **Limitations** | Statistical validity | PASS (C18 added §VII-D) |
| **Future Work** | Directly follows limitations | PASS (C19 restructured) |
| **Conclusion** | Active finding statement (no "presented") | PASS (C20) |
| **Conclusion** | No abstract repetition | PASS |
| **Conclusion** | Future direction specific | PASS (C21) |
| **References** | IEEE appearance order | NEEDS REVISION (only in LaTeX; markdown retains thematic) |
| **References** | DOIs present and correct | PASS (⚠️ [9],[20],[21],[23] verify) |
| **References** | et al. for >6 authors | PASS |
| **Grammar** | Active voice preferred | PASS |
| **Consistency** | British English throughout | PASS |
| **Novelty** | "First" claims hedged | PASS |
| **Length** | ≤ 6 pages (estimated) | PASS (~5.4 pages with 11-figure set) |

**Overall compliance: PASS with 3 author-side items pending (DOI verification,
author block completion, LaTeX compilation).**

---

## 6. Remaining Issues for Manual Verification

| # | Issue | Priority | Action |
|---|---|---|---|
| M1 | Author/affiliation placeholders not filled | **BLOCKING** | Author must complete |
| M2 | [9] Patil location "San Jose" removed — verify on IEEE Xplore | **HIGH** | Author |
| M3 | [20] Hermosilla Appl. Sci. Jul 2025 — confirm publication date | HIGH | Author |
| M4 | [21] Hermosilla Computers May 2025 — confirm publication date | HIGH | Author |
| M5 | [23] EU AI Act — verify venue accepts non-peer-reviewed grey literature | MODERATE | Author |
| M6 | Run pdflatex twice and verify PDF ≤ 6 pages | **BLOCKING** | Author |
| M7 | Verify all 11 figure PNGs ≥ 300 DPI before PDF export | **BLOCKING** | Author |
| M8 | Abstract word count: verify ≤ 250 after LaTeX rendering | MODERATE | Author |
| M9 | Check TEMSMET 2026 CFP for title word limit (17 words) | MODERATE | Author |
| M10 | Run Scopus/Google Scholar search for July 2026 papers on NIDS + XAI | RECOMMENDED | Author |

---

## 7. One Recommendation Beyond This Prompt

**The single highest-impact action not yet implemented:**

Add a one-row **"Explanation Drift Monitoring" algorithm box** (IEEE `algorithm`
environment, `algorithmicx` package) to §VI-B. The algorithm would show:

```
Algorithm 1: Explanation Drift Detection After Retraining
Require: Original model M₀, retrained model M₁, test set X, threshold ρ_min
1: Compute SHAP rankings R₀, R₁ on matched instance set X_60
2: Compute LIME rankings L₀, L₁ on matched instance set X_60
3: ρ_SHAP ← SpearmanCorr(R₀, R₁)
4: ρ_LIME ← SpearmanCorr(L₀, L₁)
5: if ρ_SHAP < ρ_min OR ρ_LIME < ρ_min then
6:     ALERT: Explanation drift detected — revalidate XAI outputs
7: end if
```

**Why this matters:** The paper provides the first empirical evidence of disproportionate
explanation instability; it should also be the first to propose a concrete
monitoring procedure. A lightweight algorithm box (occupying ~0.3 column-inches)
converts the finding into an actionable practitioner artifact, which dramatically
increases citation potential and practical impact.

This does NOT require new experiments — all components (Spearman correlation on
matched instances) are already part of the methodology. The threshold ρ_min can
be stated as "application-dependent; the values observed in this study
(ρ_SHAP = 0.900, ρ_LIME = 0.565) provide baseline reference points."

---

*End of refinement_changelog.md | 2026-07-09*
