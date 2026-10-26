# Diagnosis of the STIR-L4 prompt v1.0 Codex/GPT test (SGLT2 run), with baseline metrics and ranked fixes

Sources read in full:
- prompt/versions/STIR-L4_prompt_v1.0.txt
- eval/transcripts/2026-10-19_codex-gpt_prompt-v1.0-early_sglt2.md

No files were created or changed. Line numbers refer to the current v1.0 file. "Current v1.0" says whether that file has already fixed each friction point.

## A. Friction points, turn by turn

**T1. Pre-planning ritual, and the step map is never shown**
- **Quote:** User: "Follow the uploaded ... prompt's first-turn instructions only ... Do not begin planning."
- **What the user experienced:** The tester had to write a steering instruction, paste and grade the quiz (T2), then send "you are calibrated, please begin" (T3). That is three user turns before any planning. Nothing tells the team what the 12 steps are or how long this will take.
- **Prompt lines:**
  - L5: "(3) wait ... do not create files, run searches or start planning until the team tells you the quiz result and asks you to begin."
  - L152 (Step 0).
  - No line asks for an orientation to the steps.
- **Current v1.0:** Still open.

**T3. A nine-item intake form, written in codes**
- **Quote:** "who may certify IM, TP, NR, RO, FE, RQ, SS and ME, and who is supplying these intake answers. Which literature sources ... what deadline and resources ... institutional privacy or LLM rules ... decisions already made ... (options: Save paraphrased notes / ...)"
- **What the user experienced:** A form, not a conversation. The codes were unreadable, which led to the complaint in T4. The agent never asked the topic; the user had volunteered one.
- **Prompt lines:**
  - L154 ordering. This is now fixed: purpose and motivation come before logistics.
  - L154 still says "ask the remaining intake questions, at most three per turn: the members, their roles and which decisions each may certify; the sources ...; deadlines and resources; decisions already made ...; and any institutional rules." The limit counts question groups, not items, so three "questions" can carry nine asks.
  - The prompt itself is code-first, which primes the model to write codes:
    - L11: "IM and TP are motives; NR, RO, FE, RQ, SS and ME are planning decisions"
    - L19 to L28 define each element by its code.
    - Step headings use codes, for example L154 "(IM, TP)" and L155 "(NR; notebooks/01_need_A.ipynb)".
  - R14 (L96) bans codes in prose, but it comes last among the rules.
- **Current v1.0:** Partly fixed (ordering, R14). The item-stuffing and the code priming remain.

**T4. A set-up wall that exposes the theory's internals, plus three more form questions**
- **Quote:** "the model has 10 elements, 27 flows and 47 loops, with Feasibility on 40 loops ... what contact email may I use ...? ... Who may certify Individual Motivation and Team's Purpose ...? ... what model name/version and settings ...?"
- **What the user experienced:**
  - Infrastructure before any planning substance.
  - The agent asked who may certify, although the user had said "I will play every role."
- **Prompt lines:**
  - L144: "check by code that the file reproduces the facts in section 1.3"
  - L110: "Set Entrez.email (required by NCBI)"
  - L105: "Record the LLM running each session ... read by a team member from the interface"
  - L87: "The reviewer must be listed in plan/team.yaml as able to certify that decision; otherwise ask who may."
  - No line says to do the set-up quietly, or to ask a logistics question only when it is needed.
- **Current v1.0:** Still open.

**T5. Smoke-test details, then Individual Motivation offered as an eight-option menu**
- **Quote:** "OpenAlex returned the first page but rejected pagination without an API key ... what do you seek from the exercise? You may name several: learning the review process, developing skills, academic activity, career advancement ..."
- **What the user experienced:**
  - Technical status that a clinician cannot act on.
  - Individual Motivation "felt like additional questions." The user picked two menu items, and no interest in the research area was ever captured.
- **Prompt lines:**
  - L146: "run one trivial query against each source ... fetch a second page as well ... and report which sources work"
  - L19: the IM state space (career-type states only).
  - L72: "Individual Motivation | What each member seeks; conflicts with the agreed purpose"
  - L154: "ask each member ... what they want from the review and what expertise they bring". Nothing asks about the member's interest in the topic, focus or question.
  - R5 (L87): "Offer options from the variable's state space where it applies"
