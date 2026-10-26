import json, sys, os, ssl, urllib.request, urllib.parse, time
import certifi
CTX = ssl.create_default_context(cafile=certifi.where())
W = sys.argv[1]
log = {json.loads(l)['id']: json.loads(l) for l in open(os.path.join(W, 'log/actions.jsonl'))}
for lid in ['L000152', 'L000257', 'L000432']:
    p = log[lid]['parameters']
    q = {'search': p['search'], 'filter': p['filter'], 'per-page': 1}
    url = 'https://api.openalex.org/works?' + urllib.parse.urlencode(q)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'stir-l4-audit'}), context=CTX, timeout=60) as r:
            j = json.loads(r.read())
        print(lid, 'logged', log[lid]['n_total'], 'live', j['meta']['count'])
    except Exception as e:
        print(lid, 'live check failed:', str(e)[:200])
    time.sleep(1)
# DOI check for the Zenodo record
for doi in ['10.5281/zenodo.22978843']:
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.openalex.org/works/doi:' + doi, headers={'User-Agent': 'stir-l4-audit'}), context=CTX, timeout=60) as r:
            j = json.loads(r.read())
        print(doi, '->', j.get('id'), j.get('publication_year'), j.get('type'), (j.get('title') or '')[:120])
    except Exception as e:
        print(doi, 'openalex failed:', str(e)[:200])
    try:
        req = urllib.request.Request('https://doi.org/api/handles/' + doi, headers={'User-Agent': 'stir-l4-audit'})
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            j = json.loads(r.read())
        print(doi, 'doi.org handle responseCode', j.get('responseCode'), [v.get('data', {}).get('value') for v in j.get('values', []) if v.get('type') == 'URL'])
    except Exception as e:
        print(doi, 'doi.org failed:', str(e)[:200])
