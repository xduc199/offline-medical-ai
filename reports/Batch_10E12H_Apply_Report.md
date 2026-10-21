# Batch 10E-12H ? Apply report

- Baseline SHA-256 `e8eccc7d20d68bbce8b7e505d97cbe60d3bf17377b3a3770ff7974c20acf7d77`; 465280 bytes; 14723 splitlines; U+FFFD 0; LF 14722.
- Backup `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12H_26_verified_joins.txt` SHA-256 `e8eccc7d20d68bbce8b7e505d97cbe60d3bf17377b3a3770ff7974c20acf7d77`.
- After SHA-256 `795161de8ff9fc0653acdc614250f30e7309b35c5931fa8f35813114763de10b`; 465254 bytes; 14697 splitlines; U+FFFD 0; LF 14696.
- PDF SHA-256 `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e` unchanged.

## Visually verified LF joins

| ID | Baseline line | Join | Physical PDF page |
|---|---:|---|---:|
| E12H-01 | 4146?4147 | `A` + LF + `ny` ? `Any` | 73 |
| E12H-02 | 4151?4152 | `Br` + LF + `eathing` ? `Breathing` | 73 |
| E12H-03 | 4154?4155 | `C` + LF + `irculation` ? `Circulation` | 73 |
| E12H-04 | 4159?4160 | `Exposur` + LF + `e` ? `Exposure` | 73 |
| E12H-05 | 4164?4165 | `P` + LF + `lacental` ? `Placental` | 73 |
| E12H-06 | 4166?4167 | `S` + LF + `eizures` ? `Seizures` | 73 |
| E12H-07 | 4170?4171 | `I` + LF + `f` ? `If` | 73 |
| E12H-08 | 4173?4174 | `I` + LF + `f` ? `If` | 73 |
| E12H-09 | 4217?4218 | `W` + LF + `hen` ? `When` | 75 |
| E12H-10 | 4224?4225 | `I` + LF + `f` ? `If` | 75 |
| E12H-11 | 4239?4240 | `evidenc` + LF + `e` ? `evidence` | 76 |
| E12H-12 | 4249?4250 | `sev` + LF + `ere` ? `severe` | 76 |
| E12H-13 | 4253?4254 | `sig` + LF + `nificant` ? `significant` | 76 |
| E12H-14 | 4263?4264 | `f` + LF + `or` ? `for` | 76 |
| E12H-15 | 4265?4266 | `f` + LF + `or` ? `for` | 76 |
| E12H-16 | 4268?4269 | `entir` + LF + `e` ? `entire` | 76 |
| E12H-17 | 4270?4271 | `Pr` + LF + `otect` ? `Protect` | 76 |
| E12H-18 | 4272?4273 | `log-r` + LF + `oll` ? `log-roll` | 76 |
| E12H-19 | 4337?4338 | `A` + LF + `irway` ? `Airway` | 78 |
| E12H-20 | 4339?4340 | `Sig` + LF + `ns` ? `Signs` | 78 |
| E12H-21 | 4341?4342 | `T` + LF + `ension` ? `Tension` | 78 |
| E12H-22 | 4344?4345 | `P` + LF + `ericardial` ? `Pericardial` | 78 |
| E12H-23 | 4346?4347 | `A` + LF + `ltered` ? `Altered` | 78 |
| E12H-24 | 4348?4349 | `T` + LF + `rauma` ? `Trauma` | 78 |
| E12H-25 | 4350?4351 | `pr` + LF + `oblem` ? `problem` | 78 |
| E12H-26 | 4352?4353 | `A` + LF + `ny` ? `Any` | 78 |

## Verification

- Exact fragment preflight: 26/26 PASS.
- Physical PDF pages 73?78 rendered and visually inspected. Each changed fragment is visibly one complete word in the corresponding page content.
- Diff against backup: exactly 26 LF bytes removed, no other bytes changed.
- Byte-for-byte reconstruction: PASS.
- Integrity deltas: ?26 bytes, ?26 splitlines, ?26 LF; U+FFFD remains zero.
- Selected regression checks PASS.

**Result: PASS ? 26 visually confirmed split words repaired.**
