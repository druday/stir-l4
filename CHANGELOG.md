# Changelog

## Release 1.0, revised after Prof. Jiang's review (2026-10-26)

Release 1.0 is now development prompt v1.5, kit 1.1.9 and quiz v1.1 (key revised), relabeled; the version shown to
readers stays 1.0. Build: `prompt/build_v1_5.py`, then `release/build_release.py`.

- Planning boundary (section 1 of the prompt and the model file): planning ends when the team certifies the protocol.
  The studies admitted during planning are provisionally included; they test the criteria and the search and show the
  landscape around the topic, including related questions. The final set of included studies is decided when the review
  is carried out. Step 9 and Step 12 ("End of planning") follow; quiz question 15 asks where planning ends and what
  registering the protocol does.
- Section 5: duplicates and reports of one study are matched on the fields of each paper object (study key); counts are
  per study unless another grain is stated; properties are prespecified and verifiable, not "objective"; an empty cell
  or atlas region is a candidate gap; a negative targeted search speaks only for the sources and dates searched;
  earlier RED registrations are kept.
- Credentials appear in the log only as `<redacted:NAME>` placeholders.
- Kit 1.1.9: step 12 renamed; the commitment records a snapshot of the provisionally included studies; redacted
  placeholders.
- Paper V11: Box S1 and Supplementary Files 1 to 5 are this release.

## Release 1.0 (2026-10-25; first build)

Readers see one version: the prompt, quiz, model, core properties and helper kit are all version 1.0
(`release/1.0/`, built by `release/build_release.py`). Release 1.0 is development prompt v1.4, kit 1.1.8 and quiz
v1.1, relabeled; the development history below stays for the authors.

- Prompt v1.4 (`prompt/build_v1_4.py`): references in the protocol are linked (PMID to PubMed, DOI through doi.org);
  the protocol is one document with no version numbers, draft history or notes on what changed (amendments after
  registration go under item 4); certified wording reads on its own, without version labels or the chat's search numbers.
- Kit 1.1.8: `link_refs`, used by `final_report`, links every PMID and DOI; `init` defaults to the current prompt file.
- Example: `docs/example/clean_report.py` prepares the example's report for readers (version labels and draft history
  removed, references linked, the Methodology entry showing the methods as certified); every edit is listed and checked;
  the cover of the example PDF says so. All 73 links in the example PDF were checked to resolve.
- Paper V10: Box S1 and Supplementary Files 1 to 5 are release 1.0; section S2.3 describes the prompt without its
  development history.

## v1.3 (2026-10-25; approved by the first author)

The theory is unchanged (section 1 of the prompt is byte-identical to v1.0). Build: `prompt/build_v1_3.py`. The
calibration quiz stays at v1.1.

Why: the first author asked that every STIR-L4 run end in a general output, a report with the plan as certified and a
proper protocol in a standard template, and that the report not suggest that studies were screened, included or
represented: STIR-L4 in a chat app plans a review.

- Step 11: the protocol is the main output of planning, written in full sentences in short paragraphs, item by item in
  the order of the PRISMA-P 2015 checklist (still the current version; an update is in development), with the
  searches reported as PRISMA-S asks, a reason and a retrieved source for each methodological choice (guidance or
  methods research, never a study that merely used the method), "GAP:" wherever the team has not decided, and three
  added sections: what planning found (pilot screening only as a test of the criteria), how STIR-L4 and AI were used
  (as the 2025 position statement on AI in evidence synthesis and RAISE ask: framework, prompt and kit versions, the
  model as recorded, dates, what the AI did and what people decided and checked), and gaps.
- End of planning: a final report (`k.final_report`), one HTML file holding the plan as certified and then the protocol.
  Paper as an Object, Literature as a Tensor and Registering Evidence Dynamically take one line: building them is not
  available in the prompt version (in development for a dedicated planning tool). Screening counts, the commitment and
  conflicts stay in the log.
- Step 7 and sections 5 and 6: the three representations are designed and certified only; Step 9 no longer asks for
  them to be built.
