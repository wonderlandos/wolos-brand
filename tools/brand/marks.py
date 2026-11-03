# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""WolOS logo marks A/B/C and the wordmark (hand-written SVG geometry, stdlib only).
Every drawing is fill-only: strokes are expanded to outlines by outline.stroke()."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outline import stroke, circle_d
ACC = "#7C5CFF"      # tokens accent.light
ACC_D = "#8B6CFF"    # tokens accent.dark
DEEP = "#4B2FD6"     # one step darker than accent (depth only)
NIGHT = "#33208A"    # deepest step (depth only)
INK = "#1C1C1E"      # tokens light.text
PAPER = "#F5F5F7"    # tokens light.bg / dark.text
LIGHT = "#E9E3FF"    # accent tint, "light through the door"


def svg(vb, body, w=None, h=None, title="WolOS"):
    x, y, vw, vh = vb
    w = w or vw
    h = h or vh
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {vw} {vh}" width="{w}" height="{h}">'
            f'<title>{title}</title>'
            '<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. WolOS brand. -->'
            f'{body}</svg>\n')

# ---------------------------------------------------------------- A: Ears
# Grid u = 64 (1024 = 16u). Head: circle r = 4u. Ears: capsules 3u wide, 6.5u / 5.5u long,
# leaning out 8 deg / 14 deg from the head centre. Gap between ear and head = 0.75u.
# The eye is a 1u x 1.5u capsule cut out of the head, set right of centre: the rabbit looks ahead.
HEAD = (512, 664, 256)

def _ear(cx, cy, length, ang, w=192):
    # capsule from the head centre outward, rotated ang degrees (0 = straight up)
    return (f'<rect x="{cx - w / 2:g}" y="{cy - length:g}" width="{w}" height="{length + w / 2:g}" rx="{w / 2:g}" '
            f'transform="rotate({ang} {cx} {cy})"/>')

def mark_a(fg=ACC, uid="a", eye=True, bg=None):
    hx, hy, r = HEAD
    ears = _ear(hx - 64, hy, 600, -10) + _ear(hx + 64, hy, 520, 16)
    cut = f'<circle cx="{hx}" cy="{hy}" r="{r + 48}" fill="#000"/>'
    eye_cut = '<rect x="576" y="560" width="72" height="120" rx="36" fill="#000"/>' if eye else ''
    return (f'<defs><mask id="{uid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">'
            f'<rect width="1024" height="1024" fill="#fff"/>{cut}</mask>'
            f'<mask id="{uid}e" maskUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">'
            f'<rect width="1024" height="1024" fill="#fff"/>{eye_cut}</mask></defs>'
            f'<g fill="{fg}" mask="url(#{uid}m)">{ears}</g>'
            f'<circle cx="{hx}" cy="{hy}" r="{r}" fill="{fg}" mask="url(#{uid}e)"/>')

def mark_a16(fg=ACC):
    return (f'<defs><mask id="a16" maskUnits="userSpaceOnUse" x="0" y="0" width="16" height="16"><rect width="16" height="16" fill="#fff"/>'
            '<rect x="9" y="8.5" width="1.5" height="2.25" rx=".75" fill="#000"/></mask></defs>'
            f'<g fill="{fg}"><circle cx="8" cy="10.75" r="4.25" mask="url(#a16)"/>'
            '<rect x="3.6" y="0.6" width="3" height="5.6" rx="1.5" transform="rotate(-10 5.1 6.2)"/>'
            '<rect x="9.4" y="1.8" width="3" height="4.6" rx="1.5" transform="rotate(16 10.9 6.4)"/></g>')

# ---------------------------------------------------------------- B: W keyhole
def mark_b(fg=ACC, uid="b"):
    w = stroke("M200 296 V600 A156 156 0 0 0 512 600 A156 156 0 0 0 824 600 V296", 128)
    return (f'<path d="{w}" fill="{fg}"/>'
            f'<circle cx="512" cy="344" r="112" fill="{fg}"/>'
            f'<path d="M468 400 H556 Q576 480 576 600 H448 Q448 480 468 400 Z" fill="{fg}"/>')

