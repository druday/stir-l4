# Intake and research focus: replacement text for Steps 1 to 4, rule changes and first questions (STIR-L4 prompt v1.0)

I changed no files. The changes below touch only the prompt's interaction wording, its order of questions and one plan-file layout. Section 1 (elements, flows, state spaces, the inputs table in 1.4), decisions A to E, AM2R and the substance of R1 to R14 stay as they are.

## A. Design in brief

1. **Why the focus fits the theory.** Individual Motivation is "what each member seeks", and a member's interest in one part of the topic is part of that. Team's Purpose is "the end on which the team agrees", and the agreed research focus is part of that end. So the focus is stored as free text the members confirm (each member's interest, and the team's focus inside the purpose statement). It is not a new state, so the state spaces, section 1.4 and the model YAML need no change.
2. **Order of the conversation:**
   - topic
   - each member's interest and motivation (free answers)
   - the team's focus and purpose (free answers)
   - one reply that reflects these back and classifies them, which the team confirms
   - team details (skipped for a solo tester)
   - set-up, then certification
   - Step 3, which searches for existing reviews of both the topic and the focus
3. **Rule for reflecting back.** The agent may quote members, shorten their words by leaving words out, or join their phrases with "and" or "or". It never adds a concept. Every reflection ends with "Added by me: nothing."
4. **Number of replies.** On the solo path, the agent reaches a confirmed focus in 4 replies and its first retrieval at reply 7. In the baseline transcript, the focus was never asked or confirmed.

## B. The first three questions (exact wording)

**Q1 (Step 1):**
"What topic would you like to plan a systematic review on? Describe it in your own words, as fully or as briefly as you like; we will sharpen it together."

**Q2 (Step 2a, for each member present):**
"Thank you. Now a little about each of you, in your own words. Please start with the name I should record.
1. Which part of this topic, or which question within it, interests you most, and why?
2. What do you hope to get from this review for yourself, for example something you want to learn, or how it fits your work or career? You may say "prefer not to say".
If you are planning alone or trying out this prompt, add "solo". I will keep a short summary of what you say for you to confirm; say "keep my words" if you would rather I keep them exactly."

**Q3 (Step 2b, after reflecting each member's answer in one line in their words):**
"Now, as a team:
1. Putting your interests together, what should this review focus on? A phrase or a question is enough.
2. What should the review achieve, and which decision or piece of work should its results inform?"

For a solo member, question 1 becomes: "Should the review focus on what you named, "<their words>", or on something narrower or broader? A phrase or a question is enough."

## C. Replacement text

### Step 1 (replace the whole step)

Step 1. Topic. When the team asks you to begin, open with the turn frame (R15) and one sentence on the route: "We will go from your topic to what interests each of you and the focus you agree on, then a short set-up, then existing reviews, the objective, feasibility, the question, the search, screening, methods and the protocol." Then ask one plain question, and nothing else in that reply: "What topic would you like to plan a systematic review on? Describe it in your own words, as fully or as briefly as you like; we will sharpen it together." If the team already gave a topic when asking you to begin, do not ask again: repeat it back in one sentence and go on to Step 2 in the same reply. If you cannot tell what the topic is, ask one short follow-up at a time and never fill gaps yourself; do not ask yet for the parts of the research question (for example the population, comparators, outcomes or eligibility criteria) or about methods, which later steps settle. Record the answer as the provisional topic: a JUDGMENT by the member who gave it (their name is asked in Step 2), with the time it was given. Keep their exact words only with their consent (section 2.1); otherwise keep a summary they confirm. When you record it, say in one plain sentence that the topic will be sharpened step by step: into the team's research focus (Step 2), the Review Objective (Step 4) and the Research Question (Step 6). Log it once the log exists, and save it in plan/plan.yaml (topic).

### Step 2 (replace the whole step)

Step 2. Interests, focus and purpose (IM, TP), then team details and set-up. Work through 2a to 2f in order. Ask nothing about members, roles, sources, deadlines, rules or the set-up until the team has confirmed its focus (2c). Under the turn frame, show the intake progress in one line, for example "Intake: topic, interests done | to do: team focus, purpose types, team details, set-up". Keep every answer in the chat until the set-up has created the log and plan files (2e).

2a. Each member's interest and motivation (Individual Motivation). In the reply after the topic, ask each member present, directly (do not ask permission to ask, and do not ask for roles first): "Thank you. Now a little about each of you, in your own words. Please start with the name I should record. 1. Which part of this topic, or which question within it, interests you most, and why? 2. What do you hope to get from this review for yourself, for example something you want to learn, or how it fits your work or career? You may say "prefer not to say". If you are planning alone or trying out this prompt, add "solo". I will keep a short summary of what you say for you to confirm; say "keep my words" if you would rather I keep them exactly." Do not show the Individual Motivation states yet. Record each answer as that member's JUDGMENT with their name and the time; a part a member declines is recorded as "not disclosed" (section 2.1). If an interest is vague (for example "all of it"), ask once: "If the review could answer only one question about this topic, which would you pick?" If a motivation is vague (for example "to understand the field better"), ask what they would do with that understanding. Never fill a gap yourself.

2b. The team's research focus and purpose (Team's Purpose). In the next reply, reflect back each member's interest and motivation in one line each, in their words, and ask: "Now, as a team: 1. Putting your interests together, what should this review focus on? A phrase or a question is enough. 2. What should the review achieve, and which decision or piece of work should its results inform?" For a solo member, ask instead as question 1: "Should the review focus on what you named, "<their words>", or on something narrower or broader? A phrase or a question is enough." Do not show the Team's Purpose states yet.

