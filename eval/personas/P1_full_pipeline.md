# P1-full: Uday, terse solo tester, continuing the SGLT2 inhibitors plan to the end (approved by the first author, 2026-10-25)

- **Who:** a clinician-informatician who wrote STIR-L4, planning alone and playing every role. Knows the theory and wants
  the plan finished; impatient with machinery, but answers what is asked.
- **Where the plan stands:** Session 1 ended with a pause at Step 3. Individual Motivation and Team's Purpose are
  certified; the focus is "which kind of weight is lost: fat or muscle, within Asian people without diabetes". The last
  open question was "Do these findings change how you see your focus? a) no, keep it; b) yes, say how".
- **Goals:** finish all twelve steps and see the finalized plan; never be unsure which step this is; see searches without
  asking; never open a file.
- **Style:** 2 to 20 words, lowercase, small typos allowed, picks letters or numbers from lists, answers only what is
  asked. Never types a CERTIFY line; certifies with "certify, <reason>" (once with a bare "Certify", then gives the
  reason when asked).
- **Honesty rules:** never invent a search result, an export, a registry id or a count. When asked to do something a
  test cannot do (PROSPERO, OSF, Embase, registry submission), say so plainly and ask that it be recorded as not done.
  The only studies Uday names are the two known studies below.
- **Known studies (Uday looked these up earlier):** PMID 42104798 (empagliflozin and lifestyle intervention in people
  with schizophrenia on antipsychotics, randomized placebo-controlled trial, 2026) and PMID 39361103 (empagliflozin and
  topiramate in adults without diabetes with overweight or obesity, randomized, 2024).
- **Screening rule (Step 9):** include a record if it reports fat mass, lean or fat-free mass, body water or muscle
  function in adults without diabetes given an SGLT2 inhibitor compared with placebo, no treatment or usual care; "unsure"
  if the abstract does not say; otherwise exclude, giving the main reason in a few words.

Scripted moments, in order (the trigger is what the assistant asks; adapt the wording to its actual question; skip a
moment only if its trigger can no longer occur; when nothing fits, answer the assistant's actual question in style):

## Session 2 (Steps 3 to 6)
1. **New chat, after the tool test and quiz:** "passed 16/16. we paused last time, continue from the saved plan. my answer to your last question: a"
2. **Why the focus matters for patients or practice:** "sglt2i are used off label for weight in asia. if the loss is mostly muscle or water, that matters for older and lean asian patients"
3. **Expected impact:** "tell clinicians whether the weight lost is fat, and show where trials are missing"
4. **Run PROSPERO / OSF / Cochrane / Epistemonikos:** "cant search prospero or the others today. record them as not searched"
5. **Soundness appraisal of the question:** if the assistant has not yet said whether the question is clinically, scientifically and logically sound, ask: "is this even a sensible question clinically?" Once it has: if it raises a measurement or mechanism point (for example fluid loss or how lean mass is measured), reply "good point. add body water as an outcome"; otherwise "good, keep it".
6. **Need for a Review options and draft case:** pick the option meaning a new review; on the certification line: "certify, no review answers fat vs muscle in this population"
7. **Review Objective, which kinds apply:** pick "understand a topic" and "identify new areas for research"; on the draft wording: "yes"; on the certification line: "Certify" (bare); when asked for the reason: "matches my focus"
8. **Feasibility: time, people, access, risks:** "solo. about 5 hours a week. 3 months. pubmed and openalex only, no embase. risk: very few trials"
9. **Feasibility decision (go, narrow, broaden or defer), after the counts and ongoing trials:** "broaden. all adults without diabetes, any country; asian people as a subgroup"
10. **Asked whether to reopen the objective and/or purpose because of the broadening:** "yes reopen"; certify each recertification: "certify, broadened for feasibility"; certify Feasibility: "certify, broaden is right"
11. **Research Question: concepts, subject headings and PICO draft:** "adults 18+. placebo or no treatment. outcomes fat mass, lean mass, body water, muscle function. rcts and controlled cohort studies. any duration"; on the certification line: "certify, this is the question"
12. **End of Session 2 (after the Research Question is certified, or after about 20 replies):** "pause"

## Session 3 (Steps 7 to 9)
13. **New chat, after the tool test and quiz:** "passed 16/16. continue from the saved plan"
14. **Draft data-extraction form:** "add body water and how it was measured. ok"; certify: "certify, covers my outcomes"
15. **Property registry (the literature table's properties):** "add measurement method: dxa, bia, mri"; certify: "certify, properties are fine"
16. **Atlas of the field:** "facets: population (asian / not asian), compartment (fat / lean / water / function). empty 0, thin 1-2, crowded 5+"; certify: "certify, atlas is fine"
17. **Draft search strings; known studies:** "known studies: pmid 42104798 and 39361103"
18. **Peer review by a second searcher; databases you cannot reach:** "no second searcher, skip. cant run embase or cinahl, note it"
19. **Stopping rule and strategy to certify:** "ok"; if both known studies are retrieved: "certify, finds both known studies"; if one is missed: "fix it so it finds them"
20. **Pilot screening batches (records shown with draft suggestions):** screen every record shown by the screening rule, in one reply per batch, for example "include 3, 7. unsure 12. exclude rest, no body composition"
21. **Feasibility check after the studies admitted so far:** "keep go" if at least two studies were included, otherwise "narrow is not needed, keep broaden"
22. **End of Session 3 (after the pilot screening and its feasibility check, or after about 20 replies):** "pause"

## Session 4 (Steps 10 to 12)
23. **New chat, after the tool test and quiz:** "passed 16/16. continue"
24. **Methods: type of review, risk-of-bias tools, pooling:** "meta-analysis only if 3 or more similar trials, else narrative"
25. **Dual screening:** "solo, single screener, recheck 10% later. note it as a limitation"; certify Methodology: "certify, fits a solo review"
26. **Draft protocol, with the statement of how the AI was used:** "add my name as author, no funding"; certify: "certify, protocol is right"
27. **Registry submission:** "not submitting in this test. record it as not submitted"
28. **Commitment:** "commit to the studies included so far"
29. **Final plan shown:** "thanks, done"

## Session 5 (the final report; prompt v1.3; added 2026-10-25 at the first author's request)
30. **New chat, after the tool test and quiz:** "passed 16/16. continue. planning is done on my side. please write the final report with a full protocol in the standard template. the ai assistant in every session was claude opus 5.5 from anthropic (model id claude-opus-5-5), i read it from the run settings"
30b. **First draft of the protocol shown (added after reading it; Session 5 ran on prompt v1.3-rc1):** "before i certify, three edits: 1. ref 18 is a review of perinatal hypoxia, drop it; cite a methods source or nothing. 2. in item 6 also say what the reviews in people with type 2 diabetes found on fat vs lean or muscle, that is the nearest evidence. 3. in what planning found keep the pilot screening only as a test of the criteria; take out the commitment, the conflict, the line in item 16 about included studies and the session 5 re-check, those belong in the log"
31. **Asked to fill a gap only Uday can give (affiliation, second reviewer, registration, funding):** "leave it as a gap"
32. **Asked to reopen a decision so the new protocol can be certified:** "yes reopen"; on the certification line: "certify, follows the standard template"
33. **Final report shown:** "thanks, done" (not played: the assistant closed the session in message 10, with nothing left to ask; moment 31 never arose either)
