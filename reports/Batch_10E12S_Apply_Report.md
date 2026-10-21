# Batch 10E12S ? Apply Report

Status: **PASS**. Applied 28 exact joins visually verified on physical PDF pages 131?136. The AVPU single-letter labels were deliberately retained as labels; the printed `space-occupying` line hyphen and `inflamation` source spelling were not altered.

## Integrity

| Measure | Before | Backup | After |
|---|---:|---:|---:|
| SHA-256 | `0ff109610397caa21d5f7ddea849dad0722c7f82748666ea10b4ae3a79f1b6e9` | `0ff109610397caa21d5f7ddea849dad0722c7f82748666ea10b4ae3a79f1b6e9` | `a08cf6335792c687fb93d3d11a7e4dce5b45b601b51d9772d0ead5735664d3da` |
| Bytes | 464912 | 464912 | 464884 |
| `splitlines()` | 14355 | 14355 | 14327 |
| U+FFFD | 0 | 0 | 0 |

Backup: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12S_28_verified_joins.txt`; hash matches baseline. PDF SHA-256 (read only): `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e`.

## Exact edits

| ID | Physical PDF page | Pre-edit cleaned lines | Fragments | Joined word | Status |
|---|---:|---:|---|---|---|
| E12S-01 | 131 | 6719?6720 | `W` + LF + `hen` | `When` | PASS |
| E12S-02 | 132 | 6757?6758 | `an` + LF + `yone` | `anyone` | PASS |
| E12S-03 | 132 | 6779?6780 | `H` + LF + `istory` | `History` | PASS |
| E12S-04 | 133 | 6790?6791 | `H` + LF + `istory` | `History` | PASS |
| E12S-05 | 133 | 6796?6797 | `H` + LF + `istory` | `History` | PASS |
| E12S-06 | 133 | 6799?6800 | `H` + LF + `istory` | `History` | PASS |
| E12S-07 | 133 | 6809?6810 | `H` + LF + `istory` | `History` | PASS |
| E12S-08 | 133 | 6813?6814 | `H` + LF + `istory` | `History` | PASS |
| E12S-09 | 133 | 6816?6817 | `H` + LF + `istory` | `History` | PASS |
| E12S-10 | 133 | 6820?6821 | `H` + LF + `istory` | `History` | PASS |
| E12S-11 | 133 | 6825?6826 | `U` + LF + `se` | `Use` | PASS |
| E12S-12 | 133 | 6829?6830 | `H` + LF + `istory` | `History` | PASS |
| E12S-13 | 134 | 6848?6849 | `R` + LF + `ecent` | `Recent` | PASS |
| E12S-14 | 134 | 6854?6855 | `R` + LF + `ecent` | `Recent` | PASS |
| E12S-15 | 135 | 6898?6899 | `C` + LF + `heck` | `Check` | PASS |
| E12S-16 | 135 | 6909?6910 | `C` + LF + `heck` | `Check` | PASS |
| E12S-17 | 135 | 6923?6924 | `I` + LF + `n` | `In` | PASS |
| E12S-18 | 135 | 6926?6927 | `C` + LF + `heck` | `Check` | PASS |
| E12S-19 | 135 | 6930?6931 | `C` + LF + `heck` | `Check` | PASS |
| E12S-20 | 135 | 6934?6935 | `C` + LF + `heck` | `Check` | PASS |
| E12S-21 | 135 | 6938?6939 | `C` + LF + `heck` | `Check` | PASS |
| E12S-22 | 135 | 6944?6945 | `C` + LF + `heck` | `Check` | PASS |
| E12S-23 | 136 | 6956?6957 | `C` + LF + `heck` | `Check` | PASS |
| E12S-24 | 136 | 6960?6961 | `C` + LF + `heck` | `Check` | PASS |
| E12S-25 | 136 | 6967?6968 | `C` + LF + `heck` | `Check` | PASS |
| E12S-26 | 136 | 6971?6972 | `C` + LF + `heck` | `Check` | PASS |
| E12S-27 | 136 | 6974?6975 | `C` + LF + `heck` | `Check` | PASS |
| E12S-28 | 136 | 6979?6980 | `M` + LF + `onitor` | `Monitor` | PASS |

## Verification

- 28/28 line contexts matched before write.
- Diff consists of exactly 28 LF deletions, with no other byte changes.
- Reconstructed from backup using these joins: byte-for-byte match **PASS**.
- `splitlines()` decreased by 28; U+FFFD remains 0.
- PDF and extracted sources were not modified.
