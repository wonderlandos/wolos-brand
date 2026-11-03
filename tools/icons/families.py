# SPDX-License-Identifier: GPL-2.0-or-later
"""Families (LANGUAGE.md 7): places are folders (tab on the right, a paper emblem on the front
plane, never embossed) plus the trash basket; devices are ink slabs with one mint LED; mimetypes
are paper pages with the dog-ear on the big top-left corner and a type band in the category hue.

Each builder returns an Icon: the SVG, the (glyph, plane) pairs and the silhouette bodies that
checks.py holds to the contrast rules."""
from dataclasses import dataclass, field

import card
from app_glyphs import W, WD, arc_d, keyhole_d
from palette import CAT, INK, PAPER, contrast, deep, glyph_tone, mix


@dataclass
class Icon:
    name: str
    ctx: str
    svg: str
    glyphs: list = field(default_factory=list)     # (label, glyph tone, plane it sits on)
    bodies: list = field(default_factory=list)     # silhouette bodies (body or rim vs both grounds)


# ---- app tiles ----------------------------------------------------------------------------
def app_icon(name, cat, glyph, kit):
    c = CAT[cat]
    body = c["body"]
    fg = glyph_tone(body)
    layers = card.plane(card.card_d(), body, card.card_d(1.6))
    if kit:
        layers += card.kit_band(body)
    svg = card.svg(name, layers, glyph(fg=fg, body=body, tint=c["tint"], pop=c["pop"]))
    return Icon(name, "apps", svg, [("glyph", fg, body)], [body])


# ---- places: folders ---------------------------------------------------------------------
def e_documents(fg, body, tint, pop):
    return (f'<rect x="24" y="27.5" width="16" height="21.5" rx="2" fill="{fg}"/>'
            f'<path d="M27.5 33.5H36.5M27.5 38.5H36.5M27.5 43.5H33" stroke="{body}" stroke-width="{WD}"/>')


def e_download(fg, body, tint, pop):
    return (f'<path d="M32 27.5V42M26 36.5L32 42.5L38 36.5" fill="none" stroke="{fg}" stroke-width="{W}"/>'
            f'<path d="M23 48.5H41" stroke="{fg}" stroke-width="{W}"/>')


def e_music(fg, body, tint, pop):
    return (f'<circle cx="32" cy="38.5" r="10.5" fill="{fg}"/>'
            f'<circle cx="32" cy="38.5" r="7.2" fill="none" stroke="{tint}" stroke-width="1.4"/>'
            f'<circle cx="32" cy="38.5" r="3.6" fill="{pop}"/><circle cx="32" cy="38.5" r="1.1" fill="{fg}"/>')


def e_pictures(fg, body, tint, pop):
    return (f'<rect x="21" y="29" width="22" height="19" rx="2.2" fill="{fg}"/>'
            f'<path d="M23.5 46L29.5 37.5L33.8 42L36.8 39L40.5 46Z" fill="{body}"/>'
            f'<circle cx="37.5" cy="33.6" r="2.4" fill="{pop}"/>')


def e_publicshare(fg, body, tint, pop):
    return (f'<path d="{arc_d(32, 34, 9.5, 205, 245)}" fill="none" stroke="{tint}" stroke-width="{WD}"/>'
            f'<path d="{arc_d(32, 34, 9.5, 295, 335)}" fill="none" stroke="{tint}" stroke-width="{WD}"/>'
            f'<circle cx="32" cy="34" r="4.4" fill="{fg}"/>'
            f'<path d="M23.5 49a8.5 8.2 0 0 1 17 0z" fill="{fg}"/>')


def e_templates(fg, body, tint, pop):
    return (f'<rect x="26.5" y="27.5" width="17" height="17" rx="2" fill="{tint}"/>'
            f'<rect x="20.5" y="32" width="17" height="17" rx="2" fill="{fg}"/>'
            f'<path d="M24.5 37.5H33.5M24.5 42.5H30" stroke="{body}" stroke-width="{WD}"/>')


