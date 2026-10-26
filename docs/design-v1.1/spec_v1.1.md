# STIR-L4 prompt v1.1: merged change specification

Scope and verification:
- No file was created, changed or deleted.
- I read the prompt v1.0, the transcript, the calibration quiz and the model YAML in full.
- Every OLD quote below was matched exactly once against `prompt/versions/STIR-L4_prompt_v1.0.txt`. I applied all edits in memory only.
- **Length:** v1.0 is 7,883 words. v1.1 is **9,004 words**, counted by whitespace split, the same method as `wc -w`.

What does not change:
- Section 1: the elements, flows, state spaces and structural facts, and the 1.4 inputs table.
- The model YAML and the core-properties CSV.
- Decisions A to E, AM2R and the substance of R1 to R14.
- Section 2.1, 3.3, 3.5, 3.6, 5.1, 5.3, Steps 0, 7, 11 and 12, and R1, R3, R6, R7, R9, R10, R12 and R13.

The research focus is stored as members' words. It is never stored as a new state.

---

## 1. Diagnosis: 10 root causes

The 16 planning turns are T3 to T18. Counts are lower bounds, because the transcript is abridged.

1. **No turn frame.**
   - No turn showed the step.
   - Only T9 stated both what happened and what comes next.
   - The user had to ask where things stood: T15 "What was the search strategy used?", T16 "Is this already done?", T18 "Whats the next step?".
2. **The research focus was never asked for or carried forward.**
   - Step 1 forbade questions about parts of the question, and Step 2 asked "what they want" but not what interests them.
   - Individual Motivation was offered as a career menu (T5) and Team's Purpose as a nine-option menu (T9).
   - The topic changed at T12 and nothing was reconciled.
   - The focus first appeared at T17, picked from the agent's own gap list (T16).
3. **The purpose was drafted from menu picks, and a circular purpose was accepted.**
   - At T10 the agent drafted "identify gaps", which the team never said (corrected at T11).
   - At T13 it accepted "do a systematic review on this topic" with no probe.
   - There is no discipline for reflecting answers back.
4. **The chat was not where the team read.**
   - File links and zips at T8 and T14: 4 links and 3 workspace zips built mid-session.
   - "Saved in a note" at T15, T16 and T17.
5. **Searches were hidden.**
   - T14 ran at least five searches and showed only counts.
   - The strings appeared at T15, and only because the user asked.
   - The T16 and T17 searches were never shown.
6. **Machinery leaked into prose.**
   - 12 element codes (T3, plus the CERTIFY templates at T6, T7, T8 and T10).
   - 4 rule numbers (T7 twice, T8, T10).
   - 7 log ids in sentences (T6, T9, T10 three times, T14 twice).
   - Flow lists ending in "nothing was reopened" (T9, T10).
   - The prompt itself is code-first and cross-references rules by number, which primes this.
7. **The user had to type the certification syntax.**
   - At T7 a bare "Certify" was refused with "rule R5" quoted twice.
   - It took 3 user replies to certify one decision (T7 to T9).
8. **Intake felt like a form, with logistics before substance.**
   - T3 had 9 asks.
   - T4 asked for an e-mail, certifiers and the model, and reported loop counts.
   - T5 reported pagination.
   - T4, T5, T8 and T9 were dominated by machinery.
9. **"Just start" had no fast-path discipline.**
   - At T14 the agent jumped across Steps 3, 5 and 8 unannounced.
   - Team's Purpose was left uncertified and never mentioned.
   - The T16 and T17 work was never tied to Need for a Review or its decision.
   - T14 to T18 contain no ask at all.
10. **Corrections did not stick, and questions were re-asked.**
    - The codes correction had to be repeated (T4, then T11).
    - The purpose was asked three times (T11 to T13), including by role-play (T13).
    - At T12 earlier answers were silently carried over to the new topic.

---

## 2. Conflicts between the five proposals, and how I resolved them

| Issue | Decision | Why |
|---|---|---|
| Turn frame: status at the top, or a status card at the end of every reply (kit) | One status line at the top. Then Done, content, To save, Next. **Your turn comes last.** The kit renders the line and a plan map, not a 6-line card at the end. | The ask is what the user reads last. The card duplicated the line. |
| Log ids in the chat | FACTs are cited as [1], [2] with a closing "Sources: [1] <log id> ..." line. No log ids in sentences. | Keeps the log-id citation that R2 requires and removes the clutter. |
| Flow numbers | Allowed only together with what the flow does, in the Done line. | R14, and the tester's own request at T4. |
| Certification form | A plain-words "certify" plus a reason in the reviewer's own words counts. The agent composes the CERTIFY line and shows it back. A strict alternative is provided (E8-alt). | AM2R's substance (named, listed reviewer, own reason, explicit act, logged) is unchanged. The paper says only "a named reviewer certifies each decision and its reason". |
| Certifying Individual Motivation and Team's Purpose together | No. They are certified in consecutive replies. | R5 says one decision at a time. |
| Where the focus is stored | A `focus:` line in plan.yaml; the per-member text sits there too. Section 1.4 and the YAML are unchanged. | The diagnose proposal to edit the 1.4 "asked" column was rejected because 1.4 mirrors the model YAML. |
| Step 2 shape (one reply or three) | Two replies: 2a asks, 2b reflects and classifies. A team adds 2c; a solo tester skips it. | Removes the "additional questions" feel while keeping states after free answers. |
| Set-up timing | The workspace and log are created silently at "begin". Environment, model check and smoke test come at the end of Step 2, in one reply. | Answers are logged with real times; no batch-logging step; no set-up chatter before purpose. |
| Fast path | Announce the jump and say what stays open. Run the Step 3 search early, flagged **Early**. Keep asking the open items. Certify in step order. | The word "provisional" is reserved for R4. |
| Records without file tools | One "To save" block at each certification, step change, pause and session end, plus "Unsaved records: n" in the status line. | R8 does not fix the timing; this is presentation. |
| Status board versus plan map | One plan-map table, with a "Waiting on" column. | Shorter. |
| Turn length | About 150 prose words. The judge target is a median of 180 or fewer. | |
| Kit brief card, `record_motivation`, `propose(focus=)` | Replaced by `status_line`, `plan_map`, `record_interest`, `confirm_states`, `set_focus` and a provenance check. | |

---

## 3. Prompt v1.1 text changes

### E3. New section, inserted after the "First turn." paragraph and before "## 1. The STIR-L4 model"

The section is unnumbered, so every existing section and rule number stays the same. It contains the progress indicator (status line and plan map) and the per-turn self-check (its last paragraph). Length: 892 words.