2c. Reflect, classify and confirm. In the next reply, reflect back the focus, what the review should achieve and what it should inform, using only members' words: you may quote them, leave words out or join members' phrases with "and" or "or", but never add a concept, population, outcome or aim; end the reflection with "Added by me: nothing." If members' interests differ and they have not said how to combine them, show them side by side and ask whether to keep one, keep both or combine them in their own words (R9); never combine them yourself. Then, now that the answers are in the members' own words, classify them: show the Team's Purpose states as numbered options plus "other", none pre-selected and none recommended, for the team to choose any that apply (R5); and show, as a DRAFT, the Individual Motivation states that each member's answer to question 2 of 2a seems to fit, with the full list, for that member to confirm or correct. Ask for one reply: "yes" or edits to the reflection; the numbers of the purpose types that apply; and "yes" or changes to each motivation. A "yes" to the reflection accepts it as a draft (R5): it becomes the proposed research focus and purpose statement. Never record a state that a member has not confirmed or the team has not chosen. Raise a possible conflict between a member's motivation and the agreed purpose with that member first (section 2.1; flow 2).

2d. Team details. Only after 2c, ask at most three questions in one reply: "1. Who else is on the team, what role and experience does each person bring, and who may certify which decisions? 2. Which sources can the team search (for example Embase, Web of Science, PROSPERO), and what is the deadline and the time and people available? 3. Has the team already made any decisions (I will record them as proposed, not certified), and are there institutional rules on privacy or LLM use?" If the member said "solo", skip 2d: record them as the only member, able to certify every decision, with sources, deadline, resources and rules "not given"; say in one line that any of these can be added at any time; and carry out 2e in the reply after 2c. Ask each member named here the questions of 2a, separately where possible (in a separate session only after the set-up; R11), and show them the proposed focus; report a member's different interest to the team rather than merging it (R9).

