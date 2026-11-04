# SPDX-License-Identifier: GPL-2.0-or-later
"""Type A2 for the full shipped set (docs/adr/brand-east.md section 8.2), in batches of six.

  python3 -I design/tools/east/fullset.py BATCH [--sheet OUT.png]      BATCH = 1, 2, ...

Writes east/fullset/wolos-<app>.svg and small/; with --sheet, the current vs A2 board with the
eight-rule scores and the craft checks (scored in parallel, par.fanout)."""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("east_types", os.path.join(HERE, "types.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
from geom import Doc, rrect, circle, juzhe, smooth, shade, f  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
S = 1024
VIOLET, INK, JADE_CARD, AZURITE, LAKE, OCHRE = (T.CARD["settings"], T.CARD["console"], T.CARD["doctor"],
                                                T.CARD["files"], T.CARD["atlas"], T.STORE_A2)
WHITE, GOLD, RED, JADE = T.WHITE, T.GOLD, T.RED, T.JADE


def start(title, card):
    T.a2_setup()
    doc = Doc(S, S, title)
    T.a2_card(doc, card)
    return doc, T.X, T.FEN


def g(doc, d, colour=WHITE, small=False, elev="glyph", rule="nonzero"):
    T.g2(doc, d, colour, small=small, elev=elev, rule=rule)


def flat(doc, d, colour, rule="nonzero"):
    doc.add(f'<path d="{d}" fill-rule="{rule}" fill="{colour}"/>')


# ---------------------------------------------------------------- batch 1
def calculator(small=False):
    doc, X, F = start("calculator, A2", INK)
    keys = [(3.0, 3.0), (11.0, 3.0), (3.0, 11.0), (11.0, 11.0)]          # 7 x 7 keys, 1 fen gap
    for i, (x, y) in enumerate(keys):
        g(doc, rrect(X(x), X(y), 7 * F, 7 * F, 1.6 * F), GOLD if i == 3 else WHITE, small, "accent" if i == 3 else "glyph")
    th = (1.2 if small else 0.9) * F
    sym = INK
    cx, cy = 6.5, 6.5                                                      # plus
    flat(doc, rrect(X(cx - 2), X(cy) - th / 2, 4 * F, th, th / 2) + rrect(X(cx) - th / 2, X(cy - 2), th, 4 * F, th / 2), sym)
    flat(doc, rrect(X(14.5 - 2), X(6.5) - th / 2, 4 * F, th, th / 2), sym)  # minus
    cx, cy = 6.5, 14.5                                                     # times: the plus turned 45
    flat(doc, f'{rrect(X(cx - 2), X(cy) - th / 2, 4 * F, th, th / 2)}{rrect(X(cx) - th / 2, X(cy - 2), th, 4 * F, th / 2)}', sym)
    doc.body[-1] = doc.body[-1].replace("<path ", f'<path transform="rotate(45 {f(X(cx))} {f(X(cy))})" ')
    for dy in (-0.9, 0.9):                                                 # equals, on the gold key
        flat(doc, rrect(X(12.5), X(14.5 + dy) - th / 2, 4 * F, th, th / 2), INK)
    return doc.svg()


def calendar(small=False):
    doc, X, F = start("calendar, A2", JADE_CARD)
    page = rrect(X(3.0), X(4.0), 15 * F, 14.5 * F, 1.6 * F)
    g(doc, page, small=small)
    band = rrect(X(3.0), X(4.0), 15 * F, 4.0 * F, 1.6 * F, 1.6 * F, 0, 0)
    flat(doc, band, T.leaf(JADE_CARD))
    for x in (7.0, 14.0):                                                  # the rings
        g(doc, rrect(X(x - 0.6), X(2.4), 1.2 * F, 3.4 * F, 0.6 * F), shade(JADE_CARD, -8), small, "accent")
    if small:
        g(doc, circle(X(10.5), X(13.2), 2.6 * F), RED, small, "accent")
    else:
        for r in range(2):
            for c in range(4):
                x, y = 5.0 + c * 3.0, 10.2 + r * 3.4
                if (r, c) == (1, 2):
                    g(doc, circle(X(x + 0.5), X(y + 0.5), 1.25 * F), RED, small, "accent")
                else:
                    flat(doc, rrect(X(x - 0.4), X(y - 0.4), 1.8 * F, 1.8 * F, 0.5 * F), T.leaf(JADE_CARD))
    return doc.svg()


def control_center(small=False):
    doc, X, F = start("control center, A2", VIOLET)
    for i, (y, on) in enumerate(((4.0, True), (11.5, False))):
        pill = rrect(X(3.0), X(y), 15 * F, 5.5 * F, 2.75 * F)
        g(doc, pill, WHITE if on else T.leaf(VIOLET), small)
        kx = 15.25 if on else 5.75
        g(doc, circle(X(kx), X(y + 2.75), 2.0 * F), GOLD if on else WHITE, small, "accent")
    return doc.svg()


def games(small=False):
    doc, X, F = start("games, A2", VIOLET)
    # controller: a body 15 x 8 with two grips falling to y 17 (water forms: no corner)
    body = (f"M{f(X(6.0))} {f(X(6.5))}H{f(X(15.0))}C{f(X(18.2))} {f(X(6.5))} {f(X(19.0))} {f(X(10.5))} {f(X(18.6))} {f(X(14.5))}"
            f"C{f(X(18.3))} {f(X(17.4))} {f(X(15.6))} {f(X(17.6))} {f(X(14.4))} {f(X(15.0))}L{f(X(13.4))} {f(X(13.4))}H{f(X(7.6))}"
            f"L{f(X(6.6))} {f(X(15.0))}C{f(X(5.4))} {f(X(17.6))} {f(X(2.7))} {f(X(17.4))} {f(X(2.4))} {f(X(14.5))}"
            f"C{f(X(2.0))} {f(X(10.5))} {f(X(2.8))} {f(X(6.5))} {f(X(6.0))} {f(X(6.5))}Z")
    g(doc, body, small=small)
    th = (1.4 if small else 1.1) * F
    cx, cy = 6.5, 10.0                                                     # d-pad
    flat(doc, rrect(X(cx - 1.9), X(cy) - th / 2, 3.8 * F, th, th / 3) + rrect(X(cx) - th / 2, X(cy - 1.9), th, 3.8 * F, th / 3), VIOLET)
    for (x, y) in ((14.0, 9.0), (15.9, 11.0)):                            # two buttons (fire as accent)
        g(doc, circle(X(x), X(y), (1.1 if not small else 1.3) * F), RED, small, "accent")
    return doc.svg()


def installer(small=False):
    doc, X, F = start("installer, A2", VIOLET)
    # the door (the mark's arch), 11 wide x 15 tall, with the down arrow inside it
    w, top, bot = 11.0, 3.0, 18.0
    r = w / 2 * F
    door = f"M{f(X(10.5 - w / 2))} {f(X(bot))}V{f(X(top) + r)}A{f(r)} {f(r)} 0 0 1 {f(X(10.5 + w / 2))} {f(X(top) + r)}V{f(X(bot))}Z"
    g(doc, door, small=small)
    th = (1.8 if small else 1.4) * F
    stem = rrect(X(10.5) - th / 2, X(7.0), th, 6.0 * F, th / 2)
    head = T.ribbon([(X(7.6), X(10.6)), (X(10.5), X(13.6)), (X(13.4), X(10.6))], th)
    g(doc, stem + head, GOLD, small, "accent")
    return doc.svg()


def launcher(small=False):
    """Search: the lens (a ring 12 fen across) and its handle along the light's 1:2 diagonal; the
    keyhole in the lens is the landing (what you look for opens)."""
    doc, X, F = start("launcher (search), A2", VIOLET)
    cx, cy, ro, ri = 9.0, 9.0, 6.0, 4.4 if not small else 4.0
    ring = circle(X(cx), X(cy), ro * F) + circle(X(cx), X(cy), ri * F)
    ang = math.atan2(2, 1)                                   # down-right, 1:2
    x0, y0 = cx + ro * 0.92 * math.cos(ang), cy + ro * 0.92 * math.sin(ang)
    x1, y1 = cx + (ro + 4.4) * math.cos(ang), cy + (ro + 4.4) * math.sin(ang)   # ends 2 fen inside the card: no line into the frame
    hnd = T.ribbon([(X(x0), X(y0)), (X(x1), X(y1))], (2.6 if small else 2.2) * F)
    g(doc, ring + hnd, small=small, rule="evenodd")
    g(doc, T.keyhole_at(X(cx), X(cy), (2.6 if small else 2.0) * F), GOLD, small, "accent")
    return doc.svg()


BATCHES = {1: [("calculator", calculator), ("calendar", calendar), ("control-center", control_center),
               ("games", games), ("installer", installer), ("launcher", launcher)]}


def _job(args):
    b, i, small = args
    name, fn = BATCHES[b][i]
    out = os.path.join(D, "east", "fullset", "small" if small else "")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, f"wolos-{name}.svg"), "w").write(fn(small))
    return name


