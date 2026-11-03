# SPDX-License-Identifier: GPL-2.0-or-later
"""App glyphs on the 64 grid (LANGUAGE.md 3): planes, not outlines; primary tone (paper or ink,
whichever contrasts with the body), the category tint for planes behind it, at most one pop.
Each glyph is fn(fg, body, tint, pop) -> SVG elements. Kits sit under the lid band (y >= 22)."""
import math

from palette import INK, PAPER

W = 4.0     # main stroke (3 px at 48, 8 at 128)
WD = 2.5    # detail stroke (minimum)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def gear_d(cx, cy, ro, ri, teeth, tw=0.36):
    pts = []
    for k in range(teeth):
        a = 2 * math.pi * k / teeth - math.pi / 2
        for da, r in ((-tw * 1.25, ri), (-tw * 0.62, ro), (tw * 0.62, ro), (tw * 1.25, ri)):
            t = a + da * math.pi / teeth
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"


def keyhole_d(cx, cy, s=1.0):
    r = 3.6 * s
    return (f"M{f(cx - 1.6 * s)} {f(cy + 1.8 * s)}L{f(cx - 2.8 * s)} {f(cy + 8.5 * s)}H{f(cx + 2.8 * s)}"
            f"L{f(cx + 1.6 * s)} {f(cy + 1.8 * s)}A{f(r)} {f(r)} 0 1 0 {f(cx - 1.6 * s)} {f(cy + 1.8 * s)}Z")


def sparkle_d(cx, cy, r, waist=0.2):
    w = r * waist
    return (f"M{f(cx)} {f(cy - r)}Q{f(cx + w)} {f(cy - w)} {f(cx + r)} {f(cy)}Q{f(cx + w)} {f(cy + w)} {f(cx)} {f(cy + r)}"
            f"Q{f(cx - w)} {f(cy + w)} {f(cx - r)} {f(cy)}Q{f(cx - w)} {f(cy - w)} {f(cx)} {f(cy - r)}Z")


def arc_d(cx, cy, r, a0, a1):
    """Arc from angle a0 to a1 (degrees, clockwise on screen, 0 = east)."""
    p = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{f(x0)} {f(y0)}A{f(r)} {f(r)} 0 {large} 1 {f(x1)} {f(y1)}"


# ---- the eight approved samples (.claude/brand/icons-apps/new) ---------------------------
def g_settings(fg, body, tint, pop):
    return (f'<path d="{gear_d(32, 32, 19, 14.5, 7)}" fill="{fg}" stroke="{fg}" stroke-width="3"/>'
            f'<circle cx="32" cy="32" r="8.6" fill="{body}"/>'
            f'<path d="{keyhole_d(32, 28.6, 0.95)}" fill="{pop}"/>')


def g_store(fg, body, tint, pop):
    # a market stall: striped awning with a scalloped hem, counter, door, a heart in the window
    xs = [14 + 7.2 * k for k in range(6)]
    parts = [f'<rect x="17" y="31" width="30" height="17" rx="3" fill="{tint}" stroke="{fg}" stroke-width="{W}"/>',
             f'<rect x="21.5" y="36" width="9" height="12" rx="1.5" fill="{fg}"/>']
    hem = f"M{f(xs[0])} 16V24"
    for k in range(5):
        a, b = xs[k], xs[k + 1]
        r = (b - a) / 2
        hem += f"A{f(r)} {f(r)} 0 0 0 {f(b)} 24"
        col = fg if k % 2 == 0 else PAPER
        parts.append(f'<path d="M{f(a)} 16V24A{f(r)} {f(r)} 0 0 0 {f(b)} 24V16Z" fill="{col}"/>')
    hem += "V16Z"
    parts.append(f'<path d="{hem}" fill="none" stroke="{fg}" stroke-width="1.6"/>')
    parts.append(f'<path d="M12.5 15.5H51.5" stroke="{fg}" stroke-width="{W}"/>')
    parts.append('<path d="M38.5 37.2c1.5-2 4.6-1.1 4.1 1.3-.4 1.5-2.4 3-4.1 4.1-1.7-1.1-3.7-2.6-4.1-4.1'
                 f'-.5-2.4 2.6-3.3 4.1-1.3z" fill="{pop}"/>')
    return "".join(parts)


