"""Build 'STIR-L4 complete pipeline example.pdf': one simulated plan from the first question to the final report.

Part 1 is the STIR-L4 final report as the helper kit wrote it (the plan as certified, then the protocol). Part 2
reproduces every message of the five sessions word for word, with lettered margin notes.
Run: python docs/example/build_full_pipeline_pdf.py [<planning folder after session 5>]
"""
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_example_pdf as E  # noqa: E402  (render, inline, NOTES for session 1)

REPO = os.path.dirname(os.path.dirname(HERE))
RES = os.path.join(REPO, "eval", "results")
WS = sys.argv[1]   # the example run's STIR-L4 workspace (its planning record is in docs/example/planning_record)
S5 = os.path.join(os.path.dirname(WS), "turns", "transcript.json")
OUT = os.path.join(os.path.dirname(REPO), "STIR-L4 complete pipeline example.pdf")
NOTES = {
    (2, 6): [("R", "A new chat resumes from the saved files", "The assistant has no memory of Session 1. It reads the saved plan, "
              "team file, log and session summary, restores the status line and plan map, and continues from the open question.")],
    (2, 10): [("S", "The soundness check of the question", "Before drafting the case for a review, the assistant checks with "
               "real, logged PubMed searches whether the question holds up clinically, scientifically and logically: the whole "
               "topic, the focus in any region, how the drug causes weight loss, fat or muscle with water, and off-label use.")],
    (2, 12): [("F", "A feedback loop: the focus changes, so the purpose is reopened", "Uday adds body water to the focus. Because "
               "the certified Team's Purpose names the focus, it is reopened and certified again (message 14).")],
    (2, 16): [("H", "Honest about what was not searched", "PROSPERO, OSF Registries, Cochrane and Epistemonikos are recorded as "
               "not searched, so whether a planned review exists stays unknown.")],
    (2, 20): [("C", "Need for a Review certified: 3 of 8", "A new review, on four grounds the user chose, with the user's reason.")],
    (2, 24): [("C", "A bare \"Certify\" gets one question", "Only the reason is asked for.")],
    (2, 30): [("F", "Feasibility says broaden, and the flows say what it reopens", "Widening to all adults without diabetes "
               "changes three certified decisions that name Asian people. The assistant lists each with the evidence and asks "
               "before reopening anything.")],
    (2, 34): [("F", "Reopened with the user's agreement: Certified drops from 4 to 2", "Feasibility is certified; the Team's "
               "Purpose, Need for a Review and Review Objective are reopened and marked in the status line. They are certified "
               "again at messages 38, 48 and 52, and the count climbs back to 5.")],
    (2, 38): [("S", "The soundness check is repeated for the wider focus", "With new searches, before the case is certified again.")],
    (3, 6): [("R", "Session 3 resumes at the Research Question", "From the saved files, with the draft question for the user to edit.")],
    (3, 8): [("C", "Subject headings by retrieval", "Each concept of the question is mapped to MeSH headings looked up in PubMed, "
              "not recalled.")],
    (3, 12): [("C", "Research Question certified: 6 of 8", "")],
    (3, 16): [("L", "Step 7, before the search: the data-extraction form", "Paper as an Object: the fields to extract from each "
               "study are fixed and certified before anything is screened. Designs only: building paper objects for each study is "
               "not available in the prompt version (it is being developed for a dedicated planning tool).")],
    (3, 20): [("L", "The property registry", "Literature as a Tensor: the features to count across studies, with fixed levels, "
               "certified before the search. A design only, not applied to studies in the prompt version.")],
    (3, 26): [("L", "The atlas", "Registering Evidence Dynamically: the map of the field (sides and thresholds for empty, thin and "
               "crowded regions) certified before the search; then the first draft search is run. A design only, not applied to "
               "studies in the prompt version.")],
    (3, 28): [("V", "Known studies test the search", "The draft searches find 3 of 4 known studies; the assistant reads the free "
               "full text of the missed trial. The strategy is refined until a search finds all 4 (certified at message 36).")],
    (3, 32): [("H", "No key, no pretending", "Without an OpenAlex access code, the OpenAlex search waits rather than being reported "
               "as done.")],
    (3, 36): [("C", "Search Strategy certified: 7 of 8", "Then the records are gathered for pilot screening.")],
    (3, 38): [("P", "Pilot screening: the person decides", "Uday screens each record shown; the assistant only suggests, as a DRAFT, "
               "and points out duplicates. Pilot screening tests the eligibility criteria and the search; it is not the review's "
               "screening and stays out of the final report. (The status line shows Step 10 here, a slip fixed before release.)")],
    (4, 6): [("R", "Session 4 resumes at Methodology", "")],
    (4, 8): [("F", "Methods feed back to feasibility", "Each methods choice is checked against the hours available (flow 23), "
              "as the model requires.")],
    (4, 16): [("C", "Methodology certified: 8 of 8", "Every decision of the model is now certified.")],
    (4, 18): [("C", "The protocol is drafted and edited", "PRISMA-P order, a statement of how the AI helped, author, funding, "
               "registry and the author's interest in the prompt and kit: four drafts in the chat. This first protocol is a table; "
               "Session 5 rewrites it in full in the standard template.")],
    (4, 24): [("V", "The kit refuses an unsafe certification", "The protocol changes certified methods, so it cannot be certified "
               "until the user agrees to reopen Methodology (message 26).")],
    (4, 28): [("H", "Not submitted, and recorded as such", "The protocol was not registered in this test.")],
    (4, 30): [("V", "A test step: the commitment", "The prompt's last step asks the team to commit to its included studies. In this "
               "test the script had Uday commit to the 4 records he included in the pilot, which conflicts with his approved search "
               "and methods; the assistant lays out the conflict and leaves the choice to him. The commitment and the conflict stay "
               "in the log and are not part of the final report.")],
    (4, 34): [("C", "End of Session 4", "The plan is saved; Session 5 turns it into the final report.")],
    (5, 6): [("W", "The protocol in the standard template", "The assistant writes the protocol in full, item by "
              "item in PRISMA-P order, with the searches reported as PRISMA-S asks, a reason and a retrieved source for each choice, "
              "every gap marked, and a section on how STIR-L4 and the AI were used. The helper kit refuses to build the report if "
              "the protocol cites a paper that no saved search returned.")],
    (5, 7): [("W", "The user reviews before certifying", "Uday asks for three edits: drop an off-topic reference, add the nearest "
              "evidence (reviews in people with type 2 diabetes), and leave the commitment and the conflict to the log.")],
    (5, 8): [("V", "Corrections, each backed by a search", "The assistant searches for a methods source for the re-check, finds none and "
              "cites none; it chooses the diabetes reviews by a stated rule and checks every number against the saved abstracts.")],
    (5, 10): [("C", "Protocol certified; the final report is produced", "The plan as certified and this protocol form the final "
               "report in Part 1. (The one-line steps view here leaves out steps 9, 11 and 12, and the kit would have called an "
               "unsubmitted protocol registered: both fixed before release.)")],
}
LEGEND2 = [("R", "Resuming a session from saved files"), ("S", "The soundness check of the question"),
           ("F", "Feedback between decisions (reopening)"), ("C", "Certifications and progress"),
           ("L", "Before the search: extraction form, registry, atlas"), ("V", "Verification and safeguards"),
           ("P", "Pilot screening by the person (a test of the criteria)"), ("H", "Honesty about what was not done"),
           ("W", "Writing the protocol and the final report")]