- **Current v1.0:** The menu is partly fixed: options now come after the member's own words. The skipped research focus is still open.

**T6. A log id in prose, and a syntax string to type**
- **Quote:** "(your judgment, L000035)? STIR-L4 requires your own reason and this exact format ... `CERTIFY IM | ... | reason: <your reason> | Uday Singh, Reviewer A (lead reviewer)`"
- **What the user experienced:** Machinery and a typing burden.
- **Prompt lines:**
  - R2 (L84): "FACT (retrieved; cite the log id)". The model extended this to judgments.
  - R5 (L87): "A certification counts only when a named reviewer writes: CERTIFY <element> | <decision> | reason: <reason> | <name>, <role>."
  - R14 (L96): "A reviewer may name the element or give its code in a CERTIFY line"
- **Current v1.0:** Still open.

**T7. Refusal with rule-lawyering**
- **Quote:** User: "Certify". Assistant: "rule R5 of your STIR-L4 prompt requires ... Individual Motivation therefore remains proposed ... send the complete statement required by STIR-L4 rule R5"
- **What the user experienced:** Rebuffed. The rule number was quoted twice.
- **Prompt lines:**
  - R5 (L87): "Treat 'OK' or 'looks good' as acceptance of a draft at most, never as certification"
  - No line says to ask for the missing reason in plain words, or never to cite rule numbers. The prompt cross-references rules by number throughout ("(R5)", "(R4)", "(R8)"), and the model mirrors that.
- **Current v1.0:** Still open.

**T8. A third round trip for one certification, plus file links, a zip and git**
- **Quote:** "[summary](./outputs/.../session_summary.md) · [workspace ZIP](./outputs/stir-l4-setup.zip) ... a Git author identity remain outstanding ... because rule R5 requires your complete certification statement ... send this line to certify"
- **What the user experienced:** The agent had the reason and still did not finalize. The user was pointed to files, and git jargon appeared.
- **Prompt lines:**
  - R11 (L93): "package the workspace (for example as a zip file) ... End every session with a summary in reports/"
  - 3.1 (L103): "Put the workspace under version control (for example git) ... Commit whenever a decision is certified"
  - R5 (L87): the exact-line requirement.
- **Current v1.0:** Still open.

**T9. A flow-trace narration with no actionable content, then a nine-option Team's Purpose menu**
- **Quote:** "certified as L000050 ... flows 1 and 25, strong ... flow 23, strong ... flow 17, weak). It stopped at the unsettled variables; nothing was reopened."
- **What the user experienced:** Four flow numbers that end in "nothing happened," then a form. This is the only turn that clearly says both what just happened and what is next.
- **Prompt lines:**
  - R4 (L86): "After every new fact or answer, list the elements it changes and follow their outgoing flows step by step ... report the variables ... reached at each step, ordered by flow strength"
  - R14 (L96): "Refer to a flow by what it does as well as its number"
- **Current v1.0:** The menu-first ordering for Team's Purpose is fixed in L154. The flow-trace dump is still open.

**T10. A purpose drafted from menu picks, in the most jargon-dense turn**
- **Quote:** "JUDGMENT (L000064) ... DRAFT (L000065): To identify gaps ... FACT — flow review (L000066) ... (flows 5 and 24) ... (flows 2 and 3) ... (flow 4) ... required by rule R5: `CERTIFY TP | ...`"
- **What the user experienced:** "We never said our aim was to identify gaps" (T11).
- **Prompt lines:**
  - R2, R4 and R5 as above.
  - L154: "draft a purpose statement only from what members said and the states they chose". A purpose built purely from clicked states, with no research focus, is still permitted.
  - L73: "Team's Purpose | The agreed end; the decision the review must inform"
- **Current v1.0:** Partly fixed (no invented aims). Purposes without a focus remain possible.