def g_files(fg, body, tint, pop):
    # back plane with the tab on the RIGHT, the front plane lower, one label slot
    return (f'<path d="M15 21a3 3 0 0 1 3-3h17l3-3h8a3 3 0 0 1 3 3v24H15z" fill="{tint}"/>'
            f'<rect x="13" y="24" width="38" height="24" rx="3.5" fill="{fg}"/>'
            f'<rect x="20" y="30" width="12" height="4" rx="2" fill="{pop}"/>')


def g_terminal(fg, body, tint, pop):
    return (f'<path d="M17 20.5L28.5 32L17 43.5" fill="none" stroke="{fg}" stroke-width="5.5"/>'
            f'<rect x="33" y="38.5" width="14" height="6" rx="1.5" fill="{pop}"/>'
            f'<path d="M33 25.5h7" stroke="{tint}" stroke-width="{WD + .5}"/>')


def g_browser(fg, body, tint, pop):
    cx, cy, r = 32, 32, 14.5
    orbit = 'transform="rotate(-24 32 32)"'
    return (f'<path d="M9 32a23 8.5 0 0 1 46 0" fill="none" stroke="{tint}" stroke-width="3" {orbit}/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fg}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="6" ry="{r}" fill="none" stroke="{body}" stroke-width="{WD}"/>'
            f'<path d="M{cx - r + 1.5} {cy}H{cx + r - 1.5}" stroke="{body}" stroke-width="{WD}"/>'
            f'<path d="M55 32a23 8.5 0 0 1-46 0" fill="none" stroke="{tint}" stroke-width="3" {orbit}/>'
            f'<circle cx="49.6" cy="22.8" r="3.4" fill="{pop}" stroke="{body}" stroke-width="1.5"/>')


def g_music(fg, body, tint, pop):
    # a record on its deck, the tone arm in ink
    return (f'<circle cx="30" cy="34" r="16" fill="{fg}"/>'
            f'<circle cx="30" cy="34" r="11.5" fill="none" stroke="{tint}" stroke-width="1.6"/>'
            f'<circle cx="30" cy="34" r="6.2" fill="{pop}"/>'
            f'<circle cx="30" cy="34" r="1.6" fill="{fg}"/>'
            f'<path d="M48 13V30L41.5 36" fill="none" stroke="{INK}" stroke-width="{WD + .5}"/>'
            f'<circle cx="48" cy="13" r="3" fill="{INK}"/>')


def g_mail(fg, body, tint, pop):
    # an envelope closed with a wax seal (the keyhole motif: a letter is a secret)
    return (f'<rect x="12" y="19" width="40" height="27" rx="3.5" fill="{fg}"/>'
            f'<path d="M14 21.5L32 35L50 21.5" fill="none" stroke="{tint}" stroke-width="{W - .5}"/>'
            f'<circle cx="32" cy="35" r="6.5" fill="{pop}" stroke="{fg}" stroke-width="1.6"/>'
            f'<path d="{keyhole_d(32, 33.2, 0.5)}" fill="{body}"/>')


def g_installer(fg, body, tint, pop):
    # the little door: arched opening full of light, the leaf swung open, a step
    return (f'<path d="M22 49V26a10 10 0 0 1 20 0V49z" fill="{pop}"/>'
            f'<path d="M22 48V26a10 10 0 0 1 20 0V48" fill="none" stroke="{fg}" stroke-width="{W}"/>'
            f'<path d="M22 27L15.5 24V49L22 47Z" fill="{tint}" stroke="{fg}" stroke-width="2.6"/>'
            f'<circle cx="18.6" cy="37" r="1.4" fill="{body}"/>'
            f'<path d="M32 30V40M27.8 36L32 40.2L36.2 36" fill="none" stroke="{body}" stroke-width="{WD + .5}"/>'
            f'<path d="M16 50H46" stroke="{fg}" stroke-width="{W}"/>')


