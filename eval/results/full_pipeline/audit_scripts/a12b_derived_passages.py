import sys, os, csv, glob, re, json
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import build, norm
csv.field_size_limit(10**8)
W = sys.argv[1]
C = build(W)
# extra texts per pmid: labelled abstracts, OpenAlex abstracts, PMC full texts
alt = {}
for f in glob.glob(os.path.join(W, 'data/raw/*_pubmed_efetch_*.xml')):
    for a in ET.parse(f).getroot().findall('PubmedArticle'):
        pmid = a.find('.//MedlineCitation/PMID').text
        t = a.find('.//ArticleTitle'); title = ''.join(t.itertext()) if t is not None else ''
        parts = []
        for x in a.findall('.//Abstract/AbstractText'):
            lab = x.get('Label'); body = ''.join(x.itertext())
            parts.append((lab + ': ' if lab else '') + body)
        alt.setdefault(pmid, []).append(norm(title + ' ' + ' '.join(parts)))
for k, rec in C.items():
    if rec['src'] == 'openalex' and rec.get('pmid'):
        alt.setdefault(rec['pmid'].rstrip('/').split('/')[-1], []).append(rec['text'])
    if rec['src'] == 'openalex' and rec.get('doi'):
        alt.setdefault(rec['doi'].lower().replace('https://doi.org/', ''), []).append(rec['text'])
log = {json.loads(l)['id']: json.loads(l) for l in open(os.path.join(W, 'log/actions.jsonl'))}
for k, rec in C.items():
    if rec['src'] == 'pmc':
        lid = k.split()[1]; pm = log[lid]['parameters'].get('pmid')
        if pm: alt.setdefault(pm, []).append(rec['text'])
for k, rec in C.items():
    if rec['src'] == 'pubmed':
        alt.setdefault(k.split()[1], []).append(rec['text'])
    if rec['src'] == 'ctgov':
        alt.setdefault(k.split()[1], []).append(rec['text'])
tot = ok = 0; bad = []; skipped = 0
for f in sorted(glob.glob(os.path.join(W, 'data/derived/*.csv'))):
    rows = list(csv.DictReader(open(f, encoding='utf-8')))
    if not rows: continue
    cols = [c for c in rows[0] if c and ('passage' in c.lower() or c.lower() in ('quote', 'says', 'quoted'))]
    idcols = [c for c in ('pmid', 'record_id', 'nct', 'doi', 'id', 'key', 'work_id') if c in rows[0]]
    if not cols or not idcols: continue
    for r in rows:
        ids = []
        for c in idcols:
            v = (r[c] or '').strip()
            if not v: continue
            v = v.replace('PMID ', '').replace('https://doi.org/', '').lower() if c == 'doi' else v.replace('PMID ', '').replace('NCT ', '')
            ids.append(v)
        texts = [t for i in ids for t in alt.get(i, [])]
        for c in cols:
            q = (r[c] or '').strip()
            if not q or q.lower() in ('none', 'nan', 'false', 'true', 'not stated', 'no record'): continue
            tot += 1
            if not texts:
                skipped += 1; bad.append((os.path.basename(f), ids, c, 'NO SAVED TEXT', q[:80])); continue
            frags = [norm(x) for x in re.split('…|\.\.\.', q) if norm(x)]
            good = False
            for t in texts:
                pos = 0; g = True
                for fr in frags:
                    i = t.find(fr, pos)
                    if i < 0: i = t.lower().find(fr.lower(), pos)
                    if i < 0: g = False; break
                    pos = i + len(fr)
                if g: good = True; break
            if good: ok += 1
            else: bad.append((os.path.basename(f), ids, c, q[:110]))
print('TOTAL passages', tot, 'found', ok, 'not found', len(bad), '(of which no saved text', skipped, ')')
for b in [x for x in bad if x[0]!="step5_ongoing_studies.csv"]: print('NOT FOUND', b)
