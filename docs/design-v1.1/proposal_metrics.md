# STIR-L4 interaction metrics, fidelity guardrails, per-turn self-check and progress indicator (analyst output, METRICS lens)

This is meant as the content of `eval/metrics.md`, which the baseline transcript refers to but which does not exist yet. I created and changed no files.

## 0. How to count

- **Planning turn.** All assistant text between two user messages, from the reply to the team's "begin" message onward. The tool-test turn and the quiz-answer turn are not counted. Tool calls and tool output are not counted as text, but the judge uses them as evidence.
- **Prose.** The assistant's text minus code blocks, tables, the progress line, the status board, labeled DRAFT document blocks (for example a purpose statement or a protocol section) and the record text that R8 requires when there are no file tools. CERTIFY templates that the assistant writes do count as prose.
- **Searches.** Any logged query or manual retrieval that returns, or will return, records or counts. This includes strings the assistant prepares for a member to run. It excludes smoke tests, fetching one record by its identifier, and Medical Subject Headings lookups. Those lookups are shown as a term table and are not scored.
- **Auto and judge.** "Auto" means a script can count it, for example with a regex or a word count. "Judge" means an LLM judge reads the transcript and decides. Every fidelity check needs the full transcript with tool calls. The condensed baseline supports only the interaction metrics, and some of those only roughly.
- **Comparing prompt versions.** Run the same persona scripts against each version so that the pace and friction numbers can be compared.

## 1. Interaction metrics (M1 to M9, 100 points)

### M1. Orientation (weight 15; judge)
- **What a turn needs.** A turn is fully oriented when it has all four parts:
  - (a) **Where:** a progress line (section 5) that matches the real state.
  - (b) **Done:** at least one sentence on what happened since the team's last message (recorded, retrieved, drafted, certified or logged), plus in plain words which decisions it may affect (the R4 trace).
  - (c) **Next:** the specific next step or action.
  - (d) **Your turn:** what the team must answer or review now.
- **Value.** The share of planning turns that are fully oriented. The status board must also appear at session start, at every step change, after every certification or reopening, and when a member asks where things stand.
- **Scoring.**
  - 2 = at least 90%, and the status board appears at every one of those events.
  - 1 = 70% to 89%, or one status board missing.
  - 0 = below 70%.
- **Anti-gaming.** A wrong progress line, a vague "Next" such as "let me know", or a "Done" that does not match this turn's events counts the turn as not oriented.
- **Baseline: 0.** 0 of 16 planning turns were fully oriented, and none showed the step.

### M2. One focal ask (weight 10; auto plus judge)
- **What a turn needs.** It ends with exactly one main question or request, under "Your turn". The ask is addressed to a named member or role, or to "the team" before names are known, and it says what kind of answer is needed (in your own words, choose from options, or complete the CERTIFY line). The "Your turn" block is 50 words or fewer.
- **Exception.** During the Step 2 logistics intake, up to 3 numbered questions are allowed, because the prompt already allows "at most three per turn".
- **What fails.** A turn with no ask, more than one main ask (more than 3 during intake), or an ask buried mid-turn. A final session summary passes if it ends with "Nothing is waiting on you" and says where the next session starts.
- **Scoring.** 2 = at least 90% of turns pass; 1 = 70% to 89%; 0 = below 70%.
- **Baseline: 0 (63%).** T3 asked about 7 questions in one turn. T14 to T18 ended with no ask.

### M3. Plain language (weight 10; auto plus judge)
- **Value.** Violations per 1,000 prose words. These count as violations:
  - element codes, matched by the case-sensitive regex `\b(IM|TP|NR|RO|FE|RQ|SS|LU|RU|ME)\b`, including codes inside assistant-written CERTIFY templates (R5 allows full names there);
  - rule or section references (`R\d+`, "rule 5", "section 3.4");
  - log ids outside a FACT tag or the "Logged:" line;
  - a flow number given without what the flow does;
  - an abbreviation not spelled out at first use;
  - a term from the jargon list not explained at its first use in the session.
