# SPDX-License-Identifier: GPL-2.0-or-later
"""Third-party app icons in Type A2 (docs/adr/brand-calculus.md section 8.1): each app keeps its own
animal or object and its own card hue; the drawing follows the A2 grammar (the zucai card, one big
white glyph on the 15-fen square, one accent at the landing, shadow rules S1-S6, a 16-32 px variant).

  python3 -I design/tools/brand/thirdparty.py [APP ...] [--sheet OUT.png] [--family OUT.png]

Writes brand/thirdparty/<app>.svg and brand/thirdparty/small/<app>.svg. The originals, their source
URLs and licences are in brand/thirdparty/src/ (SOURCES.tsv); measure.py reads them.
Cards: the original card hue, value and chroma derived from the base (calculus.derive): the first
step on the value ruler where the white glyph holds 3.2:1 (craft's 16 px floor is 3:1).
Only licence-permitting icons are redrawn; trademarked browser marks are not (lead decision)."""
import importlib.util
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("brand_fullset", os.path.join(HERE, "fullset.py"))
FS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FS)
T = FS.T
import calculus as K  # noqa: E402
from colour import oklch, contrast  # noqa: E402
from geom import rrect, circle, shade, f  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(D, "brand", "thirdparty")
SRC = os.path.join(OUT, "src")
WHITE, GOLD, RED, JADE = T.WHITE, T.GOLD, T.RED, T.JADE
L0, C0, H0 = oklch(K.BASE)


FLOOR = 3.2          # white-on-card contrast floor (themesets raises it: muted bases lose the lit corner)


def card_of(original, floor=None, chroma=16, cap=True):
    """The app's card: its own hue, chroma `chroma`/21 of the base's (capped by the original's),
    value from the base's ruler, the lightest k where white holds `floor`."""
    floor = FLOOR if floor is None else floor
    _, c, h = oklch(original)
    cf = min(chroma, 21 * c / C0) if cap else chroma
    k = K.first_k(lambda k: contrast(K.derive(k, cf, h), WHITE) >= floor, range(8, -16, -1))
    return K.derive(k, cf, h)


def P(s):
    """A path written in card fen (0..21): every coordinate pair goes through X. Only absolute
    M L C Q S T Z (no arcs, no H/V), so pairs are unambiguous."""
    X = T.X
    toks = re.findall(r"[MLCQSTZ]|-?\d*\.?\d+", s)
    out, nums = [], []
    for t in toks:
        if t.isalpha():
            out.append(t)
        else:
            nums.append(float(t))
            if len(nums) == 2:
                out.append(f"{f(X(nums[0]))} {f(X(nums[1]))}")
                nums = []
    return re.sub(r" ?([MLCQSTZ]) ?", r"\1", " ".join(out))


def disc(cx, cy, r):
    X, F = T.X, T.FEN
    return circle(X(cx), X(cy), r * F)


def ell(cx, cy, rx, ry, rot=0):
    """An ellipse as four cubic arcs (k = 0.5523), rotated by rot degrees about its centre."""
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    k = 0.5523

    def p(x, y):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    pts = [p(rx, 0), p(rx, k * ry), p(k * rx, ry), p(0, ry), p(-k * rx, ry), p(-rx, k * ry), p(-rx, 0),
           p(-rx, -k * ry), p(-k * rx, -ry), p(0, -ry), p(k * rx, -ry), p(rx, -k * ry), p(rx, 0)]
    s = f"M{pts[0][0]:.4f} {pts[0][1]:.4f}"
    for i in range(1, 13, 3):
        s += "C" + " ".join(f"{x:.4f} {y:.4f}" for x, y in pts[i:i + 3])
    return P(s + "Z")


def rib(pts, th):
    X, F = T.X, T.FEN
    return T.ribbon([(X(a), X(b)) for a, b in pts], th * F)


def lic_comment(app):
    src = {r[0]: r for r in (l.rstrip("\n").split("\t") for l in open(os.path.join(SRC, "SOURCES.tsv")))}
    s = src.get(app)
    if not s:
        return ""
    return f"<!-- Type A2 redraw of the {s[0]} app icon ({s[1]}). Original: {s[2]}. Licence of the original: {s[3]}; this drawing is offered under the same terms. -->"


def finish(doc, app):
    svg = doc.svg(lic=False)
    return svg.replace("</title>", "</title>" + lic_comment(app), 1)


start, g, flat = FS.start, FS.g, FS.flat


# ================================================================ image editor (the wilber)
# Lead 07:56-07:57Z: the first redraw lost the eye; keep the base with a tool. So the wilber is
# not redrawn by hand: measure.svg_shapes reads the original's own shapes, measure.fit puts its
# art box into the glyph box (proportions kept), and only the materials change (A2).
import measure as MS  # noqa: E402

GIMP_CARD = card_of("#8C8073", chroma=7, cap=False)
GIMP_SRC = os.path.join(D, "icons", "store", "gimp.svg")


def art_box(path, size=512):
    """The drawn art box of an SVG in its own user units (rendered, so control points that fall
    outside the curve do not count)."""
    import read_icon as RI
    src = open(path, encoding="utf-8").read()
    vb = [float(v) for v in re.findall(MS._NUM, re.search(r'viewBox="([^"]*)"', src).group(1))]
    x0, y0, x1, y1 = RI.read(path, size)["box_fen"]
    k = vb[2] / 24
    return (vb[0] + x0 * k, vb[1] + y0 * k, vb[0] + x1 * k, vb[1] + y1 * k)


