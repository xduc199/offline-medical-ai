
import hashlib, shutil

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''): h.update(chunk)
    return h.hexdigest()

src = r'd:/AI_YTe_Ngoai_Tuyen/knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1.txt'
backup = r'd:/AI_YTe_Ngoai_Tuyen/knowledge_base/03_cleaned/WHO_ICRC_Basic_Emergency_Care_2018_cleaned_v1_before_batch10E12B_fixes.txt'

sha_before = sha256_file(src)
print('SHA before:', sha_before)
shutil.copy2(src, backup)
assert sha256_file(backup) == sha_before
print('Backup OK')

with open(src, encoding='utf-8', newline='') as f:
    content = f.read()
lf_before = content.count(chr(10))

splits = [
    (' Suc', 'tion airway secretions, blood and/'),
    (' incr', 'eased work of breathing'),
    (' abnor', 'mal chest wall'),
    (' tr', 'acheal shift'),
    (' suck', 'ing chest wound'),
    (' abr', 'asion, bruising or other'),
    (' absen', 't or decreased breath'),
    (' seizur', 'es/convulsions'),
    (' Suspec', 't spine injury or closed head'),
    (' Gur', 'gling airway sounds'),
    (' Lar', 'ge haemothorax may'),
    (' Ur', 'ine colour changes (dark urine or obvious blood) to'),
    (' Unev', 'en chest wall movement or'),
    (' Dr', 'ooling'),
    (' Exposur', 'e to known allergen'),
    (' Gr', 'adually more laboured breathing'),
    (' Hollo', 'w sounds (hyperresonance) to percussion'),
    (' Diaphor', 'esis and mottled skin'),
    (' Dist', 'ended neck veins'),
    (' Slo', 'w, shallow breathing'),
    (' sw', 'elling of lips, tongue and mouth'),
    (' tach', 'ycardia and hypotension'),
    (' hist', 'ory of allergies'),
    (' hist', 'ory of tuberculosis'),
    (' Childr', 'en may present with rapid breathing as t'),
    (' Hear', 't failure'),
    (' Nalo', 'xone'),
    (' Sig', 'ns of airway obstruction (unable to swal'),
    (' Sig', 'ns of poor perfusion (tachycardia, tachy'),
    (' Sig', 'ns of poor perfusion'),
    (' Sig', 'ns of heart failure'),
    (' Sig', 'nificant pre-burn illness (such as diabe'),
    (' Dr', 'ess wound.'),
    (' Splin', 't the wound.'),
    (' Lac', 'eration'),
    (' Dr', 'ess wounds with sterile gauze, if availa'),
    (' Splin', 't extremities with large lacerations to'),
    (' Splin', 't fractures to keep bone ends from causi'),
    (' Bur', 'ns should be dressed and fluid needs cal'),
    (' Sk', 'in colour can'),
    (' Bur', 'ns involving the airway can rapidly caus'),
    (' Bur', 'ns are at high risk for infection, even'),
    (' Bur', 'ns involving the hands, face, groin area'),
    (' Bur', 'ns with other associated trauma'),
    (' per', 'form critical actions for high-risk caus'),
    (' per', 'form critical actions for patients with'),
    (' selec', 't appropriate fluid administration based'),
    (' Sk', 'in rash'),
    (' Dr', 'y mucous membranes'),
]

applied = []
skipped = []
for frag, cont in splits:
    old = frag + chr(10) + cont
    count = content.count(old)
    if count > 0:
        content = content.replace(old, frag + cont)
        applied.append((frag, cont, count))
    else:
        skipped.append((frag, cont))

with open(src, 'w', encoding='utf-8', newline='') as f:
    f.write(content)

sha_after = sha256_file(src)
lf_after = content.count(chr(10))
size_after = len(content.encode('utf-8'))
print('Applied:', len(applied), 'patterns,', sum(c for _,_,c in applied), 'total joins')
print('Skipped:', len(skipped))
print('LF removed:', lf_before - lf_after)
print('Size after:', size_after, 'bytes')
print('SHA after:', sha_after)
for frag, cont, n in applied:
    print('  APPLIED x' + str(n) + ': ' + repr((frag+cont)[:50]))
for frag, cont in skipped:
    print('  SKIP: ' + repr(frag + chr(10) + cont[:20]))
