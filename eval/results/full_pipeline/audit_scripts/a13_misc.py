import sys, os, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import build
W = sys.argv[1]
C = build(W)
r = json.load(open('a1_results.json'))
s = lambda k: set(r[k]['ids'])
rct13 = [p for p in r['L000195']['ids'] if 'Randomized Controlled Trial' in C['PMID ' + p]['pubtypes']]
print('13 RCT in L000424:', len(set(rct13) & s('L000424')), 'in L000426:', len(set(rct13) & s('L000426')))
print('L000459 - L000424:', len(s('L000459') - s('L000424')), '| L000424 - L000459:', len(s('L000424') - s('L000459')))
print('L000150 subset of L000149:', s('L000150') <= s('L000149'), r['L000150']['ids'])
print('L000443 ids', r['L000443']['ids'], 'L000444', r['L000444']['ids'], 'L000460', r['L000460']['ids'], 'L000427', r['L000427']['ids'], 'L000428', r['L000428']['ids'])
print('known in L000424:', [p for p in ['29235586','33879970','42104798','39361103'] if p in s('L000424')], '| in L000426:', [p for p in ['29235586','33879970','42104798','39361103'] if p in s('L000426')])
# ctgov L000468
studies = [C[k]['raw'] for k in C if C[k]['src'] == 'ctgov' and 'L000468' in C[k]['logs']]
print('L000468 studies', len(studies))
st = collections.Counter(x['protocolSection']['statusModule']['overallStatus'] for x in studies)
print('status', st.most_common())
print('hasResults', sum(1 for x in studies if x.get('hasResults')))
pm2026 = s('L000459')
linked = [x['protocolSection']['identificationModule']['nctId'] for x in studies if any((ref.get('pmid') in pm2026) for ref in x['protocolSection'].get('referencesModule', {}).get('references', []))]
linked_res = [x['protocolSection']['identificationModule']['nctId'] for x in studies if any((ref.get('pmid') in pm2026 and ref.get('type') in ('RESULT', 'DERIVED')) for ref in x['protocolSection'].get('referencesModule', {}).get('references', []))]
print('register entries listing one of the 2026 PubMed records (any ref type):', len(linked), '| as RESULT/DERIVED:', len(linked_res))
# ongoing L000198: rough independent rule
ong = [C[k]['raw'] for k in C if C[k]['src'] == 'ctgov' and 'L000198' in C[k]['logs']]
drug = [x for x in ong if any(re.search(r'gliflozin|sglt', (i.get('name') or '') + ' ' + ' '.join(i.get('otherNames', []) or []), re.I) for i in x['protocolSection'].get('armsInterventionsModule', {}).get('interventions', []))]
print('ongoing', len(ong), 'with gliflozin/SGLT intervention name', len(drug))
