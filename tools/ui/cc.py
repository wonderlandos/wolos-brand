# SPDX-License-Identifier: GPL-2.0-or-later
"""The Control Center: the shell's layout (measured from crates/shell tests/golden/controlcenter-all-*.png
and kit.css) and the layout on the module.

  python3 -I design/tools/ui/cc.py render OUT_DIR       panels (light, dark), trees, per version

Both versions are drawn by one function from a parameter set, with the same content and state, so the board
differs only in the numbers, the order and the light.  Current = the golden (368 x 706 with 24 px glass margins):
panel 320 wide, 1 px border + 12 padding (content 294), gaps 8, top cards 143 x 92, modules 294 x 72, tiles 68 x 92.
"""
import io
import json
import os
import re
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
import dock as DK  # noqa: E402  (wallpaper crop, rounded masks)

D = os.path.normpath(os.path.join(HERE, "..", ".."))
CURSYM = os.path.join(D, "icons", "symbolic")
NEWSYM = os.path.join(D, "ui", "symbolic", "16")

# the golden's contents, in the shell's order (current) and the five-phase order (proposed)
TILES_CUR = [("battery-good", "82%"), ("video-display", "Screen\nMirroring"), ("keyboard-brightness", "Keyboard\nBrightness"), ("night-light", "Night Shift"),
             ("camera-photo", "Screenshot"), ("media-record", "Record"), ("wolos-reduce-motion", "Reduce\nMotion"), ("wolos-contrast", "Increase\nContrast"),
             ("zoom-in", "Zoom"), ("computer", "Stay Awake")]
# water -> wood -> fire -> earth -> metal -> water (sheng): fire tiles, earth tiles, metal tiles, the loop closes on water
TILES_NEW = [("night-light", "Night Shift"), ("keyboard-brightness", "Keyboard\nBrightness"), ("battery-good", "82%"), ("computer", "Stay Awake"),
             ("camera-photo", "Screenshot"), ("media-record", "Record"), ("zoom-in", "Zoom"), ("wolos-contrast", "Increase\nContrast"),
             ("wolos-reduce-motion", "Reduce\nMotion"), ("video-display", "Screen\nMirroring")]

CUR = dict(name="current", W=320, pad=12, border=1, r_panel=16, r_card=10, gap=8, gap_v=8, top_h=92, mod_h=72, np_h=72, tile_w=[68, 68, 67, 67], tile_h=92,
           circle=28, order=("display", "sound", "np"), tiles=TILES_CUR, tile_layout="centred", fat=24, shadow=(0, 1, 2, 0.08), panel_shadow=[(0, 6, 18, 0.24), (0, 1, 4, 0.16)],
           rim="top", icons=CURSYM, lit=False, art=40)
NEW = dict(name="proposed", W=336, pad=12, border=0, r_panel=24, r_card=12, gap=8, gap_v=8, top_h=84, mod_h=64, np_h=64, tile_w=[72, 72, 72, 72], tile_h=84,
           circle=28, order=("sound", "np", "display"), tiles=TILES_NEW, tile_layout="top", fat=24, shadow=(1, 2, 4, 0.12), panel_shadow=[(3, 6, 24, 0.22), (1, 2, 4, 0.16)],
           rim="lit", icons=NEWSYM, lit=True, art=40)
COL = {"light": dict(glass=(255, 255, 255, 150), card="#FFFFFF", control="#EEEDF5", off="#CFCDD6", text="#181521", dim="#686575", accent="#7C5CFF", accent_fg="#FFFFFF", ink=(24, 21, 33), line="#E3E1EA"),
       "dark": dict(glass=(41, 41, 50, 150), card="#33323C", control="#413F4B", off="#4A4753", text="#F6F5FB", dim="#AAA7B6", accent="#8B6CFF", accent_fg="#FFFFFF", ink=(2, 2, 6), line="#403E4A")}
COL_NEW = {"light": dict(COL["light"], accent="#7452F5", text="#151520", dim="#565563", control="#EBEBF3", ink=(21, 21, 32)),
           "dark": dict(COL["dark"], accent="#7452F5", text="#F8F8FC", dim="#B4B4BB", control="#403F4A", ink=(2, 2, 6))}


