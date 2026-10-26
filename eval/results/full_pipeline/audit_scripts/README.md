# Literature audit scripts (full-pipeline run, 2026-10-25)

Scripts an independent auditing agent wrote to check the full-pipeline run. Each takes the planning folder
(`stir-l4-workspace/`) as its first argument and checks one thing: saved counts against raw files (`a1`), identifiers
(`a2`), live PubMed re-runs (`a3`, `a8`), titles (`a4`), quoted passages (`a5`, `a12`, `a12b`), ClinicalTrials.gov
(`a6`), search strings (`a7`), OpenAlex (`a9`), snippets and recomputed counts (`a10`, `a11`, `a13`) and known studies
(`a14`); `corpus.py` builds the text corpus they share. The verdict and issues are in `../audit.json`.

The planning folder itself is not in this repository because it holds full texts retrieved from PubMed Central; the
first author keeps a copy.