# ---- the rest of the set ------------------------------------------------------------------
def g_calculator(fg, body, tint, pop):
    # the four operations as one 2x2 block; equals carries the pop (no key grid, no column)
    s = 'stroke-width="4.5"'
    return (f'<path d="M15.5 22.5h13M22 16v13" stroke="{fg}" {s}/>'
            f'<path d="M35.5 22.5h13" stroke="{tint}" {s}/>'
            f'<path d="M17.4 38.4l9.2 9.2M26.6 38.4l-9.2 9.2" stroke="{fg}" {s}/>'
            f'<path d="M35.5 39.5h13M35.5 46.5h13" stroke="{pop}" {s}/>')


def g_calendar(fg, body, tint, pop):
    # a paper day card on two rings; today is a square in the body hue (no header band)
    cells = []
    for r, y in enumerate((27.5, 35, 42.5)):
        for c, x in enumerate((18.5, 29.5, 40.5)):
            col = body if (r, c) == (1, 1) else tint
            if (r, c) == (2, 2):
                continue
            cells.append(f'<rect x="{x}" y="{y}" width="5" height="5" rx="1.5" fill="{col}"/>')
    return (f'<rect x="13" y="17" width="38" height="34" rx="4" fill="{fg}"/>'
            + "".join(cells) +
            f'<rect x="41" y="43" width="4" height="4" rx="2" fill="{pop}"/>'
            f'<path d="M22 13v8M42 13v8" stroke="{tint}" stroke-width="{W}"/>')


def g_control_center(fg, body, tint, pop):
    # three level sliders: tint track above the knob, paper below; one knob carries the pop
    out = []
    for x, k, col in ((21, 36, fg), (32, 24, pop), (43, 30, fg)):
        out.append(f'<path d="M{x} 15V{k}" stroke="{tint}" stroke-width="{W}"/>')
        out.append(f'<path d="M{x} {k}V49" stroke="{fg}" stroke-width="{W}"/>')
        out.append(f'<circle cx="{x}" cy="{k}" r="5.2" fill="{col}" stroke="{body}" stroke-width="1.6"/>')
    return "".join(out)


def g_launcher(fg, body, tint, pop):
    # the looking glass: a lens with a spark in it
    return (f'<circle cx="28.5" cy="29" r="9" fill="{tint}"/>'
            f'<circle cx="28.5" cy="29" r="11.5" fill="none" stroke="{fg}" stroke-width="5"/>'
            f'<path d="M37.5 38L46.5 47" stroke="{fg}" stroke-width="6.5"/>'
            f'<path d="{sparkle_d(28.5, 29, 5.6, 0.22)}" fill="{pop}"/>')


def g_plugin_maker(fg, body, tint, pop):
    # a puzzle piece (paper) with a socket on the left, a spark where the next piece joins
    return (f'<rect x="18" y="22" width="25" height="25" rx="3.5" fill="{fg}"/>'
            f'<circle cx="30.5" cy="20" r="5" fill="{fg}"/>'
            f'<circle cx="45" cy="34.5" r="5" fill="{fg}"/>'
            f'<circle cx="18" cy="34.5" r="4.4" fill="{body}"/>'
            f'<path d="M24 41H33" stroke="{tint}" stroke-width="{WD + .5}"/>'
            f'<path d="{sparkle_d(48.5, 18, 5.2, 0.22)}" fill="{pop}"/>')


def g_notes(fg, body, tint, pop):
    # a notebook page (tint, ink edge), three written lines, a ribbon bookmark
    return (f'<rect x="16.5" y="13" width="31" height="38" rx="4" fill="{tint}" stroke="{fg}" stroke-width="{W}"/>'
            f'<path d="M23 25H41M23 32H41M23 39H34" stroke="{fg}" stroke-width="3"/>'
            f'<path d="M37 11V22L39.75 19.5L42.5 22V11Z" fill="{pop}"/>')


def g_photos(fg, body, tint, pop):
    # an instant print, tilted: ink frame, tint sky, ink hills, a violet sun
    return ('<g transform="rotate(-7 32 32)">'
            f'<rect x="14" y="13" width="36" height="39" rx="3.5" fill="{fg}"/>'
            f'<rect x="18" y="17" width="28" height="25" rx="1.5" fill="{tint}"/>'
            f'<path d="M18 42L26.5 30.5L32.5 37L37 32L46 42Z" fill="{fg}"/>'
            f'<circle cx="39.5" cy="24" r="3.6" fill="{pop}"/></g>')


