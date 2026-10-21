# Batch 10E-9B - Apply report

**Status: PASS**

## Baseline before editing

- Cleaned: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt`
- SHA-256: `c9369a736ee5876b3b12b7c3f1f0ce65010901bd63b68b0334a04428357c197c`
- Size: `465,688` bytes; `splitlines()`: `15,121`; U+FFFD: `0`.
- Newlines: LF 15,120; CRLF 0; standalone CR 0; BOM absent.

## Backup

- `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E9B_47_verified_fixes.txt`
- SHA-256: `c9369a736ee5876b3b12b7c3f1f0ce65010901bd63b68b0334a04428357c197c`; byte-for-byte equal to baseline: **True**.

## Applied scope

- Applied all **47/47 verified locations**. E9-30 (`Bag-` / `valve-mask`) was not edited.
- Atomic edits: **48** - 47 LF joins plus removal of one extra `l` in E9-35. The E9-35 `r` + `esuscitation` join is included in the 47 LF joins.
- No approved item was skipped or blocked. All 47 line-pair contexts matched, and each wider context was unique.

| ID | Before-edit line references | Before | After | Result |
|---|---:|---|---|---|
| E9-01 | 2090-2091 | `• Children ar\ne able to maintain normal blood pressure for longer than adults when they are` | `• Children are able to maintain normal blood pressure for longer than adults when they are` | PASS |
| E9-02 | 2093-2094 | `• The amoun\nt of IV fluid appropriate for children is different from that for adults. [See SKILLS]` | `• The amount of IV fluid appropriate for children is different from that for adults. [See SKILLS]` | PASS |
| E9-03 | 2161-2162 | ` S\nevere infection` | ` Severe infection` | PASS |
| E9-04 | 2165-2166 | ` A\nsthma attack` | ` Asthma attack` | PASS |
| E9-05 | 2172-2173 | ` P\nlacing her in the recovery position` | ` Placing her in the recovery position` | PASS |
| E9-06 | 2174-2175 | `B. A\ndministering salbutamol` | `B. Administering salbutamol` | PASS |
| E9-07 | 2177-2178 | ` Ja\nw thrust` | ` Jaw thrust` | PASS |
| E9-08 | 2179-2180 | `D. Head-tilt/chin-lif\nt` | `D. Head-tilt/chin-lift` | PASS |
| E9-09 | 2192-2193 | ` B\negin chest compressions` | ` Begin chest compressions` | PASS |
| E9-10 | 2196-2197 | ` B\negin bag-valve-mask ventilations` | ` Begin bag-valve-mask ventilations` | PASS |
| E9-11 | 2202-2203 | ` Check blood pr\nessure` | ` Check blood pressure` | PASS |
| E9-12 | 2204-2205 | `B. Check A\nVPU scale` | `B. Check AVPU scale` | PASS |
| E9-13 | 2208-2209 | `D. Check br\neathing` | `D. Check breathing` | PASS |
| E9-14 | 2213-2214 | ` C\nrackles on both sides` | ` Crackles on both sides` | PASS |
| E9-15 | 2215-2216 | `B. A\nbsent lung sounds on one side ` | `B. Absent lung sounds on one side ` | PASS |
| E9-16 | 2218-2219 | ` S\ntridor` | ` Stridor` | PASS |
| E9-17 | 2220-2221 | `D. W\nheezing on both sides` | `D. Wheezing on both sides` | PASS |
| E9-18 | 2257-2258 | ` r\necognize key history findings suggestive of high-risk injuries;` | ` recognize key history findings suggestive of high-risk injuries;` | PASS |
| E9-19 | 2260-2261 | ` r\necognize physical examination findings suggestive of high-risk injuries;` | ` recognize physical examination findings suggestive of high-risk injuries;` | PASS |
| E9-20 | 2263-2264 | ` per\nform Trauma Primary Survey (the ABCDE approach to trauma patients);` | ` perform Trauma Primary Survey (the ABCDE approach to trauma patients);` | PASS |
| E9-21 | 2266-2267 | ` per\nform Trauma Secondary Survey (the head-to-toe trauma exam);` | ` perform Trauma Secondary Survey (the head-to-toe trauma exam);` | PASS |
| E9-22 | 2269-2270 | ` r\necognize life-threatening injuries; ` | ` recognize life-threatening injuries; ` | PASS |
| E9-23 | 2272-2273 | ` per\nform critical interventions for high-risk conditions.` | ` perform critical interventions for high-risk conditions.` | PASS |
| E9-24 | 2277-2278 | ` Spine immobiliza\ntion and log-roll manoeuvre` | ` Spine immobilization and log-roll manoeuvre` | PASS |
| E9-25 | 2280-2281 | ` Ja\nw-thrust manoeuvre` | ` Jaw-thrust manoeuvre` | PASS |
| E9-26 | 2283-2284 | ` A\nirway suctioning` | ` Airway suctioning` | PASS |
| E9-27 | 2286-2287 | ` I\nnsertion of oropharyngeal and ` | ` Insertion of oropharyngeal and ` | PASS |
| E9-28 | 2290-2291 | ` R\necovery Position` | ` Recovery Position` | PASS |
| E9-29 | 2293-2294 | ` O\nxygen delivery` | ` Oxygen delivery` | PASS |
| E9-31 | 2299-2300 | ` Needle dec\nompression for tension ` | ` Needle decompression for tension ` | PASS |
| E9-32 | 2303-2304 | ` T\nhree-sided dressing for a sucking chest wound` | ` Three-sided dressing for a sucking chest wound` | PASS |
| E9-33 | 2308-2309 | ` T\nourniquet for haemorrhage control` | ` Tourniquet for haemorrhage control` | PASS |
| E9-34 | 2311-2312 | ` IV line inser\ntion` | ` IV line insertion` | PASS |
| E9-35 | 2314-2315 | ` IV flluid r\nesuscitation ` | ` IV fluid resuscitation ` | PASS |
| E9-36 | 2317-2318 | ` A\nVPU and GCS assessment` | ` AVPU and GCS assessment` | PASS |
| E9-37 | 2320-2321 | ` P\nelvic binding` | ` Pelvic binding` | PASS |
| E9-38 | 2323-2324 | ` Basic fr\nacture immobilization` | ` Basic fracture immobilization` | PASS |
| E9-39 | 2326-2327 | ` T\nrauma secondary survey` | ` Trauma secondary survey` | PASS |
| E9-40 | 2329-2330 | ` Basic w\nound management, including irrigation ` | ` Basic wound management, including irrigation ` | PASS |
| E9-41 | 2333-2334 | ` Bur\nn management` | ` Burn management` | PASS |
| E9-42 | 2405-2406 | ` • Appr\noach to trauma` | ` • Approach to trauma` | PASS |
| E9-43 | 2407-2408 | ` • ABCDE: T\nrauma primary survey` | ` • ABCDE: Trauma primary survey` | PASS |
| E9-44 | 2411-2412 | ` • ASK: Key hist\nory findings (SAMPLE history)` | ` • ASK: Key history findings (SAMPLE history)` | PASS |
| E9-45 | 2415-2416 | ` • DO: Impor\ntant conditions to recognize and manage based on the history and secondary` | ` • DO: Important conditions to recognize and manage based on the history and secondary` | PASS |
| E9-46 | 2419-2420 | ` – Tr\nauma in pregnancy` | ` – Trauma in pregnancy` | PASS |
| E9-47 | 2421-2422 | ` – Special consider\nations in children` | ` – Special considerations in children` | PASS |
| E9-48 | 2423-2424 | ` • Disposition consider\nations` | ` • Disposition considerations` | PASS |
| E9-35 spelling | 2314 | `flluid` | `fluid` | PASS |

## Diff and reconstruction

- Exact diff accounting: 47 LF bytes removed and 1 additional byte removed; no byte additions.
- The additional deletion is the approved extra `l` in `flluid` - `fluid` at E9-35.
- Reconstructed from backup with only the approved operations; byte-for-byte: **PASS**.
- E9-30 unchanged: **PASS**.
- Worksheet tables from physical PDF pages 41-42 unchanged: **PASS**.
- Encoding remains UTF-8 without BOM and LF line endings.

## Integrity after editing

- SHA-256: `ce428bd65b526af744b4de052f5ac4f12ac5337bf0ffbc1b2ac2966c9b57726f`
- Size: `465,640` bytes
- `splitlines()`: `15,074`
- U+FFFD: `0`
- Newlines: LF `15,073`; CRLF `0`; standalone CR `0`; BOM absent.

## Regression checks

| Batch | Results |
|---|---:|
| 10E-5B C01-C08 | 8/8 PASS |
| 10E-6B E6 context | 10/10 PASS |
| 10E-7B E7-01-E7-20 | 20/20 PASS |
| 10E-8B E8-01-E8-43 + header bullet | 44/44 PASS |

### 10E-5B C01-C08

- C01: PASS
- C02: PASS
- C03: PASS
- C04: PASS
- C05: PASS
- C06: PASS
- C07: PASS
- C08: PASS

### 10E-6B

- item-01: PASS
- item-02: PASS
- item-03: PASS
- item-04: PASS
- item-05: PASS
- item-06: PASS
- item-07: PASS
- item-08: PASS
- item-09: PASS
- Signs of poor perfusion (at least 2): PASS

### 10E-7B

- E7-01: PASS
- E7-02: PASS
- E7-03: PASS
- E7-04: PASS
- E7-05: PASS
- E7-06: PASS
- E7-07: PASS
- E7-08: PASS
- E7-09: PASS
- E7-10: PASS
- E7-11: PASS
- E7-12: PASS
- E7-13: PASS
- E7-14: PASS
- E7-15: PASS
- E7-16: PASS
- E7-17: PASS
- E7-18: PASS
- E7-19: PASS
- E7-20: PASS

### 10E-8B

- E8-01: PASS
- E8-02: PASS
- E8-03: PASS (verified the actual UTF-8 text around the word sniffing without relying on a console-encoded curly-quote literal)
- E8-04: PASS
- E8-05: PASS
- E8-06: PASS
- E8-07: PASS
- E8-08: PASS
- E8-09: PASS
- E8-10: PASS
- E8-11: PASS
- E8-12: PASS
- E8-13: PASS
- E8-14: PASS
- E8-15: PASS
- E8-16: PASS
- E8-17: PASS
- E8-18: PASS
- E8-19: PASS
- E8-20: PASS
- E8-21: PASS
- E8-22: PASS
- E8-23: PASS
- E8-24: PASS
- E8-25: PASS
- E8-26: PASS
- E8-27: PASS
- E8-28: PASS
- E8-29: PASS
- E8-30: PASS
- E8-31: PASS
- E8-32: PASS
- E8-33: PASS
- E8-34: PASS
- E8-35: PASS
- E8-36: PASS
- E8-37: PASS
- E8-38: PASS
- E8-39: PASS
- E8-40: PASS
- E8-41: PASS
- E8-42: PASS
- E8-43: PASS
- E8 header bullet: PASS (verified U+2022 directly)

The first E8 check used a typographic quote literal that was mis-encoded in the shell input. Follow-up checks inspected the actual UTF-8 context and U+2022 code point directly; both checks PASS. This affected the regression probe only, not the cleaned data.

## Protected files

- PDF: SHA-256 `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e` - PASS, unchanged.
- extracted TXT: SHA-256 `a8ca6da7e65e953f10b7220ec747fe5ca16f5422e6cdc1a8296bb8ba1cf8a017` - PASS, unchanged.
- extracted PyMuPDF: SHA-256 `3a184fc725d35481039ff3cfa6c2b757d360e787f5eeac16d43b5a6de356acbd` - PASS, unchanged.
- extracted fonttools: SHA-256 `a8ca6da7e65e953f10b7220ec747fe5ca16f5422e6cdc1a8296bb8ba1cf8a017` - PASS, unchanged.

Only the cleaned target, the named backup, and this requested report were written. No next batch was started.
