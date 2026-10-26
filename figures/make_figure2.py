"""Figure 2: Paper as an Object (PAO), Literature as a Tensor (LAT) and Registering Evidence Dynamically (RED), three
proposed representations, applied in turn, that make the evidence behind planning traceable. One example throughout
(SGLT2 inhibitors and the kind of weight lost); values are illustrative.
Run: python figures/make_figure2.py figures/Figure2.png   (prints any text that overflows or overlaps)
"""
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

for f in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/System/Library/Fonts/Supplemental/Arial Italic.ttf"]:
    try:
        font_manager.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.family"] = "Arial"

INK, MUTED, LINE = "#1F2430", "#5B6170", "#9AA0AC"
PANEL = "#F5F6F8"
C_ID, C_STD, C_REV, C_LED = "#4F5D7E", "#23877C", "#7B5EA7", "#9A7B3F"   # the four kinds of property
REPORTED, NOTREP, CONFLICT, UNKNOWN = "#4A63C9", "#C9CDD6", "#E08A2E", "#FFFFFF"
DOT, BAD, THIN = "#2F3FE8", "#D1443B", "#C27A1A"
CARD = "#596074"

W, H = 2040, 1128
PANELS = [(30, 640), (700, 680), (1410, 600)]
TEXTS = []          # (artist, right limit) for the overflow check


def box(ax, x, y, w, h, fc, ec=LINE, lw=1.0, r=10, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                zorder=z))


def arrow(ax, p0, p1, color=INK, lw=1.8, ms=16, z=8):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, zorder=z,
                                 shrinkA=0, shrinkB=0))


def t(ax, x, y, s, size=10.5, maxx=None, **kw):
    kw.setdefault("color", INK)
    kw.setdefault("va", "center")
    kw.setdefault("ha", "left")
    a = ax.text(x, y, s, fontsize=size, zorder=kw.pop("zorder", 9), **kw)
    TEXTS.append((a, maxx))
    return a


def block(ax, x, y, w, h, n, color, title, tag):
    box(ax, x, y, w, h, "white", ec=color, lw=1.4, r=8, z=4)
    ax.add_patch(Circle((x + 22, y + 24), 13, fc=color, ec="none", zorder=6))
    t(ax, x + 22, y + 24, str(n), 10.5, ha="center", color="white", weight="bold")
    t(ax, x + 44, y + 24, title, 11.5, weight="bold")
    t(ax, x + w - 12, y + 24, tag, 10, ha="right", color=color, style="italic")


