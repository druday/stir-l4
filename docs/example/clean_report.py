"""Prepare the example's final report for readers: remove the working version labels and draft history, and link every
PMID and DOI. Content is not changed; every replacement is listed here and checked to occur exactly once.
The Methodology entry of the plan shows the methods as certified (L000655) and the later certification with the
protocol (L000780), instead of the protocol's certification line. Prompt 1.0 asks for this form from the start.
Run: python docs/example/clean_report.py <final_report.md> <out_dir>"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "kit"))
import stir_l4_kit as k  # noqa: E402

METHODS = (
    "Certified by Uday on 2026-10-25 at 11:51 UTC (L000655); reason, as given: \"fits a solo review\"\n\n"
    "{methods}\n\n"
    "Certified again together with the protocol (section 2) on 2026-10-25 at 15:17 UTC (L000780); reason, as given: "
    "\"follows the standard template\"")

STATUS = (
    "Status: certified by Uday on 2026-10-25 with the reason “follows the standard template” (L000780). The protocol "
    "writes every decision Uday certified in full sentences, item by item in the order of the PRISMA-P 2015 checklist "
    "[34], with the searches reported as PRISMA-S asks [14], a numbered reference for each methodological choice, and "
    "three closing sections: what planning found, how STIR-L4 and AI were used, and gaps. '(my suggestion)' marks wording "
    "the assistant drafted that came from neither Uday nor a retrieved fact; Uday accepted it when he certified the "
    "protocol. The word GAP marks what is missing and who can supply it; every gap is listed again at the end. "
    "Planning-record ids (L followed by six digits) are given for audit; numbered references are listed at the end.")

EDITS = [
    ("STIR-L4 prompt version(s): 1.1, 1.2, 1.3; helper kit 1.1.7; ",
     "STIR-L4 prompt and helper kit: development versions, before release 1.0; "),
    ("version 1: PubMed — search 4 as shown,", "PubMed — the search shown in protocol item 10,"),
    ("ClinicalTrials.gov — search 5 as shown,", "ClinicalTrials.gov — the search shown in protocol item 10,"),
    ("OpenAlex — search 3 as shown,", "OpenAlex — the planned search shown in protocol item 10,"),
    ("the drug names of search 5,", "the drug names of the ClinicalTrials.gov search,"),
    ("## 2. Protocol, version 2, as certified", "## 2. Protocol"),
    ("This protocol is not an amendment: version 2 rewrites version 1 before any registration.",
     "This protocol is not an amendment; it has not been registered."),
    ("[7]. **New in version 2.** The nearest evidence", "[7]. The nearest evidence"),
    ("(certified search strategy, version 1; record: L000489)", "(certified search strategy; record: L000489)"),
    ("the certified data-extraction form (version 1),", "the certified data-extraction form,"),
    ("the certified data-extraction form, version 1 (record: L000380)", "the certified data-extraction form (record: L000380)"),
    ("**New in version 2.** This section replaces the statement on the AI's help in version 1. It follows",
     "This section follows"),
    ("The assistant followed the STIR-L4 planning prompt version 1.1 (session 1), 1.2 (sessions 2 to 4) and 1.3 "
     "(session 5), and the helper kit 1.1.4 (sessions 1 to 4) and 1.1.7 (session 5); each file",
     "The assistant followed the STIR-L4 planning prompt and its helper kit, in development versions made before "
     "release 1.0; each file"),
    ("session 5 from 14:28 UTC, still open when this draft was written).", "session 5 from 14:28 UTC)."),
    ("the methods with protocol version 1.", "the methods with the protocol."),
    ("*Use during the review* (certified, version 1):", "*Use during the review* (certified):"),
    ("*Interests and sharing* (certified, version 1):", "*Interests and sharing* (certified):"),
    (" **New in version 2:** the limitation that the model and version could not be given is removed, as Uday has now "
     "given them.", ""),
    ("Cited as the STIR-L4 planning prompt version 1.3 gives it (env/prompt_v1.3.txt, sha256 "
     "4894fc6e9ac8bf492af6f559b749e96531af7aa0f3ca3914893695423f7f39ca).",
     "Cited as the STIR-L4 planning prompt gives it."),
]


def clean(md, methods):
    for a, b in EDITS:
        assert md.count(a) == 1, (md.count(a), a[:70])
        md = md.replace(a, b)
    md, n = re.subn(r"(?m)^Status: certified by Uday on 2026-10-25 with the reason “follows the standard template” "
                    r"\(L000780\), after he agreed.*$", STATUS, md)
    assert n == 1
    md, n = re.subn(r"(?s)Certified by Uday on 2026-10-25 at 15:17 UTC \(L000780\); reason, as given: \"follows the "
                    r"standard template\"\n\nprotocol, version 2, with Uday's three edits:.*?pooling method\n",
                    METHODS.format(methods=methods).replace("\\", "\\\\") + "\n", md)
    assert n == 1
    left = re.findall(r".{0,40}\b(?:(?<!API )version [12]\b|v1\.[0-9]|1\.1\.[0-9]|New in version|search [0-9] as shown).{0,40}", md)
    assert not left, left
    return k.link_refs(md)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    ws = os.path.dirname(os.path.dirname(os.path.abspath(src)))
    import json
    rec = next(json.loads(l) for l in open(os.path.join(ws, "log", "actions.jsonl"), encoding="utf-8")
               if json.loads(l)["id"] == "L000655")
    md = clean(open(src, encoding="utf-8").read(), rec["decision"])
    os.makedirs(out, exist_ok=True)
    head = re.match(r"# (.*)", md).group(1)
    with open(os.path.join(out, "STIR-L4 example final report.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(out, "STIR-L4 example final report.html"), "w", encoding="utf-8") as f:
        f.write(f"<!doctype html><html><head><meta charset='utf-8'><title>{k._inline_html(head)}</title><meta name='viewport' "
                f"content='width=device-width, initial-scale=1'><style>{k._REPORT_CSS}</style></head><body>"
                + k._md_html(md).replace("<p>" + k._inline_html(k._NOT_IN_PROMPT) + "</p>",
                                         "<p class=note>" + k._inline_html(k._NOT_IN_PROMPT) + "</p>")
                + "</body></html>")
    print("wrote", out)
