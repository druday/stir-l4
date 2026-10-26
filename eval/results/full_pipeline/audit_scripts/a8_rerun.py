"""Audit 8: re-run every logged PubMed esearch live (count only, same term and date limits) and the ClinicalTrials.gov counts;
compare with the logged n_total. Also list PubMed 'phrases not found' warnings from the saved responses."""
import json, os, sys, time, ssl, urllib.request, urllib.parse, glob
import certifi
W = sys.argv[1]
CTX = ssl.create_default_context(cafile=certifi.where())
log = [json.loads(l) for l in open(os.path.join(W, 'log/actions.jsonl'))]
_last = [0.0]

def get(url, data=None):
    w = 0.36 - (time.time() - _last[0])
    if w > 0: time.sleep(w)
    for a in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': 'stir-l4-audit'})
            with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
                _last[0] = time.time(); return json.loads(r.read())
        except Exception as e:
            _last[0] = time.time(); err = e; time.sleep(2 * (a + 1))
    raise err

rows = []
for d in log:
    if d['kind'] != 'query' or d['source'] != 'pubmed' or d['endpoint'] != 'esearch':
        continue
    p = d['parameters']
    if p.get('purpose') == 'smoke test':
        continue
    params = dict(db='pubmed', term=p['term'], retmode='json', retmax=0, tool='stir_l4_audit')
    for k in ('datetype', 'mindate', 'maxdate'):
        if p.get(k): params[k] = p[k]
    j = get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', urllib.parse.urlencode(params).encode())
    live = int(j['esearchresult']['count'])
    rows.append((d['id'], d['n_total'], live))
    flag = '' if live == d['n_total'] else '  <-- differs by %+d' % (live - d['n_total'])
    print(d['id'], 'logged', d['n_total'], 'live', live, flag)

print('pubmed re-run:', len(rows), 'equal:', sum(1 for r in rows if r[1] == r[2]))
# ClinicalTrials.gov
for d in log:
    if d['kind'] == 'query' and d['source'] == 'ctgov' and d['endpoint'] == 'studies' and d['parameters'].get('purpose') != 'smoke test':
        p = {k: v for k, v in d['parameters'].items() if k.startswith('query.') or k.startswith('filter.')}
        p.update(countTotal='true', pageSize=1)
        j = get('https://clinicaltrials.gov/api/v2/studies?' + urllib.parse.urlencode(p))
        print(d['id'], 'ctgov logged', d['n_total'], 'live', j.get('totalCount'))
# phrases not found, from saved responses
for f in sorted(glob.glob(os.path.join(W, 'data/raw/*_pubmed_esearch_1.json'))):
    j = json.load(open(f))
    e = j.get('esearchresult', {})
    nf = (e.get('errorlist') or {}).get('phrasesnotfound') or []
    wl = (e.get('warninglist') or {})
    if nf or wl.get('quotedphrasesnotfound') or wl.get('phrasesignored'):
        print(os.path.basename(f), 'notfound', nf, 'quoted-not-found', wl.get('quotedphrasesnotfound'), 'ignored', wl.get('phrasesignored'))
