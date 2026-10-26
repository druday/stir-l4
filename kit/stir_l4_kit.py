"""STIR-L4 helper kit, version 1.1.9 (for STIR-L4 prompt version 1.5).

One file the team uploads with the prompt. It does the deterministic work of the prompt's section 3 and the
record keeping of rules R4 to R8 and R11, so that each assistant turn needs a few short calls instead of new code.
It never prints and never asks the team anything: every public function returns a value, usually a Result dict
with "ok", "md" (chat-ready Markdown, full element names, no log ids in sentences), "log_ids", "warnings" (for the
assistant), "refusal" (one plain sentence, or None) and "fallback" (a manual-retrieval request, or None).

Use:  import stir_l4_kit as k; k.init(...) once; in later sessions k.use(root) then k.session_start("S2").
License: MIT (LICENSE-CODE). If you use STIR-L4, please cite the STIR-L4 paper (Singh, Walji, Fenton, Jiang) and send the
authors refinements and specific improvements (uday.pratapsingh@uth.tmc.edu).
Dependencies: Python 3.11+, pyyaml; requests if installed (otherwise urllib). Hosts contacted: NCBI E-utilities,
OpenAlex and ClinicalTrials.gov only. Credentials are read from the environment or the workspace .env file
(NCBI_EMAIL, NCBI_API_KEY, OPENALEX_API_KEY) and are never returned, logged or shown.
"""
import csv
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import yaml

try:
    import requests as _requests
except ImportError:  # pragma: no cover
    _requests = None

__version__ = "1.1.9"

ELEMENTS = {"IM": "Individual Motivation", "TP": "Team's Purpose", "NR": "Need for a Review", "RO": "Review Objective",
            "FE": "Feasibility", "RQ": "Research Question", "SS": "Search Strategy", "LU": "Literature Universe",
            "RU": "Review Universe", "ME": "Methodology", "PAO": "Paper as an Object",
            "LAT": "Literature as a Tensor", "RED": "Registering Evidence Dynamically"}
VARIABLES = ["IM", "TP", "NR", "RO", "FE", "RQ", "SS", "ME"]
CERT_ORDER = ["IM", "TP", "NR", "RO", "FE", "RQ", "PAO", "LAT", "RED", "SS", "ME"]
KINDS = ["query", "manual_retrieval", "computation", "question", "answer", "draft", "certification", "reopen",
         "amendment", "screening_decision", "calibration", "consent", "registration", "commitment", "correction", "note"]
LOG_FIELDS = ["id", "time_utc", "actor", "kind", "element", "source", "endpoint", "parameters", "date_range", "n_total",
              "n_retrieved", "raw_path", "sha256", "derived_path", "model", "decision", "text", "reason", "refers_to"]
STEPS = [(1, "Topic", []), (2, "Interests, focus and purpose", ["IM", "TP"]), (3, "Need for a Review", ["NR"]),
         (4, "Review Objective", ["RO"]), (5, "Feasibility", ["FE"]), (6, "Research Question", ["RQ"]),
         (7, "Before the search", ["PAO", "LAT", "RED"]), (8, "Search Strategy", ["SS"]),
         (9, "Scoping and pilot screening", []), (10, "Methodology", ["ME"]), (11, "Protocol", []),
         (12, "End of planning", [])]
SETTLES = {1: "the provisional topic", 2: "each member's interest and motivation; the team's focus and purpose",
           3: "whether a new review or an update is needed", 4: "what the review should achieve",
           5: "go, narrow, broaden or defer", 6: "the question and eligibility criteria",
           7: "extraction form, property registry and atlas", 8: "search strings and stopping rule",
           9: "provisionally included studies", 10: "methods for the protocol", 11: "protocol and registration",
           12: "a snapshot of the plan and the provisional studies"}
SOURCE_NAMES = {"pubmed": "PubMed", "openalex": "OpenAlex", "ctgov": "ClinicalTrials.gov", "mesh": "MeSH"}
ONGOING = ["RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION", "ACTIVE_NOT_RECRUITING"]
FOLDERS = ["env", "log", "plan", "notes", "data/raw", "data/derived", "notebooks", "pao", "lat", "red", "protocol",
           "reports"]
