"""Audit 3: live NCBI esummary for every PMID in the saved efetch files (and every PMID named in the conversation);
compare title, journal, year, DOI with the saved records. At most 3 requests per second."""
import json, os, sys, glob, time, ssl, urllib.request, urllib.parse, re, html, unicodedata
import xml.etree.ElementTree as ET
import certifi

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
CTX = ssl.create_default_context(cafile=certifi.where())
BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
_last = [0.0]

def call(endpoint, params, post=False):
    wait = 0.36 - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    params = dict(params, tool='stir_l4_audit')
    data = urllib.parse.urlencode(params).encode()
    for attempt in range(4):
        try:
            if post:
                req = urllib.request.Request(BASE + endpoint, data=data)
            else:
                req = urllib.request.Request(BASE + endpoint + '?' + data.decode())
            with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
                _last[0] = time.time()
                return r.read()
        except Exception as e:
            _last[0] = time.time()
            time.sleep(1.5 * (attempt + 1))
            err = e
    raise err

def norm(s):
    s = html.unescape(s or '')
    s = unicodedata.normalize('NFKD', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'[^0-9a-z]+', ' ', s.lower()).strip()
    return s

saved = {}
for f in glob.glob(os.path.join(W, 'data/raw/*_pubmed_efetch_*.xml')):
    root = ET.parse(f).getroot()
    for a in root.findall('PubmedArticle'):
        pmid = a.find('.//MedlineCitation/PMID').text
        t = a.find('.//ArticleTitle')
        title = ''.join(t.itertext()) if t is not None else ''
        y = a.find('.//JournalIssue/PubDate/Year'); md = a.find('.//JournalIssue/PubDate/MedlineDate')
        year = y.text if y is not None else (md.text[:4] if md is not None else None)
        j = a.find('.//Journal/ISOAbbreviation')
        dois = [e.text for e in a.findall('.//PubmedData/ArticleIdList/ArticleId') if e.get('IdType') == 'doi']
        saved[pmid] = dict(title=title, year=year, journal=j.text if j is not None else None, doi=(dois[0] if dois else None))
    for a in root.findall('PubmedBookArticle'):
        pmid = a.find('.//BookDocument/PMID').text
        t = a.find('.//BookTitle'); at = a.find('.//ArticleTitle')
        saved[pmid] = dict(title=''.join((at if at is not None else t).itertext()), year=None, journal='(book)', doi=None)

conv = [x['pmid'] for x in json.load(open(os.path.join(HERE, 'a2_ids.json')))]
extra = ['34516288', '42339604']
allids = sorted(set(saved) | set(conv) | set(extra))
print('PMIDs to check live:', len(allids))
live = {}
for i in range(0, len(allids), 200):
    chunk = allids[i:i + 200]
    raw = call('esummary.fcgi', dict(db='pubmed', id=','.join(chunk), retmode='json', version='2.0'), post=True)
    j = json.loads(raw)
    for uid in j['result'].get('uids', []):
        rec = j['result'][uid]
        doi = None
        for aid in rec.get('articleids', []):
            if aid.get('idtype') == 'doi':
                doi = aid.get('value')
        live[uid] = dict(title=rec.get('title'), source=rec.get('source'), fulljournal=rec.get('fulljournalname'),
                         pubdate=rec.get('pubdate'), sortpubdate=rec.get('sortpubdate'), doi=doi,
                         pubtype=rec.get('pubtype'), error=rec.get('error'))
json.dump(live, open(os.path.join(HERE, 'a3_live.json'), 'w'))
missing = [p for p in allids if p not in live or live[p].get('error')]
print('not found live:', missing)
mism = []
for p in allids:
    if p not in saved or p not in live:
        continue
    s, l = saved[p], live[p]
    tn, ln = norm(s['title']), norm(l['title'])
    if tn != ln and not (tn in ln or ln in tn):
        mism.append(('title', p, s['title'][:100], l['title'][:100]))
    if s['doi'] and l['doi'] and s['doi'].lower() != l['doi'].lower():
        mism.append(('doi', p, s['doi'], l['doi']))
    ly = (l['pubdate'] or '')[:4]
    if s['year'] and ly and s['year'] != ly:
        mism.append(('year', p, s['year'], l['pubdate']))
print('saved records compared:', sum(1 for p in allids if p in saved and p in live))
for m in mism:
    print('MISMATCH', m)
