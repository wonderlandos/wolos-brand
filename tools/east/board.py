# SPDX-License-Identifier: GPL-2.0-or-later
"""Side-by-side boards for the east study: current vs east, with the scores (score.py).

  python3 -I design/tools/east/board.py icons OUT.png [--json OUT.json]
  python3 -I design/tools/east/board.py pair NAME CURRENT NEW KIND OUT.png [--tree-a A.json --tree-b B.json]
"""
import io
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score as SC  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
FONT = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
FONT_B = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INK, DIM, BG, LINE = (21, 21, 32), (86, 85, 99), (241, 241, 250), (220, 219, 230)
GOOD, BAD = (31, 152, 75), (197, 73, 48)


def font(sz, bold=False):
    try:
        # Noto Sans CJK JP: Latin and kana in one face, so labels with ウォルOS render
        return ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc" % ("Bold" if bold else "Regular"), sz, index=0)
    except OSError:
        return ImageFont.load_default()


def raster(path, w, h=None):
    if path.endswith(".svg"):
        args = ["rsvg-convert", "-w", str(w)] + (["-h", str(h)] if h else []) + [path]
        im = Image.open(io.BytesIO(subprocess.run(args, check=True, capture_output=True).stdout))
    else:
        im = Image.open(path)
        r = w / im.width
        im = im.resize((w, h or round(im.height * r)), Image.LANCZOS)
    return im.convert("RGBA")


def scored(path, kind, tree=None):
    s = SC.score_pixels(path, kind)
    if tree:
        t = SC.tree_scores(json.load(open(tree)))
        s["proportion"]["score"] = round(0.5 * s["proportion"]["score"] + 0.5 * t["proportion"], 1)
        s["density"]["score"] = round(0.75 * s["density"]["score"] + 0.25 * t["rhythm"], 1)
        s["palette"]["score"] = round(0.5 * s["palette"]["score"] + 0.5 * t["palette_adjacency"], 1)
        s["sha"]["score"] = round(max(0.0, s["sha"]["score"] - 5 * t["edge_lines"]), 1)
        s["tree"] = t
    s["total"] = SC.total(s)
    return s


def score_lines(dr, x, y, a, b, sz=15):
    f, fb = font(sz), font(sz, True)
    for i, r in enumerate(SC.RULES + ("total",)):
        va = a[r]["score"] if r != "total" else a["total"]
        vb = b[r]["score"] if r != "total" else b["total"]
        ff = fb if r == "total" else f
        yy = y + i * (sz + 7)
        dr.text((x, yy), r, font=ff, fill=INK if r == "total" else DIM)
        dr.text((x + 110, yy), f"{va:5.1f}", font=ff, fill=INK)
        dr.text((x + 165, yy), "->", font=f, fill=DIM)
        dr.text((x + 195, yy), f"{vb:5.1f}", font=ff, fill=GOOD if vb > va else BAD if vb < va else INK)
    return y + (len(SC.RULES) + 1) * (sz + 7)


ICONS = [("Settings", "icons/apps/wolos-settings.svg", "icons/apps/small/wolos-settings.svg", "settings"),
         ("Store", "icons/apps/wolos-software.svg", "icons/apps/small/wolos-software.svg", "store"),
         ("Files", "icons/apps/wolos-files.svg", "icons/apps/small/wolos-files.svg", "files"),
         ("Console", "icons/apps/wolos-terminal.svg", "icons/apps/small/wolos-terminal.svg", "console"),
         ("Doctor", None, None, "doctor"),
         ("Atlas Folio", None, None, "atlas-folio")]
EXTERNAL = {"Doctor": "/home/ubuntu/wolos/wt/webapp-int/webapps/doctor/icon.svg",
            "Atlas Folio": "/home/ubuntu/wolos/wt/atlas-brand/brand/atlas/directions/atlas-b-folio-512.svg"}


