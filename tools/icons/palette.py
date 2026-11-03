# SPDX-License-Identifier: GPL-2.0-or-later
"""Colour of the Wonderland card: the icon palette from design/tokens/colors.json (written by
tools/tokens.py), WCAG contrast, and the two derived tones every card uses (glyph tone, rim)."""
import json
import os

DESIGN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ICON = json.load(open(os.path.join(DESIGN, "tokens", "colors.json"), encoding="utf-8"))["icon"]

PAPER = ICON["paper"]            # glyph tone on dark or saturated bodies (warm, never pure white)
INK = ICON["ink"]                # glyph tone on bright bodies, and the dev body
GROUND_LIGHT = ICON["ground-light"]
GROUND_DARK = ICON["ground-dark"]
CAT = ICON["categories"]         # category -> {body, tint, pop}

GLYPH_MIN = 3.0   # glyph primary against its plane (WCAG 1.4.11 non-text)
EDGE_MIN = 1.8    # body or rim against each ground


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def tohex(t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(v))) for v in t)


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tohex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in hx(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def glyph_tone(body):
    """Paper on dark bodies, ink on bright ones: whichever contrasts more."""
    return PAPER if contrast(PAPER, body) >= contrast(INK, body) else INK


def rim(body):
    """The 1-unit hairline: the body darkened 30%, or lightened 28% when it is near-black."""
    return mix(body, "#FFFFFF", 0.28) if lum(body) < 0.03 else mix(body, "#000000", 0.30)


def deep(body, t=0.24):
    """A second flat plane behind the body (folder back): darker, or lighter on near-black."""
    return mix(body, "#FFFFFF", t) if lum(body) < 0.03 else mix(body, "#000000", t)
