"""Audit 7: search strings as shown in the conversation (transcribed block by block) vs the logged terms."""
import json, os, sys
W = sys.argv[1]
log = {}
for l in open(os.path.join(W, 'log/actions.jsonl')):
    d = json.loads(l); log[d['id']] = d

def term(lid):
    p = log[lid]['parameters']
    return p.get('term') or p.get('search') or p.get('query.intr') or p.get('query.outc')

D16 = '"Sodium-Glucose Transporter 2 Inhibitors"[Mesh] OR SGLT2*[tiab] OR "SGLT-2"[tiab] OR "sodium-glucose cotransporter 2"[tiab] OR "sodium glucose cotransporter 2"[tiab] OR "sodium-glucose co-transporter 2"[tiab] OR gliflozin*[tiab] OR empagliflozin[tiab] OR dapagliflozin[tiab] OR canagliflozin[tiab] OR ertugliflozin[tiab] OR ipragliflozin[tiab] OR luseogliflozin[tiab] OR tofogliflozin[tiab] OR sotagliflozin[tiab] OR henagliflozin[tiab] OR bexagliflozin[tiab]'
D22 = D16 + ' OR enavogliflozin[tiab] OR ganagliflozin[tiab] OR remogliflozin[tiab] OR sergliflozin[tiab] OR janagliflozin[tiab] OR licogliflozin[tiab]'
WT = '"Body Weight"[Mesh] OR weight[tiab] OR obes*[tiab] OR overweight[tiab]'
AS = '"Asian People"[Mesh] OR "Asia"[Mesh] OR asian*[tiab] OR asia[tiab] OR chinese[tiab] OR china[tiab] OR japanese[tiab] OR japan[tiab] OR korean*[tiab] OR korea[tiab] OR indian[tiab] OR india[tiab] OR taiwan*[tiab] OR thai*[tiab] OR singapore*[tiab] OR malaysia*[tiab] OR vietnam*[tiab] OR indonesia*[tiab] OR philippine*[tiab] OR pakistan*[tiab] OR bangladesh*[tiab]'
ND = '"non-diabetic"[tiab] OR nondiabetic[tiab] OR "non diabetic"[tiab] OR "without diabetes"[tiab] OR "without type 2 diabetes"[tiab] OR "non-diabetes"[tiab] OR "absence of diabetes"[tiab] OR normoglycemic[tiab] OR normoglycaemic[tiab]'
FM = '"Body Composition"[Mesh] OR "Adipose Tissue"[Mesh] OR "Muscle, Skeletal"[Mesh] OR "Sarcopenia"[Mesh] OR fat[tiab] OR muscle*[tiab] OR adipos*[tiab] OR "body composition"[tiab] OR "lean mass"[tiab] OR "lean body mass"[tiab] OR "fat-free mass"[tiab] OR "fat free mass"[tiab] OR sarcopeni*[tiab]'
MECH = '"Glycosuria"[Mesh] OR glycosuria[tiab] OR glucosuria[tiab] OR "urinary glucose"[tiab] OR "Energy Intake"[Mesh] OR "energy intake"[tiab] OR "energy balance"[tiab] OR "energy expenditure"[tiab] OR calori*[tiab]'
WATER = '"Body Water"[Mesh] OR "body water"[tiab] OR "extracellular water"[tiab] OR "extracellular fluid"[tiab] OR "plasma volume"[tiab] OR "fluid volume"[tiab] OR hydration[tiab] OR "Diuresis"[Mesh] OR diuresis[tiab] OR "Natriuresis"[Mesh] OR natriuresis[tiab]'
OFF = '"Off-Label Use"[Mesh] OR "off-label"[tiab] OR "off label"[tiab]'
WADD = '"Body Water"[Mesh] OR "body water"[tiab] OR "total body water"[tiab] OR "extracellular water"[tiab] OR "intracellular water"[tiab] OR "extracellular fluid"[tiab] OR "fluid volume"[tiab] OR "plasma volume"[tiab] OR hydration[tiab] OR "water loss"[tiab] OR "fluid loss"[tiab]'
FMW = FM + ' OR ' + WADD
OA_D = '"SGLT2" OR "SGLT-2" OR "sodium-glucose cotransporter 2" OR "sodium glucose cotransporter 2" OR gliflozin OR gliflozins OR empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR ipragliflozin OR luseogliflozin OR tofogliflozin OR sotagliflozin OR henagliflozin OR bexagliflozin'
OA_FMW = 'fat OR muscle OR muscles OR adipose OR adiposity OR "body composition" OR "lean mass" OR "lean body mass" OR "fat-free mass" OR sarcopenia OR "body water" OR "total body water" OR "extracellular water" OR "intracellular water" OR "extracellular fluid" OR "fluid volume" OR "plasma volume" OR hydration OR "water loss" OR "fluid loss"'
TRIAL = '"Randomized Controlled Trial"[pt] OR "Controlled Clinical Trial"[pt] OR "Clinical Trial"[pt] OR randomized[tiab] OR randomised[tiab] OR randomly[tiab] OR placebo[tiab] OR trial[ti]'
CT6 = 'SGLT2 OR "SGLT-2" OR "sodium-glucose cotransporter 2" OR "sodium glucose cotransporter 2" OR empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR ipragliflozin OR luseogliflozin OR tofogliflozin OR sotagliflozin OR henagliflozin OR bexagliflozin'
OA_ND = '"non-diabetic" OR nondiabetic OR "without diabetes" OR "without type 2 diabetes" OR "absence of diabetes" OR normoglycemic'
OUT = '"Body Composition"[Mesh] OR "Adipose Tissue"[Mesh] OR "Muscle, Skeletal"[Mesh] OR "Sarcopenia"[Mesh] OR "Body Water"[Mesh] OR "Muscle Strength"[Mesh] OR "Physical Functional Performance"[Mesh] OR fat[tiab] OR adipos*[tiab] OR muscle*[tiab] OR muscular[tiab] OR "body composition"[tiab] OR "lean mass"[tiab] OR "lean body mass"[tiab] OR "lean tissue"[tiab] OR "fat-free mass"[tiab] OR "fat free mass"[tiab] OR sarcopeni*[tiab] OR "body water"[tiab] OR "extracellular water"[tiab] OR "intracellular water"[tiab] OR "extracellular fluid"[tiab] OR "fluid volume"[tiab] OR "plasma volume"[tiab] OR hydration[tiab] OR "water loss"[tiab] OR "fluid loss"[tiab] OR "grip strength"[tiab] OR handgrip[tiab] OR "hand grip"[tiab] OR dynamomet*[tiab] OR "physical performance"[tiab] OR "physical function"[tiab] OR "walk test"[tiab] OR "minute walk"[tiab] OR "gait speed"[tiab] OR "walking speed"[tiab] OR "chair stand"[tiab] OR DXA[tiab] OR DEXA[tiab] OR "dual-energy x-ray"[tiab] OR bioimpedance[tiab] OR "bioelectrical impedance"[tiab]'
BW = '"body weight"[tiab] OR "weight loss"[tiab] OR "weight reduction"[tiab] OR "weight change"[tiab]'
DES = '"Randomized Controlled Trial"[pt] OR "Controlled Clinical Trial"[pt] OR "Clinical Trial"[pt] OR randomized[tiab] OR randomised[tiab] OR randomly[tiab] OR placebo[tiab] OR trial[tiab] OR crossover[tiab] OR "cross-over"[tiab] OR "Cohort Studies"[Mesh] OR cohort*[tiab] OR "Observational Study"[pt] OR propensity[tiab] OR retrospective*[tiab] OR prospective*[tiab]'
ANIM = '"Animals"[Mesh] NOT "Humans"[Mesh]'
ND2 = ND + ' OR prediabet*[tiab] OR "pre-diabetes"[tiab] OR "impaired glucose tolerance"[tiab] OR "impaired fasting glucose"[tiab]'
OA_D22 = '"SGLT2" OR "SGLT-2" OR "sodium-glucose cotransporter 2" OR "sodium glucose cotransporter 2" OR "sodium-glucose co-transporter 2" OR gliflozin OR gliflozins OR empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR ipragliflozin OR luseogliflozin OR tofogliflozin OR sotagliflozin OR henagliflozin OR bexagliflozin OR enavogliflozin OR ganagliflozin OR remogliflozin OR sergliflozin OR janagliflozin OR licogliflozin'
OA_OUT = 'fat OR adipose OR adiposity OR muscle OR muscles OR muscular OR "body composition" OR "lean mass" OR "lean body mass" OR "lean tissue" OR "fat-free mass" OR "fat free mass" OR sarcopenia OR "body water" OR "extracellular water" OR "intracellular water" OR "extracellular fluid" OR "fluid volume" OR "plasma volume" OR hydration OR "water loss" OR "fluid loss" OR "grip strength" OR handgrip OR "hand grip" OR "physical performance" OR "physical function" OR "walk test" OR "minute walk" OR "gait speed" OR "walking speed" OR "chair stand" OR DXA OR DEXA OR "dual-energy x-ray" OR bioimpedance OR "bioelectrical impedance"'
OA_DES = 'randomized OR randomised OR randomly OR placebo OR trial OR crossover OR "cross-over" OR cohort OR "observational study" OR propensity OR retrospective OR prospective'
S1 = '((%s) AND (%s) AND (%s)) NOT (%s)' % (D22, OUT, DES, ANIM)
S4 = '((%s) AND (%s OR %s) AND (%s)) NOT (%s)' % (D22, OUT, BW, DES, ANIM)
G6 = '(("scoping review"[ti] OR "scoping reviews"[ti]) AND ("systematic review"[ti] OR "systematic reviews"[ti]) AND (guidance[ti] OR choosing[ti] OR choose[ti] OR difference*[ti] OR "when to"[ti])) OR ("synthesis without meta-analysis"[ti] OR ("few studies"[ti] AND (meta-analy*[ti] OR synthesis[ti]))) OR (("single screening"[ti] OR "single-reviewer"[ti] OR "single reviewer"[ti] OR "single screener"[ti] OR "one reviewer"[ti] OR "dual screening"[ti] OR "double screening"[ti]) AND (screening[ti] OR selection[ti] OR review*[ti]))'
M1 = '("systematic review*"[tiab] OR "scoping review*"[tiab] OR "evidence synthes*"[tiab]) AND ("abstract screening"[tiab] OR "citation screening"[tiab] OR "study selection"[tiab] OR "screening decision*"[tiab] OR "full-text screening"[tiab] OR "title screening"[tiab] OR "eligibility assessment*"[tiab]) AND ("intra-rater"[tiab] OR intrarater[tiab] OR "intra-reviewer"[tiab] OR intrareviewer[tiab] OR "intra-observer"[tiab] OR intraobserver[tiab] OR "test-retest"[tiab] OR rescreen*[tiab] OR "re-screening"[tiab] OR "re-screened"[tiab] OR "same reviewer"[tiab] OR "same reviewers"[tiab] OR "self-consistency"[tiab])'
M2 = '("systematic review*"[ti] OR "scoping review*"[ti] OR "evidence synthes*"[ti] OR "meta-analys*"[ti]) AND (screening[ti] OR "data extraction"[ti] OR "study selection"[ti] OR conduct*[ti] OR production[ti] OR producing[ti] OR complete[ti] OR "risk of bias"[ti]) AND (time[ti] OR hours[ti] OR workload[ti] OR "resource use"[ti] OR resources[ti] OR effort[ti] OR "person-hours"[ti] OR minutes[ti] OR duration[ti])'
M3 = '("risk of bias"[ti] AND (randomised[ti] OR randomized[ti]) AND tool[ti]) OR ("risk of bias"[ti] AND (non-randomised[ti] OR non-randomized[ti] OR nonrandomized[ti] OR observational[ti] OR exposures[ti] OR "follow-up studies"[ti]) AND tool[ti]) OR (GRADE[ti] AND ("quality of evidence"[ti] OR "certainty of evidence"[ti] OR "certainty of the evidence"[ti] OR "rating quality"[ti] OR "rating the quality"[ti])) OR (PRISMA[ti] AND "scoping reviews"[ti]) OR ("PRISMA 2020"[ti])'
R1 = '("ROBINS-I"[tiab] OR "ROBINS I"[tiab] OR "risk of bias in non-randomized studies of interventions"[tiab] OR "risk of bias in non-randomised studies of interventions"[tiab] OR "risk of bias in nonrandomized studies of interventions"[tiab]) AND (minutes[tiab] OR hours[tiab] OR "time to apply"[tiab] OR "time to complete"[tiab] OR "time taken"[tiab] OR "time required"[tiab] OR "time needed"[tiab] OR "time-consuming"[tiab] OR workload[tiab] OR burden[tiab])'
P1 = '("PRISMA-P"[ti] OR ("preferred reporting items"[ti] AND protocols[ti])) OR (("artificial intelligence"[ti] OR AI[ti] OR "large language model*"[ti] OR LLM*[ti] OR generative[ti] OR ChatGPT[ti]) AND ("evidence synthesis"[ti] OR "evidence syntheses"[ti] OR "systematic review*"[ti]) AND (reporting[ti] OR responsible[ti] OR "position statement"[ti] OR guidance[ti] OR recommendation*[ti] OR disclos*[ti] OR transparen*[ti] OR checklist[ti])) OR ("scoping review*"[ti] AND (registration[ti] OR registering[ti] OR registry[ti] OR registries[ti] OR PROSPERO[ti] OR "Open Science Framework"[ti] OR OSF[ti])) OR (PROSPERO[ti])'
KS = 'AND (29235586[pmid] OR 33879970[pmid] OR 42104798[pmid] OR 39361103[pmid])'