- Kit 1.1.7: `final_report` (refuses a report whose protocol cites a PMID or DOI that no saved search result holds; a
  small Markdown-to-HTML converter, no new dependency); a registration recorded as "not submitted" no longer shows as
  "registered" or turns later recertifications into amendments; the one-line steps view shows Steps 9, 11 and 12 once
  done.

### Session 5 of the full-pipeline run (`eval/results/full_pipeline/S5_session.json`, `session5/`)

Session 5 ran on the release candidate v1.3-rc1 (kept in `prompt/versions/`) with kit 1.1.7. The assistant wrote the
protocol (version 2) from the saved planning folder; the simulated user asked for three edits before certifying (an
off-topic reference, the nearest evidence from reviews in type 2 diabetes, and the commitment and conflict left to the
log); the assistant made them with new logged searches, and the protocol was certified and the final report built
(`docs/example/final_report/`). Checks after the session: all 38 references exist and match PubMed or Crossref
(36 with a PMID or DOI, plus RAISE through the position statement and the STIR-L4 paper); every number about the six
diabetes reviews matches the live abstracts; all 55 planning-record ids cited exist. v1.3 differs from rc1 by the rules
that came from those edits (pilot screening only as a test; commitments and conflicts in the log; sources must be
guidance or methods research) and by asking for short paragraphs and tables; these were not re-tested in a session.

The complete example (`docs/example/STIR-L4 complete pipeline example.pdf`, 129 pages) now opens with the final report
and then reproduces all five sessions; the journey table, the run's checks and the old protocol appendix were removed.

### Known issues (for v1.3.x)
- The protocol's Methodology entry in the plan quotes the protocol's certification line, because the protocol is
  certified under Methodology.
- The final report is HTML only when the environment has no converter; the browser can print it to PDF.
- Earlier known issues (long search replies, bundled questions) still apply.

## v1.2 (2026-10-25; approved by the first author after the full-pipeline run)

The theory is unchanged (section 1 of the prompt is byte-identical to v1.0). Build: `prompt/build_v1_2.py` (checked
edits on v1.1). The calibration quiz stays at v1.1.

- Step 3: before drafting the case for a review, the assistant appraises whether the question is sound clinically (does
  the population use or need the intervention; does the outcome matter to patients), scientifically (plausible mechanism
  or earlier evidence; can the outcome be measured, and how) and logically (do population, intervention, comparison and
  outcome fit one another and the purpose), as a DRAFT based on logged searches. If the question rests on a mistaken
  assumption it says so and offers ways to reframe it; the team decides.
- Consent split: research content (topic, interests, focus, purpose, terms of the question, certification reasons,
  instructions) is always kept in members' own words, so the plan holds nothing they did not say; consent governs only
  what members say about themselves (motivations, career aims, opinions).
- Keys: the assistant never asks anyone to type a key or password into the chat; a member adds it to the private
  settings file (.env) or as an environment variable. The OpenAlex "free access code" is requested only when a search
  needs more than 100 results or OpenAlex's free daily allowance is used up.
- Steps 9, 11 and 12 are recorded through the kit: the end of pilot screening (`k.step_done`), the registry submission
  or the reason it was not submitted (`k.register(..., status="not submitted")`) and the commitment (`k.commitment`).
- Licences: MIT for code (`LICENSE-CODE`), CC BY 4.0 for the prompt, quiz, model files, documentation and examples
  (`LICENSE-CONTENT`), `CITATION.cff`; the prompt states its licence and asks that the paper be cited. Citation and
  reports of refinements are requests, not licence conditions.
- Kit 1.1.5 to 1.1.6: consent split in the provenance check; Step 9 stays current until the pilot is marked finished;
  Step 12 is reached once a registration (submitted or not) is recorded; the commitment is written to the plan; an
  "early" note clears once that step is certified; MeSH lookups log the total; PubMed book chapters (for example
  StatPearls) are parsed and counted; when OpenAlex's daily allowance is used up the kit stops retrying and says so in
  plain words; search card titles are no longer doubled ("Search 1: Search 1: ..."); `k.init` defaults to prompt v1.2.

