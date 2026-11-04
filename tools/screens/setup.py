# SPDX-License-Identifier: GPL-2.0-or-later
"""Setup Assistant pages (ui/setup.rs): the welcome hero, Wi-Fi, appearance, done. Shares the card with the installer."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import assistant as A  # noqa: E402
from assistant import ILL, MARK, new, head, foot, start, card_list  # noqa: E402
from scene import Scene, TOK, wrap  # noqa: E402

SETUP_STEPS = 6


def _P(P):
    Q = dict(P)
    Q["app_icon"] = "mark"
    return Q


def page_welcome(mode, P, tok, name="setup-welcome"):
    """Full-bleed art, the title on its calm left (ui/setup.rs welcome, kit::assistant::welcome)."""
    s = Scene(1280, 800, mode, tok, name, backdrop=None)
    art = os.path.join(ILL, "setup-welcome@2x.png" if os.path.exists(os.path.join(ILL, "setup-welcome@2x.png")) else "setup-welcome@1x.png")
    # cover, anchored bottom-right (assistant::cover_anchored)
    from PIL import Image
    iw, ih = Image.open(art).size
    sc = max(1280 / iw, 800 / ih)
    s.image(1280 - iw * sc, 800 - ih * sc, iw * sc, ih * sc, png_path=art, tree=False)
    on = "#ffffff"
    if not new(P):
        x, tl = 72, 0
        s.text(None, x, 296, 520, 150, "", 60, 700, on, lines=["Welcome to", "WolOS"], lh=72, ls=-1)
        s.text(None, x, 456, 520, 28, "Let’s get you set up.", 18, 400, on, opacity=0.82)
        s.button(None, x, 506, 100, 36, "Continue", "primary", r=18, size=14)
    else:
        x = 84
        s.image(60, 60, 40, 40, svg_path=MARK["dark"], role="box")
        s.text(None, 60 + 52, 60, 120, 40, "WolOS", 16, 600, on, opacity=0.9)
        s.text(None, x, 276, 480, 168, "", 56, 700, on, lines=["Welcome to", "WolOS"], lh=84, ls=-1)
        s.text(None, x, 464, 480, 24, "Let’s get you set up.", 16, 400, on, opacity=0.86)
        s.button(None, x, 512, 168, 40, "Continue", "primary", r=20, size=14, shadow="e1")
    return s


def page_wifi(mode, P, tok, name="setup-wifi"):
    s, c, w, h = start(mode, _P(P), tok, name)
    P = _P(P)
    y = head(s, P, c, w, "network-wireless-signal-good" if not new(P) else None, "Wi-Fi",
             ["Choose a network to get online. You can skip this and join later."], step=2 if new(P) else None)
    if not new(P):
        pass
    rows = [("Wonderland", ""), ("Rabbit Hole 5G", ""), ("Tea Party", "")]
    pad = P["pad"]
    rh = P["list_row"]
    top = y + P["gap_head"]
    bot = h - pad - P["btn_h"] - 24
    ly = round((top + max(0, (bot - top - rh * 3) // 2)) / 4) * 4
    cl = card_list(s, P, c, pad, ly, w - 2 * pad, rows, 0, icon="network-wireless-signal-good")
    for i in range(3):
        s.sym(cl, w - 2 * pad - 12 - 16 - 24, i * rh + (rh - 16) // 2, 16, "network-wireless-encrypted" if i < 2 else "network-wireless-signal-good", "dim")
    foot(s, P, c, w, h, extra="Not Now")
    return s


def preview(s, P, parent, x, y, pw, ph, kind, sel):
    r = P["ctl_r"]
    if sel:
        s.panel(x - 3, y - 3, pw + 6, ph + 6, r + 3, fill="accent", parent=parent, role="box", opacity=0.9, group="prev")
    fills = {"Light": ("#e9e9f3", "#ffffff"), "Dark": ("#1f1d29", "#2a2834"), "Auto": ("#e9e9f3", "#2a2834"),
             "Wonderland": ("#e9e7f6", "#ffffff"), "Ocean": ("#dce6f3", "#ffffff"), "Slate": ("#e3e3e8", "#ffffff")}
    a, b = fills[kind]
    pv = s.panel(x, y, pw, ph, r, fill=a, parent=parent, stroke="line", role="box", group="prev")
    s.panel(pw * 0.34, 6, pw * 0.60, ph - 12, 4 if new(P) else 3, fill=b, parent=pv, role="box")
    for i in range(3):
        s.panel(8, 10 + i * 8, pw * 0.2, 3, 1, fill="#8a87a0", parent=pv, role="line" if False else "box", tree=False)
    acc = {"Ocean": "#1d64b0", "Slate": "#5e6070"}.get(kind, "accent")
    s.panel(pw * 0.34 + pw * 0.60 - 28, ph - 18, 22, 8, 4, fill=acc, parent=pv, role="box", tree=False)
    return pv


def page_appearance(mode, P, tok, name="setup-appearance"):
    s, c, w, h = start(mode, _P(P), tok, name)
    P = _P(P)
    y = head(s, P, c, w, "preferences-desktop-appearance" if not new(P) else None, "Appearance",
             ["Choose a look. You can change it any time in System Settings."], step=5 if new(P) else None)
    pad = P["pad"]
    pw, ph, gx, gy = (112, 78, 20, 28) if not new(P) else (120, 84, 28, 40)
    kinds = ["Light", "Dark", "Auto", "Wonderland", "Ocean", "Slate"]
    gw = 3 * pw + 2 * gx
    x0 = (w - gw) // 2 if not new(P) else pad
    y0 = y + (28 if not new(P) else P["gap_head"])
    for i, k in enumerate(kinds):
        cx = x0 + (i % 3) * (pw + gx)
        cy = y0 + (i // 3) * (ph + gy + 16)
        preview(s, P, c, cx, cy, pw, ph, k, sel=(k == ("Wonderland")))
        s.text(c, cx, cy + ph + 4, pw, 20 if new(P) else 18, k, 13, 600 if k == "Wonderland" else 400, "text", "middle", group="labels")
    foot(s, P, c, w, h)
    return s


def page_done(mode, P, tok, name="setup-done"):
    s, c, w, h = start(mode, _P(P), tok, name)
    P = _P(P)
    pad = P["pad"]
    if not new(P):
        s.image((w - 240) // 2, 40, 240, 240, png_path=os.path.join(ILL, "keyhole@2x.png"), parent=c)
        s.text(c, pad, 296, w - 2 * pad, 34, "You’re All Set", 26, 700, "text", "middle", ls=-0.5)
        s.text(c, pad, 338, w - 2 * pad, 18, "Your account is ready.", 13, 400, "dim", "middle")
        s.button(c, w - pad - 100, h - pad - 28, 100, 28, "Get Started", "primary", r=6)
    else:
        head(s, P, c, w, True, "You’re All Set", ["Your account is ready."], step=6)
        s.image(w - pad - 240, pad + 64, 240, 240, png_path=os.path.join(ILL, "keyhole@2x.png"), parent=c)
        lines = wrap("Welcome to WolOS. Your files, your apps and your settings are where you left them in your head, and everything can be changed later.", 200)
        s.text(c, pad, pad + 96, 200, 20 * len(lines), "", 13, 400, "dim", lines=lines, lh=20)
        s.button(c, w - pad - 168, h - pad - 40, 168, 40, "Get Started", "primary", r=8, shadow="e1", group="foot")
    return s


def _mk(table):
    pages = {}
    for key, (title, fn, g) in table.items():
        def render(v, m, fn=fn, key=key):
            return fn(m, A.P_CUR if v == "cur" else A.P_NEW, TOK[v], key)
        pages[key] = dict(title=title, render=render, golden=(lambda m, g=g: f"{A.GOLDEN}/{g.format(m=m)}.png"),
                          sub="1280 x 800, 1x; o mesmo cartao do instalador")
    return pages


PAGES = _mk({
    "setup-welcome": ("Setup: boas-vindas (arte em tela cheia)", page_welcome, "setup-welcome-1280-{m}"),
    "setup-wifi": ("Setup: Wi-Fi", page_wifi, "setup-wifi-1280-{m}"),
    "setup-appearance": ("Setup: aparencia", page_appearance, "setup-appearance-1280-{m}"),
    "setup-done": ("Setup: pronto", page_done, "setup-done-1280-{m}"),
})
