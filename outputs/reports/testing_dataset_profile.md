# UNSW-NB15 Testing Dataset Profile

**Generated:** 2026-06-30T04:11:37.163502+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## 1. Basic Dataset Information

| Property | Value |
|---|---|
| Dataset Name | testing |
| File Path | C:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026\data\raw\UNSW_NB15_testing-set.csv |
| File Size (bytes) | 15,380,800 |
| Rows | 82,332 |
| Columns | 45 |
| Memory Usage (bytes) | 44,378,735 |
| Encoding | utf-8 |

---

## 2. Schema Analysis

| Column | Dtype | Missing | Missing % | Unique |
|---|---|---|---|---|
| id | int64 | 0 | 0.0% | 82332 |
| dur | float64 | 0 | 0.0% | 39888 |
| proto | object | 0 | 0.0% | 131 |
| service | object | 0 | 0.0% | 13 |
| state | object | 0 | 0.0% | 7 |
| spkts | int64 | 0 | 0.0% | 420 |
| dpkts | int64 | 0 | 0.0% | 436 |
| sbytes | int64 | 0 | 0.0% | 4489 |
| dbytes | int64 | 0 | 0.0% | 4034 |
| rate | float64 | 0 | 0.0% | 40616 |
| sttl | int64 | 0 | 0.0% | 11 |
| dttl | int64 | 0 | 0.0% | 8 |
| sload | float64 | 0 | 0.0% | 42873 |
| dload | float64 | 0 | 0.0% | 40614 |
| sloss | int64 | 0 | 0.0% | 253 |
| dloss | int64 | 0 | 0.0% | 311 |
| sinpkt | float64 | 0 | 0.0% | 39970 |
| dinpkt | float64 | 0 | 0.0% | 37617 |
| sjit | float64 | 0 | 0.0% | 39944 |
| djit | float64 | 0 | 0.0% | 38381 |
| swin | int64 | 0 | 0.0% | 11 |
| stcpb | int64 | 0 | 0.0% | 39219 |
| dtcpb | int64 | 0 | 0.0% | 39108 |
| dwin | int64 | 0 | 0.0% | 14 |
| tcprtt | float64 | 0 | 0.0% | 26130 |
| synack | float64 | 0 | 0.0% | 24934 |
| ackdat | float64 | 0 | 0.0% | 24020 |
| smean | int64 | 0 | 0.0% | 1282 |
| dmean | int64 | 0 | 0.0% | 1222 |
| trans_depth | int64 | 0 | 0.0% | 8 |
| response_body_len | int64 | 0 | 0.0% | 1190 |
| ct_srv_src | int64 | 0 | 0.0% | 57 |
| ct_state_ttl | int64 | 0 | 0.0% | 7 |
| ct_dst_ltm | int64 | 0 | 0.0% | 50 |
| ct_src_dport_ltm | int64 | 0 | 0.0% | 50 |
| ct_dst_sport_ltm | int64 | 0 | 0.0% | 33 |
| ct_dst_src_ltm | int64 | 0 | 0.0% | 57 |
| is_ftp_login | int64 | 0 | 0.0% | 3 |
| ct_ftp_cmd | int64 | 0 | 0.0% | 3 |
| ct_flw_http_mthd | int64 | 0 | 0.0% | 8 |
| ct_src_ltm | int64 | 0 | 0.0% | 50 |
| ct_srv_dst | int64 | 0 | 0.0% | 57 |
| is_sm_ips_ports | int64 | 0 | 0.0% | 2 |
| attack_cat | object | 0 | 0.0% | 10 |
| label | int64 | 0 | 0.0% | 2 |

---

## 3. Target Variable Analysis

**Target column:** `attack_cat`  
**Number of classes:** 10

| Class | Count | % of Total |
|---|---|---|
| Normal | 37,000 | 44.94% |
| Generic | 18,871 | 22.9206% |
| Exploits | 11,132 | 13.5209% |
| Fuzzers | 6,062 | 7.3629% |
| DoS | 4,089 | 4.9665% |
| Reconnaissance | 3,496 | 4.2462% |
| Analysis | 677 | 0.8223% |
| Backdoor | 583 | 0.7081% |
| Shellcode | 378 | 0.4591% |
| Worms | 44 | 0.0534% |

