# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Atlas chrome mock frames: the new tab page and the first run, drawn with the WolOS tokens
(tokens/colors.json), the HIG scaffold (36 px toolbar under the 28 px strip, 220 px sidebar, rows 28 px,
radius 6 / 10 / 12, spacing 4 8 12 16 24, Inter 13 / 11 / 26) and the symbolic icons of the theme.
They are illustrations for review, not a UI: the text is real SVG text (Inter), the names are invented.

  python3 -I atlas_chrome.py <design dir>            write brand/atlas/chrome/atlas-{newtab,firstrun}.svg + .png
  python3 -I atlas_chrome.py <design dir> --check    fail when a file on disk is not what this writes
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import atlas  # noqa: E402

DESIGN = atlas.DESIGN
T = atlas._T
FONT = "Inter, Cantarell, 'Noto Sans', 'DejaVu Sans', sans-serif"
# The 13 theme tokens of the two built-in WolOS themes, as shipped: crates/core/src/theme/builtin/wol-light.json
# and wol-dark.json (atlas_check.py compares them with those files when the design repo sits in the tree).
THEME = {
    "light": {"surface": "#F3F1F8", "sidebar": "rgba(233,231,241,0.92)", "card": "#FFFFFF", "line": "rgba(34,27,54,0.10)",
              "text": "#181521", "dim": "#686575", "accent": "#7C5CFF", "accentText": "#FFFFFF",
              "glass": "rgba(245,244,251,0.84)", "control": "#E9E9F3", "success": "#1C9A6E", "warning": "#D9541E",
              "danger": "#CF3A68"},
    "dark": {"surface": "#1B1924", "sidebar": "rgba(39,37,49,0.92)", "card": "#2A2834", "line": "rgba(237,232,255,0.10)",
             "text": "#F6F5FB", "dim": "#AAA7B6", "accent": "#8B6CFF", "accentText": "#FFFFFF",
             "glass": "rgba(35,33,45,0.84)", "control": "#393647", "success": "#5BE3B0", "warning": "#FF8A55",
             "danger": "#F2678F"},
}
KEY = "b"               # the direction the mocks wear: B, Folio, the one the lead chose (2026-11-03)


def col(c):
    """'#RRGGBB' or 'rgba(r,g,b,a)' -> (hex, opacity) so no renderer has to parse rgba()."""
    if c.startswith("url("):
        return c, 1.0
    m = re.match(r"rgba\((\d+),(\d+),(\d+),([\d.]+)\)", c)
    if m:
        r, g, b, a = m.groups()
        return "#%02X%02X%02X" % (int(r), int(g), int(b)), float(a)
    return c.upper(), 1.0


def fill(c, extra=1.0):
    h, a = col(c)
    a *= extra
    return f'fill="{h}"' + (f' fill-opacity="{a:.3g}"' if a < 1 else "")


def lum(h):
    v = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    v = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v]
    return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def over(fg, bg):
    """Composite an rgba token over an opaque hex ground; returns hex."""
    h, a = col(fg)
    f = [int(h[i:i + 2], 16) for i in (1, 3, 5)]
    g = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(a * x + (1 - a) * y) for x, y in zip(f, g))


