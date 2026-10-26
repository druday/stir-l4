# Search Strategy, version 1

Status: DRAFT, shown to Uday for certification. Written by code from the log (2026-10-25T10:04:30Z); strings and counts are as saved, not retyped.

## 1. PubMed (search 4; run)
Purpose: primary studies for the certified question. Records created 1800/01/01 to 2026/10/25 (Create Date bound checked in the saved query translation); no language, publication-date or population filter.

```
(("Sodium-Glucose Transporter 2 Inhibitors"[Mesh] OR SGLT2*[tiab] OR "SGLT-2"[tiab] OR "sodium-glucose cotransporter 2"[tiab] OR "sodium glucose cotransporter 2"[tiab] OR "sodium-glucose co-transporter 2"[tiab] OR gliflozin*[tiab] OR empagliflozin[tiab] OR dapagliflozin[tiab] OR canagliflozin[tiab] OR ertugliflozin[tiab] OR ipragliflozin[tiab] OR luseogliflozin[tiab] OR tofogliflozin[tiab] OR sotagliflozin[tiab] OR henagliflozin[tiab] OR bexagliflozin[tiab] OR enavogliflozin[tiab] OR ganagliflozin[tiab] OR remogliflozin[tiab] OR sergliflozin[tiab] OR janagliflozin[tiab] OR licogliflozin[tiab]) AND ("Body Composition"[Mesh] OR "Adipose Tissue"[Mesh] OR "Muscle, Skeletal"[Mesh] OR "Sarcopenia"[Mesh] OR "Body Water"[Mesh] OR "Muscle Strength"[Mesh] OR "Physical Functional Performance"[Mesh] OR fat[tiab] OR adipos*[tiab] OR muscle*[tiab] OR muscular[tiab] OR "body composition"[tiab] OR "lean mass"[tiab] OR "lean body mass"[tiab] OR "lean tissue"[tiab] OR "fat-free mass"[tiab] OR "fat free mass"[tiab] OR sarcopeni*[tiab] OR "body water"[tiab] OR "extracellular water"[tiab] OR "intracellular water"[tiab] OR "extracellular fluid"[tiab] OR "fluid volume"[tiab] OR "plasma volume"[tiab] OR hydration[tiab] OR "water loss"[tiab] OR "fluid loss"[tiab] OR "grip strength"[tiab] OR handgrip[tiab] OR "hand grip"[tiab] OR dynamomet*[tiab] OR "physical performance"[tiab] OR "physical function"[tiab] OR "walk test"[tiab] OR "minute walk"[tiab] OR "gait speed"[tiab] OR "walking speed"[tiab] OR "chair stand"[tiab] OR DXA[tiab] OR DEXA[tiab] OR "dual-energy x-ray"[tiab] OR bioimpedance[tiab] OR "bioelectrical impedance"[tiab] OR "body weight"[tiab] OR "weight loss"[tiab] OR "weight reduction"[tiab] OR "weight change"[tiab]) AND ("Randomized Controlled Trial"[pt] OR "Controlled Clinical Trial"[pt] OR "Clinical Trial"[pt] OR randomized[tiab] OR randomised[tiab] OR randomly[tiab] OR placebo[tiab] OR trial[tiab] OR crossover[tiab] OR "cross-over"[tiab] OR "Cohort Studies"[Mesh] OR cohort*[tiab] OR "Observational Study"[pt] OR propensity[tiab] OR retrospective*[tiab] OR prospective*[tiab])) NOT ("Animals"[Mesh] NOT "Humans"[Mesh])
```

Records: 2,026 (L000459, run 2026-10-25). Records not returned by search 1: 1,287 (L000461); records of search 1 lost: 0 (grain: PubMed records).

## 2. ClinicalTrials.gov (search 5; run)
Purpose: registered studies, any status. Data timestamp 2026-10-23T09:00:04 (L000468, run 2026-10-25).

```
Interventions: "SGLT2" OR "SGLT-2" OR "sodium-glucose cotransporter 2" OR "sodium glucose cotransporter 2" OR "sodium-glucose co-transporter 2" OR gliflozin OR gliflozins OR empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR ipragliflozin OR luseogliflozin OR tofogliflozin OR sotagliflozin OR henagliflozin OR bexagliflozin OR enavogliflozin OR ganagliflozin OR remogliflozin OR sergliflozin OR janagliflozin OR licogliflozin
Outcome measures: fat OR adipose OR adiposity OR muscle OR muscles OR muscular OR "body composition" OR "lean mass" OR "lean body mass" OR "lean tissue" OR "fat-free mass" OR "fat free mass" OR sarcopenia OR "body water" OR "extracellular water" OR "intracellular water" OR "extracellular fluid" OR "fluid volume" OR "plasma volume" OR hydration OR "water loss" OR "fluid loss" OR "grip strength" OR handgrip OR "hand grip" OR "physical performance" OR "physical function" OR "walk test" OR "minute walk" OR "gait speed" OR "walking speed" OR "chair stand" OR DXA OR DEXA OR "dual-energy x-ray" OR bioimpedance OR "bioelectrical impedance"
```