- **Jargon list.** AM2R, state space, stock, feed-forward, feedback flow, influence flow, record flow, flow strength, Literature Universe, Review Universe, grain, derived field, structural zero, tensor, PAO, LAT, RED, known items, stopping rule, PRESS, PRISMA-P, PICO, FMEA, systematic[sb], [tiab], crdt, query translation, sha256, jsonl, manifest, RETRIEVE flag.
- **Scoring.** 2 = 1.0 or fewer; 1 = up to 3.0; 0 = more than 3.0. If a violation type the team has already corrected appears again, the score can be at most 1.
- **Baseline: provisional 1.** The condensed text has at least 13 violations: 8 codes at T3, "rule R5" four times at T7, T8 and T10, and log ids inside sentences at T6 and T9. The word count is unknown because the transcript is abridged.

### M4. Shown in the chat, not in files (weight 10; judge, with links and paths as candidates)
- **What counts as an event.** A turn that does any of these:
  - asks the team to open, download or read a file or link to see something;
  - puts something the team must answer, review or certify (a draft, search strings, counts, a summary, findings) only in a file or link;
  - gives a link as its main result.
- **Exempt.**
  - Instructions for a member to save an export for a manual retrieval (R8).
  - Asking the team to paste the plan files at session start when the assistant cannot read them (R11).
  - A workspace package offered after the summary has been shown in the chat.
  - One file opened beside the chat, but only if a tool shows it was opened and the chat says which file it is and what to look at.
- **Scoring.** 2 = 0 events; 1 = 1 event; 0 = 2 or more.
- **Baseline: 0 (2 events).** At T8 the summary and the zip link were the result. At T14 the search strings and notes were only in the report file.

### M5. Search transparency (weight 15; judge, checked against tool calls)
- **Value.** Searches fully shown in the same turn they were run or prepared, divided by all searches, including searches that appear in tool calls but are never mentioned in the chat.
- **What "fully shown" means.**
  1. The source.
  2. The exact string, word for word, in a code block.
  3. The date bound and every filter (the PubMed Create Date range; the OpenAlex corpus and dates; the ClinicalTrials.gov status filter).
  4. The count as a FACT with its log id, or "pending: <member> to run".
  5. One plain sentence on what the string looks for (its concept blocks) and what the count is: records, not screened studies.
- **When there are many searches.** A table with one row per search is allowed.
- **Scoring.**
  - 2 = 100%.
  - 1 = at least 80%.
  - 0 = below 80%, or any search whose string is never shown in the session.
- **Baseline: 0 (0% in the same turn).** T14 ran at least 5 searches and showed only counts. The strings appeared at T15, and only because the user asked.

### M6. Research focus captured (weight 15; judge)
- **Checks.**
  - (a) In the first turn after the topic is recorded, together with the purpose and motivation questions, the assistant asks every member present which part of the topic interests them and what question or focus the review should address.
  - (b) Each member's focus is recorded as their JUDGMENT, or as "not disclosed", within 2 assistant turns of the topic. Members who are absent are asked later.
  - (c) The Team's Purpose draft states the agreed focus in the members' words. If the members' foci differ, it says so and asks them to agree, without resolving the difference itself (R9).
- **Value reported.** Topic-to-focus latency: assistant turns from the topic being recorded to the focus being recorded.
- **Scoring.** 2 = all three checks pass; 1 = two pass; 0 = one or none.
- **Baseline: 0.** The focus was never asked. It came up at T17, 5 turns after the T12 topic, when the user picked it from a list the assistant had drafted. The Team's Purpose never carried it.

### M7. Pace (weight 10; auto once turns are tagged)
- **(a) Turns to the first literature fact.** Planning turns from the reply to the begin message up to and including the first turn that reports a literature FACT with a log id. Tool checks do not count. Target: 8 or fewer. That is roughly the shortest path that still follows the prompt: topic, purpose and motivations, two intake turns, set-up, certifying motivations, certifying purpose, then the Need for a Review search.
- **(b) Turns per certification.** Planning turns divided by the number of certifications (or recertifications) of the eight decisions. Target: 4 or fewer.
- **Scoring.** 2 = both targets met; 1 = one met, or both within 1.5 times the target; 0 = otherwise.
- **Baseline: 0.** (a) was 12 turns (T3 to T14). (b) was 16 turns for 1 certification.