def md(text):
    """Markdown with headings, for the saved plan and protocol files."""
    out = []
    buf = []
    for ln in text.split("\n"):
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            if buf:
                out.append(E.render("\n".join(buf), False))
                buf = []
            lvl = min(4, len(m.group(1)) + 1)
            out.append(f"<h{lvl}>{E.inline(m.group(2))}</h{lvl}>")
        else:
            buf.append(ln)
    if buf:
        out.append(E.render("\n".join(buf), False))
    return "\n".join(out)


def chat(n, tr, notes):
    out = []
    for idx, t in enumerate(tr, 1):
        if idx < 5:
            continue
        who = "assistant" if t["role"] == "assistant" else "user"
        label = "STIR-L4 assistant" if who == "assistant" else "Uday (simulated user)"
        side = (f'<div class="side">Opened beside the chat: {html.escape(t["side_panel"])}</div>' if t.get("side_panel") else "")
        out.append(f'<div class="msg {who}"><div class="who">{label} <span class="num">session {n}, message {idx}</span></div>'
                   f'<div class="bubble">{E.render(t["text"], who == "assistant")}</div>{side}</div>')
        for mark, title, text in notes.get(idx, []):
            out.append(f'<div class="note"><span class="mark">{mark}</span><div><b>{html.escape(title)}.</b> '
                       f'{html.escape(text)}</div></div>')
    return "\n".join(out)


