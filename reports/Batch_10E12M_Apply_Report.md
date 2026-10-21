# Batch 10E12M ? Apply Report

Status: **PASS**. Applied 19 visually verified word joins on physical PDF pages 96, 98 and 99. Physical page 97 was also inspected; table row wraps there separate whole words and were retained.

## Integrity

| Measure | Before | Backup | After |
|---|---:|---:|---:|
| SHA-256 | `58d6ca55c60707c133988687a7c9e76f43213a4c03958e7df5cac8d39c02d44d` | `58d6ca55c60707c133988687a7c9e76f43213a4c03958e7df5cac8d39c02d44d` | `c5f1de0c678efbf9653aabbd203aaa60967aa39427efe3b251c84245484f0942` |
| Bytes | 465123 | 465123 | 465104 |
| `splitlines()` | 14566 | 14566 | 14547 |
| U+FFFD | 0 | 0 | 0 |

Backup: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12M_18_verified_joins.txt`. PDF SHA-256 (read only): `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e`.

## Exact changes

| ID | Physical PDF page | Pre-edit cleaned lines | Fragments | Joined word | Result |
|---|---:|---:|---|---|---|
| E12M-01 | 96 | 5121?5122 | `S` + LF + `weet` | `Sweet` | PASS |
| E12M-02 | 96 | 5124?5125 | `H` + LF + `igh` | `High` | PASS |
| E12M-03 | 96 | 5127?5128 | `D` + LF + `ehydrated` | `Dehydrated` | PASS |
| E12M-04 | 96 | 5138?5139 | `r` + LF + `ash` | `rash` | PASS |
| E12M-05 | 96 | 5146?5147 | `e` + LF + `xposure` | `exposure` | PASS |
| E12M-06 | 96 | 5156?5157 | `hear` + LF + `t` | `heart` | PASS |
| E12M-07 | 98 | 5262?5263 | `I` + LF + `ncreased` | `Increased` | PASS |
| E12M-08 | 98 | 5266?5267 | `C` + LF + `yanosis` | `Cyanosis` | PASS |
| E12M-09 | 98 | 5269?5270 | `A` + LF + `ltered` | `Altered` | PASS |
| E12M-10 | 98 | 5272?5273 | `P` + LF + `oor` | `Poor` | PASS |
| E12M-11 | 98 | 5275?5276 | `V` + LF + `omiting` | `Vomiting` | PASS |
| E12M-12 | 98 | 5278?5279 | `S` + LF + `eizures` | `Seizures` | PASS |
| E12M-13 | 98 | 5281?5282 | `L` + LF + `ow` | `Low` | PASS |
| E12M-14 | 98 | 5285?5286 | `W` + LF + `heezing` | `Wheezing` | PASS |
| E12M-15 | 98 | 5289?5290 | `S` + LF + `tridor` | `Stridor` | PASS |
| E12M-16 | 98 | 5295?5296 | `R` + LF + `apid` | `Rapid` | PASS |
| E12M-17 | 99 | 5334?5335 | `I` + LF + `f` | `If` | PASS |
| E12M-18 | 99 | 5339?5340 | `F` + LF + `ollowing` | `Following` | PASS |
| E12M-19 | 99 | 5344?5345 | `M` + LF + `ake` | `Make` | PASS |

## Verification

- 19/19 adjacent contexts validated from the backup.
- Byte diff: exactly 19 LF bytes removed; no other byte changes.
- Reconstructed from backup with exactly these 19 joins: byte-for-byte match **PASS**.
- `splitlines()` reduced by 19; U+FFFD remains 0.
- Prior page 93?96 fixes were spot-checked and remain intact.
- PDF and extracted source files were not modified.
