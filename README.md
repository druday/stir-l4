# STIR-L4 prompt kit

STIR-L4 (a Systems Thinking-based InfoRmatics approach for pLanning systematic reviews Leveraging Large Language
models) represents the planning of a systematic review as a system of 10 elements joined by 27 flows. An LLM agent
retrieves facts at five decisions (A to E) through logged queries and drafts text for the team, and a named reviewer
certifies every decision (Automated Approach with Manual Milestone Review, AM2R).

STIR-L4 is an initial proposal that has yet to be tested. The prompt, quiz and helper kit here offer a prompt-based
exploration of it, while the authors build a dedicated planning application that is not yet available.

This repository holds everything a team needs to use STIR-L4 with its own LLM: the copy-paste prompt, a calibration
quiz, the machine-readable model, the core properties of a paper object, an optional helper kit that does the
deterministic set-up and record keeping in a few calls, and the evaluation harness used to improve the prompt.

> Singh UP, Walji M, Fenton S, Jiang X. Planning systematic reviews with large language models: a systems thinking
> approach. (Citation to be updated on publication.)

The authors are using STIR-L4 to build a dedicated planning tool. STIR-L4 is an open framework: you are free to use it
and this prompt with your own LLM. Feedback, calibration scores (with the LLM name and version) and reports of failures
are very welcome: uday.pratapsingh@uth.tmc.edu.

## What is here

| Path | What it is |
|---|---|
| `release/1.0/` | **Release 1.0, the files readers use and the paper ships** (Supplementary Files 1 to 5): prompt, quiz, model, core properties and helper kit, all version 1.0; built by `release/build_release.py` |
| `prompt/versions/` | Development versions of the prompt (v1.0 to v1.5); release 1.0 is v1.5 |
| `prompt/versions/STIR-L4_prompt_v1.0.txt` | The prompt as published with the paper's supplement (Box S1) |
| `prompt/build_v1_1.py` to `prompt/build_v1_5.py` | Build each version from the one before by checked edits, so every change is explicit |
| `kit/stir_l4_kit.py` | Optional helper kit (Python 3.11+, pyyaml; requests if available) |
| `kit/tests/` | Offline tests; set `STIR_L4_LIVE=1` to also test PubMed, OpenAlex and ClinicalTrials.gov |
| `data/STIR-L4_model_v1.0.yaml` | The model: elements, state spaces, flows (Supplementary File 4) |
| `data/STIR-L4_core_properties_v1.0.csv` | Core verifiable properties of a paper object (Supplementary File 3) |
| `analysis/count_loops.py` | Counts the loops of the flow graph from the model file (Figure 1, Supplementary Table S1) and checks how the counts change under other encodings (Supplementary Section S1) |
| `figures/` | The code that draws Figure 2, and the figure |
| `quiz/` | The calibration quiz (give the LLM only the questions) and its answer key |
| `eval/` | Interaction metrics, personas, transcripts, the automatic scorer and simulation results (including a full run to Step 12 with a literature audit) |
| `docs/design-v1.1/` | The diagnosis of the first live test and the design of v1.1 |
| `docs/example/` | Worked examples (PDF) and the scripts that build them from simulated sessions |
| `docs/example/planning_record/` | The planning record of the complete worked example: its log, plan, protocol, report, notebooks and saved search responses (see its README) |

## Quick start

1. Open a chat with an LLM that can run code and reach the web (for example the Codex app, ChatGPT with code
   execution, or Claude). Upload the files in `release/1.0/`: `STIR-L4_prompt_v1.0.txt`, `stir_l4_kit.py`,
   `STIR-L4_model_v1.0.yaml` and `STIR-L4_core_properties_v1.0.csv`.
2. Paste the prompt (or set it as the system instruction) and ask the LLM to follow its first-turn instructions. It
   reads the prompt, tests its tools and waits.
3. Paste `release/1.0/STIR-L4_calibration_quiz_v1.0.txt`. Score the answers with `release/1.0/quiz_key_v1.0.json`. The LLM is
   calibrated at 14 of 16 or more with every critical question (2, 7, 9, 10, 11, 14 and 16) in full. Never give the
   LLM the key.
4. Tell it the score and say "begin". From then on every reply opens with a status line, for example
   `Step 3 of 12: Need for a Review | Certified 2 of 8 | Waiting on you: 1 | Focus: what kind of weight is lost`,
   shows what was done, the content to review (searches in full), what comes next, and ends with "Your turn".
