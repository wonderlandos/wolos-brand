# SPDX-License-Identifier: GPL-2.0-or-later
"""Colour arithmetic for the east calculus: sRGB <-> OKLab/OKLCH, gamut fit, WCAG contrast,
and the five-element classification. Stdlib only."""
import math


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb2hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02X}" for v in c)


def _lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _gam(v):
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def rgb2oklab(c):
    r, g, b = (_lin(v) for v in c)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab2rgb_lin(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def oklch(c):
    L, a, b = rgb2oklab(hex2rgb(c) if isinstance(c, str) else c)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def from_oklch(L, C, h):
    """sRGB hex of oklch(L C h); chroma is reduced (hue and lightness kept) until it is in gamut."""
    lo, hi = 0.0, C
    for _ in range(40):
        a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
        rgb = oklab2rgb_lin(L, a, b)
        if all(-1e-6 <= v <= 1 + 1e-6 for v in rgb):
            if C == hi:
                break
            lo = C
        else:
            hi = C
        C = (lo + hi) / 2 if hi - lo > 1e-5 else lo
        if hi - lo <= 1e-5:
            a, b = lo * math.cos(math.radians(h)), lo * math.sin(math.radians(h))
            rgb = oklab2rgb_lin(L, a, b)
            break
    return rgb2hex(tuple(_gam(max(0.0, min(1.0, v))) for v in rgb))


def lum(c):
    r, g, b = (_lin(v) for v in (hex2rgb(c) if isinstance(c, str) else c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


# ---- five elements (wuxing) ----
# Generating cycle (sheng): Wood -> Fire -> Earth -> Metal -> Water -> Wood.
# Overcoming cycle (ke):    Wood -> Earth -> Water -> Fire -> Metal -> Wood.
ELEMENTS = ("wood", "fire", "earth", "metal", "water")
SHENG = {("wood", "fire"), ("fire", "earth"), ("earth", "metal"), ("metal", "water"), ("water", "wood")}
KE = {("wood", "earth"), ("earth", "water"), ("water", "fire"), ("fire", "metal"), ("metal", "wood")}


def element(c, base_hue=None):
    """Element of a colour, as a one-element frozenset. Violet (zi) is the intermediate colour of
    the north (black over cinnabar), and the north is water: zi counts as water. Low-chroma
    colours are white/metal (light) or black/water (dark), whatever their tint."""
    L, C, h = oklch(c) if isinstance(c, (str, tuple)) else c
    if C < 0.035:
        return frozenset({"metal"}) if L > 0.55 else frozenset({"water"})
    if 130 <= h < 215:
        return frozenset({"wood"})
    if 215 <= h < 330:
        return frozenset({"water"})        # azurite blue to violet (zi)
    if 55 <= h < 130:
        return frozenset({"earth"})
    return frozenset({"fire"})  # 330..360, 0..55: rose, cinnabar, tangerine


def _hd(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def rel1(a, b):
    if a == b:
        return "same"
    if (a, b) in SHENG or (b, a) in SHENG:
        return "sheng"
    return "ke"


def relation(ea, eb):
    """'same' | 'sheng' | 'ke' between two element sets ('mixed' only for multi-element sets)."""
    if ea == eb:
        return "same"
    rs = {rel1(x, y) for x in ea for y in eb}
    if "ke" not in rs:
        return "sheng" if "sheng" in rs else "same"
    return "mixed" if ("sheng" in rs or "same" in rs) else "ke"
