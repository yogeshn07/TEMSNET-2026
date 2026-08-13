# UNSW-NB15 Feature Selection & Leakage Elimination Report

**Generated:** 2026-06-30T05:51:58.529345+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## Target Leakage Analysis

### `id`

id is unique for 175341/175341 rows (ratio=1.0) and correlates with binary label at r=0.7272, indicating rows were likely captured in blocks ordered by traffic/attack type — row position alone carries target signal.

### `label`

verify_label_consistency() confirms every 'attack_cat' class maps to exactly one 'label' value in both splits, with 0 exceptions (Normal->0, every attack class->1) — label is a deterministic duplicate of the target.

**Other low-cardinality features checked for deterministic target mapping:** 0 found (beyond the `label` case already documented above).

---

## Feature Audit

| Column | Classification | Reason |
|---|---|---|
| id | mandatory_removal | id is unique for 175341/175341 rows (ratio=1.0) and correlates with binary label at r=0.7272, indicating rows were likely captured in blocks ordered by traffic/attack type — row position alone carries target signal. |
| dur | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| proto | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| service | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| state | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| spkts | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| dpkts | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| sbytes | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| dbytes | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| rate | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| sttl | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| dttl | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| sload | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| dload | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| sloss | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| dloss | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| sinpkt | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| dinpkt | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| sjit | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| djit | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| swin | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| stcpb | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| dtcpb | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| dwin | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| tcprtt | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| synack | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ackdat | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| smean | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| dmean | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| trans_depth | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| response_body_len | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| ct_srv_src | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_state_ttl | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| ct_dst_ltm | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_src_dport_ltm | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_dst_sport_ltm | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_dst_src_ltm | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| is_ftp_login | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_ftp_cmd | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_flw_http_mthd | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| ct_src_ltm | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| ct_srv_dst | candidate | Involved in a highly correlated feature pair (|r| > 0.8, Task B.3). Retained — not removed solely for correlation, since Random Forest tolerates multicollinearity and removal without an empirical accuracy/explanation-quality comparison would be premature at this descriptive stage. Flagged for reconsideration once real modelling experiments exist. |
| is_sm_ips_ports | final_baseline | No leakage evidence found; not involved in a highly correlated pair. |
| label | mandatory_removal | verify_label_consistency() confirms every 'attack_cat' class maps to exactly one 'label' value in both splits, with 0 exceptions (Normal->0, every attack class->1) — label is a deterministic duplicate of the target. |

---

## Correlation Review (reusing Task B.3 findings)

21 feature(s) are involved in at least one highly correlated pair (|r| > 0.8) and are classified as **Candidate** — retained, not removed. Random Forest (the locked research model) tolerates multicollinearity without the instability linear models exhibit, and removing features by correlation alone, without an empirical comparison of model accuracy or explanation quality, would be a premature decision at this descriptive stage.

---

## Final Schema

| Split | Path | Rows | Columns |
|---|---|---|---|
| Training | `C:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026\data\processed\training_selected.parquet` | 175,341 | 43 |
| Testing | `C:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026\data\processed\testing_selected.parquet` | 82,332 | 43 |

**Output format:** parquet

---

## Feature Selection Summary (Methodology Section)

*(Suitable for inclusion in the Methodology section)*

Of 44 original features, 2 were removed for confirmed target leakage (`id, label`) and 42 were retained (21 flagged as correlated candidates, 21 as final baseline features). `id` was removed because it is unique for every row (uniqueness ratio = 1.0) and correlates with the binary label at r = 0.727173, indicating row order itself carries target information. `label` was removed because it is a deterministic duplicate of the multi-class target (Normal->0, every attack->1, 0 exceptions in either split). The resulting baseline datasets (175,341 training rows, 82,332 testing rows, 43 columns each) were saved to `data/processed/` for all downstream modelling experiments.

---
*End of Feature Selection Report*