**T11. A repeated correction, and the agent answered the wrong item**
- **Quote:** User: "3. Use full names ... instead of two-letter codes" (a repeat of T4). Assistant: "Uday, speaking first as the lead reviewer: what do you want from this review...?"
- **What the user experienced:** The user had to repeat the code correction. The request "ask the topic in one plain question" was answered with the purpose question.
- **Prompt lines:**
  - R14 (L96) has low salience.
  - No line makes the team's interaction corrections standing instructions for the session.
  - R3 (L85): "addressed to the member whose role fits"
- **Current v1.0:** Partly fixed (topic first in Step 1). There is still no standing-preference rule.

**T12. The topic changed with no reconciliation, and the same question was asked again**
- **Quote:** User: "role of SGLT2i in weight management in non diabeteic asian populations". Assistant: "Recorded your provisional topic ... Uday, as the lead reviewer, what do you want this review to help you decide or do?"
- **What the user experienced:**
  - The certified Individual Motivation, sources and "decisions already made" from the readmission topic were silently carried over to the SGLT2 topic.
  - The research focus within "weight management" was never asked.
- **Prompt lines:**
  - L153: "do not yet ask for the parts of the research question (for example the population, comparators, outcomes or eligibility criteria)". This suppresses the focus as well.
  - L153: "Record the answer as the provisional topic". There is no rule for a changed topic.
  - R4 traces elements only, and the topic is not an element.
  - R11 (L93): "without asking again for answers already recorded"
- **Current v1.0:** Still open.

**T13. A circular purpose was accepted, and the same question was asked a third time to a mock role**
- **Quote:** User: "do a systematic review on this topic." Assistant: "Recorded ... now speaking as the information specialist: what do you want from this review...?"
- **What the user experienced:** Interrogation by role-play, which led directly to T14.
- **Prompt lines:**
  - L154: "If an answer is vague ... ask what the team would do with that understanding". This was not applied, and there is no example of a circular answer.
  - L154: "Once the intake has named the other members, ask each of them the same, separately where possible"
  - R3 (L85).
  - Nothing covers one person playing several roles, or answering for several members at once.
- **Current v1.0:** Still open.

**T14. "Just start": the agent drifted off the step map in a long, silent, tool-heavy turn**
- **Quote:** User: "Just start with the review process please." Assistant: [three PubMed searches, ClinicalTrials.gov, OpenAlex, PMC full texts, report, notebook, zip] "saved the [initial scoping report](...) ... (L000107, L000111) ... The report contains the executed searches, candidate-study notes and a draft review framework ... [Download the complete working files](...zip)."
- **What the user experienced:**
  - No step was named. The turn actually mixed Step 3 (Need for a Review), Step 5 (Feasibility) and Step 8 (Search Strategy).
  - The search strings and the draft framework were hidden in a file.
  - The turn ended with no ask.
  - Team's Purpose was left as "do a systematic review," uncertified and unmentioned.
- **Prompt lines:**
  - L150: "Work through the steps in order". There is no guidance for a team that asks to skip or speed up, and no rule to announce the current position or a jump.
  - Steps 3, 5 and 8 say "Retrieve ..." (L155, L157) and "report their yields" (L160). None says to show the strings.
  - R11 (zip) and R2 (log ids).
- **Current v1.0:** Still open.

**T15. The search strategy was shown only after the user asked**
- **Quote:** User: "I see. What was the search strategy used?"
- **What the user experienced:** The content was good (strings and an explanation of [tiab] and [Mesh]) but late. The turn ends: "The complete executed PubMed strings and search notes are saved."
- **Prompt lines:**
  - L160: "Draft a Boolean string for each source. Run the strings you can run ... and report their yields"
  - Only Literature as a Tensor (LAT) has a show-the-query rule, at L188: "report feasibility counts and empty cells to the team with the queries that produced them"
- **Current v1.0:** Still open.

**T16. Need for a Review content not linked to its step; new searches not shown**
- **Quote:** User: "Please help me understand the current gaps in knowledge." Assistant: [targeted searches, not shown] "... DRAFT interpretation ... [table of five questions] ... I saved this updated assessment in the knowledge-gap note."
- **What the user experienced:** Substantive and engaging, the best moment of the run. But the agent never said this was Need for a Review (decision A) and never asked anyone to certify the need.
- **Prompt lines:**
  - L155: "Draft the case for a new review, an update or no review. A reviewer certifies it." The agent did not connect its output to this step.
  - No rule says that each substantive output must end with that step's decision.