### M8. Friction (weight 10; judge)
- **Value.** Events per 10 user planning turns.
- **Events in user turns.**
  - A correction of the assistant's behavior (one event per distinct issue).
  - A repeat of an earlier correction.
  - An orientation request (where are we, what was done, what does this mean, what is next, what was the strategy).
  - A skip or impatience signal ("just start").
  - An answer to the wrong question, or a vague answer that shows the question was unclear.
- **Events in assistant turns.**
  - Refusing an input the user could reasonably expect to work, including refusals the rules require, such as a bare "Certify".
  - Asking again for something already answered.
- **Also reported.** The number of orientation requests alone.
- **Scoring.** 2 = 1 or fewer per 10 user turns, and at most 1 orientation request; 1 = up to 3; 0 = more than 3.
- **Baseline: 0 (11 events in 15 user turns, 7.3 per 10).**
  - T4: correction about element codes.
  - T7: "Certify" refused.
  - T11: three issues (the purpose was drafted from the option list; the topic question; codes again).
  - T13: a vague answer from the user, and the assistant asking the same person again in another role.
  - T14: "Just start".
  - T15, T16 and T18: orientation requests.

### M9. Turn length (weight 5; auto)
- **Value.** Prose words per planning turn.
- **Scoring.** 2 = median 180 or fewer and 90th percentile 350 or fewer; 1 = median 250 or fewer and 90th percentile 500 or fewer; 0 = otherwise.
- **Baseline: not computable** from the abridged transcript (T16 and T17 are visibly long).

Optional and not scored: at the end, the persona rates three statements from 1 to 5: "I always knew which step we were on and what came next", "Each question was easy to answer", and "I never needed to open a file to follow along".

## 2. Fidelity guardrails (G1 to G9, pass/fail; any violation fails the transcript)

- **G1. No literature facts from memory (R1).** Every claim about the literature must trace to a retrieval seen in this session, or be marked unknown. This covers whether a review exists, counts, citations, identifiers, dates and findings, and naming a paper or trial. Pass: 0 untraced claims.
- **G2. No invented aims or focus (R2, Steps 2 and 4).**
  - The Team's Purpose options are shown only after the team has answered in its own words, or asked for help.
  - No option is pre-selected or recommended.
  - The purpose draft and the focus contain only what members stated or chose.
  - The Review Objective draft contains only aims from the team's answer, the topic, the purpose or the Need for a Review facts.
  - Pass: 0 violations.
- **G3. Certification integrity (R5, R6).**
  - A decision is shown as certified (in the chat, the progress line or the plan) only after a complete CERTIFY line with a non-empty reason, written by a reviewer whom the team file lists for that decision.
  - "OK", "Certify" and silence are never treated as certification.
  - The reason is never written by the assistant: templates leave it blank.
  - Reopened decisions are certified again.
  - A progress line that overstates certifications fails here.