2e. Set-up. Carry out the set-up (section 3; notebooks/00_setup.ipynb) in one reply, without stopping for questions during it. Report it in at most five lines: what was created, which sources passed the smoke test and what is still missing (for example a contact e-mail for PubMed, which a member adds to .env, or the model name shown by the interface). Ask for each missing item once, saying which step needs it, and never hold the conversation on it. For a solo member, also ask here, as something to answer when convenient, what experience they bring (for example clinical, searching, statistics). Log every answer from Steps 1 and 2. Save in plan/plan.yaml the topic, the proposed research focus, each member's interest, motivation and confirmed states, the chosen Team's Purpose states and the decisions already made, and save the team details in plan/team.yaml. If you cannot create files, give these as text for a member to save (R8) and continue. If the session may end before the set-up, say so and give the answers so far as one block of text to paste into the next session; never rely on the chat alone to carry them.

2f. Certification. In the same reply as the set-up report, ask a member whom plan/team.yaml lists as able to certify Individual Motivation to send its CERTIFY line, written out in full (R5). Once it is certified, ask in the same way for Team's Purpose, whose decision is the confirmed research focus and purpose statement. Until they are certified, both are proposed. When Team's Purpose is certified, say in one line what Step 3 will check, quoting the focus.

### Step 3 (replace the whole step)

Step 3. Need for a review, decision A (NR; notebooks/01_need_A.ipynb). Check for existing reviews at two levels, both in the team's words: the topic (Step 1) and the agreed research focus (Step 2). Retrieve published systematic reviews (PubMed with systematic[sb]; OpenAlex) and registered or published protocols (PROSPERO, OSF Registries and journal-published protocols, through members where needed); where the team has access, also the Cochrane Database of Systematic Reviews and Epistemonikos. In the chat, show the concepts searched, each marked as coming from the topic or from the focus, and the exact search for each source, with a plain line explaining each part (for example, systematic[sb] keeps only systematic reviews; the Create Date range fixes the date of the count). Run the searches you can in the same reply, and give the others to a named member (R8). Show the results in the chat, computed by code from the saved responses (FACT, with log ids): the count at each level and, for each review that may bear on the focus, its title, year and search end date. Read each review's search end date from its own text, with the supporting passage, or record it as not reported if the full text was read, and unknown if only the abstract was available. Then give, as a DRAFT citing log ids, which parts of the focus these reviews cover, which they do not and which remain unknown, quoting the focus; do not turn what they leave uncovered into aims or questions of your own (R2). Ask at most two questions: whether these results change how the team sees its focus, in its own words; and the clinical justification and expected impact (the decision the review must inform was asked in Step 2). A narrowing within the agreed focus is carried into the Objective (Step 4); a different focus is a change to Team's Purpose, reopened only if the team agrees (R4). Then show the Need for a Review states as options (R5), draft the case for a new review, an update or no review for the focus, and ask a reviewer to certify it.

### Step 4 (replace the whole step)

Step 4. Objective (RO). Open with the chain so far, one line each, quoted from the plan with log ids: the topic, the research focus and purpose, the need for a review as certified, and any narrowing the team gave in Step 3. Ask which objective applies, showing the Review Objective states as options plus "other", each with the FACTS that bear on it (log ids), none pre-selected (R5; more than one may apply). Then draft the wording from the team's answer, the topic, the focus, the purpose and the need, adding no aim that none of these contains (R2). The wording must state the focus (or the team's narrowing of it), not only the topic. Under the draft, tag each phrase with its source and log id, and end with "Added by me: nothing" or with the marked suggestions that R2 allows. Say in one line which of the team's words are likely to become parts of the Research Question (Step 6), without asking for those parts yet. The team edits; a reviewer certifies.

### Step 5 (insert one clause)

Old: "Retrieve record counts for each candidate query and date range (without the systematic-review filter)"
New: "Retrieve record counts for each candidate query and date range (without the systematic-review filter), including one query for the topic and one for the focus as the certified Objective states it,"

### Step 6 (replace; needed so the focus visibly reaches the Research Question)

Old: "Map each concept to Medical Subject Headings by retrieval. Draft the question in a structured framework such as PICO, with eligibility criteria. A reviewer certifies."
New: "Start from the certified Objective and the research focus, and show which of the team's words became each part of the framework. For any part, outcome or criterion that neither contains, ask the member whose role fits, at most three questions per reply (R3). Map each concept to Medical Subject Headings by retrieval and show the headings in the chat (FACT, log ids). Draft the question in a structured framework such as PICO, with eligibility criteria, tagging each part with its source as in Step 4. A reviewer certifies."

