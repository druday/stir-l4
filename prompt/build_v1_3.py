"""Build STIR-L4 prompt v1.3 from v1.2 by checked edits. Theory unchanged. Run: python prompt/build_v1_3.py
Approved by the first author (2026-10-25):
- The protocol is the main output of planning: full sentences in PRISMA-P 2015 order, searches reported as PRISMA-S
  asks, a reason and a retrieved source for each methodological choice, GAP where the team has not decided, and three
  added sections (what planning found; how STIR-L4 and AI were used, as the 2025 position statement and RAISE ask; gaps).
- Planning ends with a final report (k.final_report): the plan as certified, then the protocol, as HTML (PDF if
  possible); screening counts and the running record stay in the log.
- Paper as an Object, Literature as a Tensor and Registering Evidence Dynamically are designed and certified only:
  building them for each study is not part of the prompt (in development for a dedicated planning tool).
- After Session 5 (which ran on v1.3-rc1): pilot screening appears in the protocol only as a test of the criteria;
  commitments, conflicts and checks of the record stay in the log; sources for choices are guidance or methods research;
  short paragraphs, with findings from several studies in a table (not yet tested in a simulated session)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.2.txt")
OUT = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.3.txt")

STEP11 = (
    "Step 11. Protocol (notebooks/07_protocol.ipynb; protocol/protocol_v<n>.md). The protocol is the main output of "
    "planning. Write it in full sentences, in short paragraphs of one point each (findings from several studies go in a "
    "table), item by item in the order of the PRISMA-P 2015 checklist (administrative "
    "information, introduction, methods), with the item number in each heading, and report the searches as PRISMA-S "
    "asks (each source and platform, the date searched, the full strings, limits and filters, the known-study check and "
    "any peer review). Build each item from the certified decisions and logged facts, and give the reason for each "
    "methodological choice with a source for it (for example the reporting guideline, the handbook chapter, the "
    "risk-of-bias tool, methods research or the guidance for the review type, never a study on another topic that "
    "merely used the method), found by a logged retrieval, never from memory (R1). "
    "Number the references and give each its PMID or DOI, or its web address and the date it was read. Where an item "
    "needs something the team has not decided or given, write \"GAP:\", what is missing and who can supply it; never "
    "fill a gap yourself (R2). After the methods, add three sections: \"What planning found\", the facts behind the "
    "decisions (existing reviews and what they cover, the counts and ongoing studies behind feasibility, the soundness "
    "appraisal and the known-study check), each as a FACT with its source, where pilot screening appears only as a "
    "test of the eligibility criteria and the search (how many records were screened and what they showed about the "
    "criteria), while commitments, recorded conflicts and checks of the planning record stay in the log; \"How STIR-L4 "
    "and AI were used\", as the "
    "2025 position statement on AI in evidence synthesis and the RAISE guidance ask: the framework and its paper, the "
    "prompt and kit versions, the LLM's name and version as recorded (or \"not available\"), the dates of the sessions, "
    "what the AI did at each step (retrieving, counting, drafting, suggesting screening decisions), what people decided "
    "and certified, and how they checked the AI's work; and \"Gaps\", listing every GAP. In the chat, show the protocol "
    "as a table of its items, one line each, with every GAP in full; show an item in full on request, and the whole "
    "protocol beside the chat. The team edits and a reviewer certifies it. Record the registry submission (kind "
    "registration), or that the protocol was not submitted and why (with the kit, k.register(..., status=\"not "
    "submitted\", note=<reason>)). Any later reopening is an amendment (R6).")

REPORT = (
    " When planning ends, or whenever the team asks for it, produce the final report (with the kit, k.final_report()): "
    "one HTML file in reports/ (also a PDF if your tools can make one) that holds, first, the plan as certified (the "
    "topic, the focus and each certified decision in step order, with who certified it, when and the reason as given) "
    "and, second, the protocol. In the report, Paper as an Object, Literature as a Tensor and Registering Evidence "
    "Dynamically take one line saying that building them is not available in this prompt version; screening counts "
    "and the running record stay in the log. Show the report beside the chat and its outline in the chat.")

EDITS = [
    ("# STIR-L4 PLANNING ASSISTANT (prompt version 1.2, October 2026)",
     "# STIR-L4 PLANNING ASSISTANT (prompt version 1.3, October 2026)"),
    ("This is version 1.2 of the prompt", "This is version 1.3 of the prompt"),
    ("as section 5 describes. A named reviewer certifies all three before the search is run.",
     "as section 5 describes. A named reviewer certifies all three before the search is run. In this prompt version "
     "the three are designed and certified only: building paper objects, the tensor and the atlas registration for each "
     "study is not part of the prompt (it is being developed for a dedicated planning tool), so section 5 describes "
     "their files for that tool and for teams that build them by hand. Say so plainly if the team asks for them."),
    ("As studies are admitted, build the PAO, LAT and RED files (section 5). ", ""),
    ("Step 11. Protocol (notebooks/07_protocol.ipynb). Assemble a draft protocol that covers the PRISMA-P items, "
     "including a statement of how the LLM was used, as evidence-synthesis guidance and journals ask. The team edits and "
     "a reviewer certifies it. Record the registry submission (kind registration), or that the protocol was not "
     "submitted and why (with the kit, k.register(..., status=\"not submitted\", note=<reason>)). Any later reopening is "
     "an amendment (R6).", STEP11),
    ("Report the final counts, by grain, from the saved data.",
     "Report the final counts, by grain, from the saved data." + REPORT),
    ("k.commitment, k.session_start,", "k.commitment, k.final_report, k.session_start,"),
    ("and three for the representations of the included literature: 10_pao, 11_lat and 12_red.",
     "and three for the representations of the included literature: 10_pao, 11_lat and 12_red (in this prompt version, "
     "only their designs at Step 7)."),
    ("- pao/, lat/ and red/: the paper objects, the cross-tabulations and the atlas registration.",
     "- lat/ and red/: the property registry and the atlas certified at Step 7 (paper objects, cross-tabulations and "
     "atlas registration are not built in this prompt version)."),
    ("- notes/ and reports/: discussion notes and session summaries.",
     "- notes/ and reports/: discussion notes, session summaries and the final report (the plan as certified, then the "
     "protocol)."),
]


def build():
    t = open(SRC, encoding="utf-8").read()
    for a, b in EDITS:
        assert t.count(a) == 1, (t.count(a), a[:70])
        t = t.replace(a, b)
    n = t.count("prompt_v1.2")
    assert n >= 2, n
    t = t.replace("prompt_v1.2", "prompt_v1.3")
    assert "version 1.2" not in t and "prompt_v1.2" not in t
    return t


if __name__ == "__main__":
    t = build()
    open(OUT, "w", encoding="utf-8").write(t)
    print(f"wrote {OUT}: {len(t.split())} words")