5. Useful commands, in any wording: "where are we", "next", "why", "show <item>", "skip", "back", "pause".
6. Planning ends with a final report (one HTML file, beside the chat): the plan as certified, then the protocol,
   written in full in the order of the PRISMA-P 2015 checklist, with a reason and a retrieved source for each choice, every
   gap marked, and a section on how STIR-L4 and the AI were used.
7. Optional access codes (a PubMed contact email or API key, an OpenAlex key) go in a `.env` file in the workspace or in
   environment variables (`NCBI_EMAIL`, `NCBI_API_KEY`, `OPENALEX_API_KEY`). Never paste a key into the chat.

Everything is logged in a workspace folder (`stir-l4-workspace/`) under version control; the team never needs to open
those files to follow the planning.

## Versions

Versions follow `major.minor.patch`: a new major version would change the theory (elements, flows, state spaces,
decisions or AM2R); a minor version changes how the assistant behaves and talks; a patch fixes wording. Each version is
a git tag (`git tag -l`), and every prompt version is also kept as a file in `prompt/versions/`, so going back is
`git checkout v1.0` or simply using the older file. See `CHANGELOG.md`.

## Helper kit at a glance

`import stir_l4_kit as k`, then: `k.selftest()`; `k.init(calibration=...)`; `k.status_line()`, `k.plan_map()`;
`k.set_topic`, `k.record_interest`, `k.set_focus`, `k.confirm_states`, `k.propose`; `k.certify_line`, `k.certify`;
`k.trace`, `k.reopen`, `k.early`; `k.setup()`; `k.screen`, `k.step_done`, `k.register`, `k.commitment`, `k.final_report`; `k.run_strategy`, `k.pubmed_search`, `k.pubmed_fetch`, `k.mesh_lookup`,
`k.known_item_check`, `k.openalex_works`, `k.ctgov_studies`, `k.request_manual`, `k.ingest_manual`, `k.verify`;
`k.session_start`, `k.session_summary`, `k.package`. Every function returns chat-ready Markdown in `md`; refusals come
back as one plain sentence (for example, a certification without the reviewer's reason). The kit enforces the log
schema, counts computed from saved responses, the PubMed Create Date bound and its check, the systematic-review
filter's scope, certification rights, step order and the "added by me: nothing" check on the research focus.

The kit has no functions that build PAO, LAT and RED (the paper objects, the literature tensor and the registration of
studies on the atlas). Building them for every provisionally included study is heavy, and the result is difficult to review and
manage within a chat, so they are left out of a prompt and kit meant to run inside any LLM provider's app. The prompt
asks the assistant to design all three before the search (the data-extraction form, the property registry and the
atlas) so that a named reviewer can certify them, and it describes their files; building them in full is intended for
a dedicated planning tool.

## Evaluating a prompt version

`eval/metrics.md` defines nine interaction metrics (orientation, one clear ask, research focus carried, search
transparency, the chat as the reading surface, plain language, pace, friction and turn length) and nine fidelity
guardrails that must never fail. `eval/personas/` holds simulated users; `eval/score_transcript.py` computes the
automatic parts; `eval/results/` holds simulated transcripts and scores for each version.

## How to cite

If you use STIR-L4, the prompt or the helper kit in research, teaching or a tool, please cite:

> Singh UP, Walji M, Fenton S, Jiang X. Planning systematic reviews with large language models: a systems thinking
> approach. Manuscript in preparation (citation to be updated on publication).

`CITATION.cff` holds the same information in a machine-readable form.

## Feedback and refinement

STIR-L4 is an open framework, and the authors would like it to become more robust over time. Please report refinements
to the corresponding author (uday.pratapsingh@uth.tmc.edu) or as a repository issue: valid suggestions and specific
improvements to the framework, the prompt or its architecture, failures you observed, and calibration scores. Include
the prompt and kit versions, the LLM name and version and, where you can, the transcript or the session summary.

## License

Code (the kit, the evaluation scripts and the build scripts) is under the MIT License (`LICENSE-CODE`); the prompts,
quiz, model files, documentation and examples are under CC BY 4.0 (`LICENSE-CONTENT`). Citing the paper and reporting
refinements are requests from the authors, not conditions of either license (see `LICENSE`).
The copyright holders are the four authors.