### Full-pipeline run (persona P1-full, `eval/personas/P1_full_pipeline.md`; results in `eval/results/full_pipeline/`)

A simulated solo planner continued the SGLT2 inhibitors example from the Step 3 pause to the end, over three more
sessions with the real kit and live PubMed, OpenAlex and ClinicalTrials.gov. All 12 steps were reached: the 8 decisions
and the 3 Step 7 items were certified (16 certifications, 5 reopenings after "broaden"), the search found 4 of 4 known
studies, the planner screened 26 records, committed to 4 studies, certified the protocol and recorded the registration
as not submitted.

| Session | Steps | Interaction score | Fidelity |
|---|---|---|---|
| S2 | 3 to 6 | 100 | pass |
| S3 | 6 to 9 | 92.5 | pass |
| S4 | 10 to 12 | 82.5 | fail (G8: the commitment was recorded while Step 11 stood open; fixed in kit 1.1.6) |

Literature audit (independent agent, live sources): "Genuine, with minor issues". Every identifier exists (3,549 PMIDs,
12 NCT ids, 1 DOI) and traces to a logged query; all 55 combined PubMed counts shown reproduce live; 132 of 134 quoted
passages are word for word in the saved text (the other 2 differ by one space); 50 of 51 search strings equal the
logged term (the other differs by redundant parentheses); the 26 screening decisions are the planner's own. The 15
minor issues (a skipped book chapter, MeSH totals, mild overstatements, one design misread from an abstract) are fixed
in the kit or listed below.

### Known issues (for v1.2.x)
- Search-heavy replies (Steps 3, 8 and 10) still carry several cards and tables; the simulated user skimmed them.
- Several questions in one "Your turn" led to repeated asks in Step 10.
- The case for a review did not surface the nearest evidence from another population (reviews in type 2 diabetes).
- Labels can still overstate a source (for example "lean mass is not muscle" for "does not directly measure muscle").
- A resumed session did not always log the quiz result; the judges vary by about 5 to 10 points between runs.

## v1.1 (2026-10-25; released from v1.1-rc5 after five rounds of simulated conversations)

Interaction layer only; the theory is unchanged (section 1 of the prompt is byte-identical to v1.0).

Why: in the first live test (Codex app, GPT model; `eval/transcripts/2026-10-19_...`), no reply showed the step, the
research focus was never asked for, searches were shown only on request, content was left in files and zips, codes,
log ids and rule numbers cluttered the text, certification took three replies, and "just start" made the assistant
jump ahead unannounced. Diagnosis and design: `docs/design-v1.1/`.

- New section "How to talk with the team": a status line on every reply (step, certified decisions, items waiting,
  research focus), a fixed reply shape (Done, content, To save, Next, Your turn last), a plan map with quick commands,
  plain voice, the research focus carried through the steps, searches shown in full with each concept block explained,
  plain-words certification, a rule for "just start" (work marked Early, nothing skipped), the chat as the reading
  surface (optionally one file beside the chat), batched tool work, and a silent self-check before each reply.
- Step 2 now asks each member which part or question of the topic interests them and why, what they hope to get, and
  what the review should achieve and inform, before any logistics; the agent reflects back only members' words
  ("Added by me: nothing") and the agreed focus names the Team's Purpose. Steps 3, 4 and 6 quote the focus.
- Certification: a listed reviewer may reply "certify" with a reason in their own words; the agent composes the
  CERTIFY line and shows it back; a bare "certify" gets one question for the reason. No reason is ever supplied.
- The workspace and log are created silently at "begin"; the rest of the set-up happens in one reply at the end of
  Step 2. Packaging only at a pause or the end of a session.
- R14 rewritten: no rule or section numbers, no codes or log ids in sentences, technical terms explained.
- New section 3.10 and `kit/stir_l4_kit.py` 1.1.0: the optional helper kit.
- Quiz v1.1: question 16 now tests the intake order and the member-words-only focus.
- New: `eval/metrics.md`, personas, `eval/score_transcript.py`, simulation results.

Refinements from simulated conversations (rc2 and rc3; results in `eval/results/`):
- Replies: prose capped at 180 words; nothing already shown is repeated (a compact recap on request); a reply with
  searches opens with a two- or three-line answer; tables show at most ten rows; one or two one-line examples.