def g_system_monitor(fg, body, tint, pop):
    # a dial: tint scale, paper level, the needle and a pop hub
    a = 302
    nx = 32 + 12 * math.cos(math.radians(a))
    ny = 39 + 12 * math.sin(math.radians(a))
    ticks = "".join(
        f'<path d="M{f(32 + 9.5 * math.cos(math.radians(t)))} {f(39 + 9.5 * math.sin(math.radians(t)))}'
        f'L{f(32 + 7 * math.cos(math.radians(t)))} {f(39 + 7 * math.sin(math.radians(t)))}" stroke="{tint}" stroke-width="2.5"/>'
        for t in (200, 235, 270, 305, 340))
    return (f'<path d="{arc_d(32, 39, 16, 180, 360)}" fill="none" stroke="{tint}" stroke-width="5"/>'
            f'<path d="{arc_d(32, 39, 16, 180, a)}" fill="none" stroke="{fg}" stroke-width="5"/>'
            + ticks +
            f'<path d="M32 39L{f(nx)} {f(ny)}" stroke="{fg}" stroke-width="3.5"/>'
            f'<circle cx="32" cy="39" r="4.2" fill="{pop}" stroke="{fg}" stroke-width="2"/>'
            f'<path d="M15 48H49" stroke="{fg}" stroke-width="{W}"/>')


def g_text_editor(fg, body, tint, pop):
    # lines being written, the caret after the last word
    return (f'<path d="M16 19H44M16 27H48M16 35H36" stroke="{fg}" stroke-width="{W}"/>'
            f'<path d="M16 43H30" stroke="{tint}" stroke-width="{W}"/>'
            f'<path d="M38 31.5H44M41 31.5V46.5M38 46.5H44" stroke="{pop}" stroke-width="{WD + .3}"/>')


def g_games(fg, body, tint, pop):
    # a pad: body-hue cross, two buttons (one pop)
    return ('<path d="M20.5 22H43.5a10 10 0 0 1 9.7 7.6l2.3 10.6a5.6 5.6 0 0 1-9.7 4.9L41.5 40.5H22.5'
            f'l-4.3 4.6a5.6 5.6 0 0 1-9.7-4.9l2.3-10.6A10 10 0 0 1 20.5 22z" fill="{fg}"/>'
            f'<path d="M17 31.5h9M21.5 27v9" stroke="{body}" stroke-width="3.4"/>'
            f'<circle cx="41" cy="28.5" r="2.7" fill="{body}"/>'
            f'<circle cx="46.5" cy="33.5" r="2.7" fill="{pop}"/>'
            f'<path d="M29 29.5h6" stroke="{tint}" stroke-width="{WD}"/>')


def g_trash(fg, body, tint, pop):
    # a woven wastepaper basket, open at the top: paper wicker, body-hue weave (no lid, no slots)
    walls = "M18.5 23H45.5L42 47.5A3.5 3.5 0 0 1 38.5 50.5H25.5A3.5 3.5 0 0 1 22 47.5Z"
    weave = "".join(f"M{x} 22L{x + 26} 52M{x + 26} 22L{x} 52" for x in (6, 15, 24, 33))
    return (f'<clipPath id="wall"><path d="{walls}"/></clipPath>'
            f'<path d="{walls}" fill="{fg}"/>'
            f'<path d="{weave}" stroke="{body}" stroke-width="2.2" clip-path="url(#wall)"/>'
            f'<rect x="14.5" y="18" width="35" height="6" rx="3" fill="{fg}" stroke="{body}" stroke-width="1.4"/>'
            f'<path d="M27 18.5H37" stroke="{tint}" stroke-width="{WD}"/>')


# ---- kits: the glyph lives under the lid band (y 22..53) -------------------------------
def g_kit_ai(fg, body, tint, pop):
    return (f'<path d="{sparkle_d(29.5, 38.5, 13, 0.2)}" fill="{fg}"/>'
            f'<path d="{sparkle_d(44, 28, 5, 0.22)}" fill="{pop}"/>'
            f'<circle cx="44.5" cy="46" r="2.4" fill="{tint}"/>')


