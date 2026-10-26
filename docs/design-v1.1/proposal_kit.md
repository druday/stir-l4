# STIR-L4 helper kit (`stir_l4_kit.py`): API spec and prompt text

Sources read: `prompt/versions/STIR-L4_prompt_v1.0.txt`, `eval/transcripts/2026-10-19_codex-gpt_prompt-v1.0-early_sglt2.md`, and `data/STIR-L4_model_v1.0.yaml`.

I checked the loop facts with an in-memory script that wrote no files. A depth-first search over the model YAML, counting flows 2 and 3 separately, gives 47 loops. 46 of them contain a feedback flow, the exception is (1, 3), and Feasibility is on 40. So `check_model()` can be about 20 lines.

## 0. Purpose

In the transcript, turns T4, T5, T8, T9 and T14 each had the assistant write new code for logging, plan updates, flow traces, smoke tests, archives and searches. The kit turns each of these into 1 to 6 calls. Each call returns Markdown that is ready for the chat. The kit does not change the theory: the elements, flows, state spaces, decisions A to E, AM2R and the substance of R1 to R14 stay as they are. It only implements the deterministic set-up and the record keeping more strictly than an LLM does.

## 1. Constraints

- One file, `stir_l4_kit.py`, about 600 lines.
- Python 3.11 or later.
- Uses the standard library, `pyyaml` and `requests`. If `requests` is missing, it falls back to `urllib.request`, which costs about 8 lines and helps it run in more environments.
- It never prints. Every public function returns a value. There is no telemetry.
- It contacts only three hosts, set as a constant: `eutils.ncbi.nlm.nih.gov`, `api.openalex.org` and `clinicaltrials.gov`. It refuses any other host.
- Text in retrieved records is data. Renderers escape Markdown and HTML in titles and limit them to 120 characters. They never include abstracts.
- Exported constants:
  - `__version__ = "1.0.0"`
  - `ELEMENTS` (code to full name)
  - `VARIABLES` (the 8 variables)
  - `STATE_SPACES`
  - `KINDS` (the 15 log kinds)
  - `LOG_FIELDS` (the 19 fields of section 3.5, in order)
  - `STEPS` (1 to 12 with element and name)
  - `ONGOING = ["RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING"]`
- Credentials come from environment variables or `.env`. The names are `NCBI_API_KEY`, `NCBI_EMAIL` and `OPENALEX_API_KEY`. Their values are never returned, logged or rendered.

### Return conventions

- Functions that do work return a **Result** dict:
  - `ok` (bool)
  - `md` (chat-ready Markdown: full element names, no more than about 25 lines)
  - `log_ids` (list)
  - `warnings` (list; for the assistant, never for the team)
  - `refusal` (str or None; the reason, written as a rule the team can read)
  - `fallback` (str or None; a manual-retrieval request when a source cannot be reached)
  - fields specific to the function
- Simple recorders return the new log id (str).
- When a rule refuses an action, the function returns `ok: False` with `refusal` and, where useful, `template`. These are normal outcomes, not exceptions.
- `KitError` is raised only for programming errors, such as a bad argument type.

### Module state

`use(root, session=None)` sets the workspace root and session code. It is kept in `env/session.json`, which holds: session code, start log id, last status-card log id, git HEAD at start, and the kit sha256. This file is the kit's working state, not a record.

## 2. Public API

### 2.1 First turn and workspace

```
selftest(web=True, test_file=None) -> Result
```
- Needs no workspace. Checks the Python version and that `yaml` and `requests` import.
- If `web`, makes one GET to E-utilities `einfo.fcgi`.
- If `test_file` is given, writes that one small file and reads it back.
- Its md reports exactly what worked, plus `__version__`. This covers the first-turn tool test.

```
init(root="stir-l4-workspace", *, session="S1", calibration: dict,
     prompt="STIR-L4_prompt_v1.0.txt", model="STIR-L4_model_v1.0.yaml",
     core_properties="STIR-L4_core_properties_v1.0.csv", git=True) -> Result
```
- `calibration = {"answers": str, "score": str, "graded_by": str, "time_utc": str|None}`. It is required.
- Creates the 12 folders of section 3.1: `env/ log/ plan/ notes/ data/raw/ data/derived/ notebooks/ pao/ lat/ red/ protocol/ reports/`.
- Adds any missing lines to `.gitignore`: `.env`, `.env.*`, `data/raw/text/`, `__pycache__/`.
- Runs `git init` if git exists; otherwise adds a warning.
- Copies files unchanged, recording the sha256 of each:
  - prompt to `env/prompt_v1.0.txt`
  - model to `plan/STIR-L4_model_v1.0.yaml`
  - core properties to `lat/STIR-L4_core_properties_v1.0.csv`
  - the kit itself to `env/stir_l4_kit.py`