def icon(name, base, x, y, size, color):
    p = os.path.join(base, f"{name}-symbolic.svg")
    if not os.path.exists(p):
        p = os.path.join(CURSYM, f"{name}-symbolic.svg")
    s = open(p, encoding="utf-8").read()
    inner = s[s.index("<g"):s.rindex("</svg>")].replace("currentColor", color)
    return f'<g transform="translate({x} {y}) scale({size / 16})">{inner}</g>'


def build(P, mode):
    C = (COL_NEW if P["name"] == "proposed" else COL)[mode]
    W = P["W"]
    pad = P["pad"] + P["border"]
    cw = W - 2 * pad
    nodes, out, defs = [], [], []
    new = P["name"] == "proposed"

    def shadow(x, y, w, h, r, e, ink=None):
        dx, dy, blur, op = e
        if op <= 0:
            return
        i = f"f{len(defs)}"
        defs.append(f'<filter id="{i}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="{blur / 2}"/></filter>')
        col = "#%02X%02X%02X" % (C["ink"] if new else (0, 0, 0))
        out.append(f'<rect x="{x + dx}" y="{y + dy}" width="{w}" height="{h}" rx="{r}" fill="{col}" opacity="{op}" filter="url(#{i})"/>')

    def card(id_, x, y, w, h, group=None):
        shadow(x, y, w, h, P["r_card"], P["shadow"])
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{P["r_card"]}" fill="{C["card"]}"/>')
        nodes.append({"id": id_, "rect": [x, y, w, h], "role": "box", "fill": C["card"], "parent": "panel", "radius": P["r_card"], **({"group": group} if group else {})})

    def circle(x, y, d, on, ic, iname):
        fill = C["accent"] if on else C["off"]
        if on and P["lit"]:
            i = f"g{len(defs)}"
            defs.append(f'<linearGradient id="{i}" x1="0.25" y1="0" x2="0.75" y2="1"><stop offset="0" stop-color="#9A83FF"/><stop offset="1" stop-color="{C["accent"]}"/></linearGradient>')
            fill = f"url(#{i})"
        out.append(f'<circle cx="{x + d / 2}" cy="{y + d / 2}" r="{d / 2}" fill="{fill}"/>')
        out.append(icon(iname, P["icons"], x + d / 2 - 8, y + d / 2 - 8, 16, C["accent_fg"] if on else C["text"]))

    def text(x, y, s, size=13, weight=400, fill=None, anchor="start"):
        out.append(f'<text x="{x}" y="{y}" font-family="Inter" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill or C["text"]}">{s}</text>')

    y = pad
    x0 = pad
    # --- top row: connectivity | modes
    cwid = (cw - P["gap"]) // 2 + (1 if (cw - P["gap"]) % 2 else 0) if not new else (cw - P["gap"]) // 2
    cwid = 143 if not new else cwid
    for k, (id_, rows) in enumerate((("connectivity", (("network-wireless", "Wi-Fi", "Wonderland", True), ("bluetooth-active", "Bluetooth", "On", True))),
                                      ("modes", (("night-light", "Focus", "Off", False), ("wolos-dark-mode", "Dark Mode", "Off", False))))):
        x = x0 + k * (cwid + P["gap"])
        card(id_, x, y, cwid, P["top_h"], "top")
        pitch = P["top_h"] - 2 * P["pad"] - P["circle"]
        for r, (ic, t, sub, on) in enumerate(rows):
            cy = y + P["pad"] + r * pitch
            circle(x + P["pad"], cy, P["circle"], on, ic, ic)
            text(x + P["pad"] + P["circle"] + 8, cy + 12, t, 13, 600)
            text(x + P["pad"] + P["circle"] + 8, cy + 25, sub, 11, 400, C["dim"])
            nodes.append({"id": f"{id_}{r}", "rect": [x + P["pad"], cy, P["circle"], P["circle"]], "role": "control", "parent": id_, "radius": P["circle"] // 2})
    y += P["top_h"] + P["gap_v"]
    # --- modules
    for m in P["order"]:
        if m == "np":
            h = P["np_h"]
            card("np", x0, y, cw, h, "mods")
            art = P["art"]
            ay = y + (h - art) // 2
            art_c = "#E8672E"
            out.append(f'<rect x="{x0 + P["pad"]}" y="{ay}" width="{art}" height="{art}" rx="8" fill="{art_c}"/><circle cx="{x0 + P["pad"] + art / 2}" cy="{ay + art / 2}" r="{art * 0.33}" fill="#2A1A14"/><circle cx="{x0 + P["pad"] + art / 2}" cy="{ay + art / 2}" r="3" fill="#F6E3C4"/>')
            tx = x0 + P["pad"] + art + 12
            text(tx, y + h / 2 - 2, "White Rabbit", 13, 600)
            text(tx, y + h / 2 + 13, "Jefferson Airplane", 11, 400, C["dim"])
            for k, n in enumerate(("media-skip-backward", "media-playback-pause", "media-skip-forward")):
                out.append(icon(n, P["icons"], x0 + cw - P["pad"] - 16 - (2 - k) * 28, y + h / 2 - 8, 16, C["text"]))
            nodes.append({"id": "np-art", "rect": [x0 + P["pad"], ay, art, art], "role": "box", "parent": "np", "radius": 8})
        else:
            h = P["mod_h"]
            card(m, x0, y, cw, h, "mods")
            title, val, iname = ("Display", 72, "display-brightness") if m == "display" else ("Sound", 64, "audio-volume-medium")
            text(x0 + P["pad"], y + P["pad"] + 12, title, 13, 600)
            text(x0 + cw - P["pad"] - 20 - 4, y + P["pad"] + 12, f"{val}%", 11, 400, C["dim"], "end")
            fat = P["fat"]
            sy = y + h - P["pad"] - fat
            sw = cw - 2 * P["pad"] - 20
            out.append(f'<rect x="{x0 + P["pad"]}" y="{sy}" width="{sw}" height="{fat}" rx="{fat // 2}" fill="{C["off"]}"/>')
            fillw = sw * val / 100
            if P["lit"]:
                i = f"s{len(defs)}"
                defs.append(f'<linearGradient id="{i}" x1="0.25" y1="0" x2="0.75" y2="1"><stop offset="0" stop-color="#8C74FF"/><stop offset="1" stop-color="{C["accent"]}"/></linearGradient>')
                fillc = f"url(#{i})"
            else:
                fillc = C["accent"]
            out.append(f'<rect x="{x0 + P["pad"]}" y="{sy}" width="{fillw}" height="{fat}" rx="{fat // 2}" fill="{fillc}"/>')
            out.append(icon(iname, P["icons"], x0 + P["pad"] + 4, sy + 4, 16, C["accent_fg"]))
            kx = x0 + P["pad"] + fillw - fat
            shadow(kx, sy, fat, fat, fat // 2, (P["shadow"][0], P["shadow"][1], 3, 0.30))
            out.append(f'<circle cx="{kx + fat / 2}" cy="{sy + fat / 2}" r="{fat / 2}" fill="#FFFFFF"/>')
            out.append(icon("go-next", P["icons"], x0 + cw - P["pad"] - 14, sy + 4, 16, C["dim"]))
            nodes.append({"id": m + "-bar", "rect": [x0 + P["pad"], sy, sw, fat], "role": "control", "parent": m, "radius": fat // 2})
        y += h + P["gap_v"]
    # --- tiles: 4 columns
    tw = P["tile_w"]
    for i, (iname, label) in enumerate(P["tiles"]):
        r, c = divmod(i, 4)
        tx = x0 + sum(tw[:c]) + c * P["gap"]
        ty = y + r * (P["tile_h"] + P["gap_v"])
        w, h = tw[c], P["tile_h"]
        card(f"tile{i}", tx, ty, w, h, f"tiles{r}")
        lines = label.split("\n")
        if P["tile_layout"] == "top":
            cy = ty + P["pad"]
            ly = ty + P["pad"] + P["circle"] + 12 + 11
        else:
            gh = P["circle"] + 8 + 16 * max(len(lines), 1)
            cy = ty + (h - gh) // 2
            ly = cy + P["circle"] + 8 + 11
        on = i == (2 if new else 0) and False
        circle(tx + (w - P["circle"]) / 2, cy, P["circle"], on, iname, iname)
        for k, ln in enumerate(lines):
            text(tx + w / 2, ly + 16 * k, ln, 11, 400, C["text"], "middle")
        nodes.append({"id": f"tile{i}c", "rect": [tx + (w - P["circle"]) / 2, cy, P["circle"], P["circle"]], "role": "control", "parent": f"tile{i}", "radius": P["circle"] // 2})
    rows_t = (len(P["tiles"]) + 3) // 4
    y += rows_t * (P["tile_h"] + P["gap_v"]) - P["gap_v"]
    H = y + pad
    return H, "".join(defs), "".join(out), nodes, C


FRAME = (400, 720)       # the same desktop crop for both versions, so the ground is the same


def render(P, mode, margin=24, scale=1):
    H, defs, body, nodes, C = build(P, mode)
    W = P["W"]
    FW, FH = FRAME
    mx = (FW - W) // 2
    base = DK.wall(mode, FW, FH).convert("RGBA")
    box = (mx, margin, mx + W, margin + H)
    mask = DK.rr_mask((FW, FH), box, P["r_panel"])
    new = P["name"] == "proposed"
    ink = C["ink"] if new else (0, 0, 0)
    canvas = base
    for dx, dy, blur, op in P["panel_shadow"]:
        if mode == "dark" and new:
            op *= 2
        layer = Image.new("RGBA", (FW, FH), ink + (0,))
        layer.putalpha(ImageChops.offset(mask, dx, dy).filter(ImageFilter.GaussianBlur(blur / 2)).point(lambda v, op=op: int(v * op)))
        canvas = Image.alpha_composite(canvas, layer)
    blurred = canvas.filter(ImageFilter.GaussianBlur(14))
    canvas.paste(blurred, (0, 0), mask)
    glass = Image.new("RGBA", (FW, FH), COL[mode]["glass"])
    glass.putalpha(ImageChops.multiply(glass.getchannel("A"), mask))
    canvas = Image.alpha_composite(canvas, glass)
    inner = DK.rr_mask((FW, FH), (box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1), max(P["r_panel"] - 1, 0))
    ring = ImageChops.subtract(mask, inner)
    hl = Image.new("RGBA", (FW, FH), (255, 255, 255, 0))
    hl.putalpha(ring.point(lambda v: int(v * 0.22)))
    canvas = Image.alpha_composite(canvas, hl)
    if P["rim"] == "top":
        edge = ImageChops.subtract(inner, ImageChops.offset(inner, 0, 1))
        ra = edge.point(lambda v: int(v * 0.5))
    else:
        import numpy as np
        edge = ImageChops.subtract(inner, ImageChops.offset(inner, 1, 1))
        ys, xs = np.mgrid[0:FH, 0:FW]
        t = np.clip(1 - (((xs - mx) + (ys - margin) * 0.5) / (W * 0.55)), 0, 1)
        ra = Image.fromarray((np.asarray(edge).astype(float) * 0.7 * t).astype(np.uint8))
    rim = Image.new("RGBA", (FW, FH), (255, 255, 255, 0))
    rim.putalpha(ra)
    canvas = Image.alpha_composite(canvas, rim)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{defs}</defs>{body}</svg>'
    ov = subprocess.run(["rsvg-convert", "-w", str(W * scale), "-h", str(H * scale), "-"], input=svg.encode(), capture_output=True, check=True).stdout
    ovi = Image.open(io.BytesIO(ov)).convert("RGBA")
    if scale > 1:
        canvas = canvas.resize((FW * scale, FH * scale), Image.BICUBIC)
    canvas.alpha_composite(ovi, (mx * scale, margin * scale))
    tree = {"frame": [FW, FH], "nodes": [{"id": "frame", "rect": [0, 0, FW, FH], "role": "box"},
                                          {"id": "panel", "rect": [mx, margin, W, H], "role": "opening", "parent": "frame", "radius": P["r_panel"]}] +
            [dict(n, rect=[n["rect"][0] + mx, n["rect"][1] + margin] + n["rect"][2:]) for n in nodes]}
    return canvas.convert("RGB"), tree, (W, H)


def main(argv):
    out = argv[1]
    os.makedirs(out, exist_ok=True)
    for P in (CUR, NEW):
        for mode in ("light", "dark"):
            im, tree, size = render(P, mode)
            im.save(os.path.join(out, f"cc-{P['name']}-{mode}.png"))
            if mode == "light":
                json.dump(tree, open(os.path.join(out, f"cc-{P['name']}.json"), "w"), indent=1)
                print(P["name"], "panel", size)


if __name__ == "__main__":
    main(sys.argv[1:])
