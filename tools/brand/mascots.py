# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""WolOS mascots (the Rabbit ships; the Cheshire Cat is the alternative).  python3 -I mascots.py <src dir> <concept dir>
Construction (both characters): unit u = 16 px on a 512-wide canvas.
One outline weight (10 px = 0.625u, round joins), flat fills, no gradients.
Eyes are solid ink capsules (1.5u x 2.25u) with one white catch-light (r 0.4u) top-right.
Pink #F5A9B8 and blue #5BCEFA come from the doctrine band; violet from tokens.accent."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marks import svg, ACC, ACC_D, PAPER, INK
from outline import stroke, rect_d, ellipse_d, circle_d, dashes, polyline_d

LINE = "#2B2140"      # outline ink (tokens text, tinted violet)
LW = 10
PINK = "#F5A9B8"
BLUE = "#5BCEFA"
WHITE = "#FFFFFF"
GOLD = "#FFCC00"      # tokens light.yellow
DEEP = "#5B3BE8"

# Fill-only drawing: no SVG stroke is used anywhere.  shp() paints a shape and, on top, its
# outline expanded to a filled ring (outline.stroke); ln() paints an open line the same way.
def shp(d, fill, line=True, w=LW, color=LINE):
    return f'<path d="{d}" fill="{fill}"/>' + (f'<path d="{stroke(d, w)}" fill="{color}"/>' if line else "")

def ln(d, w=LW, color=LINE, butt=False):
    return f'<path d="{stroke(d, w, butt=butt)}" fill="{color}"/>'

def cap(cx, cy, w, h, ang=0, fill=WHITE, line=True, pivot=None):
    px, py = pivot or (cx, cy + h / 2)
    return (f'<g transform="rotate({ang:g} {px:g} {py:g})">'
            + shp(rect_d(cx - w / 2, cy - h / 2, w, h, w / 2), fill, line) + '</g>')

def eye(x, y, kind="open", look=0):
    if kind == "open":
        return (f'<rect x="{x - 12 + look:g}" y="{y - 18:g}" width="24" height="36" rx="12" fill="{LINE}"/>'
                f'<circle cx="{x + 4 + look:g}" cy="{y - 8:g}" r="6" fill="{WHITE}"/>')
    if kind == "big":
        return (f'<circle cx="{x:g}" cy="{y:g}" r="20" fill="{LINE}"/><circle cx="{x + 7:g}" cy="{y - 7:g}" r="7" fill="{WHITE}"/>')
    if kind == "happy":   # ^ arcs
        return ln(f"M{x - 15:g} {y + 6:g}Q{x:g} {y - 18:g} {x + 15:g} {y + 6:g}")
    if kind == "closed":  # sleepy: u arcs
        return ln(f"M{x - 15:g} {y:g}Q{x:g} {y + 14:g} {x + 15:g} {y:g}")
    if kind == "wink":
        return ln(f"M{x - 15:g} {y:g}H{x + 15:g}")
    raise ValueError(kind)

