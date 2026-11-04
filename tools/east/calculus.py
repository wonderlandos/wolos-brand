# SPDX-License-Identifier: GPL-2.0-or-later
"""The east design calculus (docs/adr/brand-east.md): the numbers every east drawing and the
scorer share. Stdlib only.

Proportion
  Module: the Yingzao fashi (Li Jie, 1103) measures a building in fen, the 1/15 part of the
  height of the standard timber section (cai). Its named sections, in fen:
      cai  15 high x 10 wide     zhi (filler block) 6 high x 4 wide     zucai = cai + zhi = 21
  Here 1 fen = U = 4 px (0.25 rem). NAMED holds the lengths drawn from those sections; any other
  whole number of fen is on the module but unnamed.
  Door-light ruler (menguang chi, the Lu Ban ruler): 1.44 chi long, eight bands of 0.18 chi:
      cai (wealth) bing (illness) li (parting) yi (duty) guan (office) jie (loss) hai (harm) ben (root)
  Openings (doors, windows) were sized so that each dimension, taken modulo the ruler, ends in
  cai, yi, guan or ben. Here the ruler is 144 fen (576 px) and a band 18 fen (72 px).
Light: one source, upper left, steep (the eye and the light come in through the same gate).
Palette: the five elements (wuxing) with the base violet as zi, the northern intermediate colour
  (water). See colour.py for the relations; the derivation is east_palette() below.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from colour import from_oklch, oklch, contrast  # noqa: E402

U = 4                      # px per fen
REM = 16                   # px per rem
CAI, CAI_W, ZHI, ZHI_W = 15, 10, 6, 4
ZUCAI = CAI + ZHI          # 21
NAMED = (1, 2, 3, ZHI_W, ZHI, CAI_W, CAI, ZUCAI, 2 * CAI, 2 * ZUCAI, 4 * CAI, 4 * ZUCAI, 144)
RATIOS = {"1:1": 1.0, "cai 3:2": CAI / CAI_W, "zucai 7:5": ZUCAI / CAI, "2:1": 2.0,
          "zhi 3:2": ZHI / ZHI_W}
RULER = 144                # fen
BANDS = ("cai", "bing", "li", "yi", "guan", "jie", "hai", "ben")
GOOD_BANDS = {"cai", "yi", "guan", "ben"}

# light: unit vector pointing TOWARD the light in image coordinates (x right, y down)
LIGHT = (-1 / math.sqrt(5), -2 / math.sqrt(5))
SHADOW = (1, 2)            # shadow offset direction dx:dy (away from the light)

# density: area shares of ground : second plane : first plane = zucai : cai : zhi
PLANES = (ZUCAI / 42, CAI / 42, ZHI / 42)
ACCENT_SHARE = ZHI / 42    # a ke (overcoming) colour may cover at most 1/7 of a frame


def px(fen):
    return fen * U


def scale_px():
    return [px(n) for n in NAMED]


def band(length_px):
    """Door-light band of a length in px: (name, position 0..1 inside the band)."""
    f = (length_px / U) % RULER
    i = int(f // (RULER / 8))
    return BANDS[i], (f % (RULER / 8)) / (RULER / 8)


def module_fit(length_px, tol=0.5):
    """1.0 on a named length, 0.6 on any whole fen, 0 off the module (tolerance in px)."""
    f = length_px / U
    if any(abs(length_px - px(n)) <= tol for n in NAMED):
        return 1.0
    if abs(f - round(f)) * U <= tol:
        return 0.6
    return 0.0


def ratio_fit(w, h, tol=0.04):
    r = max(w, h) / max(1e-9, min(w, h))
    return 1.0 if any(abs(r - v) / v <= tol for v in RATIOS.values()) else 0.0


# ---- type: line height on the module, size = 2/3 of it (the cai section 10:15) ----
TYPE = {  # role: line height in fen
    "caption": 4, "body": 5, "heading": 6, "title-2": 9, "title": 10, "display": 15}


def type_scale():
    return {k: {"size": round(px(v) * CAI_W / CAI), "line": px(v)} for k, v in TYPE.items()}


# ---- palette ----
BASE = "#7C5CFF"
# Element hue anchors: the traditional mineral pigments (zhongguose table values), OKLCH hue.
PIGMENTS = {"fire": ("zhusha cinnabar", "#FF461F"), "earth": ("tenghuang gamboge", "#FFB61E"),
            "wood": ("shilv malachite", "#16A951"), "water": ("shiqing azurite", "#1685A9")}


def ladder(L0, k):
    """Value ruler: 21 fen from the base to white (k > 0) and 21 fen from the base to black (k < 0)."""
    return L0 + (1 - L0) * k / ZUCAI if k >= 0 else L0 * (1 + k / ZUCAI)


def derive(k, chroma_fen, hue, base=BASE):
    """A colour derived from the base: lightness k fen on the value ruler, chroma as fen of the
    base chroma (21 = the base's own), hue in degrees."""
    L0, C0, _ = oklch(base)
    return from_oklch(ladder(L0, k), C0 * chroma_fen / ZUCAI, hue)


def hue_of(element, base=BASE):
    if element in ("base", "metal"):
        return oklch(base)[2]
    return oklch(PIGMENTS[element][1])[2]


def first_k(pred, ks):
    for k in ks:
        if pred(k):
            return k
    return None


def east_palette(base=BASE):
    """The derived palette. Every colour = derive(k, chroma, hue): value and chroma from the base,
    hue from the base or an element anchor. Returns {name: (hex, formula, element, use)}."""
    L0, C0, h0 = oklch(base)
    out = {}

    def put(name, k, cf, el, use, mode=None):
        hx = derive(k, cf, hue_of(el, base), base)
        out[name] = (hx, f"derive(k={k}, chroma={cf}/21, hue={el})", el, use)
        return hx

    # accent: the base itself where it holds 4.5:1 under white, else the first shade that does
    ka = first_k(lambda k: contrast(derive(k, 21, h0, base), "#FFFFFF") >= 4.5, range(0, -22, -1))
    put("accent", ka, 21, "base", "fills under white text, both modes")
    put("accent-hover", ka - 2, 21, "base", "pressed / hover fill")
    # light neutrals (metal grounds tinted by the base, chroma 1 fen)
    put("light.bg", 19, 1, "base", "ground")
    put("light.surface", 21, 0, "base", "cards")
    put("light.surface-2", 18, 1, "base", "second plane")
    put("light.text", -14, 2, "base", "text (water)")
    put("light.text-2", -5, 2, "base", "secondary text")
    kt = first_k(lambda k: contrast(derive(k, 21, h0, base), derive(19, 1, h0, base)) >= 4.5,
                 range(0, -22, -1))
    put("light.accent-text", kt, 21, "base", "accent as text on the ground")
    # dark neutrals (water grounds)
    put("dark.bg", -14, 1.5, "base", "ground")
    put("dark.surface", -11, 1.5, "base", "cards")
    put("dark.surface-2", -9, 1.5, "base", "second plane")
    put("dark.text", 20, 0.5, "base", "text (metal)")
    put("dark.text-2", 9, 1, "base", "secondary text")
    kd = first_k(lambda k: contrast(derive(k, 21, h0, base), derive(-11, 1.5, h0, base)) >= 4.5,
                 range(0, 22))
    put("dark.accent-text", kd, 21, "base", "accent as text on dark surfaces")
    # elements: wood is the companion (water feeds wood), fire and earth are accents (ke)
    put("wood", 0, 14, "wood", "companion: may neighbour the base at any area (sheng)")
    put("wood-tint", 14, 8, "wood", "companion tint")
    put("water", -2, 14, "water", "kin of the base (same element)")
    put("fire", -1, 15, "fire", "accent only (water overcomes fire): <= 1/7 of a frame")
    put("earth", 15, 14, "earth", "accent only (earth overcomes water): the gold pop")
    put("earth-deep", 4, 15, "earth", "earth on light grounds (borders, icons)")
    put("metal", 21, 0, "metal", "white: mother of water (sheng)")
    return out
