"""Build a text corpus from the saved raw files: PubMed abstracts, OpenAlex abstracts, PMC full texts, ClinicalTrials.gov entries, MeSH records."""
import json, os, glob, re, html, unicodedata
import xml.etree.ElementTree as ET


def norm(s):
    s = html.unescape(s or '')
    s = unicodedata.normalize('NFKC', s)
    s = s.replace(' ', ' ').replace(' ', ' ').replace('\xa0', ' ')
    for a, b in [('‘', "'"), ('’', "'"), ('“', '"'), ('”', '"'), ('‐', '-'), ('‑', '-'), ('‒', '-'), ('–', '-'), ('—', '-'), ('−', '-')]:
        s = s.replace(a, b)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def build(W):
    corpus = {}  # key -> dict(src, log, text)
    for f in sorted(glob.glob(os.path.join(W, 'data/raw/*_pubmed_efetch_*.xml'))):
        lid = os.path.basename(f).split('_')[0]
        root = ET.parse(f).getroot()
        for a in root.findall('PubmedArticle'):
            pmid = a.find('.//MedlineCitation/PMID').text
            t = a.find('.//ArticleTitle')
            title = ''.join(t.itertext()) if t is not None else ''
            abst = ' '.join(''.join(x.itertext()) for x in a.findall('.//Abstract/AbstractText'))
            affs = ' | '.join(''.join(x.itertext()) for x in a.findall('.//AffiliationInfo/Affiliation'))
            pts = [x.text for x in a.findall('.//PublicationTypeList/PublicationType')]
            key = 'PMID ' + pmid
            rec = corpus.setdefault(key, dict(src='pubmed', logs=set(), title=title, text=norm(title + ' ' + abst), abstract=abst, affs=affs, pubtypes=pts))
            rec['logs'].add(lid)
        for a in root.findall('PubmedBookArticle'):
            pmid = a.find('.//BookDocument/PMID').text
            txt = ' '.join(a.itertext())
            rec = corpus.setdefault('PMID ' + pmid, dict(src='pubmed-book', logs=set(), title='', text=norm(txt), abstract='', affs='', pubtypes=['Book']))
            rec['logs'].add(lid)
    for f in sorted(glob.glob(os.path.join(W, 'data/raw/*_pmc_efetch_*.xml'))):
        lid = os.path.basename(f).split('_')[0]
        root = ET.parse(f).getroot()
        txt = ' '.join(root.itertext())
        corpus['PMC ' + lid] = dict(src='pmc', logs={lid}, title='', text=norm(txt))
    for f in sorted(glob.glob(os.path.join(W, 'data/raw/*_openalex_works_*.json'))):
        lid = os.path.basename(f).split('_')[0]
        j = json.load(open(f))
        for w in j.get('results', []):
            inv = w.get('abstract_inverted_index') or {}
            pos = []
            for word, ps in inv.items():
                for p in ps:
                    pos.append((p, word))
            abst = ' '.join(wd for _, wd in sorted(pos))
            key = 'OA ' + w['id'].split('/')[-1]
            rec = corpus.setdefault(key, dict(src='openalex', logs=set(), title=w.get('title') or '', text=norm((w.get('title') or '') + ' ' + abst),
                                              doi=w.get('doi'), pmid=(w.get('ids') or {}).get('pmid'), year=w.get('publication_year')))
            rec['logs'].add(lid)
    for f in sorted(glob.glob(os.path.join(W, 'data/raw/*_ctgov_studies_*.json'))):
        lid = os.path.basename(f).split('_')[0]
        j = json.load(open(f))
        for s in j.get('studies', []):
            nct = s['protocolSection']['identificationModule']['nctId']
            rec = corpus.setdefault('NCT ' + nct, dict(src='ctgov', logs=set(), title=s['protocolSection']['identificationModule'].get('briefTitle', ''), text=norm(json.dumps(s, ensure_ascii=False)), raw=s))
            rec['logs'].add(lid)
    for f in sorted(glob.glob(os.path.join(W, 'data/raw/*_mesh_esummary_*.json'))):
        lid = os.path.basename(f).split('_')[0]
        j = json.load(open(f))
        for uid in j['result'].get('uids', []):
            r = j['result'][uid]
            corpus['MESH ' + uid + ' ' + lid] = dict(src='mesh', logs={lid}, title=str(r.get('ds_meshterms', ''))[:80], text=norm(json.dumps(r, ensure_ascii=False)), raw=r)
    return corpus