- Writes `env/requirements.lock` (pip freeze) and a skeleton `plan/plan.yaml` in the section 3.7 layout, with all variables `unsettled` and `provisional: false`.
- Writes a skeleton `plan/team.yaml` with `members: []`, `sources`, `deadlines`, `resources`, `rules` and `decisions_made`.
- Creates an empty `log/actions.jsonl`, writes `data/manifest.csv` with the header `path,sha256,log_id,bytes`, and writes `env/session.json`.
- Log order:
  1. L000001 `calibration` (actor agent, quiz answers)
  2. L000002 `calibration` (actor `graded_by`, score)
  3. one `note` per copied file, with its sha256
  4. the `check_model` computation
- Refuses to re-initialize a workspace whose log already has records.
- If the prompt file is missing, adds a warning telling the assistant to ask the team for it (section 3.2).

```
check_model() -> Result
```
- Computes from the saved YAML: 10 elements, 27 flows, feedback flows {2,7,13,15,17,20,21,23}, record flows {12,13,19,20}, 47 loops (simple cycles, parallel flows counted separately), 46 with feedback, Feasibility on 40, Methodology in {8,18,22,24,25,27} and out {23}.
- Compares these with the section 1.3 constants.
- Writes `data/derived/model_check.json` and logs a `computation`.
- Returns `mismatches` (an empty list when everything matches).

```
record_model(provider, model, *, version=None, settings=None, read_from) -> str
```
- Appends a session entry to `env/model.json`.
- `read_from` must be `"API response"` or `"interface, read by <member>"`. Without it, the function refuses, because section 3.2 forbids recording the model from memory.
- From then on, `log()` fills `model` automatically on records whose actor is `agent`.

```
smoke_test(sources=("pubmed","openalex","ctgov"), *, nb="00_setup") -> Result
```
- Runs one trivial query per source, plus page 2 for sources that page, and logs each.
- md is a table with columns Source | page 1 | page 2 | note.
- If there is no OpenAlex key, page 2 is skipped and the note says why.

```
session_start(session: str) -> Result
```
- This is R11 at the start of a later session.
- Reads `plan.yaml`, `team.yaml`, the latest `reports/*summary*.md` and the last 20 log records.
- Compares the sha256 of `env/stir_l4_kit.py` with the logged hash.
- Sets the id prefix if the session code differs from the last one and concurrent sessions are declared.
- md is the full status card plus "first unfinished step".

### 2.2 Log (append-only, section 3.5 schema)

```
log(kind, *, text=None, actor="agent", element=None, decision=None, reason=None,
    refers_to=None, derived_path=None, parameters=None, time_utc="now") -> str
```
- `kind` may only be `question`, `answer`, `draft`, `computation`, `note`, `consent` or `correction`. Every other kind has its own function. This keeps typed counts and unchecked certifications out of the log.
- There are no public `n_total`, `n_retrieved`, `raw_path` or `sha256` arguments.
- `time_utc`:
  - `"now"`: the system clock
  - `None`: null, for an answer given before the clock was available
  - an ISO 8601 string: accepted, after its format is checked, only when the actor is a member
- Validates:
  - `element` is one of the 13 codes
  - each `refers_to` id exists
  - `parameters` contains no value equal to a secret environment value and no e-mail pattern; secret values are replaced by `"<ENV_NAME>"`
- Writes exactly the 19 fields in order, filling the rest with nulls.
- Assigns the next sequential id by reading the last line under a lock file (`O_EXCL`, which also works on Windows). Ids are prefixed `S2-` and so on when prefixing is on.
- Returns the id.

Thin wrappers, each returning an id:

```
ask(to, text, *, element=None) -> str
```
Kind `question`; the text is stored as `"to <to>: <text>"` so metrics can find open questions.

```
answer(by, text, *, element=None, refers_to=None, verbatim=False, relayed_by=None) -> str
```
- Refuses `verbatim=True` unless `team.yaml` records verbatim consent for `by` (section 2.1).
- When `relayed_by` is given, the text is prefixed `"relayed by <name>: "` (R5).

```
consent(member, verbatim: bool) -> str
draft(element, text, *, uses=()) -> str
correct(log_id, text, *, by="agent") -> str
records(kind=None, element=None, since=None, last=None) -> list[dict]
```
- `draft`: every id in `uses` must be a `query`, `manual_retrieval` or `computation` record. These are the FACT ids that R2 requires a draft to cite.
- `correct`: logs kind `correction` with `refers_to=[log_id]`.

### 2.3 Plan and team

```
plan() -> dict
team() -> dict
```

```
set_topic(text, *, given_by, refers_to=None) -> str
```
Logs an `answer` and writes `plan.topic = {text, given_by, log_id}`. A refinement is a new record that refers to the earlier one.

```
add_member(name, role, *, can_certify: list[str], sources=(), consent="summary"|"verbatim"|"unknown", by=None) -> str
set_team(key, value, *, by) -> str
```
`set_team` keys: `sources`, `deadlines`, `resources`, `rules`, `decisions_made`.