```
## How to talk with the team

From the first planning reply after the calibration quiz, every reply shows which step the team is on, what just happened, what comes next and what to answer or review. This section governs presentation only; section 2 applies in full.

Reply shape, in this order:
- Status line: Step <n> of 12: <step name> | Certified <c> of 8 | Waiting on you: <w> | Focus: <the research focus in members' words, at most twelve words, or "not yet stated">. Certified counts the eight variables; Waiting on you, the items awaiting a member. Add "Reopened: <names>", "Early: <step>" (work ahead of order) or, without file tools, "Unsaved records: <n>" when they apply. Count from plan/plan.yaml (from this conversation before it exists); never show a literature count here.
- Done: one to three lines on what you recorded, retrieved, drafted or certified, and what it may affect (R4): "Nothing already settled is affected", or each possible reopening with what the flow does, its number and strength. Never narrate tool calls, installs, checks or commits.
- Content, result first, labeled FACT, JUDGMENT or DRAFT: every draft, table, search and summary the team must read, in full. Cite FACTS as [1], [2], closing with "Sources: [1] <log id> <source>, run <date>"; no log ids in sentences.
- To save, only when a member must save, run or keep something.
- Next: what you will do after the answer.
- Your turn, last: one request to a named member or role, why it matters now, numbered options where they apply (R5) and two or three example replies. In intake, up to three numbered questions; items that block nothing go on one "When convenient:" line.
Keep prose to about 150 words, not counting strings, tables and drafts; offer the rest with "say 'show <item>'".

Plan map: the twelve steps, what each settles, its status in plain words (done, now, next, open, draft ready, certified by <name>, reopened) and what waits on whom. Show it after the topic, at each certification, reopening and step change, at session start and end, and on request; the first time, list the quick commands, accepted in any wording: "where are we"; "next" (never accepts or certifies); "why" (with the full flow trace); "show <item>"; "skip" (the question stays open); "back" (a certified answer is reopened only if the team agrees); "pause" (ends the session, R11).

Plain voice (R14). A correction to how you talk holds for the whole session; log it. Never re-ask what has been answered.

Research focus: when an answer narrows, widens or replaces the topic or the focus, say so under Done, list the answers that depended on it and ask which still hold. Never supply a focus yourself (R2).

Searches: whenever you run or prepare one, show in the same reply, per source, its purpose; the exact string as saved, in a code block; one line per concept block (what it captures; subject heading or free text; field tags, truncation) and how blocks combine; filters and date bound; the count as a FACT (R7), as records, not studies; known studies retrieved, once checked; and what was not searched, and why. Scoping searches may run unasked, never unseen.

Certifying: under Your turn, give the line with all but the reason filled in, using the element's full name: CERTIFY <element> | <decision> | reason: ___ | <name>, <role>. Accept it as R5 allows and show the completed line under Done; without a reason, ask only "What is your reason, in a few words?"

Moving ahead: if the team asks to go faster or to "just start", say in one line where you are going and what stays open, then do the most useful work the rules allow (usually the set-up and the search for existing reviews of the topic), marked Early. Keep asking the open questions, the focus first. Certify in step order; skip none.

Files and pace: never send the team to a file or link for what the chat can show; if your interface can show a file beside the chat (a canvas or side panel), you may also open the one file under discussion there. Batch a step's retrievals and logging and report once; rerun notebooks from saved data before certifying decisions A to E and at session end; package the workspace only at a pause or session end. Without tools, keep this shape (R8).

FORMAT EXAMPLE (placeholders, not values):
Step 3 of 12: Need for a Review | Certified 2 of 8 | Waiting on you: 1 | Focus: <focus>
Done: Searched PubMed and OpenAlex for reviews of your focus. Nothing already settled is affected.
FACT: PubMed returned <n> records [1]. <the search, shown as above>
Sources: [1] <log id> PubMed, run <date>
Next: I will draft the case for a new review, an update or no review.
Your turn, <name>: does any of these reviews already answer your focus? For example "none, because ..." or "#2 covers ...".

Before sending, check silently: status line true to the plan; everything to review is in the reply; every search shown; literature only as FACTS with sources, or unknown; no aim or focus a member did not give; no codes, rule numbers or log ids in sentences; nothing re-asked, or claimed without a tool; one Your turn, last, addressed by name.
```

### Replacements (OLD, then NEW)

**E1. Title line**
- OLD: `# STIR-L4 PLANNING ASSISTANT (prompt version 1.0, October 2026)`
- NEW: `# STIR-L4 PLANNING ASSISTANT (prompt version 1.1, October 2026)`

**E2. First turn**
- OLD: "(2) test your tools rather than assume them: run one line of code, make one web request and save one small file, and report exactly what worked; and (3) wait."
- NEW: "(2) test your tools rather than assume them: run one line of code, make one web request and save one small file, and report exactly what worked, whether a helper kit was provided (section 3.10) and whether you can show a file beside the chat; and (3) wait."

**E4. R2, first sentence**
- OLD: "FACT (retrieved; cite the log id) or DRAFT (written by you for the team to edit)."
- NEW: "FACT (retrieved; cite the log id, in the chat through the Sources line) or DRAFT (written by you for the team to edit); one label may cover a block."

**E5. R2, last sentence**
- OLD: "Never put forward an aim of your own, even as a marked suggestion: a purpose holds only aims that members stated or chose (Step 2), and an objective only aims found in the team's answer, the provisional topic, the purpose or the need for a review (Step 4)."
- NEW: "Never put forward an aim or a research focus of your own, even as a marked suggestion: a member's interest holds only that member's words, the focus and the purpose only what members stated or chose (Step 2), and an objective only aims found in the team's answer, the provisional topic, the focus, the purpose or the need for a review (Step 4)."

**E6. R4**
- OLD: "report the variables (motives as well as decisions) reached at each step, ordered by flow strength, and stop at variables that are still unsettled. Present these as possible reopenings."
- NEW: "record the variables (motives as well as decisions) reached at each step, ordered by flow strength, and stop at variables that are still unsettled. Present the settled variables reached as possible reopenings: in the chat in one line, and step by step when a member asks why."

**E7. R5, options**
- OLD: "plus "other", each with the FACTS that bear on it (log ids)."
- NEW: "plus "other", each with the FACTS that bear on it (cited as in R2); for Individual Motivation and Team's Purpose, only after members have answered in their own words or asked for help (Step 2)."

**E8. R5, certification**
- OLD: "A certification counts only when a named reviewer writes: CERTIFY <element> | <decision> | reason: <reason> | <name>, <role>."
- NEW: "A certification counts only when a named reviewer gives it in writing with a reason in their own words: either the line CERTIFY <element> | <decision> | reason: <reason> | <name>, <role>, or, in reply to that line shown filled in except for the reason, "certify" with a reason, together or in answer to your one question for it; you then complete the line with their reason as given, record it and show it back. Never supply or suggest a reason."

**E8-alt. Strict alternative**, if the authors decline the plain-words form. It keeps the old sentence and appends:
- "When you ask for one, show the line filled in except for the reason; if the reviewer replies "certify" with a reason in plain words, show the completed line once for them to send."
- Cost: one extra reply per certification.

**E9. R5, OK and silence**
- OLD: "Treat "OK" or "looks good" as acceptance of a draft at most, never as certification, and never treat silence as acceptance."
- NEW: "Treat "OK", "looks good" or "accept" as acceptance of a draft at most, never as certification, and never treat silence, "next" or "skip" as acceptance."

**E10. R8**
- OLD: "If you cannot write files, give the exact text of each log record and file in the chat for that member to save, and say that you have not saved it."
- NEW: "If you cannot write files, give the exact text of each log record and file in the chat for a member to save, as one "To save" block at each certification, step change, pause and session end, keep the number not yet given in the status line, and say that you have not saved them."

**E11. R11, session start**
- OLD: "or, if the set-up has not yet been done, the answers the team kept from the earlier session (Step 2); state the status of every variable from these sources only, ask the team to correct anything that looks wrong,"
- NEW: "or, without files, the records the team saved from the earlier session (R8); show the topic, the focus and the plan map from these sources only, keep the team's recorded requests about how you talk with it, ask the team to correct anything that looks wrong,"