# ------------------------------------------------------------------ Mascot 1: the Rabbit
def rabbit_head(cx=256, cy=272, ears=(-8, 8), fold=None, eyes=("open", "open"), look=0, mouth="w",
                brows=None, extra="", tilt=0):
    r = 112
    out = [f'<g transform="rotate({tilt} {cx} {cy + r})">']
    for i, (side, ang) in enumerate(zip((-1, 1), ears)):
        ex = cx + side * 48
        top = cy - r - 128
        h = cy - top
        ear = cap(ex, top + h / 2, 64, h, ang, WHITE, True, (ex, cy))
        inner = cap(ex, top + h / 2 - 4, 28, h - 92, ang, PINK, False, (ex, cy))
        if fold is not None and fold == i:   # tip folds forward: ear shorter, flap drawn as second capsule
            h2 = h - 70
            ear = cap(ex, cy - h2 / 2, 64, h2, ang, WHITE, True, (ex, cy))
            inner = cap(ex, cy - h2 / 2 - 4, 28, h2 - 92, ang, PINK, False, (ex, cy))
            a = math.radians(ang)
            tx, ty = ex + math.sin(a) * h2, cy - math.cos(a) * h2
            flap = cap(tx + side * 30, ty + 8, 60, 96, ang + side * 62, WHITE, True, (tx, ty + 24))
            inner += flap
        out += [ear, inner]
    out.append(shp(circle_d(cx, cy, r), WHITE))
    out.append(f'<circle cx="{cx - 70}" cy="{cy + 44}" r="17" fill="{PINK}" opacity=".7"/>'
               f'<circle cx="{cx + 70}" cy="{cy + 44}" r="17" fill="{PINK}" opacity=".7"/>')
    out.append(eye(cx - 42, cy + 2, eyes[0], look) + eye(cx + 42, cy + 2, eyes[1], look))
    if brows == "worried":
        out.append(ln(f"M{cx - 60} {cy - 30}L{cx - 26} {cy - 42}M{cx + 60} {cy - 30}L{cx + 26} {cy - 42}"))
    if brows == "up":
        out.append(ln(f"M{cx - 58} {cy - 44}Q{cx - 42} {cy - 54} {cx - 26} {cy - 44}M{cx + 26} {cy - 44}Q{cx + 42} {cy - 54} {cx + 58} {cy - 44}"))
    out.append(shp(f"M{cx - 9} {cy + 32}H{cx + 9}L{cx} {cy + 42}Z", PINK, True, 6, PINK))
    m = {"w": ln(f"M{cx - 20} {cy + 52}Q{cx - 10} {cy + 62} {cx} {cy + 50}Q{cx + 10} {cy + 62} {cx + 20} {cy + 52}"),
         "smile": shp(f"M{cx - 26} {cy + 50}Q{cx} {cy + 82} {cx + 26} {cy + 50}Z", LINE),
         "o": f'<ellipse cx="{cx}" cy="{cy + 64}" rx="11" ry="14" fill="{LINE}"/>',
         "flat": ln(f"M{cx - 14} {cy + 58}Q{cx} {cy + 52} {cx + 14} {cy + 58}"),
         }[mouth]
    out.append(m)
    out.append(extra)
    out.append("</g>")
    return "".join(out)

def rabbit_pose():
    torso = "M150 470 C150 410 200 380 256 380 C312 380 362 410 362 470 V520 C362 566 316 590 256 590 C196 590 150 566 150 520 Z"
    body = (cap(150, 478, 44, 124, 18, WHITE, True, (166, 424))
            + cap(372, 450, 44, 120, -48, WHITE, True, (352, 424))
            + shp(ellipse_d(196, 598, 54, 28), WHITE) + shp(ellipse_d(316, 598, 54, 28), WHITE)
            + f'<defs><clipPath id="torso"><path d="{torso}"/></clipPath></defs>'
            f'<path d="{torso}" fill="{WHITE}"/>'
            # waistcoat: accent panel, clipped to the torso so it shares its outline
            + f'<path d="M192 396 L256 470 L320 396 H420 V640 H90 V396 Z" fill="{ACC}" clip-path="url(#torso)"/>'
            + ln("M192 396L256 470L320 396M256 470V590")
            + ln(torso)
            + f'<circle cx="240" cy="504" r="7" fill="{GOLD}"/><circle cx="240" cy="540" r="7" fill="{GOLD}"/>')
    chain = "".join(ln(polyline_d(r), 6, GOLD) for r in dashes("M240 504C290 534 340 514 380 470", 2, 10))   # dotted chain
    watch = (chain
             + shp(circle_d(418, 394, 40), GOLD) + f'<circle cx="418" cy="394" r="26" fill="{WHITE}"/>'
             + ln("M418 394V376M418 394L430 402", 6)
             + shp(rect_d(410, 342, 16, 12, 4), GOLD))
    bow = shp("M256 386L222 368V406ZM256 386L290 368V406Z", ACC) + shp(circle_d(256, 386, 10), ACC)
    return body + rabbit_head() + bow + watch

def zed(x, y, size):
    """A drawn 'z' (no font): baseline at y, left edge x, `size` tall."""
    w, t = size * 0.62, size * 0.2
    return ln(f"M{x + t / 2:g} {y - size + t / 2:g}H{x + w:g}L{x + t / 2:g} {y - t / 2:g}H{x + w:g}", t, ACC)

RABBIT_EXPR = [
    ("neutral", dict()),
    ("happy", dict(eyes=("happy", "happy"), mouth="smile")),
    ("curious", dict(ears=(-4, 30), look=8, tilt=-8, brows="up")),
    ("late!", dict(ears=(-24, 24), brows="worried", mouth="o",
                   extra=shp("M392 232Q406 256 392 268Q378 256 392 232Z", BLUE, True, 6))),
    ("sleepy", dict(ears=(-30, 30), eyes=("closed", "closed"), mouth="flat",
                    extra=zed(96, 190, 44) + zed(66, 150, 30))),
    ("surprised", dict(ears=(-2, 2), eyes=("big", "big"), mouth="o", brows="up")),
]

