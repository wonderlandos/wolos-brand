# SPDX-License-Identifier: GPL-2.0-or-later
"""The three signature candidates as rendered 3D objects (walls_ribbon.py): swept ribbons with key light,
ambient fill, rim, thickness, self-occlusion and contact shadow, matte, no streamline ends inside the frame
(every ribbon enters from outside and leaves outside; the ring is closed)."""
import math

from walls_ribbon import Scene, ribbon
from walls_flow import matte_backdrop, quiet_accent, grain


def _asp(fr):
    return fr.w / fr.h


def _c(fr, pts):
    a = _asp(fr)
    return [(x * a, y, z) for x, y, z in pts]


def bundle(sc, fr, base, n, dy, dz, wbase, theta_fn, chroma=5.5, fade_far=0.35):
    for j in range(n):
        o = j - (n - 1) / 2
        ctrl = _c(fr, [(x, y + dy * o, z + dz * o) for x, y, z in base])
        w = wbase * (0.8 + 0.4 * ((j * 5) % 7) / 6)
        strips = ribbon(ctrl, lambda s, w=w: w * (0.92 + 0.08 * math.sin(6.28 * s * 1.3 + j)), lambda s, j=j: theta_fn(s, j), N=170, M=3, cup=0.13)
        far = max(0.0, min(1.0, (0.5 - (o * dz)) * 0.8 - 0.2)) * fade_far
        sc.add(strips, tone=(0.0, 1.0), fade=far, chroma=chroma, emit=(lambda s: 0.05 + 0.85 * s ** 2) if sc.night else None)


def form_3d_juzhe(doc, fr, P):
    """A, the lifted eave. Reading: falls from the light NO in the juzhe fold, flattens across the middle and
    leaves by the lifted eave at the right edge; the SE is where the bundle is closest and gold shows through."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    matte_backdrop(doc, fr, P)
    quiet_accent(doc, fr, P, 0.78 * W, 0.70 * H, 0.22 * H)
    sc = Scene(doc, fr, P, night)
    base = [(-0.20, -0.16, 0.0), (0.04, -0.10, 0.04), (0.20, 0.20, 0.12), (0.34, 0.50, 0.18), (0.54, 0.66, 0.12), (0.80, 0.68, 0.02), (1.02, 0.58, -0.04), (1.25, 0.38, -0.10)]
    bundle(sc, fr, base, 6, 0.085, 0.10, 0.18, lambda s, j: 0.55 + 1.15 * math.sin(2 * math.pi * (s * 1.1 + j * 0.07)))
    sc.render(shadow_op=0.22, glow=night)
    grain(doc, fr, P)


def form_3d_fold(doc, fr, P):
    """B, the screen fold. Reading: enters by the light NO, turns over once at the fold (the ribbon shows its other
    face), and leaves by the right edge; the SE is where the bundle comes closest."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    matte_backdrop(doc, fr, P)
    quiet_accent(doc, fr, P, 0.74 * W, 0.72 * H, 0.22 * H)
    sc = Scene(doc, fr, P, night)
    base = [(-0.20, 0.08, 0.0), (0.12, 0.06, 0.06), (0.34, 0.28, 0.20), (0.44, 0.58, 0.16), (0.62, 0.78, 0.0), (0.90, 0.76, -0.08), (1.22, 0.54, -0.10)]
    bundle(sc, fr, base, 6, 0.08, 0.10, 0.17, lambda s, j: 2 * math.pi * 0.95 * s + 0.35 + j * 0.28)
    sc.render(shadow_op=0.22, glow=night)
    grain(doc, fr, P)


def form_3d_gate(doc, fr, P):
    """C, the gate in the flow (the WolOS signature). Reading: ribbons enter by the light NO, part around a closed ring
    (the moon gate), pass above and below it and leave by the right and bottom edges; the ring has no end, nothing
    crosses its void (clean ground for the windows), and the SE is where the ribbons gather."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    a = _asp(fr)
    matte_backdrop(doc, fr, P)
    quiet_accent(doc, fr, P, 0.84 * W, 0.80 * H, 0.24 * H)
    sc = Scene(doc, fr, P, night)
    cx, cy, R = 0.58 * a, 0.50, 0.23
    ring = [(cx + R * math.cos(2 * math.pi * k / 12), cy + R * 0.82 * math.sin(2 * math.pi * k / 12), R * 0.5 * math.sin(2 * math.pi * k / 12)) for k in range(12)]
    em = (lambda s: 0.85) if night else None
    # through ribbons: far ones first; two above the ring, two below, none across the void
    paths = [
        (-0.22, [(-0.22, 0.04), (0.15, 0.03), (0.45, 0.09), (0.70, 0.15), (0.89, 0.40), (1.03, 0.68), (1.24, 0.80)], 0.16, 0.24),
        (-0.12, [(-0.22, 0.52), (0.10, 0.80), (0.40, 0.92), (0.64, 0.92), (0.84, 0.86), (1.03, 0.84), (1.24, 0.86)], 0.17, 0.16),
        (0.16, [(-0.22, 0.27), (0.10, 0.18), (0.40, 0.15), (0.66, 0.18), (0.87, 0.44), (1.03, 0.72), (1.24, 0.88)], 0.13, 0.10),
        (0.30, [(-0.22, 0.58), (0.12, 0.86), (0.40, 0.99), (0.70, 1.04), (0.92, 1.10), (1.1, 1.2)], 0.20, 0.08),
    ]
    for j, (z, pts, w, fade) in enumerate(paths):
        ctrl = _c(fr, [(x, y, z + 0.015 * i) for i, (x, y) in enumerate(pts)])
        st = ribbon(ctrl, lambda s, w=w: w * (0.94 + 0.06 * math.sin(6.28 * s + j)), lambda s, j=j: 0.55 + 0.9 * math.sin(2 * math.pi * (s * 0.9 + j * 0.17)), N=190, M=3, cup=0.13)
        sc.add(st, tone=(0.0, 0.62 if night else 0.9), fade=fade if z < 0 else 0.0, chroma=5.5, emit=(lambda s: 0.03 + 0.25 * s ** 2) if night else None, fibres=False)
    # the ring: closed, one full twist, the light of the night
    strips = ribbon(ring, lambda s: 0.115, lambda s: 2 * math.pi * s + 0.4, N=200, M=4, cup=0.12, closed=True, ref=lambda p: (p[0] - cx, p[1] - cy, 0.0))
    sc.add(strips, tone=(0.15, 0.88), chroma=4.5, emit=em)
    sc.render(shadow_op=0.22, glow=night)
    grain(doc, fr, P)