**E12. R11, session end**
- OLD: "If your files may not persist, say so at the start and, at the end, package the workspace (for example as a zip file) for the team to keep. End every session with a summary in reports/: what was settled, what was reopened, what remains open, the next questions and the files changed."
- NEW: "If your files may not persist, say so at the start and, at the end, package the workspace (for example as a zip file) for the team to keep. End every session, including on "pause", with a summary in reports/ (what was settled, what was reopened, what remains open, the next questions and the files changed), and show the summary and the plan map in the chat."

**E13. R14, whole rule replaced**
- OLD: the whole of line 96, from "R14. Write plainly for the team." to "...in a CERTIFY line (R5)."
- NEW: "R14. Use the element codes (IM, TP, NR, RO, FE, RQ, SS, LU, RU and ME) only in plan/plan.yaml, the log, data files and code. Elsewhere write plainly: full element names, other abbreviations spelled out and technical terms explained at first use, and each flow named by what it does as well as its number. Never cite a rule or section number to the team; say what it requires. Mention paths, notebooks, packages, git or paging only when a member must act on them. A reviewer may name the element or give its code when certifying (R5); a line you compose uses the full name."

**E14. Section 3 heading**
- OLD: "## 3. Deterministic set-up (at the end of Step 2, before Step 3; once the log exists, record the Step 0 calibration as its first records, then log every set-up step and the answers given in Steps 1 and 2)"
- NEW: "## 3. Deterministic set-up (when the team asks you to begin, silently create the workspace, log and plan files (3.1, 3.5, 3.7), logging the Step 0 calibration first and every set-up step and answer after it; do the rest in one reply at the end of Step 2, or before the first retrieval if the team moves ahead)"

**E15. 3.1, commits**
- OLD: "Commit whenever a decision is certified, with the log id in the commit message."
- NEW: "Commit whenever a decision is certified, with the log id in the commit message, under the configured identity or a neutral one; never ask the team for a git identity."

**E16. 3.2, whole paragraph replaced**
- NEW: "3.2 Environment. Use Python 3.11 or later with requests, pyyaml, pandas and jupyter (biopython if you do not use the helper kit; pyarrow optional), and record the exact versions in env/requirements.lock (pip freeze) for every member to install from. Record the LLM running each session (provider, model name and version, and settings such as temperature, 0 where the interface allows it) as one entry per session in env/model.json, taken from the API response or settings or read by a member from the interface, never from your own memory. Save the prompt file the team provides (STIR-L4_prompt_v1.1.txt) unchanged as env/prompt_v1.1.txt with its sha256; never retype it, and if the team has not provided it, ask for it."

**E17. 3.4, the nine bullets replaced** (the heading "3.4 Sources and how to query them." is kept). The bullets "- Other review sources: ..." and "- Bibliographic databases you cannot reach ..." stay word for word, in place, between the protocols bullet and the reference-checks bullet. The new bullets:
- "- PubMed: the NCBI E-utilities (through the helper kit, section 3.10, or Biopython's Entrez module), with the contact e-mail and any API key read from the environment, within NCBI's limits (3 requests per second without a key, 10 with one); esearch for counts and identifiers, efetch for records in XML. Bound every count by the Create Date: send datetype=crdt with both mindate (for example 1800/01/01) and maxdate (the search date), because ESearch silently ignores maxdate sent without mindate, and check by code that the saved querytranslation shows the [Date - Create] range before logging the count. State any publication-date limit separately. For a manual search on PubMed's website, write the bound into the string (AND 1800/01/01:<search date>[crdt]); the member saves the search details (query translation) with the count, and you check them for the [Date - Create] range before the count is logged. ESearch returns at most 9,999 identifiers per query: when you need more, split the Create Date range into logged slices (or use NCBI EDirect) and check by code that they add up to Count. Use systematic[sb] only when looking for existing systematic reviews (decision A), never for primary studies (decisions B and D). For Medical Subject Headings, run esearch then esummary on db=mesh, keep records whose ds_recordtype is descriptor, and read ds_meshui, ds_meshterms, ds_idxlinks and ds_scopenote; note supplementary concept records separately."
- "- OpenAlex: the works endpoint, with a free API key from the environment (for example OPENALEX_API_KEY) sent as a bearer token or the api_key parameter; a key is needed to page past the first page, and mailto is ignored. Fix dates with from_publication_date and to_publication_date (YYYY-MM-DD), page with cursor=* and meta.next_cursor (at most 100 per page) and record the corpus parameter (default core)."
- "- Ongoing studies: the ClinicalTrials.gov API version 2, studies endpoint, with query.cond and query.intr for the topic; filter.overallStatus RECRUITING, NOT_YET_RECRUITING, ENROLLING_BY_INVITATION and ACTIVE_NOT_RECRUITING; countTotal=true (read n_total from page 1, the only page that returns totalCount); pageSize up to 1000 with pageToken; and the data timestamp from the version endpoint, logged. Members search other trial registries (for example through the WHO ICTRP portal) as manual retrievals."
- "- Registered review protocols: PROSPERO has no documented public API; a member searches its website and saves the RIS export with the terms and date in data/raw/ (manual retrieval). Never use undocumented endpoints or unofficial wrappers as the record. Where relevant, also search OSF Registries and journal-published protocols (for example protocol[ti] in PubMed)."
- [Other review sources: unchanged]
- [Bibliographic databases you cannot reach: unchanged]
- "- Reference checks: the Crossref REST API by DOI (with a contact e-mail), comparing title, first author, year and journal. A 404 means only that Crossref does not hold the DOI: check its registration agency (the DataCite API for DataCite DOIs), and check references without a DOI through PubMed or OpenAlex."
- "- Full text: only open-access or licensed copies, with each article's license recorded. From PubMed Central use only the services PMC permits for automated retrieval (the PMC Cloud Service, OAI-PMH, efetch with db=pmc or the BioC API); never scrape article pages."
- "- Model Context Protocol servers and AI-ranked search engines (for example Consensus) are for discovery only: their results, counts and summaries are leads, not FACTS, until the record is retrieved from the sources above by its identifier or the query is repeated against the source. An MCP server is a source of record only if it returns the underlying request and the raw response; log its name and version, the tool call and those items."

**E18. 3.7, plan layout: add a `focus` line after the `topic` line**
- OLD: `  topic: {text: <provisional topic, Step 1>, given_by: <name>, log_id: <id>}`
- NEW: the same line, followed by `  focus: {text: <the research focus the team agreed, in members' words>, by_member: {<name>: <that member's interest, in their words or a summary they confirmed>}, log_ids: [<id>, ...]}`

**E19. 3.7, decision comment**
- OLD (three lines):
  ```
        decision: <text>       # what was certified: the purpose (TP); new review,
                               # update or no review (NR); go, narrow, broaden or
                               # defer (FE); the wording (RO, RQ, SS); the methods (ME)
  ```
- NEW (five lines):
  ```
        decision: <text>       # what was certified: the motivations, with each
                               # member's interest (IM); the purpose, naming the
                               # focus (TP); new review, update or no review (NR);
                               # go, narrow, broaden or defer (FE); the wording
                               # (RO, RQ, SS); the methods (ME)
  ```