def rabbit_svg():
    """The White Rabbit, neutral, on a square canvas (the PNGs the apps load are 256 and 512)."""
    return svg((-74, 0, 660, 660), rabbit_pose(), 512, 512, "The White Rabbit")


# where the figure's feet meet the ground, in the coordinates of rabbit_pose()
FEET = (256, 626)


def rabbit_peek():
    """320 x 200 lock-screen peek: the Rabbit looks up over the bottom edge, paws on it."""
    head = rabbit_head(ears=(-6, 9), tilt=-5, look=-5)
    paws = "".join(shp(ellipse_d(px, 196, 24, 15), WHITE) +
                   ln(f"M{px - 6} 187Q{px - 4} 195 {px - 6} 201M{px + 5} 187Q{px + 7} 195 {px + 5} 201", 5)
                   for px in (112, 208))
    g = f'<g transform="translate(6 -7) scale(.6)">{head}</g>' + paws
    return svg((0, 0, 320, 200), g, 320, 200, "Hello again")


# ------------------------------------------------------------------ Mascot 2: the Cheshire Cat
def cat_head(cx=256, cy=260, eyes="open", grin="grin", fade=1.0, tilt=0, extra=""):
    o = []
    g = f'<g opacity="{fade}">'
    # ears: rounded triangles
    ear = lambda s: (shp(f"M{cx + s * 128} {cy - 20}L{cx + s * 118} {cy - 142}L{cx + s * 44} {cy - 92}Z", ACC_D)
                     + shp(f"M{cx + s * 110} {cy - 52}L{cx + s * 106} {cy - 114}L{cx + s * 70} {cy - 88}Z", PINK, True, 8, PINK))
    o.append(g + ear(-1) + ear(1))
    o.append(shp(ellipse_d(cx, cy, 150, 116), ACC_D))
    # forehead stripes
    o.append(ln(f"M{cx} {cy - 112}V{cy - 78}M{cx - 36} {cy - 108}L{cx - 30} {cy - 82}M{cx + 36} {cy - 108}L{cx + 30} {cy - 82}", 12, DEEP))
    o.append(ln(f"M{cx - 150} {cy + 6}H{cx - 118}M{cx - 148} {cy + 34}H{cx - 120}M{cx + 150} {cy + 6}H{cx + 118}M{cx + 148} {cy + 34}H{cx + 120}", 12, DEEP))
    for s in (-1, 1):
        ex, ey = cx + s * 58, cy - 26
        if eyes in ("open", "smug", "look", "wide"):
            ry = {"open": 24, "smug": 24, "look": 24, "wide": 30}[eyes]
            o.append(shp(ellipse_d(ex, ey, 32, ry), GOLD))
            px = ex + (10 if eyes == "look" else 0)
            pw = 8 if eyes != "wide" else 18
            o.append(f'<rect x="{px - pw / 2}" y="{ey - ry + 6}" width="{pw}" height="{2 * ry - 12}" rx="{pw / 2}" fill="{LINE}"/>'
                     f'<circle cx="{ex + 14}" cy="{ey - 10}" r="5" fill="{WHITE}"/>')
            if eyes == "smug":   # heavy upper lid
                o.append(shp(f"M{ex - 32} {ey + 2}A32 {ry} 0 0 1 {ex + 32} {ey + 2}Z", ACC_D))
        elif eyes == "closed":
            o.append(ln(f"M{ex - 26} {ey}Q{ex} {ey + 16} {ex + 26} {ey}"))
        elif eyes == "happy":
            o.append(ln(f"M{ex - 26} {ey + 8}Q{ex} {ey - 20} {ex + 26} {ey + 8}"))
    o.append(shp(f"M{cx - 12} {cy + 4}H{cx + 12}L{cx} {cy + 16}Z", PINK, True, 8, PINK))
    o.append("</g>")
    # the grin never fades: it is the cat's one constant
    G = {"grin": (shp(f"M{cx - 104} {cy + 22}Q{cx} {cy + 58} {cx + 104} {cy + 22}Q{cx + 64} {cy + 104} {cx} {cy + 104}Q{cx - 64} {cy + 104} {cx - 104} {cy + 22}Z", WHITE)
                  + ln(f"M{cx - 104} {cy + 22}Q{cx} {cy + 86} {cx + 104} {cy + 22}", 6)
                  + "".join(ln(f"M{cx + t} {cy + 40 + abs(t) * -0.12:g}V{cy + 100 - abs(t) * 0.28:g}", 6) for t in (-60, -30, 0, 30, 60))),
         "small": ln(f"M{cx - 40} {cy + 38}Q{cx - 20} {cy + 54} {cx} {cy + 36}Q{cx + 20} {cy + 54} {cx + 40} {cy + 38}"),
         "o": f'<ellipse cx="{cx}" cy="{cy + 56}" rx="20" ry="24" fill="{LINE}"/>',
         }[grin]
    return f'<g transform="rotate({tilt} {cx} {cy + 116})">' + "".join(o) + G + extra + "</g>"