```
record_motivation(member, *, states, interest, expertise=None, disclosed=True,
                  refers_to=None) -> Result
```
This implements the tester's request without changing the theory. Individual Motivation stays "what each member seeks" with the same state space; the member's interest in the area, focus or question is stored as text.

- `states` must come from the Individual Motivation state space or have the form `"other: ..."`.
- Refuses an empty `interest` unless `disclosed=False`. In that case it records `"not disclosed"`.
- Writes `team.yaml members[<member>].motivation = {states, interest, expertise, log_id}`.
- Recomputes plan IM:
  - `states` is the union of all members' confirmed states
  - `decision` has one line per member: `"<name>: <states>; interest: <interest>"`
  - `status` becomes `proposed` once at least one member has answered
- Runs `trace(["IM"])`.

```
propose(element, *, decision, accepted_by, states=None, focus=None, draft_id=None) -> Result
```
- This is how a draft enters the plan under R5. Refuses `accepted_by == "agent"`. Validates `states` against the state space.
- For Team's Purpose, refuses without `focus`, the research focus the members agreed on. It stores `decision = "Focus: <focus>. Purpose: <decision>"`.
- Sets `status: proposed` and logs an `answer` by `accepted_by` that refers to `draft_id`.
- Runs `trace([element])`. md: confirmation, trace and brief card.

```
reopen(element, *, agreed_by, reason, refers_to) -> Result
```
- R4: a decision is reopened only when the team agrees, so `agreed_by` is required. Logs kind `reopen`.
- Sets `status: reopened` and recomputes `provisional` for every variable. A variable is provisional if it is reachable from a reopened variable by the trace rule. This needs no extra plan fields.
- After registration, its md notes that recertification will be an amendment (R6).

```
register(registry, reg_id, version, *, by) -> str
commitment(by, text) -> str
```
- `register`: kind `registration`; writes `plan.registration`.
- `commitment`: kind `commitment` (Step 12).

Statuses change only through `propose`, `certify` and `reopen`; there is no public `set_status`. Allowed transitions:
- unsettled or reopened to proposed
- unsettled, proposed or reopened to certified, or to amended after registration
- certified or amended to reopened

### 2.4 Certification

```
certify(line: str) -> Result
```
Parses `^CERTIFY\s+(?P<el>[^|]+)\|\s*(?P<decision>[^|]+)\|\s*reason:\s*(?P<reason>[^|]+)\|\s*(?P<name>[^,|]+),\s*(?P<role>.+)$`.

Refuses, with a one-line reason and a template from `certify_template`, when:
- the line does not match. The reason then says that "OK" or "Certify" counts at most as acceptance of a draft.
- the element is not a known code or full name. PAO, LAT and RED are also accepted for Step 7.
- the reason is empty, a `<placeholder>`, or the same as the decision.
- the name is not in `team.yaml` with that element in `can_certify`. The refusal asks who may certify.
- the status does not allow it.

On success:
- Logs kind `certification`, or `amendment` if `plan.registration` exists and the element was certified before. The record has actor = name, `decision`, `reason`, `text` = the line verbatim, and `refers_to` = the earlier certification and the latest accepted draft.
- Updates the plan: `status`, `certified_by: "name, role"`, `certified_at`, `reason`, `decision`, `log_ids`. Recomputes `provisional`.
- Calls `commit(f"Certify {code} ({id})")` (section 3.1).
- Runs `trace([element], because=id)`.
- After an amendment, adds a pending "submit the amendment to the registry" item to the status card (R6).
- md: confirmation, trace, brief card.

```
certify_template(element, reviewer=None) -> str
```
Returns:

`CERTIFY <Full Name> | <decision from plan or latest accepted draft> | reason: <your reason> | <eligible name>, <role>`

Only the reason is left for the reviewer to fill in. This removes the T6 to T9 loop in the transcript, where it took four turns to certify Individual Motivation.

```
commit(message, log_id=None) -> str|None
```
- Runs `check_secrets()` first and refuses if anything is found.
- Runs `git add -A` and commits.
- Uses the configured git identity if there is one; otherwise `-c user.name="STIR-L4 assistant" -c user.email=stir-l4@localhost`. It never asks the team for an identity and never stores a member's e-mail.
- Returns the short hash, or None if there is no git.

```
check_secrets() -> Result
```
Scans files that are not git-ignored for the values of the secret environment variables and the contact e-mail. Returns the hits, which are paths only and never values.

### 2.5 Flows

```
flows_from(element) -> list[dict]
```
Each entry has `id`, `to`, `type`, `class`, `strength` and `meaning`.

```
trace(changed: list[str], *, because=None) -> Result
```
A breadth-first search over the saved model YAML:
- Step 0 is `changed`, marked as visited.
- At each step, follow every outgoing flow of the frontier to elements not yet visited. If two flows reach the same element in one step, keep the strongest and note the others. Order results strong, moderate, weak, then by flow id.
- A stock target (Literature Universe or Review Universe) is listed under "stock contents may change" and expanded further.
- An `unsettled` variable is listed as "not yet settled: stopped" and not expanded.
- Any other variable is a candidate reopening and is expanded.