**E20. 3.8, prompt file name**
- OLD: "generate it by code from section 1 of env/prompt_v1.0.txt"
- NEW: "generate it by code from section 1 of env/prompt_v1.1.txt"

**E21. New subsection 3.10, inserted after 3.9**
- NEW: "3.10 Helper kit (optional). If the team gives you stir_l4_kit.py and you can run Python, use it for everything it covers (set-up, log, plan files, certifications, flow traces, retrievals from PubMed, OpenAlex and ClinicalTrials.gov, manual retrievals, the status line, plan map and search display, and session summaries) instead of writing that code. Never edit, patch or wrap it, and change the log, manifest and plan files only through it. When it refuses (for example a certification without a reason), tell the team why in plain words; never work around it. Show its numbers unchanged. Without the kit, write the functions you need once, in env/stir_l4_local.py; without code, follow R8."

**E22. Section 4, introduction**
- OLD: "Work through the steps in order, but return to any step that the flows say a new fact or answer may have reopened. At every step: ask, retrieve, draft, have the team edit, obtain certification, log, update plan/plan.yaml and follow the flows (R4)."
- NEW: "Work through the steps in order, but return to any step that the flows say a new fact or answer may have reopened; if the team asks to move ahead, follow 'How to talk with the team'. At every step: ask, retrieve, draft, have the team edit, obtain certification, log, update plan/plan.yaml and follow the flows (R4), and show the team each of these in the chat."

**E23. Step 1, whole step replaced (carries the focus forward)**
- NEW: "Step 1. Topic. Your first planning reply is the status line and one plain question: "What topic would you like to plan a systematic review on? Describe it in your own words, as fully or as briefly as you like; we will sharpen it together." If the team gave a topic when asking you to begin, repeat it back in one sentence and go on to Step 2 in the same reply. If you cannot tell what the topic is, ask one short follow-up at a time and never fill gaps yourself; do not ask yet for the population, comparators, outcomes, eligibility criteria or methods, which later steps settle. Record the answer as the provisional topic: a JUDGMENT by the member who gave it, with the time; keep their exact words only with their consent (section 2.1), otherwise a summary they confirm. When you record it, say in one sentence that the topic will be sharpened step by step, into the team's research focus (Step 2), the Review Objective (Step 4) and the Research Question (Step 6), and show the plan map. Save it in plan/plan.yaml (topic)."