def cat_pose(fade=1.0):
    tail = ('M330 600 C430 600 470 520 440 450 C420 400 360 410 372 452')
    body = (f'<g opacity="{fade}">'
            + ln(tail, 44 + 2 * LW)
            + ln(tail, 44, ACC_D)
            + "".join(ln(polyline_d(r), 44, DEEP, butt=True) for r in dashes(tail, 16, 30, -20))
            + shp("M166 600C150 520 176 400 256 372C336 400 362 520 346 600Z", ACC_D)
            + ln("M200 470Q214 476 228 470M190 520Q206 528 222 520M284 470Q298 476 312 470M290 520Q306 528 322 520", 12, DEEP)
            + f'<path d="M256 420 C226 440 220 520 230 600 H282 C292 520 286 440 256 420 Z" fill="#CFC4FF"/>'
            + shp(ellipse_d(210, 600, 40, 22), ACC_D) + shp(ellipse_d(302, 600, 40, 22), ACC_D)
            + '</g>')
    return body + cat_head(256, 270, fade=fade)

CAT_EXPR = [
    ("neutral", dict()),
    ("happy", dict(eyes="happy")),
    ("smug", dict(eyes="smug")),
    ("curious", dict(eyes="look", grin="small", tilt=8,
                     extra=f'<text x="384" y="170" font-family="Inter, sans-serif" font-weight="700" font-size="60" fill="{ACC}">?</text>')),
    ("surprised", dict(eyes="wide", grin="o")),
    ("vanishing", dict(fade=0.18)),
]

def sheet(title, pose, exprs, headfn, path, bg=PAPER, fg=INK, vb_head=(56, 56, 400, 400)):
    # pose left (512x640), 3x2 expression grid right (6 x 240)
    W, H = 512 + 3 * 240 + 64, 760
    out = [f'<rect width="{W}" height="{H}" fill="{bg}"/>',
           f'<text x="32" y="54" font-family="Inter, sans-serif" font-size="28" font-weight="700" fill="{fg}">{title}</text>',
           f'<g transform="translate(16 90)">{pose}</g>']
    for i, (name, kw) in enumerate(exprs):
        x, y = 560 + (i % 3) * 240, 110 + (i // 3) * 310
        out.append(f'<rect x="{x - 1}" y="{y - 1}" width="226" height="252" rx="19" fill="#DEDEE0"/>'
                   f'<rect x="{x}" y="{y}" width="224" height="250" rx="18" fill="#FFFFFF"/>')
        out.append(f'<svg x="{x + 12}" y="{y + 8}" width="200" height="200" viewBox="{" ".join(map(str, vb_head))}">{headfn(**kw)}</svg>')
        out.append(f'<text x="{x + 112}" y="{y + 234}" text-anchor="middle" font-family="Inter, sans-serif" font-size="20" font-weight="600" fill="#6E6E73">{name}</text>')
    open(path, "w").write(svg((0, 0, W, H), "".join(out), W, H))

if __name__ == "__main__":
    B = sys.argv[2]
    for d in ("mascot-1-rabbit", "mascot-2-cat"):
        os.makedirs(os.path.join(B, d), exist_ok=True)
    open(f"{B}/mascot-1-rabbit/neutral.svg", "w").write(svg((0, 0, 512, 660), rabbit_pose(), 512, 660, "WolOS rabbit, neutral"))
    open(f"{B}/mascot-2-cat/neutral.svg", "w").write(svg((0, 0, 512, 660), cat_pose(), 512, 660, "WolOS Cheshire Cat, neutral"))
    sheet("Mascot 1 · the Rabbit · neutral + expressions", rabbit_pose(), RABBIT_EXPR, rabbit_head,
          f"{B}/mascot-1-rabbit/expressions.svg", vb_head=(16, -24, 480, 480))
    sheet("Mascot 2 · the Cheshire Cat · neutral + expressions", cat_pose(), CAT_EXPR, cat_head,
          f"{B}/mascot-2-cat/expressions.svg", vb_head=(56, 80, 400, 400))