It writes `data/derived/trace_<id>.json`, logs a `computation` (`refers_to=[because]`), and returns `steps`, `candidates`, `stopped_at`, `stocks` and `md`. The md uses full names and gives each flow's meaning with its number, for example "the included studies feed back to Feasibility (flow 21, strong)". It ends: "Possible reopenings, not reopened until the team agrees: ...".

### 2.6 Raw files, manifest, reproducibility and notebooks

- Internal `_save_pages(log_id, source, endpoint, pages: list[bytes], ext)`:
  - writes `data/raw/<log id>_<source>_<endpoint>_<page>.<ext>` and never overwrites
  - appends one manifest row per page
  - for one page, the log `raw_path` is that file and `sha256` is its hash
  - for several pages, `raw_path` is the glob `data/raw/<id>_<source>_<endpoint>_*.<ext>` and `sha256` is the hash of the page hashes joined by newlines, in order. This is an implementation convention that the authors need to confirm; see open decision 1.

```
verify(log_ids=None) -> Result
```
- For every record that has `raw_path`, checks that the files exist and that the hashes match the log and the manifest.
- Recomputes `n_total` and `n_retrieved` from the raw files with the source's own parser and reports any mismatch.
- Logs a `computation`. md is a table.
- This is the analysis cell that reproduces every reported count with `RETRIEVE=False` (section 3.6).

Notebooks: every retrieval function takes `nb="<notebook>"`, for example `"01_need_A"`.
- The function appends its own call to `notebooks/<nb>.ipynb` as a cell guarded by `if RETRIEVE:`.
- If the notebook does not exist, it is first created with the header cell `import stir_l4_kit as k; k.use("..."); RETRIEVE = False` and a final `k.verify()` cell.
- Notebooks are built as a by-product of the calls; the assistant does not write them by hand.

### 2.7 PubMed (E-utilities through requests; replaces the Biopython wording in section 3.4)

```
pubmed_search(term, *, element, purpose: "reviews"|"primary"|"scoping",
              search_date=None, mindate="1800/01/01", retmax=0, ids=False, nb=None) -> Result
```
- Throttles to 3 requests per second, or 10 with a key.
- Sends `db=pubmed`, `term`, `datetype=crdt`, `mindate`, `maxdate=search_date` (default: UTC today, `YYYY/MM/DD`), `retmode=json`, `tool=stir_l4_kit`, and `email` and `api_key` from the environment. The last two are recorded as `"<NCBI_EMAIL>"` and `"<NCBI_API_KEY>"`.
- Filter rule:
  - refuses `systematic[sb]` when `element` is FE or SS, or `purpose == "primary"`
  - refuses `element == "NR"` with `purpose == "reviews"` when the term lacks `systematic[sb]`
- Saves the raw JSON and reads `esearchresult.count`, `idlist` and `querytranslation`.
- Checks the translation for `"<mindate>"[Date - Create] : "<maxdate>"[Date - Create]`. If the check fails, it logs the query with `n_total: null` and the text "count not logged: Create Date bound missing", and returns `ok: False`.
- With `ids=True` and a count above 9,999, it splits the Create Date range into slices below 9,999. Each slice is logged with `refers_to` the parent. It writes `data/derived/<id>_pmids.txt` and checks that the union of identifiers equals Count; otherwise it adds a warning and marks the record unresolved.
- The log `date_range` is `{"datetype":"crdt","min":..., "max":...}`.
- Returns `count`, `n_retrieved`, `translation`, `raw_path`, `ids` and md, for example: "PubMed, searched 2026-10-24, Create Date 1800/01/01 to 2026/10/24 (checked): N records (L...)".

```
pubmed_fetch(pmids, *, element, nb=None, batch=200) -> Result
```
- Fetches XML with `efetch`, using POST for long lists, and saves each batch as a page.
- `n_retrieved` is the number of `<PubmedArticle>` elements.
- Returns `records` with `pmid`, `title`, `journal`, `year`, `doi` and `pub_types`, parsed with `xml.etree`. md is a short table with titles escaped.

```
mesh_lookup(term, *, nb=None) -> Result
```
- Runs `esearch db=mesh`, then `esummary db=mesh`.
- Keeps `ds_recordtype == descriptor` and returns `ui` (`ds_meshui`), name, entry terms, tree numbers and scope note.
- Lists supplementary concept records separately. Logs 2 records.

```
known_item_check(term, pmids=None, *, element="SS", search_date=None, nb=None) -> Result
```
- Runs `(<term>) AND (<p1>[pmid] OR ...)` with the same Create Date bound. If `pmids` is None, it reads `data/derived/known_items.csv`.
- Writes `data/derived/<id>_known_items.csv` with found and missed items. This is the Step 8 check, with no need to page through every identifier.

