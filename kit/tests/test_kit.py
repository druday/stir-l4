"""Tests for stir_l4_kit. Offline by default; set STIR_L4_LIVE=1 to also call PubMed, OpenAlex and ClinicalTrials.gov.

Run from the repository root:  python -m unittest discover -s kit/tests -v
"""
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "kit"))
import stir_l4_kit as k  # noqa: E402

DATA = os.path.join(REPO, "data")
LIVE = os.environ.get("STIR_L4_LIVE") == "1"
STATUS_RE = re.compile(r"^Step \d{1,2} of 12: .+ \| Certified \d of 8 \| Waiting on you: \d+ \| Focus: .+")


def fresh():
    d = tempfile.mkdtemp(prefix="stirl4_")
    ws = os.path.join(d, "ws")
    r = k.init(ws, calibration={"answers": "1. Ten elements ...", "score": "16 of 16, all critical", "graded_by": "Uday"},
               prompt=os.path.join(REPO, "prompt", "versions", "STIR-L4_prompt_v1.0.txt"),
               model=os.path.join(DATA, "STIR-L4_model_v1.0.yaml"),
               core_properties=os.path.join(DATA, "STIR-L4_core_properties_v1.0.csv"))
    return d, ws, r


class Offline(unittest.TestCase):
    def setUp(self):
        self.tmp, self.ws, self.init = fresh()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_and_log_schema(self):
        self.assertTrue(self.init["ok"], self.init)
        recs = k.records()
        self.assertEqual([r["kind"] for r in recs[:2]], ["calibration", "calibration"])
        self.assertEqual([r["id"] for r in recs], [f"L{i:06d}" for i in range(1, len(recs) + 1)])
        for r in recs:
            self.assertEqual(list(r.keys()), k.LOG_FIELDS)
        for d in k.FOLDERS:
            self.assertTrue(os.path.isdir(os.path.join(self.ws, d)))
        again = k.init(self.ws, calibration={"answers": "x", "score": "y", "graded_by": "z"})
        self.assertFalse(again["ok"])

    def test_model_check(self):
        r = k.check_model()
        self.assertTrue(r["ok"], r["computed"])
        self.assertEqual(r["computed"]["loops"], 47)
        self.assertEqual(r["computed"]["feasibility_loops"], 40)

    def test_status_line_and_map(self):
        line = k.status_line()
        self.assertRegex(line, STATUS_RE)
        self.assertTrue(line.startswith("Step 1 of 12: Topic"))
        self.assertIn("not yet stated", line)
        m = k.plan_map()
        self.assertEqual(sum(1 for l in m.splitlines() if re.match(r"\| \d+\. ", l)), 12)
        self.assertIn("Quick commands", m)
        self.assertNotIn("Quick commands", k.plan_map())
        self.assertNotRegex(m + line, r"\b(IM|TP|NR|RO|FE|RQ|SS|LU|RU|ME)\b")

    def test_intake_focus_and_purpose(self):
        k.consent("Uday", True)
        k.set_topic("role of SGLT2i in weight management in non diabetic asian populations", given_by="Uday")
        self.assertTrue(k.status_line().startswith("Step 2 of 12"))
        k.add_member("Uday", "solo", solo=True)
        a = k.record_interest("Uday", interest="what kind of weight is lost, fat or muscle",
                              seeks="learning; decide if a full review is worth it, maybe publish")
        self.assertTrue(a["ok"])
        bad = k.set_focus("cardiovascular outcomes of weight loss", agreed_by="Uday", refers_to=a["log_ids"])
        self.assertFalse(bad["ok"])
        self.assertIn("cardiovascular", bad["added"])
        good = k.set_focus("what kind of weight is lost, fat or muscle", agreed_by="Uday", refers_to=a["log_ids"])
        self.assertTrue(good["ok"], good)
        self.assertIn("Focus: what kind of weight is lost", k.status_line())
        self.assertFalse(k.confirm_states("TP", states=["research gaps"], by="agent")["ok"])
        self.assertFalse(k.confirm_states("TP", states=["world peace"], by="Uday")["ok"])
        self.assertTrue(k.confirm_states("TP", states=["Research gaps", "finding the right question"], by="Uday")["ok"])
        self.assertTrue(k.confirm_states("IM", states=["Learn the process"], by="Uday", member="Uday")["ok"])
        k.draft("TP", "Map cardiovascular outcomes")
        self.assertFalse(k.propose("TP", decision="Map cardiovascular outcomes", accepted_by="Uday")["ok"])
        k.draft("TP", "what kind of weight is lost, fat or muscle; decide if a full review is worth it")
        p = k.propose("TP", decision="what kind of weight is lost, fat or muscle; decide if a full review is worth it",
                      accepted_by="Uday")
        self.assertTrue(p["ok"], p)

    def _ready(self):
        k.set_topic("SGLT2 inhibitors for weight in non-diabetic Asian adults", given_by="Uday")
        k.add_member("Uday", "solo", solo=True)
        a = k.record_interest("Uday", interest="fat or muscle loss", seeks="learning")
        k.set_focus("fat or muscle loss", agreed_by="Uday", refers_to=a["log_ids"])
        k.draft("IM", "Uday: interest — fat or muscle loss; seeks — learning")
        k.propose("IM", decision="Uday: interest — fat or muscle loss; seeks — learning", accepted_by="Uday")

    def test_certify_plain_words(self):
        self._ready()
        line = k.certify_line("IM")
        self.assertTrue(line.startswith("CERTIFY Individual Motivation |"))
        self.assertIn("reason: ___", line)
        r = k.certify(element="IM", reviewer="Uday", said="Certify", reason="")
        self.assertFalse(r["ok"])
        self.assertEqual(r["refusal"], "What is your reason, in a few words?")
        r = k.certify(element="IM", reviewer="Uday", said="testing the workflow", reason="the workflow is fine")
        self.assertFalse(r["ok"])  # reason not in what was said
        r = k.certify(element="IM", said="certify, testing the workflow", reason="testing the workflow")
        self.assertTrue(r["ok"], r)
        self.assertIn("Certified 1 of 8", k.status_line())
        self.assertIn("reason: testing the workflow | Uday, solo", r["line"])
        again = k.certify(element="IM", reviewer="Uday", said="certify again ok", reason="again ok")
        self.assertFalse(again["ok"])

    def test_certify_order_rights_and_wording(self):
        self._ready()
        k.add_member("Jamal", "information specialist", can_certify=["Search Strategy"])
        k.certify_line("IM")
        r = k.certify(element="IM", reviewer="Jamal", said="certify because fine", reason="fine")
        self.assertFalse(r["ok"])
        self.assertIn("not listed", r["refusal"])
        r = k.certify(line="CERTIFY Need for a Review | new review | reason: no review covers it | Uday, solo")
        self.assertFalse(r["ok"])
        self.assertIn("comes first", r["refusal"])
        r = k.certify(line="CERTIFY Individual Motivation | something else | reason: ok then | Uday, solo")
        self.assertFalse(r["ok"])
        self.assertIn("differs", r["refusal"])

    def test_trace_and_reopen(self):
        self._ready()
        k.certify_line("IM")
        k.certify(element="IM", reviewer="Uday", said="certify: fine for a test", reason="fine for a test")
        t = k.trace(["RU"])
        self.assertIn("Feasibility", t["md_full"])
        self.assertNotRegex(t["md"], r"\b(FE|RU|SS|ME)\b")
        self.assertFalse(k.reopen("IM", agreed_by="agent", reason="x")["ok"])
        r = k.reopen("IM", agreed_by="Uday", reason="new member joined")
        self.assertTrue(r["ok"])
        self.assertIn("Reopened: Individual Motivation", k.status_line())
        self.assertTrue(k.status_line().startswith("Step 2 of 12"))

    def test_waiting_and_answer_links(self):
        q = k.ask("Uday", "What topic would you like to plan a systematic review on?")
        self.assertIn("Waiting on you: 1", k.status_line())
        k.answer("Uday", "SGLT2 inhibitors and weight")
        self.assertIn("Waiting on you: 0", k.status_line())
        self.assertEqual(k.records(kind="answer")[-1]["refers_to"], [q])

    def test_secrets_redacted_and_email(self):
        os.environ["OPENALEX_API_KEY"] = "sk-test-SECRET-123"
        try:
            lid = k.log("note", text="x", parameters={"url": "https://api.openalex.org/works?api_key=sk-test-SECRET-123",
                                                     "contact": "someone@example.org"})
            rec = k.records()[-1]
            self.assertEqual(rec["id"], lid)
            self.assertNotIn("SECRET", json.dumps(rec))
            self.assertNotIn("example.org", json.dumps(rec))
        finally:
            del os.environ["OPENALEX_API_KEY"]

    def test_screening_and_early(self):
        self.assertFalse(k.screen("R1", "include", by="agent", criterion="adults", source_ids={})["ok"])
        k.set_topic("topic words here", given_by="Uday")
        k.early(3, requested_by="Uday", open_items=["Team's Purpose"])
        self.assertIn("Step 2 of 12: Interests, focus and purpose (Step 3 started early)", k.status_line())

    def test_round1_fixes(self):
        k.set_topic("SGLT2 inhibitors for weight in non-diabetic Asian adults", given_by="Uday")
        k.add_member("Uday", "solo", solo=True)
        a = k.record_interest("Uday", interest="fat or muscle loss", seeks="learning")
        r = k.reflect_focus("fat or muscle loss", refers_to=a["log_ids"])
        self.assertTrue(r["ok"], r)
        self.assertIn("Focus: fat or muscle loss (to confirm)", k.status_line())
        k.ask("Uday", "If you like, type a contact email for PubMed searches", blocking=False)
        self.assertIn("Waiting on you: 0", k.status_line())
        k.set_focus("fat or muscle loss", agreed_by="Uday", refers_to=a["log_ids"])
        self.assertNotIn("to confirm", k.status_line())
        k.draft("IM", "Uday: fat or muscle loss; learning")
        k.propose("IM", decision="Uday: fat or muscle loss; learning", accepted_by="Uday")
        n_q = len(k.records(kind="question"))
        k.certify_line("IM")
        self.assertEqual(len(k.records(kind="question")), n_q + 1)
        k.certify(element="IM", reviewer="Uday", said="Certify", reason="")
        self.assertEqual(k.records(kind="question")[-1]["text"], "to Uday: What is your reason, in a few words?")
        ok = k.certify(element="IM", reviewer="Uday", said="testing the workflow", reason="testing the workflow")
        self.assertTrue(ok["ok"], ok)
        self.assertIn("Waiting on you: 0", k.status_line())
        k.draft("TP", "fat or muscle loss; learning")
        k.propose("TP", decision="fat or muscle loss; learning", accepted_by="Uday")
        t = k.trace(["IM"])
        self.assertIn("draft of Team's Purpose", t["md"])
        self.assertNotIn("flow", t["md"])
        self.assertIn("flow 1", t["md_full"])

    def test_round2_fixes(self):
        k.set_topic("SGLT2 inhibitors for weight in non-diabetic Asian adults", given_by="Uday")
        k.add_member("Uday", "solo", solo=True)
        a = k.record_interest("Uday", interest="fat or muscle loss", seeks="learning")
        r = k.reflect_focus("fat or muscle loss", refers_to=a["log_ids"])
        self.assertIn("in your words", r["md"])
        k.set_focus("fat or muscle loss", agreed_by="Uday", refers_to=a["log_ids"])
        k.draft("IM", "Uday: fat or muscle loss; learning")
        k.propose("IM", decision="Uday: fat or muscle loss; learning", accepted_by="Uday")
        k.certify_line("IM")
        self.assertIn("Waiting on you: 1 (Uday)", k.status_line())
        k.certify(element="IM", reviewer="Uday", said="Certify", reason="")
        self.assertIn("Waiting on you: 1 (Uday)", k.status_line())
        bad = k.certify(element="IM", reviewer="Uday", said="it says what that person wants from the review",
                        reason="it says what that person wants from the review",
                        asked="Does each entry say what that person wants from the review?")
        self.assertFalse(bad["ok"])
        ok = k.certify(element="IM", reviewer="Uday", said="certify, I am testing", reason="I am testing")
        self.assertTrue(ok["ok"], ok)
        self.assertIn("Waiting on you: 0", k.status_line())
        t = k.trace(["TP"])
        self.assertNotIn("undisclosed", t["md"])  # flow 2 needs an undisclosed motivation; flow 3 still applies
        c = k.check_reply("hello")
        self.assertFalse(c["ok"])
        good = (k.status_line() + "\nDone: recorded.\nFACT: PubMed returned 1,234 records [1].\nSources: [1] L000009 PubMed\n"
                "Next: draft.\nYour turn, Uday: ok?")
        self.assertTrue(k.check_reply(good)["ok"], k.check_reply(good))
        self.assertFalse(k.check_reply(good.replace(" [1].", ".").replace("Sources: [1]", "Sources:"))["ok"])
        self.assertTrue(k.steps_line().startswith("Steps: 1 done"))
        m = k.prepare_strategy("PROSPERO", [("SGLT2", "sglt2"), ("weight", "weight")], member="Uday", purpose="protocols")
        self.assertIn("pending: Uday", m["md"])

    def test_round3_fixes(self):
        k.set_team("sources", "not given", by="Uday")
        self.assertEqual(k.team()["sources"], [])
        k.set_topic("SGLT2 inhibitors for weight in non-diabetic Asian adults", given_by="Uday")
        k.add_member("Uday", "solo", solo=True)
        a = k.record_interest("Uday", interest="fat or muscle loss", seeks="learning")
        k.set_focus("fat or muscle loss", agreed_by="Uday", refers_to=a["log_ids"])
        line = k.certify_line("IM", draft="Uday: fat or muscle loss; learning")
        self.assertIn("fat or muscle loss; learning", line)
        self.assertEqual(k.plan()["variables"]["IM"]["status"], "unsettled")
        ok = k.certify(element="IM", reviewer="Uday", said="certify, testing it", reason="testing it")
        self.assertTrue(ok["ok"], ok)
        self.assertEqual(k.plan()["variables"]["IM"]["decision"], "Uday: fat or muscle loss; learning")
        reply = k.status_line() + "\nDone: x.\nNext: y.\nYour turn, Uday: a? b? c? d?"
        self.assertTrue(any("at most three" in i for i in k.check_reply(reply)["issues"]))
        self.assertIn("Labels: FACT", k.plan_map())

    def test_round4_fixes(self):
        k.set_topic("VR for needle procedures in children", given_by="Maya")
        for n in ("Maya", "Jamal", "Priya"):
            k.add_member(n, "member", can_certify=["all"] if n == "Maya" else [])
        self.assertFalse(k.propose("RO", decision="never shown wording", accepted_by="Maya")["ok"])
        k.ask("all three of you", "1. a 2. b 3. c", items=3)
        line = k.status_line()
        self.assertIn("Waiting on you: 3 (Maya, Jamal, Priya)", line)
        with self.assertRaises(k.KitError):
            k.certify_line("IM", draft="learning (both; strike one if wrong)")
        recs = [{"pmid": "1", "title": "A review", "year": "2025",
                 "abstract": "Background. We searched databases. Virtual reality reduced pain in children during venipuncture."}]
        t = k.review_table(recs, terms=["pain", "child*"])
        self.assertIn("“", t)
        self.assertIn("pain", t)

    def test_full_run_fixes(self):
        k.set_topic("t", given_by="Uday")
        k.add_member("Uday", "solo", solo=True)
        k.early(3, requested_by="Uday", open_items=["x"])
        # pilot screening keeps the step at 9 until the team marks it finished
        plan = k.plan()
        for c in ("IM", "TP", "NR", "RO", "FE", "RQ", "SS"):
            plan["variables"][c]["status"] = "certified"
        k._save_plan(plan)
        for e in ("PAO", "LAT", "RED"):
            k._append("certification", actor="Uday", element=e, reason="ok", text="x")
        self.assertTrue(k.status_line().startswith("Step 9 of 12"))
        self.assertNotIn("started early", k.status_line())
        k.screen("R1", "include", by="Uday", criterion="fits", source_ids={"pmid": "1"})
        self.assertTrue(k.status_line().startswith("Step 9 of 12"))
        k.step_done(9, by="Uday")
        self.assertTrue(k.status_line().startswith("Step 10 of 12"))
        plan = k.plan(); plan["variables"]["ME"]["status"] = "certified"; k._save_plan(plan)
        self.assertTrue(k.status_line().startswith("Step 11 of 12"))
        with self.assertRaises(k.KitError):
            k.register("OSF Registries", by="Uday")
        k.register("OSF Registries", by="Uday", status="not submitted", note="test run")
        self.assertTrue(k.status_line().startswith("Step 12 of 12"))
        self.assertIn("not submitted (OSF Registries)", k.plan_map())
        self.assertNotIn("registered (", k.plan_map())
        self.assertFalse(k._submitted(k.plan()))
        k.commitment("Uday", "commit to the studies included so far", included=["1"])
        self.assertEqual(k.plan()["commitment"]["included"], ["1"])
        self.assertIn("Planning complete", k.status_line())
        line = k.steps_line()
        for n in (9, 11, 12):
            self.assertIn(f"{n} done", line)

    def test_final_report(self):
        k.set_topic("t", given_by="Uday")
        k.add_member("Uday", "solo", solo=True)
        k._append("certification", actor="Uday", element="NR", reason="no review answers it", decision="new review",
                  text="CERTIFY Need for a Review")
        os.makedirs(os.path.join(self.ws, "protocol"), exist_ok=True)
        with open(os.path.join(self.ws, "data", "raw", "L000099_pubmed_efetch_1.xml"), "w") as f:
            f.write("<PMID>25554246</PMID><ArticleId IdType='doi'>10.1186/2046-4053-4-1</ArticleId>")
        pr = os.path.join(self.ws, "protocol", "protocol_v2.md")
        with open(pr, "w") as f:
            f.write("# Protocol, version 2\n\n## 1a Title\n\nA title.\n\n## 2 Registration\n\nGAP: not yet registered; "
                    "Uday decides.\n\n## References\n\n1. Moher D, et al. PRISMA-P. PMID 25554246; "
                    "doi:10.1186/2046-4053-4-1\n2. Unretrieved. PMID 11111111\n")
        r = k.final_report()
        self.assertFalse(r["ok"])
        self.assertIn("PMID 11111111", r["md"])
        with open(pr, "w") as f:
            f.write("# Protocol, version 2\n\n## 1a Title\n\nA title.\n\n## 2 Registration\n\nGAP: not yet registered; "
                    "Uday decides.\n\n## References\n\n1. Moher D, et al. PRISMA-P. PMID 25554246; "
                    "doi:10.1186/2046-4053-4-1\n")
        r = k.final_report()
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["gaps"], 1)
        with open(os.path.join(self.ws, r["path"]), encoding="utf-8") as f:
            html = f.read()
        self.assertIn("The plan, as certified", html)
        self.assertIn("not available in this prompt version", html)
        self.assertIn("no review answers it", html)
        self.assertIn("<h3>2 Registration</h3>", html)
        self.assertIn('<a href="https://pubmed.ncbi.nlm.nih.gov/25554246/">PMID 25554246</a>', html)
        self.assertIn('<a href="https://doi.org/10.1186/2046-4053-4-1">10.1186/2046-4053-4-1</a>', html)
        self.assertNotIn("screened", html)

    def test_systematic_filter_rules(self):
        r = k.pubmed_search("sglt2 AND systematic[sb]", element="Feasibility", purpose="primary")
        self.assertFalse(r["ok"])
        r = k.pubmed_search("sglt2", element="Need for a Review", purpose="reviews")
        self.assertFalse(r["ok"])