def gimp(small=False):
    """Roles of the original's 15 shapes (document order): 0 brush tip (ink), 1 head, 2/11 eye
    whites, 3/12 pupils, 4/13 glints, 5 the bulging eye, 6 its glint, 7/8 the smile, 9 handle,
    10 ferrule, 14 the paint on the tip. A2: the head is the white glyph; eye whites are raised
    white balls ringed in the card tone so they read on the white head; pupils, smile and tip in
    the card's deep tone; the handle is the gold accent at the landing."""
    c = GIMP_CARD
    doc, X, F = start("image editor, A2", c)
    shapes, _ = MS.svg_shapes(GIMP_SRC)
    M = MS.fit(art_box(GIMP_SRC), (10.6, 10.7, 17.0))
    d = [MS.to_d(sh["sub"], M, X) for sh in shapes]
    ink = shade(c, -10)
    g(doc, d[1], small=small)                                  # head
    g(doc, d[14], small=small)                                 # paint on the tip
    flat(doc, d[0], ink)                                       # tip
    g(doc, d[9], GOLD, small, "accent")                        # handle: the landing
    flat(doc, d[10], T.leaf(c))                                # ferrule
    flat(doc, d[8], ink); flat(doc, d[7], ink)                 # smile
    sw = (0.55 if small else 0.4) * F
    for i in (2, 11):                                          # eye whites: raised white balls (S1 shadow)
        T.cast(doc, d[i], c, T.ELEV["glyph"])
        doc.add(f'<path d="{d[i]}" fill="{WHITE}"/>')
    T.cast(doc, d[5], c, T.ELEV["accent"])
    doc.add(f'<path d="{d[5]}" fill="{ink}" stroke="{WHITE}" stroke-width="{f(1.5 * sw)}"/>')   # the bulging eye, its white rim meets the head
    flat(doc, d[3], ink); flat(doc, d[12], ink)                # pupils
    for i in (4, 13, 6):                                       # glints
        flat(doc, d[i], WHITE)
    return finish(doc, "gimp")


# ================================================================ the craft family
# Lead 08:03Z: keep the coloured square, recreate what is inside: a bold A2 glyph of the app's own
# animal or object (pose from the original), with a Chinese or Brazilian motif where it means
# something, one accent at the landing. Cards: each app's own hue through card_of.
def sym(cx, top, segs):
    """A shape symmetric about x = cx: `segs` are cubic segments [(c1, c2, p), ...] for the left
    half, from (cx, top) down to a point on the axis; the right half is mirrored."""
    def m(q):
        return (2 * cx - q[0], q[1])
    pts = [(cx, top)] + [q[2] for q in segs]
    s = f"M{cx} {top}"
    for c1, c2, q in segs:
        s += f"C{c1[0]} {c1[1]} {c2[0]} {c2[1]} {q[0]} {q[1]}"
    for i in range(len(segs) - 1, -1, -1):
        c1, c2, q = segs[i]
        a = m(c2); b = m(c1); e = m(pts[i])
        s += f"C{a[0]:.3f} {a[1]:.3f} {b[0]:.3f} {b[1]:.3f} {e[0]:.3f} {e[1]:.3f}"
    return P(s + "Z")


