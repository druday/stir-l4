"""Count the loops of the STIR-L4 flow graph and check how the counts depend on the way the graph is drawn.

Input: data/STIR-L4_model_v1.0.yaml (Supplementary File 4), read as a directed multigraph of 10 elements and 27 flows.
A loop is an elementary circuit: a chain of flows that returns to its starting element without passing through any
element twice. Two flows between the same pair of elements (flows 2 and 3) make separate loops.

Run: python analysis/count_loops.py          (prints the counts in Supplementary Table S1 and Section S1)
"""
import os
from collections import Counter

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(os.path.dirname(HERE), "data", "STIR-L4_model_v1.0.yaml")


def load(path=MODEL):
    m = yaml.safe_load(open(path, encoding="utf-8"))
    return [e["id"] for e in m["elements"]], m["flows"]


def loops(flows):
    """Every elementary circuit, as a list of flow ids, each found once (it starts at its smallest element)."""
    out = {}
    for f in flows:
        out.setdefault(f["from"], []).append(f)
    nodes = sorted({f["from"] for f in flows} | {f["to"] for f in flows})
    found = []

    def walk(start, node, seen, path):
        for f in out.get(node, []):
            if f["to"] == start:
                found.append(path + [f["id"]])
            elif f["to"] not in seen and nodes.index(f["to"]) > nodes.index(start):
                walk(start, f["to"], seen | {f["to"]}, path + [f["id"]])

    for s in nodes:
        walk(s, s, {s}, [])
    return found


def per_element(flows, cycles):
    by_id = {f["id"]: f for f in flows}
    c = Counter()
    for cyc in cycles:
        for el in {by_id[i]["from"] for i in cyc}:
            c[el] += 1
    return c


def summary(label, flows):
    cyc = loops(flows)
    c = per_element(flows, cyc)
    top = max(c.values()) if c else 0
    first = ", ".join(sorted(k for k, v in c.items() if v == top))
    print(f"{label:<44} {len(cyc):>3} loops; feasibility on {c.get('FE', 0):>2}; most frequent: {first} ({top})")
    return cyc, c


def main():
    _, flows = load()
    cyc, c = summary("STIR-L4 as proposed", flows)
    print("\nLoops on which each element lies (Supplementary Table S1):")
    for el, n in c.most_common():
        print(f"  {el:<3} {n}")
    print("\nOther encodings (Supplementary Section S1):")
    merged = [f for f in flows if f["id"] != 3]
    summary("flows 2 and 3 merged into one", merged)
    summary("record flows removed", [f for f in flows if f["class"] != "record"])
    weak = [f["id"] for f in flows if f["strength"] == "weak"]
    summary(f"weak flows removed {tuple(weak)}", [f for f in flows if f["strength"] != "weak"])
    for fid in [f["id"] for f in flows if f["type"] == "feedback"]:
        summary(f"feedback flow {fid} removed", [f for f in flows if f["id"] != fid])


if __name__ == "__main__":
    main()
