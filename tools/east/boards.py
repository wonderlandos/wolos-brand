# SPDX-License-Identifier: GPL-2.0-or-later
"""Every east board in one run: python3 -I design/tools/east/boards.py OUTDIR
Writes the PNG boards and scores.json (all score tables)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import board as B  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
WT = os.path.normpath(os.path.join(D, ".."))
LIGHT, DARK = "#F1F1FA", "#15151D"


def j(*p):
    return os.path.join(D, *p)


def marks(out):
    rows = [
        ("Stack, light: WolOS over ウォルOS", j("brand", "wolos-wordmark-ja-boot.svg"), j("east", "marks", "wolos-mark-east.svg"), "mark", "#FFFFFF", None, None),
        ("Stack, dark", j("brand", "wolos-wordmark-ja-boot-dark.svg"), j("east", "marks", "wolos-mark-east-dark.svg"), "mark", DARK, None, None),
        ("Lockup: door + letters", j("brand", "wolos-wordmark.svg"), j("east", "marks", "wolos-lockup-east.svg"), "mark", "#FFFFFF", None, None),
        ("Lockup, dark", j("brand", "wolos-wordmark-dark.svg"), j("east", "marks", "wolos-lockup-east-dark.svg"), "mark", DARK, None, None),
        ("Boot splash 1920x1080", j("brand", "wolos-boot-ja.svg"), j("east", "marks", "wolos-boot-east.svg"), "screen", DARK, None, None),
        ("Release lockup 0.13 Qíjiā, light", None, j("east", "marks", "wolos-0.13-qijia-east.svg"), "mark", LIGHT, None, None),
        ("Release lockup 0.13 Qíjiā, dark", None, j("east", "marks", "wolos-0.13-qijia-east-dark.svg"), "mark", DARK, None, None),
    ]
    return B.rows_board("East marks: WolOS with ウォルOS in the zucai stack (15 + 2 + 4 fen)",
                        "The letters are the cai (15 fen), the katakana line is the zhi under them (2 fen gap, 4 fen ink), "
                        "tracked by equal ink gaps to 2/3 of the letters' width. Door mark 21 fen tall, 6 fen away.",
                        rows, os.path.join(out, "marks-current-vs-east.png"))




def wallpapers(out):
    rows = [("Wallpaper, day", j("wallpapers", "wonderland-day.svg"), j("east", "wallpapers", "east-courtyard-day.svg"), "wallpaper", "#FFFFFF", None, None),
            ("Wallpaper, night", j("wallpapers", "wonderland-night.svg"), j("east", "wallpapers", "east-moon-gate-night.svg"), "wallpaper", "#000000", None, None)]
    return B.rows_board("East wallpapers: shanshui in three planes, one light, the river as the qi path",
                        "Entry = the light at the upper left; the river turns twice and lands in the pool at the lit door "
                        "(lower right third); the mountain anchors the lower left; the calm middle is left for windows.",
                        rows, os.path.join(out, "wallpapers-current-vs-east.png"), width=760)


def main(argv):
    out = argv[0]
    what = argv[1:] or ["marks"]
    res = {}
    path = os.path.join(out, "scores.json")
    if os.path.exists(path):
        res = json.load(open(path))
    for w in what:
        res[w] = globals()[w](out)
        for k, v in res[w].items():
            a = v["current"]["total"] if v["current"] else None
            print(f"{w:10s} {k:40s} {a!s:>6} -> {v['east']['total']:5.1f}")
    json.dump(res, open(path, "w"), indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv[1:])
