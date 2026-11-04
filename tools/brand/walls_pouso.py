# SPDX-License-Identifier: GPL-2.0-or-later
"""Pouso (the landing): the WolOS signature. One ribbon of light with a real body enters from outside the
frame at the upper left, makes one calm turn across the upper middle (the spirit screen), and settles
heavy and quiet in the lower-right third, leaving the frame at the bottom. The centre stays empty for
icons and windows. Day: a warm matte surface with thickness, key light upper left, coloured contact
shadow, soft occlusion. Night: the same ribbon as a vein of light over a deep ground. The geometry never
changes between themes; only the dye does (derive() from the theme accent).
Reading: entra pela luz NO, faz uma curva calma no alto, e pousa pesado e quieto no SE."""
import math

from walls_ribbon import Scene, ribbon
from walls_flow import matte_backdrop, quiet_accent, grain
from walls_lib import rad, blurf, lin
from geom import f

BASE = [(-0.16, 0.36, -0.20), (0.10, 0.28, -0.14), (0.32, 0.16, -0.06), (0.52, 0.19, 0.04), (0.66, 0.40, 0.14), (0.72, 0.66, 0.22), (0.74, 0.92, 0.28), (0.75, 1.16, 0.32)]


def _ctrl(fr, dy=0.0, dz=0.0, dx=0.0):
    a = fr.w / fr.h
    return [((x + dx) * a, y + dy, z + dz) for x, y, z in BASE]


def width(s):
    return 0.07 + 0.29 * s ** 1.5          # slim at the entry, heavy at the landing


def theta(s):
    return 0.35 + 0.35 * math.sin(math.pi * s) + 1.5 * math.exp(-((s - 0.40) / 0.10) ** 2)   # one calm turn-over near s = 0.4


def form_pouso(doc, fr, P):
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    matte_backdrop(doc, fr, P)
    quiet_accent(doc, fr, P, 0.70 * W, 0.78 * H, 0.26 * H)
    sc = Scene(doc, fr, P, night)
    # satellites: two slim ribbons that keep company with the hero and part from it at the turn
    for dy, dz, wm in ((-0.05, 0.03, 0.30), (0.055, -0.04, 0.20)):
        st = ribbon(_ctrl(fr, dy, dz), lambda s, wm=wm: width(s) * wm + 0.01, lambda s: theta(s) + 0.9, N=240, M=2, cup=0.10)
        sc.add(st, tone=(0.1, 1.0), chroma=5.0, emit=(lambda s: 0.05 + 0.8 * s ** 2) if night else None, thick=5)
    # the hero
    st = ribbon(_ctrl(fr), width, theta, N=300, M=5, cup=0.14)
    sc.add(st, tone=(0.0, 1.0), chroma=5.5, emit=(lambda s: 1.05 * s ** 2.2) if night else None, thick=lambda s: 4 + 16 * s)
    sc.render(shadow_op=0.22, glow=night)
    grain(doc, fr, P)
