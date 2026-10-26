"""Audit 1: integrity of raw files and recomputation of every logged query count from data/raw."""
import json, hashlib, glob, os, re, sys, csv
import xml.etree.ElementTree as ET

W = sys.argv[1]
log = [json.loads(l) for l in open(os.path.join(W, 'log/actions.jsonl'))]
byid = {d['id']: d for d in log}
manifest = {r['path']: r for r in csv.DictReader(open(os.path.join(W, 'data/manifest.csv')))}

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

problems = []
# manifest check
for p, r in manifest.items():
    fp = os.path.join(W, p)
    if not os.path.exists(fp):
        problems.append(('manifest_missing', p)); continue
    if sha(fp) != r['sha256']:
        problems.append(('manifest_sha_mismatch', p))
    if int(r['bytes']) != os.path.getsize(fp):
        problems.append(('manifest_bytes_mismatch', p))
raw_files = sorted(glob.glob(os.path.join(W, 'data/raw/*')))
for f in raw_files:
    rel = os.path.relpath(f, W)
    if rel not in manifest:
        problems.append(('not_in_manifest', rel))

results = {}
for d in log:
    if d['kind'] != 'query':
        continue
    rp = d['raw_path']
    files = sorted(glob.glob(os.path.join(W, rp)), key=lambda s: int(re.search(r'_(\d+)\.\w+$', s).group(1))) if rp else []
    if not files:
        problems.append(('no_raw', d['id'], rp)); continue
    # sha check: log sha256 may be of single file or combined
    shas = [sha(f) for f in files]
    logsha = d['sha256']
    sha_ok = None
    if logsha:
        if len(files) == 1:
            sha_ok = (shas[0] == logsha)
        else:
            comb = hashlib.sha256(b''.join(open(f, 'rb').read() for f in files)).hexdigest()
            sha_ok = logsha in shas or logsha == comb
            if not sha_ok:
                # try manifest-of-shas style
                sha_ok = 'unknown-combined'
    n_total = None; n_ret = None; ids = []
    src, ep = d['source'], d['endpoint']
    try:
        if src in ('pubmed', 'mesh') and ep == 'esearch':
            j = json.load(open(files[0]))
            n_total = int(j['esearchresult']['count'])
            ids = j['esearchresult']['idlist']; n_ret = len(ids)
        elif src == 'mesh' and ep == 'esummary':
            j = json.load(open(files[0]))
            ids = j['result']['uids']; n_total = len(ids); n_ret = len(ids)
        elif ep == 'efetch':
            ids = []
            for f in files:
                txt = open(f, 'rb').read()
                root = ET.fromstring(txt)
                if src == 'pubmed':
                    for a in root.iter('PubmedArticle'):
                        ids.append(a.find('.//MedlineCitation/PMID').text)
                    for a in root.iter('PubmedBookArticle'):
                        ids.append(a.find('.//BookDocument/PMID').text)
                else:
                    ids = ['pmc']
            n_ret = len(ids); n_total = len(d['parameters'].get('id', [])) if isinstance(d['parameters'].get('id'), list) else 1
        elif src == 'openalex':
            j = json.load(open(files[0]))
            n_total = j['meta']['count']; n_ret = len(j['results'])
            ids = [w['id'] for w in j['results']]
        elif src == 'ctgov' and ep == 'studies':
            tot = None; ids = []
            for f in files:
                j = json.load(open(f))
                if tot is None: tot = j.get('totalCount')
                ids += [s['protocolSection']['identificationModule']['nctId'] for s in j.get('studies', [])]
            n_total = tot; n_ret = len(ids)
        elif src == 'ctgov' and ep == 'version':
            n_total = None; n_ret = None
    except Exception as e:
        problems.append(('parse_error', d['id'], str(e)[:100]))
    results[d['id']] = dict(n_total=n_total, n_ret=n_ret, ids=ids, files=[os.path.basename(f) for f in files], sha_ok=sha_ok)
    lt, lr = d['n_total'], d['n_retrieved']
    if src in ('pubmed', 'mesh', 'openalex', 'ctgov') and ep in ('esearch', 'works', 'studies'):
        if lt != n_total:
            problems.append(('n_total_mismatch', d['id'], lt, n_total))
        if lr is not None and lr != n_ret and not (lr == 9999 and n_ret == 0):
            problems.append(('n_retrieved_mismatch', d['id'], lr, n_ret))
    if ep == 'efetch':
        if lr != n_ret:
            problems.append(('efetch_retrieved_mismatch', d['id'], lr, n_ret))
        req = d['parameters'].get('id')
        if isinstance(req, list):
            missing = sorted(set(req) - set(ids))
            if missing:
                problems.append(('efetch_ids_not_returned', d['id'], missing))
    if sha_ok is False:
        problems.append(('sha_mismatch', d['id']))

json.dump({k: {**v, 'ids': v['ids']} for k, v in results.items()}, open(os.path.join(os.path.dirname(__file__), 'a1_results.json'), 'w'))
print('queries checked:', len(results), 'raw files:', len(raw_files), 'manifest rows:', len(manifest))
for p in problems:
    print('PROBLEM', p)
