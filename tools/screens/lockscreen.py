# SPDX-License-Identifier: GPL-2.0-or-later
"""Lock screen and login window (ui/lock.rs, login.rs, kit.css "Lock / login"). Golden frame 900 x 600.

Current numbers are measured from lock-*.png and login-*.png (bounding boxes against the backdrop):
clock digits 78 tall (96 px type), date 22, avatar 96, name 15/600, pill 200 x 28, tiles pitch 160, power circles 32.
Proposal: the same elements, anchored on the diagonal: clock and date at the upper left (entry), the user panel (avatar, name, pill)
at the lower right (landing), the calm wallpaper between them (the centre of the nine)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene import Scene, TOK  # noqa: E402

W, H = 900, 600
GOLD = "/home/ubuntu/wolos/wt/webapp-int/crates/shell/tests/golden"
AV = {"cur": ("#5cb0ff", "#0a6fe0"), "new": ("#5cb0ff", "#0a6fe0")}   # tone gradients unchanged (kit.css avatar-tone-*)
TONES = [("#ff7fae", "#d02a6e", "A", "alice"), ("#ffb04d", "#e06a00", "D", "dinah"), ("#a48bff", "#6f4ff0", "MH", "Mad Hatter")]


def ink(s, v):
    if v == "cur":
        return ("#1c1838", "#161230") if s.mode == "light" else ("#ffffff", "#ffffff")
    return (s.t["text"], s.t["text"])


def avatar(s, cx, y, d, c0, c1, label, size):
    gid = f"av{len(s.defs)}"
    s.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient>')
    s.raw(f'<circle cx="{cx}" cy="{y + d / 2}" r="{d / 2}" fill="url(#{gid})"/>')
    s._node("box", (cx - d / 2, y, d, d), None, radius=d / 2, fill=c1)
    s.text(None, cx - d / 2, y, d, d, label, size, 600, "#ffffff", "middle", tree=False)


def pill(s, v, x, y, w, h, disc, placeholder="Enter Password", group="pill"):
    light = s.mode == "light"
    if v == "cur":
        fill, op, stroke, sop = ("#ffffff", 0.62, "#ffffff", 0.85) if light else ("#ffffff", 0.14, "#ffffff", 0.30)
        sh = "cur-card"
    else:
        fill, op, stroke, sop = ("#ffffff", 0.70, "#ffffff", 0.9) if light else ("#ffffff", 0.14, "#ffffff", 0.30)
        sh = "e2"
    p = s.panel(x, y, w, h, h / 2, fill=fill, opacity=op, stroke=stroke, stroke_op=sop, shadow=sh, role="control", group=group)
    ic = ink(s, v)[0]
    s.text(p, 16 if v == "new" else 12, 0, w - 90, h, placeholder, 13, 400, ic, opacity=0.72, tree=False)
    s.sym(p, w - 12 - disc - 6 - 16 - 2, (h - 16) // 2, 16, "view-reveal", ic, tree=False)
    dp = s.panel(w - (h - disc) // 2 - disc if v == "new" else w - 4 - disc, (h - disc) / 2, disc, disc, disc / 2,
                 fill=ic, opacity=0.8 if light else 0.3, parent=p, role="control")
    s.sym(dp, (disc - 12) / 2, (disc - 12) / 2, 12, "go-next", "#ffffff", tree=False)
    return p


def clock(s, v):
    c1, c2 = ink(s, v)
    if v == "cur":
        s.text(None, 0, 62, W, 115, "14:05", 96, 600, c1, "middle", ls=-2, opacity=0.92)
        s.text(None, 0, 176, W, 26, "Monday, 26 October", 22, 500, c2, "middle")
    else:
        s.text(None, 84, 60, 360, 120, "14:05", 80, 600, c1, "start", ls=-2, opacity=0.92)
        s.text(None, 84, 180, 360, 36, "Monday, 26 October", 24, 500, c2, "start")


def page_lock(mode, v, tok, name="lock"):
    s = Scene(W, H, mode, tok, name)
    clock(s, v)
    c1, c2 = ink(s, v)
    if v == "cur":
        avatar(s, 450, 377, 96, *AV["cur"], "AL", 22)
        s.text(None, 300, 478, 300, 24, "Alice Liddell", 15, 600, c2, "middle")
        pill(s, v, 350, 513, 200, 28, 20)
    else:
        cx = W - 84 - 120
        avatar(s, cx, 348, 84, *AV["new"], "AL", 22)
        s.text(None, cx - 120, 444, 240, 24, "Alice Liddell", 16, 600, c2, "middle")
        pill(s, v, cx - 120, 476, 240, 40, 28)
    return s


def page_login(mode, v, tok, name="login"):
    s = Scene(W, H, mode, tok, name)
    clock(s, v)
    c1, c2 = ink(s, v)
    light = mode == "light"
    if v == "cur":
        for i, (a, b, lab, nm) in enumerate(TONES):
            cx = 290 + i * 160
            avatar(s, cx, 341, 96, a, b, lab, 22)
            s.text(None, cx - 70, 446, 140, 24, nm, 15, 600, c2, "middle")
        for cx, ic, cap in ((370, "weather-clear-night", "Sleep"), (439, "view-refresh", "Restart"), (517, "system-shutdown", "Shut Down")):
            s.panel(cx - 16, 513, 32, 32, 16, fill="#ffffff", opacity=0.55 if light else 0.18, stroke="#ffffff", stroke_op=0.85 if light else 0.25, role="control", group="power")
            s.sym(None, cx - 8, 521, 16, ic, c2)
            s.text(None, cx - 40, 550, 80, 20, cap, 11, 400, c2, "middle", opacity=0.9)
    else:
        # tiles in the lower right: pitch 144 (tile 120 + gap 24), last tile ends 84 from the edge
        n = 3
        x_end = W - 84
        for i, (a, b, lab, nm) in enumerate(TONES):
            cx = x_end - 60 - (n - 1 - i) * 144
            avatar(s, cx, 348, 84, a, b, lab, 22)
            s.text(None, cx - 60, 444, 120, 24, nm, 16, 600, c2, "middle")
        # power row: quiet, lower left, 40 circles, gap 40
        for i, (ic, cap) in enumerate((("weather-clear-night", "Sleep"), ("view-refresh", "Restart"), ("system-shutdown", "Shut Down"))):
            cx = 84 + 20 + i * 80
            s.panel(cx - 20, 476, 40, 40, 20, fill="#ffffff", opacity=0.62 if light else 0.18, stroke="#ffffff", stroke_op=0.9 if light else 0.25, role="control", group="power", shadow="e1")
            s.sym(None, cx - 8, 488, 16, ic, c2)
            s.text(None, cx - 40, 524, 80, 20, cap, 11, 400, c2, "middle", opacity=0.9)
    return s


def _mk(key, title, fn, g):
    def render(v, m):
        return fn(m, v, TOK[v], key)
    return dict(title=title, render=render, golden=lambda m: f"{GOLD}/{g.format(m=m)}.png", sub="900 x 600, 1x (o quadro dos goldens)")


PAGES = {
    "lock": _mk("lock", "Tela de bloqueio", page_lock, "lock-{m}"),
    "login": _mk("login", "Janela de login", page_login, "login-{m}"),
}
