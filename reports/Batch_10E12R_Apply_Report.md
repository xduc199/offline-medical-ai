# Batch 10E12R ? Apply Report

Status: **PASS**. Applied 37 PDF-confirmed joins on physical pages 121, 124, 125, 127 and 129. The flowchart on physical page 116 and ordinary word-boundary wraps were preserved.

## Integrity

| Measure | Before | Backup | After |
|---|---:|---:|---:|
| SHA-256 | `945a8c93cafb8ac5f77e3cca96827efb3be65ea43be9691c64eb57a606a9c5fb` | `945a8c93cafb8ac5f77e3cca96827efb3be65ea43be9691c64eb57a606a9c5fb` | `0ff109610397caa21d5f7ddea849dad0722c7f82748666ea10b4ae3a79f1b6e9` |
| Bytes | 464949 | 464949 | 464912 |
| `splitlines()` | 14392 | 14392 | 14355 |
| U+FFFD | 0 | 0 | 0 |

Backup: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12R_37_verified_joins.txt`, hash matches baseline. PDF SHA-256 (read only): `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e`.

## Exact changes

| ID | Physical PDF page | Pre-edit lines | Fragments | Joined word | Status |
|---|---:|---:|---|---|---|
| E12R-01 | 121 | 6407?6408 | `P` + LF + `atients` | `Patients` | PASS |
| E12R-02 | 121 | 6410?6411 | `P` + LF + `atients` | `Patients` | PASS |
| E12R-03 | 124 | 6482?6483 | `S` + LF + `tart` | `Start` | PASS |
| E12R-04 | 124 | 6484?6485 | `C` + LF + `ontinue` | `Continue` | PASS |
| E12R-05 | 124 | 6487?6488 | `P` + LF + `lace` | `Place` | PASS |
| E12R-06 | 124 | 6489?6490 | `R` + LF + `apidly` | `Rapidly` | PASS |
| E12R-07 | 124 | 6497?6498 | `I` + LF + `ntraosseous` | `Intraosseous` | PASS |
| E12R-08 | 124 | 6500?6501 | `Sur` + LF + `gery` | `Surgery` | PASS |
| E12R-09 | 124 | 6502?6503 | `A` + LF + `drenaline` | `Adrenaline` | PASS |
| E12R-10 | 124 | 6507?6508 | `P` + LF + `neumonia` | `Pneumonia` | PASS |
| E12R-11 | 124 | 6509?6510 | `injur` + LF + `y` | `injury` | PASS |
| E12R-12 | 124 | 6512?6513 | `D` + LF + `ehydration` | `Dehydration` | PASS |
| E12R-13 | 124 | 6514?6515 | `H` + LF + `ypoglycaemia` | `Hypoglycaemia` | PASS |
| E12R-14 | 124 | 6521?6522 | `S` + LF + `tomach` | `Stomach` | PASS |
| E12R-15 | 124 | 6523?6524 | `A` + LF + `bdominal` | `Abdominal` | PASS |
| E12R-16 | 124 | 6526?6527 | `D` + LF + `ehydration` | `Dehydration` | PASS |
| E12R-17 | 124 | 6528?6529 | `S` + LF + `evere` | `Severe` | PASS |
| E12R-18 | 125 | 6543?6544 | `dec` + LF + `ompression` | `decompression` | PASS |
| E12R-19 | 125 | 6546?6547 | `tr` + LF + `ansfusion` | `transfusion` | PASS |
| E12R-20 | 125 | 6548?6549 | `S` + LF + `tart` | `Start` | PASS |
| E12R-21 | 127 | 6586?6587 | `r` + LF + `ecognize` | `recognize` | PASS |
| E12R-22 | 127 | 6589?6590 | `r` + LF + `ecognize` | `recognize` | PASS |
| E12R-23 | 127 | 6592?6593 | `high-r` + LF + `isk` | `high-risk` | PASS |
| E12R-24 | 127 | 6598?6599 | `A` + LF + `VPU` | `AVPU` | PASS |
| E12R-25 | 127 | 6600?6601 | `R` + LF + `ecovery` | `Recovery` | PASS |
| E12R-26 | 127 | 6602?6603 | `O` + LF + `xygen` | `Oxygen` | PASS |
| E12R-27 | 127 | 6604?6605 | `inser` + LF + `tion` | `insertion` | PASS |
| E12R-28 | 127 | 6606?6607 | `r` + LF + `esuscitation` | `resuscitation` | PASS |
| E12R-29 | 127 | 6608?6609 | `Snake` + LF + `-bite` | `Snake-bite` | PASS |
| E12R-30 | 127 | 6610?6611 | `immobiliza` + LF + `tion` | `immobilization` | PASS |
| E12R-31 | 129 | 6664?6665 | `elemen` + LF + `ts` | `elements` | PASS |
| E12R-32 | 129 | 6670?6671 | `P` + LF + `ossible` | `Possible` | PASS |
| E12R-33 | 129 | 6672?6673 | `M` + LF + `anagement` | `Management` | PASS |
| E12R-34 | 129 | 6674?6675 | `c` + LF + `onsiderations` | `considerations` | PASS |
| E12R-35 | 129 | 6676?6677 | `c` + LF + `onsiderations` | `considerations` | PASS |
| E12R-36 | 129 | 6680?6681 | `T` + LF + `hen` | `Then` | PASS |
| E12R-37 | 129 | 6682?6683 | `T` + LF + `hen` | `Then` | PASS |

## Verification

- 37/37 exact contexts matched before write.
- Byte diff consists only of 37 LF deletions.
- Backup reconstruction with exactly these operations matched byte-for-byte.
- `splitlines()` decreased by 37; U+FFFD remains 0.
- No PDF or extracted file was modified.
