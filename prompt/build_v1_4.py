"""Build STIR-L4 prompt v1.4 from v1.3 by checked edits. Theory unchanged. Run: python prompt/build_v1_4.py
Approved by the first author (2026-10-25), before submission of the paper:
- References in the protocol are linked: each PMID to its PubMed page and each DOI through doi.org.
- The protocol is one document: no version numbers, draft history or notes on what changed; earlier drafts stay in the
  planning folder and the log, and after registration each amendment is listed under item 4.
- The wording of a certified decision reads on its own: no version labels and no numbers the chat gave to searches.
v1.4 is released to readers as version 1.0 (release/build_release.py)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.3.txt")
OUT = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.4.txt")

EDITS = [
    ("# STIR-L4 PLANNING ASSISTANT (prompt version 1.3, October 2026)",
     "# STIR-L4 PLANNING ASSISTANT (prompt version 1.4, October 2026)"),
    ("This is version 1.3 of the prompt", "This is version 1.4 of the prompt"),
    ("Number the references and give each its PMID or DOI, or its web address and the date it was read.",
     "Number the references and give each its PMID, linked to its PubMed page (https://pubmed.ncbi.nlm.nih.gov/<PMID>/), "
     "and its DOI, linked through https://doi.org/, or else its web address and the date it was read, so that a reader "
     "can open every paper. The protocol is one document: write no version numbers, draft history or notes on what "
     "changed into it; earlier drafts stay in the planning folder and the log, and after registration each amendment is "
     "listed under item 4."),
    ("When a decision is ready, show once the line with everything filled in except the reason, using the element's full "
     "name (k.certify_line):",
     "When a decision is ready, show once the line with everything filled in except the reason, using the element's full "
     "name and wording the decision so that it reads on its own, without version labels or the numbers the chat gave to "
     "searches (k.certify_line):"),
]


def build():
    t = open(SRC, encoding="utf-8").read()
    for a, b in EDITS:
        assert t.count(a) == 1, (t.count(a), a[:70])
        t = t.replace(a, b)
    assert t.count("prompt_v1.3") >= 2
    t = t.replace("prompt_v1.3", "prompt_v1.4")
    assert "version 1.3" not in t and "prompt_v1.3" not in t
    return t


if __name__ == "__main__":
    t = build()
    open(OUT, "w", encoding="utf-8").write(t)
    print(f"wrote {OUT}: {len(t.split())} words")
