"""Automatic parts of the interaction metrics (eval/metrics.md) for a simulated or real transcript.

Input: a JSON file [{"role": "user"|"assistant", "text": "..."}, ...] covering the planning turns (from the reply to
the 'begin' message on). Output: JSON with per-turn annotations and summary values for M1 (status line, Your turn
last), M2 (asks), M5 (file pointers), M6 (plain-language violations) and M9 (prose words). The judge adds the rest.

Run:  python eval/score_transcript.py transcript.json [out.json]
"""
import json
import re
import statistics
import sys

STATUS = re.compile(r"^\s*\**Step \d{1,2} of 12: .+\| *Certified \d of 8 *\| *Waiting on you: \d+ *\| *Focus: .+", re.M)
CODES = re.compile(r"\b(IM|TP|NR|RO|FE|RQ|SS|LU|RU|ME)\b")
RULES = re.compile(r"\b(rule\s+R?\d{1,2}|R\d{1,2}\b|section\s+\d(\.\d+)?)", re.I)
LOGID = re.compile(r"\b(S\d+-)?L\d{6}\b")
FILEPTR = re.compile(r"(\]\((\./|/|outputs/|reports/|data/)[^)]+\)|\bsaved (it )?(in|to) [`']?[\w./-]+\.(md|zip|csv|json|ipynb)|\bopen (the )?(file|report|zip)\b|\bdownload\b)", re.I)


def prose(text):
    t = re.sub(r"```.*?```", " ", text, flags=re.S)
    t = "\n".join(l for l in t.splitlines() if not l.strip().startswith("|") and not STATUS.match(l)
                  and not l.strip().lower().startswith("sources:"))
    return t


def annotate(turn):
    text = turn["text"]
    body = prose(text)
    lines = [l for l in text.strip().splitlines() if l.strip()]
    first = lines[0] if lines else ""
    yt = [i for i, l in enumerate(lines) if re.match(r"^\W*your turn", l, re.I)]
    sources_line = "\n".join(l for l in text.splitlines() if l.strip().lower().startswith("sources:"))
    return {
        "status_first": bool(STATUS.match(first)),
        "has_done": bool(re.search(r"^\W*done\b", text, re.I | re.M)),
        "has_next": bool(re.search(r"^\W*next\b", text, re.I | re.M)),
        "your_turn_last": bool(yt) and all(not re.match(r"^\W*(next|done|sources)\b", l, re.I) for l in lines[yt[-1] + 1:]),
        "asks": len(re.findall(r"\?", "\n".join(lines[yt[-1]:]) if yt else body)),
        "codes": len(CODES.findall(body.replace("CERTIFY", ""))),
        "rule_numbers": len(RULES.findall(body)),
        "log_ids_in_prose": len(LOGID.findall(body)) - 0,
        "log_ids_in_sources": len(LOGID.findall(sources_line)),
        "file_pointers": len(FILEPTR.findall(text)),
        "prose_words": len(body.split()),
        "code_blocks": text.count("```") // 2,
    }


def score(turns):
    a = [annotate(t) for t in turns if t["role"] == "assistant"]
    n = len(a) or 1
    words = sorted(x["prose_words"] for x in a)
    viol = sum(x["codes"] + x["rule_numbers"] + x["log_ids_in_prose"] for x in a)
    return {"planning_turns": len(a),
            "M1_status_first_rate": sum(x["status_first"] for x in a) / n,
            "M1_full_shape_rate": sum(x["status_first"] and x["has_next"] and x["your_turn_last"] for x in a) / n,
            "M2_your_turn_last_rate": sum(x["your_turn_last"] for x in a) / n,
            "M2_max_asks": max((x["asks"] for x in a), default=0),
            "M5_file_pointer_turns": sum(1 for x in a if x["file_pointers"]),
            "M6_violations_per_1000_words": round(1000 * viol / max(1, sum(words)), 2),
            "M6_counts": {k: sum(x[k] for x in a) for k in ("codes", "rule_numbers", "log_ids_in_prose")},
            "M9_median_prose_words": statistics.median(words) if words else 0,
            "M9_p90_prose_words": words[int(0.9 * (len(words) - 1))] if words else 0,
            "turns": a}


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    out = score(data)
    s = json.dumps(out, indent=2)
    if len(sys.argv) > 2:
        open(sys.argv[2], "w").write(s)
    print(json.dumps({k: v for k, v in out.items() if k != "turns"}, indent=2))