def check(fig, ax):
    """Report text that runs past its limit (or its panel) and pairs of texts that overlap."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    boxes = []
    for a, maxx in TEXTS:
        bb = a.get_window_extent(r)
        (x0, y0), (x1, y1) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
        x0, x1, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
        lim = maxx
        if lim is None:
            for px, pw in PANELS:
                if px <= a.get_position()[0] <= px + pw:
                    lim = px + pw - 6
        if lim is not None and x1 > lim + 1:
            print(f"OVERFLOW by {x1 - lim:.0f}: {a.get_text()[:60]!r}")
        if x0 < 0 or x1 > W:
            print(f"OFF CANVAS: {a.get_text()[:60]!r}")
        boxes.append((x0, ya, x1, yb, a.get_text()))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                print(f"OVERLAP: {a[4][:40]!r} / {b[4][:40]!r}")


def draw(out):
    fig = plt.figure(figsize=(13.6, 13.6 * H / W), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    # ------------------------------------------------------------------ banner
    box(ax, 30, 16, W - 60, 120, "#EEF2FB", ec="#8C9BD6", lw=1.2, r=14)
    t(ax, 55, 46, "STIR-L4", 13.5, weight="bold", maxx=W - 40)
    t(ax, 182, 46, "plans a systematic review with human input, through a staged, step-by-step process, with "
                   "continuous awareness of the whole process as a system.", 11.5, maxx=W - 40)
    t(ax, 55, 82, "Three proposed representations, applied in turn, make the evidence behind planning traceable: Paper as an "
                  "Object, Literature as a Tensor and Registering Evidence Dynamically.", 11.5, maxx=W - 40)
    t(ax, 55, 114, "Every value keeps its source and can be checked by a person or the model; a person's correction "
                   "always overrides the model.", 10.5, color=MUTED, maxx=W - 40)

    py, ph = 156, H - 156 - 18
    titles = [("(a)  Paper as an Object (PAO)", "each paper is one object: three kinds of property and a ledger"),
              ("(b)  Literature as a Tensor (LAT)", "each paper becomes one row; layers add a third property"),
              ("(c)  Registering Evidence Dynamically (RED)", "the landscape of the field: every kind of study on one atlas")]
    for (x, w), (title, sub) in zip(PANELS, titles):
        box(ax, x, py, w, ph, PANEL, ec="#B5BAC4", lw=1.0, r=14)
        t(ax, x + 22, py + 32, title, 13, weight="bold")
        t(ax, x + 22, py + 60, sub, 10.5, color=MUTED, style="italic")

    # ------------------------------------------------------------------ (a) PAO
    cx, cy, cw = 50, 276, 560
    bx, bw = cx + 14, cw - 28
    heights = [128, 128, 156, 214]
    ch = 46 + sum(heights) + 26 * (len(heights) - 1) + 14
    off = 24
    for k, lab in ((2, "Paper 3"), (1, "Paper 2")):
        box(ax, cx + off * k, cy - off * k, cw, ch, "#E9EBF0", ec="#A9AFBA", lw=1.0, r=12, z=2)
        t(ax, cx + off * k + cw - 12, cy - off * k + 12, lab, 9, ha="right", color=MUTED, zorder=3, maxx=W)
    box(ax, cx, cy, cw, ch, "white", ec=CARD, lw=1.6, r=12, z=3)
    ax.add_patch(FancyBboxPatch((cx, cy), cw, 34, boxstyle="round,pad=0,rounding_size=12", fc=CARD, ec="none",
                                zorder=4))
    ax.add_patch(Rectangle((cx, cy + 18), cw, 16, fc=CARD, ec="none", zorder=4))
    t(ax, cx + 16, cy + 17, "Paper 1", 11.5, color="white", weight="bold")
    t(ax, cx + cw - 16, cy + 17, "one object", 10, ha="right", color="white")

    y = cy + 46
    block(ax, bx, y, bw, heights[0], 1, C_ID, "Identity", "immutable")
    t(ax, bx + 18, y + 56, "DOI · PMID · PMCID · OpenAlex ID · title", 10.2)
    t(ax, bx + 18, y + 80, "authors · year · abstract · retraction status", 10.2)
    t(ax, bx + 18, y + 108, "used to merge duplicates and link reports of one study", 9.6, color=C_ID,
      style="italic")

    y += heights[0] + 26
    block(ax, bx, y, bw, heights[1], 2, C_STD, "Standard properties", "verifiable")
    t(ax, bx + 18, y + 56, "publication type · affiliations · funding", 10.2)
    t(ax, bx + 18, y + 80, "study design · sample size · setting · country", 10.2)
    t(ax, bx + 18, y + 106, "the same fields in every review", 9.8, color=MUTED, style="italic")

    y += heights[1] + 26
    block(ax, bx, y, bw, heights[2], 3, C_REV, "Custom data extraction", "for this review")
    t(ax, bx + 18, y + 56, "drug: empagliflozin · comparator: placebo", 10.2)
    t(ax, bx + 18, y + 80, "population: adults without diabetes", 10.2)
    t(ax, bx + 18, y + 104, "outcomes: fat mass, lean mass (DXA scan)", 10.2)
    t(ax, bx + 18, y + 128, "result: change at week 24, for each outcome", 10.2)

    y += heights[2] + 26
    block(ax, bx, y, bw, heights[3], 4, C_LED, "Ledger", "the evidence for each value")
    rows = [("value", "fat mass, week 24: −1.1 kg"), ("source", "“…fell by 1.1 kg…” (Results, p. 5)"),
            ("status", "reported  (or not reported, unclear)"), ("checked", "the model extracted it; Uday verified it")]
    for k, (a, b) in enumerate(rows):
        yy = y + 58 + k * 28
        if k % 2 == 0:
            ax.add_patch(Rectangle((bx + 10, yy - 13), bw - 20, 26, fc="#F6F2EA", ec="none", zorder=5))
        t(ax, bx + 18, yy, a, 9.8, color=MUTED, weight="bold")
        t(ax, bx + 110, yy, b, 10.2, style="italic" if a == "source" else "normal")
    t(ax, bx + 18, y + 178, "extract  →  verify  →  cite  →  ask a person", 10.2)
    t(ax, bx + 18, y + 200, "a person's correction overrides the model", 9.8, color=MUTED, style="italic")
    card_bottom = cy + ch

    # ------------------------------------------------------------------ (b) LAT
    cols = [("DOI", C_ID), ("year", C_ID), ("design", C_STD), ("size", C_STD), ("P", C_REV), ("I", C_REV),
            ("C", C_REV), ("O", C_REV)]
    rowsP = ["Paper 1", "Paper 2", "Paper 3", "Paper 4", "Paper 5", "Paper 6", "Paper 7", "Paper n"]
    cs, rh = 56, 52
    gx, gy = 830, 372
    nC, nR = len(cols), len(rowsP)
    gw, gh = nC * cs, nR * rh

    def grid_status(seed, p_rep):
        random.seed(seed)
        g = []
        for i in range(nR):
            row = []
            for j in range(nC):
                if j < 2:
                    row.append(REPORTED)
                    continue
                r = random.random()
                row.append(REPORTED if r < p_rep[j] else (NOTREP if r < p_rep[j] + 0.25 else
                                                          (CONFLICT if r < p_rep[j] + 0.31 else UNKNOWN)))
            g.append(row)
        return g

    layers = [(31, [1, 1, .8, .7, .55, .6, .3, .2]), (17, [1, 1, .85, .8, .7, .45, .7, .5]),
              (7, [1, 1, .85, .8, .7, .6, .5, .45])]
    alphas = [0.4, 0.62, 0.9]
    dx, dy = 36, -36
    for li, (seed, prob) in enumerate(layers):
        off_ = 2 - li
        lx, ly = gx + off_ * dx, gy + off_ * dy
        g = grid_status(seed, prob)
        if off_ == 0:
            g[0] = [REPORTED] * 7 + [REPORTED]
            g[3][6] = CONFLICT
        z = 4 + 2 * li
        for i in range(nR):
            for j in range(nC):
                ax.add_patch(Rectangle((lx + j * cs, ly + i * rh), cs, rh, fc=g[i][j], ec="white", lw=1.4, zorder=z,
                                       alpha=alphas[li]))
        ax.add_patch(Rectangle((lx, ly), gw, gh, fc="none", ec="#7A8090", lw=1.0, zorder=z + 1))
    # depth arrow: the third property
    arrow(ax, (gx + gw + 8, gy - 6), (gx + gw + 2 * dx + 8, gy + 2 * dy - 6), color=MUTED, lw=1.4, ms=12)
    t(ax, gx + gw + 2 * dx + 8, gy + 2 * dy - 50, "third property, e.g., region: one layer per level", 10, ha="right",
      color=MUTED, style="italic")
    t(ax, 718, 270, "one paper → one row", 10.2, color=CARD, weight="bold")
    # the row that Paper 1 condenses into
    ax.add_patch(Rectangle((gx - 2, gy - 2), gw + 4, rh + 4, fc="none", ec=CARD, lw=2.4, zorder=12))
    for i, r in enumerate(rowsP):
        t(ax, gx - 10, gy + i * rh + rh / 2, r, 10.2, ha="right", weight="bold" if i == 0 else "normal",
          color=INK if i == 0 else MUTED)
    for j, (c, col) in enumerate(cols):
        t(ax, gx + j * cs + cs / 2, gy + gh + 18, c, 9.4, ha="center", color=MUTED)
    groups = [(0, 2, C_ID, "1 identity"), (2, 4, C_STD, "2 standard"), (4, 8, C_REV, "3 custom (PICO)")]
    for a, b, col, lab in groups:
        ax.add_patch(Rectangle((gx + a * cs + 3, gy + gh + 36), (b - a) * cs - 6, 6, fc=col, ec="none", zorder=6))
        t(ax, gx + (a + b) * cs / 2, gy + gh + 58, lab, 10, ha="center", color=col, weight="bold")

    # funnel: the paper card condenses into its row
    fx0, fx1 = cx + cw + 2 * off + 4, gx - 84
    ax.add_patch(Polygon([(fx0, cy + 10), (fx1, gy - 2), (fx1, gy + rh + 2), (fx0, card_bottom - 10)], closed=True,
                         fc=CARD, alpha=0.10, ec="none", zorder=1.5))
    for (a0, a1) in (((fx0, cy + 10), (fx1, gy - 2)), ((fx0, card_bottom - 10), (fx1, gy + rh + 2))):
        ax.plot([a0[0], a1[0]], [a0[1], a1[1]], color=CARD, lw=1.1, ls=(0, (4, 3)), zorder=2)

    # legend and notes
    ly0 = gy + gh + 100
    for k, (c, name) in enumerate([(REPORTED, "reported"), (NOTREP, "not reported"), (CONFLICT, "conflicting"),
                                   (UNKNOWN, "unclear")]):
        lx = 724 + k * 158
        ax.add_patch(Rectangle((lx, ly0 - 10), 20, 20, fc=c, ec="#9AA0AC", lw=0.8, zorder=6))
        t(ax, lx + 28, ly0, name, 10.2)
    notes = ["Each cell is one value with its ledger (panel a, block 4).",
             "Duplicates are merged first, so each study is counted once.",
             "Columns and their levels are fixed before the search.",
             "Layers add a third property (for example region or year),",
             "so candidate gaps that two-way tables hide become visible."]
    for k, s in enumerate(notes):
        t(ax, 724, ly0 + 40 + k * 27, s, 10.2, color=INK if k == 0 else MUTED)

    # ------------------------------------------------------------------ (c) RED
    px = PANELS[2][0]
    acols = ["in\nsilico", "in\nvitro", "animal", "observ.\n(EHR)", "trial", "meta-\nanalysis"]
    arows = ["molecule", "cell", "tissue", "person", "population"]
    ax0, ay0, aw, ah = px + 156, 336, 72, 74
    t(ax, px + 22, 262, "The atlas: one topic, every kind of study", 11.5, weight="bold")
    t(ax, px + 22, 288, "drawn before the search; each circle is a paper from (b)", 10, color=MUTED)
    for j, c in enumerate(acols):
        t(ax, ax0 + j * aw + aw / 2, ay0 + 2, c, 9.6, ha="center", color=MUTED, linespacing=1.05)
    for i, r in enumerate(arows):
        t(ax, ax0 - 8, ay0 + 30 + i * ah + ah / 2, r, 10.2, ha="right", color=MUTED)
    t(ax, ax0 + 3 * aw, ay0 + 30 + 5 * ah + 22, "kind of study: mechanistic  →  clinical", 10.2, ha="center",
      color=MUTED)
    t(ax, px + 22, ay0 + 30 + 2.5 * ah, "level: molecule  →  population", 10.2, ha="center", color=MUTED,
      rotation=270)
    papers = {(0, 0): ["5"], (0, 1): ["3"], (1, 1): ["3", "6"], (2, 2): ["7"], (3, 3): ["2"], (4, 3): ["2", "9"],
              (3, 4): ["1", "4", "12", "15", "n"], (3, 5): ["10"], (4, 5): ["10"]}
    for i in range(len(arows)):
        for j in range(len(acols)):
            x, y = ax0 + j * aw, ay0 + 30 + i * ah
            ax.add_patch(Rectangle((x, y), aw, ah, fc="white", ec=LINE, lw=1.0, zorder=5))
            for k, num in enumerate(papers.get((i, j), [])):
                cxx, cyy = x + 14 + (k % 3) * 22.5, y + 15 + (k // 3) * 24
                ax.add_patch(Circle((cxx, cyy), 11, fc=DOT, ec="white", lw=0.8, zorder=6))
                t(ax, cxx, cyy, num, 9.6 if len(num) < 2 else 8.4, ha="center", color="white", weight="bold")

    def tag(i, j, s_, col):
        dyy = ah / 2 if s_ == "empty" else ah - 12
        t(ax, ax0 + j * aw + aw / 2, ay0 + 30 + i * ah + dyy, s_, 9.6, ha="center", color=col, weight="bold")
    tag(3, 4, "crowded", MUTED)
    tag(2, 2, "thin", THIN)
    tag(2, 4, "empty", BAD)
    tag(1, 2, "empty", BAD)

    ry = ay0 + 30 + 5 * ah + 46
    bxw = 556
    box(ax, px + 22, ry, bxw, 152, "white", ec="#7A8090", r=8, z=4)
    t(ax, px + 38, ry + 26, "Placing a paper, as in image registration", 11.5, weight="bold")
    steps = ["1  by rule, from its properties (e.g., its design)", "2  by how closely its text matches a section",
             "3  by a person, when neither settles it"]
    for k, s_ in enumerate(steps):
        t(ax, px + 38, ry + 56 + k * 25, s_, 10.2)
    t(ax, px + 38, ry + 132, "a paper can sit in more than one section (2, 3, 10)", 9.8, color=MUTED, style="italic")
    ry2 = ry + 164
    box(ax, px + 22, ry2, bxw, 142, "white", ec="#7A8090", r=8, z=4)
    t(ax, px + 38, ry2 + 26, "Reading the atlas", 11.5, weight="bold")
    reads = ["thresholds: empty 0 · thin 1–2 · crowded 5 or more",
             "an empty section is a candidate gap; a targeted search",
             "speaks only for the sources and dates searched;",
             "what the atlas shows returns to feasibility"]
    for k, s_ in enumerate(reads):
        t(ax, px + 38, ry2 + 56 + k * 25, s_, 10.2)

    arrow(ax, (1358, 520), (1404, 520), lw=2.4, ms=20)

    check(fig, ax)
    fig.savefig(out, dpi=300)
    if out.endswith(".png"):
        fig.savefig(out[:-4] + ".pdf")
    plt.close(fig)


if __name__ == "__main__":
    draw(sys.argv[1] if len(sys.argv) > 1 else "Figure2.png")
    print("ok")
