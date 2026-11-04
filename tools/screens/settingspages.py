# SPDX-License-Identifier: GPL-2.0-or-later
"""Settings shell: toolbar, sidebar and the pane frame (ui/settings/mod.rs on kit AppWindow), 900 x 600 like the goldens.
Representative pane: Sound (a card with a slider and a switch, a list card with a check). Current numbers are measured from
settings-sound-wide-*.png: toolbar 36, sidebar 228 + 1 px border, search 212 x 28 at (8, 45), rows pitch 28, group gap 12,
page padding 24, cards 41-pitch rows, r 10."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene import Scene, TOK  # noqa: E402

W, H = 900, 600
GOLD = "/home/ubuntu/wolos/wt/webapp-int/crates/shell/tests/golden"
ROWS = [
    [("Wi-Fi", "network-wireless", "water", "#CF3A68"), ("Bluetooth", "bluetooth-active", "water", "#B07A0C"), ("Network", "network-wired", "water", "#6A4DF4")],
    [("Notifications", "preferences-system-notifications", "earth", "#0C8A80"), ("Sound", "audio-volume-high", "water", "#1D64B0")],
    [("General", "emblem-system", "base", "#E9622A"), ("Appearance", "preferences-desktop-appearance", "base", "#E9622A"),
     ("Accessibility", "preferences-desktop-accessibility", "base", "#6A4DF4"), ("Control Center", "wolos-control-center", "base", "#1D64B0"),
     ("Desktop & Dock", "user-desktop", "base", "#1D64B0"), ("Displays", "preferences-desktop-display", "base", "#E9622A"),
     ("Wallpaper", "preferences-desktop-wallpaper", "base", "#E9622A"), ("Effects & Looks", "preferences-color", "earth", "#B07A0C"),
     ("Widgets", "wolos-widgets", "base", "#6A4DF4"), ("Battery", "battery-good", "wood", "#B07A0C")],
    [("Lock Screen", "system-lock-screen", "wood", "#6A4DF4"), ("Privacy & Security", "preferences-system-privacy", "wood", "#CF3A68")],
]
# brand tints, one per group (five phases, fire is not used here): water, earth, base violet, wood
TINT = {"light": {"water": "#007B9E", "earth": "#B07A0C", "base": "#6D48EB", "wood": "#00863C"},
        "dark": {"water": "#35BEEE", "earth": "#FFD189", "base": "#9181FF", "wood": "#6BC681"}}


def frame(s, v, new):
    W_, H_ = W, H
    s.panel(0, 0, W_, H_, 0, fill="surface", tree=False)
    root = s.panel(0, 0, W_, H_, 0, fill="surface", role="box")
    tb = 40 if new else 36
    sw = 240 if new else 228
    # toolbar
    s.panel(0, 0, W_, tb, 0, fill="glass", opacity=0.9, parent=root, role="box", tree=True)
    # sidebar
    sb = s.panel(0, tb, sw, H_ - tb, 0, fill="sidebar", parent=root, role="box")
    if new:    # hairlines inset: they end before the frame edge (sha: no rule into the border)
        s.line(12, tb - 1, W_ - 24, 1, "line", tree=True)
        s.line(sw, tb + 8, 1, H_ - tb - 16, "line", tree=True)
    else:
        s.line(0, tb - 1, W_, 1, "line", parent=None, tree=True)
        s.line(sw, tb, 1, H_ - tb, "line", tree=True)
    return root, sb, tb, sw


def page_sound(mode, v, tok, name="settings-shell"):
    new = v == "new"
    s = Scene(W, H, mode, tok, name, backdrop=None)
    root, sb, tb, sw = frame(s, v, new)
    t = TINT[mode]
    # search
    if new:
        sx, sy, sh_, swd, r = 12, 8, 32, sw - 24, 8
        pitch, rowh, gap, ry0 = 28, 24, 16, 8 + 32 + 12
    else:
        sx, sy, sh_, swd, r = 8, 8, 28, 212, 6
        pitch, rowh, gap, ry0 = 28, 28, 12, 8 + 28 + 11
    sf = s.panel(sx, sy, swd, sh_, r, fill="control", parent=sb, stroke="line", role="control", group="side")
    s.sym(sf, 10, (sh_ - 16) // 2, 16, "system-search", "accent_ink")
    s.text(sf, 34, 0, 120, sh_, "Search", 13, 400, "dim", tree=False)
    y = ry0
    for gi, grp in enumerate(ROWS):
        for (lab, ic, ph, oldtint) in grp:
            sel = lab == "Sound"
            tint = s.t["accent_ink"] if False else (t[ph] if new else oldtint)
            if sel:
                s.panel(sx, y, sw - 2 * sx, rowh, r, fill="accent", opacity=0.18, parent=sb, role="control", group="rows")
            else:
                s.panel(sx, y, sw - 2 * sx, rowh, r, fill="control", opacity=0.0, parent=sb, role="control", group="rows") if False else None
            s.sym(sb, sx + 8, y + (rowh - 16) // 2, 16, ic, tint)
            s.text(sb, sx + 8 + 16 + 8, y, 150, rowh, lab, 13, 500 if sel else 400, "text", group="labels")
            y += pitch
        y += gap - (pitch - rowh) if new else gap
    # pane
    if new:   # content column = min(pane - 48, 576), centred in the pane: 576 is one ruler (cai band)
        pw = min(W - sw - 1 - 48, 576)
        px = sw + 1 + (W - sw - 1 - pw) // 2
    else:
        px = sw + 1 + 24
        pw = W - px - 24
    ty = tb + (4 if new else 4)
    s.sym(root, px - 24 + 6, ty + 10, 16, "go-previous", "text") if False else None
    s.text(root, px, ty, 400, 40 if new else 34, "Sound", 27 if new else 26, 700, "text", ls=-0.5, group="title")
    cy = ty + (40 if new else 34) + (16 if new else 17)
    rh = 40
    sep = 1 if not new else 0
    rows1 = 2
    c1 = s.panel(px, cy, pw, rh * rows1 + (sep if not new else 0) * (rows1), 12 if new else 10, fill="card", parent=root, stroke="line",
                 shadow="e1" if new else None, role="opening" if False else "box", group="cards")
    s.text(c1, 12, 0, 160, rh, "Output volume", 13, 400, "text", group="r")
    tr = 4
    sx0, sx1 = pw - 12 - 240, pw - 12
    s.sym(c1, sx0 - 32, (rh - 16) // 2, 16, "audio-volume-low", "text")
    s.panel(sx0, (rh - tr) // 2, 216 if False else sx1 - sx0 - 28, tr, 2, fill="control", parent=c1)
    s.panel(sx0, (rh - tr) // 2, 110, tr, 2, fill="accent", parent=c1)
    s.panel(sx0 + 110 - 8, (rh - 16) // 2, 16, 16, 8, fill="#ffffff", parent=c1, stroke="line", shadow="e1" if new else "cur-card", role="control")
    s.sym(c1, sx1 - 16, (rh - 16) // 2, 16, "audio-volume-high", "text")
    y2 = rh + (sep if not new else 0)
    if new:
        s.line(12, rh, pw - 24, 1, "line", parent=c1)
    else:
        s.line(1, rh, pw - 2, 1, "line", parent=c1)
    s.text(c1, 12, y2, 160, rh, "Mute", 13, 400, "text", group="r")
    swd_, swh_, swp = (36, 24, 2) if new else (30, 18, 2)
    s.switch(c1, pw - 12 - swd_, y2 + (rh - swh_) // 2, swd_, swh_, on=False, pad=swp)
    hy = cy + c1_h(rh, rows1, sep, new) + (24 if new else 24)
    s.text(root, px, hy, 300, 24 if new else 22, "Output", 16 if new else 15, 600, "text", group="head")
    c2y = hy + (24 if new else 22) + (8 if new else 8)
    rows = [("Wired headset", "AAC"), ("Built-in speakers", ""), ("HDMI display", ""), ("Balance", "slider"), ("Allow louder", "Volume sliders pass 100%. Sound above 100% can distort.")]
    rhs = [48, 40, 40, 60, 52] if new else [51, 40, 40, 54, 51]
    c2 = s.panel(px, c2y, pw, sum(rhs) + (0 if new else 4), 12 if new else 10, fill="card", parent=root, stroke="line", shadow="e1" if new else None, role="box", group="cards")
    yy = 0
    for i, ((a, b), rh_) in enumerate(zip(rows, rhs)):
        if i:
            s.line(12 if new else 1, yy, pw - 24 if new else pw - 2, 1, "line", parent=c2)
            yy += 0 if new else 1
        if i < 3:
            icn = ["audio-headphones", "audio-speakers", "video-display"][i]
            s.sym(c2, 12, yy + (rh_ - 16) // 2, 16, icn, "text")
            if b:
                s.text(c2, 40, yy + 6, 300, 20, a, 13, 400, "text", group="rr")
                s.text(c2, 40, yy + 6 + 20, 300, 16, b, 11, 400, "dim", tree=False)
            else:
                s.text(c2, 40, yy, 300, rh_, a, 13, 400, "text", group="rr")
            if i == 0:
                s.sym(c2, pw - 12 - 16, yy + (rh_ - 16) // 2, 16, "emblem-ok", "accent_ink")
        elif i == 3:
            s.text(c2, 12, yy + 6, 200, 20, a, 13, 400, "text", group="rr")
            s.text(c2, 12, yy + rh_ - 22, 40, 16, "Left", 11, 400, "text", tree=False)
            s.text(c2, pw - 12 - 40, yy + rh_ - 22, 40, 16, "Right", 11, 400, "text", "end", tree=False)
            s.panel(52, yy + rh_ - 22 + 6, pw - 104, 4, 2, fill="control", parent=c2)
            s.panel(52, yy + rh_ - 22 + 6, (pw - 104) // 2, 4, 2, fill="accent", parent=c2)
            s.panel(52 + (pw - 104) // 2 - 8, yy + rh_ - 22 + 2, 16, 16, 8, fill="#ffffff", parent=c2, stroke="line", shadow="e1" if new else "cur-card", role="control")
        else:
            s.text(c2, 12, yy + 6, 300, 20, a, 13, 400, "text", group="rr")
            s.text(c2, 12, yy + 6 + 20, pw - 90, 16, b, 11, 400, "text", tree=False)
            s.switch(c2, pw - 12 - swd_, yy + (rh_ - swh_) // 2, swd_, swh_, on=False, pad=swp)
        yy += rh_
    # next heading peeks in
    iy = c2y + sum(rhs) + 4 + 24
    s.text(root, px, iy, 300, 24, "Input", 16 if new else 15, 600, "text", group="head")
    return s


def c1_h(rh, rows, sep, new):
    return rh * rows + (0 if new else sep * rows)


PAGES = {"settings-shell": dict(title="Configuracoes: barra lateral e moldura do painel", render=lambda v, m: page_sound(m, v, TOK[v]),
                                golden=lambda m: f"{GOLD}/settings-sound-wide-{m}.png", sub="900 x 600, 1x; painel Som como amostra")}
