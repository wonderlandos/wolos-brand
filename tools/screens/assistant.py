# SPDX-License-Identifier: GPL-2.0-or-later
"""Installer and Setup pages (kit/assistant.rs Card): the current card (numbers measured from the goldens
installer-*-1280 and setup-*-1280, 1280 x 800) and the proposed one (named lengths, calculus.band).

Both come from the same builders; P_CUR and P_NEW are the whole difference (documented in docs/adr/brand-screens.md)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scene import Scene, ROOT, wrap  # noqa: E402

ILL = "/home/ubuntu/wolos/wt/webapp-int/design/illustrations/png"   # the shell's own art (its design submodule), so mocks match the goldens
MARK = {"light": os.path.join(ROOT, "brand", "wolos-mark.svg"), "dark": os.path.join(ROOT, "brand", "wolos-mark-on-dark.svg")}

P_CUR = dict(
    name="cur", card=(552, 492), radius=24, pad=32, shadow="cur-glass", fill_op=0.84, rim=True, centre_y=0.5,
    align="center", icon=48, title=(26, 700, 34, -0.5), sub=(13, 400, 16), gap_icon=8, gap_title=8, gap_head=24,
    btn_h=28, back_w=63, primary_w=None, ctl_r=6, field_h=30, pitch=38, label_w=96, label_gap=8, list_row=36, list_r=10,
    switch=(36, 22, 2), foot_gap=8, step=False, mark=None, hint=(12, 400, 16), bar=6, back_kind="default",
)
P_NEW = dict(
    name="new", card=(576, 540), radius=24, pad=40, shadow="e3", fill_op=0.86, rim=True, centre_y=0.5,
    align="left", icon=40, title=(27, 700, 40, -0.5), sub=(13, 400, 20), gap_icon=16, gap_title=8, gap_head=24,
    btn_h=40, back_w=96, primary_w=168, ctl_r=8, field_h=32, pitch=40, label_w=120, label_gap=12, list_row=40, list_r=12,
    switch=(36, 24, 2), foot_gap=12, step=True, mark=40, hint=(11, 400, 16), bar=8, back_kind="default",
)

STEPS = 7


def new(P):
    return P["name"] == "new"


def start(mode, P, tok, name, card_h=None, W=1280, H=800):
    s = Scene(W, H, mode, tok, name)
    if P.get("mark"):   # the door mark at the upper left of the screen: the entry of the whole screen
        m = P["mark"]
        s.image(60, 60, m, m, svg_path=MARK[mode], role="box")
        s.text(None, 60 + m + 12, 60, 96, 40, "WolOS", 16, 600, "text", opacity=0.8)
    w, h = P["card"]
    h = card_h or h
    x = (W - w) // 2
    y = (H - h) // 2 if P["centre_y"] == 0.5 else round((H * P["centre_y"] - h / 2) / 4) * 4
    c = s.panel(x, y, w, h, P["radius"], fill="glass", opacity=P["fill_op"], shadow=P["shadow"], stroke="#ffffff", stroke_op=0.22 if mode == "dark" else 0.6,
                role="opening", rim=P["rim"])
    return s, c, w, h


def head(s, P, c, w, icon, title, sub_lines, step=None, illu=None):
    """Icon, title, subtitle. Returns the y (card-relative) under the header."""
    pad = P["pad"]
    y = pad
    tsz, tw, tlh, tls = P["title"]
    ssz, sw, slh = P["sub"]
    if P["align"] == "center":
        if icon:
            s.sym(c, (w - P["icon"]) // 2, y, P["icon"], icon, "accent_ink", tree=True)
            y += P["icon"] + P["gap_icon"]
        s.text(c, pad, y, w - 2 * pad, tlh, title, tsz, tw, "text", "middle", ls=tls)
        y += tlh + P["gap_title"]
        if sub_lines:
            s.text(c, pad, y, w - 2 * pad, slh * len(sub_lines), "", ssz, sw, "dim", "middle", lines=list(sub_lines), lh=slh)
            y += slh * len(sub_lines)
    else:
        isz = P["icon"]
        tx = pad
        if icon:
            ai = P.get("app_icon", "installer")     # one identity per assistant: its own icon on every page
            if ai == "mark":
                s.image(pad, y, isz, isz, svg_path=MARK[s.mode], parent=c, role="box")
            else:
                s.icon(c, pad, y, isz, ai)
            tx = pad + isz + P["gap_icon"]
        s.text(c, tx, y, w - pad - tx - (64 if step else 0), tlh, title, tsz, tw, "text", "start", ls=tls)
        if step:
            s.text(c, w - pad - 64, y, 64, tlh, f"{step} of {STEPS}", 11, 500, "dim", "end", group="step")
        y += max(isz, tlh) + P["gap_title"]
        if sub_lines:
            s.text(c, pad, y, w - 2 * pad, slh * len(sub_lines), "", ssz, sw, "dim", "start", lines=list(sub_lines), lh=slh)
            y += slh * len(sub_lines)
    return y


def foot(s, P, c, w, h, back=True, primary="Continue", extra=None, status=None, primary_w=None):
    pad, bh, r = P["pad"], P["btn_h"], P["ctl_r"]
    y = h - pad - bh
    pw = primary_w or P["primary_w"] or max(88, round(7.4 * len(primary)) + 28)
    px = w - pad - pw
    if back:
        s.button(c, pad, y, P["back_w"], bh, "Back", P["back_kind"], r=r, group="foot")
    if extra:
        ew = round(7.4 * len(extra)) + 2 * (24 if new(P) else 16)
        if new(P):
            ew = 96
        s.button(c, px - P["foot_gap"] - ew, y, ew, bh, extra, "default" if not new(P) else "plain", r=r, group="foot")
    s.button(c, px, y, pw, bh, primary, "primary", r=r, shadow="e1" if new(P) else None, group="foot")
    if status:
        s.text(c, pad + P["back_w"] + 16, y, px - pad - P["back_w"] - 32, bh, status, 12 if not new(P) else 13, 400, "dim", "end", tree=False)
    return y


def label_col(P):
    return P["label_w"] + P["label_gap"]


def form_row(s, P, c, w, y, label, value="", ph="", trailing=None, focus=False, grp="fields"):
    pad, fh = P["pad"], P["field_h"]
    fx = pad + label_col(P)
    s.text(c, pad, y, P["label_w"], fh, label, 13, 400, "dim", "end" if not new(P) else "start", group="labels")
    s.field(c, fx, y, w - pad - fx, fh, value, ph, r=P["ctl_r"], trailing=trailing, focus=focus, group=grp)


def card_list(s, P, c, x, y, w, rows, selected=0, icon=None, group="list"):
    """Rows of (primary, secondary, glyph); a card-list of P['list_row'] rows."""
    rh = P["list_row"]
    cl = s.panel(x, y, w, rh * len(rows), P["list_r"], fill="card", parent=c, stroke="line", shadow="e1" if new(P) else None, role="box", group=group)
    for i, (a, b) in enumerate(rows):
        ry = i * rh
        if i:
            s.line(1 if not new(P) else 12, ry, w - 2 if not new(P) else w - 24, 1, "line", parent=cl)
        tx = 12
        if icon:
            s.sym(cl, 12, ry + (rh - 16) // 2, 16, icon, "dim")
            tx = 12 + 16 + 8
        s.text(cl, tx, ry, 240, rh, a, 13, 500 if icon else 400, "text", group="rows")
        s.text(cl, 200, ry, w - 200 - 40, rh, b, 13, 400, "dim", "end", tree=False)
        if i == selected:
            s.sym(cl, w - 12 - 16, ry + (rh - 16) // 2, 16, "emblem-ok", "accent_ink")
    return cl


# ------------------------------------------------------------------ pages
def page_account(mode, P, tok, name="account"):
    s, c, w, h = start(mode, P, tok, name, card_h=522 if not new(P) else None)
    sub = (["You use this to sign in. It is like your Windows or Mac user account: it signs in,", "installs apps and changes settings. Next: music and video formats."]
           if not new(P) else ["You use this to sign in, install apps and change settings.", "Next: music and video formats."])
    y = head(s, P, c, w, "user-available" if not new(P) else "settings", "Create Your Account", sub, step=4)
    y += P["gap_head"] if new(P) else 24
    pitch, fh, pad = P["pitch"], P["field_h"], P["pad"]
    for i, (lab, val, ph, tr, foc) in enumerate((("Full name", "Alice Liddell", "", None, True), ("Account name", "aliceliddell", "", None, False),
                                                  ("Password", "", "Choose a password", "view-reveal", False), ("Verify", "", "Type it again", "view-reveal", False))):
        form_row(s, P, c, w, y + i * pitch, lab, val, ph, tr, foc)
    y += 4 * pitch
    fx = pad + label_col(P)
    if not new(P):
        s.text(c, pad, y - 2, w - 2 * pad, 32, "", 12, 400, "dim", "middle", lines=["If the chip can’t open the disk, your account password does. Use letters, digits", "and common symbols only."], lh=16)
        y += 38
        s.text(c, pad, y, 111, fh, "Computer name", 13, 400, "dim", "end", group="labels")
        s.field(c, pad + 119, y, w - 2 * pad - 119, fh, "", "aliceliddell-wolos", r=P["ctl_r"], group="fields")
        y += 38
        s.text(c, pad, y + 4, 123, 18, "Log in automatically", 13, 400, "dim", group="labels")
        s.switch(c, pad + 135, y, *P["switch"][:2], on=False, pad=P["switch"][2])
    else:
        s.text(c, fx, y - 4, w - pad - fx, 32, "", 11, 400, "dim", lines=["If the chip can’t open the disk, your account password does.", "Use letters, digits and common symbols only."], lh=16)
        y += 36
        form_row(s, P, c, w, y, "Computer", "", "aliceliddell-wolos")
        y += pitch + 4
        s.text(c, pad, y, 240, 24, "Log in automatically", 13, 400, "text", group="labels")
        sw, sh, sp = P["switch"]
        s.switch(c, w - pad - sw, y, sw, sh, on=False, pad=sp)
    foot(s, P, c, w, h)
    return s


def page_disk(mode, P, tok, name="disk"):
    s, c, w, h = start(mode, P, tok, name)
    y = head(s, P, c, w, "drive-harddisk" if not new(P) else "drive-harddisk", "Choose a Disk",
             ["Choose where WolOS goes. A disk is the drive inside your computer that holds", "Windows, macOS or Linux and your files. Choosing one changes nothing yet.", "Next: whether WolOS shares the disk or takes all of it."]
             if not new(P) else ["Choose where WolOS goes: the drive inside your computer that holds", "your files. Choosing one changes nothing yet. Next: share the disk or take all of it."], step=2)
    rows = [("Samsung SSD 980 PRO", "1 TB · /dev/nvme0n1 · NVMe"), ("WD Blue SA510", "500 GB · /dev/sda")]
    pad = P["pad"]
    rh = P["list_row"]
    area_top = y + P["gap_head"]
    area_bot = h - pad - P["btn_h"] - 24
    ly = area_top + max(0, (area_bot - area_top - rh * len(rows)) // 2)
    ly = round(ly / 4) * 4
    card_list(s, P, c, pad, ly, w - 2 * pad, rows, 0, icon="drive-harddisk")
    foot(s, P, c, w, h)
    return s


def page_language(mode, P, tok, name="language"):
    s, c, w, h = start(mode, P, tok, name, card_h=560 if not new(P) else None)
    y = head(s, P, c, w, "preferences-desktop-locale" if False else "network-workgroup", "Language and Keyboard",
             ["Choose your language and the keyboard you type on. This is the language of menus", "and apps, and what your keys type. Both can be changed later in System Settings."]
             if not new(P) else ["The language of menus and apps, and what your keys type.", "Both can be changed later in System Settings."], step=1)
    y += P["gap_head"] if new(P) else 16
    pad = P["pad"]
    rows = [("English", "United States"), ("English", "United Kingdom"), ("Português", "Brasil"), ("Português", "Portugal"), ("Español", "España")]
    cl = card_list(s, P, c, pad, y, w - 2 * pad, rows, 0)
    y += P["list_row"] * 5 + (16 if not new(P) else 12)
    form_row(s, P, c, w, y, "Keyboard", "U.S.", "", "pan-down")
    form_row(s, P, c, w, y + P["pitch"], "Try it", "", "Type here to try the keyboard")
    foot(s, P, c, w, h)
    return s


def page_begin(mode, P, tok, name="begin"):
    s, c, w, h = start(mode, P, tok, name)
    pad = P["pad"]
    if not new(P):
        s.image((w - 240) // 2, 42, 240, 240, png_path=os.path.join(ILL, "white-rabbit@1x.png"), parent=c)
        y = 42 + 240 + 24
        s.text(c, pad, y, w - 2 * pad, 34, "Welcome to WolOS", 26, 700, "text", "middle", ls=-0.5)
        y += 42
        s.text(c, 20, y, w - 40, 64, "", 13, 400, "dim", "middle", lines=[
            "Install it on this computer, or try it first. Trying changes nothing. The installer",
            "asks a few questions first. Nothing on this computer changes until you click",
            "Install on the last page. Next: your language and keyboard."], lh=16)
        by = h - pad - P["btn_h"]
        s.button(c, w - pad - 221, by, 98, 28, "Try WolOS", "default", r=6)
        s.button(c, w - pad - 115, by, 115, 28, "Install WolOS", "primary", r=6)
    else:
        # entry upper left (icon, title), the art answers at the right, the landing is the lower right
        s.icon(c, pad, pad, 40, "installer")
        s.text(c, pad + 56, pad, 280, 40, "Welcome to WolOS", 27, 700, "text", ls=-0.5)
        s.text(c, w - pad - 64, pad, 64, 40, "", 11, 500, "dim", "end", group="step")
        lines = wrap("Install it on this computer, or try it first. Trying changes nothing. The installer asks a few questions first. "
                     "Nothing on this computer changes until you click Install on the last page. Next: your language and keyboard.", 232)
        s.text(c, pad, pad + 64, 232, 20 * len(lines), "", 13, 400, "dim", lines=lines, lh=20)
        s.image(w - pad - 232, pad + 56, 232, 232, png_path=os.path.join(ILL, "white-rabbit@2x.png"), parent=c)
        by = h - pad - P["btn_h"]
        s.button(c, pad, by, 120, 40, "Try WolOS", "default", r=P["ctl_r"], group="foot")
        s.button(c, w - pad - 168, by, 168, 40, "Install WolOS", "primary", r=P["ctl_r"], shadow="e1", group="foot")
    return s


def page_installing(mode, P, tok, name="installing"):
    s, c, w, h = start(mode, P, tok, name)
    pad = P["pad"]
    if not new(P):
        s.image((w - 200) // 2, 28, 200, 200, png_path=os.path.join(ILL, "pocket-watch@1x.png"), parent=c)
        y = 28 + 200 + 8
        s.text(c, pad, y, w - 2 * pad, 34, "Installing WolOS", 26, 700, "text", "middle", ls=-0.5)
        y += 42
        s.text(c, pad, y, w - 2 * pad, 48, "", 13, 400, "dim", "middle", lines=["This takes a few minutes. Keep your computer plugged in. Nothing restarts", "until you click Restart. The tips below show a few things worth knowing."], lh=16)
        y += 48
        s.panel(pad, y, w - 2 * pad, 6, 3, fill="control", parent=c)
        s.panel(pad, y, (w - 2 * pad) * 0.45, 6, 3, fill="accent", parent=c)
        s.text(c, pad, y + 14, w - 2 * pad, 18, "Encrypting the disk… About 3 minutes remaining", 12, 400, "dim", "middle")
        s.text(c, pad, y + 44, w - 2 * pad, 32, "", 12, 400, "dim", "middle", lines=["Updates install into a second copy of WolOS, so you can always start the", "previous one."], lh=16)
    else:
        s.icon(c, pad, pad, 40, "installer")
        s.text(c, pad + 56, pad, 280, 40, "Installing WolOS", 27, 700, "text", ls=-0.5)
        s.text(c, w - pad - 64, pad, 64, 40, "7 of 7", 11, 500, "dim", "end", group="step")
        s.text(c, pad, pad + 56, 240, 100, "", 13, 400, "dim", lines=["This takes a few minutes.", "Keep your computer plugged in.", "Nothing restarts until you", "click Restart."], lh=20)
        s.image(w - pad - 200, pad + 48, 200, 200, png_path=os.path.join(ILL, "pocket-watch@1x.png"), parent=c)
        by = h - pad - 160
        s.text(c, pad, by, 300, 20, "Encrypting the disk…", 13, 500, "text", group="prog")
        s.text(c, w - pad - 200, by, 200, 20, "About 3 minutes remaining", 13, 400, "dim", "end", group="prog")
        s.panel(pad, by + 28, w - 2 * pad, P["bar"], P["bar"] // 2, fill="control", parent=c)
        s.panel(pad, by + 28, round((w - 2 * pad) * 0.45), P["bar"], P["bar"] // 2, fill="accent", parent=c)
        s.text(c, pad, by + 56, w - 2 * pad, 40, "", 11, 400, "dim", lines=["Updates install into a second copy of WolOS, so you can always", "start the previous one."], lh=16)
        trail = s.panel(w - pad - 100, h - pad - 40, 100, 0, 0, fill="card", parent=c, tree=False)
    return s


PAGES_I = {
    "installer-begin": ("Instalador: boas-vindas", page_begin, "installer-begin-1280-{m}"),
    "installer-account": ("Instalador: criar conta", page_account, "installer-account-1280-{m}"),
    "installer-disk": ("Instalador: escolher disco", page_disk, "installer-disk-1280-{m}"),
    "installer-language": ("Instalador: idioma e teclado", page_language, "installer-language-1280-{m}"),
    "installer-installing": ("Instalador: instalando", page_installing, "installer-installing-1280-{m}"),
}
GOLDEN = "/home/ubuntu/wolos/wt/webapp-int/crates/shell/tests/golden"


def make_pages(table):
    pages = {}
    for key, (title, fn, g) in table.items():
        def render(v, m, fn=fn, key=key):
            return fn(m, P_CUR if v == "cur" else P_NEW, __import__("scene").TOK[v], key)
        pages[key] = dict(title=title, render=render, golden=(lambda m, g=g: f"{GOLDEN}/{g.format(m=m)}.png"),
                          sub="1280 x 800, 1x; cartao visivel 552 x 492 -> 576 x 540 (faixas cai x ben)")
    return pages
