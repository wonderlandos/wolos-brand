# SPDX-License-Identifier: GPL-2.0-or-later
"""UI primitives specimen: the kit's controls as they are (kit.css) and as the calculus sets them.

  python3 -I design/tools/ui/primitives.py [OUTDIR]       (default design/ui/primitives)

Writes current-light/dark.svg, proposed-light/dark.svg and the layout trees (current|proposed.json,
tools/brand/score.py --tree).  One drawing function takes a parameter set, so the two specimens carry the
same content and differ only in the numbers.  Sources of CUR: crates/shell/src/kit/kit.css (px).
Proposal rules: lengths named or whole fen, radii 8/12/16/24, shadows (1,2)/(2,4)/(3,6) in the ink of
the surface, never straight down and never black, density 21:15:6 by planes.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
import calculus as K  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))

CUR = dict(name="current", btn_h=24, btn_r=6, btn_px=12, sw_w=30, sw_h=18, sw_pad=2, slider_t=4, slider_k=16, circ=28, entry_h=24,
           entry_r=6, seg_h=20, seg_r=4, seg_pad=8, row_h=40, tile_h=76, card_r=10, panel_r=16, inset=12, gap=8, sect=12, bar=28,
           shadow=("0 1px 2px", 0, 1, 2, 0.08), panel_shadow=(0, 6, 18, 0.24), fat=24)
NEW = dict(name="proposed", btn_h=24, btn_r=8, btn_px=12, sw_w=40, sw_h=24, sw_pad=2, slider_t=4, slider_k=16, circ=28, entry_h=24,
           entry_r=8, seg_h=24, seg_r=6, seg_pad=8, row_h=40, tile_h=84, card_r=12, panel_r=16, inset=12, gap=8, sect=12, bar=28,
           shadow=("1px 2px 4px", 1, 2, 4, 0.12), panel_shadow=(3, 6, 24, 0.22), fat=24)

LIGHT_CUR = dict(bg="#F3F1F8", surface="#FFFFFF", s2="#E9E7F0", text="#181521", dim="#686575", accent="#7C5CFF", accent_fg="#FFFFFF", line="#DAD8E2",
                 red="#CF3A68", ink="#181521", off="#CFCDD6", glass="#F8F7FB")
DARK_CUR = dict(bg="#191720", surface="#2A2832", s2="#393643", text="#F6F5FB", dim="#AAA7B6", accent="#8B6CFF", accent_fg="#FFFFFF", line="#3E3B48",
                red="#F2678F", ink="#08060E", off="#4A4753", glass="#232029")
LIGHT_NEW = dict(bg="#F1F1FA", surface="#FFFFFF", s2="#EBEBF3", text="#151520", dim="#565563", accent="#7452F5", accent_fg="#FFFFFF", line="#DEDEE6",
                 red="#BB3F27", ink="#151520", off="#CDCDD9", glass="#F8F8FC")
DARK_NEW = dict(bg="#15151D", surface="#292932", s2="#383741", text="#F8F8FC", dim="#B4B4BB", accent="#7452F5", accent_fg="#FFFFFF", line="#3A3944",
                red="#EE7E66", ink="#020206", off="#4A4954", glass="#22222B")


def rr(x, y, w, h, r, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{min(r, w / 2, h / 2)}" fill="{fill}" {extra}/>'


def render(P, C, mode):
    """returns (svg, tree). Frame 576 x 432 (3:4 of one ruler) (one door-light ruler wide)."""
    W, H = 576, 432
    nodes, out, defs = [], [], []

    def node(id_, x, y, w, h, role="box", fill=None, parent=None, radius=None, group=None):
        n = {"id": id_, "rect": [x, y, w, h], "role": role}
        for k, v in (("fill", fill), ("parent", parent), ("radius", radius), ("group", group)):
            if v is not None:
                n[k] = v
        nodes.append(n)

    def shadow(x, y, w, h, r, elev):
        """a coloured shadow, light upper left: (dx, dy) = elevation x (1, 2)"""
        dx, dy, blur, op = elev
        i = f"s{len(defs)}"
        defs.append(f'<filter id="{i}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{blur / 2}"/></filter>')
        out.append(f'<rect x="{x + dx}" y="{y + dy}" width="{w}" height="{h}" rx="{min(r, w / 2, h / 2)}" fill="{C["ink"]}" opacity="{op}" filter="url(#{i})"/>')

    el = P["shadow"]
    elev = (el[1], el[2], el[3], el[4])
    pel = P["panel_shadow"]
    pad = P["inset"]
    out.append(rr(0, 0, W, H, 0, C["bg"]))
    node("frame", 0, 0, W, H, "box", C["bg"])
    # panel (glass), 576 - 2 x 24
    px, py, pw, ph = 24, 24, W - 48, H - 48
    shadow(px, py, pw, ph, P["panel_r"], (pel[0], pel[1], pel[2], pel[3] * 0.6))
    out.append(rr(px, py, pw, ph, P["panel_r"], C["glass"], f'stroke="{C["line"]}" stroke-width="1"'))
    node("panel", px, py, pw, ph, "opening", C["glass"], "frame", P["panel_r"])
    x0 = px + P["inset"] * 2
    y = py + P["inset"] * 2
    inner_w = pw - P["inset"] * 4
    # row 1: buttons
    bx = x0
    for i, (label, fill, fg) in enumerate((("Cancel", C["s2"], C["text"]), ("Save", C["accent"], C["accent_fg"]), ("Erase", C["red"], C["accent_fg"]))):
        w = 72 if P["name"] == "proposed" else 68
        out.append(rr(bx, y, w, P["btn_h"], P["btn_r"], fill))
        out.append(f'<text x="{bx + w / 2}" y="{y + P["btn_h"] / 2 + 4.5}" font-family="Inter" font-size="13" font-weight="500" text-anchor="middle" fill="{fg}">{label}</text>')
        node(f"btn{i}", bx, y, w, P["btn_h"], "control", fill, "panel", P["btn_r"], "row1")
        bx += w + P["gap"] + (4 if P["name"] == "proposed" else 0)
    # icon button
    out.append(rr(bx, y, P["btn_h"], P["btn_h"], P["btn_r"], C["s2"]))
    node("iconbtn", bx, y, P["btn_h"], P["btn_h"], "control", C["s2"], "panel", P["btn_r"], "row1")
    # row 2: switch off, on, slider, circle controls
    y2 = y + P["btn_h"] + P["sect"] * 2
    sx = x0
    for on in (False, True):
        fill = C["accent"] if on else C["off"]
        out.append(rr(sx, y2, P["sw_w"], P["sw_h"], 999, fill))
        kn = P["sw_h"] - 2 * P["sw_pad"]
        kx = sx + (P["sw_w"] - P["sw_pad"] - kn if on else P["sw_pad"])
        shadow(kx, y2 + P["sw_pad"], kn, kn, kn, (elev[0] * 0.5, elev[1] * 0.5, 2, 0.3))
        out.append(f'<circle cx="{kx + kn / 2}" cy="{y2 + P["sw_h"] / 2}" r="{kn / 2}" fill="#FFFFFF"/>')
        node(f"sw{int(on)}", sx, y2, P["sw_w"], P["sw_h"], "control", fill, "panel", P["sw_h"] // 2, "row2")
        sx += P["sw_w"] + P["gap"] * 2
    # slider
    sl_w = 148
    ty = y2 + P["sw_h"] / 2 - P["slider_t"] / 2
    out.append(rr(sx, ty, sl_w, P["slider_t"], P["slider_t"] / 2, C["off"]))
    out.append(rr(sx, ty, sl_w * 0.6, P["slider_t"], P["slider_t"] / 2, C["accent"]))
    kx = sx + sl_w * 0.6 - P["slider_k"] / 2
    shadow(kx, y2 + P["sw_h"] / 2 - P["slider_k"] / 2, P["slider_k"], P["slider_k"], 99, (elev[0], elev[1], 3, 0.3))
    out.append(f'<circle cx="{kx + P["slider_k"] / 2}" cy="{y2 + P["sw_h"] / 2}" r="{P["slider_k"] / 2}" fill="#FFFFFF"/>')
    node("slider", sx, y2 + P["sw_h"] / 2 - P["slider_k"] / 2, sl_w, P["slider_k"], "control", C["accent"], "panel", P["slider_k"] // 2, "row2")
    sx += sl_w + P["gap"] * 2
    # circle controls (CC): off, on
    for on in (False, True):
        c = P["circ"]
        out.append(f'<circle cx="{sx + c / 2}" cy="{y2 + P["sw_h"] / 2}" r="{c / 2}" fill="{C["accent"] if on else C["off"]}"/>')
        node(f"circ{int(on)}", sx, y2 + P["sw_h"] / 2 - c / 2, c, c, "control", C["accent"] if on else C["off"], "panel", c // 2, "row2")
        sx += c + P["gap"]
    # row 3: entry, segmented
    y3 = y2 + max(P["sw_h"], P["circ"]) + P["sect"] * 2
    ew = 216
    out.append(rr(x0, y3, ew, P["entry_h"], P["entry_r"], C["s2"], f'stroke="{C["line"]}" stroke-width="1"'))
    out.append(f'<text x="{x0 + 8}" y="{y3 + P["entry_h"] / 2 + 4.5}" font-family="Inter" font-size="13" fill="{C["dim"]}">Search</text>')
    node("entry", x0, y3, ew, P["entry_h"], "control", C["s2"], "panel", P["entry_r"], "row3")
    segx = x0 + ew + P["gap"] * 3
    seg_w = 3 * (56 if P["name"] == "proposed" else 52)
    out.append(rr(segx, y3, seg_w + 4, P["seg_h"] + 4, P["seg_r"] + 2, C["s2"]))
    sw_ = seg_w / 3
    out.append(rr(segx + 2, y3 + 2, sw_, P["seg_h"], P["seg_r"], C["surface"]))
    for i, lab in enumerate(("Day", "Week", "Year")):
        out.append(f'<text x="{segx + 2 + sw_ * (i + .5)}" y="{y3 + 2 + P["seg_h"] / 2 + 4.5}" font-family="Inter" font-size="13" text-anchor="middle" fill="{C["text"]}">{lab}</text>')
    node("segmented", segx, y3, seg_w + 4, P["seg_h"] + 4, "control", C["s2"], "panel", P["seg_r"] + 2, "row3")
    # row 4: list rows in a card
    y4 = y3 + max(P["entry_h"], P["seg_h"] + 4) + P["sect"] * 2
    cw = inner_w
    rows = 2
    ch = P["row_h"] * rows
    shadow(x0, y4, cw, ch, P["card_r"], elev)
    out.append(rr(x0, y4, cw, ch, P["card_r"], C["surface"]))
    node("card", x0, y4, cw, ch, "box", C["surface"], "panel", P["card_r"])
    for i, lab in enumerate(("Wi-Fi", "Bluetooth")):
        ry = y4 + i * P["row_h"]
        out.append(f'<text x="{x0 + P["inset"] + 28}" y="{ry + P["row_h"] / 2 + 4.5}" font-family="Inter" font-size="13" fill="{C["text"]}">{lab}</text>')
        out.append(rr(x0 + P["inset"], ry + P["row_h"] / 2 - 8, 16, 16, 4, C["accent"] if i == 0 else C["dim"]))
        if i == 0:
            out.append(f'<line x1="{x0}" y1="{ry + P["row_h"]}" x2="{x0 + cw}" y2="{ry + P["row_h"]}" stroke="{C["line"]}"/>'.replace(f'x1="{x0}"', f'x1="{x0 + P["inset"]}"').replace(f'x2="{x0 + cw}"', f'x2="{x0 + cw - P["inset"]}"'))
        node(f"row{i}", x0, ry, cw, P["row_h"], "text", None, "card", None, "rows")
    # row 5: tiles
    y5 = y4 + ch + P["sect"] * 2
    tw = (inner_w - 3 * P["gap"]) / 4
    tw = int(tw) if P["name"] == "current" else 108
    for i in range(4):
        tx = x0 + i * (tw + (P["gap"] if P["name"] == "current" else 12))
        shadow(tx, y5, tw, P["tile_h"], P["card_r"], elev)
        out.append(rr(tx, y5, tw, P["tile_h"], P["card_r"], C["surface"]))
        c = 28 if P["name"] == "current" else 24
        on = i == 0
        out.append(f'<circle cx="{tx + tw / 2}" cy="{y5 + 8 + c / 2}" r="{c / 2}" fill="{C["accent"] if on else C["off"]}"/>')
        out.append(f'<text x="{tx + tw / 2}" y="{y5 + P["tile_h"] - 10}" font-family="Inter" font-size="11" text-anchor="middle" fill="{C["dim"]}">Tile</text>')
        node(f"tile{i}", tx, y5, tw, P["tile_h"], "box", C["surface"], "panel", P["card_r"], "tiles")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{"".join(defs)}</defs>{"".join(out)}</svg>')
    return svg, {"frame": [W, H], "nodes": nodes}


def main(argv):
    outdir = argv[0] if argv else os.path.join(D, "ui", "primitives")
    os.makedirs(outdir, exist_ok=True)
    for P, Cl, Cd in ((CUR, LIGHT_CUR, DARK_CUR), (NEW, LIGHT_NEW, DARK_NEW)):
        for mode, Cc in (("light", Cl), ("dark", Cd)):
            svg, tree = render(P, Cc, mode)
            open(os.path.join(outdir, f"{P['name']}-{mode}.svg"), "w").write(svg)
            if mode == "light":
                json.dump(tree, open(os.path.join(outdir, f"{P['name']}.json"), "w"), indent=1)
    print("primitives.py ->", outdir)


if __name__ == "__main__":
    main(sys.argv[1:])