@unittest.skipUnless(LIVE, "set STIR_L4_LIVE=1 for live API tests")
class Live(unittest.TestCase):
    def setUp(self):
        self.tmp, self.ws, _ = fresh()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_pubmed_strategy_and_verify(self):
        k.set_topic("SGLT2 inhibitors and weight in people without diabetes", given_by="Uday")
        r = k.run_strategy([("SGLT2 inhibitors", '"Sodium-Glucose Transporter 2 Inhibitors"[Mesh] OR empagliflozin[tiab] OR dapagliflozin[tiab]'),
                            ("weight", '"Body Weight"[Mesh] OR weight[tiab]')],
                           element="Need for a Review", purpose="reviews", filters="systematic[sb]",
                           label="Existing reviews", nb="01_need_A", origin=["topic", "focus"])
        self.assertTrue(r["ok"], r)
        self.assertGreater(r["count"], 0)
        self.assertIn("```", r["md"])
        self.assertIn("How to read the strings", r["md"])
        self.assertIn("Sources:", r["md"])
        v = k.verify()
        self.assertTrue(v["ok"], v)
        with open(os.path.join(self.ws, "notebooks", "01_need_A.ipynb")) as f:
            nb = json.load(f)
        self.assertGreaterEqual(len(nb["cells"]), 5)

    def test_mesh_openalex_ctgov(self):
        m = k.mesh_lookup("metformin")
        self.assertTrue(m["ok"])
        self.assertTrue(any(d["ui"] == "D008687" for d in m["descriptors"]))
        c = k.ctgov_studies("obesity", "empagliflozin", element="Feasibility")
        self.assertTrue(c["ok"])
        self.assertIsNotNone(c["data_timestamp"])
        o = k.openalex_works("SGLT2 inhibitor weight loss", element="Feasibility", max_pages=2)
        if not o["ok"] and "daily allowance" in o["md"]:
            self.skipTest("OpenAlex's daily allowance for this network is used up; the kit said so plainly")
        self.assertTrue(o["ok"])
        s = k.run_strategy([("SGLT2 inhibitors", "SGLT2 OR empagliflozin OR dapagliflozin"), ("weight", "weight OR adiposity")],
                           source="openalex", element="Need for a Review", purpose="reviews", filters="type:review",
                           origin=["topic", "focus"])
        self.assertTrue(s["ok"], s)
        self.assertIn("| 2 | weight | focus |", s["md"])
        self.assertTrue(k.verify()["ok"])

    def test_setup(self):
        r = k.setup()
        if not r["ok"] and "daily allowance" in r["md"]:
            self.skipTest("OpenAlex's daily allowance for this network is used up; set-up said so plainly")
        self.assertTrue(r["ok"], r)
        self.assertLessEqual(len(r["md"].splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
