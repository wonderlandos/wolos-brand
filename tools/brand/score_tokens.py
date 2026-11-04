# SPDX-License-Identifier: GPL-2.0-or-later
"""Score a token file against the brand calculus: the current colors.json and the brand proposal.

  python3 -I design/tools/brand/score_tokens.py [FILE.json ...]   (default: both, side by side)

Token-level rules (0-100 each; flow needs a layout, so it is scored on mocks, not here):
  proportion  every px length (space, radius, size, type line) on the fen module (named = 1,
              whole fen = 0.6); type size = 2/3 of its line (the cai section 10:15)
  palette     contrast floors (accent-fg on accent 4.5, text 7, text-2 4.5, accent as text 4.5,
              both modes); neutrals on the base hue (+-6 deg); large surfaces same/sheng with
              the accent; ke colours never a large surface
  light       a light direction is declared and shadows/elevations follow it (dx:dy = 1:2)
  density     planes bg / surface-2 / surface are distinct steps (dL >= 0.015) and the spacing
              scale grows by gentle steps (ratio 1.3..2.0 after 16 px)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calculus as K  # noqa: E402
from colour import contrast, element, oklch, relation  # noqa: E402

TOK = os.path.normpath(os.path.join(HERE, "..", "..", "tokens"))
HIG_SPACE = [4, 8, 12, 16, 24, 32]          # docs/modules/hig.md section 2 (current tokens carry none)
HIG_TYPE = {"secondary": (11, None), "body": (13, None), "heading": (15, None), "empty": (22, None), "title": (26, None)}
HIG_SIZE = {"toolbar": 36, "sidebar": 220, "sidebar-item": 28, "status-bar": 24, "content-max": 680}


def pxs(v):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)px", str(v))
    return float(m.group(1)) if m else None


def solid(v):
    return v if isinstance(v, str) and v.startswith("#") else None


def score(t):
    notes = {}
    # ---- proportion
    lens = []
    space = [pxs(v) for v in t.get("space", {}).values()] or HIG_SPACE
    lens += space
    lens += [x for x in (pxs(v) for v in t.get("radius", {}).values()) if x]
    sizes = {k: pxs(v) for k, v in t.get("size", {}).items()} or HIG_SIZE
    lens += list(sizes.values())
    typ = t.get("type")
    tfit = []
    if typ:
        for k, v in typ.items():
            s, l = pxs(v["size"]), pxs(v["line"])
            lens.append(l)
            tfit.append(1.0 if abs(s - l * 2 / 3) <= 0.7 else 0.0)
    else:
        tfit = [0.0] * len(HIG_TYPE)      # no line heights declared: the 2/3 rule cannot hold
    mod = sum(K.module_fit(x) for x in lens) / len(lens)
    prop = 100 * (0.7 * mod + 0.3 * (sum(tfit) / len(tfit)))
    notes["proportion"] = {"lengths": len(lens), "on_module": round(mod, 2), "type_2_3": f"{sum(tfit):.0f}/{len(tfit)}",
                           "off": sorted({x for x in lens if K.module_fit(x) == 0})}
    # ---- palette
    checks = []
    h0 = oklch(K.BASE)[2]
    for mode in ("light", "dark"):
        m = t[mode]
        acc = m["accent"]
        checks.append(("accent-fg/accent " + mode, contrast(m["accent-fg"], acc), 4.5))
        checks.append(("text/bg " + mode, contrast(m["text"], m["bg"]), 7.0))
        for g in ("bg", "surface", "surface-2"):
            checks.append((f"text-2/{g} {mode}", contrast(m["text-2"], m[g]), 4.5))
        at = m.get("accent-text", acc)
        checks.append(("accent as text/surface " + mode, contrast(at, m["surface"]), 4.5))
    ok = [c for c in checks if c[1] >= c[2]]
    hue_ok = []
    for mode in ("light", "dark"):
        for k in ("bg", "surface-2", "text", "text-2"):
            L, C, h = oklch(t[mode][k])
            d = min(abs(h - h0) % 360, 360 - abs(h - h0) % 360)
            hue_ok.append(C < 0.003 or d <= 6)
    rel_ok = []
    for mode in ("light", "dark"):
        ea = element(t[mode]["accent"])
        for k in ("bg", "surface", "surface-2"):
            rel_ok.append(relation(element(t[mode][k]), ea) in ("same", "sheng"))
    pal = 100 * (0.6 * len(ok) / len(checks) + 0.2 * sum(hue_ok) / len(hue_ok) + 0.2 * sum(rel_ok) / len(rel_ok))
    notes["palette"] = {"contrast_pass": f"{len(ok)}/{len(checks)}",
                        "fails": [(n, round(v, 2), f) for n, v, f in checks if v < f],
                        "neutrals_on_base_hue": f"{sum(hue_ok)}/{len(hue_ok)}"}
    # ---- light
    ls = t.get("light-source")
    el = t.get("elevation")
    if not ls:
        light = 40.0
        notes["light"] = "no light direction declared (shadows are colour only)"
    else:
        agree = []
        for e in (el or {}).values():
            dx, dy = e["offset"]
            agree.append(abs(dx / dy - K.SHADOW[0] / K.SHADOW[1]) < 0.05)
        light = 60 + 40 * (sum(agree) / len(agree) if agree else 0)
        notes["light"] = f"declared {ls['from']}; elevations agree {sum(agree)}/{len(agree)}"
    # ---- density
    dist = []
    for mode in ("light", "dark"):
        Ls = sorted(oklch(t[mode][k])[0] for k in ("bg", "surface", "surface-2"))
        dist.append(all(b - a >= 0.015 for a, b in zip(Ls, Ls[1:])))
    sp = sorted(space)
    steps = [b / a for a, b in zip(sp, sp[1:]) if a >= 16]
    gentle = sum(1.3 <= r <= 2.0 for r in steps) / len(steps) if steps else 0.0
    dens = 100 * (0.5 * sum(dist) / len(dist) + 0.5 * gentle)
    notes["density"] = {"planes_distinct": f"{sum(dist)}/2", "space_steps": [round(r, 2) for r in steps]}
    out = {"proportion": round(prop, 1), "palette": round(pal, 1), "light": round(light, 1), "density": round(dens, 1)}
    out["total"] = round(sum(out.values()) / 4, 1)
    return out, notes


def main(argv):
    files = argv or [os.path.join(TOK, "colors.json"), os.path.join(TOK, "tokens-brand.json")]
    res = {}
    for f in files:
        res[os.path.basename(f)] = score(json.load(open(f)))
    names = list(res)
    print(f"{'rule':12s}" + "".join(f"{n:>20s}" for n in names))
    for r in ("proportion", "palette", "light", "density", "total"):
        print(f"{r:12s}" + "".join(f"{res[n][0][r]:20.1f}" for n in names))
    for n in names:
        print(f"\n{n}:")
        for k, v in res[n][1].items():
            print(f"  {k}: {v}")
    if "--json" in os.environ.get("BRAND_JSON", ""):
        print(json.dumps(res))


if __name__ == "__main__":
    main(sys.argv[1:])
