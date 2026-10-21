# Batch 10E-12B ? Apply Report

## Baseline and backup

- Before: SHA-256 `6ea79ab18bab13c5885d3fba2d1c0f182b830181b5030c6415d26b1b283bc48c`, 465611 bytes, 15054 splitlines, U+FFFD 0, LF 15053, CRLF 0, standalone CR 0.
- Backup: `D:\AI_YTe_Ngoai_Tuyen\knowledge_base\03_cleaned\WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12B_67_verified_joins.txt`; SHA-256 `6ea79ab18bab13c5885d3fba2d1c0f182b830181b5030c6415d26b1b283bc48c`; byte-for-byte equal to pre-edit cleaned.
- After: SHA-256 `fe87476fd3b83ad943b09a9899b5b4986b478f1c19b758017d48bb954a78dc82`, 465544 bytes, 14987 splitlines, U+FFFD 0, LF 14986, CRLF 0, standalone CR 0.
- PDF unchanged: SHA-256 `51e5000a8f268d67f28a8206e7b8a35ba7877bec0b45e28084970b074e00043e`.

## Applied fixes

- Candidate source: 49 patterns from `reports/batch12b.py`. 48 matched, producing 69 pattern hits; two hits overlap the same two `Sig` / `ns` line breaks, so 67 unique LF deletions were applied. Pattern 12 (`Urine colour changes...`) was absent and not edited.
- All unique occurrences were located by exact offset and page marker. Each mapped PDF physical page was rendered and visually checked. Each edit removed only the LF between the verified word fragments.
- No global replacement was used; unique offsets were processed from end to beginning.

| Pattern ID | Split fragment | Pattern hits | Cleaned lines before edit | PDF physical page(s) |
|---:|---|---:|---|---|
|01|`Suc\ntion airway secretions, blood and/`|1|2438|49|
|02|`incr\neased work of breathing`|1|2460|49|
|03|`abnor\nmal chest wall`|1|2463|49|
|04|`tr\nacheal shift`|1|2468|49|
|05|`suck\ning chest wound`|1|2471|49|
|06|`abr\nasion, bruising or other`|1|2479|49|
|07|`absen\nt or decreased breath`|1|2488|49|
|08|`seizur\nes/convulsions`|1|2612|50|
|09|`Suspec\nt spine injury or closed head`|1|2640|50|
|10|`Gur\ngling airway sounds`|1|2700|51|
|11|`Lar\nge haemothorax may`|1|2919|53|
|13|`Unev\nen chest wall movement or`|1|3789|66|
|14|`Dr\nooling`|3|5333, 5369, 7808|93, 94, 137|
|15|`Exposur\ne to known allergen`|1|5350|93|
|16|`Gr\nadually more laboured breathing`|1|5396|94|
|17|`Hollo\nw sounds (hyperresonance) to percussion`|1|5425|94|
|18|`Diaphor\nesis and mottled skin`|2|5489, 6581|95, 114|
|19|`Dist\nended neck veins`|9|5180, 5511, 5526, 6569, 6616, 6635, 10826, 11412, 11844|91, 95, 114, 164, 176, 183|
|20|`Slo\nw, shallow breathing`|1|5569|96|
|21|`sw\nelling of lips, tongue and mouth`|1|5596|96|
|22|`tach\nycardia and hypotension`|1|5603|96|
|23|`hist\nory of allergies`|1|5606|96|
|24|`hist\nory of tuberculosis`|1|5622|96|
|25|`Childr\nen may present with rapid breathing as t`|1|5758|98|
|26|`Hear\nt failure`|1|5893|102|
|27|`Nalo\nxone`|4|5803, 5916, 8270, 8372|99, 102, 145, 147|
|28|`Sig\nns of airway obstruction (unable to swal`|1|5724|98|
|29|`Sig\nns of poor perfusion (tachycardia, tachy`|2|5522, 6611|95, 114|
|30|`Sig\nns of poor perfusion`|4|3979, 5522, 6611, 7719|67, 95, 114, 137|
|31|`Sig\nns of heart failure`|2|5495, 6592|95, 114|
|32|`Sig\nnificant pre-burn illness (such as diabe`|1|4383|71|
|33|`Dr\ness wound.`|1|4106|68|
|34|`Splin\nt the wound.`|1|4111|68|
|35|`Lac\neration`|1|4128|69|
|36|`Dr\ness wounds with sterile gauze, if availa`|1|4156|69|
|37|`Splin\nt extremities with large lacerations to`|1|4164|69|
|38|`Splin\nt fractures to keep bone ends from causi`|1|4228|70|
|39|`Bur\nns should be dressed and fluid needs cal`|1|4289|70|
|40|`Sk\nin colour can`|1|4311|71|
|41|`Bur\nns involving the airway can rapidly caus`|1|4341|71|
|42|`Bur\nns are at high risk for infection, even`|1|4362|71|
|43|`Bur\nns involving the hands, face, groin area`|1|4370|71|
|44|`Bur\nns with other associated trauma`|1|4377|71|
|45|`per\nform critical actions for high-risk caus`|2|4824, 7248|83, 127|
|46|`per\nform critical actions for patients with`|1|5951|103|
|47|`selec\nt appropriate fluid administration based`|1|5957|103|
|48|`Sk\nin rash`|1|6411|112|
|49|`Dr\ny mucous membranes`|2|6451, 7728|112, 137|

## Verification

- 67 unique LF deletions: True; splitline reduction 67: True.
- Byte reconstruction from backup: True.
- Diff limited to exactly 67 deleted LF bytes: True.
- Old exact split patterns remaining: 0.
- Regression phrase checks C01?C08, E6, E7, E8, E9: PASS; prior detailed regression results are recorded in the 10E-9A audit report.

## Result

PASS ? 67 source-verified unique joins applied; no other bytes changed.