def _score(p):
    import board as B
    import craft
    s = B.scored(p, "icon")
    c = craft.check(p)
    return s, [k for k, (ok, _) in c.items() if not ok]


def sheet(b, out):
    import board as B
    from par import fanout
    from PIL import Image, ImageDraw
    names = [n for n, _ in BATCHES[b]]
    cur = [os.path.join(D, "icons", "apps", f"wolos-{n}.svg") for n in names]
    new = [os.path.join(D, "east", "fullset", f"wolos-{n}.svg") for n in names]
    small = [os.path.join(D, "east", "fullset", "small", f"wolos-{n}.svg") for n in names]
    res = fanout(_score, cur + new + small)
    cw, pad = 230, 24
    W, H = pad + 6 * (cw + pad), 720
    im = Image.new("RGB", (W, H), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((pad, 10), f"Type A2, full set, batch {b}: current (top) vs A2 (bottom), score 0-100, craft checks", font=B.font(20, True), fill=B.INK)
    for i, n in enumerate(names):
        x = pad + i * (cw + pad)
        (sa, fa), (sb, fb), (_, fs) = res[i], res[6 + i], res[12 + i]
        for row, (p, s) in enumerate(((cur[i], sa), (new[i], sb))):
            y = 50 + row * 300
            ic = B.raster(p, 200, 200)
            im.paste(ic, (x + 10, y), ic)
            col = B.INK if row == 0 else (B.GOOD if sb["total"] > sa["total"] else B.BAD)
            dr.text((x + 10, y + 208), f"{n}  {s['total']:.1f}", font=B.font(17, True), fill=col)
        for k, sz in enumerate((16, 32, 64)):
            t = B.raster(small[i] if sz <= 32 else new[i], sz, sz)
            im.paste(t, (x + 10 + k * 60, 600 + (64 - sz) // 2), t)
        bad = sorted(set(fb) | set(fs))
        dr.text((x + 10, 680), "craft: pass" if not bad else "craft FAIL: " + ", ".join(bad), font=B.font(13, True), fill=B.GOOD if not bad else B.BAD)
    im.save(out)
    return {n: (res[i][0]["total"], res[6 + i][0]["total"], sorted(set(res[6 + i][1]) | set(res[12 + i][1]))) for i, n in enumerate(names)}


def main(argv):
    from par import fanout
    b = int(argv[0])
    fanout(_job, [(b, i, sm) for i in range(len(BATCHES[b])) for sm in (False, True)])
    if "--sheet" in argv:
        r = sheet(b, argv[argv.index("--sheet") + 1])
        for n, (a, e, bad) in r.items():
            print(f"{n:16s} {a:5.1f} -> {e:5.1f}  craft {'pass' if not bad else bad}")


if __name__ == "__main__":
    main(sys.argv[1:])