SECRET_NAMES = ["NCBI_API_KEY", "NCBI_EMAIL", "OPENALEX_API_KEY"]
HOSTS = {"eutils.ncbi.nlm.nih.gov", "api.openalex.org", "clinicaltrials.gov"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
STRENGTH_RANK = {"strong": 0, "moderate": 1, "weak": 2}
COMMANDS = ('"where are we" · "next" (never accepts or certifies) · "why" (how this answer affects your other decisions) · "show <item>" · '
            '"skip" (the question stays open) · "back" (reopens only if the team agrees) · "pause" (summary and stop)')
GLOSSARY = [("[Mesh]", "a MeSH subject heading, including narrower headings"), ("[mh]", "a MeSH subject heading, including narrower headings"),
            ("[mh:noexp]", "a MeSH heading without narrower headings"), ("[majr]", "a MeSH heading as a major topic"),
            ("[tiab]", "words in the title or abstract"), ("[ti]", "words in the title"), ("[pt]", "publication type"),
            ("[sb]", "a PubMed subset, such as systematic reviews"), ("[crdt]", "the date the record was created in PubMed"),
            ("[pmid]", "a PubMed identifier"), ("*", "any word ending (truncation)"), ('"', "an exact phrase"),
            (" AND ", "every block must match"), (" OR ", "any one term in the block may match"),
            (" NOT ", "excludes records that match"), ("(", "parentheses group the terms of a block")]
STOP = set("""a an the and or of in on for to with without by from at as is are be been being this that these those
which what who whom whose how why when where whether into onto over under about across after before between during
than then there their them they it its our your we you i me my mine yours he she his her not no nor so such very can
could should would may might will shall do does did done also more most less least much many some any each other
review reviews systematic study studies evidence team purpose focus research question questions inform informs
decision decisions work topic aim aims want wants hope hopes interest interests interested area part please plan
planning about whole""".split())

_ROOT = None
_LAST_REQ = {}


class KitError(Exception):
    """A programming error in a call to the kit (not a refusal)."""


# ---------------------------------------------------------------- basics

def _now():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today(sep="/"):
    return _dt.datetime.now(_dt.timezone.utc).strftime(f"%Y{sep}%m{sep}%d")


def _res(ok=True, md="", log_ids=None, warnings=None, refusal=None, fallback=None, **extra):
    r = {"ok": ok, "md": md, "log_ids": list(log_ids or []), "warnings": list(warnings or []), "refusal": refusal,
         "fallback": fallback}
    r.update(extra)
    return r


def _refuse(text, **extra):
    return _res(False, md=text, refusal=text, **extra)


def _p(*parts):
    if _ROOT is None:
        raise KitError("No workspace: call init(...) or use(root) first.")
    return os.path.join(_ROOT, *parts)


def _rel(path):
    return os.path.relpath(path, _ROOT).replace(os.sep, "/")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _yload(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _ydump(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=110)
    os.replace(tmp, path)


def _jload(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _jdump(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def _read(path, errors=None):
    with open(path, encoding="utf-8", errors=errors) as f:
        return f.read()


def _jread(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _esc(s, n=120):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    s = s.replace("|", "/").replace("<", "‹").replace(">", "›").replace("[", "(").replace("]", ")")
    s = re.sub(r"([*_`#])", r"\\\1", s)
    return s if len(s) <= n else s[: n - 1] + "…"


def _fmt(n):
    return "unknown" if n is None else f"{n:,}"


def name(code):
    """Full name of an element code; codes never appear in chat text."""
    return ELEMENTS.get(code, code)


def _code(el):
    if el in ELEMENTS:
        return el
    t = str(el or "").strip().lower().replace("\u2019", "'")
    if t.upper() in ELEMENTS:
        return t.upper()
    for c, n in ELEMENTS.items():
        if t in (n.lower(), n.lower().replace("'", "")):
            return c
    return None


# ---------------------------------------------------------------- environment and secrets

def _dotenv():
    vals = {}
    if _ROOT and os.path.exists(_p(".env")):
        for line in _read(_p(".env")).splitlines():
            m = re.match(r"\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$", line)
            if m:
                vals[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return vals


def _secret(nm):
    return os.environ.get(nm) or _dotenv().get(nm) or None


def _redact(obj):
    secrets = {v: f"<redacted:{k}>" for k in SECRET_NAMES if (v := _secret(k))}
    if isinstance(obj, dict):
        return {k: _redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    if isinstance(obj, str):
        for v, tag in secrets.items():
            obj = obj.replace(v, tag)
        return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<redacted:email>", obj)
    return obj


# ---------------------------------------------------------------- HTTP (allowlisted, throttled, retried)

def _http(url, *, params=None, data=None, headers=None, timeout=40):
    host = urllib.parse.urlparse(url).hostname
    if host not in HOSTS:
        raise KitError(f"Host not allowed: {host}")
    gap = 0.12 if (host.startswith("eutils") and _secret("NCBI_API_KEY")) else 0.35
    wait = _LAST_REQ.get(host, 0) + gap - time.time()
    if wait > 0:
        time.sleep(wait)
    headers = dict(headers or {})
    headers.setdefault("User-Agent", f"stir_l4_kit/{__version__}")
    err = None
    for attempt in range(4):
        _LAST_REQ[host] = time.time()
        try:
            if _requests is not None:
                r = (_requests.post(url, data=data, params=params, headers=headers, timeout=timeout) if data is not None
                     else _requests.get(url, params=params, headers=headers, timeout=timeout))
                status, body, wait_s = r.status_code, r.content, r.headers.get("retry-after")
            else:  # pragma: no cover
                q = url + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
                req = urllib.request.Request(q, data=urllib.parse.urlencode(data).encode() if data else None,
                                             headers=headers)
                try:
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        status, body, wait_s = resp.status, resp.read(), None
                except urllib.error.HTTPError as e:
                    status, body, wait_s = e.code, e.read(), e.headers.get("Retry-After")
            if status == 429 and str(wait_s or "").isdigit() and int(wait_s) > 60:
                return status, body, f"HTTP 429: allowance used up, retry after {int(wait_s)} s"
            if status in (429, 500, 502, 503, 504):
                err = f"HTTP {status}"
                time.sleep(2 ** attempt)
                continue
            return status, body, None
        except Exception as e:  # network blocked or unreachable
            err = f"{type(e).__name__}: {e}"
            time.sleep(1 + attempt)
    return None, b"", err


def _ncbi_params(extra):
    p = {"tool": "stir_l4_kit"}
    if _secret("NCBI_EMAIL"):
        p["email"] = _secret("NCBI_EMAIL")
    if _secret("NCBI_API_KEY"):
        p["api_key"] = _secret("NCBI_API_KEY")
    p.update(extra)
    return p


def _logged_params(params):
    out = {}
    for k, v in params.items():
        if k == "email":
            out[k] = "<redacted:NCBI_EMAIL>"
        elif k == "api_key":
            out[k] = "<redacted:NCBI_API_KEY>"
        else:
            out[k] = v
    return _redact(out)


# ---------------------------------------------------------------- session state

def _session():
    return _jload(_p("env", "session.json"), {}) or {}


def _session_set(**kv):
    s = _session()
    s.update(kv)
    _jdump(_p("env", "session.json"), s)


def use(root, session=None):
    """Point the kit at an existing workspace (later sessions)."""
    global _ROOT
    root = os.path.abspath(root)
    if not os.path.exists(os.path.join(root, "log", "actions.jsonl")):
        raise KitError(f"No STIR-L4 workspace at {root}")
    _ROOT = root
    if session:
        _session_set(session=session)
    return root


# ---------------------------------------------------------------- log (append-only, 19 fields)

def _records():
    path = _p("log", "actions.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def records(kind=None, element=None, since=None, last=None):
    """Log records, optionally filtered by kind, element, id (since, exclusive) or the last n."""
    rows = _records()
    if since:
        ids = [r["id"] for r in rows]
        rows = rows[ids.index(since) + 1:] if since in ids else rows
    if kind:
        rows = [r for r in rows if r["kind"] == kind]
    if element:
        rows = [r for r in rows if r["element"] == element]
    return rows[-last:] if last else rows


def _lock():
    lock = _p("log", ".lock")
    for _ in range(200):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock
        except FileExistsError:
            if time.time() - os.path.getmtime(lock) > 30:
                os.remove(lock)
            time.sleep(0.05)
    raise KitError("Log is locked")


def _append(kind, **f):
    if kind not in KINDS:
        raise KitError(f"Unknown kind {kind}")
    lock = _lock()
    try:
        rows = _records()
        prefix = _session().get("prefix") or ""
        n = 1 + sum(1 for r in rows if r["id"].startswith(prefix + "L") or (not prefix and r["id"].startswith("L")))
        rid = f"{prefix}L{n:06d}"
        known = {r["id"] for r in rows}
        refs = f.get("refers_to")
        if refs:
            refs = [refs] if isinstance(refs, str) else list(refs)
            missing = [x for x in refs if x not in known]
            if missing:
                raise KitError(f"refers_to unknown ids: {missing}")
        rec = {k: None for k in LOG_FIELDS}
        rec.update({"id": rid, "time_utc": _now(), "actor": "agent", "kind": kind})
        for k, v in f.items():
            if k not in LOG_FIELDS:
                raise KitError(f"Unknown log field {k}")
            rec[k] = v
        rec["refers_to"] = refs or None
        if rec["parameters"] is not None:
            rec["parameters"] = _redact(rec["parameters"])
        if rec["actor"] == "agent" and rec["model"] is None:
            rec["model"] = _session().get("model")
        with open(_p("log", "actions.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rid
    finally:
        os.remove(lock)


def log(kind, *, text=None, actor="agent", element=None, decision=None, reason=None, refers_to=None,
        derived_path=None, parameters=None, time_utc="now"):
    """Append a question, answer, draft, computation, note, consent or correction (other kinds have own functions)."""
    if kind not in ("question", "answer", "draft", "computation", "note", "consent", "correction"):
        raise KitError(f"Use the dedicated function for kind {kind}")
    if element is not None and _code(element) is None:
        raise KitError(f"Unknown element {element}")
    f = dict(text=text, actor=actor, element=_code(element) if element else None, decision=decision, reason=reason,
             refers_to=refers_to, derived_path=derived_path, parameters=parameters)
    if time_utc is None:
        f["time_utc"] = None
    elif time_utc != "now":
        if actor == "agent" or not re.match(r"\d{4}-\d\d-\d\dT\d\d:\d\d", str(time_utc)):
            raise KitError("A supplied time must be ISO 8601 and given by a member")
        f["time_utc"] = time_utc
    return _append(kind, **f)


def ask(to, text, *, element=None, blocking=True, items=1):
    """Log a question to a member, role or 'team'. Blocking questions (the current step needs the answer) count as
    'Waiting on you' until answered; non-blocking ones ('When convenient') are logged but never counted."""
    return log("question", text=f"to {to}: {text}", element=element,
               parameters={"to": to, "blocking": bool(blocking), "items": max(1, int(items))})


def _open_asks():
    rows = _records()
    answered = {x for r in rows if r["kind"] in ("answer", "manual_retrieval", "certification", "amendment")
                for x in (r["refers_to"] or [])}
    return [r for r in rows if r["kind"] == "question" and r["id"] not in answered
            and not (r["parameters"] or {}).get("closed")]


def answer(by, text, *, element=None, refers_to=None, verbatim=False, relayed_by=None):
    """Log a member's answer (a JUDGMENT). Verbatim only with logged consent. Links to the open question if any."""
    if verbatim and not _consents().get(by):
        return _refuse(f"I can keep {by}'s exact words only after they agree to it; I have kept a summary instead.")
    if refers_to is None:
        opens = [r for r in _open_asks() if (r["parameters"] or {}).get("to") in (by, "team", "all")]
        refers_to = [opens[-1]["id"]] if opens else None
    t = (f"relayed by {relayed_by}: " if relayed_by else "") + text
    return log("answer", text=t, actor=by, element=element, refers_to=refers_to,
               parameters={"verbatim": bool(verbatim), "relayed_by": relayed_by})


def _consents():
    out = {}
    for r in _records():
        if r["kind"] == "consent":
            out[r["actor"]] = bool((r["parameters"] or {}).get("verbatim"))
    return out


def consent(member, verbatim):
    """Record whether a member's exact words may be kept (otherwise summaries they confirm)."""
    return log("consent", actor=member, text=f"{member}: exact words {'may' if verbatim else 'may not'} be kept",
               parameters={"verbatim": bool(verbatim)})


def draft(element, text, *, uses=()):
    """Log a DRAFT; every id in uses must be a retrieved or computed FACT."""
    rows = {r["id"]: r for r in _records()}
    bad = [u for u in uses if rows.get(u, {}).get("kind") not in ("query", "manual_retrieval", "computation")]
    if bad:
        raise KitError(f"uses must cite FACT records: {bad}")
    return log("draft", text=text, element=element, refers_to=list(uses) or None)


def correct(log_id, text, *, by="agent"):
    """Log a correction that refers to an earlier record (records are never edited)."""
    return log("correction", text=text, actor=by, refers_to=[log_id])


def preference(text, *, by):
    """Log a standing request about how the assistant talks with the team; session_start re-applies these."""
    return log("note", text=text, actor=by, parameters={"preference": True})


def early(step, *, requested_by, open_items):
    """Log that the team asked to work ahead of order; the status line shows Early until earlier steps are done."""
    return log("note", actor=requested_by, text=f"Work ahead: Step {step}; still open: {'; '.join(open_items)}",
               parameters={"early": int(step), "open_items": list(open_items)})


# ---------------------------------------------------------------- model, flows and loops

def _model():
    return _yload(_p("plan", "STIR-L4_model_v1.0.yaml"))


def _flows():
    return _model()["flows"]


def state_space(code):
    """The state space of a variable, word for word from the model file."""
    for e in _model()["elements"]:
        if e["id"] == code:
            return list(e.get("state_space") or [])
    return []


def _cycles(flows):
    nodes = sorted({f["from"] for f in flows} | {f["to"] for f in flows})
    idx = {n: i for i, n in enumerate(nodes)}
    out = {n: [] for n in nodes}
    for f in flows:
        out[f["from"]].append(f)
    cyc = []

    def dfs(start, node, seen, path):
        for f in out[node]:
            t = f["to"]
            if t == start:
                cyc.append(path + [f])
            elif idx[t] > idx[start] and t not in seen:
                dfs(start, t, seen | {t}, path + [f])
    for s in nodes:
        dfs(s, s, {s}, [])
    return cyc


def check_model():
    """Check the saved model file against the structural facts of prompt section 1.3."""
    m = _model()
    fl = m["flows"]
    cyc = _cycles(fl)
    fb = sorted(f["id"] for f in fl if f["type"] == "feedback")
    rec = sorted(f["id"] for f in fl if f["class"] == "record")
    on_fe = sum(1 for c in cyc if any(f["from"] == "FE" or f["to"] == "FE" for f in c))
    with_fb = sum(1 for c in cyc if any(f["type"] == "feedback" for f in c))
    me_in = sorted(f["id"] for f in fl if f["to"] == "ME")
    me_out = sorted(f["id"] for f in fl if f["from"] == "ME")
    got = {"elements": len(m["elements"]), "flows": len(fl), "feedback": fb, "record": rec, "loops": len(cyc),
           "loops_with_feedback": with_fb, "feasibility_loops": on_fe, "methodology_in": me_in,
           "methodology_out": me_out}
    want = {"elements": 10, "flows": 27, "feedback": [2, 7, 13, 15, 17, 20, 21, 23], "record": [12, 13, 19, 20],
            "loops": 47, "loops_with_feedback": 46, "feasibility_loops": 40, "methodology_in": [8, 18, 22, 24, 25, 27],
            "methodology_out": [23]}
    mism = [k for k in want if got[k] != want[k]]
    _jdump(_p("data", "derived", "model_check.json"), {"computed": got, "expected": want, "mismatches": mism})
    lid = _append("computation", element=None, derived_path="data/derived/model_check.json",
                  text="Checked the model file against the structural facts of section 1.3", parameters={"mismatches": mism})
    md = ("Model check passed: 10 elements, 27 flows, 47 loops, Feasibility on 40." if not mism
          else f"Model check FAILED on: {', '.join(mism)}. Do not plan until the model file is replaced.")
    return _res(not mism, md, [lid], mismatches=mism, computed=got)


def flows_from(element):
    """Outgoing flows of an element: id, to, type, class, strength, meaning."""
    c = _code(element)
    return [dict(id=f["id"], to=f["to"], type=f["type"], cls=f["class"], strength=f["strength"], meaning=f["meaning"])
            for f in _flows() if f["from"] == c]


def _status_of(code):
    v = (_plan().get("variables") or {}).get(code)
    return v["status"] if v else None


def trace(changed, *, because=None):
    """Follow outgoing flows from the changed elements (R4): each element once, by strength, stop at unsettled."""
    changed = [_code(c) for c in ([changed] if isinstance(changed, str) else changed)]
    visited, frontier, steps = set(changed), list(changed), []
    candidates, stopped, stocks, drafts = [], [], [], []
    while frontier:
        reach = {}
        all_disclosed = all((m.get("motivation") or {}).get("disclosed", False) for m in _team().get("members", [])) \
            and bool(_team().get("members"))
        for src in frontier:
            for f in _flows():
                if f["id"] == 2 and all_disclosed:
                    continue  # flow 2 acts only when an undisclosed motivation conflicts with the purpose
                if f["from"] == src and f["to"] not in visited:
                    t = f["to"]
                    if t not in reach or STRENGTH_RANK[f["strength"]] < STRENGTH_RANK[reach[t]["strength"]]:
                        reach[t] = f
        order = sorted(reach.items(), key=lambda kv: (STRENGTH_RANK[kv[1]["strength"]], kv[1]["id"]))
        step, nxt = [], []
        for t, f in order:
            visited.add(t)
            st = _status_of(t)
            entry = {"element": t, "flow": f["id"], "strength": f["strength"], "meaning": f["meaning"], "status": st}
            step.append(entry)
            if t in ("LU", "RU"):
                stocks.append(entry)
                nxt.append(t)
            elif st in ("certified", "amended"):
                candidates.append(entry)
                nxt.append(t)
            elif st == "proposed":
                drafts.append(entry)
                stopped.append(entry)
            else:
                stopped.append(entry)
        if step:
            steps.append(step)
        frontier = nxt

    def say(e):
        return f"{name(e['element'])} ({e['meaning'][0].lower() + e['meaning'][1:].rstrip('.')}; flow {e['flow']}, {e['strength']})"

    def plain(e):
        return f"{name(e['element'])} ({e['meaning'][0].lower() + e['meaning'][1:].rstrip('.')})"
    any_cert = any(v["status"] in ("certified", "amended") for v in (_plan().get("variables") or {}).values())
    md = (("Nothing you have approved is affected." if any_cert else "") if not candidates
          else "This may change what you approved for " + "; ".join(plain(e) for e in candidates)
          + ". Nothing changes unless you agree.")
    if drafts:
        md += " Please check your draft of " + " and ".join(name(e["element"]) for e in drafts) + " against this."
    full = []
    for i, s in enumerate(steps, 1):
        full.append(f"{i}. " + "; ".join(say(e) + (" — not yet settled, stop" if e in stopped else "") for e in s))
    md_full = "\n".join(full) or "No outgoing flows reach another element."
    tid = _append("computation", text="Traced flows from " + ", ".join(name(c) for c in changed),
                  refers_to=[because] if because else None, parameters={"changed": changed})
    _jdump(_p("data", "derived", f"trace_{tid}.json"), {"changed": changed, "steps": steps})
    return _res(True, md, [tid], md_full=md_full, candidates=[e["element"] for e in candidates],
                drafts=[e["element"] for e in drafts], stopped_at=[e["element"] for e in stopped], steps=steps)


# ---------------------------------------------------------------- workspace set-up

def selftest(test_file="stir_l4_tool_test.txt", web=True):
    """First-turn tool test: one line of code, one web request, one small file written and read back."""
    lines = [f"Code: Python {sys.version.split()[0]} ran; 2 + 2 = {2 + 2}."]
    ok = True
    if web:
        st, body, err = _http(EUTILS + "einfo.fcgi", params={"retmode": "json", "tool": "stir_l4_kit"})
        good = st == 200 and b"einforesult" in body
        ok &= good
        lines.append("Web: NCBI E-utilities answered." if good else f"Web: no answer ({err or st}).")
    try:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("STIR-L4 tool test\n")
        good = _read(test_file).startswith("STIR-L4")
        lines.append(f"File: saved and read back {os.path.basename(test_file)}." if good else "File: read-back failed.")
    except OSError as e:
        ok = False
        lines.append(f"File: could not be saved ({e}).")
    lines.append(f"Helper kit {__version__} loaded.")
    return _res(ok, "\n".join(lines))


def _skeleton_plan():
    var = lambda: {"states": [], "decision": None, "status": "unsettled", "provisional": False, "certified_by": None,
                   "certified_at": None, "reason": None, "log_ids": []}
    return {"version": 1, "topic": {"text": None, "given_by": None, "log_id": None},
            "focus": {"text": None, "by_member": {}, "log_ids": []},
            "variables": {c: var() for c in VARIABLES},
            "stocks": {"LU": {"queries": []}, "RU": {"included": "data/derived/screening.csv"}},
            "registration": None}


def init(root="stir-l4-workspace", *, calibration, session="S1", prompt="STIR-L4_prompt_v1.5.txt",
         model="STIR-L4_model_v1.0.yaml", core_properties="STIR-L4_core_properties_v1.0.csv", git=True):
    """Create the workspace silently when the team says 'begin'; the calibration becomes the first two records.

    calibration = {"answers": <the quiz answers as given>, "score": <score as the team gave it>, "graded_by": <name>}
    """
    global _ROOT
    root = os.path.abspath(root)
    if os.path.exists(os.path.join(root, "log", "actions.jsonl")) and os.path.getsize(
            os.path.join(root, "log", "actions.jsonl")) > 0:
        _ROOT = root
        return _refuse("This workspace already has a log; I have opened it instead of starting again.")
    for k in ("answers", "score", "graded_by"):
        if not calibration.get(k):
            raise KitError(f"calibration needs {k}")
    _ROOT = root
    for d in FOLDERS:
        os.makedirs(_p(d), exist_ok=True)
    gi = _p(".gitignore")
    have = _read(gi).split("\n") if os.path.exists(gi) else []
    with open(gi, "a", encoding="utf-8") as f:
        for line in (".env", ".env.*", "data/raw/text/", "__pycache__/", "log/.lock", "*.tmp"):
            if line not in have:
                f.write(line + "\n")
    open(_p("log", "actions.jsonl"), "a").close()
    with open(_p("data", "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["path", "sha256", "log_id", "bytes"])
    _ydump(_p("plan", "plan.yaml"), _skeleton_plan())
    _ydump(_p("plan", "team.yaml"), {"members": [], "sources": [], "deadlines": None, "resources": None,
                                     "rules": None, "decisions_made": []})
    _jdump(_p("env", "session.json"), {"session": session, "started": _now(), "last_shown": {}, "map_shown": False,
                                       "model": None, "prefix": ""})
    warnings = []
    ids = [_append("calibration", text=str(calibration["answers"]), parameters={"part": "answers"}),
           _append("calibration", actor=calibration["graded_by"], text=str(calibration["score"]),
                   parameters={"part": "score"})]
    copies = [(prompt, "env"), (model, "plan"), (core_properties, "lat"), (os.path.abspath(__file__), "env")]
    for src, dest in copies:
        if src and os.path.exists(src):
            target = _p(dest, os.path.basename(src))
            if os.path.abspath(src) != os.path.abspath(target):
                shutil.copyfile(src, target)
            ids.append(_append("note", text=f"Saved {os.path.basename(src)} unchanged",
                               derived_path=_rel(target), sha256=sha256_file(target),
                               parameters={"kit_file": dest == "env" and src.endswith(".py")}))
        else:
            warnings.append(f"Missing file {src}: ask the team for it (section 3.2).")
    if not os.path.exists(_p("plan", "STIR-L4_model_v1.0.yaml")):
        warnings.append("No model file: generate it from section 1 of the prompt before tracing flows.")
    if git and shutil.which("git"):
        subprocess.run(["git", "-C", root, "init", "-q"], capture_output=True)
    elif git:
        warnings.append("git is not available; certifications will not be committed.")
    _session_set(start_log=ids[0], start_head=_git_head())
    return _res(True, "Workspace ready; your answers are now recorded as you give them.", ids, warnings)


def _git_head():
    if not shutil.which("git"):
        return None
    r = subprocess.run(["git", "-C", _ROOT, "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or None


def record_model(provider, model, *, version=None, settings=None, read_from):
    """Record the LLM of this session; read_from must be 'API response' or 'interface, read by <member>'."""
    if not (read_from == "API response" or str(read_from).startswith("interface, read by ")):
        return _refuse("I can record the model only as the interface or API reports it, not from my own memory.")
    path = _p("env", "model.json")
    entries = _jload(path, []) or []
    entry = {"session": _session().get("session"), "provider": provider, "model": model, "version": version,
             "settings": settings, "read_from": read_from, "time_utc": _now()}
    entries.append(entry)
    _jdump(path, entries)
    _session_set(model=f"{provider} {model}" + (f" {version}" if version else ""))
    return log("note", text=f"Model of this session: {provider} {model} {version or ''}".strip(),
               parameters={"read_from": read_from}, derived_path="env/model.json")


def setup(sources=("pubmed", "openalex", "ctgov")):
    """End of Step 2: lock the environment, check the model and smoke-test the sources; md is at most 3 lines."""
    warnings = []
    try:
        out = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=120)
        with open(_p("env", "requirements.lock"), "w") as f:
            f.write(out.stdout)
    except Exception as e:  # pragma: no cover
        warnings.append(f"pip freeze failed: {e}")
    lid = log("note", text="Recorded package versions", derived_path="env/requirements.lock")
    m = check_model()
    s = smoke_test(sources)
    works = [a for a, b in s["table"] if b.startswith("works")]
    broken = [a for a, b in s["table"] if not b.startswith("works")]
    gloss = {"PubMed": "PubMed (an index of medical journals)", "OpenAlex": "OpenAlex (an open index of research papers)",
             "ClinicalTrials.gov": "ClinicalTrials.gov (a registry of clinical trials)"}
    names_ = [gloss.get(a, a) for a in works]
    md = ("The search tools work: " + (", ".join(names_[:-1]) + " and " + names_[-1] if len(names_) > 1 else names_[0])
          + "." if works else "The search tools could not be reached.")
    if broken:
        md += " Not working yet: " + ", ".join(broken) + "; a member can run those searches instead."
        if any("daily allowance" in w for w in s["warnings"]):
            md += " (OpenAlex's free daily allowance is used up until midnight UTC.)"
    if not m["ok"]:
        md += " The model file failed its check; please upload the original file again."
    asks = []
    if not _secret("NCBI_EMAIL"):
        asks.append("If you like, type a contact email for PubMed searches (PubMed asks for one); I keep it private.")
    return _res(m["ok"] and s["ok"], md, [lid] + m["log_ids"] + s["log_ids"], warnings + s["warnings"],
                when_convenient=asks)


# ---------------------------------------------------------------- raw files, manifest, notebooks

def _save_pages(lid, source, endpoint, pages, ext):
    paths = []
    with open(_p("data", "manifest.csv"), "a", newline="", encoding="utf-8") as mf:
        w = csv.writer(mf)
        for i, body in enumerate(pages, 1):
            path = _p("data", "raw", f"{lid}_{source}_{endpoint}_{i}.{ext}")
            if os.path.exists(path):
                raise KitError(f"Raw file exists: {path}")
            with open(path, "wb") as f:
                f.write(body)
            w.writerow([_rel(path), sha256_file(path), lid, len(body)])
            paths.append(path)
    if len(paths) == 1:
        return _rel(paths[0]), sha256_file(paths[0])
    combined = hashlib.sha256("\n".join(sha256_file(p) for p in paths).encode()).hexdigest()
    return f"data/raw/{lid}_{source}_{endpoint}_*.{ext}", combined


def _next_id():
    rows = _records()
    prefix = _session().get("prefix") or ""
    return f"{prefix}L{1 + sum(1 for r in rows if r['id'].startswith(prefix + 'L') or (not prefix and r['id'].startswith('L'))):06d}"


def _nb_add(nb, call):
    if not nb:
        return
    path = _p("notebooks", f"{nb}.ipynb")
    cell = lambda src: {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}
    if os.path.exists(path):
        doc = _jload(path)
    else:
        doc = {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"name": "python3",
               "display_name": "Python 3", "language": "python"}}, "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": f"# {nb}\nRetrieval cells run only when RETRIEVE is True; "
             "the last cell recomputes every logged count from the saved raw files."},
            cell("import os, sys\nsys.path.insert(0, os.path.abspath('../env'))\nimport stir_l4_kit as k\n"
                 "k.use(os.path.abspath('..'))\nRETRIEVE = False"),
            cell("print(k.verify()['md'])")]}
    doc["cells"].insert(len(doc["cells"]) - 1, cell(f"if RETRIEVE:\n    {call}"))
    _jdump(path, doc)


def _call(fn, *args, **kw):
    a = [repr(x) for x in args] + [f"{k}={v!r}" for k, v in kw.items() if v is not None and k != "nb"]
    return f"k.{fn}({', '.join(a)})"


# ---------------------------------------------------------------- PubMed

def _translation_ok(tr, mindate, maxdate):
    tr = (tr or "").replace('"', "").replace(" ", "")
    return f"{mindate}:{maxdate}[Date-Create]" in tr


def pubmed_search(term, *, element, purpose="primary", search_date=None, mindate="1800/01/01", retmax=0,
                  ids=False, origin=None, label=None, nb=None, _block=False):
    """Count (and optionally list) PubMed records, bounded by Create Date; the count is logged only if checked."""
    el = _code(element)
    sb = "systematic[sb]" in term.replace(" ", "").lower()
    if sb and (el in ("FE", "SS") or purpose == "primary"):
        return _refuse("The systematic-review filter is only for finding existing reviews, not for counting primary studies.")
    if el == "NR" and purpose == "reviews" and not sb and not _block:
        return _refuse("A search for existing reviews needs the systematic-review filter, systematic[sb].")
    maxdate = (search_date or _today()).replace("-", "/")
    params = _ncbi_params({"db": "pubmed", "term": term, "datetype": "crdt", "mindate": mindate, "maxdate": maxdate,
                           "retmode": "json", "retmax": 9999 if ids else retmax})
    st, body, err = _http(EUTILS + "esearch.fcgi", params=params)
    if st != 200:
        return _res(False, "PubMed could not be reached, so this count is unknown for now.",
                    fallback=request_manual("the information specialist", "PubMed", pubmed_web_query(term, maxdate),
                                            element=el)["md"], warnings=[err or f"HTTP {st}"])
    lid = _next_id()
    raw, h = _save_pages(lid, "pubmed", "esearch", [body], "json")
    res = json.loads(body)["esearchresult"]
    count, idlist, tr = int(res.get("count", 0)), res.get("idlist", []), res.get("querytranslation", "")
    checked = _translation_ok(tr, mindate, maxdate)
    warnings = []
    lid2 = _append("query", element=el, source="pubmed", endpoint="esearch", parameters=_logged_params(params) | {
        "purpose": purpose, "origin": origin, "label": label}, date_range={"datetype": "crdt", "min": mindate, "max": maxdate},
                   n_total=count if checked else None, n_retrieved=len(idlist), raw_path=raw, sha256=h,
                   text=("Create Date bound checked in the query translation" if checked
                         else "count not logged: Create Date bound missing from the query translation"))
    if lid2 != lid:
        raise KitError("Log id changed during the search; another session may be writing at the same time.")
    if not checked:
        warnings.append("Create Date bound missing in translation; count not logged")
    if ids and count > 9999:
        warnings.append("More than 9,999 records: slice the Create Date range (pubmed_slices) before listing identifiers.")
    if el in ("NR", "RO", "FE", "RQ", "SS"):
        plan = _plan()
        plan["stocks"]["LU"]["queries"].append(lid)
        _save_plan(plan)
    _nb_add(nb, _call("pubmed_search", term, element=el, purpose=purpose, search_date=maxdate, mindate=mindate,
                      retmax=retmax, ids=ids or None))
    md = (f"PubMed, run {maxdate.replace('/', '-')}, records created up to that date (checked): {_fmt(count)} records"
          if checked else f"PubMed, run {maxdate.replace('/', '-')}: count unknown, because PubMed did not confirm "
          "the date bound; I will rerun it.")
    return _res(checked, md, [lid], warnings, count=count if checked else None, ids=idlist, translation=tr,
                raw_path=raw, term=term, search_date=maxdate)


def pubmed_web_query(term, search_date=None):
    """The string a member runs on PubMed's website, with the Create Date bound written in."""
    d = (search_date or _today()).replace("-", "/")
    return f"({term}) AND 1800/01/01:{d}[crdt]"


def pubmed_fetch(pmids, *, element, nb=None, batch=200):
    """Fetch PubMed records (XML), save them and return title, journal, year, DOI and publication types."""
    import xml.etree.ElementTree as ET
    pmids = [str(p) for p in pmids]
    pages = []
    for i in range(0, len(pmids), batch):
        st, body, err = _http(EUTILS + "efetch.fcgi", data=_ncbi_params(
            {"db": "pubmed", "id": ",".join(pmids[i:i + batch]), "retmode": "xml"}))
        if st != 200:
            return _res(False, "PubMed records could not be fetched just now.", warnings=[err or f"HTTP {st}"])
        pages.append(body)
    lid = _next_id()
    raw, h = _save_pages(lid, "pubmed", "efetch", pages, "xml")
    recs = []
    for body in pages:
        for a in ET.fromstring(body).findall("PubmedArticle"):
            art = a.find("MedlineCitation/Article")
            doi = next((x.text for x in a.findall("PubmedData/ArticleIdList/ArticleId") if x.get("IdType") == "doi"), None)
            recs.append({"pmid": a.findtext("MedlineCitation/PMID"),
                         "title": "".join(art.find("ArticleTitle").itertext()) if art is not None else "",
                         "journal": a.findtext("MedlineCitation/Article/Journal/ISOAbbreviation"),
                         "year": a.findtext("MedlineCitation/Article/Journal/JournalIssue/PubDate/Year")
                         or (a.findtext("MedlineCitation/Article/Journal/JournalIssue/PubDate/MedlineDate") or "")[:4],
                         "doi": doi, "pub_types": [p.text for p in a.findall("MedlineCitation/Article/PublicationTypeList/PublicationType")],
                         "abstract": " ".join("".join(x.itertext()) for x in a.findall("MedlineCitation/Article/Abstract/AbstractText"))})
        for a in ET.fromstring(body).findall("PubmedBookArticle"):
            bd = a.find("BookDocument")
            recs.append({"pmid": bd.findtext("PMID") if bd is not None else None,
                         "title": "".join((bd.find("ArticleTitle") if bd is not None and bd.find("ArticleTitle") is not None
                                           else bd.find("Book/BookTitle")).itertext()) if bd is not None else "",
                         "journal": "book chapter", "year": (bd.findtext("Book/PubDate/Year") if bd is not None else None),
                         "doi": None, "pub_types": ["Book chapter"],
                         "abstract": " ".join("".join(x.itertext()) for x in bd.findall("Abstract/AbstractText")) if bd is not None else ""})
    _append("query", element=_code(element), source="pubmed", endpoint="efetch", parameters={"id": pmids, "db": "pubmed"},
            n_total=len(pmids), n_retrieved=len(recs), raw_path=raw, sha256=h, text="Fetched PubMed records")
    _nb_add(nb, _call("pubmed_fetch", pmids, element=_code(element)))
    rows = ["| # | Title | Journal | Year | PMID |", "|---|---|---|---|---|"]
    rows += [f"| {i} | {_esc(r['title'])} | {_esc(r['journal'], 40)} | {r['year']} | {r['pmid']} |"
             for i, r in enumerate(recs, 1)]
    return _res(True, "\n".join(rows), [lid], records=recs)


def mesh_lookup(term, *, nb=None):
    """Look up Medical Subject Headings: esearch then esummary on db=mesh; keep descriptors."""
    st, body, err = _http(EUTILS + "esearch.fcgi", params=_ncbi_params({"db": "mesh", "term": term, "retmode": "json",
                                                                          "retmax": 20}))
    if st != 200:
        return _res(False, "The MeSH database could not be reached just now.", warnings=[err or f"HTTP {st}"])
    l1 = _next_id()
    raw1, h1 = _save_pages(l1, "mesh", "esearch", [body], "json")
    uids = json.loads(body)["esearchresult"].get("idlist", [])
    _append("query", source="mesh", endpoint="esearch", parameters={"db": "mesh", "term": term},
            n_total=int(json.loads(body)["esearchresult"].get("count", len(uids))),
            n_retrieved=len(uids), raw_path=raw1, sha256=h1, element="RQ")
    descs, scrs = [], []
    ids = [l1]
    if uids:
        st, body, err = _http(EUTILS + "esummary.fcgi", params=_ncbi_params({"db": "mesh", "id": ",".join(uids),
                                                                              "retmode": "json"}))
        if st == 200:
            l2 = _next_id()
            raw2, h2 = _save_pages(l2, "mesh", "esummary", [body], "json")
            res = json.loads(body)["result"]
            for u in uids:
                d = res.get(u, {})
                item = {"ui": d.get("ds_meshui"), "name": (d.get("ds_meshterms") or [None])[0],
                        "entry_terms": (d.get("ds_meshterms") or [])[1:],
                        "tree_numbers": [x.get("treenum") for x in d.get("ds_idxlinks", []) if x.get("treenum")],
                        "scope_note": d.get("ds_scopenote")}
                (descs if d.get("ds_recordtype") == "descriptor" else scrs).append(item)
            _append("query", source="mesh", endpoint="esummary", parameters={"db": "mesh", "id": uids},
                    n_total=len(uids), n_retrieved=len(descs) + len(scrs), raw_path=raw2, sha256=h2, element="RQ",
                    refers_to=[l1])
            ids.append(l2)
    _nb_add(nb, _call("mesh_lookup", term))
    lines = [f"- **{_esc(d['name'])}** ({d['ui']}); also: {', '.join(_esc(x, 40) for x in d['entry_terms'][:5]) or '—'}"
             for d in descs]
    md = (f"Medical Subject Headings for \"{_esc(term, 60)}\":\n" + ("\n".join(lines) or "- none found")
          + (f"\nAlso {len(scrs)} supplementary concept record(s), not headings." if scrs else ""))
    return _res(True, md, ids, descriptors=descs, supplementary=scrs)


def known_item_check(term, pmids=None, *, element="SS", search_date=None, nb=None):
    """Check which known relevant studies a search retrieves (Step 8)."""
    if pmids is None:
        path = _p("data", "derived", "known_items.csv")
        pmids = [r["pmid"] for r in csv.DictReader(_read(path).splitlines())] if os.path.exists(path) else []
    pmids = [str(p) for p in pmids]
    if not pmids:
        return _refuse("There are no known studies to check yet; please list the studies you already know are relevant.")
    q = f"({term}) AND ({' OR '.join(p + '[pmid]' for p in pmids)})"
    r = pubmed_search(q, element=element, purpose="primary", search_date=search_date, ids=True, nb=nb)
    if not r["ok"]:
        return r
    found = set(r["ids"])
    rows = [{"pmid": p, "retrieved": p in found} for p in pmids]
    out = _p("data", "derived", f"{r['log_ids'][0]}_known_items.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["pmid", "retrieved"])
        w.writeheader()
        w.writerows(rows)
    missed = [p for p in pmids if p not in found]
    md = f"Known studies retrieved: {len(pmids) - len(missed)} of {len(pmids)}" + (f"; missed: {', '.join(missed)}" if missed else "")
    return _res(True, md, r["log_ids"], found=sorted(found), missed=missed)


# ---------------------------------------------------------------- OpenAlex and ClinicalTrials.gov

def openalex_works(search=None, *, element=None, filter=None, from_date=None, to_date=None, corpus="core", per_page=100,
                   max_pages=1, nb=None, purpose=None, label=None, origin=None):
    """Search OpenAlex works (publication dates up to the search date by default); without an API key only the
    first page can be read."""
    key = _secret("OPENALEX_API_KEY")
    if to_date is None and purpose != "smoke test":
        to_date = _today("-")
    f = [x for x in [filter, from_date and f"from_publication_date:{from_date}", to_date and f"to_publication_date:{to_date}"] if x]
    params = {"per-page": min(per_page, 100), "cursor": "*"}
    if search:
        params["search"] = search
    if f:
        params["filter"] = ",".join(f)
    if corpus != "core":
        params["corpus"] = corpus
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    pages, n_total, warnings = [], None, []
    for i in range(max_pages if key else 1):
        st, body, err = _http("https://api.openalex.org/works", params=params, headers=headers)
        if st != 200:
            if not pages:
                md = "OpenAlex could not be reached just now, so this count is unknown."
                if st == 429 and not key:
                    md = ("OpenAlex's free daily allowance for this network is used up (it resets at midnight UTC), so "
                          "this count is unknown. A free access code, added by a member to the private settings file, "
                          "lifts the limit.")
                return _res(False, md, warnings=[err or f"HTTP {st}"])
            break
        pages.append(body)
        d = json.loads(body)
        n_total = d["meta"]["count"] if n_total is None else n_total
        nxt = d["meta"].get("next_cursor")
        if not nxt:
            break
        params["cursor"] = nxt
    if not key and max_pages > 1:
        warnings.append("No OpenAlex key: only the first page was read.")
    lid = _next_id()
    raw, h = _save_pages(lid, "openalex", "works", pages, "json")
    n_ret = sum(len(json.loads(b)["results"]) for b in pages)
    _append("query", element=_code(element) if element else None, source="openalex", endpoint="works",
            parameters={k: v for k, v in params.items() if k != "cursor"} | {"corpus": corpus,
                                                                               "api_key": "<redacted:OPENALEX_API_KEY>" if key else None,
                                                                               "purpose": purpose, "label": label,
                                                                               "origin": origin},
            date_range={"from": from_date, "to": to_date}, n_total=n_total, n_retrieved=n_ret, raw_path=raw, sha256=h)
    _nb_add(nb, _call("openalex_works", search, element=_code(element) if element else None, filter=filter,
                      from_date=from_date, to_date=to_date, corpus=corpus, max_pages=max_pages, purpose=purpose))
    md = f"OpenAlex, run {_today('-')}: {_fmt(n_total)} works; {n_ret} read" + ("" if key else " (first page only, no API key)")
    return _res(True, md, [lid], warnings, count=n_total, results=[r for b in pages for r in json.loads(b)["results"]])


def ctgov_studies(cond=None, intr=None, *, element="FE", statuses=ONGOING, page_size=1000, max_pages=None, nb=None,
                  purpose=None):
    """Ongoing studies from ClinicalTrials.gov API v2; totalCount comes from page 1 only."""
    base = "https://clinicaltrials.gov/api/v2/"
    st, vbody, err = _http(base + "version")
    if st != 200:
        return _res(False, "ClinicalTrials.gov could not be reached just now.", warnings=[err or f"HTTP {st}"])
    lv = _next_id()
    rawv, hv = _save_pages(lv, "ctgov", "version", [vbody], "json")
    stamp = json.loads(vbody).get("dataTimestamp")
    _append("query", element=_code(element) if element else None, source="ctgov", endpoint="version", raw_path=rawv, sha256=hv,
            parameters={"purpose": purpose},
            text=f"Data timestamp {stamp}")
    params = {"countTotal": "true", "pageSize": page_size}
    if cond:
        params["query.cond"] = cond
    if intr:
        params["query.intr"] = intr
    if statuses:
        params["filter.overallStatus"] = ",".join(statuses)
    pages, n_total, i = [], None, 0
    while True:
        st, body, err = _http(base + "studies", params=params)
        if st != 200:
            if not pages:
                return _res(False, "ClinicalTrials.gov could not be searched just now.", warnings=[err or f"HTTP {st}"])
            break
        pages.append(body)
        d = json.loads(body)
        if n_total is None:
            n_total = d.get("totalCount")
        i += 1
        if not d.get("nextPageToken") or (max_pages and i >= max_pages):
            break
        params["pageToken"] = d["nextPageToken"]
    lid = _next_id()
    raw, h = _save_pages(lid, "ctgov", "studies", pages, "json")
    studies = []
    for b in pages:
        for s in json.loads(b).get("studies", []):
            ps = s.get("protocolSection", {})
            studies.append({"nct": ps.get("identificationModule", {}).get("nctId"),
                            "title": ps.get("identificationModule", {}).get("briefTitle"),
                            "status": ps.get("statusModule", {}).get("overallStatus")})
    _append("query", element=_code(element) if element else None, source="ctgov", endpoint="studies",
            parameters={k: v for k, v in params.items() if k != "pageToken"} | {"purpose": purpose}, n_total=n_total,
            n_retrieved=len(studies), raw_path=raw, sha256=h, refers_to=[lv], text=f"Data timestamp {stamp}")
    _nb_add(nb, _call("ctgov_studies", cond, intr, element=_code(element), max_pages=max_pages))
    rows = [f"ClinicalTrials.gov, data as of {stamp}: {_fmt(n_total)} studies"
            + (f" with status {', '.join(s.lower().replace('_', ' ') for s in statuses)}" if statuses else "")]
    if studies:
        rows += ["", "| NCT | Title | Status |", "|---|---|---|"]
        rows += [f"| {s['nct']} | {_esc(s['title'], 90)} | {str(s['status']).lower().replace('_', ' ')} |" for s in studies[:15]]
        if len(studies) > 15:
            rows.append(f"| … | {len(studies) - 15} more saved | |")
    return _res(True, "\n".join(rows), [lv, lid], count=n_total, studies=studies, data_timestamp=stamp)


# ---------------------------------------------------------------- manual retrievals (R8)

def request_manual(member, source, query, *, element=None, instructions=None):
    """Ask a member to run a search the assistant cannot run, with exact steps."""
    qid = ask(member, f"Please run in {source}: {query}", element=element)
    steps = [f"**For {member}: please run this in {source}**", "```", query, "```",
             instructions or ("Save the export (or a screenshot showing the count) and, for PubMed, the 'Search details' "
                              "box; tell me the run date when you send it.")]
    return _res(True, "\n".join(steps), [qid])


def ingest_manual(path, *, member, source, query, run_date, element, refers_to=None, n_total=None, translation=None):
    """Save a member's export unchanged and log it as a manual retrieval; counts are computed from the file."""
    if not os.path.exists(path):
        return _refuse("I cannot find that file; please share it again.")
    ext = os.path.splitext(path)[1].lstrip(".") or "txt"
    if refers_to is None:
        opens = [r for r in _open_asks() if (r["parameters"] or {}).get("to") == member]
        refers_to = [opens[-1]["id"]] if opens else None
    lid = _next_id()
    with open(path, "rb") as f:
        raw, h = _save_pages(lid, re.sub(r"\W+", "", source.lower())[:20], "manual", [f.read()], ext)
    text = _read(_p(*raw.split("/")), "ignore")
    n_ret = (text.count("\nTY  -") + text.startswith("TY  -") if "TY  -" in text else
             len(re.findall(r"^PMID-", text, re.M)) or (max(0, len(text.strip().splitlines()) - 1) if ext == "csv" else None))
    warnings = []
    if source.lower() == "pubmed" and n_total is not None and not (translation and "[Date - Create]" in translation):
        warnings.append("PubMed count not logged: the search details do not show the Create Date bound.")
        n_total = None
    rid = _append("manual_retrieval", actor=member, element=_code(element), source=source, endpoint="manual",
                  parameters={"query": query, "run_date": run_date, "translation": translation}, n_total=n_total,
                  n_retrieved=n_ret, raw_path=raw, sha256=h, refers_to=refers_to)
    return _res(True, f"{source} export from {member} saved: {_fmt(n_ret)} records in the file"
                + (f"; {_fmt(n_total)} reported by the source" if n_total is not None else ""), [rid], warnings)


def verify(log_ids=None):
    """Recompute every logged count from the saved raw files and check the hashes (the analysis cell of 3.6)."""
    import glob
    import xml.etree.ElementTree as ET
    rows, bad = [], []
    for r in _records():
        if not r.get("raw_path") or (log_ids and r["id"] not in log_ids):
            continue
        files = sorted(glob.glob(_p(*r["raw_path"].split("/"))))
        if not files:
            bad.append(r["id"])
            continue
        h = sha256_file(files[0]) if len(files) == 1 else hashlib.sha256(
            "\n".join(sha256_file(f) for f in files).encode()).hexdigest()
        tot = ret = None
        try:
            if r["source"] == "pubmed" and r["endpoint"] == "esearch":
                d = _jread(files[0])["esearchresult"]
                tot, ret = int(d["count"]), len(d.get("idlist", []))
                if r["n_total"] is None:
                    tot = None
            elif r["source"] == "pubmed" and r["endpoint"] == "efetch":
                ret = sum(len(ET.parse(f).getroot().findall("PubmedArticle"))
                          + len(ET.parse(f).getroot().findall("PubmedBookArticle")) for f in files)
                tot = r["n_total"]
            elif r["source"] == "openalex":
                ds = [_jread(f) for f in files]
                tot, ret = ds[0]["meta"]["count"], sum(len(d["results"]) for d in ds)
            elif r["source"] == "ctgov" and r["endpoint"] == "studies":
                ds = [_jread(f) for f in files]
                tot, ret = ds[0].get("totalCount"), sum(len(d.get("studies", [])) for d in ds)
            else:
                tot, ret = r["n_total"], r["n_retrieved"]
        except Exception:
            bad.append(r["id"])
            continue
        good = h == r["sha256"] and tot == r["n_total"] and ret == r["n_retrieved"]
        if not good:
            bad.append(r["id"])
        rows.append((r["id"], r["source"], r["endpoint"], tot, ret, good))
    lid = _append("computation", text=f"Verified {len(rows)} saved responses; {len(bad)} problem(s)",
                  parameters={"problems": bad})
    _session_set(last_verify={"time": _now(), "checked": len(rows), "problems": bad})
    md = (f"Checked {len(rows)} saved search results against the log: all counts and files match."
          if not bad else f"Checked {len(rows)} saved results: {len(bad)} do not match ({', '.join(bad)}).")
    return _res(not bad, md, [lid], problems=bad, rows=rows)


# ---------------------------------------------------------------- plan, team, interests, focus

def _plan():
    return _yload(_p("plan", "plan.yaml"), {}) or {}


def _save_plan(plan):
    _ydump(_p("plan", "plan.yaml"), plan)


def plan():
    """The plan file as a dict."""
    return _plan()


def _team():
    return _yload(_p("plan", "team.yaml"), {}) or {}


def team():
    """The team file as a dict."""
    return _team()


def _member(tm, nm):
    for m in tm["members"]:
        if m["name"].lower() == nm.lower():
            return m
    return None


def set_topic(text, *, given_by, refers_to=None):
    """Record the provisional topic (a JUDGMENT); a changed topic lists the answers that may no longer hold."""
    pl = _plan()
    old = (pl.get("topic") or {}).get("text")
    lid = log("answer", text=text, actor=given_by, element=None, refers_to=refers_to,
              parameters={"topic": True, "replaces": old})
    pl["topic"] = {"text": text, "given_by": given_by, "log_id": lid}
    _save_plan(pl)
    md = f"Topic recorded: “{_esc(text, 300)}”."
    if old:
        dep = [f"{m}: “{_esc(v, 80)}”" for m, v in (pl.get("focus") or {}).get("by_member", {}).items()]
        md += " This replaces the earlier topic; please say which earlier answers still hold" + (
            ": " + "; ".join(dep) if dep else "") + "."
    return _res(True, md, [lid])


def add_member(name_, role, *, can_certify=(), sources=(), consent_="unknown", by=None, solo=False):
    """Add a member with role and certification rights (codes or full names, or 'all')."""
    tm = _team()
    cc = ["all"] if (solo or "all" in can_certify) else [c for c in (_code(x) for x in can_certify) if c]
    m = _member(tm, name_)
    if m is None:
        m = {"name": name_, "motivation": None}
        tm["members"].append(m)
    m.update({"role": "solo" if solo else role, "can_certify": cc, "sources": list(sources), "consent": consent_,
              "solo": bool(solo)})
    _ydump(_p("plan", "team.yaml"), tm)
    return log("answer", actor=by or name_, text=f"Member {name_} ({m['role']}); may certify: "
               + (", ".join(name(c) for c in cc) if cc != ["all"] else "every decision"), parameters={"team": True})


def set_team(key, value, *, by):
    """Record sources, deadlines, resources, rules or decisions_made (JUDGMENTS)."""
    if key not in ("sources", "deadlines", "resources", "rules", "decisions_made"):
        raise KitError(f"Unknown team key {key}")
    tm = _team()
    if key in ("sources", "decisions_made"):
        if isinstance(value, str):
            value = [] if value.strip().lower() in ("", "not given", "none", "n/a") else [value]
        value = [v for v in (value or []) if str(v).strip()]
    tm[key] = value
    _ydump(_p("plan", "team.yaml"), tm)
    return log("answer", actor=by, text=f"{key}: {value if value not in ([], None) else 'not given'}",
               parameters={"team": key})


def record_interest(member, *, interest, seeks=None, expertise=None, disclosed=True, refers_to=None):
    """Record a member's interest in the topic and what they seek (Individual Motivation, in their words)."""
    if disclosed and not str(interest or "").strip():
        return _refuse(f"I need {member}'s own words for their interest, or a note that they prefer not to say.")
    tm = _team()
    m = _member(tm, member)
    if m is None:
        m = {"name": member, "role": None, "can_certify": [], "sources": [], "consent": "unknown", "solo": False,
             "motivation": None}
        tm["members"].append(m)
    mot = m.get("motivation") or {}
    mot.update({"interest": interest if disclosed else "not disclosed", "seeks": seeks if disclosed else "not disclosed",
                "expertise": expertise, "states": mot.get("states", []), "disclosed": bool(disclosed)})
    m["motivation"] = mot
    _ydump(_p("plan", "team.yaml"), tm)
    lid = log("answer", actor=member, element="IM", refers_to=refers_to,
              text=f"Interest: {mot['interest']}. Seeks: {mot['seeks']}." + (f" Expertise: {expertise}." if expertise else ""),
              parameters={"interest": True})
    pl = _plan()
    pl["focus"]["by_member"][member] = mot["interest"]
    pl["focus"]["log_ids"].append(lid)
    v = pl["variables"]["IM"]
    v["log_ids"].append(lid)
    v["decision"] = "; ".join(f"{x['name']}: interest — {x['motivation']['interest']}; seeks — {x['motivation']['seeks']}"
                              for x in tm["members"] if x.get("motivation"))
    _save_plan(pl)
    return _res(True, f"Recorded {member}'s interest and motivation.", [lid])


def provenance(text, refers_to, extra=()):
    """Content words in text that appear in neither the referenced records, the topic nor extra (deterministic)."""
    rows = {r["id"]: r for r in _records()}
    src = " ".join(str(rows[i].get("text") or "") for i in (refers_to or []) if i in rows)
    src += " " + " ".join(extra) + " " + str((_plan().get("topic") or {}).get("text") or "")

    def norm(w):
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        if w.endswith("s") and not w.endswith("ss") and len(w) > 4:
            return w[:-1]
        return w

    def words(s):
        out = set()
        for w in re.findall(r"[A-Za-z][A-Za-z0-9'-]+", s.lower().replace("\u2019", "'")):
            w = w.strip("'-")
            if w.endswith("'s"):
                w = w[:-2]
            if len(w) >= 4 and w not in STOP:
                out.add(norm(w))
        return out
    have = words(src)
    added = sorted(w for w in words(text) if w not in have)
    return {"added": added}


def set_focus(text, *, agreed_by, refers_to):
    """Record the research focus the team agreed, in members' words; any added content word is refused."""
    prov = provenance(text, refers_to)
    if prov["added"]:
        return _refuse("The focus may hold only the team's own words; these words came from me: "
                       + ", ".join(prov["added"]) + ". Please remove them or say them yourselves.", added=prov["added"])
    lid = log("answer", actor=agreed_by, element="TP", text=f"Agreed focus: {text}", refers_to=refers_to,
              parameters={"focus": True})
    pl = _plan()
    pl["focus"]["text"] = text
    pl["focus"]["proposed"] = None
    pl["focus"]["log_ids"].append(lid)
    _save_plan(pl)
    return _res(True, f"Focus recorded: “{_esc(text, 200)}”.", [lid])


def reflect_focus(text, *, refers_to):
    """Show the focus reflected back from members' words (checked for added words); the status line marks it
    '(to confirm)' until the team confirms it with set_focus."""
    prov = provenance(text, refers_to)
    if prov["added"]:
        return _refuse("The focus may hold only the team's own words; these words came from me: "
                       + ", ".join(prov["added"]) + ". Please remove them.", added=prov["added"])
    lid = log("draft", element="TP", text=f"Focus reflected back: {text}", refers_to=refers_to)
    pl = _plan()
    pl["focus"]["proposed"] = text
    _save_plan(pl)
    return _res(True, f"Focus, in your words: “{_esc(text, 200)}”. Added by me: nothing.", [lid])


def confirm_states(element, *, states, by, member=None):
    """Record the states a member (Individual Motivation) or the team (Team's Purpose) chose."""
    el = _code(element)
    if by == "agent":
        return _refuse("Only a member can choose these; I can show the options but not pick them.")
    space = state_space(el)
    lower = {s.lower(): s for s in space}
    fixed, bad = [], []
    for s in states:
        if str(s).lower().startswith("other:"):
            fixed.append(s)
        elif str(s).lower() in lower:
            fixed.append(lower[str(s).lower()])
        else:
            bad.append(s)
    if bad:
        return _refuse(f"These are not options for {name(el)}: {', '.join(map(str, bad))}. Please pick from the list or say 'other: …'.")
    lid = log("answer", actor=by, element=el, text=f"Chose: {'; '.join(fixed)}" + (f" (for {member})" if member else ""),
              parameters={"states": fixed, "member": member})
    pl = _plan()
    if el == "IM":
        tm = _team()
        m = _member(tm, member or by)
        if m is not None:
            m["motivation"] = (m.get("motivation") or {}) | {"states": fixed}
            _ydump(_p("plan", "team.yaml"), tm)
            union = []
            for x in tm["members"]:
                for s in (x.get("motivation") or {}).get("states", []):
                    if s not in union:
                        union.append(s)
            pl["variables"]["IM"]["states"] = union
    else:
        pl["variables"][el]["states"] = fixed
    pl["variables"][el]["log_ids"].append(lid)
    _save_plan(pl)
    return _res(True, f"{name(el)}: recorded {'; '.join(fixed)}.", [lid])


def propose(element, *, decision, accepted_by, states=None, draft_id=None):
    """A draft enters the plan when a named member accepts it (status proposed); then trace its flows."""
    el = _code(element)
    if accepted_by == "agent":
        return _refuse("A draft enters the plan only when a member accepts it.")
    shown_texts = [str(r.get("text") or "") for r in _records() if r["kind"] in ("draft", "question")]
    shown_texts += list((_session().get("last_shown") or {}).values())
    if not any(_norm(decision) in _norm(t) for t in shown_texts):
        return _refuse("Show this wording to the team first (k.draft or k.certify_line with draft=); "
                       "record acceptance only after a member has seen it.")
    pl = _plan()
    if el == "TP":
        if not (pl.get("focus") or {}).get("text"):
            return _refuse("Before the purpose is proposed, the team needs to agree its research focus (it may be the whole topic).")
        ans = [r["id"] for r in _records() if r["kind"] == "answer" and r["element"] in ("IM", "TP")]
        prov = provenance(decision, ans, extra=list(pl["variables"]["TP"]["states"]) + list(states or []))
        if prov["added"]:
            return _refuse("The purpose may hold only what members said or chose; these words came from me: "
                           + ", ".join(prov["added"]) + ". Please remove them or say them yourselves.", added=prov["added"])
    if states:
        r = confirm_states(el, states=states, by=accepted_by) if el in ("IM", "TP") else None
        if r and not r["ok"]:
            return r
        pl = _plan()
        if el not in ("IM", "TP"):
            pl["variables"][el]["states"] = list(states)
    v = pl["variables"][el]
    if v["status"] in ("certified", "amended"):
        return _refuse(f"{name(el)} is already certified; it can change only if the team agrees to reopen it.")
    lid = log("answer", actor=accepted_by, element=el, text=f"Accepted: {decision}",
              refers_to=[draft_id] if draft_id else None, parameters={"accepts_draft": True})
    v.update({"decision": decision, "status": "proposed"})
    v["log_ids"].append(lid)
    _save_plan(pl)
    t = trace([el], because=lid)
    return _res(True, f"{name(el)} accepted by {accepted_by} and ready to certify. {t['md']}", [lid] + t["log_ids"])


def _recompute_provisional(pl):
    reopened = [c for c, v in pl["variables"].items() if v["status"] == "reopened"]
    reach = set()
    frontier = list(reopened)
    while frontier:
        nxt = []
        for s in frontier:
            for f in _flows():
                if f["from"] == s and f["to"] in pl["variables"] and f["to"] not in reach and f["to"] not in reopened:
                    reach.add(f["to"])
                    nxt.append(f["to"])
        frontier = nxt
    for c, v in pl["variables"].items():
        v["provisional"] = c in reach and v["status"] in ("certified", "amended", "proposed")


def reopen(element, *, agreed_by, reason, refers_to=None):
    """Reopen a settled decision; only when the team agrees (R4). Work that depends on it becomes provisional."""
    el = _code(element)
    if agreed_by == "agent" or not reason:
        return _refuse("A decision is reopened only when the team agrees, with its reason.")
    lid = _append("reopen", actor=agreed_by, element=el, reason=reason, refers_to=refers_to,
                  text=f"Reopened {name(el)}")
    pl = _plan()
    pl["variables"][el]["status"] = "reopened"
    pl["variables"][el]["log_ids"].append(lid)
    _recompute_provisional(pl)
    _save_plan(pl)
    md = f"{name(el)} reopened at {agreed_by}'s request."
    if _submitted(pl):
        md += " Because the protocol is registered, its recertification will be recorded as an amendment."
    return _res(True, md, [lid])


def register(registry, reg_id=None, version=None, *, by, status="submitted", note=None):
    """Record the protocol's registry submission (kind registration), or the team's decision not to submit it
    (status="not submitted"); either settles Step 11."""
    if status not in ("submitted", "not submitted"):
        raise KitError('status must be "submitted" or "not submitted"')
    if status == "submitted" and not reg_id:
        raise KitError("a submitted registration needs the registry's identifier, as the registry gave it")
    text = (f"Submitted to {registry}: {reg_id} (version {version})" if status == "submitted"
            else f"Not submitted to {registry}" + (f": {note}" if note else ""))
    lid = _append("registration", actor=by, text=text,
                  parameters={"registry": registry, "id": reg_id, "version": version, "status": status})
    pl = _plan()
    pl["registration"] = {"registry": registry, "id": reg_id, "version": version, "status": status, "log_id": lid}
    _save_plan(pl)
    return lid


def step_done(step, *, by, note=None):
    """Record that the team has finished a step that has no certification of its own (Step 9, pilot screening)."""
    return log("note", actor=by, text=f"Step {step} finished" + (f": {note}" if note else ""),
               parameters={"step_done": int(step)})


def commitment(by, text, *, included=None):
    """Record the end of planning: a snapshot of the provisionally included studies (the final included set is decided
    when the review is carried out), also in plan.yaml."""
    lid = _append("commitment", actor=by, text=text, parameters={"included": included})
    pl = _plan()
    pl["commitment"] = {"by": by, "time_utc": _now(), "included": included, "log_id": lid}
    _save_plan(pl)
    return lid


def screen(record_id, decision, *, by, criterion, source_ids, passage=None):
    """Record a person's screening decision (include, exclude or unsure); the assistant never screens (R13)."""
    if by == "agent":
        return _refuse("Screening decisions belong to people; I can only suggest one as a draft.")
    if decision not in ("include", "exclude", "unsure"):
        raise KitError("decision must be include, exclude or unsure")
    lid = _append("screening_decision", actor=by, element="RU", decision=decision, text=passage,
                  parameters={"record_id": record_id, "criterion": criterion, "source_ids": source_ids})
    path = _p("data", "derived", "screening.csv")
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["record_id", "source_ids", "screener", "decision", "criterion", "time_utc", "log_id"])
        w.writerow([record_id, json.dumps(source_ids), by, decision, criterion, _now(), lid])
    return lid


# ---------------------------------------------------------------- certification

def _eligible(el):
    tm = _team()
    return [m for m in tm["members"] if "all" in (m.get("can_certify") or []) or el in (m.get("can_certify") or [])]


def certify_line(element, *, reviewer=None, draft=None):
    """The certification line, filled in except for the reviewer's reason. draft = a wording built from answers the
    team confirmed, shown for certification without recording any acceptance (the plan changes only on certify)."""
    el = _code(element)
    v = (_plan()["variables"].get(el) or {})
    dec = draft or v.get("decision") or "<the decision as drafted>"
    if re.search(r"strike one|if wrong|to confirm", str(dec), re.I):
        raise KitError("Keep instructions out of the decision; say them outside the line.")
    el_members = _eligible(el)
    m = next((x for x in el_members if reviewer and x["name"].lower() == reviewer.lower()), el_members[0] if el_members else None)
    who = f"{m['name']}, {m['role']}" if m else "<name>, <role>"
    line = f"CERTIFY {name(el)} | {dec} | reason: ___ | {who}"
    shown = _session().get("last_shown", {})
    shown[el] = dec
    _session_set(last_shown=shown)
    if not any((r["parameters"] or {}).get("certify") == el for r in _open_asks()):
        log("question", text=f"to {m['name'] if m else 'reviewer'}: {line}", element=el,
            parameters={"to": m["name"] if m else "reviewer", "blocking": True, "certify": el})
    return line


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _shares_run(a, b, n=5):
    aw, bw = _norm(a).split(), _norm(b).split()
    grams = {tuple(bw[i:i + n]) for i in range(len(bw) - n + 1)}
    return any(tuple(aw[i:i + n]) in grams for i in range(len(aw) - n + 1))


def certify(*, line=None, element=None, reviewer=None, said=None, reason=None, asked=None):
    """Record a certification: the full CERTIFY line, or 'certify' with a reason in the reviewer's own words.
    asked = the text of your request; a reason that repeats five or more of its words in a row is refused."""
    if line:
        m = re.match(r"^\s*CERTIFY\s+(?P<el>[^|]+)\|\s*(?P<dec>[^|]+?)\s*\|\s*reason:\s*(?P<reason>[^|]*?)\s*\|\s*"
                     r"(?P<name>[^,|]+),\s*(?P<role>.+?)\s*$", line, re.I | re.S)
        if not m:
            return _refuse("Please reply “certify” with your reason in a few words.")
        el, dec, reason, who = _code(m["el"].strip()), m["dec"].strip(), m["reason"].strip(), m["name"].strip()
        said = said or line
    else:
        el, who, dec = _code(element), reviewer, (_session().get("last_shown") or {}).get(_code(element or ""))
        if not said or not reason or _norm(reason) not in _norm(said):
            if said:
                answer(who or "reviewer", said, element=el)
            ask(who or "reviewer", "What is your reason, in a few words?", element=el)
            return _refuse("What is your reason, in a few words?")
    if el is None:
        return _refuse("Which decision are you certifying?")
    if not reason or re.fullmatch(r"(_+|<.*>|\.+|-+)", reason) or _norm(reason) == _norm(dec):
        return _refuse("What is your reason, in a few words?")
    if not dec:
        return _refuse("Please look at the wording shown above first; I need to show it before it can be certified.")
    if asked and _shares_run(reason, asked):
        return _refuse("Please give your reason in your own words, not the words of my question.")
    eligible = _eligible(el)
    if not who and len(eligible) == 1:
        who = eligible[0]["name"]
    rec = next((x for x in eligible if x["name"].lower() == str(who).lower()), None)
    if rec is None:
        names = ", ".join(x["name"] for x in eligible) or "nobody yet"
        return _refuse(f"{who} is not listed as able to certify {name(el)} (listed: {names}). Who may certify it?")
    pl = _plan()
    var = pl["variables"].get(el)
    shown = (_session().get("last_shown") or {}).get(el)
    current = (var or {}).get("decision") if var else shown
    if shown and _norm(dec) != _norm(shown):
        return _refuse("That wording differs from the wording I last showed; I will show the new wording for you to confirm first.")
    if not shown and var is not None and current and _norm(dec) != _norm(current):
        return _refuse("That wording differs from the plan; I will show the current wording for you to confirm first.")
    status = (var or {}).get("status")
    recert = status == "reopened"
    if var is not None and status in ("certified", "amended"):
        return _refuse(f"{name(el)} is already certified; it changes only if the team agrees to reopen it.")
    if not recert:
        done = _certified_set()
        for prior in CERT_ORDER[:CERT_ORDER.index(el)]:
            if prior not in done:
                return _refuse(f"{name(prior)} comes first; let us settle it before {name(el)}.")
    kind = "amendment" if (_submitted(pl) and recert) else "certification"
    composed = f"CERTIFY {name(el)} | {dec} | reason: {reason} | {rec['name']}, {rec.get('role') or 'member'}"
    prev = [r["id"] for r in _records() if r["kind"] in ("certification", "amendment") and r["element"] == el][-1:]
    pending = [r["id"] for r in _open_asks() if r["element"] == el]
    lid = _append(kind, actor=rec["name"], element=el, decision=dec, reason=reason, text=composed,
                  parameters={"said": said}, refers_to=(prev + pending) or None)
    if var is not None:
        var.update({"status": "amended" if kind == "amendment" else "certified", "decision": dec,
                    "certified_by": f"{rec['name']}, {rec.get('role') or 'member'}", "certified_at": _now(),
                    "reason": reason})
        var["log_ids"].append(lid)
        _recompute_provisional(pl)
        _save_plan(pl)
    sha = commit(f"Certify {el} ({lid})", lid)
    t = trace([el], because=lid) if var is not None else {"md": "", "log_ids": []}
    md = f"Certified: `{composed}`\n{t['md']}"
    if kind == "amendment":
        md += "\nThe team should also submit this amendment to the registry."
    return _res(True, md.strip(), [lid] + t["log_ids"], commit=sha, line=composed)


def _certified_set():
    out = {c for c, v in _plan()["variables"].items() if v["status"] in ("certified", "amended")}
    out |= {r["element"] for r in _records() if r["kind"] in ("certification", "amendment") and r["element"] in ("PAO", "LAT", "RED")}
    return out


def check_secrets():
    """Scan files that are not git-ignored for credential values or email addresses; returns paths only."""
    vals = [v for k in SECRET_NAMES if (v := _secret(k))]
    hits = []
    ignored = set()
    if shutil.which("git") and os.path.exists(_p(".git")):
        r = subprocess.run(["git", "-C", _ROOT, "ls-files", "--others", "--ignored", "--exclude-standard"],
                           capture_output=True, text=True)
        ignored = set(r.stdout.split())
    for dp, dn, fn in os.walk(_ROOT):
        if ".git" in dp.split(os.sep):
            continue
        for f in fn:
            path = os.path.join(dp, f)
            rel = _rel(path)
            if rel in ignored or f == ".env" or rel.startswith("data/raw/text/"):
                continue
            try:
                s = _read(path, "ignore")
            except OSError:
                continue
            if any(v in s for v in vals):
                hits.append(rel)
    return _res(not hits, "No credentials found in files to be committed." if not hits else
                f"Credentials found in: {', '.join(hits)}", hits=hits)


def commit(message, log_id=None):
    """Commit the workspace after a certification (identity: configured, or a neutral one); never asks the team."""
    if not shutil.which("git") or not os.path.exists(_p(".git")):
        return None
    if not check_secrets()["ok"]:
        return None
    subprocess.run(["git", "-C", _ROOT, "add", "-A"], capture_output=True)
    ident = []
    if not subprocess.run(["git", "-C", _ROOT, "config", "user.email"], capture_output=True, text=True).stdout.strip():
        ident = ["-c", "user.name=STIR-L4 assistant", "-c", "user.email=stir-l4@localhost"]
    subprocess.run(["git", "-C", _ROOT, *ident, "commit", "-q", "-m", message], capture_output=True)
    return _git_head()


# ---------------------------------------------------------------- where we are: status line, plan map, metrics

def _current_step():
    pl = _plan()
    var = pl.get("variables") or {}
    reop = [c for c in VARIABLES if var.get(c, {}).get("status") == "reopened"]
    if reop:
        return min(n for n, _, els in STEPS for c in reop if c in els)
    if not (pl.get("topic") or {}).get("text"):
        return 1
    done = _certified_set()
    for n, _, els in STEPS[1:8]:
        if any(e not in done for e in els):
            return n
    rows = _records()
    if any(r["kind"] == "commitment" for r in rows):
        return 13
    me = (var.get("ME") or {}).get("status")
    pilot_done = any((r["parameters"] or {}).get("step_done") == 9 for r in rows if r["kind"] == "note")
    if not pilot_done and "ME" not in done and me not in ("proposed",):
        return 9
    if "ME" not in done:
        return 10
    if not pl.get("registration"):
        return 11
    return 12


def _waiting():
    items, seen_el = [], set()
    for r in reversed(_open_asks()):
        p = r["parameters"] or {}
        if not p.get("blocking", True):
            continue
        key = ("certify", r["element"]) if (p.get("certify") or "reason" in r["text"].lower()) and r["element"] else ("ask", r["id"])
        if key in seen_el:
            continue
        seen_el.add(key)
        items.append((p.get("to") or "team", r["text"].split(": ", 1)[-1], r["id"], r["element"], int(p.get("items", 1))))
    return list(reversed(items))


def _early():
    step = _current_step()
    notes = [r for r in _records() if r["kind"] == "note" and (r["parameters"] or {}).get("early")]
    if notes and notes[-1]["parameters"]["early"] > step:
        e = notes[-1]["parameters"]["early"]
        later = {x for n, _, els in STEPS if n >= e for x in els}
        reached = any(r["kind"] in ("certification", "amendment") and r["element"] in later
                      and r["id"] > notes[-1]["id"] for r in _records())
        return None if reached else e
    return None


def status_line():
    """The one-line status that opens every reply: step, certified count, waiting items and the focus."""
    pl = _plan()
    n = _current_step()
    nm = "Planning complete" if n > 12 else STEPS[n - 1][1]
    cert = sum(1 for c in VARIABLES if pl["variables"][c]["status"] in ("certified", "amended"))
    fo = pl.get("focus") or {}
    focus = fo.get("text")
    tag = ""
    if not focus and fo.get("proposed"):
        focus, tag = fo["proposed"], " (to confirm)"
    focus = focus or "not yet stated"
    words = focus.split()
    focus = " ".join(words[:12]) + ("…" if len(words) > 12 else "") + tag
    e = _early()
    if e:
        nm += f" (Step {e} started early)"
    w = _waiting()
    members = [m["name"] for m in _team().get("members", [])]
    who = []
    for x in w:
        t = str(x[0])
        names = members if re.search(r"\b(team|all|each|everyone|every member)\b", t, re.I) else \
            [m for m in members if re.search(rf"\b{re.escape(m)}\b", t, re.I)] or ([t] if t not in ("reviewer",) else [])
        for n_ in names:
            if n_ not in who and not re.search(r"\b(team|all|each|everyone)\b", n_, re.I):
                who.append(n_)
    n_items = sum(x[4] if len(x) > 4 else 1 for x in w)
    wait = f"{n_items}" + (f" ({', '.join(who)})" if who else "")
    line = f"Step {min(n, 12)} of 12: {nm} | Certified {cert} of 8 | Waiting on you: {wait} | Focus: {focus}"
    reop = [name(c) for c in VARIABLES if pl["variables"][c]["status"] == "reopened"]
    if reop:
        line += f" | Reopened: {', '.join(reop)}"
    return line


def plan_map():
    """The 12-step plan map (Step | Settles | Status | Waiting on), with interests recorded and quick commands."""
    pl = _plan()
    tm = _team()
    now = _current_step()
    done = _certified_set()
    wait = _waiting()
    rows = ["| Step | Settles | Status | Waiting on |", "|---|---|---|---|"]
    for n, nm, els in STEPS:
        if n == 1:
            st = "done" if (pl.get("topic") or {}).get("text") else "now"
        elif els and n != 7:
            vs = [pl["variables"][e] for e in els]
            if any(v["status"] == "reopened" for v in vs):
                st = "reopened"
            elif all(e in done for e in els):
                st = "certified by " + ", ".join(sorted({v["certified_by"].split(",")[0] for v in vs if v["certified_by"]}))
            elif any(v["status"] == "proposed" for v in vs):
                st = "draft ready"
            else:
                st = "now" if n == now else ("next" if n == now + 1 else "open")
        elif n == 7:
            k = sum(1 for e in els if e in done)
            st = f"{k} of 3 certified" if k else ("now" if n == now else "open")
        elif n == 9:
            k = sum(1 for r in _records() if r["kind"] == "screening_decision")
            st = f"{k} screening decisions" if k else ("now" if n == now else "open")
        elif n == 11:
            reg = pl.get("registration") or {}
            st = ((f"registered ({reg['registry']})" if _submitted(pl) else f"not submitted ({reg.get('registry')})")
                  if reg else ("now" if n == now else "open"))
        else:
            st = "done" if any(r["kind"] == "commitment" for r in _records()) else ("now" if n == now else "open")
        if n == now and st in ("open", "next"):
            st = "now"
        if _early() == n and st in ("open", "next", "now"):
            st = "started early"
        w = "; ".join(sorted({x[0] for x in wait if x[3] in els or (n == 1 and x[3] is None and not
                              (pl.get("topic") or {}).get("text"))})) or "—"
        rows.append(f"| {n}. {nm} | {SETTLES[n]} | {st} | {w} |")
    members = tm.get("members", [])
    got = sum(1 for m in members if m.get("motivation"))
    rows.append("")
    rows.append(f"Interests recorded: {got} of {len(members) or 1} member{'s' if len(members) != 1 else ''}."
                if members else "Interests recorded: none yet.")
    if not _session().get("map_shown"):
        rows.append("The line at the top of each reply shows the step, the decisions you have approved (out of 8), "
                    "the answers or approvals the current step is waiting for, and your research focus.")
        rows.append("Labels: FACT = found in a search; JUDGMENT = what one of you said; DRAFT = my wording for you to "
                    "edit; \"Added by me: nothing\" means every word came from you.")
        rows.append("Quick commands, in any wording: " + COMMANDS + ".")
        _session_set(map_shown=True)
    return "\n".join(rows)


def metrics():
    """Progress figures for guiding the conversation (all computed from the plan and the log)."""
    pl = _plan()
    s = _session()
    rows = _records()
    since = s.get("start_log")
    sess = records(since=since) if since else rows
    tm = _team()
    return {"step_now": min(_current_step(), 12), "early": _early(),
            "certified": sum(1 for c in VARIABLES if pl["variables"][c]["status"] in ("certified", "amended")),
            "waiting": [{"who": x[0], "what": x[1], "id": x[2], "element": x[3]} for x in _waiting()],
            "focus": {"text": (pl.get("focus") or {}).get("text"),
                      "members_with_interest": sum(1 for m in tm.get("members", []) if m.get("motivation")),
                      "members": len(tm.get("members", []))},
            "reopened": [name(c) for c in VARIABLES if pl["variables"][c]["status"] == "reopened"],
            "step7_certified": sum(1 for e in ("PAO", "LAT", "RED") if e in _certified_set()),
            "queries_this_session": sum(1 for r in sess if r["kind"] in ("query", "manual_retrieval")),
            "certifications_this_session": sum(1 for r in sess if r["kind"] in ("certification", "amendment")),
            "last_verify": s.get("last_verify")}


# ---------------------------------------------------------------- search display

def _how(line):
    parts = []
    if re.search(r"\[(mesh|mh)(:noexp)?\]|\[majr\]", line, re.I):
        parts.append("subject headings")
    if re.search(r"\[tiab\]", line, re.I):
        parts.append("title/abstract words")
    elif re.search(r"\[ti\]", line, re.I):
        parts.append("words in the title")
    if "*" in line:
        parts.append("with truncation")
    if re.search(r"\[sb\]|\[pt\]", line, re.I):
        parts.append("publication filter")
    return ", ".join(parts) or "free text in all fields"


def search_card(log_ids, *, purpose, explain=None, origin=None, title=None):
    """Show searches in the chat: exact strings, block-by-block counts, how to read the tags, and what is not searched."""
    rows = {r["id"]: r for r in _records()}
    qs = [rows[i] for i in log_ids if i in rows and rows[i]["kind"] in ("query", "manual_retrieval")]
    if not qs:
        return "No searches to show."
    last = qs[-1]
    term = (last["parameters"] or {}).get("term") or (last["parameters"] or {}).get("search") or (last["parameters"] or {}).get("query")
    dr = last.get("date_range") or {}
    src = SOURCE_NAMES.get(last["source"], last["source"])
    head = f"**{title or src + ' search'}** — purpose: {purpose}; run {str(last['time_utc'])[:10]}"
    if dr.get("datetype") == "crdt":
        head += f"; records created {dr['min']} to {dr['max']} (date bound checked)"
    out = [head, "", "```", str(term), "```"]
    if len(qs) > 1:
        out += ["", "| Block | Covers | From | How it searches | Records |", "|---|---|---|---|---|"]
        for i, q in enumerate(qs[:-1], 1):
            p = q["parameters"] or {}
            cov = (explain.get(i) if isinstance(explain, dict) else None) or p.get("label") or f"block {i}"
            org = (origin.get(i) if isinstance(origin, dict) else None) or p.get("origin") or "—"
            out.append(f"| {i} | {_esc(cov, 60)} | {org} | {_how(p.get('term', ''))} | {_fmt(q['n_total'])} |")
        out.append(f"| All | combined | — | blocks joined as shown | **{_fmt(last['n_total'])}** |")
    else:
        out.append(f"Records: **{_fmt(last['n_total'])}** (records, not studies).")
    seen = set(_session().get("glossary_shown", []))
    used = [(t, d) for t, d in GLOSSARY if t.lower() in str(term).lower() and t not in seen]
    if used:
        out += ["", "How to read it: " + "; ".join(f"`{t.strip()}` {d}" for t, d in used) + "."]
        _session_set(glossary_shown=sorted(seen | {t for t, _ in used}))
    if isinstance(explain, str):
        out += ["", f"DRAFT: {explain}"]
    tm = _team()
    searched = {r["source"].lower() for r in _records() if r["kind"] in ("query", "manual_retrieval") and r["source"]}
    srcs = tm.get("sources") if isinstance(tm.get("sources"), list) else []
    todo = [s for s in srcs if str(s).strip() and str(s).lower().split()[0] not in searched]
    if todo:
        out += ["", "Not searched yet: " + "; ".join(str(s) for s in todo) + "."]
    out += ["", "Sources: " + "; ".join(f"[{i}] {q['id']} {SOURCE_NAMES.get(q['source'], q['source'])}, run {str(q['time_utc'])[:10]}"
                                        for i, q in enumerate(qs, 1))]
    return "\n".join(out)


def search_report(groups, *, purpose, compact=False, lead=None, explain=None):
    """Show several searches in one block with one Sources line (citations numbered across all of them).

    groups = [[block ids..., combined id], [single id], ...] as returned in log_ids by run_strategy or a search.
    compact=True gives one row per search (for "what was the search strategy?" after the full cards were shown).
    """
    rows = {r["id"]: r for r in _records()}
    groups = [[i for i in g if i in rows] for g in groups]
    groups = [g for g in groups if g]
    cites, out = [], []
    if lead:
        out += [lead, ""]

    def cite(i):
        if i not in cites:
            cites.append(i)
        return f"[{cites.index(i) + 1}]"
    terms = " ".join(str((rows[g[-1]]["parameters"] or {}).get("term") or (rows[g[-1]]["parameters"] or {}).get("search") or "")
                     for g in groups)
    seen = set(_session().get("glossary_shown", []))
    used = [(t, d) for t, d in GLOSSARY if t.lower() in terms.lower() and t not in seen]
    if used and not compact:
        out += ["How to read the strings: " + "; ".join(f"`{t.strip()}` {d}" for t, d in used) + ".", ""]
        _session_set(glossary_shown=sorted(seen | {t for t, _ in used}))
    if compact:
        out += ["| # | Source | Looks for | Filters and dates | Records |", "|---|---|---|---|---|"]
    for n, g in enumerate(groups, 1):
        last = rows[g[-1]]
        p = last["parameters"] or {}
        src = SOURCE_NAMES.get(last["source"], last["source"])
        term = p.get("term") or p.get("search") or p.get("query") or ""
        dr = last.get("date_range") or {}
        bound = f"created {dr['min']} to {dr['max']} (checked)" if dr.get("datetype") == "crdt" else (
            f"published {dr.get('from') or 'any'} to {dr.get('to') or 'now'}" if last["source"] == "openalex" else "—")
        filt = ("systematic-review filter" if "systematic[sb]" in str(term).replace(" ", "").lower()
                else ("type: " + str(p.get("filter")).split("type:")[1].split(",")[0] if "type:" in str(p.get("filter") or "") else "none"))
        label = re.sub(r"^\s*search\s*\d+[a-z]?\s*[:.\-]\s*", "", str(p.get("label") or purpose or ""), flags=re.I)
        if compact:
            out.append(f"| {n} | {src} | {_esc(label, 50)} | {filt}; {bound} | {_fmt(last['n_total'])} {cite(last['id'])} |")
            continue
        out += [f"**Search {n}: {_esc(label, 80)}** ({src}; {bound}; filter: {filt})", "```", str(term), "```"]
        if len(g) > 1:
            out += ["| Block | Covers | From | How it searches | Records |", "|---|---|---|---|---|"]
            for i, bid in enumerate(g[:-1], 1):
                bp = rows[bid]["parameters"] or {}
                cov = (explain or {}).get(bid) or bp.get("label") or f"block {i}"
                out.append(f"| {i} | {_esc(cov, 60)} | {bp.get('origin') or '—'} | "
                           f"{_how(bp.get('term') or '') if rows[bid]['source'] == 'pubmed' else 'words in title, abstract or text'} | "
                           f"{_fmt(rows[bid]['n_total'])} {cite(bid)} |")
            out.append(f"| All | combined | — | blocks joined as shown | **{_fmt(last['n_total'])}** {cite(last['id'])} |")
            if filt != "none":
                out.append("Block counts are before the filter; the combined count is after it.")
        else:
            out.append(f"Records: **{_fmt(last['n_total'])}** {cite(last['id'])} (records, not studies).")
        out.append("")
    if compact:
        out += ["", 'Say "show strings" to see each search string again.']
    tm = _team()
    searched = {str(r["source"]).lower() for r in _records() if r["kind"] in ("query", "manual_retrieval") and r["source"]}
    srcs = tm.get("sources") if isinstance(tm.get("sources"), list) else []
    todo = [s for s in srcs if str(s).strip() and str(s).lower().split()[0] not in searched]
    if todo and not compact:
        out += ["Not searched yet: " + "; ".join(str(s) for s in todo) + "."]
    out += ["", "Sources: " + "; ".join(f"[{i}] {cid} {SOURCE_NAMES.get(rows[cid]['source'], rows[cid]['source'])}, run "
                                        f"{str(rows[cid]['time_utc'])[:10]}" for i, cid in enumerate(cites, 1))]
    return "\n".join(out).strip()


def prepare_strategy(source, blocks, *, member, purpose, combine="AND", left_out=None, element=None):
    """A search card for a source the assistant cannot run (for example PROSPERO or Embase): the exact string,
    one line per block, 'Count: pending: <member>', and the concepts left out and why. Logs the request."""
    term = f" {combine} ".join(f"({q})" for _, q in blocks) if len(blocks) > 1 else blocks[0][1]
    r = request_manual(member, source, term, element=element)
    out = [f"**{source} (for {member} to run)** — purpose: {purpose}", "```", term, "```"]
    if len(blocks) > 1:
        out += ["| Block | Covers |", "|---|---|"] + [f"| {i} | {_esc(c, 70)} |" for i, (c, _) in enumerate(blocks, 1)]
    out.append(f"Count: pending: {member}.")
    if left_out:
        out.append(f"Left out on purpose: {left_out}.")
    return _res(True, "\n".join(out), r["log_ids"], term=term)


def _submitted(pl):
    """True once the protocol has been submitted to a registry (a 'not submitted' record does not count)."""
    reg = pl.get("registration") or {}
    return bool(reg) and reg.get("status", "submitted") != "not submitted"


def steps_line():
    """A one-line view of the twelve steps, for replies between plan-map events."""
    pl = _plan()
    now, done, e = _current_step(), _certified_set(), _early()
    parts = []
    for n, nm, els in STEPS:
        if n == 1:
            st = "done" if (pl.get("topic") or {}).get("text") else "now"
        elif (els and all(x in done for x in els)) or (not els and n < now):
            st = "done"
        elif n == now:
            st = "now"
        elif n == e:
            st = "started early"
        else:
            continue
        parts.append(f"{n} {st}")
    rest = [n for n, _, _ in STEPS if n > max(now, e or 0)]
    if rest:
        parts.append(f"{rest[0]}–12 open" if len(rest) > 1 else f"{rest[0]} open")
    return "Steps: " + " · ".join(parts)


def review_table(records, *, terms, n=10, caption_ids=None, title="Reviews that may bear on your focus"):
    """A table of reviews with a 'Says' column quoting, word for word, the abstract sentence that names a focus or
    population term (cut to about 25 words around the first hit), or 'not stated in the abstract'.
    records = pubmed_fetch(...)["records"]; terms = the focus and population words to look for."""
    rx = re.compile("|".join(re.escape(t).replace(r"\*", r"\w*") for t in terms), re.I) if terms else None
    rows = [f"**FACT, from {', '.join(f'[{i}]' for i in (caption_ids or [])) or 'the saved records'}: {title}**", "",
            "| # | Title | Year | Says (quoted from the abstract) | PMID |", "|---|---|---|---|---|"]
    shown = 0
    for r in records:
        if shown >= n:
            break
        ab = str(r.get("abstract") or "")
        quote = "not stated in the abstract"
        if rx and ab:
            for sent in re.split(r"(?<=[.;])\s+", ab):
                m = rx.search(sent)
                if m:
                    words = sent.split()
                    pos = len(sent[:m.start()].split())
                    lo, hi = max(0, pos - 10), min(len(words), pos + 15)
                    quote = ("…" if lo else "") + "“" + " ".join(words[lo:hi]) + "”" + ("…" if hi < len(words) else "")
                    break
        rows.append(f"| {shown + 1} | {_esc(r.get('title'), 90)} | {r.get('year')} | {quote.replace('|', '/')} | {r.get('pmid')} |")
        shown += 1
    if len(records) > n:
        rows.append(f"\nSay \"show all\" to see the other {len(records) - n} here.")
    return "\n".join(rows)


def check_reply(text):
    """Check a reply before sending: status line first, Your turn last, prose within 180 words, no element codes,
    rule numbers or log ids in sentences, and every number in a FACT line cited. Returns ok and issues."""
    lines = [l for l in text.strip().splitlines() if l.strip()]
    issues = []
    if not lines or not re.match(r"^\W*Step \d{1,2} of 12: .+\| *Certified \d of 8 *\| *Waiting on you: .+\| *Focus: ", lines[0]):
        issues.append("The status line is not the first line.")
    yt = [i for i, l in enumerate(lines) if re.match(r"^\W*your turn", l, re.I)]
    if not yt:
        issues.append("There is no 'Your turn'.")
    body = re.sub(r"```.*?```", " ", text, flags=re.S)
    prose = [l for l in body.splitlines() if l.strip() and not l.strip().startswith("|") and not re.match(r"^\W*Step \d", l)
             and not l.strip().lower().startswith("sources:")]
    words = sum(len(l.split()) for l in prose)
    if words > 180:
        issues.append(f"Prose is {words} words; the limit is 180.")
    p = "\n".join(prose)
    for rx, what in ((r"\b(IM|TP|NR|RO|FE|RQ|SS|LU|RU|ME)\b", "element codes"), (r"\bR\d{1,2}\b|\bsection \d", "rule or section numbers"),
                     (r"\b(S\d+-)?L\d{6}\b", "log ids in sentences")):
        hits = re.findall(rx, p.replace("CERTIFY", ""))
        if hits:
            issues.append(f"Remove {what}: {sorted(set(h if isinstance(h, str) else h[0] for h in hits))[:5]}")
    for l in body.splitlines():
        if re.search(r"\bFACT\b", l) and re.search(r"\d[\d,]{1,}", l) and not re.search(r"\[\d+\]", l):
            issues.append(f"A FACT line has a number without a citation: {l.strip()[:80]}")
    if yt:
        tail = "\n".join(lines[yt[-1]:])
        if tail.count("?") > 3:
            issues.append(f"'Your turn' asks {tail.count('?')} questions; ask at most three, one thing each.")
    if re.search(r"beside the chat", text, re.I) and not re.search(r"show all", text, re.I):
        issues.append("Content left beside the chat must also be offered here ('say \"show all\"').")
    return {"ok": not issues, "issues": issues, "prose_words": words}


def run_strategy(lines, *, source="pubmed", element, purpose, combine="AND", filters=None, label=None, search_date=None,
                 nb=None, origin=None):
    """Run each concept block, the combination and (optionally) the filtered combination; return the search card.

    lines = [(what the block covers, PubMed string), ...]; origin = ["topic" | "focus", ...] in the same order.
    """
    ids, warnings = [], []
    if source == "openalex":
        for i, (cov, q) in enumerate(lines):
            r = openalex_works(q, element=element, per_page=1, purpose=purpose, label=cov,
                               origin=(origin[i] if origin else None), to_date=(search_date or _today("-")).replace("/", "-"))
            if not r["ok"]:
                return r
            ids.append(r["log_ids"][0])
        combo = f" {combine} ".join(f"({q})" for _, q in lines)
        r = openalex_works(combo, element=element, filter=filters, purpose=purpose, label=label or "combined",
                           to_date=(search_date or _today("-")).replace("/", "-"), nb=nb)
        if not r["ok"]:
            return r
        ids.append(r["log_ids"][0])
        return _res(True, search_report([ids], purpose=purpose), ids, r["warnings"], count=r["count"], term=combo,
                    results=r["results"])
    if source != "pubmed":
        raise KitError("run_strategy runs PubMed or OpenAlex; use prepare_strategy for sources a member searches")
    for i, (cov, q) in enumerate(lines):
        r = pubmed_search(q, element=element, purpose=purpose, search_date=search_date, nb=nb,
                          origin=(origin[i] if origin else None), label=cov, _block=True)
        if not r["ok"]:
            return r
        ids.append(r["log_ids"][0])
    combo = f" {combine} ".join(f"({q})" for _, q in lines)
    if filters:
        combo = f"({combo}) AND {filters}"
    r = pubmed_search(combo, element=element, purpose=purpose, search_date=search_date, nb=nb, label=label or "combined")
    if not r["ok"]:
        return r
    ids.append(r["log_ids"][0])
    md = search_report([ids], purpose=purpose)
    return _res(True, md, ids, warnings, count=r["count"], term=combo)


# ---------------------------------------------------------------- sessions

def session_start(session):
    """Start a later session (R11): read the files, check the kit, return the status line, plan map and preferences."""
    _session_set(session=session, start_log=(_records()[-1]["id"] if _records() else None), start_head=_git_head(),
                 map_shown=False)
    warnings = []
    kit_notes = [r for r in _records() if r["kind"] == "note" and (r["parameters"] or {}).get("kit_file")]
    here = _p("env", "stir_l4_kit.py")
    if kit_notes and os.path.exists(here) and sha256_file(here) != kit_notes[0]["sha256"]:
        return _refuse("The saved helper kit has changed since the workspace was created; please check it before we continue.")
    prefs = [r["text"] for r in _records() if (r["parameters"] or {}).get("preference")]
    summaries = sorted(f for f in os.listdir(_p("reports")) if f.endswith("_summary.md"))
    md = status_line() + "\n\n" + plan_map()
    if summaries:
        md += f"\n\nLast session summary: {summaries[-1]}"
    return _res(True, md, [], warnings, preferences=prefs, topic=_plan().get("topic"), focus=_plan().get("focus"))


# ---------------------------------------------------------------- final report

REPORT_ORDER = ["IM", "TP", "NR", "RO", "FE", "RQ", "SS", "ME"]
_NOT_IN_PROMPT = ("Paper as an Object, Literature as a Tensor and Registering Evidence Dynamically: building them is not "
                  "available in this prompt version (it is being developed for a dedicated planning tool), so they may "
                  "not behave as intended here; any designs drafted at Step 7 are kept in the planning folder but were "
                  "not applied to studies.")
_PMID_RE = re.compile(r"PMID:?\s*(\d{5,9})")
_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s<>\]\)\"',;|]+)", re.I)


def link_refs(md):
    """Turn every PMID into a link to its PubMed page and every DOI into a link through doi.org (Markdown)."""
    md = re.sub(r"(?<!\[)\bPMID:?\s*(\d{5,9})\b(?!\]\()", lambda m: f"[PMID {m.group(1)}](https://pubmed.ncbi.nlm.nih.gov/{m.group(1)}/)", md)

    def doi(m):
        d = m.group(1).rstrip(".")
        tail = m.group(1)[len(d):]
        url = "https://doi.org/" + d.replace("(", "%28").replace(")", "%29")
        return f"[{d}]({url}){tail}"
    return re.sub(r"(?<![/\[\w.])(10\.\d{4,9}/(?:[^\s<>\[\]()\"',;|]|\([^\s()]*\))+)", doi, md)


def _inline_html(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', t)
    return t


def _md_html(md):
    """A small Markdown to HTML converter (headings, paragraphs, lists, tables, code blocks, emphasis, links)."""
    out, para, lines, i = [], [], md.split("\n"), 0

    def flush():
        if para:
            out.append("<p>" + _inline_html(" ".join(para)) + "</p>")
            para.clear()
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            body = "\n".join(lines[i + 1:j]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f"<pre>{body}</pre>")
            i = j + 1
            continue
        m = re.match(r"(#{1,6})\s+(.*)", ln)
        if m:
            flush()
            n = len(m.group(1))
            out.append(f"<h{n}>{_inline_html(m.group(2))}</h{n}>")
        elif ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            rows = [f"<tr>{''.join('<th>' + _inline_html(c) + '</th>' for c in cells(ln))}</tr>"]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(f"<tr>{''.join('<td>' + _inline_html(c) + '</td>' for c in cells(lines[i]))}</tr>")
                i += 1
            out.append("<table>" + "".join(rows) + "</table>")
            continue
        elif re.match(r"\s*([-*]|\d+\.)\s+", ln):
            flush()
            tag = "ol" if re.match(r"\s*\d+\.", ln) else "ul"
            items = []
            while i < len(lines) and re.match(r"\s*([-*]|\d+\.)\s+", lines[i]):
                items.append("<li>" + _inline_html(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])) + "</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue
        elif not ln.strip():
            flush()
        else:
            para.append(ln.strip())
        i += 1
    flush()
    return "\n".join(out)


_REPORT_CSS = ("body{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;max-width:820px;margin:32px auto;padding:0 16px;"
               "line-height:1.45;color:#1d2330}h1{font-size:24px}h2{font-size:19px;border-bottom:2px solid #12355b;"
               "color:#12355b;padding-bottom:3px;margin-top:28px}h3{font-size:15px;color:#12355b}h4{font-size:13.5px}"
               "table{border-collapse:collapse;width:100%;font-size:13px;margin:6px 0 12px}th,td{border:1px solid #d7dde8;"
               "padding:4px 6px;vertical-align:top;text-align:left}th{background:#eef2f8}pre{white-space:pre-wrap;"
               "background:#f3f5f9;border:1px solid #dfe4ec;border-radius:6px;padding:6px 8px;font-size:12px}"
               ".meta{color:#5b6170;font-size:13px}.note{background:#fff4e8;border-left:3px solid #e07b24;padding:6px 10px}")


def final_report(protocol=None, *, title=None, out=None):
    """End of planning: write the final report (the plan as certified, then the protocol) as Markdown and HTML in
    reports/. Refuses when the protocol cites a PMID or DOI that no saved search result contains."""
    if protocol is None:
        cands = sorted((f for f in os.listdir(_p("protocol")) if re.match(r"protocol_v\d+.*\.md$", f)),
                       key=lambda f: (int(re.match(r"protocol_v(\d+)", f).group(1)), os.path.getmtime(_p("protocol", f))))
        if not cands:
            return _refuse("There is no protocol yet; the report needs one (Step 11).")
        protocol = "protocol/" + cands[-1]
    ppath = _p(*protocol.split("/"))
    if not os.path.exists(ppath):
        return _refuse(f"I cannot find the protocol file {protocol}.")
    ptext = _read(ppath)
    # every PMID and DOI the protocol cites must be in a saved search result (R1)
    raw = []
    for dp, _, fn in os.walk(_p("data", "raw")):
        for f in fn:
            try:
                with open(os.path.join(dp, f), "rb") as fh:
                    raw.append(fh.read().decode("utf-8", "ignore").lower())
            except OSError:
                pass
    blob = "\n".join(raw)
    pmids = sorted(set(_PMID_RE.findall(ptext)), key=int)
    dois = sorted({d.rstrip(".") for d in _DOI_RE.findall(ptext)})
    missing = [f"PMID {x}" for x in pmids if not re.search(r"(?<!\d)" + x + r"(?!\d)", blob)]
    missing += [f"DOI {d}" for d in dois if d.lower() not in blob]
    if missing:
        return _refuse("The protocol cites references that no saved search result contains: " + ", ".join(missing)
                       + ". Retrieve them first (for example k.pubmed_fetch), or remove them.", missing=missing)
    pl, tm = _plan(), _team()
    latest = {}
    for r in records(kind="certification"):
        latest[r["element"]] = r
    members = ", ".join(m.get("name", "") for m in tm.get("members", [])) or "not recorded"
    prompts = sorted({m.group(1) for f in os.listdir(_p("env")) for m in [re.search(r"prompt_v(\d+\.\d+)", f)] if m})
    models = _jload(_p("env", "model.json"), []) or []
    known = [m for m in models if str(m.get("model", "")).lower() not in ("", "not available")]
    model = (f"{known[-1]['provider']} {known[-1]['model']}" + (f" {known[-1]['version']}" if known[-1].get("version")
             else "") + f" (as recorded: {known[-1]['read_from']})") if known else "not available"
    rows = _records()
    day0, day1 = (rows[0]["time_utc"][:10], rows[-1]["time_utc"][:10]) if rows else (_today("-"), _today("-"))
    focus = (pl.get("focus") or {}).get("text") or "not stated"
    head = title or f"STIR-L4 planning report: {focus}"
    L = [f"# {head}", "",
         f"Planning team: {members}. Planning record: {len(rows)} entries, {day0} to {day1}. "
         f"STIR-L4 prompt version(s): {', '.join(prompts) or 'not recorded'}; helper kit {__version__}; "
         f"AI model: {model}.", "",
         "## 1. The plan, as certified", "",
         f"Topic: {(pl.get('topic') or {}).get('text') or 'not recorded'}", "", f"Research focus: {focus}", ""]
    for el in REPORT_ORDER:
        if el == "SS":
            L += [_NOT_IN_PROMPT, ""]
        r = latest.get(el)
        L += [f"### {name(el)}", ""]
        if not r:
            L += ["Not certified.", ""]
            continue
        L += [f"Certified by {r['actor']} on {r['time_utc'][:10]} at {r['time_utc'][11:16]} UTC ({r['id']}); reason, "
              f"as given: \"{r['reason']}\"", "", str(r.get("decision") or r.get("text") or ""), ""]
    body = link_refs(ptext).split("\n")
    ptitle = re.sub(r"^#\s*", "", body[0]) if body and body[0].startswith("# ") else "Protocol"
    if body and body[0].startswith("# "):
        body = body[1:]
    body = [("#" + ln) if re.match(r"#{1,5}\s", ln) else ln for ln in body]
    L += ["## 2. " + ptitle, ""] + body + ["", "---", "",
          "Produced with STIR-L4 (Singh UP, Walji M, Fenton S, Jiang X. STIR-L4: a Systems Thinking-based InfoRmatics "
          "approach for pLanning systematic reviews Leveraging Large Language models; citation to be updated on "
          "publication). Every search, answer, draft and certification behind this report is in log/actions.jsonl."]
    md = "\n".join(L) + "\n"
    out = out or f"reports/{_today('-')}_final_report"
    with open(_p(*(out + ".md").split("/")), "w", encoding="utf-8") as fh:
        fh.write(md)
    html_ = (f"<!doctype html><html><head><meta charset='utf-8'><title>{_inline_html(head)}</title>"
             f"<meta name='viewport' content='width=device-width, initial-scale=1'><style>{_REPORT_CSS}</style></head>"
             f"<body>{_md_html(md).replace('<p>' + _inline_html(_NOT_IN_PROMPT) + '</p>', '<p class=note>' + _inline_html(_NOT_IN_PROMPT) + '</p>')}</body></html>")
    with open(_p(*(out + ".html").split("/")), "w", encoding="utf-8") as fh:
        fh.write(html_)
    gaps = len(re.findall(r"\bGAP:", ptext))
    items = len(re.findall(r"(?m)^#{1,6}\s*(?:Item\s*)?\d{1,2}[a-d]?[\s.:]", ptext))
    lid = log("note", text=f"Final report written from {protocol} and the latest certifications",
              derived_path=out + ".html", refers_to=[r["id"] for r in latest.values()],
              parameters={"protocol": protocol, "gaps": gaps, "pmids": len(pmids), "dois": len(dois)})
    commit(f"Final report ({lid})", lid)
    certified = sum(1 for e in REPORT_ORDER if e in latest)
    text = (f"The final report is ready ({out}.html, beside the chat). It holds:\n"
            f"1. The plan as certified: the topic, the focus and {certified} of {len(REPORT_ORDER)} decisions, each "
            f"with who certified it, when and the reason as given.\n"
            f"2. The protocol ({protocol}): {items} numbered items, {gaps} marked GAP, citing {len(pmids)} PMIDs and "
            f"{len(dois)} DOIs, each found in a saved search result.")
    return _res(True, text, [lid], path=out + ".html", markdown=out + ".md", gaps=gaps)


def session_summary(*, next_questions, notes=None):
    """End a session (or 'pause'): write the summary, log it, and return it with the plan map for the chat."""
    s = _session()
    sess = records(since=s.get("start_log")) if s.get("start_log") else _records()
    pl = _plan()
    cert = [r["text"] for r in sess if r["kind"] in ("certification", "amendment")]
    reop = [f"{name(r['element'])}: {r['reason']}" for r in sess if r["kind"] == "reopen"]
    open_ = [name(c) for c in VARIABLES if pl["variables"][c]["status"] not in ("certified", "amended")]
    files = []
    if s.get("start_head") and shutil.which("git"):
        files = subprocess.run(["git", "-C", _ROOT, "diff", "--name-only", s["start_head"]], capture_output=True,
                               text=True).stdout.split()
    lines = [f"# Session summary ({s.get('session')}, {_today('-')})", "", status_line(), "",
             f"Topic: {(pl.get('topic') or {}).get('text')}", f"Focus: {(pl.get('focus') or {}).get('text') or 'not yet stated'}",
             "", "Settled this session:"] + [f"- {c}" for c in cert or ["nothing"]]
    lines += ["", "Reopened:"] + [f"- {x}" for x in reop or ["nothing"]]
    lines += ["", "Still open: " + (", ".join(open_) or "nothing")]
    lines += ["", "Next questions:"] + [f"- {q}" for q in next_questions]
    if notes:
        lines += ["", notes]
    nsearch = sum(1 for r in sess if (r["kind"] == "manual_retrieval") or (
        r["kind"] == "query" and r["endpoint"] not in ("efetch", "version", "esummary")
        and (r["parameters"] or {}).get("purpose") != "smoke test" and r["source"] != "mesh"))
    lines += ["", f"Searches this session: {nsearch}"]
    text = "\n".join(lines)
    folders = sorted({f.split("/")[0] for f in files})
    path = _p("reports", f"{_today('-')}_{s.get('session')}_summary.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text + ("\n\nFolders changed: " + ", ".join(folders) if folders else "") + "\n")
    lid = log("note", text="Session summary written", derived_path=_rel(path))
    commit(f"Session summary ({lid})", lid)
    return _res(True, text + "\n\n" + plan_map(), [lid], path=_rel(path))


def package(path=None):
    """Zip the workspace for the team to keep (no .env, licensed full text or git internals); use at session end."""
    path = path or os.path.join(os.path.dirname(_ROOT), os.path.basename(_ROOT) + f"_{_today('-')}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fn in os.walk(_ROOT):
            rel = os.path.relpath(dp, _ROOT)
            if rel.split(os.sep)[0] == ".git" or rel.replace(os.sep, "/").startswith("data/raw/text"):
                continue
            for f in fn:
                if f.startswith(".env") or f.endswith(".lock") and dp.endswith("log"):
                    continue
                z.write(os.path.join(dp, f), os.path.join(os.path.basename(_ROOT), rel, f))
    return path


def smoke_test(sources=("pubmed", "openalex", "ctgov"), *, nb="00_setup"):
    """Run one trivial query per source (two pages where the source pages) and report which work."""
    rows, ids, warnings, ok = [], [], [], True
    if "pubmed" in sources:
        good = []
        for start in (0, 1):
            st, body, err = _http(EUTILS + "esearch.fcgi", params=_ncbi_params(
                {"db": "pubmed", "term": "humans[mh]", "retmode": "json", "retmax": 1, "retstart": start}))
            if st == 200:
                lid = _next_id()
                raw, h = _save_pages(lid, "pubmed", "esearch", [body], "json")
                d = json.loads(body)["esearchresult"]
                ids.append(_append("query", source="pubmed", endpoint="esearch", parameters={"term": "humans[mh]",
                           "retstart": start, "purpose": "smoke test"}, n_total=int(d["count"]),
                                   n_retrieved=len(d.get("idlist", [])), raw_path=raw, sha256=h))
            good.append(st == 200)
        ok &= all(good)
        rows.append(("PubMed", "works" if all(good) else "failed"))
    if "openalex" in sources:
        r = openalex_works("systematic review", per_page=1, max_pages=2, purpose="smoke test")
        ok &= r["ok"]
        ids += r["log_ids"]
        if not r["ok"]:
            warnings.append(r["md"])
        rows.append(("OpenAlex", ("works" if _secret("OPENALEX_API_KEY") else "works (first page only, no key)")
                     if r["ok"] else "failed"))
    if "ctgov" in sources:
        r = ctgov_studies("asthma", element=None, page_size=1, max_pages=2, statuses=None, purpose="smoke test")
        ok &= r["ok"]
        ids += r["log_ids"]
        rows.append(("ClinicalTrials.gov", "works" if r["ok"] else "failed"))
    summary = "Sources: " + "; ".join(f"{a} {b}" for a, b in rows) + "."
    return _res(ok, summary, ids, warnings, summary=summary, table=rows)
