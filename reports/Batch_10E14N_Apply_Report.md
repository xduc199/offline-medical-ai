# Batch 10E14N ? Verified extraction sentinel cleanup

- Status: **PASS**
- Scope: three literal `/uni00A0` extraction sentinel artifacts, visually compared with PDF source; no layout reconstruction.
- Input SHA-256: `77722be4220d638da877fe06a69fccfbd67eb9d734884a226c980b868d98231b` (464,401 bytes; 13,855 `splitlines()`; U+FFFD 0).
- Backup: `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E14N_sentinel_fixes.txt`
- Backup SHA-256: `77722be4220d638da877fe06a69fccfbd67eb9d734884a226c980b868d98231b`.

## Exact changes

| PDF physical page | Cleaned line before | Before | After | Visual evidence |
|---:|---:|---|---|---|
| 229 | 13061 | `Smoke inhalation and airway burns/uni00A0? rapid swelling can block the airway` | `Smoke inhalation and airway burns ? rapid swelling can block the airway` | Rendered source page visibly shows ?Smoke inhalation and airway burns ? rapid swelling can block the airway?. |
| 229 | 13111 | Same duplicated extracted line | Same corrected wording | Same PDF source wording. Duplicate text retained; no content was removed or reordered. |
| 234 | 13586 | `infection (meningitis)/uni00A0?  ` | `infection (meningitis) ?  ` | Rendered source table shows ?infection (meningitis) ? isolate patient and wear mask.? Existing two trailing spaces after dash retained. |

`/uni00A0` was replaced only in the three individually matched contexts by one ASCII space; en dash, following spaces, and all surrounding text were preserved.

## Verification

- Output SHA-256: `3b0d421707bc628316ad2a36ba11dfd437ce0e9b74aadbef02a1dd8827d00e29`.
- Output: 464,380 bytes; 13,855 `splitlines()`; U+FFFD 0.
- Exact reconstruction from backup using only the three listed replacements matched output byte-for-byte.
- Each old target count was exhausted (2 occurrences on the duplicate page-229 text, 1 occurrence on page 234); corrected contexts occur 2 and 1 times respectively.
- Full-file scan after the changes: no `/uni00A0`, `/f_l`, `/f_i`, or U+FB00?U+FB06 ligature characters remain. U+F0E0 (19), U+00A0 (16), U+2013 (359), and U+2022 (1,839) remain untouched.
- Tail review reached EOF: physical PDF page 238 visually confirms the paediatric/SBAR content; physical page 239 is blank; page 240 is the publication back cover. No further confirmed split-word artifact was identified in the remaining tail text.
- PDF and extracted-source files were only read. Their observed SHA-256 values are recorded in the handoff status.
