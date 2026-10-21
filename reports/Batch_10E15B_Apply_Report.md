# Batch 10E15B ? Apply FQA-01 Verified Split

- Status: **PASS for the single approved token join**.
- Baseline: SHA-256 `3b0d421707bc628316ad2a36ba11dfd437ce0e9b74aadbef02a1dd8827d00e29`; 464,380 bytes; 13,855 `splitlines()`; U+FFFD 0.
- Backup: `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E15B_FQA01.txt`; its SHA-256 equals the baseline.

## Applied change

At the first Trauma table copy only, cleaned lines 12910?12911:

```text
Sig
ns of open skull fracture (as above, with blood or ...)
? Signs of open skull fracture (as above, with blood or ...)
```

Physical PDF page 227 was rendered and directly shows the intact phrase ?Signs of open skull fracture (as above, with blood or fluid from the ears/nose)?. The second cleaned copy already had `Signs` and was left unchanged. Neither copy was removed or moved.

## Verification

- After SHA-256: `84bc1664880dd7bbe6eaf55d60eedb92038ea8b030f38121a927c485a991f9a9`.
- After: 464,379 bytes; 13,854 `splitlines()`; U+FFFD 0.
- Exactly one LF removed; byte delta ?1, line delta ?1.
- In-memory reconstruction from the byte-identical backup using this one exact contextual join matched the on-disk output byte-for-byte.
- The corrected phrase now appears in both retained table copies; no `Sig`/`ns` split remains in this target.
- PDF and extracted files were read only; their SHA-256 values remain as recorded in Batch 10E15A.
- Separate unresolved item: the cleaned file still contains two copies of the Trauma table while physical PDF page 227 shows one. This batch intentionally did not deduplicate, move, or restructure either block.