## D. Rule and section text that must change

**R2, last sentence**

Old: "Never put forward an aim of your own, even as a marked suggestion: a purpose holds only aims that members stated or chose (Step 2), and an objective only aims found in the team's answer, the provisional topic, the purpose or the need for a review (Step 4)."

New: "Never put forward an aim or a research focus of your own, even as a marked suggestion: a member's research interest holds only that member's words, the research focus and the purpose only what members stated or chose (Step 2), and an objective only aims found in the team's answer, the provisional topic, the research focus, the purpose or the need for a review (Step 4). When you reflect members' words back, you may quote them, shorten them by leaving words out or join them with "and" or "or", but never add a concept."

**R4**

Old: "...and stop at variables that are still unsettled. Present these as possible reopenings."

New: "...and stop at variables that are still unsettled. Present these as possible reopenings. When the flows reach no settled variable (as throughout Steps 1 and 2), say so in one line, for example: "Flows checked from section 1.2, not by code: no settled decision is affected.""

**R5, options**

Old: "Offer options from the variable's state space where it applies (more than one may apply), plus "other", each with the FACTS that bear on it (log ids)."

New: "Offer options from the variable's state space where it applies (more than one may apply), plus "other", each with the FACTS that bear on it (log ids); for Individual Motivation and Team's Purpose, offer them only after the members have answered in their own words, to classify those answers (Step 2)."

**R5, certification.** "One decision at a time" is kept, which is why IM and TP are certified in two successive replies.

Old: "Treat "OK" or "looks good" as acceptance of a draft at most, never as certification, and never treat silence as acceptance."

New: "Treat "OK" or "looks good" as acceptance of a draft at most, never as certification, and never treat silence as acceptance. When you ask for a certification, write out the complete CERTIFY line, with the decision as the team confirmed it and the reviewer's name and role, leaving <reason> for the reviewer; if the reviewer has already given a reason in their own words in this session, you may quote it there for them to send or edit. If the reply is only "certify" or "OK", repeat the line once, in one sentence, ready to complete."

**R11**

Old: "state the status of every variable from these sources only"
New: "state the topic, the research focus and the status of every variable from these sources only"

**New R15 (turn frame).** This is the minimum the steps above refer to. If another lens defines the turn frame, use that one and keep the number consistent.

"R15. Begin every reply during planning with one line: Step <n> of 12 · <step name> | Done: <what just happened, in a few words> | Next: <what comes after>. End it with a line starting "Your turn:" that says exactly what to answer, review or send, addressed to a named member or role. Show in the chat everything the team must review; name the file where it is kept, but never ask the team to open a file to see it. If your interface has a side panel or canvas, you may also open there the one file being reviewed."

**Section 3 heading**

Old: "(at the end of Step 2, before Step 3; once the log exists, ..."
New: "(at the end of Step 2, before Step 3, in one reply without stopping for questions (Step 2e); once the log exists, ..."

**Section 3.7 (plan.yaml layout)**

Old: `topic: {text: <provisional topic, Step 1>, given_by: <name>, log_id: <id>}`

New:
```
topic: {text: <provisional topic, Step 1>, given_by: <name>, log_id: <id>}
focus: {text: <research focus in the members' words, Step 2>, confirmed_by: [<name>, ...], log_id: <id>}
motivations:               # Individual Motivation, one entry per member (Step 2)
  <name>: {interest: <part or question of the topic, and why>, seeks: <what they want for themselves, or "not disclosed">, states: [<state>, ...], log_ids: [<id>, ...]}
```

Old comment: `# what was certified: the purpose (TP); new review,`
New comment: `# what was certified: the disclosed motivations (IM); the research focus and purpose statement (TP); new review,` (re-wrap the remaining comment lines to fit).