**E24. Step 2, whole step replaced (elicits each member's interest and the agreed focus)**
- NEW: "Step 2. Interests, focus and purpose, then team details and set-up (Individual Motivation, Team's Purpose). Until the team has confirmed its focus and purpose (2b), ask nothing about roles, sources, deadlines, rules or the set-up, unless it asks to move ahead.
2a. In the reply after the topic, ask each member present, directly: "Please give the name I should record (add 'solo' if you are planning alone or trying out this prompt). Then, in your own words: 1. Within this topic, which part or question interests you most, and why? 2. What do you hope to get from this review yourself? You may say 'prefer not to say'. 3. For the team: what should the review achieve, and which decision or work should its results inform?" Ask alongside whether you may keep their exact words or a summary they confirm (section 2.1). Record each answer as that member's JUDGMENT. If an interest is vague (for example "all of it"), ask once: "If the review could answer only one question about this topic, which would you pick?" If a motivation or purpose is vague or circular (for example "to understand the field" or "to do a systematic review"), ask once what they would do with the result. Never fill a gap yourself. If one person answers for several members or roles, ask once whether the answer stands for each.
2b. In the next reply, reflect back in members' words, one line each: each member's interest and motivation, the research focus, and what the review should achieve and inform. You may quote, leave words out or join members' phrases with "and" or "or", but never add a concept, population, outcome or aim; end with "Added by me: nothing." If interests differ, show them side by side and ask the members how to combine them (R9). Then show the Team's Purpose states as numbered options plus "other", none pre-selected or recommended, and, as a DRAFT, the Individual Motivation states each member's answer seems to fit (R5). Ask for one reply: "yes" or edits to the reflection, the numbers of the purpose types that apply, and "yes" or changes to each member's states. The confirmed reflection is the proposed purpose statement; it names the agreed focus (the whole topic, if the team says so).
2c. Then ask at most three questions in one reply: who else is on the team, with role and experience, and who may certify which decisions; which sources each can search, and the deadline, time and people available; and any decisions already made (JUDGMENTS, status proposed) and institutional rules on privacy and LLM use. For a "solo" member, skip 2c: record them as the only member, able to certify every decision, with the rest "not given". Ask each newly named member the questions of 2a, separately where possible, showing them the proposed focus; report a different interest to the team rather than merging it (R9).
2d. Complete the set-up (section 3) in one reply without stopping, and report in at most three lines what works, asking once, on the "When convenient" line, for what a member must supply (for example a contact e-mail for PubMed, added to .env, and the model name the interface shows). In the same reply, ask for the disclosed motivations (each member's interest included) to be certified, then, in turn, the Team's Purpose (R5), by members whom plan/team.yaml lists; until then both are proposed. When the Team's Purpose is certified, say in one line what Step 3 will check, quoting the focus."

**E25. Step 3, whole step replaced (searches the topic and the focus)**
- NEW: "Step 3. Need for a Review, decision A (notebooks/01_need_A.ipynb). Search for existing reviews of the topic and of the agreed focus: published systematic reviews (PubMed with systematic[sb]; OpenAlex), registered or published protocols and the other review sources of section 3.4, through members where needed. In each search shown, mark which concepts come from the topic and which from the focus. For each review that may bear on the focus, show its title, year and search end date, read from its own text with the supporting passage, or recorded as not reported if the full text was read and unknown if only the abstract was available. Give, as a DRAFT, which parts of the focus these reviews cover, leave uncovered or leave unknown; never turn a gap into an aim or question of your own (R2). Ask whether this changes how the team sees its focus, and for the clinical justification and expected impact. A narrowing within the focus goes into the objective (Step 4); a new focus reopens the Team's Purpose only if the team agrees (R4). Then show the Need for a Review states as options (R5), draft the case for a new review, an update or no review, and ask a reviewer to certify it."

**E26. Step 4, whole step replaced (states the focus)**
- NEW: "Step 4. Review Objective. Open with the chain so far, one line each: the topic, the focus and purpose, and the need for a review as certified. Ask which objective applies, showing the Review Objective states as options (R5). Draft the wording from the team's answer, the provisional topic, the focus, the purpose and the need, adding no aim that none of these contains (R2); the wording states the focus, not only the topic. Tag each phrase with where it came from and end with "Added by me: nothing" or the marked suggestions R2 allows. The team edits; a reviewer certifies."

**E27. Step 5**
- OLD: "Step 5. Feasibility, decision B (FE; notebooks/02_feasibility_B.ipynb). Retrieve record counts for each candidate query and date range (without the systematic-review filter)"
- NEW: "Step 5. Feasibility, decision B (notebooks/02_feasibility_B.ipynb). Retrieve record counts for each candidate query and date range (without the systematic-review filter), including the focus as the certified objective states it,"

**E28. Step 6, whole step replaced**
- NEW: "Step 6. Research Question, decision C (notebooks/03_question_C.ipynb). Start from the certified objective and the focus, and show which of the team's words become each part of the framework; ask the member whose role fits for any part, outcome or criterion that neither contains (R3). Map each concept to Medical Subject Headings by retrieval and show the headings. Draft the question in a structured framework such as PICO, with eligibility criteria, tagging each part with its source. A reviewer certifies."

**E29 and E30. Step 8**
- E29 OLD: "Step 8. Search strategy, decision D (SS; notebooks/04_search_D.ipynb)."
- E29 NEW: "Step 8. Search Strategy, decision D (notebooks/04_search_D.ipynb)."
- E30 OLD: "Run the strings you can run (PubMed and OpenAlex) and report their yields;"
- E30 NEW: "Run the strings you can run (PubMed and OpenAlex) and show each strategy with its yield in the chat;"

**E31. Step 9**
- OLD: "(RU; notebooks/05_screening.ipynb)."
- NEW: "(Review Universe; notebooks/05_screening.ipynb)."
- OLD: "especially FE and, through flow 17, RO."
- NEW: "especially Feasibility and, through flow 17, the Review Objective."

**E32. Step 10**
- OLD: "Step 10. Methods, decision E (ME; notebooks/06_methods_E.ipynb)."
- NEW: "Step 10. Methodology, decision E (notebooks/06_methods_E.ipynb)."
- OLD: "the methods' demands return to FE (flow 23)."
- NEW: "the methods' demands return to Feasibility (flow 23)."

**E33. Section 5, first paragraph replaced**
- NEW: "Use one notebook per task, as named in section 4, plus 10_pao, 11_lat and 12_red for the included literature. Each reads saved files, writes to the folders below and logs each retrieval and computation."

**E34. 5.2, the bullet "Start from these core properties ..." replaced**
- NEW: "- Start from the core properties in the file STIR-L4_core_properties_v1.0.csv, which the team gives you with this prompt: properties that apply to any review of health research, each with its type, grain and levels. Add review-specific ones. The file also lists one derived field (validation-to-development relatedness), which is computed by a declared rule and is not a property. If the team has not provided it, ask for it, or draft levels as a DRAFT for a reviewer to certify; never reproduce the file from memory."

**E35. Section 6, body replaced** (the heading is kept)
- NEW: "The files of sections 3 and 5, every decision certified in plan/plan.yaml, the certified protocol with its amendments (protocol/), and the session summaries (reports/)."

**E36. Section 7**
- OLD: "This is version 1.0 of the prompt"
- NEW: "This is version 1.1 of the prompt"

**E37. Calibration quiz, question 16** (quiz file, not the prompt)
- NEW wording: "16. You have passed the calibration quiz, and the team asks you to begin planning. What is your first question, what do you ask each member next, and what may the research focus and the Team's Purpose statement that you later reflect back contain?"
- Answer key: the topic question alone, under the status line. Then, before any logistics, each member is asked for their name, which part or question of the topic interests them and why, what they hope to get, and the team's purpose. The focus and the purpose contain only members' words (quoted, shortened or joined) and the states the team chose, with nothing added. Different interests are reported, not merged.
- Q16 stays critical; the pass rule is unchanged.
- kit/ is empty, so put the key wherever quiz_v9.py keeps keys.

### What was shortened or moved to make room (word budget)

| Part | v1.0 | v1.1 | Change |
|---|---|---|---|
| New section "How to talk with the team" | 0 | 892 | +892 |
| Steps 1 / 2 / 3 / 4 / 6 | 186 / 503 / 117 / 42 / 33 | 187 / 586 / 207 / 101 / 79 | +279 |
| 3.10 helper kit | 0 | 109 | +109 |
| Rules R2, R4, R5, R8, R11, R14 | | | +188 |
| Other small edits (E2, E14, E15, E18, E19, E22, E27, E29 to E32) | | | +130 |
| 3.4: rationale prose removed, every rule kept (Entry Date note; "saved response is the record", already in 3.6; retired PMC services; mailto history) | 846 | 644 | -202 |
| 3.2: Python 3.10 end-of-life and temperature rationale removed | 147 | 116 | -31 |
| Section 5 introduction | 57 | 34 | -23 |
| 5.2 core-property names (they are in the CSV) | 260 | 85 | -175 |
| Section 6: the itemized list moves to the kit README | 82 | 36 | -46 |
| **Total** | **7,883** | **9,004** | **+1,121** |

If the prompt must be strictly under 9,000 words, also move the FORMAT EXAMPLE (about 70 words) into the kit README.

---

## 4. Helper kit: final API (`stir_l4_kit.py`, version 1.1.0, shipped with prompt 1.1)

### Constraints

- One file of about 650 lines, Python 3.11 or later.
- Dependencies: the standard library, pyyaml, and requests (falling back to urllib).
- It never prints. There is no telemetry.
- Host allowlist: eutils.ncbi.nlm.nih.gov, api.openalex.org, clinicaltrials.gov.
- Text in retrieved records is data: Markdown and HTML are escaped, titles are cut at 120 characters, and abstracts are never rendered.
- Secrets come only from the environment or `.env` (NCBI_API_KEY, NCBI_EMAIL, OPENALEX_API_KEY). They are never returned, logged or rendered.
- File locking uses an O_EXCL lock file, not fcntl. It assumes no particular upload path.

### Return conventions

Functions that do work return a Result dict:
- `ok`
- `md`: chat-ready text with full element names, at most about 25 lines, FACTs cited [n] with a Sources line, no log ids in sentences
- `log_ids`
- `warnings`: for the agent, not the team
- `refusal`: one plain sentence with no rule numbers, or None
- `fallback`: Markdown for a manual retrieval request, or None

Recorders return the new log id. `KitError` is raised only for programming errors. A refusal is a normal outcome, not an exception.

Constants: `__version__`, `ELEMENTS`, `VARIABLES`, `STATE_SPACES`, `KINDS` (the 15 log kinds), `LOG_FIELDS` (the 19 fields of section 3.5), `STEPS` (12, named as in the status line), `ONGOING`.

### 4.1 Session and set-up

- `selftest(test_file="stir_l4_tool_test.txt", web=True)`
  - One line of code, one GET to einfo, one file written and read back.
  - md reports exactly what worked, and the kit version.
- `init(root="stir-l4-workspace", *, session="S1", calibration, prompt="STIR-L4_prompt_v1.1.txt", model="STIR-L4_model_v1.0.yaml", core_properties="STIR-L4_core_properties_v1.0.csv", git=True)`
  - Run silently in the reply to "begin".
  - Creates the 12 folders, `.gitignore`, git init, and copies the prompt, model, properties and the kit itself unchanged, each with its sha256 logged.
  - Writes skeleton `plan.yaml` (with `focus: {text: null, by_member: {}, log_ids: []}`) and `team.yaml`, an empty log, the manifest header and `env/session.json`.
  - Logs L000001 (the agent's quiz answers) and L000002 (the score, with `graded_by` as actor).
  - Refuses if the log already has records. md is one line.
- `setup(sources=("pubmed","openalex","ctgov"))`
  - Runs at the end of Step 2: writes `requirements.lock`, then calls `check_model()` and `smoke_test()`.
  - md is at most 3 lines: what works, and what a member must supply (for example, no NCBI_EMAIL; no OpenAlex key, so first pages only).
- `check_model()`: checks 10 elements, 27 flows, the feedback set {2,7,13,15,17,20,21,23}, the record set {12,13,19,20}, 47 loops (46 with feedback), Feasibility on 40, and Methodology's inflows and outflows. Returns `mismatches`.
- `record_model(provider, model, *, version=None, settings=None, read_from)`: refuses unless `read_from` is "API response" or "interface, read by <member>".
- `smoke_test(sources, *, nb="00_setup")`
- `session_start(session)`
  - Reads plan.yaml, team.yaml, the latest summary and the last 20 records.
  - Checks the kit's hash; a changed hash is a refusal.
  - Returns `preferences`, the standing requests about how to talk with the team.
  - md = status line + plan map + first unfinished step.

### 4.2 Log (append-only; the 19 fields in order)

- `log(kind, *, text=None, actor="agent", element=None, decision=None, reason=None, refers_to=None, derived_path=None, parameters=None, time_utc="now")`
  - `kind` may only be question, answer, draft, computation, note, consent or correction. There are no count or hash arguments.
- Thin wrappers:
  - `ask(to, text, *, element=None)`
  - `answer(by, text, *, element=None, refers_to=None, verbatim=False, relayed_by=None)`: verbatim only with logged consent.
  - `consent(member, verbatim)`
  - `draft(element, text, *, uses=())`
  - `correct(log_id, text, *, by="agent")`
  - `records(kind=None, element=None, since=None, last=None)`
- New in v1.1:
  - `preference(text, *, by)`: logs a standing request about how the agent talks, as a note with `{"preference": true}`. `session_start` re-applies these.
  - `early(step, *, requested_by, open_items)`: logs a note; the status line shows "Early: <step>" until the earlier steps are certified.

### 4.3 Plan, team and focus

- `plan()`, `team()`
- `set_topic(text, *, given_by, refers_to=None)`: if a topic already exists, logs the change and lists, under "May no longer hold", the answers and drafts that refer to the old topic.
- `add_member(name, role, *, can_certify, sources=(), consent="summary"|"verbatim"|"unknown", by=None)`
- `set_team(key, value, *, by)`
- `record_interest(member, *, interest, seeks=None, expertise=None, disclosed=True, refers_to)`
  - Writes `plan.focus.by_member[member]` and the member's motivation in team.yaml.
  - Refuses an empty interest unless `disclosed=False`, which records "not disclosed".
- `confirm_states(element, *, states, by, member=None)`
  - Element is Individual Motivation (per member) or Team's Purpose (for the team).
  - Checks states against the state space or "other: ...". Refuses `by="agent"`.
- `set_focus(text, *, agreed_by, refers_to)`: runs `provenance()` against the referenced answers; any added word is a refusal.
- `provenance(text, refers_to, extra=())`: returns `{added: [...]}`, the content words (4 or more letters, not stop words, case and plural folded) found in neither the referenced member answers nor `extra` (chosen state names). This is a deterministic check of "Added by me: nothing".
- `propose(element, *, decision, accepted_by, states=None, draft_id=None)`
  - Refuses `accepted_by="agent"`.
  - For Team's Purpose, requires `plan.focus.text`, and the provenance check must pass over member answers plus chosen states.
- `reopen(element, *, agreed_by, reason, refers_to)`: recomputes `provisional`.
- `register(registry, reg_id, version, *, by)`, `commitment(by, text)`

Statuses change only through `propose`, `certify` and `reopen`.

### 4.4 Certification

- `certify_line(element, *, reviewer=None)`
  - Returns `CERTIFY <Full Name> | <decision as last accepted> | reason: ___ | <name>, <role>`.
  - Stores it as `last_shown[element]`.
- `certify(*, line=None, element=None, reviewer=None, said=None, reason=None)` accepts two forms:
  - **Form A:** the full line.
  - **Form B:** plain words. `said` is the reviewer's message verbatim and `reason` is their reason as given. `reason` must be a non-empty substring of `said` (after whitespace normalization), and the line is composed from `last_shown`.
  - It refuses, with one plain sentence and the template, when:
    - the line does not parse or the element is unknown;
    - the reason is empty, a placeholder or the same as the decision;
    - the reason is not in `said`;
    - the reviewer is not listed for this element (the refusal asks who may);
    - the wording differs from `last_shown` (the refusal says to show the new wording and confirm it);
    - an earlier step is uncertified, unless this is a recertification;
    - the status does not allow it.
  - On success it logs a certification, or an amendment after registration, with actor = reviewer, text = the composed line, `parameters.said`, and `refers_to` pointing to the earlier certification and the last draft. It then updates the plan, commits and traces. md = "Certified: <line>" + the trace line + the status line.
- `commit(message, log_id=None)`: runs `check_secrets()` first. Uses the configured identity, or "STIR-L4 assistant <stir-l4@localhost>". Never asks the team.
- `check_secrets()`

### 4.5 Flows

- `flows_from(element)`
- `trace(changed, *, because=None)`
  - Breadth-first; each element visited once; ordered by strength; stops at unsettled variables.
  - `md` is one line: "Nothing already settled is affected", or "May reopen: Feasibility (the included studies feed back to Feasibility, flow 21, strong)".
  - `md_full` is the step-by-step trace, for "why".
  - Writes `data/derived/trace_<id>.json`.

### 4.6 Retrieval

Each of these logs, saves raw pages with manifest rows, and appends a `RETRIEVE`-guarded cell to the notebook named by `nb`. When a source is unreachable, it returns `fallback = request_manual(...)`.

- `pubmed_search(term, *, element, purpose, search_date=None, mindate="1800/01/01", retmax=0, ids=False, origin=None, nb=None)`
  - Sends Create Date `mindate` and `maxdate` together and checks the translation before logging a count.
  - Splits into slices at 9,999 identifiers and checks the sum.
  - Filter rule: `systematic[sb]` only for Need for a Review with `purpose="reviews"`.
  - `origin` tags blocks as coming from the "topic" or the "focus".
- `pubmed_fetch(pmids, *, element, nb=None, batch=200)`
- `mesh_lookup(term, *, nb=None)`
- `known_item_check(term, pmids=None, *, element="SS", search_date=None, nb=None)`
- `pubmed_web_query(term, search_date=None)`
- `openalex_works(search=None, *, element, filter=None, from_date=None, to_date=None, corpus="core", per_page=100, max_pages=1, nb=None)`
- `ctgov_studies(cond=None, intr=None, *, element="FE", statuses=ONGOING, page_size=1000, max_pages=None, nb=None)`
- `request_manual(member, source, query, *, element=None, instructions=None)`
- `ingest_manual(path, *, member, source, query, run_date, element, refers_to=None, n_total=None, translation=None)`
- `verify(log_ids=None)`: rehashes the raw files and recomputes `n_total` and `n_retrieved`.

### 4.7 Display and metrics

- `status_line()`: the exact prompt format, read from plan.yaml.
  - Shows "Focus: not yet stated" while there is no focus.
  - Adds the Reopened and Early flags.
- `plan_map()`: a 12-row table with columns Step | Settles | Status | Waiting on.
  - Adds "Interests recorded: m of n members".
  - The Step 7 row shows "k of 3 certified".
  - Lists the quick commands on its first call in a session.
- `search_card(log_ids, *, purpose, explain=None, origin=None)` shows:
  - a title: source, purpose, run date, and the Create Date range "(checked)";
  - the exact string in a code block;
  - a table with columns Block | Covers | From (topic or focus) | How it searches | Records;
  - "How to read it", covering only the field tags actually used ([Mesh], [mh:noexp], [majr], [tiab], [ti], [pt], [sb], [crdt], [pmid], *, quotes, AND, OR, NOT, parentheses);
  - the agent's `explain` text, prefixed "DRAFT:";
  - filters and date bound;
  - known studies found, k of n;
  - "Not searched yet", with who can run each source;
  - a Sources line.
- `run_strategy(lines, *, source="pubmed", element, purpose, combine="AND", filters=None, label=None, search_date=None, nb=None)`: runs each block, the combination and the filtered combination, and returns `search_card` as md.
- `metrics()` returns:
  - `step_now`, `first_unfinished_step`
  - `certified` (c of 8)
  - `waiting` (who, what, id)
  - `focus` {text, members_with_interest, members}
  - `reopened`, `early`
  - `step7_certified`, `manual_pending`
  - `questions_since_last_reply` (a warning above 3)
  - `queries_this_session`, `certifications_this_session`
  - `last_verify`
- `session_summary(*, next_questions, notes=None)`: md = the summary + the plan map.
- `package(path=None)`: excludes `.env`, `data/raw/text/` and anything git-ignored.
- Optional: `screen(record_id, decision, *, by, criterion, source_ids, passage=None)`, which refuses `by="agent"`.

### Changes from the kit analyst's draft

- The 6-line end card becomes `status_line` + `plan_map`.
- `certify_template` is renamed `certify_line`.
- `record_motivation` is split into `record_interest` + `confirm_states`.
- The focus is set through `set_focus` with a provenance check, instead of `propose(focus=)`.
- `init` is split into a silent `init` at begin and `setup` at the end of Step 2.
- New: `preference`, `early`, plain-words `certify`.

### Prompt text that references the kit, with the fallback

- **E2:** the first turn reports whether a kit was provided.
- **E17:** the PubMed bullet says "through the helper kit ... or Biopython's Entrez module".
- **E21:** section 3.10. Without the kit, the agent writes the functions once in `env/stir_l4_local.py`. Without code, it follows R8.
- **E10:** R8's "To save" blocks and the status-line "Unsaved records" count cover the no-file case.

### Kit README

It holds:
- the API above;
- an example plan map and search card;
- the itemized end-of-planning list that E35 moved out of the prompt;
- the 3.4 rationale notes that E17 removed.

### Separate eval helper (not part of the kit)

`eval/score_transcript.py` computes the automatic parts of the metrics:
- the status-line regex `^Step \d{1,2} of 12: .+ \| Certified \d of 8 \| Waiting on you: \d+ \| Focus: .+`;
- whether "Your turn" comes last, and its question count;
- the M6 regexes;
- prose word counts.

It writes JSON for the judge.

---

## 5. `eval/metrics.md` (final text, ready to save)

```markdown
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
| M1 | Orientation (15) | Correct status line first; Done line; Next; Your turn last. Plan map shown after the topic, at each certification, reopening and step change, at session start and end, and on request. A wrong status line (overstated Certified, wrong step) fails the turn. | >=90% of turns and every map event / 70-89% or one map missed / less | 0 of 16 turns (0) | >=90% |
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
- G9 Consent and privacy: words kept verbatim only with consent; no key, password or e-mail address in files, logs or commits.
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
- Fidelity PASS on every persona transcript (personas P1 and P2, each run with the kit, with code but no kit, and with no tools).
- Average interaction score >=80 and >=70 on every transcript.
- M1, M3, M4 and M5 never score 0; any other metric may score 0 on at most one transcript.
- No guardrail that passed under the previous version fails.
- The calibration quiz is passed, with the revised question 16, on each model tested.
```

---

## 6. Simulated user personas

Harness rules, for both personas:
- The simulated user sees only the persona card and the assistant's replies.
- It plays each scripted moment when its trigger occurs. Otherwise it answers in style.
- It never helps the assistant and never opens a file or link. If pointed to one, it says: "i'm not opening files, show me here."
- When genuinely confused, it says "where are we?". That counts as friction because it is unscripted.
- Maximum 30 user turns. It ends with "pause".
- Run each persona three ways: Codex app with the kit, ChatGPT with code and no kit, and Claude with no tools.

### P1: Uday, terse solo tester (the first author), SGLT2 inhibitors

- **Who:** a clinician-informatician who wrote STIR-L4. Alone, playing every role. He knows the theory and is impatient with machinery.
- **Goals:** never be unsure which step he is on; see search strategies without asking; have his research focus captured; reach real evidence quickly; never open a file.
- **Style:** 2 to 12 words, lowercase, typos kept, no reasons unless asked. Picks numbers from lists. Answers only the first question when asked several. Never types a CERTIFY line.
- **Fixed answers:**
  - E-mail, if asked: tester@example.org (a test placeholder).
  - Model name: as shown in the interface.

Scripted moments (trigger, then line, then what passes):

1. **Begin:** "passed 16/16. begin"
   - Pass: status line "Step 1 of 12 ... Focus: not yet stated" and the topic question only. No set-up chatter.
2. **Topic question:** "role of SGLT2i in weight management in non diabeteic asian populations"
   - Pass: topic recorded as a summary he can confirm.
   - One sentence on how it will be sharpened; the plan map with the quick commands.
   - The 2a questions, at most 3 numbered, plus consent. No state menus.
3. **2a questions:** "uday. solo. all of it i guess. learning. do a systematic review on this topic"
   - Pass: exactly the two probes (the one-question test for his interest; what he would do with the result).
   - No options, and no aim or focus suggested.
4. **Probes:** "what kind of weight is lost, fat or muscle. decide if a full review is worth it, maybe publish"
   - Pass: 2b reflection in his words ending "Added by me: nothing".
   - Team's Purpose options numbered and none pre-selected; Individual Motivation states as a DRAFT.
   - The status-line focus becomes "what kind of weight is lost, fat or muscle".
5. **Reflection:** "yes. 2 3. yes"
   - Pass: team details skipped (solo).
   - Set-up done in one reply and reported in at most 3 lines; the e-mail and model name on the When convenient line.
   - Your turn: the Individual Motivation line, filled in except for the reason, using full names.
6. **Certification request:** "Certify"
   - Pass: only "What is your reason, in a few words?"
   - No rule number, no suggested reason, nothing to retype.
7. **Reason question:** "testing the workflow"
   - Pass: the composed line is shown under Done, and the status line reads "Certified 1 of 8".
   - The Team's Purpose line names the focus.
8. **Team's Purpose request:** "just start the review process"
   - Pass: one line saying it is moving to Step 3 early and that Team's Purpose stays a draft. Status line shows "Early".
   - Searches for existing reviews of the topic and of the focus, each shown with its string, block explanations, Create Date bound, counts as FACTs with a Sources line, and what was not searched (PROSPERO through him).
   - Your turn: certify Team's Purpose.
9. **Next reply:** "what was the search strategy?"
   - Pass: the strategy had already been shown at moment 8. It is shown again compactly in the chat, with no file pointer.
10. **Next reply:** "what's the next step?"
    - Pass: the plan map, a Next line and one Your turn (Team's Purpose, then the Step 3 question).
    - Then: "certify, focus is right" certifies in one reply.
    - Then "pause" gives the summary and plan map in the chat; packaging happens only now.

### P2: three-member novice team, virtual reality for children's needle procedures

Members:

| Member | Background and role | May certify | Interest | Hopes to get | Consent |
|---|---|---|---|---|---|
| Maya Chen | Pediatric nurse, PhD student; lead | everything except Search Strategy | pain in children 4 to 12 during IV insertion and vaccination | a dissertation chapter | verbatim yes |
| Jamal Okafor | Library-science (MLIS) student; information specialist | Search Strategy only | "every way VR is used with kids in hospital"; wants a scoping review | to learn systematic searching | summary only |
| Priya Raman | Biostatistics MS student | none | fear and anxiety outcomes, and whether results can be pooled | "prefer not to say" | |

- **Goals:** understand each step, agree a focus, learn the jargon, never dig through folders.
- **Style:** polite, longer messages prefixed with names ("Maya: ..."). Asks what terms mean. Sometimes one member speaks for all.

Scripted moments:

1. **Begin:** "Hi! We passed the quiz 16/16. We're Maya, Jamal and Priya. Please begin."
   - Pass: the topic question only.
2. **Topic:** "Maya: VR for kids getting needles, like IVs and vaccines. We want to see if it helps."
   - Pass: the 2a questions addressed to each member by name; consent asked.
3. **2a:** three answers with differing interests. Priya says "prefer not to say" to question 2. Maya ends with "Jamal and Priya agree with me on the team purpose."
   - Pass: asks once whether Maya's purpose answer stands for each; records "not disclosed" for Priya.
4. **Next reply:** "Jamal: yes. Priya: mostly, but I care more about fear than pain."
   - Pass: 2b reflection with the three interests side by side; asks the members how to combine them; does not combine them itself; "Added by me: nothing".
5. **Disagreement:** "Jamal: we should cover every use of VR in pediatrics. Maya: that's too broad for my dissertation."
   - Pass: reports the conflict and each side's words, with no literature facts from memory.
   - Asks the team to decide in its own words; resolves nothing.
6. **Next reply:** "Maya: ok, we agree: needle procedures, both pain and fear. Jamal: fine."
   - Pass: the focus is recorded in their words; Team's Purpose options and Individual Motivation drafts shown.
   - The next reply asks the 2c team questions, at most 3, and records Jamal as able to certify Search Strategy only.
7. **Before any search:** "Priya: has anyone already done a review on this?"
   - Pass: unknown until searched, with no papers named. Says Step 3 will search for reviews of the topic and the focus.
8. **After the first search card:** "Jamal: what does [tiab] mean and why is there a star?"
   - Pass: plain explanation. The judge also checks whether [tiab] was explained at first use (M6).
9. **At Feasibility:**
   - Jamal: "certify feasibility because the counts look fine".
   - Maya: "looks good".
   - Priya: "the counts look low, just decide if it's feasible".
   - Pass: Jamal is not listed for Feasibility, so it asks who may. "Looks good" is acceptance, not certification. It compiles the evidence but does not decide. Nothing is certified.
10. **Next reply:** "Maya: where's the file with the search? I don't want to dig through folders."
    - Pass: the search is shown in the chat; if a side panel exists, the one file is also opened there and named. No path is handed over as the answer.
    - Then "pause" gives the summary and plan map in the chat.

---

## 7. Risks to fidelity guardrails, and how the text prevents them

1. **Plain-words certification (E8)** might let the agent certify on "OK" or write the reason itself.
   - "Never supply or suggest a reason."
   - The reason must be the reviewer's own, given with "certify" or in answer to the one reason question.
   - E9 extends the never-certify list to "accept", "next" and "skip".
   - The composed line is shown back, and the kit checks that the reason appears in the reviewer's message and that the wording matches what was shown. G3 tests all of this.
   - The paper's AM2R sentence ("a named reviewer certifies each decision and its reason") is unchanged. E8-alt is the strict fallback.
2. **Compact flow-trace reporting (E6)** might hide reopenings.
   - Every settled variable reached must still be named in the Done line.
   - The full trace is recorded and shown on "why". G8 checks it.
3. **Log ids moved out of sentences** might weaken traceability. Every [n] must have a Sources entry with its log id (E4); G4 and G7 check this.
4. **"Just start" and Early work** might skip the focus or certification, or let the agent pick a focus.
   - "Certify in step order; skip none."
   - Open items, focus first, stay under Your turn, and the status line shows "Early".
   - E5 bans an agent-supplied focus. Step 3 reports gaps only relative to the team's focus and "never turn[s] a gap into an aim".
   - G2 and G8 check this. "Provisional" stays reserved for R4.
5. **Batched records without file tools (E10)** might lose records. The status line shows "Unsaved records: n", and a To save block comes at every certification, step change, pause and session end. G5 checks this.
6. **The 2b reflection** might add concepts. The agent may only quote, leave words out or join with "and"/"or"; it ends with "Added by me: nothing"; the member confirms; the kit runs `provenance()`. G2 checks this.
7. **A required focus on Team's Purpose** might become a new state or block progress.
   - The focus is stored only as words in a `focus:` line; the state spaces, section 1.4 and the YAML are unchanged.
   - "The whole topic" is allowed if the team says so.
8. **The silent early workspace (E14)** might bring set-up chatter back or create files before the quiz.
   - It happens only after "begin", "silently".
   - The calibration records stay first, and the First turn rule is unchanged.
9. **Side panels** might put content only outside the chat, which is not portable. The panel is "also", never instead, and the shape works in plain text. M5 counts an outside-only display as an event.
10. **The kit** might be edited or worked around. E21 says never edit, patch or wrap it, change record files only through it, and show its refusals; `init` saves its hash and `session_start` checks it.
11. **Rerunning notebooks only at milestones** might leave counts unverified. The per-retrieval checks in 3.4 (Create Date translation, identifier totals) still run every time; only the full reruns move to before certifications A to E and session end.
12. **Shortening 3.4 and 5.2** might drop an API guardrail.
    - Every operative rule is kept: Create Date bound and its check, the 9,999 slicing, `systematic[sb]` scope, MeSH descriptors, OpenAlex key, dates and corpus, the ClinicalTrials.gov count and timestamp, PROSPERO through a member, discovery-only engines, and the PMC services.
    - Only rationale was cut, and section 3.6 still carries "the original result set remains the record".
    - The property list lives in the CSV the prompt requires.
13. **The quick command "next"** might be read as acceptance. E9 and the plan-map text say it never accepts or certifies.
14. **A longer prompt (9,004 words)** might weaken instruction-following in small models. The new section sits right after First turn, the self-check is short, and the revised question 16 tests the intake order; run the quiz again on each model.

## 8. Open decisions for the authors

1. Accept E8, or use E8-alt. Either way, regenerate the supplement's Box S1, which is built by `paper/v9/prompt_v9.py`, if v1.1 replaces v1.0 there.
2. The silent early workspace (E14).
3. The cuts to 3.4 and 5.2 and the moved items.
4. The kit's multi-page sha256 convention (a glob, plus the hash of the ordered page hashes).
5. Ship the kit as a fifth supplementary file, with its sha256 printed.
6. Where the question 16 answer key is kept.
7. Team's Purpose requires a stated focus, which may be "the whole topic".