def build():
    log = [json.loads(l) for l in open(os.path.join(WS, "log", "actions.jsonl"), encoding="utf-8")]
    reports = sorted(f for f in os.listdir(os.path.join(WS, "reports")) if f.endswith("_final_report.md"))
    report = open(os.path.join(HERE, "final_report", "STIR-L4 example final report.md"), encoding="utf-8").read()
    s1 = json.load(open(os.path.join(RES, "round5", "p1_rc5_transcript.json"), encoding="utf-8"))
    ss = {n: json.load(open(os.path.join(RES, "full_pipeline", f"S{n}_session.json"), encoding="utf-8"))["transcript"]
          for n in (2, 3, 4)}
    ss[5] = json.load(open(S5, encoding="utf-8"))
    css = open(os.path.join(HERE, "example.css"), encoding="utf-8").read() + """
.part { page-break-before: always; }
.divider { page-break-before: always; border: 1px solid #c9d3e3; background: #f6f8fc; border-radius: 8px; padding: 12px 16px; margin-bottom: 14px; }
.divider h2 { border: none; margin-bottom: 4px; }
.plan h2 { font-size: 12.5pt; } .plan h3 { font-size: 11pt; } .plan h4 { font-size: 10pt; }
.plan { font-size: 9.2pt; }
.plan table { border-collapse: collapse; width: 100%; font-size: 8.3pt; margin: 4px 0 8px; }
.plan th, .plan td { border: 1px solid #d7dde8; padding: 3px 5px; vertical-align: top; text-align: left; }
.plan th { background: #eef2f8; }
.mark { font-size: 7.5pt; }
a { color: #0b5cad; text-decoration: none; }
"""
    nq = sum(1 for r in log if r["kind"] in ("query", "manual_retrieval"))
    body = [f"""
<section class="cover">
  <div class="kicker">STIR-L4 · a worked example</div>
  <h1>The complete pipeline</h1>
  <p class="sub">One simulated plan, from the first question to the final report: five sessions, every reply as written</p>
  <p>Every STIR-L4 planning effort ends with a final report: the plan as the team certified it, followed by a protocol written
  in the standard template for systematic review protocols (PRISMA-P 2015). Part 1 is that report for this run, as the
  assistant produced it, tidied for readers (see Fidelity below). Part 2 is the conversation that led to it, so that readers can see how each decision was reached.
  The user, a simulated solo reviewer, plans a review of what kind of weight is lost with SGLT2 inhibitors.</p>
  <div class="box"><h3>About this run</h3><ul>
    <li><b>User:</b> a second AI playing Uday, a terse solo reviewer, from a script the first author approved (eval/personas/P1_full_pipeline.md).</li>
    <li><b>Assistant:</b> Claude Opus 5.5 (Anthropic), given only the STIR-L4 prompt and the files a team would upload: the prompt, the helper kit, the model file and the core-properties file. The sessions were run while the prompt was being finalized, on development versions that differ from the released prompt (version 1.0, Supplementary File 1) in how the assistant talks with the team and writes the report, not in the STIR-L4 model.</li>
    <li><b>Searches:</b> real. {nq} logged retrievals from PubMed (including its MeSH index and PubMed Central), OpenAlex and ClinicalTrials.gov, run live on 25 October 2026, each saved; every reference in the protocol was found in a saved search result and checked again against PubMed and Crossref.</li>
    <li><b>What the report leaves out:</b> STIR-L4 in a chat app plans a review; it does not screen studies or extract data. The pilot screening and the commitment in Sessions 3 and 4 followed the prompt's steps at the time and tested the criteria; they stay in the log. Paper as an Object, Literature as a Tensor and Registering Evidence Dynamically were designed at Step 7 but are not built in the prompt version; they are being developed for a dedicated planning tool.</li>
    <li><b>Fidelity of this document:</b> every message is reproduced word for word, so drafts in the conversation carry working version numbers. The report in Part 1 is the file the helper kit wrote, with editorial changes only, each listed in docs/example/clean_report.py: working version labels and draft history removed, every PMID and DOI linked, and the plan's Methodology entry showing the methods as certified rather than the protocol's certification line. No content was changed. Only the layout and the lettered notes are added.</li>
  </ul></div>
  <div class="box"><h3>Contents</h3><ul>
    <li><b>Part 1, the STIR-L4 report:</b> 1. the plan, as certified; 2. the protocol (PRISMA-P items, what planning found, how STIR-L4 and AI were used, gaps, references).</li>
    <li><b>Part 2, the conversation:</b> Session 1 (steps 1 to 3), Session 2 (3 to 6), Session 3 (6 to 9), Session 4 (10 to 12), Session 5 (the protocol and the final report).</li>
  </ul></div>
  <div class="box legend"><h3>Margin notes</h3>
    <ol class="legend">{''.join(f'<li><span class="mark">{m}</span>{html.escape(t)}</li>' for m, t in LEGEND2)}</ol>
    <p class="small">Session 1 keeps the numbered notes of the first example (1 to 9).</p></div>
</section>
<section class="part plan"><h2>Part 1. The STIR-L4 report</h2>
  <p class="small">From the assistant's planning folder (reports/{reports[-1]}, written by the helper kit from the saved plan
  and the certified protocol), with the editorial changes listed on the cover. Every PMID and DOI is a link.</p>
  {md(report)}
</section>
"""]
    blurbs = {1: "Session 1 (from the first example). The topic, each interest, the focus and the purpose are set; Uday asks to "
                 "\"just start\", so Step 3's searches run early; the session ends with a pause.",
              2: "Session 2. A new chat resumes from the saved files. The soundness check runs; body water joins the focus; the "
                 "need for a review and the objective are certified; feasibility says broaden, which reopens three earlier "
                 "decisions, each certified again; the session ends as the research question is drafted.",
              3: "Session 3. The research question is certified; the extraction form, property registry and atlas are designed "
                 "and certified before the search; the search strategy is refined against known studies and certified; Uday "
                 "screens a pilot of 26 records to test the criteria.",
              4: "Session 4. The methods are settled and certified; a first protocol is drafted as a table and certified after "
                 "the methods are reopened; registration is recorded as not submitted; the test script's commitment closes "
                 "the steps.",
              5: "Session 5. The assistant writes the protocol in full in the standard template, with a reason "
                 "and a source for each choice and every gap marked; Uday asks for corrections before certifying; the protocol "
                 "is certified and the final report (Part 1) is produced."}
    body.append(f'<section class="divider"><h2>Part 2. Session 1</h2><p>{html.escape(blurbs[1])}</p></section><section class="chat">')
    s1_full = [{"role": "user", "text": ""}] * 4 + s1
    out = []
    for idx, t in enumerate(s1_full, 1):
        if idx < 5:
            continue
        who = "assistant" if t["role"] == "assistant" else "user"
        label = "STIR-L4 assistant" if who == "assistant" else "Uday (simulated user)"
        side = (f'<div class="side">Opened beside the chat: {html.escape(t["side_panel"])}</div>' if t.get("side_panel") else "")
        out.append(f'<div class="msg {who}"><div class="who">{label} <span class="num">session 1, message {idx}</span></div>'
                   f'<div class="bubble">{E.render(t["text"], who == "assistant")}</div>{side}</div>')
        for mark, title, text in E.NOTES.get(idx, []):
            out.append(f'<div class="note"><span class="mark">{mark}</span><div><b>{html.escape(title)}.</b> {html.escape(text)}</div></div>')
    body.append("\n".join(out) + "</section>")
    for n in (2, 3, 4, 5):
        body.append(f'<section class="divider"><h2>Part 2. Session {n}</h2><p>{html.escape(blurbs[n])}</p>'
                    f'<p class="small">Messages 1 to 4 of each session (the tool test and the calibration quiz, scored 16 of 16) are not shown.</p></section>')
        body.append('<section class="chat">' + chat(n, ss[n], {m: v for (s, m), v in NOTES.items() if s == n}) + "</section>")
    doc = f"<!doctype html><html><head><meta charset='utf-8'><title>STIR-L4 complete pipeline example</title><style>{css}</style></head><body>{''.join(body)}</body></html>"
    tmp = os.path.join(HERE, "full_pipeline.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(doc)
    subprocess.run([E.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={OUT}", "file://" + tmp],
                   check=True, capture_output=True)
    return OUT


if __name__ == "__main__":
    print(build())
