# Planning record of the complete worked example

This folder holds the record of the worked example in Supplementary File 6 (`docs/example/STIR-L4 complete pipeline
example.pdf`): one plan followed from the first question to the final report. In that example the searches were run
live against PubMed, OpenAlex and ClinicalTrials.gov, the planning team was simulated, and the report was edited for
readers. PAO, LAT and RED were designed but not applied to studies. The example is illustrative; it is not an exact
replica of what an LLM will produce.

| Path | What it is |
|---|---|
| `log/actions.jsonl` | The append-only log: every query, answer, draft, certification and reopening, one JSON object per line |
| `plan/` | The plan as certified, the team file and the model the run used |
| `protocol/` | The data-extraction form, the drafts of the methods and the protocol, and each certified version of the protocol |
| `reports/` | Session summaries; the final report, edited for readers, is in `docs/example/final_report/` |
| `notebooks/` | The notebooks that ran each retrieval and computed each count |
| `lat/`, `red/` | The designs of the property registry and the atlas, certified before the search |
| `data/raw/` | Saved search responses, as returned by the public APIs (PubMed and MeSH searches, OpenAlex, ClinicalTrials.gov) |
| `data/derived/` | Tables computed by code from the saved responses (screening decisions, known-item checks, counts) |

Not included: the four full texts read during the example, and the PubMed record downloads (`pubmed_efetch`), whose
abstracts may be under publisher copyright. Each of them is still listed in the log with its exact query and the SHA-256
hash of the saved file, so it can be fetched again and checked. No credentials were stored: the log records only that a
key was not used or, in later versions of the kit, a redacted placeholder.
