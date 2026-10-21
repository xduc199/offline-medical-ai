# Batch 10E-9A — Read-only audit report

## A. Baseline and integrity

- Cleaned file: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt`
- SHA-256 before audit: `c9369a736ee5876b3b12b7c3f1f0ce65010901bd63b68b0334a04428357c197c`
- Size: `465,688` bytes
- Python `splitlines()` count: `15,121`
- U+FFFD count: `0`
- Newline bytes: LF `15,120`; CRLF `0`; standalone CR `0`.
- The same values were read after the audit. **Integrity PASS; cleaned was not written or modified.**
- PDF source SHA-256: `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e`.
- Reference extracted files (read-only):
  - `WHO_ICRC_Basic_Emergency_Care_2018.txt` — SHA-256 `a8ca6da7e65e953f10b7220ec747fe5ca16f5422e6cdc1a8296bb8ba1cf8a017`
  - `WHO_ICRC_Basic_Emergency_Care_2018_pymupdf.txt` — SHA-256 `3a184fc725d35481039ff3cfa6c2b757d360e787f5eeac16d43b5a6de356acbd`
  - `WHO_ICRC_Basic_Emergency_Care_2018_fonttools.txt` — SHA-256 `a8ca6da7e65e953f10b7220ec747fe5ca16f5422e6cdc1a8296bb8ba1cf8a017`
- Workspace has no Git repository (`git rev-parse --show-toplevel` did not find one).
- `reports/` existed and was empty; no batch audit reports or scripts were found there. Existing batch backup files for 10E-3B through 10E-8B are present under `knowledge_base/03_cleaned`. Prior audit evidence in this report is from the audit results in the active Codex session, with the PDF pages listed below viewed directly.

## B. Regression checks

| Batch/check | Result | Notes |
|---|---|---|
| 10E-5B C01–C08 | PASS | All eight corrected items retained in context. |
| 10E-6B E6-01–E6-11 | PASS | Both `Signs of poor perfusion` occurrences and the other nine targets retained in context. |
| 10E-7B E7-01–E7-20 | PASS | All twenty corrected targets retained in context. |
| 10E-8B E8-01–E8-43 | PASS | All 43 target phrases checked; the bullet in `• MANAGEMENT OF POOR PERFUSION` is present. `Signs of poor perfusion` occurs five times in the current text. |

The principal E6 regression contexts were also checked individually: `Unconscious` (line 1515), `Signs of poor perfusion` (lines 1583 and 1610), `Distended neck veins` (1617), `Refer rapidly` (1636), `Sweating (diaphoresis)` (1649), `Altered mental` (1651), `Seizures/convulsions` (1656), `History of diabetes` (1661), `Responds quickly` (1665), and `If the person can speak and swallow` (1670). These are current line references, not historic ones.

## C. Visually verified extraction errors

Scope: candidate scan around cleaned lines 2100–2400, with adjacent context from line 2090 and boundary follow-through through line 2424. PDF pages were rendered and the corresponding regions viewed directly. Page numbers below are **physical PDF page numbers**; the printed page number is shown separately where visible. The fragments preserve line boundaries with `\n`. Proposed changes only; none were applied.

| ID | Cleaned line(s) | Exact fragment/context | Physical PDF page (printed) | Direct visual evidence | Minimal proposed change |
|---|---:|---|---|---|---|
| E9-01 | 2090–2091 | `• Children ar\ne able to maintain…` | 40 (32) | Page reads “Children are able to maintain normal blood pressure…” | Join `ar` + `e` → `are`; retain bullet and following space. |
| E9-02 | 2093–2094 | `• The amoun\nt of IV fluid…` | 40 (32) | Page reads “The amount of IV fluid appropriate for children…” | Join `amoun` + `t` → `amount`; retain bullet and following space. |
| E9-03 | 2161–2162 | ` S` + line break + `evere infection` | 42 (34) | Option A visibly reads “Severe infection.” | Join `S` + `evere` → `Severe`. |
| E9-04 | 2165–2166 | `C.\n A\nsthma attack` | 42 (34) | Option C reads “Asthma attack.” | Join `A` + `sthma` → `Asthma`. |
| E9-05 | 2172–2173 | `A.\n Placing…` split as `P` / `lacing her in the recovery position` | 42 (34) | Option A reads “Placing her in the recovery position.” | Join `P` + `lacing` → `Placing`. |
| E9-06 | 2174–2175 | `B. A\ndministering salbutamol` | 42 (34) | Option B reads “Administering salbutamol.” | Join `A` + `dministering` → `Administering`. |
| E9-07 | 2177–2178 | `C. Ja\nw thrust` | 42 (34) | Option C reads “Jaw thrust.” | Join `Ja` + `w` → `Jaw`. |
| E9-08 | 2179–2180 | `D. Head-tilt/chin-lif\nt` | 42 (34) | Option D visibly reads “Head-tilt/chin-lift.” | Join `lif` + `t` → `lift`; preserve hyphens. |
| E9-09 | 2192–2193 | `A.\n B\negin chest compressions` | 43 (35) | Option A reads “Begin chest compressions.” | Join `B` + `egin` → `Begin`. |
| E9-10 | 2196–2197 | `C.\n B\negin bag-valve-mask ventilations` | 43 (35) | Option C reads “Begin bag-valve-mask ventilations.” | Join `B` + `egin` → `Begin`. |
| E9-11 | 2202–2203 | `A. Check blood pr\nessure` | 43 (35) | Option A reads “Check blood pressure.” | Join `pr` + `essure` → `pressure`. |
| E9-12 | 2204–2205 | `B. Check A\nVPU scale` | 43 (35) | Option B reads “Check AVPU scale.” | Join `A` + `VPU` → `AVPU`. |
| E9-13 | 2208–2209 | `D. Check br\neathing` | 43 (35) | Option D reads “Check breathing.” | Join `br` + `eathing` → `breathing`. |
| E9-14 | 2213–2214 | `A.\n C\nrackles on both sides` | 43 (35) | Option A reads “Crackles on both sides.” | Join `C` + `rackles` → `Crackles`. |
| E9-15 | 2215–2216 | `B. A\nb sent lung sounds on one side` (line text: `A` / `bsent…`) | 43 (35) | Option B reads “Absent lung sounds on one side.” | Join `A` + `bsent` → `Absent`. |
| E9-16 | 2218–2219 | `C.\n S\ntridor` | 43 (35) | Option C reads “Stridor.” | Join `S` + `tridor` → `Stridor`. |
| E9-17 | 2220–2221 | `D. W\nheezing on both sides` | 43 (35) | Option D reads “Wheezing on both sides.” | Join `W` + `heezing` → `Wheezing`. |
| E9-18 | 2257–2258 | `1.\n r\necognize key history findings…` | 45 (37) | Objectives line reads “recognize key history findings…” | Join `r` + `ecognize` → `recognize`; keep lowercase. |
| E9-19 | 2260–2261 | `2.\n r\necognize physical examination findings…` | 45 (37) | Objectives line reads “recognize physical examination findings…” | Join `r` + `ecognize` → `recognize`; keep lowercase. |
| E9-20 | 2263–2264 | `3.\n per\nform Trauma Primary Survey…` | 45 (37) | Objectives line reads “perform Trauma Primary Survey…” | Join `per` + `form` → `perform`. |
| E9-21 | 2266–2267 | `4.\n per\nform Trauma Secondary Survey…` | 45 (37) | Objectives line reads “perform Trauma Secondary Survey…” | Join `per` + `form` → `perform`. |
| E9-22 | 2269–2270 | `5.\n r\necognize life-threatening injuries` | 45 (37) | Objectives line reads “recognize life-threatening injuries.” | Join `r` + `ecognize` → `recognize`; keep lowercase. |
| E9-23 | 2272–2273 | `6.\n per\nform critical interventions…` | 45 (37) | Objectives line reads “perform critical interventions…” | Join `per` + `form` → `perform`. |
| E9-24 | 2277–2278 | `•\n Spine immobiliza\ntion and log-roll manoeuvre` | 45 (37) | Skills list reads “Spine immobilization and log-roll manoeuvre.” | Join `immobiliza` + `tion` → `immobilization`. |
| E9-25 | 2280–2281 | `•\n Ja\nw-thrust manoeuvre` | 45 (37) | Skills list reads “Jaw-thrust manoeuvre.” | Join `Ja` + `w-thrust` → `Jaw-thrust`. |
| E9-26 | 2283–2284 | `•\n A\nirway suctioning` | 45 (37) | Skills list reads “Airway suctioning.” | Join `A` + `irway` → `Airway`. |
| E9-27 | 2286–2288 | `•\n I\nnsertion of oropharyngeal and\nnasopharyngeal airway` | 45 (37) | Skills list reads “Insertion of oropharyngeal and nasopharyngeal airway.” | Join `I` + `nsertion` → `Insertion`. |
| E9-28 | 2290–2291 | `•\n R\necovery Position` | 45 (37) | Skills list reads “Recovery Position.” | Join `R` + `ecovery` → `Recovery`. |
| E9-29 | 2293–2294 | `•\n O\xygen delivery` | 45 (37) | Skills list reads “Oxygen delivery.” | Join `O` + `xygen` → `Oxygen`. |
| E9-30 | 2296–2297 | `•\n Bag-\nvalve-mask ventilation` | 45 (37) | PDF shows the compound “Bag-valve-mask ventilation”; the hyphen occurs at the word boundary. | **No correction.** Valid hyphenated line break; retain as-is. `NOT_ERROR`. |
| E9-31 | 2299–2301 | `•\n Needle dec\nompression for tension pneumothorax` | 45 (37) | Skills list reads “Needle decompression for tension pneumothorax.” | Join `dec` + `ompression` → `decompression`. |
| E9-32 | 2303–2304 | `•\n T\nhree-sided dressing for a sucking chest wound` | 45 (37) | Skills list reads “Three-sided dressing…” | Join `T` + `hree-sided` → `Three-sided`. |
| E9-33 | 2308–2309 | `•\n T\nourniquet for haemorrhage control` | 45 (37) | Skills list reads “Tourniquet for haemorrhage control.” | Join `T` + `ourniquet` → `Tourniquet`. |
| E9-34 | 2311–2312 | `•\n IV line inser\ntion` | 45 (37) | Skills list reads “IV line insertion.” | Join `inser` + `tion` → `insertion`. |
| E9-35 | 2314–2315 | `•\n IV flluid r\nesuscitation` | 45 (37) | Skills list visibly reads “IV fluid resuscitation.” | Two minimal corrections at this one location: remove the extra `l` in `flluid` → `fluid`, and join `r` + `esuscitation` → `resuscitation`. |
| E9-36 | 2317–2318 | `•\n A\nVPU and GCS assessment` | 45 (37) | Skills list reads “AVPU and GCS assessment.” | Join `A` + `VPU` → `AVPU`. |
| E9-37 | 2320–2321 | `•\n P\nelvic binding` | 45 (37) | Skills list reads “Pelvic binding.” | Join `P` + `elvic` → `Pelvic`. |
| E9-38 | 2323–2324 | `•\n Basic fr\nacture immobilization` | 45 (37) | Skills list reads “Basic fracture immobilization.” | Join `fr` + `acture` → `fracture`. |
| E9-39 | 2326–2327 | `•\n T\nrauma secondary survey` | 45 (37) | Skills list reads “Trauma secondary survey.” | Join `T` + `rauma` → `Trauma`. |
| E9-40 | 2329–2330 | `•\n Basic w\nound management, including irrigation` | 45 (37) | Skills list reads “Basic wound management, including irrigation (washing).” | Join `w` + `ound` → `wound`. |
| E9-41 | 2333–2334 | `•\n Bur\nn management` | 45 (37) | Skills list reads “Burn management.” | Join `Bur` + `n` → `Burn`. |
| E9-42 | 2405–2406 | ` • Appr` + line break + `oach to trauma` | 48 (40) | Overview bullet reads “Approach to trauma.” | Join `Appr` + `oach` → `Approach`. |
| E9-43 | 2407–2408 | `• ABCDE: T\nrauma primary survey` | 48 (40) | Overview bullet reads “ABCDE: Trauma primary survey.” | Join `T` + `rauma` → `Trauma`. |
| E9-44 | 2411–2412 | `• ASK: Key hist\nory findings (SAMPLE history)` | 48 (40) | Overview bullet reads “ASK: Key history findings (SAMPLE history).” | Join `hist` + `ory` → `history`. |
| E9-45 | 2415–2417 | `• DO: Impor\ntant conditions… based on the history and secondary\nsurvey…` | 48 (40) | Overview bullet reads “Important conditions…” with the sentence continuing over a normal line wrap. | Join `Impor` + `tant` → `Important`; preserve other line wrap. |
| E9-46 | 2419–2420 | `– Tr\nauma in pregnancy` | 48 (40) | Overview sub-bullet reads “Trauma in pregnancy.” | Join `Tr` + `auma` → `Trauma`. |
| E9-47 | 2421–2422 | `– Special consider\nations in children` | 48 (40) | Overview sub-bullet reads “Special considerations in children.” | Join `consider` + `ations` → `considerations`. |
| E9-48 | 2423–2424 | `• Disposition consider\nations` | 48 (40) | Overview bullet reads “Disposition considerations.” | Join `consider` + `ations` → `considerations`. |

> Line-fragment evidence above is transcribed from the current cleaned file. The full surrounding text was inspected locally; ellipses only abbreviate context in this report and are not proposed replacement text.

### Additional observations outside the split-word candidate list

- On physical PDF pages 41 and 42, the assessment/intervention worksheet is a table. Its flattened cleaned rows and headers do not preserve the visual grid/columns reliably. Classified as `LAYOUT_ISSUE`; no content was moved or reconstructed.
- The cleaned text has `1–2` with U+2013 on the relevant worksheet lines; this is a range symbol, not U+FFFD. The PDF also shows a 1–2 range. It was preserved and not included as a split-word correction.
- Glossary pages 46–47 were viewed as boundary follow-through; no additional split-word candidate was identified there.

## D. Unverified candidates

No selected split-word candidate remains unverified: all 48 listed cases were checked against the corresponding PDF region. Of these, 47 are extraction errors and one (E9-30, `Bag-` / `valve-mask`) is a valid hyphenated boundary and should remain unchanged. The flattened worksheet layout on physical pages 41–42 remains a separate structural review item, not a token-level correction.

## E. Items retained unchanged

- E9-30 `Bag-` / `valve-mask`: valid compound hyphenation across the line boundary (`NOT_ERROR`).
- Worksheet/table layout on physical PDF pages 41–42: retain pending a dedicated layout audit.
- U+2013 in the `1–2` range: retained; PDF confirms the range.
- All other content, including punctuation, clinical wording, lists, values, units and line breaks outside the proposed locations, remains untouched.

## F. Summary and conclusion

- Candidate locations visually checked: **48**.
- `VERIFIED_ERROR`: **47** locations (including one location with two minimal text corrections: `flluid` and `r` / `esuscitation`).
- `NOT_ERROR`: **1** location (E9-30).
- `UNVERIFIED`: **0** among the selected candidates.
- `LAYOUT_ISSUE`: **2** worksheet/table regions (physical PDF pages 41 and 42).
- Additional candidate locations left in the inspected line window: **0**; this is a targeted scan, not a claim that the whole document is error-free.
- Regression checks: C01–C08 PASS; E6-01–E6-11 PASS; E7-01–E7-20 PASS; E8-01–E8-43 PASS.
- Audit status: **PASS — verified candidates identified for review before any write batch.**
- Operation: **READ-ONLY AUDIT**. No cleaned, PDF, extracted or backup file was modified. This report is the only new file.

No Batch 10E-9B edits have been applied.

