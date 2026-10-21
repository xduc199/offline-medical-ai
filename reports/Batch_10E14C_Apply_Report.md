# Batch 10E14C ? Verified text joins

- Baseline: SHA-256 `a3c7c3038ebefb8d5e4f8fd84b5915ea21b0da1e39a8bdb9fe88b09dfae194ba`; 464,525 bytes; 13,974 splitlines; U+FFFD 0.
- Backup: `knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E14C_28_verified_joins.txt`; SHA-256 matches baseline.
- Applied 28 exact LF joins after direct visual checks of physical PDF pages 194, 196, 197. Joined split bullets, words and two punctuation-adjacent line breaks exactly as shown in the source.
- Output SHA-256 `fc9b353e1b2660749a16143c8809c60b149d2cff94175f033f194475d088b486`; 464,497 bytes; 13,946 splitlines; U+FFFD 0.
- Reconstructed output equals on-disk output byte-for-byte; diff is exactly 28 LF deletions, no other byte changes. PASS.