```
pubmed_web_query(term, search_date=None) -> str
```
Returns the string for a member to run on PubMed's website, with `AND 1800/01/01:<date>[crdt]` written in (section 3.4 manual route).

### 2.8 OpenAlex

```
openalex_works(search=None, *, element, filter=None, from_date=None, to_date=None,
               corpus="core", per_page=100, max_pages=1, nb=None) -> Result
```
- Calls `/works` with `filter` plus `from_publication_date` and `to_publication_date` (`YYYY-MM-DD`), `cursor=*`, then `meta.next_cursor`.
- Sends the key as `Authorization: Bearer`, recorded as `"<OPENALEX_API_KEY>"`. It never sends `mailto`.
- Records `corpus` in `parameters` (as section 3.4 names it).
- Without a key, it fetches only page 1 and warns.
- `n_total` is `meta.count` from page 1. `n_retrieved` is the number of results saved across pages.

### 2.9 ClinicalTrials.gov v2

```
ctgov_studies(cond=None, intr=None, *, element="FE", statuses=ONGOING,
              page_size=1000, max_pages=None, nb=None) -> Result
```
- Calls `/api/v2/studies` with `query.cond`, `query.intr`, `filter.overallStatus` as a comma-separated list, `countTotal=true`, `pageSize` and `pageToken=nextPageToken`.
- `n_total` is `totalCount`, read from page 1 only.
- Also calls `/api/v2/version` and saves and logs it, with the `dataTimestamp` in the text of the main record.
- Returns `n_total`, `n_retrieved`, `data_timestamp` and `studies` (NCT id, title, status). md is a table of at most 15 rows.

### 2.10 Manual retrievals (R8)