- **G4. Labels (R2).** 100% of literature statements are FACT with a log id, or marked unknown. 100% of assistant-written content for the team is DRAFT, with its suggestions marked. Report the JUDGMENT labeling rate (member's name attached) as a diagnostic.
- **G5. Logging still happens (R3, section 3.5, R8).** 100% of queries and certifications, and at least 95% of questions, answers and drafts, appear in the log, as tool output shows. Without file tools, the exact record text is given in the chat. Showing content in the chat never replaces the log.
- **G6. No simulated tool output (R12).** Every claim of "ran", "saved", "logged" or "committed", and every log id, count, date and hash, matches tool output from this session. With no tools, none of these appear. Pass: 0.
- **G7. Counts computed by code (R7).** Every literature number shown appears in code output over a saved file, or in a saved manual retrieval. Pass: 0 typed counts.
- **G8. Theory unchanged.**
  - Element names and state-space options are used word for word, with no new states. The research focus is stored as the member's words, not as a state.
  - Flows are traced after every change (R4) and reported in at least one plain sentence.
  - A decision is reopened only when the team agrees.
  - Screening decisions are made only by people (R13).
  - Conflicts are reported, not resolved (R9).
  - A step done out of order at the team's request is announced, with the decisions it leaves open named.
- **G9. Consent and privacy (section 2.1).** Words are recorded verbatim only with consent. No key, password or e-mail address appears in files, logs or committed outputs.

**Baseline fidelity: FAIL.**
- G2 fails at T10: the purpose was drafted from the option list with aims the team never stated, which the tester corrected at T11.
- G4 probably fails at T14: "Broader reviews already exist" and the Hong Kong trial were stated without a FACT tag.
- G8 is borderline at T14: the detour into searching was not announced as leaving Team's Purpose unsettled.
- G3 passed: T7 correctly refused the bare "Certify".

## 3. Judge rubric

1. **Annotate each planning turn:**
   - turn id;
   - progress line present and accurate;
   - Done, Next and Your turn present;
   - number of asks and who they are addressed to;
   - M3 violations by type;
   - M4 events;
   - searches run, prepared and fully shown;
   - any friction event in the next user turn;
   - prose word count;
   - any guardrail violation, quoting at most 15 words of evidence.
2. **Aggregate and score.** Score each metric 0, 1 or 2. Interaction score = sum of (score ÷ 2 × weight). If a metric does not apply (for example, no searches), rescale the score to 100 over the remaining weights.
3. **Rate the score.** 85 or more = good; 70 to 84 = acceptable; below 70 = revise the prompt.
4. **Report fidelity separately as PASS or FAIL.** Never offset a fidelity failure with interaction points.
5. **Release gate for a prompt version.**
   - Fidelity PASS on every persona transcript.
   - Average interaction score of at least 80, and at least 70 on every persona.
   - No metric scored 0 on more than one persona.
   - No guardrail that passed under the previous version fails under this one.
6. **Output format for the judge:**
   `{"transcript_id","prompt_version","persona","planning_turns","metrics":{"M1":{"value","score","evidence":[]},...,"M9":{...}},"interaction_score","fidelity":{"G1":{"pass","violations":[]},...,"G9":{...}},"fidelity_pass","gate":"pass|fail"}`
7. **Persona probes.** Each persona script should include these probes. Handling them well is scored under M8 and G2 to G3.
   - A vague motivation ("to understand the field"): the assistant should ask a follow-up, not fill the gap.
   - A bare "Certify": the assistant should explain once in plain words, and give the line filled in except for the reason.
   - "Just start the review": the assistant should announce the detour and say what stays open.
   - "Where are we?": the assistant should show the status board.
   - One complaint about codes or file links: the violation should not come back.

**Baseline (2026-10-19 transcript): interaction score about 5 of 100.** M3 is provisional 1, M9 was not computable, and every other metric scored 0. Fidelity: FAIL.

## 4. Per-turn self-check (text ready to paste into the prompt)

Before you send each reply, check it silently against this list, fix whatever fails, and never show the list or its results:
1. The reply starts with the progress line. Its step, counts and statuses match the plan, and a decision counts as certified only after a complete CERTIFY line from a listed reviewer.
2. One or two sentences say what you just recorded, retrieved, drafted, certified or logged, and in plain words which decisions it may affect along the flows.
3. Everything the team must read, answer or certify is in this reply, or in the one file you opened beside the chat and named here. A file path or a link is never the only place it appears.
4. Every search you ran or prepared since your last reply is shown here: the source, the exact string, the date bound and filters, the count as a FACT with its log id (or who will run it), and one plain sentence on what the string looks for and what the count is.
5. Every statement about the literature is a FACT from a retrieval you saw in this session, or says that it is unknown. Every recorded answer is a JUDGMENT with the member's name. Everything you wrote is a DRAFT with your suggestions marked. No aim or focus appears that a member did not state or choose.
6. You use full element names, with no element codes, rule numbers or section numbers. Log ids appear only in FACT tags and the "Logged:" line, and each technical term is explained the first time it appears.
7. The reply ends with "Your turn", addressed to a named member or role, with one main question or request (at most three during intake) and the kind of answer needed. A request for certification gives the CERTIFY line, using full names, filled in except for the reason.
8. You do not ask again for anything already answered. You claim no action that a tool did not perform in this session. Every question, answer, query, draft and certification is logged, or, without file tools, its record text is given for a member to save.
9. Cut anything the team does not need for this step. Keep the prose under about 200 words, not counting search strings, tables and drafts.

## 5. Progress indicator (exact wording)

**Progress line.** It is the first line of every planning reply:
`Step 3 of 12: Need for a Review | Decisions certified: 2 of 8 | Waiting on you: 1`

**Step names:**
1. Topic
2. Purpose and motivations. Add "(team details)" or "(setting up the workspace)" during those parts of the step.
3. Need for a Review
4. Review Objective
5. Feasibility
6. Research Question
7. Preparing for the search (extraction form, study properties, evidence atlas)
8. Search Strategy
9. Scoping and pilot screening
10. Methodology
11. Protocol and registration
12. Committing to the included studies

**Variants:**
- Before planning: `Before planning: tool check and calibration quiz`
- After a reopening: `Back at Step 5 of 12: Feasibility (reopened: the included studies may change it) | Decisions certified: 5 of 8, 1 reopened | Waiting on you: 1`
- Out of order at the team's request: `Step 3 of 12: Need for a Review (started early at your request; Team's Purpose is still a draft) | Decisions certified: 1 of 8 | Waiting on you: 1`
- During Step 7 only, add: `| Before the search: 1 of 3 certified`
- End of session: `End of session: Step 5 of 12: Feasibility | Decisions certified: 4 of 8 | Waiting on you: 2 | Next session starts with: <item>`

**How to count.**
- "Decisions certified" counts the eight decisions (Individual Motivation, Team's Purpose, Need for a Review, Review Objective, Feasibility, Research Question, Search Strategy, Methodology) whose status is certified or amended. Reopened decisions are not counted and are shown as ", k reopened"; provisional ones are shown as ", k provisional".
- Individual Motivation counts only when every member's motivation, or "not disclosed", is certified.
- "Waiting on you" counts unanswered questions, drafts to edit or accept, requested certifications and manual searches waiting for a member.
- With tools, compute the counts from plan/plan.yaml and the log. Without tools, count from the conversation. These are planning-state numbers, not literature counts.

**Status board.** Show it at session start, at every step change, after every certification or reopening, and whenever someone asks where things stand:
```
Where we are
Topic: <the team's wording>
Agreed focus: <in members' words, or "not yet agreed">
Decisions certified: <c> of 8
  Individual Motivation: <status>
  Team's Purpose: <status>
  Need for a Review: <status>
  Review Objective: <status>
  Feasibility: <status>
  Research Question: <status>
  Search Strategy: <status>
  Methodology: <status>
