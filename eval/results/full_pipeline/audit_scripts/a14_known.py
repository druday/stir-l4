import json, ssl, urllib.request, urllib.parse, time, certifi
CTX = ssl.create_default_context(cafile=certifi.where())
r = json.load(open('a1_results.json'))
s459 = set(r['L000459']['ids'])
qs = {
 'Bays 2014 canagliflozin obese without diabetes': 'canagliflozin[ti] AND overweight[ti] AND obese[ti] AND without diabetes[ti]',
 'Hollander 2017 canagliflozin+phentermine': 'canagliflozin[ti] AND phentermine[ti]',
 'Bays 2020 licogliflozin body weight': 'licogliflozin[ti] AND weight[ti]',
 'empagliflozin body composition nondiabetic (any)': '(empagliflozin[ti] OR dapagliflozin[ti] OR canagliflozin[ti]) AND "body composition"[ti] AND (nondiabetic[ti] OR non-diabetic[ti] OR "without diabetes"[ti] OR obese[ti] OR obesity[ti])',
 'SGLT2 sarcopenia heart failure trial': '(empagliflozin[ti] OR dapagliflozin[ti]) AND (muscle[ti] OR sarcopenia[ti]) AND "heart failure"[ti] AND randomized[tiab]',
}
for name, q in qs.items():
    time.sleep(0.4)
    u = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + urllib.parse.urlencode(dict(db='pubmed', term=q, retmode='json', retmax=50, tool='stir_l4_audit'))
    j = json.loads(urllib.request.urlopen(u, context=CTX, timeout=60).read())
    ids = j['esearchresult']['idlist']
    time.sleep(0.4)
    titles = {}
    if ids:
        u2 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?' + urllib.parse.urlencode(dict(db='pubmed', id=','.join(ids), retmode='json', tool='stir_l4_audit'))
        j2 = json.loads(urllib.request.urlopen(u2, context=CTX, timeout=60).read())
        titles = {i: (j2['result'][i]['title'][:90], j2['result'][i]['pubdate'][:4]) for i in ids}
    print('==', name, '| hits', len(ids))
    for i in ids[:10]:
        print('  ', i, 'IN search4' if i in s459 else 'not in search4', titles.get(i))