```
request_manual(member, source, query, *, element=None, instructions=None) -> Result
```
- Logs a `question` addressed to the member.
- md gives exact steps, what to save (the export or a screenshot, plus PubMed's search details if the source is PubMed), and the name to save it under in `data/raw/` with the run date.

```
ingest_manual(path, *, member, source, query, run_date, element, refers_to=None,
              n_total=None, translation=None) -> Result
```
- Copies the file unchanged to `data/raw/<id>_<source>_manual_1.<ext>`, records its sha256 and adds a manifest row.
- Counts `n_retrieved` by code where it can: RIS (`TY  -`), MEDLINE or nbib (`PMID-`), CSV rows, esearch JSON or XML.
- Accepts a member-read `n_total` only together with a saved file. This is the R7 rule that a count a member reports is unknown until it is saved.
- For PubMed, refuses to log the count unless `translation` contains the Create Date range.
- Logs kind `manual_retrieval` with the member as actor.

All retrieval functions return `fallback = request_manual(...)["md"]` instead of raising when the network is blocked. In a ChatGPT or Claude sandbox without internet access, every source therefore switches to R8 without breaking the turn.

### 2.11 Renderers and metrics

```
status(mode="brief"|"full"|"header", *, review=None, note=None, write=False, topic=None) -> str
```

**`"brief"`** goes at the end of every turn, in at most 6 lines:

```
**Where we are:** Step 3 of 12, Need for a Review (decision A). First unfinished step: 3.
**Research focus:** <Team's Purpose focus; else members' interests; else provisional topic> (<status>, <log id>)
**Just done:** <at most 3 lines built from records since the last card, each with its log id>
**Your turn:** <the open question or pending review, addressed by name; or `review`>
**Next:** <fixed phrase for the step and status, e.g. "Certification of the case for a review by Reviewer A">
**Progress:** 2 of 8 decisions certified · 1 question waiting · 1 manual search pending · 0 possible reopenings
```

- **`"header"`** is one line naming the step, for a turn that starts a new step.
- **`"full"`** is the plan map: Step | Element | Status | Decision (first 80 characters) | Certified by | Log. It adds stock lines ("Literature Universe: 6 logged queries; Review Universe: 0 included"), any reopened or provisional variables, and pending registry submissions.
- With `write=True`, the card is also written to `reports/status.md`, a regenerated view and not a record, so an interface can show it in a side panel.
- With no workspace yet (Steps 1 and 2), `status(topic=...)` renders a pre-set-up card that ends: "Nothing is saved yet; your answers stay in this chat until the set-up at the end of Step 2."
- If the team has jumped ahead, the card shows both the step being worked on and the first unfinished step, and says that the earlier steps are not yet settled.

Step derivation:
- Step 1 until there is a topic.
- Step 2 until Individual Motivation and Team's Purpose are certified.
- Steps 3 to 6 follow NR, RO, FE and RQ.
- Step 7 until PAO, LAT and RED certifications exist in the log.
- Step 8 follows SS.
- Step 9 while there are screening decisions and no commitment.
- Step 10 follows ME.
- Step 11 until registration.
- Step 12 until commitment.
- The earliest reopened variable takes priority over all of these.

```
metrics() -> dict
```
These metrics are what make the interaction better guided, and the brief card shows them.

| Metric | Meaning |
|---|---|
| `step_now`, `first_unfinished_step` | Where the team is working, and the first step not yet done |
| `certified` | k of 8 decisions |
| `step7_certified` | k of 3 |
| `open_questions` | `ask` records with no answer referring to them: who, what, id |
| `awaiting_certification` | proposed variables, each with its template |
| `manual_pending` | requests with no `ingest_manual` yet |
| `reopened`, `provisional` | lists |
| `focus_coverage` | members with a recorded interest out of members listed, plus whether Team's Purpose has a focus |
| `questions_since_last_card` | Step 2 intake allows at most three per turn; above 3 adds a warning for the assistant |
| `certifications_this_session`, `queries_this_session` | session totals |
| `last_verify` | result of the last `verify()` |

```
render_search(log_ids, *, title=None, explain: dict|None=None) -> str
run_strategy(lines: list[tuple[str, str]], *, source="pubmed", element, purpose,
             combine="AND", filters=None, label=None, search_date=None, nb=None) -> Result
```
`run_strategy` runs each concept line, then the combination, then the combination with filters. Each is logged as its own query that refers to a `note` holding the strategy spec, saved as `data/derived/strategy_<id>.json`. It returns `render_search` of those ids.

`render_search` produces:
- A title line: source, label or version, run date, and Create Date range "(checked in PubMed's translation)".
- A table: # | Concept | Search line (in code font, cut to 80 characters) | Records | Log. Counts are read from the log and formatted with thousands separators; they are never retyped.
- The full combined string in one code block, ready to copy.
- "How to read it": a glossary of the field tags and operators that actually appear in the string, built from a 15-entry dictionary: [mh]/[Mesh] (heading, includes narrower terms), [mh:noexp], [majr], [tiab], [ti], [pt], [sb], [crdt], [pmid], `*`, quotes, AND, OR, NOT, parentheses.
- `explain` entries per line, from the assistant, prefixed "DRAFT:".
- Filters applied, and whether the systematic-review filter was used.
- Known-item recall, if a `known_item_check` refers to these ids: "k of n known studies retrieved; missed: ...".
- "Not searched yet": `team.yaml` sources with no logged query, each with the member who can run it.

### 2.12 Session close

```
session_summary(*, next_questions: list[str], notes=None) -> Result
```
- Writes `reports/<YYYY-MM-DD>_<session>_summary.md` from the log since the session started. Sections: settled (certifications), reopened, still open (every variable not certified), next questions, and files changed (`git diff --name-only` since the HEAD at session start, or a list of paths written if there is no git).
- Logs a `note`. md is the same text, so the summary is shown in the chat (R11).

```
package(path=None) -> str
```
Zips the workspace without `.env`, `data/raw/text/` or anything in `.gitignore`, and returns the path. Used when files may not persist (R11).

Optional, if the line budget allows: `screen(record_id, decision, *, by, criterion, source_ids, passage=None)`. It refuses `by == "agent"` (R13), appends to `data/derived/screening.csv` and logs kind `screening_decision`.

## 3. Line budget (about 590; one-line docstrings; tests in a separate file with saved fixtures, not counted)

| Part | Lines |
|---|---|
| Header, constants, Result helper | 35 |
| Environment and `.env`, redaction, sha256, UTC time, YAML/JSON I/O, HTTP (allowlist, throttle, 3 retries on 429/5xx, `requests` or `urllib`) | 45 |
| `selftest`, `init`, `check_model` (loop enumeration about 20), `record_model`, `smoke_test` | 65 |
| Log and wrappers, lock, schema | 50 |
| Plan and team, motivations, propose, reopen, register, provisional | 55 |
| `certify`, template, `commit`, `check_secrets` | 45 |
| `flows_from`, `trace` with md | 30 |
| Pages, manifest, `verify`, notebook cells | 40 |
| PubMed (search with Create Date check and slicing, fetch, MeSH, known items, web query) | 75 |
| OpenAlex | 25 |
| ClinicalTrials.gov | 25 |
| Manual retrievals | 25 |
| `status`, `metrics`, `render_search` with glossary, `run_strategy` | 70 |
| `session_start`, `session_summary`, `package` | 25 |

## 4. v1.0 rules the kit enforces automatically

| Rule | How the kit enforces it |
|---|---|
| 3.5 log schema | Exactly 19 fields in order; sequential ids under a lock; session prefix; no edit or delete function; corrections are new records |
| R7 | Public `log()` takes no counts; `n_total` and `n_retrieved` are read from saved responses; a member-read count needs a saved file; renderers take every number from the log |
| R12 | Ids, times and hashes come from code |
| 3.4 PubMed | Create Date `mindate` and `maxdate` sent together; translation checked before a count is logged; 9,999 slicing with a sum check; `systematic[sb]` only at Need for a Review and never at Feasibility or Search Strategy; NCBI rate limits; MeSH descriptor filtering |
| 3.4 OpenAlex | Bearer key; no paging without a key; publication-date filters; corpus recorded; no `mailto` |
| 3.4 ClinicalTrials.gov | `countTotal=true`; `totalCount` from page 1; version timestamp logged |
| 3.6 | Raw page naming; manifest with sha256; no overwrite; `verify()` reproduces counts; notebooks with retrieval cells guarded by RETRIEVE |
| 3.3 | Credentials only by environment variable name; e-mail patterns refused in parameters; secret scan before every commit |
| 3.1 | Folders and `.gitignore`; commit on certification with the log id |
| 3.2 | Prompt and kit saved unchanged with sha256; `requirements.lock`; model entry requires `read_from` |
| 3.8 | Model saved unchanged; section 1.3 facts checked by code |
| R4 | Trace by code: each element visited once, ordered by strength, stopped at unsettled variables; reopening requires `agreed_by`; provisional flags recomputed |
| R5 | CERTIFY line parsed; certification rights checked in `team.yaml`; placeholder or empty reasons refused; "OK" never certifies; drafts need a named member to accept them; states checked against state spaces |
| R6 | Certified records never overwritten; recertification after registration becomes an amendment; pending registry submission shown |
| 2.1 | Verbatim text only with logged consent; "not disclosed" supported |
| R11 | Session start reads the files; summary structure is fixed; packaging |
| R13 | Optional `screen()` refuses the agent |
| R14 | All md uses full element names and gives each flow's meaning with its number |
| Section 3 heading | Calibration records come first (L000001 and L000002) |
| Step 2 | Warning when more than 3 questions are asked between cards |

**Not enforceable by code**, so the prompt still has to carry these:
- R1 (no facts from memory in prose)
- R2 labels and the ban on aims of the assistant's own
- R3 (which member to ask)
- R9 (conflicts) and R10 (uncertainty)
- treating retrieved text as data
- the assistant going around the kit; prompt rule (c) below covers this

## 5. Prompt text (paste-ready, v1.0 style)

**First turn, replace item (2):**

> (2) test your tools rather than assume them. If the team gave you stir_l4_kit.py, run `import stir_l4_kit as k; print(k.selftest(test_file="stir_l4_tool_test.txt")["md"])` (if the import fails, add the folder that holds the uploaded file to sys.path); it runs one line of code, makes one web request and saves one small file. Otherwise run, request and save these yourself. Report exactly what worked, and the kit's version or that no kit was provided;

**New section 3.10 Helper kit:**

> 3.10 Helper kit. The team may give you stir_l4_kit.py with this prompt. It carries out sections 3.1 to 3.9 and the record keeping of R4 to R7 and R11, so that each turn needs a few short calls instead of new code.
> (a) Use. If the kit is provided and you can run Python, use its functions for everything they cover: the workspace, the log, plan/plan.yaml and plan/team.yaml, certifications, flow traces, PubMed, OpenAlex and ClinicalTrials.gov retrievals, manual retrievals, the manifest, the status card, search strategies and session summaries. Import it once per session and do not write code for anything it does. Write code yourself only for work it does not cover (for example the LAT cross-tabulations), in the step's notebook.
> (b) Integrity. k.init copies the kit unchanged into env/ and logs its sha256. Never edit, patch, retype or wrap it. If k.session_start reports that its hash has changed, say so and ask the team before going on.
> (c) Only the kit writes the record. While you use the kit, change log/actions.jsonl, data/manifest.csv, plan/plan.yaml and plan/team.yaml only through its functions, never by editing the files.
> (d) Refusals are rules. When a function returns a refusal (for example an incomplete CERTIFY line, a reviewer who may not certify that decision, a systematic-review filter on a search for primary studies, or a PubMed count without its Create Date bound), show the team its one-line reason and the template it returns, and do not work around it.
> (e) Outputs. Show the team the Markdown that a function returns (md) without changing its numbers; copy every count from it with its log id; never retype, round or predict a count. Never describe a call you did not run or whose output you did not see (R12). Warnings are for you; act on them, but do not show them unless they affect the team.
> (f) Show, do not point. Everything the team must answer or review goes in the chat: the status card, the search strategy, the trace, the draft and the CERTIFY template. Never ask the team to open a file to see it. If your interface can show a file beside the chat (a side panel or canvas), you may also open the one relevant file there; links to files are extras, never the only place.
> (g) No network. If a source cannot be reached, the function returns a manual retrieval request; give it to the named member (R8), and when the member uploads the file, record it with k.ingest_manual.
> (h) No kit. If no kit was provided but you can run code, write the functions you need once, in env/stir_l4_local.py, with the same names and behavior, and reuse them in later turns; never rewrite logging, plan or flow code inside a turn. Log that the kit was absent. If you cannot run code, follow R8 and write the status card yourself from the plan, saying that it was not computed.

**New rule R15 (turn layout; the kit renders it, and it applies without the kit too):**

> R15. End every turn with the status card (k.status(); by hand without the kit): the step the team is on and the first unfinished step; the research focus as the team has stated it so far; what just happened, with log ids; what the team should answer or review now, addressed by name; what comes next; and the progress line. When a turn starts a new step, begin it with one line naming the step. Show the full plan map (k.status("full")) at the start and end of each session and whenever the team asks. Whenever you run or propose a search, show the strategy in the chat (k.render_search or k.run_strategy): each string in a code block, what its parts mean in plain words, the limits, the counts with log ids, the known studies it finds and what has not yet been searched, and ask the information specialist to review it.

**Step 2 edits** (the substance of IM and TP is unchanged; wording only):

> ... ask each member who is present what they want from the review, what draws them to the topic (the area, focus or question they most want answered) and what expertise they bring (Individual Motivation). ... Record each member's motivation with their interest (k.record_motivation). ... Draft the purpose statement only from what members said and the states they chose, including the research focus the members agreed on, in their words; if their interests differ, ask them to agree on one focus. Do not ask for Team's Purpose to be certified until it states an agreed research focus.

**Smaller edits:**
- **3.4:** "PubMed: the NCBI E-utilities, through the kit (k.pubmed_search, k.pubmed_fetch, k.mesh_lookup) or, without it, Biopython's Entrez module."
- **3.6:** append "The kit's retrieval functions add their own call to the step's notebook as a retrieval cell, and k.verify() recomputes every logged count from the saved files."
- **3.8:** append "With the kit, k.check_model() makes these checks and k.trace() is the flow function."
- **R4:** after "using the flow function of section 3.8" insert "(k.trace)".
- **R11:** "start with k.session_start(<session code>) and show its plan map; end with k.session_summary(next_questions=[...]) and show its text in the chat."

**Optional ordering change for speed.** This moves timing only; the authors would need to agree to it.

> With the kit, run k.init silently right after Step 1 (it asks the team nothing), so that the Step 1 and Step 2 answers are logged as they arrive, with real times, instead of being kept in the chat. The smoke test, the model record and the remaining intake stay at the end of Step 2.

This would remove the risk of losing answers carried in the chat, and the batch logging dance after set-up.

## 6. What a turn looks like with the kit

The arguments below are placeholders, not values.

- **Certification (transcript T9):** `print(k.certify(line)["md"])`. One call returns the record, commit, trace and card.
- **Step 2 answer:** `a = k.answer(name, text, element="IM")`, then `print(k.record_motivation(name, states=[...], interest=..., refers_to=a)["md"])`, then `print(k.status())`.
- **Scoping (transcript T14):** `s = k.run_strategy([(concept, line), ...], element="FE", purpose="primary", nb="02_feasibility_B")`, then `c = k.ctgov_studies(cond=..., intr=..., nb=...)`, then print `s["md"]`, `c["md"]` and `k.status(review="Reviewer B: please review the PubMed strategy above")`. The team's T15 question ("What was the search strategy used?") would not need asking.
- **Set-up (transcript T4 and T5):** `k.init(calibration={...})`, `k.record_model(..., read_from=...)`, `k.smoke_test()`, `k.status("full")`. NCBI e-mail and model name are asked once, inside the intake limit of three questions.

Metrics to add to `eval/metrics.md` (it does not exist yet; the transcript refers to it):
- lines of code the assistant wrote per turn
- tool calls per turn
- seconds per turn
- kit refusals per session
- direct edits to record files that bypass the kit (target 0)
- turns from proposal to certification

## 7. Open decisions for the authors

1. **Multi-page sha256.** Section 3.5 has one `raw_path` and one `sha256` per record. The kit's convention (a glob, and the hash of the ordered page hashes) needs approval.
2. **Where each member's interest lives.** Proposed: in `team.yaml members[].motivation`, with plan Individual Motivation `states` as the union and `decision` as one line per member. The plan.yaml layout is unchanged.
3. **Agreed focus before certifying Team's Purpose.** `propose("TP")` refuses without an agreed `focus`. Confirm that this is interaction behavior and not a change to Team's Purpose.
4. **Running `k.init` after Step 1.** An ordering change; see section 5.
5. **Dependencies.** Section 3.4's Biopython wording becomes "kit or Biopython". Set-up needs only `requests` and `pyyaml`; `pandas` and `jupyter` could be installed at Step 7 and the lock file re-recorded then.
6. **New file `env/session.json`.** Kit state, not a record. Also the commit identity fallback `STIR-L4 assistant <stir-l4@localhost>`.
7. **Distribution.** Ship the kit as a fifth supplementary file, versioned with the prompt (kit 1.0.x with prompt 1.0), with its sha256 printed in the supplement so teams can check the copy `k.init` saves.
8. **Portability.** ChatGPT and Claude sandboxes may have no internet access; there every source call returns the R8 fallback (by design). In the Codex app, network calls may need approval. The kit must not assume `fcntl` or a particular upload path.