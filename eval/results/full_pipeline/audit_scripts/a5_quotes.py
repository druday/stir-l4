"""Audit 5: every quoted passage in the conversation (S2-S4) must be a substring of a saved text, of the record it is attributed to."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import build, norm

W = sys.argv[1]
C = build(W)

# (where, expected key (or None = any), cited log ids, quote; '…' separates fragments that must appear in order)
Q = [
 ('S2m6#1', 'PMID 40707349', 'L000129', 'are now also recommended for nondiabetic patients with heart failure (HF)'),
 ('S2m6#2', 'PMID 40916713', 'L000129', 'SGLT2i uptake doubled but remained below 40%, with lower adoption in non-diabetic and non-obese patients'),
 ('S2m6#3', 'PMID 41064961', 'L000132', 'have become a viable off-label option for managing obesity'),
 ('S2m6#4', 'PMID 31192057', 'L000129/L000132', 'the early use of canagliflozin (although on an off-label basis) in patients who are at high risk'),
 ('S2m6#5', 'PMID 42730799', 'L000129', 'Glycosuria also creates a chronic negative energy balance, although compensatory hyperphagia limits the degree of weight loss'),
 ('S2m6#6', 'PMID 26861783', 'L000129', 'similar in subjects without diabetes and in those with T2D but quantitatively smaller in the former'),
 ('S2m6#7', 'PMID 33879970', 'L000129', 'With dapagliflozin, body weight decreased, which was related to changes in total body water and body fat mass'),
 ('S2m6#8', 'PMID 29235586', 'L000129', 'There was a reduction in TBW measured by D2O dilution in the RE group that was significantly greater than placebo'),
 ('S2m6#9', 'PMID 28611859', 'L000129', 'Reduction of body fat accounted for more than 70% of the total weight loss and reduction of extracellular water accounted for about 20%'),
 ('S2m6#10', 'PMID 42892668', 'L000129', 'lean-mass estimates do not directly quantify contractile skeletal muscle'),
 ('S2m10#1', 'OA', 'L000152', 'feedback, lower intraglomerular pressure, modest changes in plasma and interstitial fluid volume, improved ventricular loading conditions, metabolic adaptation, and possible effects on inflammation, oxidative stress,'),
 ('S2m10#2', 'PMID 37465122', 'L000084', 'In addition, body water likewise decreased significantly (WMD=-0.96, 95% CI: -1.68 to -0.23, P=0.009).'),
 ('S2m10#3', 'PMID 41748173', 'L000153', 'tubular sodium handling, echocardiography, cardiac output monitoring, arterial stiffness and fluid volume will be extracted.'),
 ('S2m10#4', 'OA', 'L000080', 'Consequently, there are decreases in plasma volume, body weight, and blood pressure.'),
 ('S2m12#1', 'PMID 34897070', 'L000084', 'There were no significant changes in fat mass, blood pressure, low-density lipoprotein cholesterol or high-density lipoprotein cholesterol with SGLT2 inhibitor treatment.'),
 ('S2m12#2', 'PMID 34542222', 'L000084', 'were observed, but not for the changes in waist circumference, fat mass, blood pressure, and lipid profile compared with placebo.'),
 ('S2m12 caseb', None, 'L000084', 'written in Bahasa Indonesia'),
 ('S2m16 g', 'PMID 40707349', 'L000129', 'There is an urgent need for research, especially in nondiabetic, non-Japanese and HF-patients'),
 ('S2m22 check', 'PMID 33879970', 'L000129', 'patients without type 2 diabetes mellitus were enrolled'),
 ('S2m22 NCT#1', 'NCT NCT06095492', 'L000198', 'with the diagnosis of diabetes mellitus (pre-transplantation type 2 diabetes or post-transplantation'),
 ('S2m22 NCT#2', 'NCT NCT07240844', 'L000198', 'Type 1 diabetes mellitus or insulin-dependent diabetes'),
 ('S2m22 NCT#3', 'NCT NCT06448130', 'L000198', 'Previously diagnosed with diabetes ;'),
 ('S2m22 NCT#4', 'NCT NCT06398977', 'L000198', 'Patients with type 1 diabetes mellitus.'),
 ('S2m22 NCT#6', 'NCT NCT06838286', 'L000198', 'Patients with type 2 diabetes who are 19 years of age or'),
 ('S2m22 NCT#7', 'NCT NCT06782139', 'L000198', 'Diabetes : Hemoglobin A1c ≥ 6.5%, or Fasting'),
 ('S2m22 NCT#8', 'NCT NCT07711171', 'L000198', 'duration of diabetes is less than 6 years;'),
 ('S2m30 title#1', 'PMID 34325888', 'L000196', 'Mechanistic Insights of Empagliflozin in Nondiabetic Patients With HFrEF: From the EMPA-TROPISM'),
 ('S2m30 title#2', 'PMID 33357505', 'L000196', 'estimated plasma volume, and measured glomerular filtration rate in patients with heart failure (Empire HF'),
 ('S2m30 title#3', 'PMID 35478433', 'L000196', 'dapagliflozin on volume status and systemic haemodynamics in patients with chronic kidney disease without diabetes:'),
 ('S2m30 HF review', None, 'L000152', 'plasma volume, body weight'),
 ('S2m34 clin', 'PMID 33357505', 'L000196', 'Fluid volume changes might be an important mechanism underlying the beneficial clinical effects'),
 ('S3m2 #1', None, 'L000195', 'dapagliflozin 10 mg once daily plus subcutaneous long-acting exenatide 2 mg once weekly or placebo'),
 ('S3m2 #2', None, 'L000084', 'Primary outcomes were skeletal muscle mass (SMM) and lean mass (LM)'),
 ('S3m2 #3', None, 'L000084', 'No SGLT2 inhibitor significantly reduced SMM compared with placebo'),
 ('S3m2 #4', None, 'L000129', 'insufficient to infer clinically meaningful muscle loss without concurrent assessment of muscle strength'),
 ('S3m2 #5', 'PMID 40707349', 'L000129', 'Physical-performance-tests remained unchanged under SGLT2i'),
 ('S3m2 #6', 'PMID 42892668', 'L000129', 'may be influenced by alterations in body water'),
 ('S3m4 #1', None, 'L000196', '73.5% of participants had prediabetes'),
 ('S3m4 #2', None, 'L000196', 'in addition to optimal medical treatment'),
 ('S3m4 #3', None, 'L000196', 'mostly attributable to adipose tissue reduction without lean tissue change'),
 ('S3m4 #4', None, 'L000196', 'Thirty individuals with T2D and 27 without were randomly assigned'),
 ('S3m4 #5', 'PMID 33357505', 'L000196', 'including 105 (88%) without diabetes'),
 ('S3m6 #1', None, 'L000196', 'an empagliflozin placebo (daily) plus a topiramate placebo'),
 ('S3m6 #2', None, 'L000196', 'exenatide (EQW) and dapagliflozin (DAPA) alone and coadministered'),
 ('S3m8 #1', None, 'L000372', 'reductions in subcutaneous adipose tissue area'),
 ('S3m8 #2', None, 'L000372', 'Empagliflozin Reduces Liver Fat in Individuals With and Without Diabetes'),
 ('S3m12 #1', None, 'L000383', 'Participants were instructed to follow a balanced diet and exercise moderately'),
 ('S3m12 #2', None, 'L000383', 'entered an open-label extension from 24 to 52 weeks during which all participants received active treatment'),
 ('S3m16 #1', 'PMID 33357505', 'L000196', 'Fluid volume changes might be an important mechanism'),
 ('S3m16 #2', 'PMID 35478433', 'L000196', 'did not increase 24-hour sodium and volume excretion'),
 ('S3m16 #3', None, 'L000129', 'provides an energy and osmotic drain that could alter body composition'),
 ('S3m16 #4', 'PMID 42730799', 'L000129', 'compensatory hyperphagia limits the degree of weight loss'),
 ('S3m16 #5', 'PMID 34897070', 'L000394', 'There were no significant changes in fat mass'),
 ('S3m16 #6', 'PMID 40707349', 'L000129', 'decreased in 15 and remained unchanged in 6 studies'),
 ('S3m16 #7', None, 'L000129', 'transiently promotes osmotic diuresis and natriuresis'),
 ('S3m16 #8', 'PMID 29235586', 'L000129', 'a reduction in TBW measured by D2O dilution in the RE group that was significantly greater than placebo'),
 ('S3m16 #9', None, 'L000394', 'muscle strength and physical performance outcomes were rarely reported'),
 ('S3m16 #10', 'PMID 40707349', 'L000129', 'with diabetes-mellitus (68 %) and Japanese (53 %)'),
 ('S3m16 #11', 'PMID 40707349', 'L000129', 'especially in nondiabetic, non-Japanese and HF-patients'),
 ('S3m22 #1', 'PMID 29235586', 'L000196', 'with placebo (n = 12) in obese non-diabetic subjects'),
 ('S3m22 #2', 'PMID 33879970', 'L000129', 'NAFLD patients without type 2 diabetes mellitus were enrolled'),
 ('S3m22 #3', 'PMID 33879970', 'L000129', 'allocated to receive either dapagliflozin (SGLT2i) or teneligliptin (DPP4i) for 12 weeks'),
 ('S3m24 #1', 'PMID 42104798', 'L000441', 'overweight or obese adults with schizophrenia spectrum disorders (non-diabetic or pre-diabetic)'),
 ('S3m24 #2', 'PMC L000445', 'L000445', 'Secondary outcomes included changes in waist circumference'),
 ('S3m24 #3', 'PMC L000445', 'L000445', 'in Hong Kong between November 2023 and April 2024'),
 ('S3m24 #4', 'PMID 39361103', 'L000441', 'had a greater percent change of fat mass and fat percent at week 12'),
 ('S3m32 #1', 'PMID 29235586', 'L000491', 'with placebo (n = 12) in obese non-diabetic subjects'),
 ('S3m32 #2', 'PMID 27550386', 'L000491', 'Of 25 dapagliflozin/exenatide- and 25 placebo-treated participants'),
 ('S3m32 #3', 'PMID 28345814', 'L000491', 'Of the original 25 dapagliflozin + exenatide-treated and 25 placebo-treated participants'),
 ('S3m32 #4', 'PMID 30675708', 'L000491', 'empagliflozin in non-diabetic HF patients … change in the distance in the 6-min walk test'),
 ('S3m32 #5', 'PMID 31218819', 'L000491', 'with or without type 2 diabetes … change from baseline in 6-min walk test distance'),
 ('S3m32 #6', 'PMID 32568464', 'L000491', 'adults with obesity without type 2 diabetes mellitus (T2DM) … magnetic resonance imaging assessment of body fat'),
 ('S3m32 #7', 'PMID 33091173', 'L000491', 'in a virtual population of HF-rEF patients generated by varying model parameters'),
 ('S3m32 #8', 'PMID 33186500', 'L000491', '82 (78.1%) diabetes and 23 (21.9%) prediabetes … 6-minute walk distance'),
 ('S3m32 #9', 'PMID 33197559', 'L000491', 'nondiabetic HFrEF patients (n = 84) were randomized to empagliflozin 10 mg daily or placebo … 6-min walk test'),
 ('S3m32 #10', 'PMID 33351892', 'L000491', 'with and without T2D, were randomized to empagliflozin 10 mg or placebo … 6-minute walk test distance'),
 ('S3m32 HF', None, 'L000491', 'could potentially improve congestion symptoms and exercise capacity in patients with HF'),
 ('S3m34 #11', 'PMID 33357505', 'L000491', 'randomly assigned to empagliflozin or placebo, including 105 (88%) without diabetes'),
 ('S3m34 #13', 'PMID 34097062', 'L000491', 'Nondiabetic women (n = 119 … body composition evaluated by dual-energy x-ray absorptiometry (DXA)'),
 ('S3m34 #14', 'PMID 34897070', 'L000491', 'Randomized controlled trials published in English that compared SGLT2 inhibitors with placebo'),
 ('S3m34 #15', 'PMID 34716213', 'L000491', 'with prediabetes were randomized to receive 25 mg empagliflozin every day or placebo'),
 ('S3m34 #16', 'PMID 35391843', 'L000491', 'placebo-controlled study … in untreated normotensive non-diabetic subjects … suggesting plasma volume contraction'),
 ('S3m34 #17', 'PMID 35478433', 'L000491', 'placebo-controlled double-blind crossover trial (DIAMOND) … markers of volume status in 53 patients with CKD'),
 ('S3m34 #18', 'PMID 36266774', 'L000491', 'Participants (n = 18) with type 2 diabetes (T2D) and class 3 obesity'),
 ('S3m34 #19', 'PMID 37313125', 'L000491', 'We present a case of an elderly male'),
 ('S3m34 #20', 'PMID 37436962', 'L000491', '115 individuals with prediabetes … compared with control (habitual lifestyle)'),
 ('S3m36 #21', 'PMID 38219335', 'L000491', 'in 65 participants with type 2 diabetes and high risk of cardiovascular disease'),
 ('S3m36 #22', 'PMID 38365073', 'L000491', 'but without diabetes or established HF … randomized 1:1 to 180 days treatment with empagliflozin 10 mg daily or placebo'),
 ('S3m36 #24', 'PMID 40994705', 'L000491', 'three identical trials examining patients with T2D with and without CKD and non-diabetic CKD'),
 ('S3m36 #25', 'PMID 41347301', 'L000491', 'Patients at Cardiovascular Risk With or Without Type 2 Diabetes … body fluid composition'),
 ('S3m36 #26', 'PMID 41507062', 'L000491', 'non-diabetic patients with body mass index (BMI) >28kg/m2 and risk of HF … 180-days empagliflozin 10 mg or placebo'),
 ('S3m36 #26 title', 'PMID 41507062', 'L000491', 'the Empire Prevent Metabolic Trial'),
 ('S3m36 substudy', 'PMID 42286641', 'L000545', 'a substudy from the Empire Prevent Metabolic trial'),
 ('S3m38 #1', 'PMID 30453902', 'L000575', 'where the purpose of the review is to identify knowledge gaps, scope a body of literature'),
 ('S3m38 #2', 'PMID 42702311', 'L000575', 'a complementary scoping review run alongside an SR to contextualize sparse evidence'),
 ('S3m38 #3', 'PMID 29504289', 'L000575', 'heterogeneity cannot be reliably estimated if only very few studies are available'),
 ('S3m38 #4', 'PMID 34550585', 'L000575', 'it might be the best solution to refrain from a quantitative meta-analysis'),
 ('S3m38 #5', 'PMID 31948937', 'L000579', 'in which alternative synthesis methods to meta-analysis of effect estimates are used'),
 ('S3m38 #6', 'PMID 31972274', 'L000575', 'single-reviewer abstract screening missed 13% of relevant studies … dual-reviewer abstract screening missed 3%'),
 ('S3m38 #7', 'PMID 31253092', 'L000575', '3% for the 6 experienced reviewers … 13% for the 3 reviewers with less experience'),
 ('S3m38 #8', 'PMID 41942890', 'L000575', 'nonrandomized studies of interventions (NRSI) constituted the highest proportion of false exclusions'),
 ('S3m38 #9', 'PMID 41484785', 'L000575', 'yet empirical evidence comparing their performance is limited'),
 ('S3m38 #3b', 'PMID 29504289', 'L000575', '2-4'),
 ('S4m4 #2', 'PMID 31972274', 'L000575', 'single-reviewer abstract screening missed 13% of relevant studies … dual-reviewer abstract screening missed 3% of relevant studies'),
 ('S4m8 #1', 'PMID 42658745', 'L000627', 'a randomly selected 10% subset re-screened after a 2-week interval to enhance internal consistency'),
 ('S4m8 #2', 'PMID 42805513', 'L000627', 'Compared with two reviewers, the sensitivity of single reviewer full-text screening ranged from 62% to 88%'),
 ('S4m8 #3', 'PMID 32562833', 'L000627', 'IRR was slight for overall judgment … Mean time to apply the tool was 28 minutes (standard deviation 13.4) per study outcome'),
 ('S4m8 #4', 'PMID 37364620', 'L000627', 'Staff resource averaged 358 minutes per study (SD 183)'),
 ('S4m8 #5', 'PMID 31462531', 'L000627', 'RoB 2: a revised tool for assessing risk of bias in randomised trials'),
 ('S4m8 #6', 'PMID 27733354', 'L000627', 'a new tool for evaluating risk of bias … from studies that did not use randomisation'),
 ('S4m8 #7', None, 'L000627', 'randomised controlled trials begin as high certainty evidence and non-randomised studies of interventions (NRSI) as low certainty'),
 ('S4m8 #8', 'PMID 35436525', 'L000627', 'whether or not to pool these bodies-of-evidence requires proper guidance'),
 ('S4m8 #9', 'PMID 30178033', 'L000627', 'The final checklist contains 20 essential reporting items and 2 optional items'),
 ('S4m8 #10', None, 'L000627', 'the PRISMA 2020 27-item checklist'),
 ('S4m10 #1', 'PMID 30981833', 'L000644', 'Mean time to apply the tool was 27.8 minutes (SD 12.6) per study … We found ROBINS-I difficult and demanding'),
 ('S4m10 #2', 'PMID 32987166', 'L000644', 'time taken to apply the tool and reach a consensus … For ROBINS-I … evaluator burden was 48.45 min'),
 ('S4m10 #3', 'PMID 34002466', 'L000644', 'The time in assessing a single study by ROBINS-I varied from 7 hours initially to 3 hours'),
 ('S4m12 #1', 'PMID 25554246', 'L000663', 'PRISMA-P consists of a 17-item checklist intended to facilitate the preparation and reporting of a robust protocol'),
 ('S4m12 #2', 'PMC L000664', 'L000664', 'we encourage reviewers preparing any type of review protocol to make use of PRISMA-P as applicable'),
 ('S4m12 #3', 'PMID 32850123', 'L000663', 'much of the information recommended in PRISMA-P was not stated in PROSPERO registrations'),
 ('S4m12 #4', None, 'L000663', 'Any use of AI or automation that makes or suggests judgements should be fully and transparently reported'),
 ('S4m12 #5', 'PMC L000665', 'L000665', 'Decisions to use AI should be considered and reported as part of protocol development.'),
 ('S4m12 #6', 'PMC L000665', 'L000665', 'The name(s) of the AI system(s), tool(s) or platform(s), version(s), and date(s) used.'),
 ('S4m12 #7', 'PMID 41667957', 'L000663', 'Sharing of prompts and human-validation procedures was insufficient'),
 ('S4m12 #8', 'PMID 22587842', 'L000663', 'inclusion in PROSPERO is restricted to systematic reviews of the effects of interventions … for which there is a health-related outcome'),
 ('S4m12 #9', 'PMID 42310541', 'L000663', 'Most protocols were registered on the Open Science Framework (OSF) (n = 478)'),
 ('S4m14', 'PMC L000664', 'L000667', 'Provide name, institutional affiliation, and e-mail address of all protocol authors'),
 ('S4m16', 'PMC L000665', 'L000665', 'Any financial and non‐financial interests the evidence synthesists have in the AI system or tool'),
 # MeSH scope notes (S2m48)
 ('S2m48 mesh SGLT2', None, 'L000308', 'are used in the treatment of TYPE 2 DIABETES MELLITUS'),
 ('S2m48 mesh Adult', None, 'L000310', 'Adults are of 19 through 44 years of age'),
 ('S2m48 mesh WeightLoss', None, 'L000320', 'Decrease in existing BODY WEIGHT.'),
 ('S2m48 mesh BodyWater', None, 'L000322', 'Fluids composed mainly of water found within the body.'),
 ('S2m48 mesh BodyComp', None, 'L000324', 'The relative amounts of various components in the body'),
 ('S2m48 mesh BodyFat', None, 'L000316', 'Body Fat'),
]


def find(q, key=None):
    frags = [norm(f) for f in q.split('…') if norm(f)]
    hits = []
    items = C.items() if key is None or key == 'OA' else ([(key, C[key])] if key in C else [])
    for k, rec in items:
        if key == 'OA' and rec['src'] != 'openalex':
            continue
        t = rec['text']; pos = 0; ok = True
        for f in frags:
            i = t.find(f, pos)
            if i < 0:
                i2 = t.lower().find(f.lower(), pos)
                if i2 < 0:
                    ok = False; break
                i = i2
            pos = i + len(f)
        if ok:
            hits.append(k)
    return hits

bad = 0
for where, key, cited, q in Q:
    h = find(q, key)
    if key and key not in ('OA',) and key not in C:
        print('NO RECORD', where, key); bad += 1; continue
    if not h:
        anyh = find(q, None)
        print('NOT FOUND', where, key, '| elsewhere:', anyh[:5], '|', q[:90]); bad += 1
    else:
        logs = sorted(set().union(*[C[k]['logs'] for k in h]))
        cited_ok = any(c in logs for c in cited.split('/')) if cited else None
        print('ok', where, h[:4], 'logs:', logs[:6], '' if cited_ok else '  (cited %s not among saved logs of the hit)' % cited)
print('quotes checked:', len(Q), 'not found:', bad)