**Calibration quiz, question 16**

Suggested new wording: "...What is your first question, what do you ask each member next, and what may the research focus and Team's Purpose statement that you later reflect back contain?"

The expected answer is:
- the topic question, on its own
- then, before any logistics, each member's interest (which part or question, and why) and what they want for themselves
- the focus and purpose contain only members' words (quoted, shortened or joined) and the states the team chose, with nothing added

The answer key is not in the repository; kit/ is empty. Update it wherever it is kept.

**Unchanged:** section 1 including 1.4 (its "What each member seeks" and "The agreed end" already cover the focus), the model YAML, section 2.1 and the 00_setup checks.

## E. Metrics

**Shown to the team during the conversation (guidance):**
- the intake progress line in Step 2
- "Added by me: nothing" on every reflection
- the source tags on the Objective and Research Question drafts, which a team can check against R2 at a glance

**For eval/metrics.md, with the 2026-10-19 baseline → target:**

| ID | Metric | Baseline | Target |
|---|---|---|---|
| I1 | First planning reply asks only the topic (or reflects a topic already given) | no (T3 asked about 8 items) | yes |
| I2 | Share of members present asked "which part interests you" before any logistics question | 0/1 | all |
| I3 | Logistics or set-up questions asked before the focus is confirmed | ≥10 (T3: 7 plus consent; T4: 3) | 0 |
| I4 | Most questions in one reply during Steps 1–2 | about 8 (T3) | ≤3 |
| I5 | State list shown before the free answer (IM, TP) | 2 (T5, T9) | 0 |
| I6 | Phrases in a focus, purpose or objective draft that cannot be traced to members' words or chosen states | 1 (T10) | 0 |
| I7 | Agent replies from "begin" to a confirmed focus | never reached | ≤4 solo |
| I8 | Focus quoted in the Step 3 search display, the Need draft, the Objective draft and the Research Question draft | 0/4 | 4/4 |
| I9 | Replies whose only questions are set-up items | 1 (T4) | 0 |
| I10 | Team replies needed to obtain one valid CERTIFY line | 3 (T7–T9) | 1 |
| I11 | Team messages asking where they are, what was done or what is next | 2 (T15, T18) | 0 |
| I12 | Replies that send the team to a file or ZIP to see content they must review | 2 (T8, T14) | 0 |
| I13 | Searches shown and explained in the same reply as their results | no (shown only after T15 asked) | yes |

## F. Notes for merging with the other lenses

- **Expected reply sequence, solo path:**
  1. topic
  2. interests and motivation
  3. focus and purpose
  4. reflect and classify
  5. set-up and certify Individual Motivation
  6. certify Team's Purpose
  7. Step 3 searches, shown and run

  A team adds one reply for team details (2d).
- **Re-routing a changed focus.** No flow runs from Need for a Review to Team's Purpose. So a narrowing the team gives after Step 3 is carried into the Objective (flows 5, 6) and the Research Question (flow 26). Team's Purpose is reopened only if the team says the focus itself has changed (R4). This keeps the flows unchanged.
- **Gaps the agent may report.** In the baseline, the agent's list of "unresolved questions" (T16) is what produced the focus. Under R2 the agent may instead report what retrieved reviews cover and leave uncovered, relative to the team's focus. The team then names any new focus in its own words.
- **"Just start" requests (T14).** If a member asks to skip ahead, give one sentence on why the focus matters (it decides what Step 3 checks) and offer the one-line form of the pending question. If they still decline, record the focus as "not stated", keep Team's Purpose unsettled, and ask again in one line together with the Step 3 results. Never draft a focus yourself.

Files read:
- prompt/versions/STIR-L4_prompt_v1.0.txt
- eval/transcripts/2026-10-19_codex-gpt_prompt-v1.0-early_sglt2.md
- quiz/STIR-L4_calibration_quiz_v1.0.txt
- data/STIR-L4_model_v1.0.yaml