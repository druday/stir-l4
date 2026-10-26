import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import build
W = sys.argv[1]
C = build(W)
checks = [
 ('PMID 40916713', ['Singapore', 'non-diabetic']),
 ('PMID 31192057', ['India', 'non-diabetic', 'Non-diabetic']),
 ('PMID 33879970', ['Japan', 'randomized', 'body water']),
 ('PMID 34897070', ['1.62', 'May 2021', 'fat mass', 'searched', 'Asian']),
 ('PMID 34542222', ['kg', 'fat mass', 'search', 'up to', 'until']),
 ('PMID 37465122', ['February 2023', 'fat mass', 'lean', 'skeletal muscle', 'body water']),
 ('PMID 33625242', ['20%', '0.80', 'heart failure', '1.21', 'body weight']),
 ('PMID 33357505', ['7.3', 'plasma volume', '88%']),
 ('PMID 35478433', ['six', '6 ', 'DAPASALT', 'sodium', 'blood pressure']),
 ('PMID 34325888', ['subcutaneous', 'adipose', 'fat']),
 ('PMID 27550386', ['adipose', 'lean', 'MRI', 'fat']),
 ('PMID 40707349', ['15', 'unchanged', 'Physical', 'muscle mass']),
 ('PMID 42011503', ['August 2025', 'testosterone', 'body composition', 'without diabetes']),
 ('PMID 35909522', ['March 2021', 'visceral', 'without']),
 ('PMID 41507062', ['extracellular', 'estimated', 'primary', 'DXA', 'fat', 'epicardial', 'body composition', 'non-diabetic']),
 ('PMID 29235586', ['random', 'placebo', 'fat-free', 'MRI', 'magnetic', 'TBW']),
 ('PMID 32568464', ['random', 'fat', 'placebo', 'magnetic']),
 ('PMID 33197559', ['random', '6-min', 'walk', 'fat', 'adipose']),
 ('PMID 41748173', ['population', 'glomerular', 'primary', 'fluid volume']),
 ('PMID 42730799', ['natriuresis', 'osmotic', 'hyperphagia']),
 ('PMID 26861783', ['without diabetes', 'similar']),
]
def snip(t, w, n=170):
    out = []
    for m in re.finditer(re.escape(w), t):
        out.append('…' + t[max(0, m.start() - n):m.end() + n] + '…')
        if len(out) >= 2: break
    return out
for key, words in checks:
    rec = C.get(key)
    if not rec:
        print(key, 'MISSING'); continue
    print('=====', key, rec['title'][:120], '| pubtypes', rec.get('pubtypes'))
    if 'affs' in rec: print('  first affiliation:', rec['affs'].split(' | ')[0][:160])
    for w in words:
        s = snip(rec['text'], w)
        if s:
            print('  [%s]' % w, s[0])
        else:
            print('  [%s] -- not in title/abstract' % w)
