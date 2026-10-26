"""Audit 4: titles and years shown in the conversation vs live PubMed (and saved OpenAlex for the DOI-only record)."""
import json, os, sys, re, glob, html, unicodedata
import xml.etree.ElementTree as ET

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
live = json.load(open(os.path.join(HERE, 'a3_live.json')))

def norm(s):
    s = html.unescape(s or '')
    s = unicodedata.normalize('NFKD', s).replace('’', "'")
    s = re.sub(r'[^0-9a-z]+', ' ', s.lower()).strip()
    return s

# (pmid or None, title-as-shown (prefix if truncated), year shown, where)
SHOWN = [
 ('40707349', 'Effect of sodium-glucose cotransporter-2 inhibitors on skeletal muscle.', 2025, 'S2m6#1'),
 ('40916713', 'Multi-Center Health Informatics to Examine the Implementation of Guideline-Directed Medical Therapy in Chronic Kidney Disease.', 2025, 'S2m6#2'),
 ('41064961', 'Before you start: the safety of SGLT2 inhibitors for anti-obesity treatment.', 2026, 'S2m6#3'),
 ('31192057', 'Administration of Once-daily Canagliflozin to a Non-diabetic Patient in Addition to Standard Aerobic Exercise: A Case Report.', 2019, 'S2m6#4'),
 ('42730799', 'Clinical Physiology of SGLT2 Inhibitors in Non-diabetic and Diabetic Individuals.', 2026, 'S2m6#5'),
 ('26861783', 'Shift to Fatty Substrate Utilization in Response to Sodium-Glucose Cotransporter 2 Inhibition in Subjects Without Diabetes and Pa', 2016, 'S2m6#6'),
 ('33879970', 'Comparison of dapagliflozin and teneligliptin in nonalcoholic fatty liver disease patients without type 2 diabetes mellitus: a pr', 2021, 'S2m6#7'),
 ('29235586', 'Exploring glycosuria as a mechanism for weight and fat mass reduction. A pilot study with remogliflozin etabonate and sergliflozi', 2014, 'S2m6#8'),
 ('28611859', 'Ipragliflozin Improves Glycemic Control and Decreases Body Fat in Patients With Type 2 Diabetes Mellitus.', 2017, 'S2m6#9'),
 ('42892668', 'Glucose-Lowering Therapies in Type 2 Diabetes-Associated Sarcopenia: Mechanisms, Clinical Evidence and a Muscle-Centred Framework.', 2026, 'S2m6#10'),
 ('37465122', 'Effect of sodium-glucose transporter 2 inhibitors on sarcopenia in patients with type 2 d', 2023, 'S2m10#2'),
 ('41748173', 'Mechanisms of SGLT inhibitor action and physiological mediators: systematic review and pr', 2026, 'S2m10#3'),
 ('34516288', 'Sodium-Glucose Cotransporter 2 Inhibitors in Heart Failure', 2021, 'S2m10#4'),
 ('34897070', 'Effect of Sodium-Glucose Cotransporter 2 Inhibitors on Weight Reduction in Overweight and', 2021, 'S2m12#1'),
 ('34542222', 'Sodium-glucose co-transporter 2 inhibitors on weight change and cardiometabolic profiles', 2021, 'S2m12#2'),
 ('34325888', 'Mechanistic Insights of Empagliflozin in Nondiabetic Patients With HFrEF: From the EMPA-TROPISM', 2021, 'S2m30#1 (quoted part)'),
 ('33357505', 'estimated plasma volume, and measured glomerular filtration rate in patients with heart failure (Empire HF', 2021, 'S2m30#2 (quoted part)'),
 ('35478433', 'dapagliflozin on volume status and systemic haemodynamics in patients with chronic kidney disease without diabetes:', 2022, 'S2m30#3 (quoted part)'),
 ('42517896', 'Selective SGLT2 inhibitors in MASLD/MASH: an outcome-specific systematic review', 2026, 'S2m34#1'),
 ('42215421', 'Effectiveness of sodium-glucose cotransporter 2 inhibitors in patients with met', 2026, 'S2m34#2'),
 ('42011503', 'Emerging Effects of Glucagon-Like Peptide-1 Receptor Agonists and Sodium-Glucos', 2026, 'S2m34#3'),
 ('42339604', 'Effects of sodium-glucose cotransporter 2 inhibitors on body weight and metabol', 2026, 'S2m34#5'),
 ('36931466', 'Comparison of sodium-glucose cotransporter-2 inhibitors and thiazolidinediones', 2023, 'S2m34#6'),
 ('35909522', 'GLP-1 RAs and SGLT-2 Inhibitors for Insulin Resistance in Nonalcoholic Fatty Li', 2022, 'S2m34#7'),
 ('33197559', 'Randomized Trial of Empagliflozin in Nondiabetic Patients With Heart Failure and', 2021, 'S4m28 included'),
 ('41507062', 'Effects of empagliflozin in patients at risk of heart failure: the Empire Prevent', 2026, 'S4m28 included'),
 ('32568464', 'Effects of Empagliflozin Treatment on Glycerol-Derived Hepatic Gluconeogenesis in', 2020, 'S4m28 included'),
 ('29235586', 'Exploring glycosuria as a mechanism for weight and fat mass reduction. A pilot', 2014, 'S4m28 included'),
 # years only (titles paraphrased in the conversation)
 ('28345814', None, 2017, 'S3m32#3'), ('30675708', None, 2019, 'S3m32#4'), ('31218819', None, 2019, 'S3m32#5'),
 ('33091173', None, 2021, 'S3m32#7'), ('33186500', None, 2021, 'S3m32#8'), ('33351892', None, 2021, 'S3m32#10'),
 ('27550386', None, 2017, 'S3m32#2'),
 ('34097062', None, 2021, 'S3m34#13'), ('34716213', None, 2022, 'S3m34#15'), ('35391843', None, 2022, 'S3m34#16'),
 ('36266774', None, 2022, 'S3m34#18'), ('37313125', None, 2023, 'S3m34#19'), ('37436962', None, 2023, 'S3m34#20'),
 ('38219335', None, 2024, 'S3m36#21'), ('38365073', None, 2024, 'S3m36#22'), ('39361103', None, 2024, 'S3m36#23'),
 ('40994705', None, 2025, 'S3m36#24'), ('41347301', None, 2026, 'S3m36#25'), ('42104798', None, 2026, 'S3m24 2026 trial'),
 ('30453902', None, 2018, 'S3m38#1'), ('42702311', None, 2026, 'S3m38#2'), ('29504289', None, 2018, 'S3m38#3'),
 ('34550585', None, 2022, 'S3m38#4'), ('31948937', None, 2020, 'S3m38#5'), ('31972274', None, 2020, 'S3m38#6'),
 ('31253092', None, 2019, 'S3m38#7'), ('41942890', None, 2026, 'S3m38#8'), ('41484785', None, 2026, 'S3m38#9'),
 ('34057072', None, 2021, 'S4m8 2021 case study'), ('25554246', None, 2015, 'S4m12 PRISMA-P'), ('41230118', None, 2025, 'S4m12 AI statement'),
 ('25166023', None, 2014, 'S3m32 2014 pair'), ('25268802', None, 2014, 'S3m32 2014 pair'),
]
# titles shown without PMIDs (S4): (title prefix, year, cited log ids)
NOPMID = [
 ('Neuroimmune and Neurovascular Remodeling after Perinatal Hypoxia:', 2026, 'S4m8#1'),
 ('Evaluating the accuracy of full text and serial screening by one', 2026, 'S4m8#2'),
 ('The revised Cochrane risk of bias tool for randomized trials (RoB 2)', 2020, 'S4m8#3'),
 ("Risk-of-bias assessment using Cochrane's revised tool for randomized", 2023, 'S4m8#4'),
 ('RoB 2: a revised tool for assessing risk of bias in randomised trials', 2019, 'S4m8#5'),
 ('ROBINS-I: a tool for assessing risk of bias in non-randomised studies', 2016, 'S4m8#6'),
 ('Core GRADE 4: rating certainty of evidence-risk of bias, publication', 2025, 'S4m8#7'),
 ('Pooling of cohort studies and RCTs affects GRADE certainty of', 2022, 'S4m8#8'),
 ('PRISMA Extension for Scoping Reviews (PRISMA-ScR): Checklist and', 2018, 'S4m8#9'),
 ('The PRISMA 2020 statement: an updated guideline for reporting', 2021, 'S4m8#10'),
 ('Risk of bias in nonrandomized studies of interventions showed low', 2019, 'S4m10#1'),
 ('Methodologically rigorous risk of bias tools for nonrandomized', 2020, 'S4m10#2'),
 ('The ROBINS-I and the NOS had similar reliability but differed in', 2021, 'S4m10#3'),
 ('Preferred reporting items for systematic review and', 2015, 'S4m12#1-2'),
 ('An assessment of the extent to which the contents of PROSPERO', 2020, 'S4m12#3'),
 ('Position Statement on Artificial Intelligence (AI) Use in', 2025, 'S4m12#4-6'),
 ('Bibliometric, methodological and reporting characteristics of', 2026, 'S4m12#7'),
 ('The nuts and bolts of PROSPERO: an international prospective', 2012, 'S4m12#8'),
 ('Contemporary practices in scoping review protocol', 2026, 'S4m12#9'),
]

def year_of(rec):
    m = re.match(r'(\d{4})', rec.get('pubdate') or '')
    return int(m.group(1)) if m else None

print('== PMID-named titles/years vs live PubMed')
for pmid, t, y, where in SHOWN:
    rec = live.get(pmid)
    if not rec:
        print('NOT LIVE', pmid, where); continue
    ly = year_of(rec)
    ok_t = True
    if t:
        ok_t = norm(t) in norm(rec['title'])
    flag = '' if (ok_t and ly == y) else '  <-- CHECK'
    print(pmid, where, 'shown', y, 'live', rec['pubdate'], '|', rec['source'], '| title ok' if ok_t else '| TITLE DIFFERS: ' + rec['title'][:120], flag)

print('== titles shown without PMIDs: find in live records')
for t, y, where in NOPMID:
    hits = [(p, r) for p, r in live.items() if norm(r.get('title')).startswith(norm(t))]
    for p, r in hits:
        print(where, 'shown', y, '->', p, r['pubdate'], r['source'], '|', r['title'][:110], '' if year_of(r) == y else '  <-- YEAR CHECK')
    if not hits:
        print(where, 'NO MATCH for', t)