- **Current v1.0:** Still open.

**T17. The research focus appeared only at the 17th turn, and the agent jumped to the Research Question**
- **Quote:** User: "Lets explore this question then: What kind of weight is lost?" Assistant: "DRAFT — a more precise Research Question would be ... The next substantive step is a study-by-outcome map"
- **What the user experienced:**
  - The focus was chosen from the agent's own gap list.
  - Team's Purpose and Individual Motivation were never updated to carry it.
  - The agent jumped to Step 6 while Need for a Review, Review Objective and Feasibility were all uncertified.
- **Prompt lines:**
  - L153 (focus suppressed).
  - L154 (purpose built from stated aims only).
  - R4 is not triggered, because the focus is not an element.
  - L150 (step order).
- **Current v1.0:** Still open.

**T18. Direct evidence that the step frame was missing**
- **Quote:** User: "Whats the next step?" Assistant: "... before finalizing eligibility criteria and beginning formal screening"
- **What the user experienced:** The answer did not say where the team was in STIR-L4 or which certifications were pending.
- **Prompt lines:** No turn-frame rule exists anywhere; L150 is the closest.
- **Current v1.0:** Still open.

**Root causes across the turns**
1. The prompt never says what a turn should look like (step, what happened, next, your turn).
2. Nothing elicits or carries the research focus between Step 1 and Step 6.
3. The prompt treats files as the place the team reads, with no rule that the chat is the reading surface.
4. Logging, provenance and flow-tracing rules are written so that their output lands in the chat.
5. Certification syntax is enforced by the user typing, not by the agent composing.
6. There is no fast-path behavior and no milestone discipline after "just start".

## B. Baseline metrics

The transcript is condensed: 32 "[...]" elisions, mostly in T14 to T18. Lengths and counts below are therefore lower bounds. The quiz turn (T2) is excluded, which leaves 17 assistant turns.

1. **Assistant turns that state both the current step and the next step: 2 of 17 (12%).**
   - The two turns are T1 and T9. Excluding the pre-planning turn T1, it is 1 of 15 (7%).
   - 0 of 17 name a step number or the position in the 12-step workflow.
   - 7 turns state only the current step: T3, T5, T6, T7, T8, T10, T11.
   - 3 turns state only the next step: T16, T17, T18 (T18 only because the user asked).
   - 5 turns state neither: T4, T12, T13, T14, T15.
