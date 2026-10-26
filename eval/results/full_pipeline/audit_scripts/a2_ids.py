"""Audit 2: every PMID/NCT/DOI named in the conversation: which logged query retrieved it; saved title/year/journal."""
import json, os, sys, glob, re
import xml.etree.ElementTree as ET

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, 'a1_results.json')))
log = [json.loads(l) for l in open(os.path.join(W, 'log/actions.jsonl'))]
byid = {d['id']: d for d in log}

# PMIDs named in the conversation (S2-S4), with where and the claimed year (None if not stated)
CONV = [
 # S2 m6 soundness table
 ('40707349', 'S2m6#1', 2025), ('40916713', 'S2m6#2', 2025), ('41064961', 'S2m6#3', 2026), ('31192057', 'S2m6#4', 2019),
 ('42730799', 'S2m6#5', 2026), ('26861783', 'S2m6#6', 2016), ('33879970', 'S2m6#7', 2021), ('29235586', 'S2m6#8', 2014),
 ('28611859', 'S2m6#9', 2017), ('42892668', 'S2m6#10', 2026),
 # S2 m10 reviews naming body water
 ('37465122', 'S2m10#2', 2023), ('41748173', 'S2m10#3', 2026), ('34516288', 'S2m10#4', 2021),
 # S2 m12 nearest reviews
 ('34897070', 'S2m12#1', 2021), ('34542222', 'S2m12#2', 2021),
 # S2 m30 HF/kidney trials
 ('34325888', 'S2m30#1', 2021), ('33357505', 'S2m30#2', 2021), ('35478433', 'S2m30#3', 2022),
 # S2 m34 reviews bearing on focus
 ('42517896', 'S2m34#1', 2026), ('42215421', 'S2m34#2', 2026), ('42011503', 'S2m34#3', 2026), ('42339604', 'S2m34#5', 2026),
 ('36931466', 'S2m34#6', 2023), ('35909522', 'S2m34#7', 2022), ('33625242', 'S2m34 soundness', None), ('27550386', 'S2m34 soundness', None),
 # S3 known studies and batches
 ('42104798', 'S3m23 user known', None), ('39361103', 'S3m23 user known', None),
 ('28345814', 'S3m32#3', 2017), ('30675708', 'S3m32#4', 2019), ('31218819', 'S3m32#5', 2019), ('32568464', 'S3m32#6', 2020),
 ('33091173', 'S3m32#7', 2021), ('33186500', 'S3m32#8', 2021), ('33197559', 'S3m32#9', 2021), ('33351892', 'S3m32#10', 2021),
 ('25166023', 'S3m32 q3', None), ('25268802', 'S3m32 q3', None),
 ('34097062', 'S3m34#13', 2021), ('34716213', 'S3m34#15', 2022), ('35391843', 'S3m34#16', 2022), ('36266774', 'S3m34#18', 2022),
 ('37313125', 'S3m34#19', 2023), ('37436962', 'S3m34#20', 2023),
 ('38219335', 'S3m36#21', 2024), ('38365073', 'S3m36#22', 2024), ('40994705', 'S3m36#24', 2025), ('41347301', 'S3m36#25', 2026),
 ('41507062', 'S3m36#26', 2026),
 # S3 m38 methods guidance
 ('30453902', 'S3m38#1', 2018), ('42702311', 'S3m38#2', 2026), ('29504289', 'S3m38#3', 2018), ('34550585', 'S3m38#4', 2022),
 ('31948937', 'S3m38#5', 2020), ('31972274', 'S3m38#6', 2020), ('31253092', 'S3m38#7', 2019), ('41942890', 'S3m38#8', 2026),
 ('41484785', 'S3m38#9', 2026),
 # full texts named via PMC
 ('34057072', 'S4m8 case study (PMC8204237)', 2021), ('25554246', 'S4m12 PRISMA-P (PMC4320440)', 2015), ('41230118', 'S4m12 AI position (PMC12603384)', 2025),
 # other ids found in log text referred to as shown
 ('42286641', 'S3m36 substudy (L000545)', None),
]

def esearch_hits(pmid):
    hits = []
    for qid, v in r.items():
        d = byid[qid]
        if d['source'] == 'pubmed' and d['endpoint'] == 'esearch' and pmid in v['ids']:
            hits.append(qid)
    return hits

def efetch_hits(pmid):
    return [qid for qid, v in r.items() if byid[qid]['endpoint'] == 'efetch' and byid[qid]['source'] == 'pubmed' and pmid in v['ids']]

# saved metadata
saved = {}
for f in glob.glob(os.path.join(W, 'data/raw/*_pubmed_efetch_*.xml')):
    root = ET.parse(f).getroot()
    for a in root.findall('PubmedArticle'):
        pmid = a.find('.//MedlineCitation/PMID').text
        title = ''.join(a.find('.//ArticleTitle').itertext()) if a.find('.//ArticleTitle') is not None else ''
        j = a.find('.//Journal/Title'); jt = j.text if j is not None else ''
        y = a.find('.//JournalIssue/PubDate/Year'); md = a.find('.//JournalIssue/PubDate/MedlineDate')
        year = y.text if y is not None else (md.text[:4] if md is not None else None)
        dois = [e.text for e in a.findall('.//ArticleIdList/ArticleId') if e.get('IdType') == 'doi']
        saved.setdefault(pmid, dict(title=title, journal=jt, year=year, doi=dois[0] if dois else None, file=os.path.basename(f)))

out = []
for pmid, where, cy in CONV:
    es = esearch_hits(pmid); ef = efetch_hits(pmid)
    s = saved.get(pmid)
    out.append(dict(pmid=pmid, where=where, claimed_year=cy, esearch=es, efetch=ef, saved=s))
    print(pmid, where, 'claimed', cy, '| saved', (s or {}).get('year'), '|', ((s or {}).get('title') or '')[:90])
    print('    esearch:', es[:8], ('+%d' % (len(es) - 8)) if len(es) > 8 else '', '| efetch:', ef)
json.dump(out, open(os.path.join(HERE, 'a2_ids.json'), 'w'), indent=1)
