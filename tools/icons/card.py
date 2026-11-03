# SPDX-License-Identifier: GPL-2.0-or-later
"""Silhouettes and lighting of the Wonderland card (.claude/brand/icons-apps/LANGUAGE.md 1-2).

Every full-colour icon is one flat body on the 64 grid, lit the same way: a hard shadow (the
silhouette 1.5 down, black 22%), one light edge (an inset 1.1 line, white 38% at the top, gone by
22% of the height) and a 1-unit rim. No filters (GTK draws them as grey boxes), no gradients on
the body. The card: x/y 6..58, radius 17 on the top-left and bottom-right, 6 on the other two.
Families cut their own silhouette by the same rule (big top-left and bottom-right corners)."""
from palette import ICON, mix, rim

_C = ICON["card"]
X0, Y0, S = float(_C["x"]), float(_C["y"]), float(_C["size"])
RB, RS = float(_C["radius-big"]), float(_C["radius-small"])


def n(v):
    """Short number for path data."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def rrect4(x0, y0, x1, y1, tl, tr, br, bl, inset=0.0):
    """Rounded rectangle with one radius per corner, shrunk by inset (radii shrink with it)."""
    x0, y0, x1, y1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    tl, tr, br, bl = (max(0.0, r - inset) for r in (tl, tr, br, bl))
    return (f"M{n(x0 + tl)} {n(y0)}H{n(x1 - tr)}A{n(tr)} {n(tr)} 0 0 1 {n(x1)} {n(y0 + tr)}"
            f"V{n(y1 - br)}A{n(br)} {n(br)} 0 0 1 {n(x1 - br)} {n(y1)}H{n(x0 + bl)}"
            f"A{n(bl)} {n(bl)} 0 0 1 {n(x0)} {n(y1 - bl)}V{n(y0 + tl)}A{n(tl)} {n(tl)} 0 0 1 {n(x0 + tl)} {n(y0)}Z")


def card_d(inset=0.0):
    return rrect4(X0, Y0, X0 + S, Y0 + S, RB, RS, RB, RS, inset)


# Folder (places): the back plane carries the tab on the RIGHT, a paper sheet sits between the
# planes, the front plane is a card cut wide (corner rule: 14 / 4).
FOLDER_FRONT = (6.0, 21.0, 58.0, 55.0, 13.0, 4.0, 13.0, 4.0)


def folder_front_d(inset=0.0):
    return rrect4(*FOLDER_FRONT, inset=inset)


def folder_back_d():
    return "M6 19A5 5 0 0 1 11 14H33.5L38 9.5H53A5 5 0 0 1 58 14.5V40H6Z"


# Page (mimetypes): paper, the dog-ear cut on the big top-left corner, 8 on the bottom-right.
PAGE = (13.0, 6.0, 51.0, 58.0)
EAR = 12.0


def page_d(inset=0.0):
    x0, y0, x1, y1 = (v + d for v, d in zip(PAGE, (inset, inset, -inset, -inset)))
    e = EAR - inset * 0.4
    return (f"M{n(x0 + e)} {n(y0)}H{n(x1 - 3)}A3 3 0 0 1 {n(x1)} {n(y0 + 3)}V{n(y1 - 8)}A8 8 0 0 1 {n(x1 - 8)} {n(y1)}"
            f"H{n(x0 + 3)}A3 3 0 0 1 {n(x0)} {n(y1 - 3)}V{n(y0 + e)}Z")


def page_ear_d():
    x0, y0 = PAGE[0], PAGE[1]
    return f"M{n(x0 + EAR)} {n(y0)}V{n(y0 + EAR - 2.5)}A2.5 2.5 0 0 1 {n(x0 + EAR - 2.5)} {n(y0 + EAR)}H{n(x0)}Z"


# Devices: a slab (the card's corner rule, flatter).
def slab_d(x0, y0, x1, y1, big=10.0, small=4.0, inset=0.0):
    return rrect4(x0, y0, x1, y1, big, small, big, small, inset)


# Trash: a wastepaper basket, open at the top (no lid, no slots), splayed walls.
def basket_d(inset=0.0):
    i = inset
    return (f"M{n(10 + i)} {n(17 + i)}H{n(54 - i)}L{n(48.5 - i)} {n(51.5 - i * 0.6)}"
            f"A6 6 0 0 1 {n(42.6 - i * 0.5)} {n(56.5 - i)}H{n(21.4 + i * 0.5)}A6 6 0 0 1 {n(15.5 + i)} {n(51.5 - i * 0.6)}Z")


EDGE_GRADIENT = ('<linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.38"/>'
                 '<stop offset="0.22" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>')


def plane(d, body, d_inset=None, shadow=True):
    """One lit plane: hard shadow, flat body with its rim, the light edge on the inset outline."""
    out = []
    if shadow:
        out.append(f'<path d="{d}" transform="translate(0 1.5)" fill="#000000" fill-opacity="0.22"/>')
    out.append(f'<path d="{d}" fill="{body}" stroke="{rim(body)}" stroke-width="1"/>')
    if d_inset:
        out.append(f'<path d="{d_inset}" fill="none" stroke="url(#edge)" stroke-width="1.1"/>')
    return "".join(out)


def kit_band(body):
    """Kits: a lid band across the top of the card, one step lighter, with a seam under it."""
    return ('<clipPath id="kit"><path d="' + card_d(0.5) + '"/></clipPath>'
            f'<g clip-path="url(#kit)"><rect x="6" y="6" width="52" height="13" fill="{mix(body, "#FFFFFF", 0.2)}"/>'
            f'<rect x="6" y="19" width="52" height="1.6" fill="{mix(body, "#000000", 0.25)}"/></g>')


def svg(name, layers, glyph):
    """The SVG file: title, the edge gradient, the lit layers, then the glyph (round caps/joins)."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
            f'<title>{name}</title><defs>{EDGE_GRADIENT}</defs>{layers}'
            f'<g stroke-linecap="round" stroke-linejoin="round">{glyph}</g></svg>\n')