def tear(x0, y0, ang, length, width):
    """A teardrop from a root point along an angle (degrees): a tail, a petal, a flame."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tip = (x0 + ux * length, y0 + uy * length)
    w = width / 2
    c1 = (x0 + ux * length * 0.35 + nx * w * 1.6, y0 + uy * length * 0.35 + ny * w * 1.6)
    c2 = (tip[0] - ux * length * 0.15 + nx * w * 0.9, tip[1] - uy * length * 0.15 + ny * w * 0.9)
    c3 = (tip[0] - ux * length * 0.15 - nx * w * 0.9, tip[1] - uy * length * 0.15 - ny * w * 0.9)
    c4 = (x0 + ux * length * 0.35 - nx * w * 1.6, y0 + uy * length * 0.35 - ny * w * 1.6)
    return P(f"M{x0:.3f} {y0:.3f}C{c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {tip[0]:.3f} {tip[1]:.3f}"
             f"C{c3[0]:.3f} {c3[1]:.3f} {c4[0]:.3f} {c4[1]:.3f} {x0:.3f} {y0:.3f}Z")


def ink_of(c):
    return shade(c, -11)


ORIGINAL_HUES = {
    "photocraft": "#317BF1", "vectorcraft": "#E55840", "pdfcraft": "#B50529", "wordcraft": "#3C5BDC",
    "deckcraft": "#F16C20", "filmcraft": "#8A5CF4", "soundcraft": "#20AAC4", "cadcraft": "#15A4C7",
    "designcraft": "#7BB51E", "figcraft": "#0AD996", "effectcraft": "#DE388F", "lightcraft": "#F2A61A",
    "materialcraft": "#198A9B", "texturecraft": "#C1672C", "gridcraft": "#1E9D55"}


def cards():
    return {a: card_of(h, floor=(max(4.1, FLOOR) if a == "wordcraft" else None)) for a, h in ORIGINAL_HUES.items()}


CARDS = cards()


def photocraft(small=False):
    """The nine-tailed fox (huli jing): a frontal fox head, its nine tails fanned behind it like a
    round fan; the gold mark on the brow (the original's own) is the landing."""
    c = CARDS["photocraft"]
    doc, X, F = start("photo editor, A2", c)
    n = 5 if small else 9
    for i in range(n):
        ang = -168 + i * (156 / (n - 1))
        g(doc, tear(10.5, 13.0, ang, 8.6, 2.6 if not small else 3.4), T.leaf(c) if i % 2 else WHITE, small)
    head = sym(10.5, 8.0, [((9.6, 7.6), (8.8, 6.4), (7.6, 5.6)), ((6.6, 4.9), (5.6, 4.4), (5.0, 4.4)),
                           ((5.0, 6.2), (5.2, 8.4), (5.4, 10.0)), ((4.6, 11.0), (4.0, 12.2), (3.6, 13.0)),
                           ((5.6, 14.0), (8.4, 17.6), (10.5, 18.0))])
    g(doc, head, small=small)
    ink = ink_of(c)
    if not small:
        for sx in (1, -1):
            ear = sym(10.5, 0, [])  # placeholder (unused)
        flat(doc, P("M6.3 6.0 C7.0 6.4 7.8 7.2 8.2 8.0 L6.4 9.6 C6.2 8.4 6.2 7.2 6.3 6.0 Z"), T.leaf(c))
        flat(doc, P("M14.7 6.0 C14.0 6.4 13.2 7.2 12.8 8.0 L14.6 9.6 C14.8 8.4 14.8 7.2 14.7 6.0 Z"), T.leaf(c))
    for sx in (-1, 1):
        flat(doc, ell(10.5 + sx * 2.5, 12.4, 1.15 if not small else 1.4, 0.62 if not small else 0.85, rot=sx * 22), ink)
    flat(doc, ell(10.5, 16.4, 0.95, 0.7), ink)
    g(doc, P("M10.5 8.6 C11.1 9.4 11.4 10.0 10.5 11.0 C9.6 10.0 9.9 9.4 10.5 8.6 Z"), GOLD, small, "accent")
    return finish(doc, "photocraft")


def vectorcraft(small=False):
    """The dragon (long) in profile, the original's pose: the head turned left with its swept
    horns and one long whisker; the flaming pearl it chases is the landing, drawn as a vector
    node on the whisker's curve (the app's craft)."""
    c = CARDS["vectorcraft"]
    doc, X, F = start("vector editor, A2", c)
    ink = ink_of(c)
    th = 1.3 if small else 1.0
    g(doc, rib([(11.4, 7.6), (13.2, 5.4), (15.6, 3.9), (17.6, 3.6)], th + 0.2), T.leaf(c), small)
    g(doc, rib([(12.6, 8.2), (14.8, 6.8), (17.0, 6.4), (18.4, 6.8)], th), T.leaf(c), small)
    if not small:   # the mane along the back of the neck: three flames
        for (x, y, a) in ((15.6, 9.6, -20), (16.4, 12.4, -10), (17.2, 15.2, 0)):
            g(doc, tear(x - 0.6, y, a, 3.0, 1.6), T.leaf(c), small)
    head = P("M3.0 9.9 C3.4 8.6 4.8 7.9 6.3 8.1 C7.5 8.3 8.3 7.1 9.8 6.8 C11.6 6.4 13.5 6.9 14.7 8.0 "
             "C15.7 9.0 16.1 10.6 16.4 12.4 C16.7 14.4 17.4 16.4 18.2 18.2 L12.2 18.2 "
             "C12.0 16.4 11.5 15.0 10.4 14.0 C9.0 13.0 7.0 13.5 5.0 13.7 C4.3 13.7 4.1 13.0 4.6 12.6 "
             "C5.8 12.2 7.4 12.2 8.6 11.8 C7.0 11.4 5.0 11.2 3.6 11.0 C2.9 10.9 2.8 10.4 3.0 9.9 Z")
    g(doc, head, small=small)
    flat(doc, ell(10.2, 9.4, 1.1 if not small else 1.3, 0.7 if not small else 0.9, rot=-12), ink)
    flat(doc, disc(4.6, 9.5, 0.45 if not small else 0.6), ink)
    # the whisker: a bezier from the upper lip; the pearl sits on its end as the node
    wh = P("M4.0 10.6 C2.2 11.4 2.0 13.8 3.4 15.0") if False else None
    g(doc, rib([(3.8, 11.0), (2.8, 12.4), (2.9, 14.0), (4.0, 15.4)], 0.7 if not small else 1.0), WHITE, small)
    g(doc, disc(5.4, 16.6, 1.7 if not small else 2.0), GOLD, small, "accent")
    if not small:
        flat(doc, disc(5.4, 16.6, 0.6), WHITE)
    return finish(doc, "vectorcraft")


def pdfcraft(small=False):
    """The lion as the Chinese guardian lion (shishi): a frontal face in a mane of round curls;
    the gold embroidered ball under its paw is the landing."""
    c = CARDS["pdfcraft"]
    doc, X, F = start("pdf workbench, A2", c)
    ink = ink_of(c)
    curls = 10 if not small else 8
    mane = disc(10.5, 10.0, 6.4)
    for i in range(curls):
        a = 2 * math.pi * i / curls - math.pi / 2
        mane += disc(10.5 + 6.2 * math.cos(a), 10.0 + 6.2 * math.sin(a), 2.0)
    g(doc, mane, T.leaf(c), small)
    face = sym(10.5, 5.6, [((8.6, 5.6), (6.4, 6.4), (6.0, 8.8)), ((5.6, 11.2), (6.4, 13.6), (7.6, 14.8)),
                           ((8.4, 15.6), (9.4, 16.0), (10.5, 16.0))])
    g(doc, face, small=small)
    for sx in (-1, 1):
        flat(doc, ell(10.5 + sx * 2.1, 9.8, 0.9 if not small else 1.1, 0.75 if not small else 0.95), ink)
        if not small:
            flat(doc, rib([(10.5 + sx * 1.0, 8.2), (10.5 + sx * 3.0, 7.9)], 0.55), T.leaf(c))
    flat(doc, P("M9.2 12.2 C9.8 11.9 11.2 11.9 11.8 12.2 C11.6 13.0 11.0 13.4 10.5 13.6 C10.0 13.4 9.4 13.0 9.2 12.2 Z"), ink)
    flat(doc, rib([(8.8, 14.4), (10.5, 15.0), (12.2, 14.4)], 0.5 if not small else 0.7), ink)
    g(doc, disc(15.6, 16.4, 2.0 if not small else 2.3), GOLD, small, "accent")
    if not small:
        flat(doc, rib([(14.2, 15.6), (15.6, 16.6), (17.0, 15.6)], 0.4), T.leaf(c))
    return finish(doc, "pdfcraft")


def wordcraft(small=False):
    """A page with lines and a pencil, as the original; the pencil is the gold accent."""
    c = CARDS["wordcraft"]
    doc, X, F = start("word processor, A2", c)
    g(doc, FS.page(X, F, 3.5, 3.0, 12.5, 15.0), small=small)
    if not small:
        FS.lines(doc, X, F, 5.5, 7.4, (8.5, 6.5, 8.5, 5.0), T.leaf(c), pitch=2.4)
    else:
        FS.lines(doc, X, F, 5.5, 8.0, (8.5, 6.0), T.leaf(c), pitch=3.2)
    body = rib([(18.0, 9.4), (12.6, 15.8)], 2.2 if not small else 2.6)
    g(doc, body, GOLD, small, "accent")
    tipd = P("M11.75 15.1 L13.45 16.5 L11.4 17.5 Z")
    flat(doc, tipd, ink_of(GOLD) if False else shade(c, -6))
    return finish(doc, "wordcraft")


def deckcraft(small=False):
    """The presentation board on its stand with a bar chart, as the original; the gold point
    (the original's dot) is the landing."""
    c = CARDS["deckcraft"]
    doc, X, F = start("presentation, A2", c)
    ink = ink_of(c)
    g(doc, rib([(10.5, 14.5), (10.5, 18.0)], 1.2) + rib([(7.6, 18.0), (13.4, 18.0)], 1.2), T.leaf(c), small)
    board = rrect(X(3.0), X(4.0), 15 * F, 10.5 * F, 1.4 * F)
    g(doc, board, small=small)
    for i, (h, col) in enumerate(((3.0, shade(c, -2)), (5.2, ink), (4.0, shade(c, -2)))):
        flat(doc, rrect(X(5.2 + i * 2.6), X(12.6 - h), 1.8 * F, h * F, 0.4 * F), col)
    if not small:
        flat(doc, rrect(X(5.2), X(5.8), 6.0 * F, 0.9 * F, 0.45 * F), T.leaf(c))
    g(doc, disc(14.6, 7.2, 1.6 if not small else 1.9), GOLD, small, "accent")
    return finish(doc, "deckcraft")


def filmcraft(small=False):
    """The owl, frontal with its ear tufts; its two eyes are film reels with gold irises: the
    landing is the gaze."""
    c = CARDS["filmcraft"]
    doc, X, F = start("video editor, A2", c)
    ink = ink_of(c)
    body = sym(10.5, 6.4, [((9.4, 6.4), (8.0, 6.0), (6.6, 5.2)), ((5.6, 4.6), (4.8, 3.8), (4.4, 3.4)),
                           ((4.6, 5.4), (4.4, 7.0), (4.2, 8.6)), ((3.6, 12.0), (4.2, 15.6), (6.4, 17.4)),
                           ((7.6, 18.4), (9.2, 18.6), (10.5, 18.6))])
    g(doc, body, small=small)
    if not small:
        for (y, w) in ((14.2, 4.0), (16.2, 2.6)):
            flat(doc, rib([(10.5 - w / 2, y - 0.5), (10.5, y + 0.2), (10.5 + w / 2, y - 0.5)], 0.5), T.leaf(c))
    for sx in (-1, 1):
        x = 10.5 + sx * 3.0
        flat(doc, disc(x, 9.6, 2.9), T.leaf(c))
        g(doc, disc(x, 9.6, 2.1 if not small else 2.3), GOLD, small, "accent")
        flat(doc, disc(x, 9.6, 1.0 if not small else 1.2), ink)
        if not small:
            for k in range(4):   # the reel's holes, in the iris
                a = math.pi / 4 + k * math.pi / 2
                flat(doc, disc(x + 1.55 * math.cos(a), 9.6 + 1.55 * math.sin(a), 0.32), shade(GOLD, -6))
    flat(doc, P("M9.7 11.6 L11.3 11.6 L10.5 13.2 Z"), ink)
    return finish(doc, "filmcraft")


def soundcraft(small=False):
    """The singing bird, as the original (profile, beak open, sound waves): drawn as the sabiá,
    the song thrush of Brazil, whose orange breast is the landing; the waves are the entry."""
    c = CARDS["soundcraft"]
    doc, X, F = start("audio workstation, A2", c)
    ink = ink_of(c)
    for i, r in enumerate((1.8, 3.4) if not small else (3.4,)):
        pts = [(6.0 - r * math.cos(t), 6.4 + r * math.sin(t) * 0.0 - r * math.sin(t)) for t in [(-0.7 + 1.4 * k / 8) for k in range(9)]]
        pts = [(5.2 - r * math.cos(t), 7.6 + r * math.sin(t)) for t in [(-0.75 + 1.5 * k / 8) for k in range(9)]]
        g(doc, rib(pts, 0.8 if not small else 1.1), T.leaf(c), small)
    body = P("M7.2 8.8 C7.6 6.2 9.6 4.6 12.0 4.6 C14.4 4.6 16.0 6.0 16.8 8.2 C17.8 10.8 18.0 13.6 17.6 16.0 "
             "L19.0 18.2 L15.2 17.6 C13.0 18.4 10.6 18.4 9.0 17.0 C7.6 15.8 7.0 13.6 7.0 11.6 C7.0 10.6 7.0 9.6 7.2 8.8 Z")
    g(doc, body, small=small)
    g(doc, P("M7.4 8.0 L3.8 8.6 L7.1 9.8 Z") + P("M7.0 10.2 L4.4 11.4 L7.2 11.2 Z"), shade(c, -6), small, "accent")
    g(doc, P("M7.2 12.2 C8.6 11.6 11.0 11.8 12.4 13.0 C13.4 14.0 13.2 16.4 11.8 17.6 C10.4 18.2 9.0 17.6 8.2 16.4 C7.4 15.2 7.0 13.6 7.2 12.2 Z"),
      T.from_oklch(0.74, 0.15, 55.0), small, "accent")
    flat(doc, disc(10.0, 8.0, 1.2 if not small else 1.4), ink)
    flat(doc, disc(9.6, 7.6, 0.4 if not small else 0.45), WHITE)
    if not small:
        for (x, y) in ((14.4, 10.4), (15.4, 12.6), (14.6, 14.8)):
            flat(doc, rib([(x - 0.8, y - 0.3), (x, y + 0.3), (x + 0.8, y - 0.3)], 0.45), T.leaf(c))
    return finish(doc, "soundcraft")


def cadcraft(small=False):
    """The set square and the compass arc, as the original; the gold point where the arc lands is
    the landing."""
    c = CARDS["cadcraft"]
    doc, X, F = start("cad, A2", c)
    if not small:
        for i in range(4):
            for j in range(4):
                flat(doc, disc(4.5 + i * 4, 4.5 + j * 4, 0.22), shade(c, 6))
    sq = P("M4.0 3.4 C4.0 2.9 4.6 2.7 5.0 3.1 L17.6 15.9 C18.0 16.3 17.8 17.0 17.2 17.0 L4.6 17.0 C4.2 17.0 4.0 16.8 4.0 16.4 Z")
    hole = P("M6.8 9.8 L12.8 14.4 L6.8 14.4 Z")
    g(doc, sq + hole, small=small, rule="evenodd")
    if not small:
        T.hole_shadow(doc, hole)
        for k in range(5):
            flat(doc, rrect(X(4.0), X(5.0 + k * 2.2), (1.2 if k % 2 else 1.8) * F, 0.4 * F, 0.2 * F), T.leaf(c))
    cx0, cy0, rr = 5.0, 17.4, 12.4
    arc = [(cx0 + rr * math.cos(t), cy0 - rr * math.sin(t)) for t in [math.radians(66 - 58 * k / 12) for k in range(13)]]
    g(doc, rib(arc, 0.9 if not small else 1.3), T.leaf(c), small)
    g(doc, disc(*arc[-1], 1.4 if not small else 1.8), GOLD, small, "accent")
    return finish(doc, "cadcraft")


def designcraft(small=False):
    """The cat, frontal, with its dotted scarf (the original's): the scarf, knotted, is the
    landing, in cinnabar with white dots (a fire accent on the earth-green card)."""
    c = CARDS["designcraft"]
    doc, X, F = start("page layout, A2", c)
    ink = ink_of(c)
    head = sym(10.5, 5.8, [((9.4, 5.8), (8.0, 5.9), (7.0, 6.4)), ((6.2, 5.2), (5.2, 3.8), (4.4, 3.4)),
                           ((4.0, 5.4), (4.0, 7.6), (4.4, 9.2)), ((3.8, 10.6), (3.6, 12.6), (4.6, 14.2)),
                           ((6.0, 16.2), (8.4, 17.3), (10.5, 17.3))])
    g(doc, head, small=small)
    if not small:
        flat(doc, P("M5.2 5.0 C5.8 5.4 6.4 6.2 6.6 6.8 L5.0 8.2 C4.9 7.0 5.0 6.0 5.2 5.0 Z"), T.leaf(c))
        flat(doc, P("M15.8 5.0 C15.2 5.4 14.6 6.2 14.4 6.8 L16.0 8.2 C16.1 7.0 16.0 6.0 15.8 5.0 Z"), T.leaf(c))
        # a patch over the left eye: the original cat's black and white coat
        flat(doc, P("M4.4 9.2 C5.2 7.6 7.4 7.2 9.0 8.0 C9.4 9.6 8.6 11.4 6.8 11.8 C5.6 12.0 4.6 11.4 4.0 10.6 Z"), T.leaf(c))
    for sx in (-1, 1):
        flat(doc, ell(10.5 + sx * 2.6, 10.2, 0.75 if not small else 0.95, 1.05 if not small else 1.25), ink)
    flat(doc, P("M9.8 12.4 L11.2 12.4 L10.5 13.2 Z"), ink)
    if not small:
        for sx in (-1, 1):
            for dy in (-0.4, 0.5):
                flat(doc, rib([(10.5 + sx * 2.4, 13.4 + dy * 0.6), (10.5 + sx * 5.4, 13.0 + dy * 1.6)], 0.28), T.leaf(c))
    scarf = P("M5.4 15.4 C8.0 17.2 13.0 17.2 15.6 15.4 C16.2 16.4 16.0 17.6 15.0 18.2 C12.4 19.4 8.6 19.4 6.0 18.2 C5.0 17.6 4.8 16.4 5.4 15.4 Z")
    g(doc, scarf + P("M12.2 17.6 L15.8 18.6 L14.8 19.8 L13.4 19.6 L12.4 18.8 Z"), RED, small, "accent")
    if not small:
        for (x, y) in ((7.0, 17.4), (9.4, 18.0), (12.0, 17.8), (14.2, 17.0), (14.0, 19.0)):
            flat(doc, disc(x, y, 0.38), WHITE)
    return finish(doc, "designcraft")


def figcraft(small=False):
    """The chameleon in profile, as the original: its tail curled in a spiral, its turret eye the
    landing (gold, with the pupil turned to the entry)."""
    c = CARDS["figcraft"]
    doc, X, F = start("interface design, A2", c)
    ink = ink_of(c)
    spiral = []
    for k in range(40):
        t = k / 39
        a = -math.pi * 0.5 - t * 2 * math.pi * 1.25
        r = 3.4 * (1 - 0.72 * t)
        spiral.append((6.4 + r * math.cos(a), 14.0 + r * math.sin(a)))
    spiral = [(8.2, 11.2), (7.0, 10.7)] + spiral
    g(doc, rib(spiral, 1.6 if not small else 2.0), small=small)
    body = P("M6.8 10.4 C7.2 7.2 10.0 5.0 13.2 5.0 C14.4 4.2 15.8 4.0 17.0 4.6 C17.4 6.2 17.8 7.4 18.4 8.6 "
             "C18.8 9.6 18.4 10.8 17.4 11.4 C16.0 12.0 14.4 12.2 13.0 12.4 C11.0 12.8 9.0 12.6 7.6 12.0 C6.8 11.6 6.6 11.0 6.8 10.4 Z")
    g(doc, body, small=small)
    g(doc, rib([(10.0, 12.2), (10.4, 15.0), (11.6, 16.2)], 1.0 if not small else 1.3) + rib([(14.6, 12.0), (15.0, 15.0), (16.2, 16.2)], 1.0 if not small else 1.3), small=small)
    g(doc, rib([(8.0, 16.6), (17.6, 16.6)], 0.9), shade(c, -5), small, "accent")
    if not small:
        for i in range(4):
            flat(doc, disc(9.0 + i * 1.6, 9.4 + (i % 2) * 0.6, 0.45), T.leaf(c))
    g(doc, disc(15.2, 7.6, 2.0 if not small else 2.2), GOLD, small, "accent")
    flat(doc, disc(14.8, 7.3, 0.7 if not small else 0.9), ink)
    return finish(doc, "figcraft")


def effectcraft(small=False):
    """The unicorn's head in profile, as the original; its mane is ruyi cloud curls (the Chinese
    auspicious cloud) and its horn, spiralled, is the gold landing."""
    c = CARDS["effectcraft"]
    doc, X, F = start("motion graphics, A2", c)
    ink = ink_of(c)
    if not small:
        for (x, y, r) in ((6.0, 6.6, 1.8), (4.8, 9.4, 1.9), (4.6, 12.6, 2.0), (5.4, 15.8, 2.0), (7.6, 5.2, 1.4)):
            g(doc, disc(x, y, r), T.leaf(c), small)
    else:
        g(doc, disc(5.2, 10.0, 2.6) + disc(5.4, 14.6, 2.4), T.leaf(c), small)
    head = P("M8.0 6.4 C8.4 5.2 9.0 4.2 9.6 3.6 C10.0 4.6 10.4 5.4 10.6 6.0 C12.6 6.2 14.2 7.4 15.4 9.2 "
             "C16.4 10.8 17.4 12.2 17.8 13.4 C18.0 14.4 17.4 15.2 16.4 15.2 C15.4 15.2 14.6 14.6 13.8 14.0 "
             "C12.8 13.4 11.8 13.6 11.4 14.4 C11.0 15.6 11.4 17.0 12.0 18.4 L6.8 18.4 "
             "C6.4 15.6 6.4 12.6 6.8 10.0 C7.0 8.6 7.4 7.4 8.0 6.4 Z")
    g(doc, head, small=small)
    horn = P("M11.0 6.2 L16.6 2.6 L12.2 7.6 Z")
    g(doc, horn, GOLD, small, "accent")
    if not small:
        for k in range(3):
            t = 0.25 + 0.22 * k
            x, y = 11.0 + (16.6 - 11.0) * t, 6.2 + (2.6 - 6.2) * t
            flat(doc, rib([(x - 0.2, y + 0.3), (x + 0.5, y + 0.9)], 0.25), shade(GOLD, -6))
    flat(doc, ell(12.6, 9.4, 0.9 if not small else 1.1, 0.6 if not small else 0.8, rot=20), ink)
    flat(doc, disc(16.6, 13.6, 0.35 if not small else 0.5), ink)
    return finish(doc, "effectcraft")


def lightcraft(small=False):
    """The lynx, frontal, with its ear tufts and cheek ruff, as the original; its eyes, jade, catch
    the light: the landing."""
    c = CARDS["lightcraft"]
    doc, X, F = start("photo library, A2", c)
    ink = ink_of(c)
    for sx in (-1, 1):
        g(doc, rib([(10.5 + sx * 5.4, 4.6), (10.5 + sx * 5.8, 2.8)], 0.7), ink, small)
    head = sym(10.5, 6.6, [((9.4, 6.6), (8.2, 6.6), (7.2, 7.0)), ((6.4, 6.0), (5.6, 5.0), (5.0, 4.4)),
                           ((4.6, 6.4), (4.6, 8.6), (5.0, 10.0)), ((4.0, 11.6), (3.2, 13.6), (2.8, 15.4)),
                           ((4.8, 15.6), (6.0, 16.2), (7.0, 17.4)), ((8.0, 18.0), (9.2, 18.4), (10.5, 18.4))])
    g(doc, head, small=small)
    if not small:
        flat(doc, P("M5.6 5.8 C6.2 6.4 6.6 7.0 6.8 7.4 L5.4 8.8 C5.3 7.8 5.4 6.8 5.6 5.8 Z"), ink)
        flat(doc, P("M15.4 5.8 C14.8 6.4 14.4 7.0 14.2 7.4 L15.6 8.8 C15.7 7.8 15.6 6.8 15.4 5.8 Z"), ink)
        for sx in (-1, 1):
            for k in range(3):
                x = 10.5 + sx * (4.0 + k * 0.9)
                flat(doc, rib([(x, 13.0 + k * 0.5), (x + sx * 0.9, 14.6 + k * 0.4)], 0.32), T.leaf(c))
    for sx in (-1, 1):
        g(doc, ell(10.5 + sx * 2.4, 10.6, 1.25 if not small else 1.4, 0.95 if not small else 1.1, rot=sx * 12), JADE, small, "accent")
        flat(doc, ell(10.5 + sx * 2.4, 10.6, 0.32 if not small else 0.45, 0.8 if not small else 0.9), ink)
    flat(doc, P("M9.6 13.2 L11.4 13.2 L10.5 14.4 Z"), shade(c, -4))
    flat(doc, rib([(9.0, 15.4), (10.5, 15.0), (12.0, 15.4)], 0.35), ink)
    return finish(doc, "lightcraft")


def materialcraft(small=False):
    """The rhino's head in profile, as the original (facing right); the great horn, gold, is the
    landing."""
    c = CARDS["materialcraft"]
    doc, X, F = start("procedural materials, A2", c)
    ink = ink_of(c)
    head = P("M3.4 9.4 C4.0 7.6 5.6 6.8 7.4 6.8 C8.6 6.8 9.6 7.2 10.6 7.8 C12.0 8.6 13.4 9.4 14.4 10.4 "
             "C15.6 11.4 17.2 12.0 18.0 13.0 C18.6 13.8 18.2 15.0 17.2 15.4 C15.6 16.0 13.8 16.2 12.0 16.4 "
             "C10.2 16.6 8.6 17.2 7.4 18.4 L3.4 18.4 Z")
    g(doc, head, small=small)
    g(doc, P("M6.0 7.2 C5.8 5.8 6.0 4.4 6.8 3.6 C7.4 4.8 8.0 6.0 8.4 7.0 Z"), small=small)    # the ear
    g(doc, P("M14.6 10.6 C15.6 8.0 17.0 5.4 18.4 3.8 C18.2 6.4 17.8 9.6 17.2 12.0 Z"), GOLD, small, "accent")
    g(doc, P("M12.0 9.0 C12.4 7.8 13.0 6.8 13.6 6.2 C13.6 7.4 13.4 8.6 13.2 9.6 Z"), GOLD, small, "accent")
    flat(doc, ell(11.0, 11.0, 0.7 if not small else 0.9, 0.5 if not small else 0.7, rot=-20), ink)
    if not small:
        flat(doc, rib([(5.2, 12.0), (7.0, 13.6), (9.6, 14.4)], 0.4), T.leaf(c))
        flat(doc, rib([(6.6, 9.4), (8.4, 10.8)], 0.35), T.leaf(c))
        flat(doc, ell(16.6, 14.2, 0.4, 0.25), ink)
    return finish(doc, "materialcraft")


def texturecraft(small=False):
    """The zebra's head, as the original (three-quarter, facing left); its stripes are the
    texture, in the card's deep tone; the mane, gold, is the landing."""
    c = CARDS["texturecraft"]
    doc, X, F = start("texture painting, A2", c)
    ink = ink_of(c)
    head = P("M10.6 4.6 C11.6 3.4 12.2 2.8 12.8 2.8 C13.0 3.8 13.0 4.8 12.8 5.6 C14.6 7.0 15.8 9.4 16.2 12.0 "
             "C16.6 14.6 17.4 16.6 18.2 18.4 L11.2 18.4 C10.6 16.6 9.6 15.6 8.0 15.4 C6.6 15.6 5.2 15.6 4.4 14.8 "
             "C3.6 14.0 3.8 12.6 4.6 11.6 C5.8 10.0 7.0 8.4 8.0 7.0 C8.2 5.8 8.0 4.4 8.2 3.4 C9.2 3.6 10.0 4.0 10.6 4.6 Z")
    g(doc, head, small=small)
    cid = doc.id("zc")
    doc.defs.append(f'<clipPath id="{cid}"><path d="{head}"/></clipPath>')
    stripes = [((9.4, 7.6), (12.6, 8.4), (15.4, 6.8)), ((7.6, 9.8), (12.4, 11.0), (16.0, 9.6)),
               ((6.0, 12.2), (11.0, 13.2), (16.8, 12.6)), ((10.4, 15.0), (13.6, 15.6), (17.4, 15.4))]
    if small:
        stripes = stripes[1::2]
    sd = "".join(rib([a, b, cc], 0.85 if not small else 1.3) for a, b, cc in stripes)
    doc.add(f'<path d="{sd}" fill="{ink}" clip-path="url(#{cid})"/>')
    flat(doc, ell(4.9, 13.4, 1.3, 1.1), ink)
    flat(doc, ell(9.4, 9.0, 0.7, 0.5, rot=-25) if not small else ell(9.4, 9.0, 0.9, 0.7, rot=-25), WHITE)
    flat(doc, disc(9.4, 9.0, 0.4 if not small else 0.5), ink)
    mane = P("M13.2 5.0 C15.0 5.4 16.8 7.6 17.4 10.0 C17.8 12.4 18.6 14.6 19.2 16.4 C17.6 15.4 16.6 13.6 16.0 12.0 C15.6 9.6 14.6 7.2 13.2 5.0 Z")
    g(doc, mane, GOLD, small, "accent")
    return finish(doc, "texturecraft")


def gridcraft(small=False):
    """The spreadsheet, as the original: a sheet with its header band and grid; the selected cell,
    gold, is the landing."""
    c = CARDS["gridcraft"]
    doc, X, F = start("spreadsheet, A2", c)
    g(doc, FS.page(X, F, 3.5, 3.0, 14.0, 15.0, fold=3.0), small=small)
    flat(doc, rrect(X(5.0), X(4.6), 7.0 * F, 1.0 * F, 0.5 * F), T.leaf(c))
    rows, cols = (4, 3) if not small else (3, 2)
    x0, y0, w, h = 5.0, 7.8, 11.0, 8.6
    for r in range(rows + 1):
        y = y0 + r * h / rows
        flat(doc, rrect(X(x0), X(y) - 0.2 * F, w * F, 0.4 * F, 0.2 * F), T.leaf(c))
    for k in range(cols + 1):
        x = x0 + k * w / cols
        flat(doc, rrect(X(x) - 0.2 * F, X(y0), 0.4 * F, h * F, 0.2 * F), T.leaf(c))
    flat(doc, rrect(X(x0) - 0.2 * F, X(y0) - 0.2 * F, (w / cols) * F + 0.4 * F, h * F + 0.4 * F, 0.2 * F), shade(c, 2))
    r, k = (2, 1) if not small else (1, 1)
    g(doc, rrect(X(x0 + k * w / cols) - 0.3 * F, X(y0 + r * h / rows) - 0.3 * F, (w / cols) * F + 0.6 * F, (h / rows) * F + 0.6 * F, 0.4 * F),
      GOLD, small, "accent")
    return finish(doc, "gridcraft")


FAMILY = ["photocraft", "vectorcraft", "pdfcraft", "wordcraft", "deckcraft", "filmcraft", "soundcraft", "cadcraft",
          "designcraft", "figcraft", "effectcraft", "lightcraft", "materialcraft", "texturecraft", "gridcraft"]
APPS = {"gimp": gimp, **{a: globals()[a] for a in FAMILY}}


def _job(args):
    app, small = args
    d = os.path.join(OUT, "small" if small else "")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{app}.svg")
    open(p, "w").write(APPS[app](small))
    return p


def original(app):
    for nm in ("site-icon-256.png",):
        p = os.path.join(SRC, app, nm)
        if os.path.exists(p):
            return p
    return os.path.join(D, "icons", "store", f"{app}.svg")


def _score(p):
    import board as B
    import craft
    s = B.scored(p, "icon")
    if not p.endswith(".svg"):
        return s, []
    c = craft.check(p)
    return s, [k for k, (ok, _) in c.items() if not ok]


def sheet(apps, out, title):
    """Original (top) vs A2 (bottom) with the brand score and the craft checks; 16/32/64 px row."""
    import board as B
    from par import fanout
    from PIL import Image, ImageDraw
    cur = [original(a) for a in apps]
    new = [os.path.join(OUT, f"{a}.svg") for a in apps]
    sm = [os.path.join(OUT, "small", f"{a}.svg") for a in apps]
    res = fanout(_score, cur + new + sm)
    k = len(apps)
    per = min(k, 6)
    rows = (k + per - 1) // per
    cw, pad, rh = 230, 24, 700
    W, H = max(pad + per * (cw + pad), 40 + 11 * len(title)), 50 + rows * rh
    im = Image.new("RGB", (W, H), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((pad, 10), title, font=B.font(20, True), fill=B.INK)
    table = {}
    for i, a in enumerate(apps):
        x = pad + (i % per) * (cw + pad)
        y0 = 50 + (i // per) * rh
        (sa, _), (sb, fb), (_, fs) = res[i], res[k + i], res[2 * k + i]
        for row, (p, s) in enumerate(((cur[i], sa), (new[i], sb))):
            y = y0 + row * 300
            ic = B.raster(p, 200, 200)
            im.paste(ic, (x + 10, y), ic)
            col = B.INK if row == 0 else (B.GOOD if sb["total"] > sa["total"] else B.BAD)
            dr.text((x + 10, y + 208), f"{LABEL.get(a, a)}  {s['total']:.1f}", font=B.font(17, True), fill=col)
        for j, sz in enumerate((16, 32, 64)):
            t = B.raster(sm[i] if sz <= 32 else new[i], sz, sz)
            im.paste(t, (x + 10 + j * 60, y0 + 560 + (64 - sz) // 2), t)
        bad = sorted(set(fb) | set(fs))
        dr.text((x + 10, y0 + 640), "craft: pass" if not bad else "craft FAIL: " + ", ".join(bad), font=B.font(13, True), fill=B.GOOD if not bad else B.BAD)
        table[a] = (sa["total"], sb["total"], bad, {r: (sa[r]["score"], sb[r]["score"]) for r in B.SC.RULES})
    im.save(out)
    return table


LABEL = {}


def main(argv):
    from par import fanout
    names = [a for a in argv if not a.startswith("--") and a in APPS] or list(APPS)
    fanout(_job, [(a, sm) for a in names for sm in (False, True)])
    for flag in ("--sheet",):
        if flag in argv:
            t = sheet(names, argv[argv.index(flag) + 1], "Third-party apps in Type A2: original (top) vs A2 (bottom), brand score 0-100, craft checks")
            for a, (o, n, bad, rules) in t.items():
                print(f"{a:14s} {o:5.1f} -> {n:5.1f}  craft {'pass' if not bad else bad}  " +
                      " ".join(f"{r} {x:.0f}/{y:.0f}" for r, (x, y) in rules.items()))


if __name__ == "__main__":
    main(sys.argv[1:])
