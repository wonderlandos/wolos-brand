# SPDX-License-Identifier: GPL-2.0-or-later
"""Per-theme icon sets in Type A2 (docs/adr/brand-east.md section 8): the same geometry, a palette
derived from each theme's own base colour with calculus.derive().

  python3 -I design/tools/east/themesets.py [THEME ...] [--no-score] [--only-board]

Themes are the built-ins of crates/core/src/theme/builtin/*.json (the theme's `accent` is its base
colour). The base the calculus sees keeps the default base's lightness (so every value-ruler step,
every white-on-card contrast and every shadow rule holds unchanged) and takes the accent's hue and
chroma (chroma clamped to 0.06..0.23: a grey theme still gets a hint of hue, a neon one stays in
gamut). The element hues (cinnabar, gamboge, malachite, azurite) are the calculus' own and do not
move, so gold stays gold and the accents keep their meaning.

Writes east/themesets/<theme>/<app>.svg, small/<app>.svg, board.png and scores.json. One process
per theme (the palette is fixed when types.py is imported: K.BASE is set first)."""
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
D = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(D, "east", "themesets")
THEMES_DIR = os.environ.get("WOLOS_THEMES", "/home/ubuntu/wolos/wt/webapp-int/crates/core/src/theme/builtin")
CHROMA = (0.06, 0.23)
L_THEME = 0.575      # a little under the default base's 0.599: a muted base loses the lit corner, this keeps 16 px at 3:1
FLOOR = 3.5
ACCENT_C = 0.16


def themes():
    r = {}
    for p in sorted(glob.glob(os.path.join(THEMES_DIR, "*.json"))):
        d = json.load(open(p))
        r[d["id"]] = d
    return r


def theme_base(accent):
    """The base the calculus runs on for a theme: default lightness, the accent's hue and chroma."""
    from colour import oklch, from_oklch
    import calculus as K
    _, c, h = oklch(accent)
    if c < 0.02:                                  # a neutral accent has no hue: keep the default base's
        h = oklch(K.BASE)[2]
    return from_oklch(L_THEME, min(max(c, CHROMA[0]), CHROMA[1]), h)


def _set_base(base):
    import calculus as K
    K.BASE = base
    K.derive.__defaults__ = (base,)
    K.east_palette.__defaults__ = (base,)


def one(theme_id, score=True):
    th = themes()[theme_id]
    base = theme_base(th["tokens"]["accent"])
    _set_base(base)
    import fullset as FS_unused  # noqa: F401  (imports types with the patched base)
    import thirdparty as TP
    TP.FLOOR = FLOOR
    TP.CARDS.update(TP.cards())
    FS, T = TP.FS, TP.T
    # The accents (gold, cinnabar) keep their pop on a muted base: their chroma is not scaled below
    # ACCENT_C (0.16, the default base's 0.23 x 15/21), only their value comes from the base's ladder.
    import calculus as K
    from colour import oklch, from_oklch
    L0, C0, _ = oklch(base)
    ca = max(C0, ACCENT_C * 21 / 15)
    gold = from_oklch(K.ladder(L0, 13), ca * 15 / 21, T.HUE["earth"])
    red = from_oklch(K.ladder(L0, 0), ca * 16 / 21, T.HUE["fire"])
    for m in (T, FS, TP):
        m.GOLD, m.RED = gold, red
    TP.GIMP_CARD = TP.card_of("#8C8073", chroma=7, cap=False)
    tdir = os.path.join(OUT, theme_id)
    os.makedirs(os.path.join(tdir, "small"), exist_ok=True)
    items = []                                     # (group, name, fn)
    items += [("core", "wolos-" + n.lower().replace(" ", "-"), fn) for n, fn in T.A2]
    for b in (1, 2, 3):
        items += [("apps", fn_name, fn) for fn_name, fn in FS.BATCHES[b]]
    items += [("third", a, TP.APPS[a]) for a in TP.APPS]
    names = []
    for grp, n, fn in items:
        for small in (False, True):
            svg = fn(small)
            open(os.path.join(tdir, "small" if small else "", f"{n}.svg"), "w").write(svg)
        names.append((grp, n))
    info = {"id": theme_id, "name": th["name"], "variant": th["variant"], "accent": th["tokens"]["accent"],
            "surface": th["tokens"]["surface"], "base": base, "icons": names}
    if score:
        import board as B
        import craft
        res = {}
        for grp, n in names:
            p = os.path.join(tdir, f"{n}.svg")
            s = B.scored(p, "icon")
            bad = []
            for q in (p, os.path.join(tdir, "small", f"{n}.svg")):
                bad += [k for k, (ok, _) in craft.check(q).items() if not ok]
            res[n] = {"total": s["total"], "craft": sorted(set(bad)),
                      "rules": {r: s[r]["score"] for r in B.SC.RULES}}
        info["scores"] = res
    json.dump(info, open(os.path.join(tdir, "scores.json"), "w"), indent=1)
    return info


