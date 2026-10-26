"""Build STIR-L4 prompt v1.2 from v1.1 by checked edits. Theory unchanged. Run: python prompt/build_v1_2.py
- rc1: appraisal of whether the question is clinically, scientifically and logically sound, at Need for a Review (Step 3).
- rc2: consent split approved by the first author (2026-10-25): research content (topic, interests, focus, purpose,
  question terms, certification reasons, instructions) is kept in members' own words, because the plan may hold nothing
  they did not say; consent governs what members say about themselves (motivations, career aims, opinions).
- rc3: after the full-pipeline run: no key is ever typed into the chat; the end of pilot screening, a registry
  submission (or its absence) and the commitment are recorded through the kit, so the status line reaches Step 12."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.1.txt")
OUT = os.path.join(HERE, "versions", "STIR-L4_prompt_v1.2.txt")

SOUND = ("Before drafting the case, appraise whether the question is sound, as a DRAFT the team can challenge: "
         "clinically (does the population use or need the intervention, and is the outcome meaningful for patients), "
         "scientifically (is there a plausible mechanism or earlier evidence that the intervention affects the outcome, and "
         "can the outcome be measured, and how) and logically (do the population, intervention, comparison and outcome fit "
         "one another and the purpose). Base every point on FACTS from logged searches (for example a search for the "
         "mechanism, or for how the outcome is measured), cite them, and say what remains uncertain; never rely on memory "
         "(R1). If the evidence suggests that the question rests on a mistaken assumption, say so plainly and offer ways to "
         "reframe it; the team decides (R9). ")

EDITS = [
    ("# STIR-L4 PLANNING ASSISTANT (prompt version 1.1, October 2026)",
     "# STIR-L4 PLANNING ASSISTANT (prompt version 1.2, October 2026)"),
    ("Save the prompt file the team provides (STIR-L4_prompt_v1.1.txt) unchanged as env/prompt_v1.1.txt",
     "Save the prompt file the team provides (STIR-L4_prompt_v1.2.txt) unchanged as env/prompt_v1.2.txt"),
    ("generate it by code from section 1 of env/prompt_v1.1.txt", "generate it by code from section 1 of env/prompt_v1.2.txt"),
    ("This is version 1.1 of the prompt", "This is version 1.2 of the prompt"),
    ("readers are free to use the framework and this prompt with their own LLMs.",
     "readers are free to use the framework and this prompt with their own LLMs (the prompt is licensed CC BY 4.0, and the authors ask that the STIR-L4 paper be cited when it is used)."),
    ("Ask each member's consent before recording their words verbatim. Consent covers what members say about themselves and their views (interests, motivations, purposes, opinions): for a member who chose summaries, record these only in your own words. Instructions to you (for example \"just start\") and certification messages and reasons are kept as given.",
     "Research content is kept in members' own words, because the plan may hold nothing they did not say: the topic, each member's interest within it, the focus, the purpose, the terms of the question, certification messages and reasons, and instructions to you (for example \"just start\"). Ask each member's consent before keeping word for word what they say about themselves (motivations, career aims, opinions); without it, record those in your own words, labeled as a summary."),
    ('Add, once: "May I keep your exact words, or only summaries you confirm?" (section 2.1), and give one example reply that answers everything, for example: "Sam (solo). 1. ... 2. ... 3. ... Summaries are fine." Say that certification messages and reasons are always kept as given. Without an answer, keep summaries they confirm and do not ask again.',
     'Add, once: "Your topic, interests, focus and approvals are kept in your own words, so the plan adds nothing. May I also keep word for word what you say about yourselves (your motivations and opinions), or only summaries?" (section 2.1), and give one example reply that answers everything, for example: "Sam (solo). 1. ... 2. ... 3. ... Summaries are fine." Without an answer, keep summaries of those statements and do not ask again.'),
    ('Without consent to exact words, write what members said about themselves as "summarized", in your own words, and never claim that none of their words were kept.',
     'Interests and the focus stay in members\' words; without consent, write what members said about themselves (motivations, opinions) as "summarized", in your own words.'),
    ("with the time; keep their exact words only with their consent (section 2.1), otherwise a summary they confirm.",
     "with the time, in their own words (section 2.1)."),
    ("Then show the Need for a Review states as options (R5), draft the case for a new review, an update or no review, and ask a reviewer to certify it.",
     SOUND + "Then show the Need for a Review states as options (R5), draft the case for a new review, an update or no review, and ask a reviewer to certify it."),
    ("Never copy API keys, passwords, identifiable patient data or confidential unpublished data into any file.",
     "Never copy API keys, passwords, identifiable patient data or confidential unpublished data into any file. Never ask anyone to type a key or password into the chat; a member who has one adds it to the private settings file (.env) or as an environment variable (section 3.3)."),
    ('Ask for an OpenAlex key only when a search needs more than its first 100 results, calling it "a free access code".',
     'Ask for an OpenAlex key only when a search needs more than its first 100 results or OpenAlex says its free daily allowance is used up, calling it "a free access code" that a member adds to the private settings file, not to the chat.'),
    ("k.review_table, k.session_start,", "k.review_table, k.screen, k.step_done, k.register, k.commitment, k.session_start,"),
    ("After each batch, follow flows 20, 21 and 8 (R4) and raise any decision they may reopen, especially Feasibility and, through flow 17, the Review Objective.",
     "After each batch, follow flows 20, 21 and 8 (R4) and raise any decision they may reopen, especially Feasibility and, through flow 17, the Review Objective. When the team says the pilot screening is finished, record it (with the kit, k.step_done(9, by=<member>))."),
    ("Record the registry submission (kind registration). Any later reopening is an amendment (R6).",
     "Record the registry submission (kind registration), or that the protocol was not submitted and why (with the kit, k.register(..., status=\"not submitted\", note=<reason>)). Any later reopening is an amendment (R6)."),
    ("which ends planning (kind commitment).", "which ends planning (kind commitment; with the kit, k.commitment)."),
]


def build():
    t = open(SRC, encoding="utf-8").read()
    for a, b in EDITS:
        assert t.count(a) == 1, (t.count(a), a[:70])
        t = t.replace(a, b)
    assert "prompt_v1.1" not in t and "version 1.1" not in t
    return t


if __name__ == "__main__":
    t = build()
    open(OUT, "w", encoding="utf-8").write(t)
    print(f"wrote {OUT}: {len(t.split())} words")
