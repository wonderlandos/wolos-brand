# SPDX-License-Identifier: GPL-2.0-or-later
"""The Store (ui/store.rs on kit AppWindow, kit AppTile and hero_banner), golden frame 900 x 600.

Current numbers are measured from store-discover-wide-light.png: toolbar 36, sidebar 228, hero 623 x 190 (r 10, pad 28 32),
tiles 304 wide at pitch 320 x 80 (icon 48, name 13/600, summary 11, Get pill 80 x 24), heading 'title' 13/600.
Content in the mock uses WolOS's own apps (A2 icons)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene import Scene, TOK, wrap  # noqa: E402
from settingspages import frame, TINT, W, H, GOLD  # noqa: E402

SIDE = [[("Discover", "starred", "earth", "#0C8A80"), ("Create", "preferences-color", "earth", "#CF3A68"), ("Work", "accessories-text-editor", "earth", "#6A4DF4"),
         ("Play", "applications-games", "earth", "#B07A0C"), ("Develop", "utilities-terminal", "earth", "#0C8A80")],
        [("Kits", "view-app-grid", "base", "#6A4DF4"), ("Plugins", "preferences-desktop-apps", "base", "#6A4DF4")],
        [("Updates", "emblem-synchronizing", "wood", "#B07A0C"), ("Community", "network-workgroup", "water", "#B07A0C")]]


def sidebar(s, sb, new, sw, mode, sel):
    t = TINT[mode]
    if new:
        sx, sy, sh_, swd, r, pitch, rowh, gap, ry0 = 12, 8, 32, sw - 24, 8, 28, 24, 16, 8 + 32 + 12
    else:
        sx, sy, sh_, swd, r, pitch, rowh, gap, ry0 = 8, 8, 28, 212, 6, 28, 28, 12, 8 + 28 + 11
    sf = s.panel(sx, sy, swd, sh_, r, fill="control", parent=sb, stroke="line", role="control", group="side")
    s.sym(sf, 10, (sh_ - 16) // 2, 16, "system-search", "accent_ink")
    s.text(sf, 34, 0, 120, sh_, "Search", 13, 400, "dim", tree=False)
    y = ry0
    for grp in SIDE:
        for lab, ic, ph, old in grp:
            if lab == sel:
                s.panel(sx, y, sw - 2 * sx, rowh, r, fill="accent", opacity=0.18, parent=sb, role="control", group="rows")
            try:
                s.sym(sb, sx + 8, y + (rowh - 16) // 2, 16, ic, t[ph] if new else old)
            except FileNotFoundError:
                s.sym(sb, sx + 8, y + (rowh - 16) // 2, 16, "view-app-grid", t[ph] if new else old)
            s.text(sb, sx + 8 + 16 + 8, y, 150, rowh, lab, 13, 500 if lab == sel else 400, "text", group="labels")
            y += pitch
        y += gap - (pitch - rowh) if new else gap


APPS = [("atlas-folio", "Atlas", "Fast, private web browser"), ("mail", "Mail", "Mail, calendar and contacts"), ("notes", "Notes", "Plain notes that sync"),
        ("photos", "Photos", "Edit and share your pictures"), ("music", "Music", "Plays any song or podcast"), ("text-editor", "Text Editor", "Plain text and code")]


def get_pill(s, parent, x, y, w, h, new, label="Get"):
    p = s.panel(x, y, w, h, h // 2, fill="control", parent=parent, role="control", group="get")
    s.text(p, 0, 0, w, h, label, 13, 700 if not new else 600, "accent_ink", "middle", tree=False)


def page_discover(mode, v, tok, name="store-discover"):
    new = v == "new"
    s = Scene(W, H, mode, tok, name, backdrop=None)
    root, sb, tb, sw = frame(s, v, new)
    sidebar(s, sb, new, sw, mode, "Discover")
    if new:
        pw = 576
        px = sw + 1 + (W - sw - 1 - pw) // 2
    else:
        px, pw = sw + 1 + 24, W - sw - 1 - 48
    ty = tb + 4
    s.text(root, px, ty, 400, 40 if new else 34, "Discover", 27 if new else 26, 700, "text", ls=-0.5, group="title")
    hy = ty + (40 if new else 34) + (16 if new else 17)
    hh = 216 if new else 190
    hr = 16 if new else 10
    gid = "hg"
    c0, c1 = ("#007B9E", "#1C3A8A") if new else ("#B2501A", "#1F4B7A")
    s.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient>')
    s.raw(f'<rect x="{px}" y="{hy}" width="{pw}" height="{hh}" rx="{hr}" fill="url(#{gid})"/>')
    hb = s._node("opening" if new else "box", (px, hy, pw, hh), root, radius=hr, fill=c1)
    pad_x = 40 if new else 32
    if new:
        s.text(hb, pad_x, 36, 300, 16, "PHOTOS", 11, 600, "#ffffff", ls=0.4, opacity=0.8, group="hero")
        s.text(hb, pad_x, 56, 380, 40, "Bring your pictures to life", 27, 700, "#ffffff", ls=-0.5, group="hero")
        s.text(hb, pad_x, 100, 340, 40, "", 13, 400, "#ffffff", lines=wrap("Edit, organise and share. The free studio for every picture you take.", 340), lh=20, opacity=0.92)
        b = s.panel(pad_x, 156, 120, 40, 20, fill="#ffffff", parent=hb, role="control", shadow="e1")
        s.text(b, 0, 0, 120, 40, "Get", 13, 600, "#151520", "middle", tree=False)
        s.icon(hb, pw - 40 - 120, (hh - 120) // 2, 120, "photos", shadow=None)
    else:
        s.text(hb, pad_x, 28, 300, 16, "PHOTOS", 11, 600, "#ffffff", ls=0.4, opacity=0.8, group="hero")
        s.text(hb, pad_x, 50, 420, 34, "Bring your pictures to life", 26, 700, "#ffffff", ls=-0.5, group="hero")
        s.text(hb, pad_x, 90, 420, 32, "", 13, 400, "#ffffff", lines=wrap("Edit, organise and share. The free studio for every picture you take.", 420), lh=16, opacity=0.92)
        b = s.panel(pad_x, 138, 80, 24, 12, fill="#ffffff", parent=hb, role="control")
        s.text(b, 0, 0, 80, 24, "Get", 13, 700, "#181521", "middle", tree=False)
        s.icon(hb, pw - 32 - 128, (hh - 128) // 2, 128, "photos", shadow=None)
    ey = hy + hh + (24 if new else 22)
    s.text(root, px, ey, 300, 24 if new else 20, "Essentials", 16 if new else 13, 600, "text", group="head")
    ty0 = ey + (24 if new else 20) + (8 if new else 8)
    colw = 276 if new else 304
    gx = 24 if new else 16
    tile_h, pitch = (72, 80) if new else (64, 80)
    for i, (ic, nm, sub) in enumerate(APPS):
        cx = px + (i % 2) * (colw + gx)
        cy = ty0 + (i // 2) * pitch
        t = s._node("box", (cx, cy, colw, tile_h), root, group="tiles") if False else None
        s.icon(root, cx - px + px - px + 0, 0, 0, "photos", tree=False) if False else None
        isz = 48
        s.icon(root, cx, cy + (tile_h - isz) // 2, isz, ic if ic != "atlas-folio" else "atlas-folio", shadow=None)
        s.text(root, cx + isz + (12 if not new else 12), cy + (tile_h - 36) // 2, colw - isz - 12 - 60 - 8, 20, nm, 13, 600, "text", group="tn")
        s.text(root, cx + isz + 12, cy + (tile_h - 36) // 2 + 20, colw - isz - 12 - 60 - 8, 16, sub, 11, 400, "dim", tree=False)
        gw = 60 if new else 80
        get_pill(s, root, cx + colw - gw, cy + (tile_h - 24) // 2, gw, 24, new)
    return s


def page_details(mode, v, tok, name="store-details"):
    new = v == "new"
    s = Scene(W, H, mode, tok, name, backdrop=None)
    root, sb, tb, sw = frame(s, v, new)
    sidebar(s, sb, new, sw, mode, "Discover")
    if new:
        pw = 576
        px = sw + 1 + (W - sw - 1 - pw) // 2
    else:
        px, pw = sw + 1 + 24, W - sw - 1 - 48
    ty = tb + 8
    s.sym(root, px, ty + 4, 16, "go-previous", "text")
    iy = ty + 40
    isz = 120 if new else 128
    s.icon(root, px, iy, isz, "photos", shadow=None)
    tx = px + isz + (24 if new else 24)
    s.text(root, tx, iy + 12, 360, 40 if new else 34, "Photos", 27 if new else 26, 700, "text", ls=-0.5, group="dh")
    s.text(root, tx, iy + 12 + (44 if new else 38), 360, 20, "Edit and share your pictures", 13, 400, "dim", group="dh")
    bw, bh = (120, 40) if new else (80, 24)
    b = s.panel(tx - px, 12 + (44 if new else 38) + 20 + (16 if new else 12) + (iy - ty) - (iy - ty), bw, bh, bh // 2, fill="accent" if new else "control", parent=None, role="control") if False else None
    by = iy + 12 + (44 if new else 38) + 20 + (16 if new else 12)
    pb = s.panel(tx, by, bw, bh, bh // 2, fill="accent" if new else "control", role="control", shadow="e1" if new else None, group="dh")
    s.text(pb, 0, 0, bw, bh, "Get", 13, 600 if new else 700, "accent_text" if new else "accent_ink", "middle", tree=False)
    hy = iy + isz + (24 if new else 24)
    s.text(root, px, hy, 300, 24 if new else 20, "Information", 16 if new else 15, 600, "text", group="head")
    cy = hy + (24 if new else 22) + 8
    rh = 40
    c1 = s.panel(px, cy, pw, rh * 3 + (0 if new else 3), 12 if new else 10, fill="card", parent=root, stroke="line", shadow="e1" if new else None, role="box", group="cards")
    for i, (a, b2) in enumerate((("Size", "154.93 MiB"), ("Source", "System packages"), ("Version", "2.10.38"))):
        yy = i * (rh + (0 if new else 1))
        if i:
            s.line(12 if new else 1, yy - (0 if new else 1), pw - 24 if new else pw - 2, 1, "line", parent=c1)
        s.text(c1, 12, yy, 200, rh, a, 13, 400, "text", group="rr")
        s.text(c1, pw - 12 - 240, yy, 240, rh, b2, 13, 400, "dim", "end", tree=False)
    return s


PAGES = {
    "store-discover": dict(title="Loja: Descobrir", render=lambda v, m: page_discover(m, v, TOK[v]), golden=lambda m: f"{GOLD}/store-discover-wide-{m}.png",
                           sub="900 x 600, 1x; apps do proprio WolOS (icones A2)"),
    "store-details": dict(title="Loja: pagina de um app", render=lambda v, m: page_details(m, v, TOK[v]), golden=lambda m: f"{GOLD}/store-details-native-wide-{m}.png",
                          sub="900 x 600, 1x"),
}