SHOWN = [
 ('S2m6 s1', 'L000124', '(%s) AND (%s) AND (%s) AND (%s)' % (D16, WT, AS, ND)),
 ('S2m6 s2', 'L000125', '(%s) AND (%s) AND (%s)' % (D16, FM, ND)),
 ('S2m6 s3', 'L000126', '(%s) AND (%s) AND (%s) AND (%s)' % (D16, FM, AS, ND)),
 ('S2m6 s4', 'L000127', '(%s) AND (%s) AND (%s)' % (D16, MECH, ND)),
 ('S2m6 s5', 'L000128', '(%s) AND (%s) AND (%s)' % (D16, FM, WATER)),
 ('S2m6 s6', 'L000131', '(%s) AND (%s) AND (%s)' % (D16, OFF, WT)),
 ('S2m6 b1', 'L000117', D16), ('S2m6 b2', 'L000118', WT), ('S2m6 b3', 'L000119', AS), ('S2m6 b4', 'L000120', ND),
 ('S2m6 b-focus', 'L000121', FM), ('S2m6 b-mech', 'L000122', MECH), ('S2m6 b-water', 'L000123', WATER), ('S2m6 b-off', 'L000130', OFF),
 ('S2m10 s1', 'L000149', '((%s) AND (%s)) AND systematic[sb]' % (D16, FMW)),
 ('S2m10 s2', 'L000150', '((%s) AND (%s) AND (protocol[ti])) AND systematic[sb]' % (D16, FMW)),
 ('S2m10 s3 (OpenAlex)', 'L000152', '(%s) AND (%s)' % (OA_D, OA_FMW)),
 ('S2m10 b-water', 'L000148', WADD),
 ('S2m22 s1', 'L000192', '(%s) AND (%s) AND (%s) AND (%s)' % (D16, FMW, AS, ND)),
 ('S2m22 s2', 'L000193', '(%s) AND (%s) AND (%s)' % (D16, FMW, ND)),
 ('S2m22 s3', 'L000195', '((%s) AND (%s) AND (%s)) AND (%s)' % (D16, FMW, ND, TRIAL)),
 ('S2m22 b-trial', 'L000194', TRIAL),
 ('S2m22 s4', 'L000199', '(enavogliflozin[tiab] OR ganagliflozin[tiab]) NOT (%s)' % D16),
 ('S2m22 s5', 'L000200', '"without type 2 diabetes"[tiab] AND 33879970[pmid]'),
 ('S2m22 s6 (ctgov)', 'L000198', CT6),
 ('S2m34 s1', 'L000255', '((%s) AND ("Body Weight"[Mesh] OR weight[tiab]) AND (%s)) AND systematic[sb]' % (D16, ND)),
 ('S2m34 s2 (OpenAlex)', 'L000257', '(%s) AND (weight) AND (%s)' % (OA_D, OA_ND)),
 ('S2m34 b1', 'L000254', '"Body Weight"[Mesh] OR weight[tiab]'),
 ('S3m22 s1', 'L000424', S1),
 ('S3m22 s2', 'L000426', '(%s) AND (%s)' % (S1, ND2)),
 ('S3m22 s3 (OpenAlex)', 'L000432', '(%s) AND (%s) AND (%s)' % (OA_D22, OA_OUT, OA_DES)),
 ('S3m22 b1', 'L000420', D22), ('S3m22 b2', 'L000421', OUT), ('S3m22 b3', 'L000422', DES), ('S3m22 b4', 'L000423', ANIM), ('S3m22 b-nd', 'L000425', ND2),
 ('S3m24 known+s1', 'L000443', '(%s) %s' % (S1, KS)),
 ('S3m24 known+s2', 'L000444', '((%s) AND (%s)) %s' % (S1, ND2, KS)),
 ('S3m26 s4', 'L000459', S4),
 ('S3m26 b-bw', 'L000458', BW),
 ('S3m26 known+s4', 'L000460', '(%s) %s' % (S4, KS)),
 ('S3m26 s5 interventions (ctgov)', 'L000468', OA_D22),
 ('S3m26 s5 outcomes (ctgov)', 'L000468:outc', OA_OUT),
 ('S3m38 s6', 'L000574', G6),
 ('S3m38 s6b', 'L000578', '(%s) OR (SWiM[ti] AND (synthesis[ti] OR "meta-analysis"[ti]))' % G6),
 ('S4m8 s1', 'L000615', M1), ('S4m8 s2', 'L000619', M2), ('S4m8 s3', 'L000625', M3),
 ('S4m10 s1', 'L000642', R1), ('S4m12 s1', 'L000661', P1),
 ('protocol item 10', 'L000459', S4),
]

import difflib
for where, lid, shown in SHOWN:
    if lid.endswith(':outc'):
        logged = log[lid.split(':')[0]]['parameters'].get('query.outc')
    else:
        logged = term(lid)
    if logged == shown:
        print('EQUAL   ', where, lid)
    else:
        sm = difflib.SequenceMatcher(None, shown, logged or '')
        diffs = [(t, shown[i1:i2][:80], (logged or '')[j1:j2][:80]) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
        print('DIFFERENT', where, lid, diffs[:4])
