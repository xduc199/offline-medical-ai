# Batch 10E14B ? Verified joins

- Baseline SHA-256: `b38806d55a19d88c699a9704ee59761f74ae0664f92dc3c97c9396eb506b2136` (464,557 bytes; 14,006 splitlines; U+FFFD 0).
- Backup: `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E14B_32_verified_joins.txt`; SHA-256 matches baseline.
- Applied 32 visually confirmed joins from physical PDF pages 191?192 (cleaned lines 11125?11259): 27 within words and 5 punctuation-adjacent extraction breaks (`Check pulses` + `, ...` twice; and equivalent row continuation preserved as concatenation). Only LF line breaks were removed.
- Output SHA-256: `a3c7c3038ebefb8d5e4f8fd84b5915ea21b0da1e39a8bdb9fe88b09dfae194ba`; 464,525 bytes; 13,974 splitlines; U+FFFD 0.
- Reconstruction from original line array equals written bytes; byte delta -32; line delta -32.
- PASS for exact-context preconditions, backup hash, and reconstructed byte equality.