def e_videos(fg, body, tint, pop):
    return (f'<rect x="20.5" y="29.5" width="23" height="18" rx="3" fill="{fg}"/>'
            f'<path d="M29 33.6L37 38.5L29 43.4Z" fill="{body}" stroke="{body}" stroke-width="1.2"/>')


def e_desktop(fg, body, tint, pop):
    return (f'<rect x="20" y="28" width="24" height="16.5" rx="2.5" fill="{fg}"/>'
            f'<rect x="23.2" y="31.2" width="17.6" height="10.1" rx="1" fill="{tint}"/>'
            f'<path d="M32 44.5V48.5M26 49H38" stroke="{fg}" stroke-width="3"/>')


def e_home(fg, body, tint, pop):
    return (f'<path d="M32 27.5L43.5 37.5V48.5H20.5V37.5Z" fill="{fg}" stroke="{fg}" stroke-width="2"/>'
            f'<path d="{keyhole_d(32, 38.6, 0.72)}" fill="{body}"/>')


def e_globe(fg, body, tint, pop):
    return (f'<circle cx="32" cy="38.5" r="10.5" fill="{fg}"/>'
            f'<ellipse cx="32" cy="38.5" rx="4.2" ry="10.5" fill="none" stroke="{body}" stroke-width="2"/>'
            f'<path d="M22.5 38.5H41.5" stroke="{body}" stroke-width="2"/>')


FOLDERS = [
    ("folder", "files", None),
    ("folder-documents", "files", e_documents),
    ("folder-download", "files", e_download),
    ("folder-music", "files", e_music),
    ("folder-pictures", "files", e_pictures),
    ("folder-publicshare", "files", e_publicshare),
    ("folder-templates", "files", e_templates),
    ("folder-videos", "files", e_videos),
    ("user-desktop", "files", e_desktop),
    ("user-home", "files", e_home),
    ("network-workgroup", "web", e_globe),
]


def folder_icon(name, cat, emblem):
    c = CAT[cat]
    body = c["body"]
    back = deep(body)
    layers = (card.plane(card.folder_back_d(), back) +
              f'<rect x="11" y="16" width="42" height="14" rx="2" fill="{c["tint"]}"/>' +
              card.plane(card.folder_front_d(), body, card.folder_front_d(1.6)))
    glyph = emblem(fg=PAPER, body=body, tint=c["tint"], pop=c["pop"]) if emblem else ""
    pairs = [("emblem", PAPER, body)] if emblem else []
    return Icon(name, "places", card.svg(name, layers, glyph), pairs, [body, back])


def trash_icon(name, full):
    c = CAT["system"]
    body = c["body"]
    clip = card.basket_d(3.0)
    weave = "".join(f'<path d="M{x} 18L{x + 34} 58M{x + 34} 18L{x} 58" stroke="{c["tint"]}" stroke-width="2"/>'
                    for x in (-2, 8, 18, 28))
    paper = ""
    if full:
        crease = mix(PAPER, INK, .4)
        paper = (f'<path d="M15.5 16.5a8.5 8 0 0 1 17-1.5l.5 2H15.5z" fill="{PAPER}" stroke="{crease}" stroke-width="1"/>'
                 f'<path d="M19 13.5l3.5 2.5 3-3.5 3 3" fill="none" stroke="{crease}" stroke-width="1.5"/>'
                 f'<path d="M30.5 16.5a9.5 9 0 0 1 19 0z" fill="{c["tint"]}" stroke="{mix(c["tint"], INK, .35)}" stroke-width="1"/>'
                 f'<path d="M35 13l4 2.5 3.5-3 3 2.5" fill="none" stroke="{mix(c["tint"], INK, .45)}" stroke-width="1.5"/>')
    layers = (card.plane(card.basket_d(), body, card.basket_d(1.6)) +
              f'<clipPath id="weave"><path d="{clip}"/></clipPath><g clip-path="url(#weave)" stroke-linecap="round">{weave}</g>')
    glyph = paper + f'<rect x="7" y="14.5" width="50" height="6" rx="3" fill="{PAPER}" stroke="{mix(body, "#000000", .3)}" stroke-width="1"/>'
    return Icon(name, "places", card.svg(name, layers, glyph), [("weave", c["tint"], body), ("lip", PAPER, body)], [body])


