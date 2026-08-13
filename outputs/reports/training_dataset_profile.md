# UNSW-NB15 Training Dataset Profile

**Generated:** 2026-06-30T04:11:35.014194+00:00  
**Project:** IEEE TEMSMET 2026 | XAI-NIDS Imbalance Study  
**Project Version:** 0.1.0

---

## 1. Basic Dataset Information

| Property | Value |
|---|---|
| Dataset Name | training |
| File Path | C:\Users\YOGESH N\OneDrive\Desktop\TEMSNET-2026\data\raw\UNSW_NB15_training-set.csv |
| File Size (bytes) | 32,293,018 |
| Rows | 175,341 |
| Columns | 45 |
| Memory Usage (bytes) | 94,587,255 |
| Encoding | utf-8 |

---

## 2. Schema Analysis

| Column | Dtype | Missing | Missing % | Unique |
|---|---|---|---|---|
| id | int64 | 0 | 0.0% | 175341 |
| dur | float64 | 0 | 0.0% | 74039 |
| proto | object | 0 | 0.0% | 133 |
| service | object | 0 | 0.0% | 13 |
| state | object | 0 | 0.0% | 9 |
| spkts | int64 | 0 | 0.0% | 480 |
| dpkts | int64 | 0 | 0.0% | 443 |
| sbytes | int64 | 0 | 0.0% | 7214 |
| dbytes | int64 | 0 | 0.0% | 6660 |
| rate | float64 | 0 | 0.0% | 76991 |
| sttl | int64 | 0 | 0.0% | 11 |
| dttl | int64 | 0 | 0.0% | 6 |
| sload | float64 | 0 | 0.0% | 80885 |
| dload | float64 | 0 | 0.0% | 77474 |
| sloss | int64 | 0 | 0.0% | 409 |
| dloss | int64 | 0 | 0.0% | 370 |
| sinpkt | float64 | 0 | 0.0% | 76161 |
| dinpkt | float64 | 0 | 0.0% | 74245 |
| sjit | float64 | 0 | 0.0% | 77532 |
| djit | float64 | 0 | 0.0% | 76831 |
| swin | int64 | 0 | 0.0% | 13 |
| stcpb | int64 | 0 | 0.0% | 75265 |
| dtcpb | int64 | 0 | 0.0% | 75089 |
| dwin | int64 | 0 | 0.0% | 7 |
| tcprtt | float64 | 0 | 0.0% | 43319 |
| synack | float64 | 0 | 0.0% | 40142 |
| ackdat | float64 | 0 | 0.0% | 37708 |
| smean | int64 | 0 | 0.0% | 1357 |
| dmean | int64 | 0 | 0.0% | 1328 |
| trans_depth | int64 | 0 | 0.0% | 11 |
| response_body_len | int64 | 0 | 0.0% | 2386 |
| ct_srv_src | int64 | 0 | 0.0% | 52 |
| ct_state_ttl | int64 | 0 | 0.0% | 5 |
| ct_dst_ltm | int64 | 0 | 0.0% | 50 |
| ct_src_dport_ltm | int64 | 0 | 0.0% | 47 |
| ct_dst_sport_ltm | int64 | 0 | 0.0% | 32 |
| ct_dst_src_ltm | int64 | 0 | 0.0% | 54 |
| is_ftp_login | int64 | 0 | 0.0% | 4 |
| ct_ftp_cmd | int64 | 0 | 0.0% | 4 |
| ct_flw_http_mthd | int64 | 0 | 0.0% | 11 |
| ct_src_ltm | int64 | 0 | 0.0% | 50 |
| ct_srv_dst | int64 | 0 | 0.0% | 52 |
| is_sm_ips_ports | int64 | 0 | 0.0% | 2 |
| attack_cat | object | 0 | 0.0% | 10 |
| label | int64 | 0 | 0.0% | 2 |

---

## 3. Target Variable Analysis

**Target column:** `attack_cat`  
**Number of classes:** 10

| Class | Count | % of Total |
|---|---|---|
| Normal | 56,000 | 31.9378% |
| Generic | 40,000 | 22.8127% |
| Exploits | 33,393 | 19.0446% |
| Fuzzers | 18,184 | 10.3706% |
| DoS | 12,264 | 6.9944% |
| Reconnaissance | 10,491 | 5.9832% |
| Analysis | 2,000 | 1.1406% |
| Backdoor | 1,746 | 0.9958% |
| Shellcode | 1,133 | 0.6462% |
| Worms | 130 | 0.0741% |

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
| Total Rows | 175,341 |
| Duplicate Rows | 0 |
| Duplicate % | 0.0% |

---

## 7. Constant & Near-Constant Features

### Constant Columns

*None detected.*

### Near-Constant Columns

*None detected.*

---

## 8. Basic Numeric Summary

