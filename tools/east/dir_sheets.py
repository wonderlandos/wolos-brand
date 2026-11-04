# SPDX-License-Identifier: GPL-2.0-or-later
"""Sheets for the three icon directions: construction, 128/64/32/16, the eight-rule score sheet
and the current icon's total. python3 -I design/tools/east/dir_sheets.py OUTDIR"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import board as B  # noqa: E402
import score as SC  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
CURRENT = {"Settings": os.path.join(D, "icons/apps/wolos-settings.svg"), "Store": os.path.join(D, "icons/apps/wolos-software.svg"),
           "Files": os.path.join(D, "icons/apps/wolos-files.svg"), "Console": os.path.join(D, "icons/apps/wolos-terminal.svg"),
           "Doctor": B.EXTERNAL["Doctor"], "Atlas Folio": B.EXTERNAL["Atlas Folio"]}
TYPES_TEXT = {
    "A-bold": ("Type A, Bold glyph",
               "The grammar the lead pointed to (Alipay, WeChat, Meituan, 12306): a flat saturated card in the app's phase colour "
               "(derived from the base violet), one big white glyph (about 2/3 of the card) with thick rounded strokes, and a "
               "single accent of colour at the landing (gold keyhole, violet keyhole, gold label, jade cursor, cinnabar pulse, "
               "gold you-are-here). The calculus stays quiet: the glyph sits on the 15-fen square, light is only a 1-fen lift "
               "(top-left lighter, contact shadow 1:2), the folder tab is a juzhe slope, and colours follow the five phases.",
               "Self-critique: the most Western-legible and the most familiar of the three, the safest at 16 px. "
               "Its risk is being generic: a mainland app-store look without a WolOS signature beyond the keyhole and the palette."),
    "B-motif": ("Type B, Traditional motif",
                "The same card and the same big glyph, but each glyph grows from a motif in the Chinese iconography lists, with no "
                "hanzi: a gear whose teeth are ruyi cloud heads, a bag sealed with a cash coin (round outside, square hole), a "
                "hand scroll with the owner's seal, the prompt carved in a seal stamp, the longevity peach with a pulse, and the "
                "Folio with a luopan dial as the you-are-here.",
                "Self-critique: a Western eye reads gear, bag, document, terminal, fruit or heart, and map. The motif is a second "
                "reading, not a barrier. Risks: the ruyi gear can read as a flower, and the peach as an apple. "
                "This is the most distinctive of the three without hanzi."),
    "C-jianzhi": ("Type C, Paper-cut (jianzhi)",
                  "A light paper card. The glyph is cut from one sheet of coloured paper, with crescent (yueya) and window cuts "
                  "and the card showing through the cuts, lifted 1 fen with a 1:2 shadow. One material, one light.",
                  "Self-critique: the most craft-like and warm, but the cuts are fine detail that dies at 16-32 px. "
                  "A Western eye may read it as a holiday or folk decoration. Good for the large sizes (Store, About, the site), "
                  "weak as a system icon."),
}
TEXT = {
    "1-wuxing": ("Direction 1, Five shapes (wuxing xing)",
                 "Rule: feng shui gives each phase a form: metal round, wood upright, water curved, fire pointed, earth "
                 "square. Each app takes its phase from its meaning, and the phase sets both its silhouette and its colour, "
                 "derived from the base violet. Settings is metal, so a round coin with a raised eight-direction gear. "
                 "Store is earth, a square carrier with a die-cut slot. Files is wood, an upright folder. Console is water, "
                 "an ink slab with a wave crest (two juzhe slopes). Doctor is fire, the heart (in Chinese medicine the heart "
                 "belongs to fire). Atlas is water, folds that make a wave, each face lit by the way it turns to the light. "
                 "There is no tile: the silhouette itself is the family.",
                 "Self-critique: a Western eye reads the object first, then notices that the outlines differ. The risk is a "
                 "toy shape-sorter feel (circle, square, triangle). Bloat risk is low. Fashion risk is medium: loose "
                 "silhouettes are common on one other desktop, but there the shape is free; here a rule fixes it. "
                 "The weak points are the Files folder, which could pass for a generic document icon, and the Store "
                 "carrier, which could read as a box."),
    "2-strata": ("Direction 2, Strata (jogakbo, layered ramie patches)",
                 "Rule: Korean layered density. Each icon is three to five translucent patches, and every side is a named "
                 "fen length (21, 15, 10, 6, 3). Where patches overlap a third tone appears, so the planes stay visible "
                 "with no outline. The patches step along the qi path, from the upper-left entry to the landing patch, "
                 "which carries the accent element. Light-catching seams run on the upper-left edges. Settings is three "
                 "sliders whose knobs walk the diagonal. Doctor is two crossing patches with the heart where they cross.",
                 "Self-critique: a Western eye reads sliders, a briefcase, stacked sheets and a pharmacy cross: legible, "
                 "but the most generic of the three. The translucency sits close to the glass fashion of the last two "
                 "years, so this one is closest to an existing platform's style. Per the brief it should die unless "
                 "the lead sees something in it. Low bloat."),
    "3-gate": ("Direction 3, Gate (kuangjing, the framed view)",
               "Rule: the WolOS story, a small door with light coming through, built with real Yingzao rules. Every app "
               "is a wall on a plinth: the wall tapers (shoufen, 21 fen at the base, 18 at the top) and wears a juzhe "
               "roof cap with flared eaves. The meaning is cut through the wall as an opening of light: a gear, a bag, "
               "a folder, the prompt, a heart, three map windows. Mountain form for the anchor (wall and plinth), water "
               "form for what flows (the light). The wall colour is the app's phase, derived from the base; the light is "
               "metal-white, the mother of water.",
               "Self-critique: a Western eye may first read 'little house' or 'shrine', then the glyph. Every icon carries "
               "the same wall, which is a frame and a possible bloat, and the glyph is smaller than in 1 (16 px suffers). "
               "No fashion risk; no platform does this. It is the most WolOS of the three: doors and light."),
}


def sheet(dname, out):
    title, why, crit = (TYPES_TEXT | TEXT)[dname]
    names = ["Settings", "Store", "Files", "Console", "Doctor", "Atlas Folio"]
    W, rowh = 1500, 300
    head = 330
    H = head + rowh * len(names) + 40
    im = Image.new("RGB", (W, H), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((40, 26), title + ("  (segunda leva, para escolha)" if dname in TYPES_TEXT else "  (primeira leva)"), font=B.font(28, True), fill=B.INK)
    y = 74
    for para, col in ((why, B.INK), (crit, B.DIM)):
        for line in textwrap.wrap(para, 165):
            dr.text((40, y), line, font=B.font(15), fill=col)
            y += 21
        y += 10
    dr.text((40, head - 30), "256 px" if dname in TYPES_TEXT else "construction: fen grid, light, qi path", font=B.font(14, True), fill=B.DIM)
    dr.text((380, head - 30), "128 / 64 / 32 / 16 px", font=B.font(14, True), fill=B.DIM)
    dr.text((760, head - 30), "score sheet (score.py, 0-100)", font=B.font(14, True), fill=B.DIM)
    table = {}
    for r, name in enumerate(names):
        slug = name.lower().replace(" ", "-")
        y0 = head + r * rowh
        base_dir = "types" if dname in TYPES_TEXT else "directions"
        cons = os.path.join(D, "east", base_dir, dname, "construction", f"wolos-{slug}.svg")
        art = os.path.join(D, "east", base_dir, dname, f"wolos-{slug}.svg")
        if not os.path.exists(cons):
            cons = art
        c = B.raster(cons, 270, 270)
        im.paste(c, (40, y0), c)
        x = 380
        for sz in (128, 64, 32, 16):
            ic = B.raster(art, sz, sz)
            im.paste(ic, (x, y0 + 140 - sz), ic)
            x += sz + 16
        s = B.scored(art, "icon")
        base = B.scored(CURRENT[name], "icon")
        table[name] = {"east": s, "current": base}
        dr.text((380, y0 + 170), name, font=B.font(20, True), fill=B.INK)
        xs = 760
        for i, rule in enumerate(SC.RULES):
            col = xs + (i % 4) * 175
            row = y0 + (i // 4) * 26
            dr.text((col, row), f"{rule}", font=B.font(14), fill=B.DIM)
            dr.text((col + 90, row), f"{s[rule]['score']:5.1f}", font=B.font(14, True), fill=B.INK)
        ok = s["total"] > base["total"]
        dr.text((xs, y0 + 64), f"total {s['total']:.1f}   current icon {base['total']:.1f}   "
                f"{'beats current' if ok else 'BELOW current: stays in the folder'}", font=B.font(16, True),
                fill=B.GOOD if ok else B.BAD)
        why_line = "; ".join(f"{k}: {v['why']}" for k, v in s.items() if k in ("qi", "light") and isinstance(v, dict))
        for j, line in enumerate(textwrap.wrap(why_line, 95)[:3]):
            dr.text((xs, y0 + 96 + j * 18), line, font=B.font(12), fill=B.DIM)
        dr.line((40, y0 + rowh - 12, W - 40, y0 + rowh - 12), fill=B.LINE)
    p = os.path.join(out, f"icons-{'type' if dname in TYPES_TEXT else 'direction'}-{dname}.png")
    im.save(p)
    return p, table


def main(argv):
    out = argv[0]
    res = {}
    for d in (argv[1:] or list(TEXT)):
        p, t = sheet(d, out)
        res[d] = t
        print(p)
        for k, v in t.items():
            print(f"   {k:12s} east {v['east']['total']:5.1f}  current {v['current']['total']:5.1f}")
    name = "icons-types-scores.json" if argv[1:] else "icons-directions-scores.json"
    json.dump(res, open(os.path.join(out, name), "w"), indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv[1:])