# ---- devices ------------------------------------------------------------------------------
def disk_icon():
    c = CAT["dev"]
    body = c["body"]
    d = card.slab_d(6, 16, 58, 50)
    layers = card.plane(d, body, card.slab_d(6, 16, 58, 50, inset=1.6))
    glyph = (f'<path d="M13 26H51" stroke="{c["tint"]}" stroke-width="{WD}"/>'
             f'<rect x="13" y="34" width="25" height="7.5" rx="3" fill="{PAPER}"/>'
             f'<circle cx="49" cy="38" r="3" fill="{c["pop"]}"/>')
    return Icon("drive-harddisk", "devices", card.svg("drive-harddisk", layers, glyph), [("label", PAPER, body)], [body])


def stick_icon():
    c = CAT["dev"]
    body = c["body"]
    plug = card.rrect4(23, 6, 41, 21, 3, 3, 0, 0)
    d = card.slab_d(16, 18, 48, 58, big=9, small=3.5)
    layers = (card.plane(plug, c["tint"]) +
              f'<rect x="27" y="10" width="3.5" height="3.5" rx=".8" fill="{body}"/>'
              f'<rect x="33.5" y="10" width="3.5" height="3.5" rx=".8" fill="{body}"/>' +
              card.plane(d, body, card.slab_d(16, 18, 48, 58, big=9, small=3.5, inset=1.6)))
    glyph = (f'<rect x="22" y="28" width="20" height="15" rx="3" fill="{PAPER}"/>'
             f'<path d="M26 33.5H38M26 38H33" stroke="{body}" stroke-width="{WD}"/>'
             f'<circle cx="32" cy="50.5" r="2.6" fill="{c["pop"]}"/>')
    return Icon("drive-removable-media", "devices", card.svg("drive-removable-media", layers, glyph),
                [("label", PAPER, body)], [body, c["tint"]])


# ---- mimetypes ----------------------------------------------------------------------------
def m_pdf(g, c):
    corners = "".join(f'<path d="{p}" fill="none" stroke="{g}" stroke-width="{WD}"/>'
                      for p in ("M20 22V18H24", "M40 18H44V22", "M44 37V41H40", "M24 41H20V37"))
    return corners + f'<path d="M25 24H39M25 29.5H39M25 35H34" stroke="{g}" stroke-width="3"/>'


def m_exec(g, c):
    return (f'<path d="M21 20L29 28.5L21 37" fill="none" stroke="{g}" stroke-width="{W}"/>'
            f'<rect x="32" y="33" width="11" height="4.5" rx="1.2" fill="{c["pop"]}"/>')


def m_generic(g, c):
    return "".join(f'<circle cx="{x}" cy="{y}" r="2.5" fill="{g}"/>' for x in (23, 32, 41) for y in (20.5, 29, 37.5))


def m_audio(g, c):
    return "".join(f'<path d="M{x} {29 - h / 2}V{29 + h / 2}" stroke="{g}" stroke-width="3.5"/>'
                   for x, h in ((20, 6), (26, 14), (32, 20), (38, 12), (44, 5)))


def m_image(g, c):
    return (f'<rect x="19" y="17" width="26" height="23" rx="2.5" fill="{c["tint"]}"/>'
            f'<path d="M19 40L27 29L33 35.5L36.5 31.5L45 40Z" fill="{g}"/>'
            f'<circle cx="38.5" cy="23.5" r="3" fill="{c["pop"]}"/>')


