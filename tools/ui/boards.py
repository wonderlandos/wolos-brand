# SPDX-License-Identifier: GPL-2.0-or-later
"""Boards for the UI work: grammar sheet, symbolic set, primitives (batch 1).

  python3 -I design/tools/ui/boards.py grammar|symbolic|primitives OUT.png
"""
import io
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "east"))
import board as B  # noqa: E402
import calculus as K  # noqa: E402
import geom  # noqa: E402
import sheet  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(D, "ui", "symbolic")
CUR = os.path.join(D, "icons", "symbolic")


def svg_png(path, w, ink=None):
    src = open(path, encoding="utf-8").read()
    if ink:
        src = re.sub(r'style="color:#[0-9a-fA-F]+"', f'style="color:{ink}"', src)
    out = subprocess.run(["rsvg-convert", "-w", str(w), "-"], input=src.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGBA")


def grammar(out):
    S = 15                                      # px per fen on the sheet
    G = 24 * S
    W, H = 4 * (G + 30) + 30, G + 440
    im = Image.new("RGB", (W, H), B.BG)
    d = ImageDraw.Draw(im)
    d.text((30, 10), "UI symbolic grammar: 24 fen master, art box 21, glyph 15, stroke 2 (16 px: 1.5), light upper left", font=B.font(20, True), fill=B.INK)
    names = ["security-high", "folder", "network-wireless-encrypted", "preferences-system-notifications"]
    notes = ["G4 juzhe shoulders (ridge to eave); 3:2 body", "G4 juzhe tab slope; named 21 x 15 body", "G5 the solid lock lands lower right; arcs open away", "G4 flare folded like an eave; G6 dim leaf = 0.35"]
    for k, n in enumerate(names):
        x0 = 30 + k * (G + 30)
        y0 = 50
        d.rectangle([x0, y0, x0 + G, y0 + G], fill=(255, 255, 255), outline=B.LINE)
        for i in range(25):
            major = i % 3 == 0
            d.line([x0 + i * S, y0, x0 + i * S, y0 + G], fill=(224, 224, 238) if major else (240, 240, 248))
            d.line([x0, y0 + i * S, x0 + G, y0 + i * S], fill=(224, 224, 238) if major else (240, 240, 248))
        # art box 21 (1.5..22.5) and glyph box 15 (4.5..19.5)
        d.rectangle([x0 + 1.5 * S, y0 + 1.5 * S, x0 + 22.5 * S, y0 + 22.5 * S], outline=(116, 82, 245), width=2)
        d.rectangle([x0 + 4.5 * S, y0 + 4.5 * S, x0 + 19.5 * S, y0 + 19.5 * S], outline=(0, 134, 60), width=1)
        d.line([x0 + 12 * S, y0, x0 + 12 * S, y0 + G], fill=(197, 138, 0))
        d.line([x0, y0 + 12 * S, x0 + G, y0 + 12 * S], fill=(197, 138, 0))
        ic = svg_png(os.path.join(OUT, "24", f"{n}-symbolic.svg"), G, "#151520")
        im.paste(ic, (x0, y0), ic)
        # the light: an arrow from the upper left, dx:dy = 1:2
        d.line([x0 + 3, y0 + 3, x0 + 3 + 14, y0 + 3 + 28], fill=(197, 138, 0), width=3)
        d.polygon([(x0 + 17 - 6, y0 + 31 - 2), (x0 + 17 + 6, y0 + 31 - 2), (x0 + 17, y0 + 40)], fill=(197, 138, 0))
        d.text((x0, y0 + G + 6), n, font=B.font(13, True), fill=B.INK)
        d.text((x0, y0 + G + 24), notes[k], font=B.font(12), fill=B.DIM)
        # 16 px, enlarged x8 (pixels), and the real size
        a16 = svg_png(os.path.join(OUT, "16", f"{n}-symbolic.svg"), 16, "#151520")
        bg = Image.new("RGBA", (16, 16), (255, 255, 255, 255))
        bg.alpha_composite(a16)
        im.paste(bg.resize((128, 128), Image.NEAREST).convert("RGB"), (x0, y0 + G + 46))
        c16 = svg_png(os.path.join(CUR, f"{n}-symbolic.svg"), 16, "#151520")
        bg2 = Image.new("RGBA", (16, 16), (255, 255, 255, 255))
        bg2.alpha_composite(c16)
        im.paste(bg2.resize((128, 128), Image.NEAREST).convert("RGB"), (x0 + 138, y0 + G + 46))
        d.text((x0, y0 + G + 178), "16 px new", font=B.font(11), fill=B.DIM)
        d.text((x0 + 138, y0 + G + 178), "16 px current", font=B.font(11), fill=B.DIM)
        # legend of rules, right of the pixels
        if k == 3:
            rows = ["G1 stroke 2 fen (1.5 px at 16), round caps and joins", "G2 sizes on named fen: 21 15 10 6 4 3 2", "G3 corners r 3 (>= 12 wide), 2 below, pill when h <= 6", "G4 slopes with a ridge and an eave are juzhe curves",
                    "G5 one light, upper left: gaps open and the one solid mass sits lower right", "G6 the second leaf is the same glyph at 0.35"]
            for j, t in enumerate(rows):
                d.text((30 + 0, y0 + G + 200 + j * 18), t, font=B.font(13), fill=B.INK)
    im.save(out)


def symbolic(out):
    import check
    names = ["system-search", "network-wireless", "network-wireless-signal-ok", "bluetooth-active", "audio-volume-high", "audio-volume-muted", "battery-good", "battery-full-charging",
             "display-brightness", "night-light", "wolos-dark-mode", "wolos-control-center", "wolos-dock", "system-shutdown", "system-lock-screen", "system-reboot",
             "system-log-out", "preferences-system-notifications", "security-high", "emblem-system", "folder", "go-next", "list-add", "window-close",
             "view-app-grid", "wolos-widgets", "wolos-assistant", "wolos-capture-selection", "weather-showers", "weather-few-clouds", "x-office-calendar", "camera-photo"]
    res = json.load(open("/tmp/ui_check.json")) if os.path.exists("/tmp/ui_check.json") else check.run(sorted(__import__("glyphs").ICONS))
    sm = check.summary(res)
    cols, big = 8, 72
    cw, ch = 2 * big + 60, big + 76
    rows = (len(names) + cols - 1) // cols
    W, H = cols * cw // 1 + 20, rows * ch + 130
    im = Image.new("RGB", (W, H), B.BG)
    d = ImageDraw.Draw(im)
    d.text((14, 8), f"UI symbolic set, {len(res)} icons: current (left) vs proposed (right); small: 24/16 light, 24/16 dark", font=B.font(20, True), fill=B.INK)
    cur_t, new_t = sm["total"]
    d.text((14, 38), f"tile score (score.py, icon, glyph 15 fen on a 21 fen tile) mean over {len(res)}: current {cur_t:.1f} -> proposed {new_t:.1f}; wins {sm['wins']}/{len(res)}", font=B.font(14), fill=B.INK)
    d.text((14, 58), "  ".join(f"{r} {a:.1f}->{b:.1f}" for r, (a, b) in sm["rules"].items()), font=B.font(12), fill=B.DIM)
    c = sm["craft"]
    d.text((14, 78), "16 px craft, icons passing (current -> proposed): " + ", ".join(f"{k} {int(v[0])}->{int(v[1])}/{v[2]}" for k, v in c.items()) + f"; edge softness {sm['crisp'][0]:.2f}->{sm['crisp'][1]:.2f}", font=B.font(12), fill=B.DIM)
    for i, n in enumerate(names):
        x0, y0 = 14 + (i % cols) * cw, 110 + (i // cols) * ch
        cur = os.path.join(CUR, f"{n}-symbolic.svg")
        new24 = os.path.join(OUT, "24", f"{n}-symbolic.svg")
        new16 = os.path.join(OUT, "16", f"{n}-symbolic.svg")
        d.rectangle([x0, y0, x0 + 2 * big + 14, y0 + big + 6], fill=(255, 255, 255))
        ic = svg_png(cur, big, "#151520"); im.paste(ic, (x0 + 3, y0 + 3), ic)
        ic = svg_png(new24, big, "#151520"); im.paste(ic, (x0 + big + 11, y0 + 3), ic)
        x = x0
        for pth, px, dark in ((new24, 24, False), (new16, 16, False), (new24, 24, True), (new16, 16, True), (cur, 16, False)):
            bgc = (21, 21, 29) if dark else (255, 255, 255)
            d.rectangle([x, y0 + big + 10, x + px + 6, y0 + big + 16 + px], fill=bgc)
            ic = svg_png(pth, px, "#F8F8FC" if dark else "#151520")
            im.paste(ic, (x + 3, y0 + big + 13), ic)
            x += px + 10
        d.text((x0, y0 + big + 44), n[:30], font=B.font(11), fill=B.DIM)
    im.save(out)


def primitives(out):
    import subprocess as sp
    sys.path.insert(0, os.path.join(HERE, "..", "east"))
    import score as SC
    base = os.path.join(D, "ui", "primitives")
    rows = []
    for v in ("current", "proposed"):
        png = f"/tmp/prim-{v}.png"
        sp.run(["rsvg-convert", os.path.join(base, f"{v}-light.svg"), "-o", png], check=True)
        s = B.scored(png, "screen", os.path.join(base, f"{v}.json"))
        rows.append(s)
    W, H = 576 * 2 + 3 * 24 + 120, 400 * 2 + 3 * 24 + 360
    im = Image.new("RGB", (1360, 1140), B.BG)
    d = ImageDraw.Draw(im)
    d.text((24, 10), "UI primitives: current (left) vs proposed (right), light above, dark below; frame 576 = one ruler", font=B.font(20, True), fill=B.INK)
    for col, v in enumerate(("current", "proposed")):
        for r, mode in enumerate(("light", "dark")):
            ic = svg_png(os.path.join(base, f"{v}-{mode}.svg"), 576)
            im.paste(ic, (24 + col * 600, 50 + r * 442), ic)
    y = 50 + 2 * 442 + 6
    B.score_lines(d, 24, y, rows[0], rows[1], 15)
    tbl = [("control h", "24", "24"), ("button / entry r", "6", "8"), ("card r", "10", "12"), ("switch", "30x18 pad 2", "40x24 pad 2"), ("circle control", "28", "28 (unchanged)"),
           ("segmented", "20 r4", "24 r6"), ("toggle tile h", "76", "84 (zucai)"), ("shadow", "0 1px 2px black .08", "1px 2px 4px ink .12 (1:2)")]
    for i, (k, a, b) in enumerate(tbl):
        d.text((560, y + i * 22), k, font=B.font(14), fill=B.DIM)
        d.text((760, y + i * 22), a, font=B.font(14), fill=B.INK)
        d.text((1010, y + i * 22), b, font=B.font(14, True), fill=B.GOOD)
    im.save(out)
    return rows




# ------------------------------------------------------------------ batch 2: dock
def dock(out_a, out_b, work="/tmp/dock"):
    import dock as DK
    import score as SC
    os.makedirs(work, exist_ok=True)
    DK.main(["render", work])
    G = "/home/ubuntu/wolos/wt/webapp-int/crates/shell/tests/golden"
    sc = {}
    for v in ("current", "proposed"):
        for m in ("light", "dark"):
            sc[(v, m)] = B.scored(os.path.join(work, f"dock-{v}-{m}-1x.png"), "screen", os.path.join(work, f"dock-{v}.json"))
    W = 1060
    im = Image.new("RGB", (W, 40 + 2 * (3 * 150 + 20) + 330), B.BG)
    d = ImageDraw.Draw(im)
    d.text((16, 8), "Dock at 1x: as shipped, current geometry with A2 icons, proposed", font=B.font(18, True), fill=B.INK)
    y = 40
    for m in ("light", "dark"):
        gold = Image.open(os.path.join(G, f"dock-{m}.png")).convert("RGB")
        d.text((16, y), f"{m}: as shipped (golden, old icons)", font=B.font(13, True), fill=B.DIM)
        im.paste(gold.crop((0, 8, 960, 120)), (16, y + 18))
        y += 140
        for v in ("current", "proposed"):
            p = Image.open(os.path.join(work, f"dock-{v}-{m}-1x.png"))
            s = sc[(v, m)]
            d.text((16, y), f"{m}: {v} geometry, A2 icons   score {s['total']:.1f}", font=B.font(13, True), fill=B.INK if v == "current" else B.GOOD)
            im.paste(p, (16, y + 18))
            y += 140
    # score table
    d.text((16, y + 4), "score.py (kind screen, with the shelf layout tree)", font=B.font(15, True), fill=B.INK)
    cols = [("light", "current"), ("light", "proposed"), ("dark", "current"), ("dark", "proposed")]
    for j, (m, v) in enumerate(cols):
        d.text((200 + j * 130, y + 28), f"{m[:1].upper()} {v}", font=B.font(13, True), fill=B.DIM)
    for i, r in enumerate(SC.RULES + ("total",)):
        yy = y + 50 + i * 20
        d.text((16, yy), r, font=B.font(13), fill=B.DIM)
        for j, (m, v) in enumerate(cols):
            val = sc[(v, m)][r]["score"] if r != "total" else sc[(v, m)]["total"]
            other = sc[("current", m)][r]["score"] if r != "total" else sc[("current", m)]["total"]
            col = B.INK if v == "current" else (B.GOOD if val > other else B.BAD if val < other else B.INK)
            d.text((200 + j * 130, yy), f"{val:5.1f}", font=B.font(13, r == "total"), fill=col)
    im = im.crop((0, 0, W, y + 50 + 9 * 20 + 10))
    im.save(out_a)
    # 2x detail + the measurement table
    crops = []
    for m in ("light", "dark"):
        for v in ("current", "proposed"):
            p = Image.open(os.path.join(work, f"dock-{v}-{m}-2x.png"))
            crops.append((m, v, p.crop((0, 0, 1040, p.height))))
    ch = crops[0][2].height
    rows = DK.table()
    H2 = 40 + 4 * (ch + 26) + 60 + len(rows) * 40
    im2 = Image.new("RGB", (1070, H2), B.BG)
    d2 = ImageDraw.Draw(im2)
    d2.text((16, 8), "Dock at 2x (HiDPI), left half: light and dark, current geometry vs proposed", font=B.font(18, True), fill=B.INK)
    y = 40
    for m, v, c in crops:
        d2.text((16, y), f"{m} {v}", font=B.font(13, True), fill=B.INK if v == "current" else B.GOOD)
        im2.paste(c, (16, y + 18))
        y += ch + 26
    d2.text((16, y + 6), "Measurements (px; 1 fen = 4 px)", font=B.font(16, True), fill=B.INK)
    import textwrap
    for i, (k, a, b) in enumerate(rows):
        yy = y + 36 + i * 40
        d2.text((16, yy), k, font=B.font(12, True), fill=B.DIM)
        d2.text((170, yy), "\n".join(textwrap.wrap(a, 62)[:2]), font=B.font(11), fill=B.INK)
        d2.text((620, yy), "\n".join(textwrap.wrap(b, 56)[:2]), font=B.font(11), fill=B.GOOD)
    im2.save(out_b)
    return sc




# ------------------------------------------------------------------ batch 3: control center
PHASE = {"water": ((116, 82, 245), "water: connect"), "wood": ((0, 134, 60), "wood: sound, media"), "fire": ((187, 63, 39), "fire: light"),
         "earth": ((197, 138, 0), "earth: power"), "metal": ((120, 120, 140), "metal: tools, capture")}


def cc_boards(out_a, out_b, work="/tmp/cc"):
    import cc as CCm
    import score as SC
    os.makedirs(work, exist_ok=True)
    CCm.main(["render", work])
    sc = {}
    for m in ("light", "dark"):
        for v in ("current", "proposed"):
            sc[(v, m)] = B.scored(os.path.join(work, f"cc-{v}-{m}.png"), "screen", os.path.join(work, f"cc-{v}.json"))
    G = "/home/ubuntu/wolos/wt/webapp-int/crates/shell/tests/golden/controlcenter-all-light.png"
    W, H = 2120, 1560
    im = Image.new("RGB", (W, 150 + 720 * 2 + 40), B.BG)
    d = ImageDraw.Draw(im)
    d.text((16, 8), "Control Center: shell golden, current layout redrawn, proposed (panel 336 x 600, content = one ruler 576)", font=B.font(20, True), fill=B.INK)
    x = 16
    gold = Image.open(G).convert("RGB")
    d.text((x, 42), "as shipped (golden, 368 x 706)", font=B.font(13, True), fill=B.DIM)
    im.paste(gold, (x, 60))
    for k, (v, m) in enumerate((("current", "light"), ("proposed", "light"), ("current", "dark"), ("proposed", "dark"))):
        p = Image.open(os.path.join(work, f"cc-{v}-{m}.png"))
        xx = 16 + 380 + k * 420
        d.text((xx, 42), f"{m} {v}   score {sc[(v, m)]['total']:.1f}", font=B.font(13, True), fill=B.INK if v == "current" else B.GOOD)
        im.paste(p, (xx, 60))
    y = 60 + 720 + 10
    d.text((16, y), "score.py (kind screen, with the layout tree)", font=B.font(15, True), fill=B.INK)
    cols = [("light", "current"), ("light", "proposed"), ("dark", "current"), ("dark", "proposed")]
    for j, (m, v) in enumerate(cols):
        d.text((200 + j * 130, y + 26), f"{m[:1].upper()} {v}", font=B.font(13, True), fill=B.DIM)
    for i, r in enumerate(SC.RULES + ("total",)):
        yy = y + 48 + i * 20
        d.text((16, yy), r, font=B.font(13), fill=B.DIM)
        for j, (m, v) in enumerate(cols):
            val = sc[(v, m)][r]["score"] if r != "total" else sc[(v, m)]["total"]
            other = sc[("current", m)][r]["score"] if r != "total" else sc[("current", m)]["total"]
            col = B.INK if v == "current" else (B.GOOD if val > other else B.BAD if val < other else B.INK)
            d.text((200 + j * 130, yy), f"{val:5.1f}", font=B.font(13, r == "total"), fill=col)
    rows = [("panel", "320 x 658", "336 x 600 (84 x 150 fen; bands guan, cai)"), ("padding / border", "12 + 1 px border (content 294)", "12; hairline as inset shadow (content 312 = 78 fen)"),
            ("top cards", "143 x 92", "152 x 84 (zucai)"), ("modules", "294 x 72", "312 x 64 (16 fen)"), ("tile", "68 x 92, content centred", "72 x 84 (18 x 21 fen), circle 12 from the top"),
            ("gaps", "8 / 8", "8 / 8 (2 fen)"), ("panel radius / card radius", "16 / 10", "24 / 12 (concentric: 12 + 12)"), ("content height", "632", "576 = one ruler")]
    for i, (k, a, b) in enumerate(rows):
        yy = y + 26 + i * 22
        d.text((760, yy), k, font=B.font(13, True), fill=B.DIM)
        d.text((960, yy), a, font=B.font(13), fill=B.INK)
        d.text((1250, yy), b, font=B.font(13, True), fill=B.GOOD)
    im.crop((0, 0, W, y + 48 + 9 * 20 + 14)).save(out_a)
    # spec figure: the proposed panel at 2x with the nine zones, the phases and the fen
    S2 = 2
    big, _, _ = CCm.render(CCm.NEW, "light", scale=S2)
    FW = 1600
    im2 = Image.new("RGB", (FW, big.height + 60), B.BG)
    d2 = ImageDraw.Draw(im2)
    d2.text((16, 8), "Control Center, proposed: nine zones, five phases (water > wood > fire > earth > metal > water), the module", font=B.font(20, True), fill=B.INK)
    ox, oy = 60, 50
    im2.paste(big, (ox, oy))
    mx = (400 - 336) // 2
    X0, Y0 = ox + mx * S2, oy + 24 * S2
    PW, PH = 336 * S2, 600 * S2
    for i in (1, 2):
        d2.line([X0 + PW * i // 3, Y0, X0 + PW * i // 3, Y0 + PH], fill=(197, 138, 0), width=1)
        d2.line([X0, Y0 + PH * i // 3, X0 + PW, Y0 + PH * i // 3], fill=(197, 138, 0), width=1)
    bars = [("water", 12, 96), ("wood", 104, 240), ("fire", 248, 312), ("fire", 320, 362), ("earth", 362, 404), ("metal", 412, 496), ("metal", 504, 588)]
    for name, a, c2 in bars:
        col = PHASE[name][0]
        d2.rectangle([X0 - 14, Y0 + a * S2, X0 - 8, Y0 + c2 * S2], fill=col)
    for name, a, c2 in (("water", 12, 96), ("wood", 104, 240), ("fire", 248, 404), ("metal", 412, 588)):
        pass
    for name, ya in (("water", 54), ("wood", 172), ("fire", 280), ("earth", 383), ("metal", 450)):
        d2.text((6, Y0 + ya * S2 - 6), name, font=B.font(12, True), fill=PHASE[name][0])
    # tile underlines by phase: row 1 fire fire earth earth; row 2 metal; row 3 metal, water
    under = [["fire", "fire", "earth", "earth"], ["metal"] * 4, ["metal", "water"]]
    for r_, row in enumerate(under):
        for c_, ph in enumerate(row):
            tx0 = 12 + c_ * 80
            ty0 = 320 + r_ * 92 + 84 - 3
            d2.rectangle([X0 + (tx0 + 10) * S2, Y0 + ty0 * S2, X0 + (tx0 + 62) * S2, Y0 + (ty0 + 2) * S2], fill=PHASE[ph][0])
    # phase notes right of the panel
    tx = ox + 400 * S2 + 30
    notes = [("water", "Wi-Fi, Bluetooth | Focus, Dark Mode  (entry: upper left)"), ("wood", "Sound, Now Playing  (quiet centre)"), ("fire", "Display, Night Shift, Keyboard Brightness"),
             ("earth", "Battery, Stay Awake"), ("metal", "Screenshot, Record, Zoom, Contrast, Reduce Motion"), ("water", "Screen Mirroring  (metal feeds water: the loop closes)")]
    y3 = 60
    d2.text((tx, y3), "Reading order = the generating cycle", font=B.font(16, True), fill=B.INK)
    for k, (ph, t) in enumerate(notes):
        d2.rectangle([tx, y3 + 34 + k * 26, tx + 8, y3 + 48 + k * 26], fill=PHASE[ph][0])
        d2.text((tx + 18, y3 + 34 + k * 26), f"{ph}: {t}", font=B.font(13), fill=B.INK)
    y3 += 34 + len(notes) * 26 + 30
    d2.text((tx, y3), "Named lengths (px = fen x 4)", font=B.font(16, True), fill=B.INK)
    spec = ["panel 336 x 600 = 84 x 150 fen; 336 and 600 sit in the good bands (guan, cai)", "padding 12 (3 fen), gap 8 (2 fen), content 312 x 576: 576 is one door-light ruler",
            "top cards 152 x 84, 84 = zucai (21 fen); modules 312 x 64 (16 fen); Now Playing art 40 (cai width)", "tiles 72 x 84: 72 = 18 fen = one band, 84 = zucai; icon circle 28, 12 from the top, label 2 x 16",
            "radii: panel 24 (6 fen) = card 12 (3 fen) + padding 12, so the corners are concentric", "light: shadows (1,2,4) cards, (3,6,24) panel, in the ink of the surface; knobs (1,2,3)",
            "lit rim 1 px on the upper-left edge only; on-circles and bars carry a 1:2 gradient, lighter at the upper left", "nine zones (thirds): entry upper left, quiet centre, weight low (the tiles): the mountain"]
    for k, t in enumerate(spec):
        d2.text((tx, y3 + 30 + k * 22), t, font=B.font(12), fill=B.INK)
    im2.save(out_b)
    return sc


if __name__ == "__main__":
    {"grammar": grammar, "symbolic": symbolic, "primitives": primitives, "dock": dock, "cc": cc_boards}[sys.argv[1]](*sys.argv[2:])
