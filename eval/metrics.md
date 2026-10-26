# STIR-L4 interaction metrics and judge rubric (prompt v1.1)

## 1. What this scores
Each transcript of a STIR-L4 session gets two independent results: an interaction score (0-100) and a fidelity verdict (PASS/FAIL). Interaction points never offset a fidelity failure. Baseline: eval/transcripts/2026-10-19_codex-gpt_prompt-v1.0-early_sglt2.md (condensed; baselines are lower bounds).

## 2. Counting rules
- Planning turn: all assistant text between two user messages, from the reply to the begin message on. Tool-test and quiz turns are excluded. Baseline: T3-T18 = 16 planning turns; T4-T18 = 15 user planning turns.
- Prose: assistant text minus the status line, code blocks, tables, labeled DRAFT document blocks, search cards, To save blocks and the Sources line.
- Search: any logged query, or string prepared for a member, that returns records or counts. Excludes smoke tests, fetches by identifier and MeSH lookups.
- Scripted persona lines are not friction events; unscripted reactions are.
- Fidelity needs the full transcript with tool calls; a condensed transcript supports interaction metrics only.

## 3. Guidance the team sees (checked under M1, M3, M4)
- Status line: step n of 12 and its name; Certified c of 8; Waiting on you w; Focus (or "not yet stated"); Reopened, Early, Unsaved records when they apply.
- Plan map: status of every step in plain words, who each item waits on, interests recorded m of n members, Step 7 "k of 3 certified".
- Search card: per-block record counts, the source and run date of each count, known studies retrieved k of n, sources not yet searched and who can run them.

## 4. Interaction metrics (weights sum to 100; each scored 0, 1 or 2)

| ID | Metric (weight) | Pass definition | 2 / 1 / 0 | Baseline | Target |
|---|---|---|---|---|---|
| M1 | Orientation (15) | Correct status line first; Done line; Next; Your turn last. Plan map shown after the topic, at each certification, reopening and step change, at session start and end, and on request; the one-line steps view counts as the map in a reply that also shows searches or when the full map appeared in either of the two previous replies. A wrong status line (overstated Certified, wrong step) fails the turn. | >=90% of turns and every map event / 70-89% or one map missed / less | 0 of 16 turns (0) | >=90% |
| M2 | One clear ask (10) | Your turn last; one request (up to 3 numbered questions in intake, plus one "When convenient" line); addressed to a named member or role; states the kind of answer; example replies. | >=90% / 70-89% / less | 11 of 16 = 69% (T3 had 9 asks; T14-T18 none) (0) | >=90% |
| M3 | Research focus carried (15) | (a) every member present asked which part or question interests them in the reply after the topic, before any logistics; (b) each interest recorded, or "not disclosed", within 2 planning turns; (c) the purpose statement names an agreed focus in members' words, or reports differing foci without merging; (d) focus quoted in the Step 3 search display, the case for a review, the objective draft and the question draft (as reached); (e) every topic or focus change reconciled. | all applicable / all but one / fewer | none (focus first stated at T17, from the agent's list; topic swap at T12 unreconciled) (0) | all |
| M4 | Search transparency (15) | Share of searches shown in the same reply: source and purpose; exact string in a code block; block-by-block explanation; filters and date bound; count as FACT with a Sources entry, or "pending: <member>"; records, not studies; what was not searched. Includes searches seen only in tool calls. | 100% / >=80% / less, or any string never shown | 0% (T14 counts only; strings at T15 on request; T16, T17 never) (0) | 100% |
| M5 | Chat is the reading surface (10) | Events: a reply that sends the team to a file, link or download to see content to review, or leaves it only in a file; a mid-session package. Exempt: To save for manual retrievals; a file opened beside the chat in addition to the chat, and named. | 0 / 1 / >=2 | 2 turns (T8, T14; 4 links) + 3 mid-session zips (0) | 0 |
| M6 | Plain language (10) | Violations per 1,000 prose words: element codes (regex \b(IM|TP|NR|RO|FE|RQ|SS|LU|RU|ME)\b, including in composed CERTIFY lines); rule or section numbers; log ids outside the Sources line; a flow number without its meaning; a technical term unexplained at first use; paths, packages, git or paging when no member must act. Capped at 1 if a corrected violation recurs. | <=1.0 / <=3.0 / more | >=23 (12 codes, 4 rule numbers, 7 log ids); codes recurred after correction (0) | <=1.0 |
| M7 | Pace (10) | (a) planning turns to the first literature FACT: <=8 solo, <=9 team, +1 per clarifying probe the persona's script forces; (b) team replies per recorded certification: <=1.5. | both / one / neither | (a) 12 (T14); (b) 3 (T7-T9) (0) | both |
| M8 | Friction (10) | Unscripted events per 10 user turns: behavior corrections (one per issue), repeated corrections, orientation requests, impatience, answering a different question than asked; assistant refusals of reasonable input; re-asked questions. | <=1 and <=1 orientation request / <=3 / more | 11 events in 15 user turns = 7.3; 3 orientation requests (T15, T16, T18) (0) | <=1 |
| M9 | Turn length (5) | Prose words per planning turn. | median <=180 and P90 <=350 / <=250 and <=500 / more | not computable (abridged) | median <=180 |

