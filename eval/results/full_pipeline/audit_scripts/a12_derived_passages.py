import sys, os, csv, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import build, norm
csv.field_size_limit(10**8)
W = sys.argv[1]
C = build(W)
tot = ok = 0; bad = []
for f in sorted(glob.glob(os.path.join(W, 'data/derived/*.csv'))):
    rows = list(csv.DictReader(open(f, encoding='utf-8')))
    if not rows: continue
    cols = [c for c in rows[0] if c and ('passage' in c.lower() or c.lower() in ('quote', 'says', 'quoted'))]
    idcol = next((c for c in ('pmid', 'record_id', 'nct', 'id', 'key') if c in rows[0]), None)
    if not cols or not idcol: continue
    n = 0
    for r in rows:
        rid = (r[idcol] or '').strip()
        key = rid if rid.startswith(('PMID ', 'NCT ')) else ('NCT ' + rid if rid.startswith('NCT') else 'PMID ' + rid)
        rec = C.get(key)
        for c in cols:
            q = (r[c] or '').strip()
            if not q or q.lower() in ('none', 'nan', 'false', 'true'): continue
            frags = [norm(x) for x in re.split('…|\.\.\.', q) if norm(x)]
            tot += 1; n += 1
            texts = [rec['text']] if rec else []
            if not texts:
                bad.append((os.path.basename(f), rid, c, 'no record')); continue
            t = texts[0]; pos = 0; good = True
            for fr in frags:
                i = t.find(fr, pos)
                if i < 0: i = t.lower().find(fr.lower(), pos)
                if i < 0: good = False; break
                pos = i + len(fr)
            if good: ok += 1
            else: bad.append((os.path.basename(f), rid, c, q[:100]))
    print(os.path.basename(f), 'passages checked:', n)
print('TOTAL', tot, 'found', ok, 'not found', len(bad))
for b in bad[:40]: print('NOT FOUND', b)