---

## 4. Feature Categorization

| Category | Count | Columns |
|---|---|---|
| Numerical | 39 | id, dur, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, sloss, dloss, sinpkt, dinpkt, sjit, djit, swin, stcpb, dtcpb, dwin, tcprtt, synack, ackdat, smean, dmean, trans_depth, response_body_len, ct_srv_src, ct_state_ttl, ct_dst_ltm, ct_src_dport_ltm, ct_dst_sport_ltm, ct_dst_src_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, ct_src_ltm, ct_srv_dst |
| Integer | 28 | id, spkts, dpkts, sbytes, dbytes, sttl, dttl, sloss, dloss, swin, stcpb, dtcpb, dwin, smean, dmean, trans_depth, response_body_len, ct_srv_src, ct_state_ttl, ct_dst_ltm, ct_src_dport_ltm, ct_dst_sport_ltm, ct_dst_src_ltm, is_ftp_login, ct_ftp_cmd, ct_flw_http_mthd, ct_src_ltm, ct_srv_dst |
| Floating-point | 11 | dur, rate, sload, dload, sinpkt, dinpkt, sjit, djit, tcprtt, synack, ackdat |
| Categorical | 4 | proto, service, state, attack_cat |
| Boolean | 2 | is_sm_ips_ports, label |

---

## 5. Missing Data Analysis

**Total missing values:** 0

*No missing values detected in any column.*

---

## 6. Duplicate Analysis

| Property | Value |
|---|---|
| Total Rows | 82,332 |
| Duplicate Rows | 0 |
| Duplicate % | 0.0% |

---

## 7. Constant & Near-Constant Features

### Constant Columns

*None detected.*

### Near-Constant Columns

| Column | Dominant Value | % |
|---|---|---|
| is_ftp_login | 0 | 99.1765% |
| ct_ftp_cmd | 0 | 99.1741% |

---

## 8. Basic Numeric Summary