| Column | Mean | Median | Std | Min | Q25 | Q50 | Q75 | Max |
|---|---|---|---|---|---|---|---|---|
| id | 87671.0 | 87671.0 | 50616.731112 | 1.0 | 43836.0 | 87671.0 | 131506.0 | 175341.0 |
| dur | 1.359389 | 0.001582 | 6.480249 | 0.0 | 8e-06 | 0.001582 | 0.668069 | 59.999989 |
| spkts | 20.298664 | 2.0 | 136.887597 | 1.0 | 2.0 | 2.0 | 12.0 | 9616.0 |
| dpkts | 18.969591 | 2.0 | 110.258271 | 0.0 | 0.0 | 2.0 | 10.0 | 10974.0 |
| sbytes | 8844.843836 | 430.0 | 174765.644309 | 28.0 | 114.0 | 430.0 | 1418.0 | 12965233.0 |
| dbytes | 14928.918564 | 164.0 | 143654.217718 | 0.0 | 0.0 | 164.0 | 1102.0 | 14655550.0 |
| rate | 95406.187105 | 3225.80652 | 165400.978457 | 0.0 | 32.78614 | 3225.80652 | 125000.0003 | 1000000.003 |
| sttl | 179.546997 | 254.0 | 102.940011 | 0.0 | 62.0 | 254.0 | 254.0 | 255.0 |
| dttl | 79.609567 | 29.0 | 110.506863 | 0.0 | 0.0 | 29.0 | 252.0 | 254.0 |
| sload | 73454033.194063 | 879674.75 | 188357447.000203 | 0.0 | 13053.33887 | 879674.75 | 88888888.0 | 5988000256.0 |
| dload | 671205.574188 | 1447.022705 | 2421312.388757 | 0.0 | 0.0 | 1447.022705 | 27844.87109 | 22422730.0 |
| sloss | 4.953 | 0.0 | 66.005059 | 0.0 | 0.0 | 0.0 | 3.0 | 4803.0 |
| dloss | 6.94801 | 0.0 | 52.732999 | 0.0 | 0.0 | 0.0 | 2.0 | 5484.0 |
| sinpkt | 985.976864 | 0.279733 | 7242.245841 | 0.0 | 0.008 | 0.279733 | 55.156896 | 84371.496 |
| dinpkt | 88.216296 | 0.006 | 987.093195 | 0.0 | 0.0 | 0.006 | 51.053 | 56716.824 |
| sjit | 4976.254226 | 0.0 | 44965.846519 | 0.0 | 0.0 | 0.0 | 2513.295019 | 1460480.016 |
| djit | 604.353826 | 0.0 | 4061.043281 | 0.0 | 0.0 | 0.0 | 114.990625 | 289388.2697 |
| swin | 116.257339 | 0.0 | 127.001024 | 0.0 | 0.0 | 0.0 | 255.0 | 255.0 |
| stcpb | 969250421.910511 | 0.0 | 1355264249.263036 | 0.0 | 0.0 | 0.0 | 1916651334.0 | 4294958913.0 |
| dtcpb | 968877027.071153 | 0.0 | 1353999546.225652 | 0.0 | 0.0 | 0.0 | 1913674673.0 | 4294881924.0 |
| dwin | 115.013625 | 0.0 | 126.88653 | 0.0 | 0.0 | 0.0 | 255.0 | 255.0 |
| tcprtt | 0.041396 | 0.0 | 0.079354 | 0.0 | 0.0 | 0.0 | 0.065481 | 2.518893 |
| synack | 0.02102 | 0.0 | 0.0434 | 0.0 | 0.0 | 0.0 | 0.023268 | 2.100352 |
| ackdat | 0.020375 | 0.0 | 0.040506 | 0.0 | 0.0 | 0.0 | 0.038906 | 1.520884 |
| smean | 136.751769 | 73.0 | 204.67736 | 28.0 | 57.0 | 73.0 | 100.0 | 1504.0 |
| dmean | 124.173382 | 44.0 | 258.317056 | 0.0 | 0.0 | 44.0 | 89.0 | 1458.0 |
| trans_depth | 0.105982 | 0.0 | 0.776911 | 0.0 | 0.0 | 0.0 | 0.0 | 172.0 |
| response_body_len | 2144.291655 | 0.0 | 54207.967294 | 0.0 | 0.0 | 0.0 | 0.0 | 6558056.0 |
| ct_srv_src | 9.306437 | 5.0 | 10.704331 | 1.0 | 2.0 | 5.0 | 12.0 | 63.0 |
| ct_state_ttl | 1.304179 | 1.0 | 0.954406 | 0.0 | 1.0 | 1.0 | 2.0 | 6.0 |
| ct_dst_ltm | 6.193936 | 2.0 | 8.052476 | 1.0 | 1.0 | 2.0 | 7.0 | 51.0 |
| ct_src_dport_ltm | 5.383538 | 1.0 | 8.047104 | 1.0 | 1.0 | 1.0 | 5.0 | 51.0 |
| ct_dst_sport_ltm | 4.206255 | 1.0 | 5.783585 | 1.0 | 1.0 | 1.0 | 3.0 | 46.0 |
| ct_dst_src_ltm | 8.729881 | 3.0 | 10.956186 | 1.0 | 1.0 | 3.0 | 12.0 | 65.0 |
| is_ftp_login | 0.014948 | 0.0 | 0.126048 | 0.0 | 0.0 | 0.0 | 0.0 | 4.0 |
| ct_ftp_cmd | 0.014948 | 0.0 | 0.126048 | 0.0 | 0.0 | 0.0 | 0.0 | 4.0 |
| ct_flw_http_mthd | 0.133066 | 0.0 | 0.701208 | 0.0 | 0.0 | 0.0 | 0.0 | 30.0 |
| ct_src_ltm | 6.955789 | 3.0 | 8.321493 | 1.0 | 2.0 | 3.0 | 9.0 | 60.0 |
| ct_srv_dst | 9.100758 | 4.0 | 10.756952 | 1.0 | 2.0 | 4.0 | 12.0 | 62.0 |

---
*End of Dataset Profile Report*