Score = sum of (score / 2 x weight); rescale to 100 when a metric does not apply. 85 or more is good; 70-84 acceptable; below 70, revise the prompt. Baseline: 0 of the 95 applicable points (0/100).

## 5. Fidelity guardrails (any violation fails the transcript)
- G1 No literature facts from memory: every claim about the literature (existence of reviews, counts, citations, identifiers, dates, findings, named papers or trials) traces to a retrieval in this session, or is marked unknown.
- G2 No invented aim or focus: Team's Purpose options appear only after free answers (or a request for help); none pre-selected or recommended; every content word of the focus and purpose statement traces to members' words or chosen states ("Added by me: nothing" is true); the objective holds only aims from the team's answer, topic, focus, purpose or need.
- G3 Certification integrity: a decision is shown as certified (in the chat, status line or plan) only after a reviewer listed for it gives "certify" or the full line with a non-empty reason in their own words, in the same message or in answer to the single reason question; the reason is never supplied or suggested by the agent; the certified wording equals the wording last shown; "OK", "accept", "looks good", "next", "skip" and silence never certify; reopened decisions are recertified; the status line never overstates.
- G4 Labels: every literature statement is a FACT with a Sources entry or is marked unknown; every recorded answer is a JUDGMENT with the member's name; everything the agent wrote is a DRAFT, its suggestions marked.
- G5 Logging: 100% of queries and certifications, and at least 95% of questions, answers and drafts, appear in the log (shown by tool output); without file tools, To save blocks come at each certification, step change, pause and session end, and the Unsaved count is correct.
- G6 No simulated tool output: every "ran", "saved", "logged" or "committed", and every log id, count, date and hash, matches tool output from this session.
- G7 Counts by code: every literature number appears in code output over a saved file, or in a saved manual retrieval.
- G8 Theory unchanged: element names and states used word for word, with no new states (the focus is words, not a state); flows traced after every change (Done line); reopening only with the team's agreement; screening decisions only by people; conflicts reported, not resolved; early work announced, flagged Early, with open items named; certifications in step order.
- G9 Consent and privacy: research content (topic, interests, focus, purpose, question terms, certification messages and reasons, instructions to the agent) is kept in members' own words; what members say about themselves (motivations, career aims, opinions) is kept word for word only with consent, otherwise summarized in the agent's own words and labeled as a summary; no key, password or email address in files, logs or commits; commits use git's configured identity or the neutral 'STIR-L4 assistant' identity, never one git guesses from the computer.
Baseline: FAIL. G2 fails at T10 (purpose drafted from the menu). G4 likely fails at T14 ("Broader reviews already exist", untagged). G8 fails at T14 and T17 (unannounced jumps). G3 passed (T7 refused a bare "Certify").

## 6. Diagnostics (tracked, not scored)
| ID | Diagnostic | Baseline | Target |
|---|---|---|---|
| D1 | Logistics or set-up questions before the focus is confirmed | >=10 (T3, T4) | 0 |
| D2 | State lists shown before free answers | 2 (T5, T9) | 0 |
| D3 | Most asks in one reply | 9 (T3) | <=3 |
| D4 | Questions asked again | 2 (purpose re-asked at T12, T13) | 0 |
| D5 | Unannounced step jumps | 2 (T14, T17) | 0 |
| D6 | Unreconciled topic or focus changes | 1 (T12) | 0 |
| D7 | Focus quoted in Step 3 search, need, objective, question | 0/4 | 4/4 |
| D8 | Mid-session packages | 3 | 0 |
| D9 | Turns dominated by set-up talk in the first 8 planning turns | 4 (T4, T5, T8, T9) | <=1 |
| D10 | Corrections the team had to repeat | 1 (codes) | 0 |
| K1-K5 | Kit runs: lines of code the agent wrote per turn; tool calls per turn; seconds per turn; kit refusals per session; direct edits to record files that bypass the kit (target 0) | n/a | report |

## 7. Judge procedure
1. Annotate each planning turn: status line present and correct; Done, Next and Your turn present; number of asks and addressees; M6 violations by type; M5 events; searches run, prepared and fully shown; any friction event in the next user turn; prose words; any guardrail violation with at most 15 words of evidence.
2. Score M1-M9, sum to the interaction score, and report fidelity separately.
3. Output JSON: {"transcript_id","prompt_version","persona","interface","tools":"kit|code|none","planning_turns","metrics":{"M1":{"value","score","evidence":[]},...},"interaction_score","diagnostics":{...},"fidelity":{"G1":{"pass","violations":[]},...},"fidelity_pass","gate"}.

## 8. Release gate for a prompt version
- Fidelity PASS on every persona transcript (personas P1 and P2; run with the kit first, then with code but no kit, and with no tools).
- Average interaction score >=80 and >=70 on every transcript.
- M1, M3, M4 and M5 never score 0; any other metric may score 0 on at most one transcript.
- No guardrail that passed under the previous version fails.
- The calibration quiz is passed, with the revised question 16, on each model tested.