2. **Questions per assistant turn: 0.94 question prompts (15/16) and 1.31 distinct asks (21/16).**
   - T3 carried 9 distinct asks in 3 grouped questions.
   - 3 option menus were shown (consent; Individual Motivation with 8 states; Team's Purpose with 9 options).
   - The last 5 turns (T14 to T18) contain 0 asks and 0 certification requests.
   - The purpose question was asked 3 times in a row (T11, T12, T13).
3. **Turns before the research topic was asked: never asked.**
   - The agent asked the topic 0 times. The user volunteered it at T3 and again at T12, in reply to a purpose question.
   - The research focus was first stated at T17, chosen from the agent's own gap list.
   - Under the current v1.0, the topic question comes at assistant turn 3 at the earliest (after the tool test and the quiz).
4. **Times the user was pointed to a file or zip instead of being shown the content: 7.**
   - 4 explicit links: T8 (session summary and zip) and T14 (scoping report and zip).
   - 3 "saved in a note" deferrals: T15, T16, T17.
   - 3 zips were built (T8, T9, T14).
   - At least one pointer hid content the user then had to ask for (the T14 strategy, asked for at T15).
5. **Internal identifiers in user-facing text: at least 32.**
   - 12 element codes: 8 in T3 prose and 4 in CERTIFY templates (T6, T7, T8, T10).
   - 7 log ids: T6, T9, three in T10, two in T14.
   - 4 rule numbers, all R5: two in T7, one in T8, one in T10.
   - 9 flow numbers: T9 and T10.
   - There are also 16 FACT/JUDGMENT/DRAFT labels. R2 requires these, so they are not counted as jargon.
   - Codes dropped to 0 only after the second correction.
6. **User corrections or complaints: 7 of 18 user turns (39%).**
   - 2 explicit correction messages (T4, T11) carrying 4 corrections. One of them, codes, had to be repeated.
   - 5 implicit friction turns:
     - T7: a bare "Certify," which the agent refused.
     - T13: a circular purpose.
     - T14: "Just start."
     - T15: asking for the search strategy.
     - T18: asking for the next step.
   - The post-session feedback was "obtuse."
7. **Search strategies shown before being asked: no.**
   - 3 search rounds (T14, T16, T17). 0 were shown before running, 1 was shown on request (T15), and the T16 and T17 strategies were never shown.
8. **Median assistant turn length: 88 words visible (range 34 to 134).**
   - This is a lower bound. With the elided tables and code blocks, the true median is estimated at about 150 to 250 words.
   - The median user turn is 11 words, a ratio of at least 8 to 1.

**Other baselines worth tracking**
- Turns per certification: 4 for Individual Motivation (T6 to T9). Team's Purpose was never certified.
- Variables certified in the session: 1 of 8 (no decision A to E).
- Turns until the first literature fact: 14, and only after the user overrode the flow.
- Turns with tool work: 8 of 17. In 4 of the first 8 planning turns, set-up, tests, git or zip took up most of the turn (T4, T5, T8, T9).
- Unannounced step jumps: 2 (T14 and T17).
- Unreconciled topic changes: 1 (T12).

## C. The 10 highest-impact fixes, ranked

None of these changes the elements, flows, state spaces, decisions A to E, AM2R or the rules' substance.

1. **A turn frame on every turn.** (Targets T18, T14 and the "obtuse" complaint.)
   - Open each planning turn with: "Step n of 12 · step name — what just happened, in one sentence."
   - Close it with: "Next: ... · Your turn: the one thing to answer, edit or certify."
   - Show a progress board at every step change, at every certification, when asked, and about every 5 turns. It lists the eight decisions with plain-word status, the two stocks by their contents, and counts such as decisions certified out of 8 and searches run.
   - Show the 12-step map in 5 or 6 lines in the first planning turn.
   - Supporting code renders the board from plan.yaml. Without tools, the agent keeps the board in the chat.
   - Where: a new section 0 before L7, and amend L150.
   - Target: 12% of turns framed now, 100% after.
2. **Carry the research focus from topic to motivation to purpose.** (Targets T5, T10, T12, T17 and the tester's request.)
   - Step 1 (L153): after the topic, ask one follow-up: "Within that topic, what do you most want to find out?" Keep the ban on population, comparator and outcome questions, but explicitly allow the focus question.
   - Step 2 and the "asked of the team" column in L72 and L73:
     - Individual Motivation asks what draws each member to the topic, which part or question they most want answered, what they want from the review, and what they bring. Their words are recorded, and any state mapping is a draft only.
     - Team's Purpose asks for the agreed research focus and the decision it informs. The purpose statement must name the focus.
   - Different focuses across members are reported as a conflict under R9 and flow 2.
   - Restate topic and focus at every step change.
   - If the topic or focus changes, list the earlier answers that depended on it and ask which still hold.
3. **The chat is where the team reads; files are the record.** (Targets T8, T14 to T17.)
   - Show every draft, string, count, table and summary in the chat, in short form, with "say more" for the full version.
   - Never ask the team to open a file or zip to see content. Close a turn with at most one line: "Saved to the plan and log."
   - If the interface has a side panel or canvas (the Codex app, ChatGPT canvas, Claude artifacts), open the one file under discussion there.
   - Package a zip only at session end, and only if files may not persist.
   - Amend R11 (L93) so the session summary is also shown in the chat.
   - Target: 7 file pointers now, 0 after.
4. **A search card for every search.** (Targets T14 to T17 and the tester's request.)
   - Whenever any search runs (Steps 3, 5, 6, 8, or a targeted search), show: the source, its purpose in plain words, the exact string in a code block, one line per concept block (MeSH or free text, and what it captures), the filters and the date bound.
   - After it runs, show the count read by code and one sentence on what it means.
   - A scoping search can run in the same turn without waiting for approval, but never unseen.
   - Supporting code prints the card from the saved log record.
   - Where: add to L155, L157, L160 and 3.4.
   - Target: 0 of 3 searches shown before running now, 3 of 3 after.
5. **A fast path with milestone discipline.** (Targets T14 to T18.)
   - When the team says "just start," skip or speed up, say in one line which step you are jumping to and what stays open (for example, "Team's Purpose stays proposed"). Do that step, and end with that step's decision ask.
   - Never deliver a step's substantive output without its ask: certify, edit, go/narrow/broaden/defer.
   - When a team question belongs to a step (for example, gaps belong to Need for a Review), name that step and treat the answer as its draft.
   - Return to open items at the next natural checkpoint.
   - Target: 2 unannounced jumps now, 0 after; no run of ask-free turns.
6. **A plain voice, placed first among the rules.** (Targets T3, T6 to T10.)
   - Move R14 to the top and extend it: no element codes (including in certification lines), log ids, rule numbers, flow numbers, paths, notebook names, git or package details in the chat.
   - State what a rule requires in plain words, never its number.
   - Cite a fact by source and date in the text ("PubMed, searched 19 Oct 2026"), and put log ids only in an optional last "Record:" line. This keeps R2's traceability.
   - Describe an effect, not a flow number ("this may change Feasibility").
   - Treat any interaction correction from the team as a standing instruction for the session, and log it as a note.
   - Target: at least 32 identifiers now, 0 after; 1 repeated correction now, 0 after.
7. **Certification in one turn.** (Targets T6 to T8.)
   - The agent composes the full certification in plain words with the decision, name and role already filled in, for example: "Certify Individual Motivation: ... — your reason: ___ (Uday Singh, lead reviewer)".
   - Accept any reply from that reviewer that says certify and gives a reason. Log it in the CERTIFY format and echo it once.
   - If the reason is missing, ask only "What is your reason, in a few words?"
   - "OK" or a bare "certify" still does not count, and the named reviewer, the reason and the log are all kept.
   - Batch Individual Motivation and Team's Purpose when the same reviewer certifies both.
   - Where: R5 (L87).
   - Target: 4 turns per certification now, 1 after.
8. **Question discipline.** (Targets T3 to T5, T9, T12, T13.)
   - One focused ask per turn, with the open question first. Show state options only after the member's own words or on request.
   - Count every item in a logistics turn, at most 3.
   - Ask logistics just in time: the contact email at the first PubMed search, the model name at set-up, certification rights at the first certification.
   - Never re-ask an answered question. Probe a circular answer once ("a systematic review to do what?").
   - When one person speaks for several roles, or members are present together, ask once: "Answer for each person, or say 'same for all'."
   - Where: L154, R3 (L85), R5 (L87), 3.2 and 3.4.
   - Target: at most 9 asks per turn now, 3 or fewer after; 3 repeated questions now, 0 after.
9. **Quiet machinery.** (Targets T4, T5, T8 to T10.)
   - Do the set-up in one turn, using defaults where possible, and report it in at most 3 lines: what works, and what needs a member.
   - Do not report loop counts, package versions, pagination or git identity unless something blocks the team.
   - Run the R4 flow trace in code after every answer and log it. In the chat, say only "Nothing already settled is affected," or name the specific possible reopening and ask whether to reopen.
   - Where: L86 and sections 3.1 to 3.9.
   - Target: 4 turns dominated by infrastructure in the first 8 planning turns now, 1 or fewer after; 9 flow numbers now, 0 after.
10. **Answer first, short turns.** (Targets the whole run.)
    - Lead with the result in 1 or 2 sentences.
    - Keep turns to about 150 words, or a table plus about 100 words when showing evidence. Offer the details on request.
    - Do the first-turn tool test and give the orientation in the same turn as the step map.
    - Target: a visible median of 88 words now (about 150 to 250 estimated actual), 150 or fewer after, with exactly one "Your turn" line.