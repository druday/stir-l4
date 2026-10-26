import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import build
W = sys.argv[1]
C = build(W)
r = json.load(open('a1_results.json'))
ids195 = r['L000195']['ids']; ids193 = r['L000193']['ids']; ids126 = r['L000126']['ids']; ids192 = r['L000192']['ids']
rct = [p for p in ids195 if 'Randomized Controlled Trial' in C['PMID ' + p]['pubtypes']]
print('L000195 ids', len(ids195), 'RCT-tagged', len(rct))
def has(t, pats): return [p for p in pats if re.search(p, t, re.I)]
for p in rct:
    rec = C['PMID ' + p]; t = rec['text']
    aff = rec['affs'].split(' | ')[0]
    country = aff.split(',')[-1].strip()[:30]
    print('---', p, rec['title'][:110])
    print('   first-aff country:', country, '| drugs:', has(t, ['empagliflozin', 'dapagliflozin', 'canagliflozin', 'remogliflozin']),
          '| placebo' if re.search('placebo', t, re.I) else '| NO placebo', '| crossover' if re.search('cross-?over', t, re.I) else '')
    print('   fat words:', has(t, [r'fat mass', r'body fat', r'percent(age)? body fat', r'adipose', r'liver fat', r'hepatic fat', r'epicardial', r'visceral', r'subcutaneous', r'intrahepatic', r'\bfat\b']),
          '| lean/muscle:', has(t, [r'lean', r'fat-free', r'muscle']), '| water:', has(t, [r'body water', r'extracellular', r'plasma volume', r'fluid']),
          '| function:', has(t, [r'walk', r'grip', r'strength', r'physical performance']))
    print('   asian words:', has(t, [r'asia', r'chin', r'japan', r'korea', r'india', r'iran', r'hong kong', r'taiwan']), '| diab:', has(t, ['prediabet', 'with and without', 'without diabetes', 'non-?diabetic', 'T2D']))
    wk = re.findall(r'(\d+)[- ](?:weeks?|wk)', t) + [str(int(m)*4)+'(mo)' for m in re.findall(r'(\d+)[- ]months?', t)]
    print('   durations mentioned:', wk[:8])
# reviews among the 153 fetched (L000196) records of L000193
recs = [C['PMID ' + p] for p in ids193 if 'PMID ' + p in C and C['PMID ' + p]['src'] == 'pubmed']
print('L000193 ids', len(ids193), 'parsed article records', len(recs))
rev = [x for x in recs if 'Review' in x['pubtypes'] or 'Systematic Review' in x['pubtypes'] or 'Meta-Analysis' in x['pubtypes']]
rev_strict = [x for x in recs if 'Review' in x['pubtypes']]
print('tagged Review (strict "Review")', len(rev_strict), '| Review or SR or MA', len(rev))
mus = [x for x in rev_strict if re.search(r'muscle|lean', x['text'], re.I)]
print('strict reviews naming muscle or lean:', len(mus), [ (x['title'][:60], 'Systematic Review' in x['pubtypes']) for x in mus])
print('observational tagged:', sum('Observational Study' in x['pubtypes'] for x in recs), '| case reports:', sum('Case Reports' in x['pubtypes'] for x in recs), '| RCT:', sum('Randomized Controlled Trial' in x['pubtypes'] for x in recs))
for lid, ids in [('L000126', ids126), ('L000192', ids192)]:
    print(lid, [(p, C['PMID ' + p]['pubtypes']) for p in ids])
print('L000072', r['L000072']['ids'], C['PMID ' + r['L000072']['ids'][0]]['title'][:100])
