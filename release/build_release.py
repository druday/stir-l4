"""Build the files released to readers (and shipped with the paper) as version 1.0, from the development files.

Development versions (prompt v1.0 to v1.4, kit 1.1.x, quiz v1.1) stay in prompt/versions/, git history and CHANGELOG;
readers see one version. Release 1.0 = prompt v1.5, kit 1.1.9, quiz v1.1, model and core properties v1.0.
Run: python release/build_release.py   (writes release/1.0/)"""
import json
import os
import re
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "release", "1.0")
SRC = {"prompt": "prompt/versions/STIR-L4_prompt_v1.5.txt", "kit": "kit/stir_l4_kit.py",
       "quiz": "quiz/STIR-L4_calibration_quiz_v1.1.txt", "key": "quiz/quiz_key_v1.1.json",
       "model": "data/STIR-L4_model_v1.0.yaml", "core": "data/STIR-L4_core_properties_v1.0.csv"}


def read(k):
    return open(os.path.join(REPO, SRC[k]), encoding="utf-8").read()


def sub(t, a, b, n=None):
    c = t.count(a)
    assert c and (n is None or c == n), (a, c)
    return t.replace(a, b)


def build():
    os.makedirs(OUT, exist_ok=True)
    p = read("prompt")
    p = sub(p, "(prompt version 1.5, October 2026)", "(prompt version 1.0, October 2026)", 1)
    p = sub(p, "This is version 1.5 of the prompt", "This is version 1.0 of the prompt", 1)
    p = sub(p, "prompt_v1.5", "prompt_v1.0")
    assert not re.search(r"version 1\.[1-9]|_v1\.[1-9]|kit 1\.1", p)
    v10 = open(os.path.join(REPO, "prompt/versions/STIR-L4_prompt_v1.0.txt"), encoding="utf-8").read()
    sec = lambda t: t[t.index("\n## 1"):t.index("\n## 2")]
    # the model section differs from v1.0 only in the planning boundary (Review Universe definition and boundary line)
    changed = [l for l in sec(p).split("\n") if l not in sec(v10).split("\n")]
    assert len(changed) == 2 and all("Review Universe" in l or "Planning boundary" in l for l in changed), changed
    kit = read("kit")
    kit = sub(kit, '__version__ = "1.1.9"', '__version__ = "1.0.0"', 1)
    kit = sub(kit, '"""STIR-L4 helper kit, version 1.1.9 (for STIR-L4 prompt version 1.5).',
              '"""STIR-L4 helper kit, version 1.0.0 (for STIR-L4 prompt version 1.0).', 1)
    kit = sub(kit, 'prompt="STIR-L4_prompt_v1.5.txt"', 'prompt="STIR-L4_prompt_v1.0.txt"', 1)
    assert not re.search(r"1\.1\.\d|prompt_v1\.[1-9]", kit)
    q = sub(read("quiz"), "STIR-L4 calibration quiz (version 1.1).", "STIR-L4 calibration quiz (version 1.0).", 1)
    key = json.loads(read("key"))
    key["version"] = "1.0"
    files = {"STIR-L4_prompt_v1.0.txt": p, "stir_l4_kit.py": kit, "STIR-L4_calibration_quiz_v1.0.txt": q,
             "quiz_key_v1.0.json": json.dumps(key, indent=1, ensure_ascii=False) + "\n"}
    for name, text in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(text)
    for k in ("model", "core"):  # copied byte for byte (the CSV keeps its line endings)
        shutil.copyfile(os.path.join(REPO, SRC[k]), os.path.join(OUT, os.path.basename(SRC[k])))
    return OUT, len(p.split())


if __name__ == "__main__":
    out, words = build()
    print(f"wrote {out}: prompt {words} words; " + ", ".join(sorted(os.listdir(out))))