def g_kit_codecs(fg, body, tint, pop):
    holes = "".join(f'<rect x="{x}" y="{y}" width="3.4" height="2.6" rx=".8" fill="{tint}"/>'
                    for x in (17, 23.5, 30, 36.5, 43) for y in (27.5, 46))
    return (f'<rect x="13" y="25" width="38" height="26" rx="3.5" fill="{fg}"/>' + holes +
            f'<rect x="18" y="32" width="28" height="12" rx="1.5" fill="{tint}"/>'
            f'<path d="M29 34.2L36.5 38L29 41.8Z" fill="{pop}"/>')


def g_kit_craft_suite(fg, body, tint, pop):
    return ('<g transform="rotate(-40 32 38)">'
            f'<rect x="14" y="33.5" width="26" height="9" rx="1.5" fill="{tint}" stroke="{fg}" stroke-width="3"/>'
            f'<path d="M40 33.5L50 38L40 42.5Z" fill="{fg}" stroke="{fg}" stroke-width="2"/>'
            f'<rect x="9.5" y="33.5" width="5" height="9" rx="1.5" fill="{pop}" stroke="{fg}" stroke-width="2"/>'
            f'<path d="M19 38H35" stroke="{fg}" stroke-width="{WD - .5}"/></g>')


def g_kit_creative(fg, body, tint, pop):
    return ('<path d="M32 24c10.5 0 18 6.5 18 13.5 0 5-4.5 6.5-8 6-2.6-.4-4.3 1.2-3.6 3.6.8 2.8-1.8 5-6.4 5'
            f'-10 0-18-6.8-18-14.4S21.5 24 32 24z" fill="{fg}"/>'
            f'<circle cx="23" cy="36" r="3" fill="{tint}"/>'
            f'<circle cx="29" cy="30" r="3" fill="{body}"/>'
            f'<circle cx="37.5" cy="30.5" r="3" fill="{pop}"/>'
            f'<circle cx="26" cy="44" r="3" fill="{tint}"/>')


def g_kit_dev(fg, body, tint, pop):
    return (f'<path d="M23 29L15.5 37.5L23 46M41 29L48.5 37.5L41 46" fill="none" stroke="{fg}" stroke-width="{W + .5}"/>'
            f'<path d="M35.5 26.5L28.5 48.5" stroke="{pop}" stroke-width="3.2"/>')


def g_kit_gaming(fg, body, tint, pop):
    return (f'<path d="M32 43V31" stroke="{tint}" stroke-width="{W}"/>'
            f'<circle cx="32" cy="29" r="6" fill="{fg}"/>'
            f'<rect x="16" y="42" width="32" height="9" rx="3.5" fill="{fg}"/>'
            f'<circle cx="41.5" cy="46.5" r="2.4" fill="{pop}"/>'
            f'<path d="M21 46.5H27" stroke="{body}" stroke-width="{WD}"/>')


# name, category (tokens icon.categories), glyph, kit (lid band)
APPS = [
    ("settings", "system", g_settings, False),
    ("software", "store", g_store, False),
    ("files", "files", g_files, False),
    ("terminal", "dev", g_terminal, False),
    ("browser", "web", g_browser, False),
    ("music", "media", g_music, False),
    ("mail", "talk", g_mail, False),
    ("installer", "wolos", g_installer, False),
    ("calculator", "system", g_calculator, False),
    ("calendar", "talk", g_calendar, False),
    ("control-center", "wolos", g_control_center, False),
    ("launcher", "wolos", g_launcher, False),
    ("plugin-maker", "wolos", g_plugin_maker, False),
    ("notes", "store", g_notes, False),
    ("photos", "media", g_photos, False),
    ("system-monitor", "system", g_system_monitor, False),
    ("text-editor", "files", g_text_editor, False),
    ("games", "web", g_games, False),
    ("trash", "system", g_trash, False),
    ("kit-ai", "wolos", g_kit_ai, True),
    ("kit-codecs", "media", g_kit_codecs, True),
    ("kit-craft-suite", "store", g_kit_craft_suite, True),
    ("kit-creative", "talk", g_kit_creative, True),
    ("kit-dev", "dev", g_kit_dev, True),
    ("kit-gaming", "web", g_kit_gaming, True),
]