- Status line: "Waiting on you" counts only what this reply asks for, with names; the focus shows "(to confirm)"
  while it awaits confirmation; working ahead reads "Step 2 ... (Step 3 started early)".
- Optional requests (contact email, model name) are asked once, in plain words, with the reason; never file or
  variable names; the plan map also appears when a member asks what comes next.
- Possible reopenings are named only for decisions already certified, in plain words; flow numbers on "why".
- Certification: the line is shown once; the request is worded so the reason cannot echo it.
- Step 2: consent folded into one example reply; "summarized" without quotation marks when exact words are not
  allowed; short glosses for each kind of purpose and motivation; ambiguous answers resolved by one either-or question.
- Step 3: reviews chosen by code over titles and abstracts, with a "Says" passage for each; broader reviews in a
  second table; records not yet examined are counted; the three follow-up questions asked one at a time.
- Kit 1.1.1 to 1.1.2: `reflect_focus`, `search_report` (one Sources line for several searches; compact recap),
  `prepare_strategy` (cards for searches a member runs), `check_reply`, `steps_line`; blocking and optional
  questions; certification requests logged; reason-echo check.
- rc4: a reply that runs searches has a fixed order (lead FACT lines naming source and filter, one sentence on what
  remains open, one card per source including OpenAlex, not-searched line, one table of up to ten rows with "show all");
  each numbered question asks one thing (at most three question marks); optional items only at set-up, on request and
  at the pause; the certification line is shown in every reply that asks for it; the either-or motivation question is
  asked once; counts are quoted with the exact set the code counted; every reported number is computed in the step's
  notebook; review tables quote checked passages and are captioned "FACT, from [n]". Kit 1.1.3: OpenAlex block cards,
  certification of a shown wording without a recorded acceptance, plain set-up glosses, stricter reply check.
- rc5: the plan map is never deferred (a one-line steps view replaces it in search replies or after two maps in a
  row); every search run is shown; Step 3 searches the topic (all concepts with AND) and the focus separately, with a
  "left out on purpose" line; a bare "certify" gets only the reason question; consent covers what members say about
  themselves, while instructions and certification reasons are kept as given; commits never use an identity git guesses.
  Kit 1.1.4: acceptance recorded only for wording already shown; waiting count with items and names; review_table
  with quoted abstract passages.

### Results of the five simulation rounds (interaction score 0-100; fidelity pass or fail)

| Conversation | R1 | R2 | R3 | R4 | R5 (= v1.1) |
|---|---|---|---|---|---|
| First author as solo tester, v1.0 prompt (baseline) | 11.8 fail | | | | |
| First author as solo tester, with kit | 50 fail | 82.5 pass | 82.5 pass | 75 fail | 90 pass |
| Three-member novice team, with kit | 62.5 pass | 75 fail | 75 pass | 65 pass | 100 fail (consent) |
| Solo tester, Sonnet as the assistant | | 70 fail | 77.5 pass | 87.5 pass | 95 pass |
| Solo tester, no helper kit | | | 90 fail | 80 fail | 82.5 pass |

In every v1.1 conversation the simulated users knew which step they were on in every turn (v1.0: 0 of 12).

### Known issues (for v1.1.1)
- Consent and the research focus pull against each other: the focus may hold only members' words, while a member who
  chose summaries should not be quoted. In round 5, short interests were kept word for word under "summarized".
- The Step 3 reply that first shows the searches is still long (several cards and tables) for a terse user.
- Coverage labels can overstate what the code matched (for example a country name matched in an unrelated sentence);
  publication windows are sometimes read as search end dates.
- Example replies under choice questions can favor one option; "Waiting on you" counts are still not always intuitive.
- The judges are strict and vary by about 5-10 points between runs.

## v1.0 (2026-10-19)

The prompt as published with the V9 supplement (Box S1 and Supplementary File 1), after the live-test revision that
asked the topic first and purpose before logistics; quiz with 16 questions (pass 14 of 16 with all critical).