def icons_board(out, js=None):
    sizes = (16, 32, 64, 128)
    colw = sum(sizes) + 12 * len(sizes)
    W = 40 + 150 + colw + 40 + colw + 40 + 270
    rowh = 128 + 44
    H = 150 + rowh * len(ICONS) + 60
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    dr.text((40, 30), "East icons: current vs east geometry, 16 / 32 / 64 / 128 px", font=font(28, True), fill=INK)
    dr.text((40, 70), "Scores from design/tools/east/score.py on a 256 px render (0-100 per rule; total = mean). "
            "16 and 32 px use each set's small variant.", font=font(15), fill=DIM)
    x_cur, x_new, x_sc = 40 + 150, 40 + 150 + colw + 40, 40 + 150 + 2 * colw + 80
    dr.text((x_cur, 110), "current", font=font(18, True), fill=DIM)
    dr.text((x_new, 110), "east", font=font(18, True), fill=DIM)
    dr.text((x_sc, 110), "rule   current -> east", font=font(18, True), fill=DIM)
    table = {}
    for r, (name, big, small, east) in enumerate(ICONS):
        y = 150 + r * rowh
        big = EXTERNAL.get(name) or os.path.join(D, big)
        small = EXTERNAL.get(name) or os.path.join(D, small)
        nb = os.path.join(D, "east", "icons", f"wolos-{east}.svg")
        ns = os.path.join(D, "east", "icons", "small", f"wolos-{east}.svg")
        dr.text((40, y + 50), name, font=font(20, True), fill=INK)
        for x0, (b, s) in ((x_cur, (big, small)), (x_new, (nb, ns))):
            x = x0
            for sz in sizes:
                ic = raster(s if sz <= 32 else b, sz, sz)
                im.paste(ic, (x, y + 128 - sz), ic)
                dr.text((x, y + 134), str(sz), font=font(11), fill=DIM)
                x += sz + 12
        a, b = scored(big, "icon"), scored(nb, "icon")
        table[name] = {"current": a, "east": b}
        score_lines(dr, x_sc, y, a, b, 13)
        dr.line((40, y + rowh - 8, W - 40, y + rowh - 8), fill=LINE)
    im.save(out)
    if js:
        json.dump(table, open(js, "w"), indent=1, default=str)
    return table


def pair_board(name, a, b, kind, out, tree_a=None, tree_b=None, width=900, labels=("current", "east"), note=""):
    ia, ib = raster(a, width), raster(b, width)
    h = max(ia.height, ib.height)
    W = 40 + 2 * width + 40 + 40 + 300
    H = 120 + h + 60
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    dr.text((40, 28), name, font=font(26, True), fill=INK)
    if note:
        dr.text((40, 66), note, font=font(14), fill=DIM)
    for i, (ii, lab) in enumerate(((ia, labels[0]), (ib, labels[1]))):
        x = 40 + i * (width + 40)
        dr.text((x, 92), lab, font=font(16, True), fill=DIM)
        bgc = Image.new("RGBA", ii.size, (255, 255, 255, 255))
        bgc.alpha_composite(ii)
        im.paste(bgc.convert("RGB"), (x, 116))
    sa, sb = scored(a, kind, tree_a), scored(b, kind, tree_b)
    x = 40 + 2 * (width + 40)
    dr.text((x, 92), "rule   current -> east", font=font(16, True), fill=DIM)
    score_lines(dr, x, 120, sa, sb, 15)
    im.save(out)
    return {"current": sa, "east": sb}


def rows_board(title, note, rows, out, width=640):
    """rows: (label, current or None, east, kind, ground hex, tree_a, tree_b). Returns the scores."""
    blocks, table = [], {}
    for label, a, b, kind, ground, ta, tb in rows:
        ims = [raster(x, width) if x else None for x in (a, b)]
        h = max(i.height for i in ims if i)
        blk = Image.new("RGB", (40 + 2 * width + 40 + 40 + 300, h + 70), BG)
        dr = ImageDraw.Draw(blk)
        dr.text((40, 8), label, font=font(18, True), fill=INK)
        for i, ii in enumerate(ims):
            x = 40 + i * (width + 40)
            if ii is None:
                dr.text((x, 50), "(no current counterpart: new for 0.13)", font=font(15), fill=DIM)
                continue
            g = Image.new("RGBA", ii.size, ground)
            g.alpha_composite(ii)
            blk.paste(g.convert("RGB"), (x, 40))
        sb = scored(b, kind, tb)
        sa = scored(a, kind, ta) if a else None
        x = 40 + 2 * (width + 40)
        if sa:
            score_lines(dr, x, 40, sa, sb, 14)
        else:
            dr.text((x, 40), f"east total {sb['total']:.1f}", font=font(14, True), fill=INK)
        table[label] = {"current": sa, "east": sb}
        blocks.append(blk)
    W = blocks[0].width
    H = 120 + sum(b.height for b in blocks) + 20
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    dr.text((40, 28), title, font=font(26, True), fill=INK)
    dr.text((40, 68), note, font=font(14), fill=DIM)
    dr.text((40, 92), "current", font=font(16, True), fill=DIM)
    dr.text((40 + width + 40, 92), "east", font=font(16, True), fill=DIM)
    y = 120
    for b in blocks:
        im.paste(b, (0, y))
        y += b.height
    im.save(out)
    return table


def main(argv):
    if argv[0] == "icons":
        js = argv[argv.index("--json") + 1] if "--json" in argv else None
        t = icons_board(argv[1], js)
        for k, v in t.items():
            print(f"{k:12s} {v['current']['total']:5.1f} -> {v['east']['total']:5.1f}")
    elif argv[0] == "pair":
        _, name, a, b, kind, out = argv[:6]
        ta = argv[argv.index("--tree-a") + 1] if "--tree-a" in argv else None
        tb = argv[argv.index("--tree-b") + 1] if "--tree-b" in argv else None
        r = pair_board(name, a, b, kind, out, ta, tb)
        print(json.dumps({k: v["total"] for k, v in r.items()}))


if __name__ == "__main__":
    main(sys.argv[1:])