class Frame:
    def __init__(self, mode, uid):
        self.m, self.d, self.uid = mode, T[mode], uid
        th = dict(THEME[mode])
        th["selection"] = T[mode]["selection"]          # the accent tint pill: alpha(accent, 22% / 30%), a design token
        self.t = th
        self.defs, self.out = [], []

    def add(self, s):
        self.out.append(s)

    def rect(self, x, y, w, h, c, r=0, extra=1.0, attrs=""):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {fill(c, extra)} {attrs}/>')

    def line(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def text(self, x, y, s, size=13, weight=400, c=None, anchor="start", extra=1.0):
        c = c or self.t["text"]
        s = s.replace("&", "&amp;")
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" {fill(c, extra)}>{s}</text>')

    def sym(self, name, x, y, size=16, c=None, dirname="icons/symbolic"):
        """A symbolic icon of the theme (16 grid, currentColor) placed at x, y."""
        src = open(os.path.join(DESIGN, dirname, f"{name}-symbolic.svg"), encoding="utf-8").read()
        m = re.search(r'<g fill="currentColor">(.*)</g>', src, re.S)
        inner = m.group(1) if m else "".join(re.findall(r'<path [^>]*?d="[^"]*"/>', src)).replace(' fill="currentColor"', "")
        self.add(f'<g transform="translate({x} {y}) scale({size / 16:g})" {fill(c or self.t["text"])}>{inner}</g>')

    def badge(self, x, y, px):
        d, b = atlas.badge(KEY, 2 if px >= 96 else 1, f"{self.uid}b{px}")
        self.defs.append(d)
        self.add(f'<g transform="translate({x - px * 100 / 824:g} {y - px * 100 / 824:g}) scale({px / 824:.6g})">{b}</g>')


def chrome(f, W=1280, H=800, sidebar=True, tabs=True):
    """Wallpaper, the 28 px strip and the window with its 36 px toolbar; returns the content rectangle."""
    t, m = f.t, f.m
    wall = (("#DCD3FF", "#F3F1F8") if m == "light" else ("#2C2358", "#191720"))
    f.defs.append(atlas.lin(f"{f.uid}w", [(0, wall[0], 1), (1, wall[1], 1)], 0, 0, .3, 1))
    f.rect(0, 0, W, H, f"url(#{f.uid}w)")
    f.rect(0, 0, W, 28, f.d["menubar"])
    f.sym("wolos-glyph", 12, 6, 16, t["text"], "brand")   # the menubar glyph (brand/wolos-glyph-symbolic.svg)
    f.text(36, 19, "Atlas", 13, 700)
    mx = 92
    for s in ("File", "Edit", "View", "History", "Bookmarks", "Window"):
        f.text(mx, 19, s, 13)
        mx += 7.2 * len(s) + 20
    f.text(W - 12, 19, "Tue 20:41", 13, anchor="end")
    # the window
    x, y, w, h = 80, 56, 1120, 700
    f.defs.append(f'<filter id="{f.uid}sh" x="-10%" y="-10%" width="120%" height="125%">'
                  '<feGaussianBlur stdDeviation="22"/></filter>')
    f.add(f'<rect x="{x}" y="{y + 18}" width="{w}" height="{h}" rx="12" fill="#000" fill-opacity="{.35 if m == "dark" else .18}" '
          f'filter="url(#{f.uid}sh)"/>')
    f.rect(x, y, w, h, t["surface"], 12)
    f.add(f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="11.5" fill="none" '
          f'stroke="{col(t["line"])[0]}" stroke-opacity="{col(t["line"])[1]}"/>')
    tb = 36
    # toolbar: glass over the window; clipped to the window's rounded top by drawing a rounded rect and
    # squaring its lower half
    f.rect(x, y, w, tb, t["glass"], 12)
    f.rect(x, y + 12, w, tb - 12, t["glass"])
    f.line(x, y + tb - 1, w, t["line"])
    ix = x + 12
    for nme in (("sidebar-show", True), ("go-previous", True), ("go-next", True), ("view-refresh", True)):
        f.sym(nme[0], ix, y + 10, 16, t["text"] if nme[0] != "go-next" else t["dim"])
        ix += 28 if nme[0] != "sidebar-show" else 36
    return x, y, w, h, tb


def omnibox(f, x, y, w, text, focused=False, locked=False, placeholder=True):
    t = f.t
    h = 26
    if focused:
        f.rect(x - 2, y - 2, w + 4, h + 4, t["accent"], 8, .9)
    f.rect(x, y, w, h, t["control"], 6)
    f.add(f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="5.5" fill="none" '
          f'stroke="{col(t["line"])[0]}" stroke-opacity="{col(t["line"])[1]}"/>')
    f.sym("system-lock-screen" if locked else "system-search", x + 8, y + 5, 16, t["dim"])
    f.text(x + 32, y + 18, text, 13, c=t["dim"] if placeholder else t["text"])


def toolbar_right(f, x, y, w):
    t = f.t
    rx = x + w - 12 - 16
    for nme in ("open-menu", "folder-download", "non-starred", "preferences-system-privacy"):
        f.sym(nme, rx, y + 10, 16, t["text"] if nme != "preferences-system-privacy" else t["accent"])
        rx -= 28


def sidebar(f, x, y, h, selected=1):
    """The tab list as the HIG sidebar: 220 px, glass, sections in small caps, rows 28 px, 16 px symbolic
    icons, the selection an accent tint pill."""
    t = f.t
    sw = 220
    f.rect(x, y, sw, h, t["sidebar"])
    f.rect(x + sw - 1, y, 1, h, t["line"])
    yy = y + 12

    def section(name):
        nonlocal yy
        f.text(x + 16, yy + 12, name.upper(), 11, 600, t["dim"])
        yy += 24

    def row(icon, label, sel=False, dim=False):
        nonlocal yy
        if sel:
            f.rect(x + 8, yy, sw - 16, 28, t["selection"], 6)
        f.sym(icon, x + 16, yy + 6, 16, t["accent"] if sel else t["dim"])
        f.text(x + 40, yy + 19, label, 13, 500 if sel else 400, t["text"] if not dim else t["dim"])
        yy += 28

    section("Pinned")
    row("user-home", "Home")
    row("mail-unread", "Mail")
    yy += 12
    section("Today")
    row("atlas", "New tab", selected == 1)       # the new tab page is Atlas's own: its 16 px glyph
    row("text-x-generic", "Release notes")
    row("text-x-generic", "Atlas manual")
    yy += 12
    section("Trip to Porto")
    row("user-bookmarks", "3 tabs", dim=True)
    # footer: new tab row at the bottom, as the HIG puts the primary action of a list under it
    f.line(x + 8, y + h - 44, sw - 16, t["line"])
    f.sym("tab-new", x + 16, y + h - 32, 16, t["text"])
    f.text(x + 40, y + h - 19, "New tab", 13)
    f.text(x + sw - 16, y + h - 19, "Ctrl T", 11, c=t["dim"], anchor="end")


def card_row_icon(f, x, y, cat, sym):
    c = T["icon"]["categories"][cat]
    f.rect(x, y, 32, 32, c["body"], 8)
    f.sym(sym, x + 8, y + 8, 16, "#FFFFFF", "icons/symbolic")


def newtab(mode="light"):
    f = Frame(mode, "nt")
    t = f.t
    x, y, w, h, tb = chrome(f)
    omnibox(f, x + (w - 560) // 2, y + 5, 560, "Search or enter an address", focused=True)
    toolbar_right(f, x, y, w)
    sidebar(f, x, y + tb, h - tb)
    cx0, cw = x + 220, w - 220
    mid = cx0 + cw / 2
    f.badge(mid - 36, y + 120, 72)
    f.text(mid, y + 240, "Atlas", 26, 700, anchor="middle")
    # search field (large)
    f.rect(mid - 280, y + 264, 560, 40, t["card"], 10)
    f.add(f'<rect x="{mid - 279.5}" y="{y + 264.5}" width="559" height="39" rx="9.5" fill="none" '
          f'stroke="{col(t["line"])[0]}" stroke-opacity="{col(t["line"])[1]}"/>')
    f.sym("system-search", mid - 264, y + 276, 16, t["dim"])
    f.text(mid - 240, y + 289, "Search or enter an address", 13, c=t["dim"])
    # pinned grid: 6 cards, 96 x 88, gap 16
    f.text(mid - 328, y + 352, "Pinned", 15, 600)
    tiles = (("web", "web-browser", "Home"), ("talk", "mail-unread", "Mail"), ("files", "folder-download", "Files"),
             ("media", "media-playback-start", "Video"), ("store", "starred", "Store"), ("system", "preferences-system", "Settings"))
    gx = mid - 328
    for i, (cat, sy, label) in enumerate(tiles):
        tx = gx + i * 112
        f.rect(tx, y + 366, 96, 88, t["card"], 10)
        f.add(f'<rect x="{tx + .5}" y="{y + 366.5}" width="95" height="87" rx="9.5" fill="none" '
              f'stroke="{col(t["line"])[0]}" stroke-opacity="{col(t["line"])[1]}"/>')
        card_row_icon(f, tx + 32, y + 378, cat, sy)
        f.text(tx + 48, y + 438, label, 11, c=t["dim"], anchor="middle")
    # continue: two cards
    f.text(mid - 328, y + 496, "Pick up where you left off", 15, 600)
    for i, (title, sub) in enumerate((("Release notes", "Opened 20 minutes ago"), ("Atlas manual", "Opened yesterday"))):
        tx = gx + i * 336
        f.rect(tx, y + 510, 320, 64, t["card"], 10)
        f.add(f'<rect x="{tx + .5}" y="{y + 510.5}" width="319" height="63" rx="9.5" fill="none" '
              f'stroke="{col(t["line"])[0]}" stroke-opacity="{col(t["line"])[1]}"/>')
        f.sym("text-x-generic", tx + 16, y + 526, 16, t["accent"])
        f.text(tx + 40, y + 539, title, 13, 600)
        f.text(tx + 40, y + 558, sub, 11, c=t["dim"])
    # status line (HIG status bar: quiet facts only)
    f.line(cx0, y + h - 24, cw, t["line"])
    f.text(mid, y + h - 8, "Do Not Track is on", 11, c=t["dim"], anchor="middle")
    return f


def firstrun(mode="dark"):
    f = Frame(mode, "fr")
    t = f.t
    x, y, w, h, tb = chrome(f)
    toolbar_right(f, x, y, w)
    omnibox(f, x + (w - 560) // 2, y + 5, 560, "Search or enter an address")
    cx0, cw = x, w
    mid = cx0 + cw / 2
    f.badge(mid - 48, y + 96, 96)
    f.text(mid, y + 236, "Welcome to Atlas", 26, 700, anchor="middle")
    f.text(mid, y + 262, "Three choices. Each one can be changed later in Settings.", 13, c=t["dim"], anchor="middle")
    cardx, cardw, rowh = mid - 260, 520, 56
    f.rect(cardx, y + 292, cardw, rowh * 3, t["card"], 10)
    f.add(f'<rect x="{cardx + .5}" y="{y + 292.5}" width="{cardw - 1}" height="{rowh * 3 - 1}" rx="9.5" fill="none" '
          f'stroke="{col(t["line"])[0]}" stroke-opacity="{col(t["line"])[1]}"/>')
    rows = (("preferences-system-privacy", "Do Not Track", "Sites are asked not to follow you. On by default.", "toggle"),
            ("folder-download", "Bring your bookmarks", "From another browser on this PC. Nothing leaves it.", "Choose…"),
            ("system-search", "Search", "Pick the search you want in the address bar.", "Choose…"))
    for i, (sym_, title, hint, ctl) in enumerate(rows):
        ry = y + 292 + i * rowh
        if i:
            f.line(cardx + 16, ry, cardw - 32, t["line"])
        f.sym(sym_, cardx + 16, ry + 20, 16, t["accent"])
        f.text(cardx + 44, ry + 24, title, 13, 600)
        f.text(cardx + 44, ry + 42, hint, 11, c=t["dim"])
        if ctl == "toggle":
            f.rect(cardx + cardw - 16 - 40, ry + 18, 40, 22, t["accent"], 11)
            f.rect(cardx + cardw - 16 - 20, ry + 20, 18, 18, t["accentText"], 9)
        else:
            bx = cardx + cardw - 16 - 88
            f.rect(bx, ry + 14, 88, 28, t["control"], 6)
            f.text(bx + 44, ry + 33, ctl, 13, anchor="middle")
    # the one primary action, right-aligned under the card (HIG: destructive/primary on the right)
    bx = cardx + cardw - 140
    f.rect(bx, y + 292 + rowh * 3 + 24, 140, 36, t["accent"], 6)
    f.text(bx + 70, y + 292 + rowh * 3 + 24 + 23, "Start browsing", 13, 600, t["accentText"], "middle")
    f.text(cardx, y + 292 + rowh * 3 + 24 + 23, "You can skip this and decide later.", 11, c=t["dim"])
    return f


def svg(f, W=1280, H=800, title=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<title>{title}</title>'
            '<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. Atlas brand: a mock, not a UI. -->'
            f'<defs>{"".join(f.defs)}</defs>{"".join(f.out)}</svg>\n')


def files():
    return {
        "brand/atlas/chrome/atlas-newtab.svg": svg(newtab("light"), title="Atlas chrome mock: new tab (light)"),
        "brand/atlas/chrome/atlas-firstrun.svg": svg(firstrun("dark"), title="Atlas chrome mock: first run (dark)"),
    }


def build(design, check=False):
    design = os.path.abspath(design)
    bad = []
    for rel, text in files().items():
        p = os.path.join(design, rel)
        if check:
            if not os.path.isfile(p) or open(p, encoding="utf-8").read() != text:
                bad.append(rel)
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        subprocess.run(["rsvg-convert", p, "-o", p[:-4] + ".png"], check=True)
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chk = "--check" in sys.argv
    bad = build(args[0] if args else DESIGN, check=chk)
    if bad:
        print("atlas_chrome: out of date or missing:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print("atlas_chrome: ok" if chk else "atlas_chrome: written")
