# Batch 10E-12C ? Controlled apply report

- Baseline: `fe87476fd3b83ad943b09a9899b5b4986b478f1c19b758017d48bb954a78dc82`, 465544 bytes, 14987 splitlines, U+FFFD 0, LF 14986.
- Backup: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12C_29_verified_joins.txt`; SHA-256 `fe87476fd3b83ad943b09a9899b5b4986b478f1c19b758017d48bb954a78dc82`.
- After: SHA-256 `386df86ff684565847e16d1196f911d33423d4ae6df8e7ecd6196221ad0a1163`, 465515 bytes, 14958 splitlines, U+FFFD 0, LF 14957.
- PDF SHA-256 unchanged: `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e`.

## Applied visually verified joins

| ID | Baseline lines | Exact join | Physical PDF page | Status |
|---|---:|---|---:|---|
| E12C-01 | 2412?2413 | `bur` + LF + `ned` ? `burned` | 49 | PASS |
| E12C-02 | 2416?2417 | `tr` + LF + `auma` ? `trauma` | 49 | PASS |
| E12C-03 | 2419?2420 | `haema` + LF + `toma` ? `haematoma` | 49 | PASS |
| E12C-04 | 2423?2424 | `alt` + LF + `ered` ? `altered` | 49 | PASS |
| E12C-05 | 2442?2443 | `P` + LF + `lace` ? `Place` | 49 | PASS |
| E12C-06 | 2446?2447 | `I` + LF + `f` ? `If` | 49 | PASS |
| E12C-07 | 2469?2470 | `c` + LF + `yanosis` ? `cyanosis` | 49 | PASS |
| E12C-08 | 2492?2493 | `P` + LF + `erform` ? `Perform` | 49 | PASS |
| E12C-09 | 2498?2499 | `P` + LF + `lace` ? `Place` | 49 | PASS |
| E12C-10 | 2502?2503 | `I` + LF + `f` ? `If` | 49 | PASS |
| E12C-11 | 2553?2554 | `c` + LF + `old` ? `cold` | 50 | PASS |
| E12C-12 | 2556?2557 | `w` + LF + `eak` ? `weak` | 50 | PASS |
| E12C-13 | 2562?2563 | `I` + LF + `f` ? `If` | 50 | PASS |
| E12C-14 | 2570?2571 | `I` + LF + `f` ? `If` | 50 | PASS |
| E12C-15 | 2576?2577 | `I` + LF + `f` ? `If` | 50 | PASS |
| E12C-16 | 2583?2584 | `fr` + LF + `acture` ? `fracture` | 50 | PASS |
| E12C-17 | 2586?2587 | `L` + LF + `eave` ? `Leave` | 50 | PASS |
| E12C-18 | 2591?2592 | `P` + LF + `osition` ? `Position` | 50 | PASS |
| E12C-19 | 2601?2602 | `c` + LF + `onfusion` ? `confusion` | 50 | PASS |
| E12C-20 | 2627?2628 | `I` + LF + `f` ? `If` | 50 | PASS |
| E12C-21 | 2645?2646 | `I` + LF + `f` ? `If` | 50 | PASS |
| E12C-22 | 2668?2669 | `R` + LF + `emove` ? `Remove` | 51 | PASS |
| E12C-23 | 2672?2673 | `R` + LF + `emove` ? `Remove` | 51 | PASS |
| E12C-24 | 2676?2677 | `C` + LF + `over` ? `Cover` | 51 | PASS |
| E12C-25 | 2682?2683 | `R` + LF + `espect` ? `Respect` | 51 | PASS |
| E12C-26 | 2693?2694 | `Ob` + LF + `vious` ? `Obvious` | 51 | PASS |
| E12C-27 | 2708?2709 | `W` + LF + `eak` ? `Weak` | 51 | PASS |
| E12C-28 | 2711?2712 | `C` + LF + `apillary` ? `Capillary` | 51 | PASS |
| E12C-29 | 2714?2715 | `e` + LF + `xam` ? `exam` | 51 | PASS |

## Verification

- 29/29 exact line contexts passed preflight: PASS.
- 29 unique LF bytes removed; no other byte differences: PASS.
- Byte-for-byte reconstruction from backup: PASS.
- Regression phrase checks: PASS.
- Direct visual source review: physical PDF pages 49?51; each listed fragment was visible as a single word in the relevant table or workbook region.

**Result: PASS ? 29 source-confirmed joins applied; no unrelated bytes changed.**
