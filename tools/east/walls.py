# SPDX-License-Identifier: GPL-2.0-or-later
"""WolOS 0.13 wallpapers, east (docs/adr/brand-east.md sections 1-7 and 10).

  python3 -I tools/east/walls.py [--out DIR] [--only FORM[,FORM]] [--palette P[,P]] [--size 4k|16x10]

One abstract form per idea, the form fixed and only the palette changing:
  juzhe      roof wings: the raise-and-fold slope, eaves turning back up inside the frame
  luoshu     the nine squares and their dot numbers, walked 1 -> 9 in the magic order
  caifen     the 7:5 module halved into itself, a spiral of zucai rectangles
  shanshui   mountains and water in three planes
  meander    the thunder fret as one continuous ribbon
  moongate   a round door in a lit wall, a branch at the entry
  ruyi       auspicious clouds flowing to one ruyi head
Places (generated, no raster): brasilia, estaiada, cachoeira, rioniteroi, holambra, camposdojordao.

Every colour is calculus.derive(k, chroma fen, element hue) from the base violet. One light at the
upper left (the entry); the qi path turns at least once and lands in the lower-right third; the
centre stays calm. Lengths snap to the fen (4 px); main divisions are named lengths or door bands.
Output: east/wallpapers/<form>-<palette>-<size>.svg.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from walls_lib import *  # noqa: E402,F401,F403
import walls_lib as lib  # noqa: E402
import walls_juzhe  # noqa: E402
import walls_moongate  # noqa: E402
import walls_cachoeira  # noqa: E402
import walls_brasilia  # noqa: E402
import walls_estaiada  # noqa: E402
import walls_rioniteroi  # noqa: E402
import walls_flow  # noqa: E402
import walls_sig3d  # noqa: E402
import walls_pouso  # noqa: E402

WIP = {"moongate"}            # drawn but not finished: only built with --only
FORMS = {"juzhe": walls_juzhe.form_juzhe, "moongate": walls_moongate.form_moongate, "cachoeira": walls_cachoeira.form_cachoeira, "brasilia": walls_brasilia.form_brasilia, "estaiada": walls_estaiada.form_estaiada, "rioniteroi": walls_rioniteroi.form_rioniteroi,
         "veil": walls_flow.form_veil, "pouso": walls_pouso.form_pouso, "sigjuzhe": walls_sig3d.form_3d_juzhe, "sigfold": walls_sig3d.form_3d_fold, "siggate": walls_sig3d.form_3d_gate, "bloom": walls_flow.form_bloom, "dunes": walls_flow.form_dunes}


FLOW_FORMS = {"pouso", "veil", "bloom", "dunes", "sigjuzhe", "sigfold", "siggate"}
FLOW_MUTE = 0.95               # the abstracts carry their chroma; the scenes were muted to 0.6


def build(form, pal, size):
    lib.MUTE = FLOW_MUTE if form in FLOW_FORMS else 0.6
    W, H = SIZES[size]
    fr = Frame(W, H)
    P, why = palette(pal)
    P['_name'] = pal
    doc = Doc(W, H, f"WolOS east wallpaper: {form}, {pal}")
    FORMS[form](doc, fr, P)
    meta = "<!-- palette: " + "; ".join(f"{k}={P[k]} {why[k]}" for k in P if k in why) + " -->"
    return doc.svg().replace("<defs>", meta + "<defs>", 1).replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"', 1)


def _score_one(path):
    import score as S
    s = S.score_pixels(path, "wallpaper")
    return os.path.basename(path), {"total": S.total(s), **{r: s[r]["score"] for r in S.RULES}}


def score_files(files, out_json):
    """Official scores (score.py --kind wallpaper) fanned out over processes, merged into out_json."""
    import json
    from par import fanout
    d = json.load(open(out_json)) if os.path.exists(out_json) else {}
    for name, s in fanout(_score_one, files, workers=min(12, len(files))):
        d[name] = s
        print(f"{name:34s} {s['total']:5.1f}")
    json.dump(d, open(out_json, "w"), indent=1, sort_keys=True)


def _theme_job(job):
    """One theme: the base from its accent, a flow family, day and night, every size."""
    tid, fam, out, sizes = job
    lib.MUTE = FLOW_MUTE
    import themesets as TS
    th = TS.themes()[tid]
    TS._set_base(TS.theme_base(th["tokens"]["accent"]))
    done = []
    for mode in ("day", "night"):
        for s in sizes:
            W, H = SIZES[s]
            fr = Frame(W, H)
            P, why = palette(mode)
            P["_name"] = mode
            doc = Doc(W, H, f"WolOS east wallpaper: {fam} flow, theme {tid}, {mode}")
            if fam == "siggate":
                walls_sig3d.form_3d_gate(doc, fr, P)
            elif fam == "pouso":
                walls_pouso.form_pouso(doc, fr, P)
            elif fam == "dunes":
                walls_flow.form_dunes(doc, fr, P)
            elif fam == "bloom":
                walls_flow.form_bloom(doc, fr, P)
            else:
                walls_flow.form_family(doc, fr, P, fam)
            svg = doc.svg().replace('<svg xmlns="http://www.w3.org/2000/svg"', '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"', 1)
            path = os.path.join(out, f"{ {'pouso': 'pouso', 'siggate': 'gate'}.get(fam, 'flow') }-{tid}-{mode}-{s}.svg")
            with open(path, "w") as fh:
                fh.write(svg)
            done.append(path)
    return tid, fam, done


def themes_run(out, sizes, fam_fixed=None):
    import themesets as TS
    from par import fanout
    ids = sorted(TS.themes())
    os.makedirs(out, exist_ok=True)
    jobs = [(t, fam_fixed or walls_flow.FAMILY_ORDER[i % len(walls_flow.FAMILY_ORDER)], out, sizes) for i, t in enumerate(ids)]
    for tid, fam, done in fanout(_theme_job, jobs, workers=12):
        print(tid, fam, len(done))


def main(argv):
    import argparse
    if argv and argv[0] == "gate":                      # the four shipped files: the signature in the default dye
        out = os.path.join(HERE, "..", "..", "east", "wallpapers")
        for mode in ("day", "night"):
            for size in SIZES:
                path = os.path.join(out, f"wolos-gate-{mode}-{size}.svg")
                with open(path, "w") as fh:
                    fh.write(build("siggate", mode, size))
                print(path)
        return
    if argv and argv[0] == "themes":
        fam = argv[1] if len(argv) > 1 else None          # e.g. "pouso": one form, every theme dye
        themes_run(os.path.join(HERE, "..", "..", "east", "wallpapers", "themes" + ("-" + fam if fam and fam != "siggate" else "")), list(SIZES), fam)
        return
    if argv and argv[0] == "score":
        files = argv[1:]
        score_files(files, os.path.join(os.path.dirname(os.path.abspath(files[0])), "scores.json"))
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "east", "wallpapers"))
    ap.add_argument("--only")
    ap.add_argument("--palette")
    ap.add_argument("--size")
    a = ap.parse_args(argv)
    forms = a.only.split(",") if a.only else [x for x in FORMS if x not in WIP]
    pals = a.palette.split(",") if a.palette else list(PALETTES)
    sizes = a.size.split(",") if a.size else list(SIZES)
    os.makedirs(a.out, exist_ok=True)
    for fm in forms:
        for p in pals:
            for s in sizes:
                path = os.path.join(a.out, f"{fm}-{p}-{s}.svg")
                with open(path, "w") as fh:
                    fh.write(build(fm, p, s))
                print(path)


if __name__ == "__main__":
    main(sys.argv[1:])