def mark_b16(fg=ACC):
    w = stroke("M3 5V10A2.5 2.5 0 0 0 8 10V8", 2) + stroke("M8 8V10A2.5 2.5 0 0 0 13 10V5", 2)
    return (f'<path d="{w}" fill="{fg}"/>'
            f'<circle cx="8" cy="4.75" r="2" fill="{fg}"/><path d="M7.25 6h1.5L9 8.5H7z" fill="{fg}"/>')

# ---------------------------------------------------------------- C: Door
def door_geo(x0, x1, yb):
    r = (x1 - x0) / 2
    return x0, x1, yb, yb - 700 * (x1 - x0) / 640 + r, r

def door(x0, x1, yb):
    _, _, _, ya, r = door_geo(x0, x1, yb)
    return f"M{x0:g} {yb:g}V{ya:g}A{r:g} {r:g} 0 0 1 {x1:g} {ya:g}V{yb:g}Z"

def door_boxes(n=4, vx=512, vy=880, s=0.70):
    out = []
    x0, x1, yb = 192, 832, 880
    for i in range(n):
        out.append((x0, x1, yb))
        x0, x1, yb = vx + (x0 - vx) * s, vx + (x1 - vx) * s, vy + (yb - vy) * s
    return out

def doors(n=4):
    return [door(*b) for b in door_boxes(n)]

def mark_c(cols=(ACC, DEEP, NIGHT, LIGHT)):
    return "".join(f'<path d="{d}" fill="{c}"/>' for d, c in zip(doors(len(cols)), cols))

def ring(outer, inner):
    """Door `outer` minus door `inner` as one path.  Both stand on the same floor line, so the
    result is a plain U with no coincident edges."""
    (x0, x1, yb, ya, r), (ix0, ix1, _, iya, ir) = outer, inner
    return (f"M{x0:g} {yb:g}V{ya:g}A{r:g} {r:g} 0 0 1 {x1:g} {ya:g}V{yb:g}H{ix1:g}V{iya:g}"
            f"A{ir:g} {ir:g} 0 0 0 {ix0:g} {iya:g}V{yb:g}Z")

def mark_c_mono(fg=INK, uid="c"):
    d = [door_geo(*g) for g in door_boxes(4)]
    return f'<path d="{ring(d[0], d[1])}{ring(d[2], d[3])}" fill="{fg}"/>'

def mark_c16(cols=(ACC, LIGHT)):
    return (f'<path d="M3 15V7a5 5 0 0 1 10 0v8z" fill="{cols[0]}"/>'
            f'<path d="M6 15v-4a2 2 0 0 1 4 0v4z" fill="{cols[1]}"/>')


# ---------------------------------------------------------------- Wordmark
# Drawn, not typeset: one 64-unit stroke, round caps, cap height 400 (y 0..400),
# x-height 290. Geometric: o and O are circles, S is two stacked ellipses.
# Letters: W 0..460, o 510..800, l 852..916, O 976..1384, S 1428..1728.  Width 1728.
WM_W, WM_H = 1728, 400

def wordmark(fg=INK, x=0, y=0, scale=1.0):
    t = 64
    h = t / 2
    o = 1428
    S = f"M{o + 252} 65A120 85 0 1 0 {o + 150} 200A120 85 0 1 1 {o + 48} 335"
    d = (stroke(f"M{h} {h}L120 {400 - h}L230 110L340 {400 - h}L{460 - h} {h}", t)
         + stroke(circle_d(655, 400 - 145, 145 - h), t)
         + stroke(f"M884 {h}V{400 - h}", t)
         + stroke(circle_d(1180, 200, 200 - h + 4), t)
         + stroke(S, t))
    return f'<path transform="translate({x:g} {y:g}) scale({scale:g})" d="{d}" fill="{fg}"/>'