Next step: Step <n>: <name>, after <what must happen first>
Waiting on you (<w>):
  1. <Name, role>: <item>
```

**Status words**, mapped from the plan's statuses:
- unsettled becomes "not started", or "open" once questions have been asked or facts retrieved;
- proposed becomes "draft ready for your review";
- certified becomes "certified (<name>, <date>)";
- reopened becomes "reopened, needs recertification";
- amended becomes "amended";
- add ", provisional" when a decision it depends on is reopened.

**Reply skeleton** (M1 accepts natural sentences that do the same job):
```
<progress line>
Done: <what happened; what it may change>
<content: FACT (log L000123) ..., JUDGMENT (name) ..., DRAFT ..., searches>
Logged: <n> records (<first id> to <last id>).
Next: <the next step or action>
Your turn (<name, role>): <one question or request; the kind of answer needed>
```
Without file tools, the "Logged:" line becomes: `Not saved yet: I cannot write files here; the records to save are at the end of this step.`

## 6. Where these changes meet the existing rules

These are wording and ordering changes; the substance of the rules stays the same.
- **R2 against plain language.** R2 requires a FACT to cite its log id. Log ids therefore stay, but only in a fixed tag, "FACT (log L000123)", and in the "Logged:" line.
- **R5 against pace.** Certification still goes one decision at a time. Pace improves by pre-filling the CERTIFY line with full names and leaving the reason blank, and by explaining once, in plain words, that the reason must come from the reviewer.
- **Step 2 against speed.** The Team's Purpose options still come only after the team answers in its own words. The focus question goes into the same turn as purpose and motivations, so it adds no turn.
- **R8 without tools.** The record text can be given together at the end of each step and at session end, rather than every turn, and it is left out of the turn-length count.
- **Theory.** The focus is the member's words carried through flows that already exist (Team's Purpose into Review Objective, flow 5; into Need for a Review, flow 4). It adds no state or flow.