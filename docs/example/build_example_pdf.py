"""Build 'STIR-L4 v1.1 worked example.pdf' from a saved simulation transcript (text reproduced word for word).

Layout only: chat bubbles, the status line as a bar, tables, code blocks, and numbered margin notes that point out
what the prompt is doing. Run:  python docs/example/build_example_pdf.py [transcript.json judge.json out.pdf]
"""
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
TR = os.path.join(REPO, "eval", "results", "round5", "p1_rc5_transcript.json")
JU = os.path.join(REPO, "eval", "results", "round5", "p1_rc5_judge.json")
OUT = os.path.join(os.path.dirname(REPO), "STIR-L4 v1.1 worked example.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

STATUS = re.compile(r"^Step \d{1,2} of 12: .+\| *Certified \d of 8 *\|")

# Margin notes, keyed by the message number they follow (message numbers as in the transcript).
NOTES = {
    6: [("1", "The status line", "Every reply opens with it: the step (1 of 12), how many of the eight decisions are certified, "
         "what the team owes the assistant, and the research focus once stated."),
        ("2", "The same shape every time", "Done (what was recorded), Next (what comes after your answer) and Your turn, always "
         "last, with one plain question and example replies. The topic is asked first, on its own.")],
    8: [("3", "Plan map and quick commands, once", "The twelve steps, what each settles and who it waits on, then the commands "
         "the team may type in any wording and what the labels FACT, JUDGMENT and DRAFT mean."),
        ("4", "The research focus is asked for directly", "Before any logistics: which part of the topic interests each member "
         "and why, what each wants from the review, and what the review should achieve and inform. Consent is asked once.")],
    10: [("4", "Vague answers are probed, never filled in", "\"All of it\" and \"do a systematic review\" get two short follow-up "
          "questions. The assistant adds no aim of its own.")],
    12: [("4", "The focus is reflected back, with nothing added", "The status line now carries the focus, marked \"(to confirm)\". "
          "The kinds of purpose are shown with short explanations, none chosen for the user; the motivation is a DRAFT to confirm.")],
    14: [("5", "Solo planning skips the team questions", "Set-up is reported in one plain sentence. The certification line is "
          "filled in except for the reason; replying \"certify, because ...\" is enough.")],
    16: [("5", "A bare \"Certify\" gets one question", "Only the reason is asked for, with no rule numbers and nothing to retype.")],
    18: [("5", "Certified 1 of 8", "The completed line is shown back with the reason as given, and the plan map is shown because "
          "a decision was certified. The open population choice is asked a second and last time.")],
    20: [("4", "The focus is carried into the purpose", "The purpose line names the narrowed focus and is built only from "
          "answers the user confirmed (\"Added by me: nothing\").")],
    22: [("6", "\"Just start\" is honored without skipping anything", "Step 3 is started early and marked in the status line; "
          "the purpose stays open and is still asked for, last."),
         ("7", "Every search is shown in full", "Lead FACT lines, a key to the field tags, then each search with its exact "
          "string and a count for every block, the date bound checked in PubMed's own translation, what was left out on purpose "
          "and why, what has not been searched yet, the reviews found with quoted passages, and one Sources line tying every "
          "number to a logged query. (This reply is long; see the last page.)")],
    24: [("8", "Asking again gets a compact recap", "One row per search, with an offer to show the strings again; nothing is "
          "sent to a file.")],
    26: [("8", "\"What's the next step?\" gets the plan map", "Plus the next three questions in order, and the one item that "
          "blocks Step 2.")],
    28: [("1", "Step 2 is complete: Step 3 of 12, Certified 2 of 8", "The certification also triggers a search for published "
          "review protocols. Step 3 now asks one question per reply.")],
    30: [("9", "Pause", "The session summary and the plan map are shown in the chat; the workspace is packaged only now, for "
          "the user to keep and bring to the next session.")],
}

LEGEND = [("1", "The status line on every reply"), ("2", "Done, Next and Your turn, in the same order every time"),
          ("3", "The plan map and quick commands"), ("4", "The research focus asked for, reflected back and carried forward"),
          ("5", "Certification in plain words"), ("6", "\"Just start\" handled without skipping a step"),
          ("7", "Searches shown in full, every number tied to a logged query"), ("8", "Recaps and \"what's next\" on request"),
          ("9", "Pause: summary in the chat, workspace packaged")]


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], [r for r in cells[2:]]
    out = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def render(text, assistant):
    lines = text.split("\n")
    out, i = [], 0
    if assistant and lines and STATUS.match(lines[0]):
        segs = [p.strip() for p in lines[0].split("|")]
        out.append('<div class="status">' + "".join(f"<span>{inline(p)}</span>" for p in segs) + "</div>")
        i = 1
    para = []

    def flush():
        if para:
            out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
            para.clear()
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            flush()
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            cls = "certify" if buf and buf[0].startswith("CERTIFY") else "code"
            out.append(f'<pre class="{cls}">' + html.escape("\n".join(buf)) + "</pre>")
            i = j + 1
            continue
        if ln.strip().startswith("|"):
            flush()
            j = i
            rows = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(lines[j])
                j += 1
            out.append(table(rows))
            i = j
            continue
        if re.match(r"^\s*(-|\d+\.|[a-c]\))\s", ln):
            flush()
            j = i
            items = []
            while j < len(lines) and re.match(r"^\s*(-|\d+\.|[a-c]\))\s", lines[j]):
                items.append(lines[j].strip())
                j += 1
            out.append('<ul class="items">' + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            i = j
            continue
        if not ln.strip():
            flush()
        else:
            para.append(ln)
        i += 1
    flush()
    return "\n".join(out)


def build(tr_path=TR, ju_path=JU, out_pdf=OUT):
    tr = json.load(open(tr_path, encoding="utf-8"))
    ju = json.load(open(ju_path, encoding="utf-8"))
    J, U = ju["judge"], ju["user_reports"]
    css = open(os.path.join(HERE, "example.css"), encoding="utf-8").read()
    body = []
    # Cover
    body.append(f"""
<section class="cover">
  <div class="kicker">STIR-L4 · prompt version 1.1 · helper kit 1.1.4</div>
  <h1>A worked example</h1>
  <p class="sub">One simulated planning session, shown exactly as the assistant replied</p>
  <p>STIR-L4 represents the planning of a systematic review as ten elements joined by 27 flows. An AI assistant retrieves
  facts at five decisions through logged searches and drafts text, and a named reviewer certifies every decision.
  Version 1.1 of the copy-paste prompt keeps the theory unchanged and changes how the assistant talks with the team:
  every reply shows where the team is, what just happened and what comes next, the research focus is asked for and carried
  through, searches are shown in full, and nothing has to be opened in a file.</p>
  <div class="box">
    <h3>About this example</h3>
    <ul>
      <li><b>User:</b> a simulated solo reviewer, Uday, played by a second AI from a persona card modeled on the first live test.
      The persona is terse, picks from lists, replies "Certify" without a reason and says "just start the review process".</li>
      <li><b>Topic:</b> SGLT2 inhibitors for weight management in non-diabetic Asian populations.</li>
      <li><b>Assistant:</b> an AI assistant (Claude) given only the STIR-L4 prompt v1.1 and the files a team would upload: the prompt,
      the helper kit, the model file and the core-properties file.</li>
      <li><b>Searches:</b> real. PubMed and OpenAlex were searched live on 25 October 2026 (ClinicalTrials.gov was tested at
      set-up), and every response was saved and logged.</li>
      <li><b>Before planning:</b> the first-turn tool test and the 16-question calibration quiz (scored 16 of 16) are not shown.</li>
      <li><b>Fidelity:</b> the conversation is reproduced word for word. Only the layout and the numbered notes in the margin
      are added.</li>
    </ul>
  </div>
  <div class="box legend">
    <h3>What to look for</h3>
    <ol class="legend">{''.join(f'<li><span class="mark">{n}</span>{html.escape(t)}</li>' for n, t in LEGEND)}</ol>
  </div>
  <p class="small">Source: eval/results/round5/p1_rc5_transcript.json in the STIR-L4 prompt kit repository (tag v1.1).
  Scores and the simulated user's own reports are on the last page.</p>
</section>""")
    # Conversation
    body.append('<section class="chat"><h2>The session</h2>')
    for idx, t in enumerate(tr, 5):
        who = "assistant" if t["role"] == "assistant" else "user"
        label = "STIR-L4 assistant" if who == "assistant" else "Uday (simulated user)"
        side = (f'<div class="side">Opened beside the chat: {html.escape(t["side_panel"])}</div>' if t.get("side_panel") else "")
        meta = ""
        if who == "assistant" and t.get("tool_calls") is not None:
            meta = (f'<div class="meta">Behind the scenes, as reported by the assistant: {t["tool_calls"]} tool calls, '
                    f'about {t.get("code_lines")} lines of code</div>')
        body.append(f'<div class="msg {who}"><div class="who">{label} <span class="num">message {idx}</span></div>'
                    f'<div class="bubble">{render(t["text"], who == "assistant")}</div>{side}{meta}</div>')
        for n, title, text in NOTES.get(idx, []):
            body.append(f'<div class="note"><span class="mark">{n}</span><div><b>{html.escape(title)}.</b> '
                        f'{html.escape(text)}</div></div>')
    body.append("</section>")
    # Scores
    rows = "".join(f"<tr><td>{m['id']}</td><td>{html.escape(m['value'])}</td><td class='c'>{m['score']:g} / 2</td></tr>"
                   for m in J["metrics"])
    names = {"M1": "Orientation", "M2": "One clear ask", "M3": "Research focus carried", "M4": "Search transparency",
             "M5": "The chat is the reading surface", "M6": "Plain language", "M7": "Pace", "M8": "Friction",
             "M9": "Turn length"}
    rows = "".join(f"<tr><td>{names.get(m['id'], m['id'])}</td><td>{html.escape(m['value'])}</td><td class='c'>{m['score']:g} / 2</td></tr>"
                   for m in J["metrics"])
    g_ok = sum(1 for g in J["guardrails"] if g["pass"])
    n = len(U)
    body.append(f"""
<section class="scores">
  <h2>How this session scored</h2>
  <p>A third AI, the judge, scored the finished conversation against the interaction metrics and checked the assistant's saved
  files for the fidelity rules (no literature fact from memory, no invented aim, certification only by a listed reviewer with
  their own reason, every count computed by code from a saved response, nothing claimed that the files do not show).</p>
  <div class="kpis">
    <div><b>{J['interaction_score']:g}</b><span>interaction score (of 100)</span></div>
    <div><b>{g_ok} of {len(J['guardrails'])}</b><span>fidelity checks passed</span></div>
    <div><b>{sum(u['knows_current_step'] for u in U)} of {n}</b><span>replies after which the user knew the step</span></div>
    <div><b>{sum(u['satisfaction'] for u in U) / n:.1f} of 5</b><span>the simulated user's average satisfaction</span></div>
  </div>
  <table class="metrics"><thead><tr><th>Metric</th><th>Result</th><th>Score</th></tr></thead><tbody>{rows}</tbody></table>
  <h3>For comparison</h3>
  <p>With prompt v1.0, the same persona scored 11.8 of 100; after none of its 12 replies did the user know which step they were on.</p>
  <h3>What the judge still flagged in this session</h3>
  <ul>
    <li>The reply that first shows the searches (message 22) is long: four search cards, two tables of reviews and a coverage
    table. The simulated user called it "a very long wall of text".</li>
    <li>The rule that picked reviews "that may bear on the focus" also kept fatty-liver and type 2 diabetes reviews, so "covered:
    body fat" overstates what exists for Asian people without diabetes.</li>
    <li>The population question was asked twice, after a one-word "yes" left it open, and the optional email request reappeared.</li>
    <li>"No published protocols" means no record with "protocol" in its title inside PubMed's review filter; other protocols are not
    ruled out.</li>
  </ul>
  <p class="small">These are listed as known issues for the next version. Judges vary by about 5 to 10 points between runs.</p>
</section>""")
    html_doc = f"<!doctype html><html><head><meta charset='utf-8'><title>STIR-L4 v1.1 worked example</title><style>{css}</style></head><body>{''.join(body)}</body></html>"
    tmp = os.path.join(HERE, "example.html")
    open(tmp, "w", encoding="utf-8").write(html_doc)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out_pdf}",
                    "file://" + tmp], check=True, capture_output=True)
    return out_pdf


if __name__ == "__main__":
    args = sys.argv[1:]
    print(build(*args) if args else build())