def board(theme_id, out=None):
    """One board per theme: the swatches, the icons at 88 px grouped, the 16 px row, the scores."""
    import board as B
    from PIL import Image, ImageDraw
    tdir = os.path.join(OUT, theme_id)
    info = json.load(open(os.path.join(tdir, "scores.json")))
    sc = info.get("scores", {})
    groups = [("core", "núcleo"), ("apps", "apps"), ("third", "terceiros")]
    cell, per = 100, 11
    pad = 24
    W = pad * 2 + per * cell
    rows = sum((len([1 for g, _ in info["icons"] if g == k]) + per - 1) // per for k, _ in groups)
    H = 150 + rows * (cell + 30) + len(groups) * 34 + 30
    dark = info["variant"] == "dark"
    bg = tuple(int(info["surface"][i:i + 2], 16) for i in (1, 3, 5))
    fg = (235, 235, 240) if dark else (30, 30, 40)
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.text((pad, 14), f"{info['name']}  ({theme_id}, {info['variant']})", font=B.font(24, True), fill=fg)
    for i, (lab, col) in enumerate((("base", info["base"]), ("accent do tema", info["accent"]), ("fundo", info["surface"]))):
        x = pad + i * 150
        d.rounded_rectangle((x, 54, x + 40, 84), 6, fill=col, outline=fg)
        d.text((x + 48, 60), f"{lab}\n{col}", font=B.font(12), fill=fg)
    tot = [v["total"] for v in sc.values()]
    nb = sum(1 for v in sc.values() if v["craft"])
    if tot:
        d.text((pad + 470, 56), f"nota east média {sum(tot) / len(tot):.1f}  (mín {min(tot):.1f}, máx {max(tot):.1f})   craft: {len(tot) - nb} de {len(tot)} ok", font=B.font(16, True), fill=fg)
    y = 110
    for k, label in groups:
        ns = [n for g, n in info["icons"] if g == k]
        d.text((pad, y), label, font=B.font(16, True), fill=fg)
        y += 30
        for j, n in enumerate(ns):
            x = pad + (j % per) * cell
            yy = y + (j // per) * (cell + 30)
            r = B.raster(os.path.join(tdir, f"{n}.svg"), 88, 88)
            im.paste(r, (x + 4, yy), r)
            if n in sc:
                d.text((x + 6, yy + 90), f"{sc[n]['total']:.0f}" + ("  !" if sc[n]["craft"] else ""), font=B.font(11), fill=fg)
        y += ((len(ns) + per - 1) // per) * (cell + 30) + 4
    # the 16 px and 32 px rows
    ns = [n for _, n in info["icons"]]
    x = pad
    for n in ns[:46]:
        for sz in (16,):
            t = B.raster(os.path.join(tdir, "small", f"{n}.svg"), sz, sz)
            im.paste(t, (x, H - 24), t)
            x += 20
    out = out or os.path.join(tdir, "board.png")
    im.save(out)
    return out


def main(argv):
    allt = themes()
    names = [a for a in argv if not a.startswith("--")] or list(allt)
    if "--one" in argv:
        one(names[0], "--no-score" not in argv)
        return
    if "--only-board" not in argv:
        from concurrent.futures import ThreadPoolExecutor

        def run(t):
            cmd = [sys.executable, "-I", os.path.abspath(__file__), "--one", t] + (["--no-score"] if "--no-score" in argv else [])
            subprocess.run(cmd, check=True)
            return t
        with ThreadPoolExecutor(max_workers=min(len(names), os.cpu_count() or 4)) as ex:
            list(ex.map(run, names))
    for t in names:
        p = board(t)
        info = json.load(open(os.path.join(OUT, t, "scores.json")))
        sc = info.get("scores", {})
        if sc:
            tot = [v["total"] for v in sc.values()]
            print(f"{t:18s} base {info['base']}  mean {sum(tot) / len(tot):5.1f}  min {min(tot):5.1f}  craft-fail {sum(1 for v in sc.values() if v['craft'])}  {p}")


if __name__ == "__main__":
    main(sys.argv[1:])
