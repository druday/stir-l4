"""Build STIR-L4 prompt v1.5 from v1.4 by checked edits. Run: python prompt/build_v1_5.py
Approved by the first author (2026-10-26), after Prof. Jiang's review of V10:
- Planning boundary (a change to the model text in section 1, as in Table 1 of the paper): planning ends when the team
  certifies the protocol; studies admitted during planning are provisionally included and also show the landscape
  around the topic, including related questions; the final included set is decided when the review is carried out.
- Step 9 and Step 12 follow that boundary; duplicates and reports of one study are matched on the fields of each paper
  object and counted once; an empty cell or atlas region is a candidate gap; a negative targeted search supports only a
  statement about the sources and dates searched; credentials appear in the log only as redacted placeholders.
v1.5 is released to readers as version 1.0 (release/build_release.py)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.4.txt")
OUT = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.5.txt")

EDITS = [
    ("# STIR-L4 PLANNING ASSISTANT (prompt version 1.4, October 2026)",
     "# STIR-L4 PLANNING ASSISTANT (prompt version 1.5, October 2026)"),
    ("This is version 1.4 of the prompt", "This is version 1.5 of the prompt"),
    ("Definition: Studies admitted to the review by screening; grows during planning and is fixed when the team commits to "
     "its included studies.",
     "Definition: Studies provisionally identified through scoping and pilot screening; the final included set is "
     "determined during review execution."),
    ("- Planning boundary: planning runs from the first scoping searches and pilot screening until the team commits to its "
     "included studies. Submitting the protocol to PROSPERO (or another registry) fixes the first certified version of the "
     "plan; any decision reopened afterwards is recertified and recorded as an amendment.",
     "- Planning boundary: planning runs from the first scoping searches and pilot screening until the team certifies the "
     "protocol. The studies admitted during planning are provisionally included (the Review Universe). They test the "
     "eligibility criteria and the search, and they show the landscape around the topic, including related questions "
     "that may matter more or have larger gaps. The final set of included studies is decided later, when the review is "
     "carried out. Registering the protocol (for example in PROSPERO) records the first certified version of the plan; "
     "any decision reopened afterwards is certified again and recorded as an amendment."),
    ("Step 9. Scoping and pilot screening (Review Universe; notebooks/05_screening.ipynb). Deduplicate records by code "
     "(section 3.6).",
     "Step 9. Scoping and pilot screening (Review Universe; notebooks/05_screening.ipynb). The studies admitted here are "
     "provisionally included: they test the eligibility criteria and the search and show the landscape around the topic, "
     "and the team decides the final set of included studies later, when it carries out the review. Deduplicate records "
     "by code (section 3.6), and link the reports of one study under one study key (section 5.1)."),
    ("Step 12. Commitment. Screening continues after registration until the team commits to its included studies, which "
     "ends planning (kind commitment; with the kit, k.commitment). Report the final counts, by grain, from the saved data.",
     "Step 12. End of planning. Planning ends when the team has certified the protocol; the final set of included studies "
     "is decided later, when the review is carried out. Record the end of planning with a snapshot of the provisionally "
     "included studies and of any related questions the team wants to keep for later (kind commitment; with the kit, "
     "k.commitment), and report the counts, by grain, from the saved data."),
    ("for example \"api_key\": \"<NCBI_API_KEY>\", and never record a key or an email address)",
     "for example \"api_key\": \"<redacted:NCBI_API_KEY>\", and never record a key or an email address)"),
    ("- Hold each included paper as a Python object", "- Hold each provisionally included paper as a Python object"),
    ("Reports of one study share a study key.",
     "Reports of one study share a study key. Because each paper is an object with many fields, duplicate records and "
     "several reports of one study are matched on those fields (identifiers, title, authors, year, registration number, "
     "population and sample size), and counts are made per study unless another grain is stated."),
    ("It is computed by a declared, versioned rule over objective properties and signed off by a reviewer.",
     "It is computed by a declared, versioned rule over prespecified properties and signed off by a reviewer."),
    ("A combination that no included study reports can be hidden in every two-way table",
     "A combination that no provisionally included study reports can be hidden in every two-way table"),
    ("which is why LAT keeps the full multi-way table and searches it for empty cells.",
     "which is why LAT keeps the full multi-way table and searches it for empty cells. An empty cell is a candidate gap: "
     "it may reflect missing reporting, inaccessible full text, a coding error, the limits of the search or a structural "
     "zero, and it is reported as such."),
    ("- Recompute after every batch of included studies,", "- Recompute after every batch of provisionally included studies,"),
    ("Only then report the region as a gap in the evidence.",
     "Only then report the region as a candidate gap, stating the sources and dates searched; a negative search does not "
     "show that no evidence exists."),
    ("Use a rule over its objective properties first;", "Use a rule over its verifiable properties first;"),
    ("Register papers again when a new paper, property or atlas version arrives.",
     "Register papers again when a new paper, property or atlas version arrives, keeping the earlier registrations."),
]


def build():
    t = open(SRC, encoding="utf-8").read()
    for a, b in EDITS:
        assert t.count(a) == 1, (t.count(a), a[:80])
        t = t.replace(a, b)
    assert t.count("prompt_v1.4") >= 2
    t = t.replace("prompt_v1.4", "prompt_v1.5")
    assert "version 1.4" not in t and "prompt_v1.4" not in t
    return t


if __name__ == "__main__":
    t = build()
    open(OUT, "w", encoding="utf-8").write(t)
    print(f"wrote {OUT}: {len(t.split())} words")