def m_package(g, c):
    return (f'<rect x="19.5" y="21" width="25" height="19" rx="2" fill="{c["tint"]}" stroke="{g}" stroke-width="3"/>'
            f'<path d="M19.5 27H44.5" stroke="{g}" stroke-width="3"/>'
            f'<rect x="29" y="19.5" width="6" height="11" rx="1" fill="{c["pop"]}"/>')


def m_text(g, c):
    return f'<path d="M20 19H44M20 25H44M20 31H39M20 37H44M20 43H32" stroke="{g}" stroke-width="{WD + .5}"/>'


def m_video(g, c):
    return (f'<rect x="19" y="18" width="26" height="21" rx="3.5" fill="{g}"/>'
            f'<path d="M28.5 23.5L37.5 28.5L28.5 33.5Z" fill="{PAPER}" stroke="{PAPER}" stroke-width="1.2"/>')


def m_document(g, c):
    return (f'<path d="M20 19.5H33" stroke="{g}" stroke-width="{W}"/>'
            f'<path d="M20 27H44M20 32.5H44M20 38H37" stroke="{g}" stroke-width="{WD}"/>')


def m_spreadsheet(g, c):
    return (f'<rect x="19" y="18" width="26" height="23" rx="2" fill="{c["tint"]}"/>'
            f'<rect x="19" y="18" width="26" height="6" rx="2" fill="{g}"/>'
            f'<path d="M27.7 24V41M36.3 24V41M19 29.7H45M19 35.3H45" stroke="{g}" stroke-width="1.8"/>'
            f'<rect x="19" y="18" width="26" height="23" rx="2" fill="none" stroke="{g}" stroke-width="{WD}"/>')


def m_presentation(g, c):
    return (f'<rect x="18" y="17" width="28" height="18" rx="2.5" fill="{g}"/>'
            f'<path d="M24 30V27M30 30V23.5M36 30V25.5" stroke="{PAPER}" stroke-width="3"/>'
            f'<path d="M32 35V41M26.5 42L32 37L37.5 42" fill="none" stroke="{g}" stroke-width="{WD}"/>')


MIMES = [
    ("application-pdf", "talk", m_pdf),
    ("application-x-executable", "dev", m_exec),
    ("application-x-generic", "system", m_generic),
    ("audio-x-generic", "wolos", m_audio),
    ("image-x-generic", "media", m_image),
    ("package-x-generic", "store", m_package),
    ("text-x-generic", "files", m_text),
    ("video-x-generic", "web", m_video),
    ("x-office-document", "web", m_document),
    ("x-office-presentation", "media", m_presentation),
    ("x-office-spreadsheet", "files", m_spreadsheet),
]


def page_tone(body):
    """The glyph on paper: the category hue when it holds 3:1 on paper, else ink."""
    return body if contrast(body, PAPER) >= 3.0 else INK


def mime_icon(name, cat, glyph):
    c = CAT[cat]
    g = page_tone(c["body"])
    ear = mix(PAPER, INK, 0.14)
    layers = (card.plane(card.page_d(), PAPER, card.page_d(1.6)) +
              f'<clipPath id="page"><path d="{card.page_d(0.5)}"/></clipPath>'
              f'<rect x="13" y="47" width="38" height="11" fill="{c["body"]}" clip-path="url(#page)"/>'
              f'<path d="{card.page_ear_d()}" fill="{ear}" stroke="{mix(ear, "#000000", .3)}" stroke-width="1"/>')
    return Icon(name, "mimetypes", card.svg(name, layers, glyph(g, c)), [("glyph", g, PAPER)], [PAPER])


def all_icons():
    from app_glyphs import APPS
    out = [app_icon(*a) for a in APPS]
    out += [folder_icon(*f) for f in FOLDERS]
    out += [trash_icon("user-trash", False), trash_icon("user-trash-full", True)]
    out += [disk_icon(), stick_icon()]
    out += [mime_icon(*m) for m in MIMES]
    return out