Studies: 540 (L000468; grain: registered studies).

## 3. OpenAlex (search 3 in titles and abstracts; planned for the next session)
Not run: refused on 2026-10-25 (L000457). Planned request: works endpoint, filter title_and_abstract.search with the string below, to_publication_date = the run date, corpus core. Search 3 as run (all fields) is in the log; the planned string adds the four body-weight phrases to its parts-of-the-weight block (the assistant's suggestion, to match PubMed search 4). Reading past the first 100 results needs a free OpenAlex access code (none configured).

```
("SGLT2" OR "SGLT-2" OR "sodium-glucose cotransporter 2" OR "sodium glucose cotransporter 2" OR "sodium-glucose co-transporter 2" OR gliflozin OR gliflozins OR empagliflozin OR dapagliflozin OR canagliflozin OR ertugliflozin OR ipragliflozin OR luseogliflozin OR tofogliflozin OR sotagliflozin OR henagliflozin OR bexagliflozin OR enavogliflozin OR ganagliflozin OR remogliflozin OR sergliflozin OR janagliflozin OR licogliflozin) AND (fat OR adipose OR adiposity OR muscle OR muscles OR muscular OR "body composition" OR "lean mass" OR "lean body mass" OR "lean tissue" OR "fat-free mass" OR "fat free mass" OR sarcopenia OR "body water" OR "extracellular water" OR "intracellular water" OR "extracellular fluid" OR "fluid volume" OR "plasma volume" OR hydration OR "water loss" OR "fluid loss" OR "grip strength" OR handgrip OR "hand grip" OR "physical performance" OR "physical function" OR "walk test" OR "minute walk" OR "gait speed" OR "walking speed" OR "chair stand" OR DXA OR DEXA OR "dual-energy x-ray" OR bioimpedance OR "bioelectrical impedance" OR "body weight" OR "weight loss" OR "weight reduction" OR "weight change") AND (randomized OR randomised OR randomly OR placebo OR trial OR crossover OR "cross-over" OR cohort OR "observational study" OR propensity OR retrospective OR prospective)
```

Count: pending (next session).

## 4. WHO trial portal (by Uday, by hand; planned for the next session)
The drug names of search 5 in the portal's intervention field; exact steps prepared at the run. Count: pending: Uday.

## 5. Not searched
Embase and CINAHL: Uday cannot search them (no access); other paid databases are also out of reach. The protocol names Embase and CINAHL as not searched and says why.

## 6. Known studies (confirmed by Uday)

| PMID | Year | Title | Search 4 |
|---|---|---|---|
| 29235586 | 2014 | Exploring glycosuria as a mechanism for weight and fat mass reduction. A pilot study with remogliflozin etabonate and sergliflozin etabonate in healthy obese subjects. | found |
| 33879970 | 2021 | Comparison of dapagliflozin and teneligliptin in nonalcoholic fatty liver disease patients without type 2 diabetes mellitus: a prospective randomized study. | found |
| 42104798 | 2026 | Effects of Empagliflozin and Lifestyle Intervention on Improving Body Weight and Other Metabolic Parameters in Atypical Antipsychotics-treated Patients with Schizophrenia Spectrum Disorders-A Double-blind Randomized Placebo-controlled Trial. | found |
| 39361103 | 2024 | Randomized study of the effects of empagliflozin and topiramate dual therapy on anthropometric and metabolic indices in non-diabetic individuals with overweight/obesity on a calorie-restricted diet. | found |

Check: search 4 AND the four identifiers: 4 of 4 (L000460).

## 7. Stopping rule (DRAFT)
The strings stop changing when every known study Uday confirmed is found and none of the records added by the last change meets the certified question. The records the four body-weight phrases added to PubMed search 4 are screened with the rest at Step 9; if any meets the question, the strings are revisited (a reopening, only if Uday agrees). OpenAlex gets the same known-study check when it is run.

## 8. Peer review (DRAFT)
None: Uday has no second searcher, so the strings are not peer reviewed (no PRESS check); the protocol says so.