| Column | Mean | Median | Std | Min | Q25 | Q50 | Q75 | Max |
|---|---|---|---|---|---|---|---|---|
| id | 41166.5 | 41166.5 | 23767.345519 | 1.0 | 20583.75 | 41166.5 | 61749.25 | 82332.0 |
| dur | 1.006756 | 0.014138 | 4.710444 | 0.0 | 8e-06 | 0.014138 | 0.71936 | 59.999989 |
| spkts | 18.666472 | 6.0 | 133.916353 | 1.0 | 2.0 | 6.0 | 12.0 | 10646.0 |
| dpkts | 17.545936 | 2.0 | 115.574086 | 0.0 | 0.0 | 2.0 | 10.0 | 11018.0 |
| sbytes | 7993.908165 | 534.0 | 171642.26188 | 24.0 | 114.0 | 534.0 | 1280.0 | 14355774.0 |
| dbytes | 13233.785563 | 178.0 | 151471.456091 | 0.0 | 0.0 | 178.0 | 956.0 | 14657531.0 |
| rate | 82410.886739 | 2650.176667 | 148620.367041 | 0.0 | 28.606114 | 2650.176667 | 111111.1072 | 1000000.003 |
| sttl | 180.967667 | 254.0 | 101.513358 | 0.0 | 62.0 | 254.0 | 254.0 | 255.0 |
| dttl | 95.713003 | 29.0 | 116.667722 | 0.0 | 0.0 | 29.0 | 252.0 | 253.0 |
| sload | 64549016.914059 | 577003.21875 | 179861832.630003 | 0.0 | 11202.466797 | 577003.21875 | 65142856.0 | 5268000256.0 |
| dload | 630546.959 | 2112.951416 | 2393000.555646 | 0.0 | 0.0 | 2112.951416 | 15858.082275 | 20821108.0 |
| sloss | 4.753692 | 1.0 | 64.64962 | 0.0 | 0.0 | 1.0 | 3.0 | 5319.0 |
| dloss | 6.308556 | 0.0 | 55.708021 | 0.0 | 0.0 | 0.0 | 2.0 | 5507.0 |
| sinpkt | 755.394301 | 0.557929 | 6182.615732 | 0.0 | 0.008 | 0.557929 | 63.409444 | 60009.992 |
| dinpkt | 121.701284 | 0.01 | 1292.378499 | 0.0 | 0.0 | 0.01 | 63.136369 | 57739.24 |
| sjit | 6363.0751 | 17.623918 | 56724.016689 | 0.0 | 0.0 | 17.623918 | 3219.332412 | 1483830.917 |
| djit | 535.18043 | 0.0 | 3635.305383 | 0.0 | 0.0 | 0.0 | 128.459914 | 463199.2401 |
| swin | 133.45908 | 255.0 | 127.357 | 0.0 | 0.0 | 255.0 | 255.0 | 255.0 |
| stcpb | 1084641551.115289 | 27888855.0 | 1390859761.610447 | 0.0 | 0.0 | 27888855.0 | 2171309606.5 | 4294949667.0 |
| dtcpb | 1073464670.880387 | 28569748.5 | 1381996192.032797 | 0.0 | 0.0 | 28569748.5 | 2144205173.0 | 4294880717.0 |
| dwin | 128.28662 | 255.0 | 127.49137 | 0.0 | 0.0 | 255.0 | 255.0 | 255.0 |
| tcprtt | 0.055925 | 0.000551 | 0.116022 | 0.0 | 0.0 | 0.000551 | 0.105541 | 3.821465 |
| synack | 0.029256 | 0.000441 | 0.070854 | 0.0 | 0.0 | 0.000441 | 0.052596 | 3.226788 |
| ackdat | 0.026669 | 8e-05 | 0.055094 | 0.0 | 0.0 | 8e-05 | 0.048816 | 2.928778 |
| smean | 139.528604 | 65.0 | 208.472063 | 24.0 | 57.0 | 65.0 | 100.0 | 1504.0 |
| dmean | 116.275069 | 44.0 | 244.600271 | 0.0 | 0.0 | 44.0 | 87.0 | 1500.0 |
| trans_depth | 0.094277 | 0.0 | 0.542922 | 0.0 | 0.0 | 0.0 | 0.0 | 131.0 |
| response_body_len | 1595.371885 | 0.0 | 38066.972292 | 0.0 | 0.0 | 0.0 | 0.0 | 5242880.0 |
| ct_srv_src | 9.546604 | 5.0 | 11.090289 | 1.0 | 2.0 | 5.0 | 11.0 | 63.0 |
| ct_state_ttl | 1.369273 | 1.0 | 1.067188 | 0.0 | 1.0 | 1.0 | 2.0 | 6.0 |
| ct_dst_ltm | 5.744923 | 2.0 | 8.418112 | 1.0 | 1.0 | 2.0 | 6.0 | 59.0 |
| ct_src_dport_ltm | 4.928898 | 1.0 | 8.389545 | 1.0 | 1.0 | 1.0 | 4.0 | 59.0 |
| ct_dst_sport_ltm | 3.663011 | 1.0 | 5.915386 | 1.0 | 1.0 | 1.0 | 3.0 | 38.0 |
| ct_dst_src_ltm | 7.45636 | 3.0 | 11.415191 | 1.0 | 1.0 | 3.0 | 6.0 | 63.0 |
| is_ftp_login | 0.008284 | 0.0 | 0.091171 | 0.0 | 0.0 | 0.0 | 0.0 | 2.0 |
| ct_ftp_cmd | 0.008381 | 0.0 | 0.092485 | 0.0 | 0.0 | 0.0 | 0.0 | 2.0 |
| ct_flw_http_mthd | 0.129743 | 0.0 | 0.638683 | 0.0 | 0.0 | 0.0 | 0.0 | 16.0 |
| ct_src_ltm | 6.46836 | 3.0 | 8.543927 | 1.0 | 1.0 | 3.0 | 7.0 | 60.0 |
| ct_srv_dst | 9.164262 | 5.0 | 11.121413 | 1.0 | 2.0 | 5.0 | 11.0 | 62.0 |

---
*End of Dataset Profile Report*
