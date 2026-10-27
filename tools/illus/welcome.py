# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Julia Klee
"""Setup Assistant welcome, 480x320: dusk at the garden hedge. The little door is ajar, Wonderland
light pours through it across the grass, and the Rabbit (late, of course) stands in it.
The left 55 % stays calm sky for the title."""
import math
import random
from kit import Canvas, f, path, fluffy, sparkle, svg
from parts import glow, motes
from keyhole import mark_paths
import rabbit

W, H = 480, 320
KX, K = 316, 2.9            # the door: the WolOS keyhole, as a doorway
BASE = 252                  # threshold / foot of the hedge
KY = BASE - 27 * K          # centre of the keyhole's round head
DEPTH = (6, 1)              # how far the back of the doorway shows, seen from a little to the right


def mix(c1, c2, u):
    u = max(0.0, min(1.0, u))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * u):02X}" for x, y in zip(a, b))


def in_mark(x, y):
    """Is (x, y) inside the keyhole doorway? Analytic, in mark space."""
    u = (x - KX) / K + 32
    v = (y - KY) / K + 33
    if (u - 32) ** 2 + (v - 33) ** 2 <= 15 ** 2:
        return True
    if 38 <= v <= 60:
        t = (v - 40) / 20
        if 27 - 3 * t <= u <= 37 + 3 * t:
            return True
    for ex in (22.5, 41.5):
        if ((u - ex) / 4.2) ** 2 + ((v - 12) / 10) ** 2 <= 1:
            return True
    return False


def sky(cv):
    g = f'<rect width="{W}" height="{H}" fill="{cv.lin(0, 0, 0, 250, [(0, "#160D3C"), (0.4, "#2E1D78"), (0.72, "#6E4CC4"), (0.9, "#C996D8"), (1, "#F3B9A8")])}"/>'
    g += glow(cv, 110, 240, 230, "#FFC9B0", .35)
    rnd = random.Random(31)
    st = ""
    for _ in range(46):
        x, y = rnd.uniform(0, W), rnd.uniform(0, 150)
        if x < 270 and 40 < y < 150:      # keep the title's sky clean
            continue
        st += f'<circle cx="{f(x)}" cy="{f(y)}" r="{rnd.choice([.4, .5, .6, .8])}" fill="#fff" opacity="{rnd.uniform(.3, .8):.2f}"/>'
    st += sparkle(452, 120, 3, "#fff", .6) + sparkle(30, 22, 2.5, "#fff", .5)
    return g + st


def far_land(cv):
    return (f'<path d="M0 226C60 214 140 220 200 228S260 232 300 236V260H0Z" fill="#7A5AC8" opacity=".55" filter="{cv.blur(1.2)}"/>'
            f'<path d="M0 238C80 230 160 236 240 242S300 244 320 246V270H0Z" fill="#4E36A6"/>')


def hedge(cv, rnd):
    top = [(262, 258), (256, 150), (260, 116), (272, 102), (290, 96), (310, 88), (334, 82), (358, 76),
           (382, 68), (406, 62), (432, 56), (458, 50), (484, 46), (490, 46), (490, 262)]
    d, poly = fluffy(top, [(0.08, 0.86, 1)], amp=7, step=22, sweep=.1, seed=5)
    fill = cv.lin(0, 50, 0, 258, [(0, "#4A43A8"), (0.5, "#2E2878"), (1, "#181348")])
    clip = cv.clip(d)
    leaf = cv.id("leaf")
    # one sprig: three leaves and their veins; fill comes from each <use>
    cv.defs.append(
        f'<g id="{leaf}"><path d="M0 0C-3 -2 -4 -6 -1 -9C2 -6 2 -2 0 0Z"/><path d="M0 0C3 -1 7 -1 9 2C6 4 2 3 0 0Z"/>'
        f'<path d="M0 0C-3 1 -7 2 -8 6C-4 6 -1 4 0 0Z"/>'
        f'<path d="M0 0L-1 -7M0 0L7 1M0 0L-6 4" stroke="#120E38" stroke-width=".5" opacity=".45" fill="none"/></g>')
    uses = []
    for _ in range(880):
        x, y = rnd.uniform(250, 490), rnd.uniform(44, 262)
        if not any(abs(px - x) < 1 for px, _ in []) and not inside_poly(poly, x, y):
            continue
        if in_mark(x, y) or near_frame(x, y, 9):
            continue
        h = (y - 50) / 210                      # 0 at the top (sky-lit) .. 1 at the foot
        col = mix("#7A70D8", "#3A3390", h * 1.4)
        col = mix(col, "#201A5A", (h - .6) * 2.2)
        dd = math.hypot((x - KX) * .8, y - (KY + 20))
        warm = max(0.0, 1 - dd / 95) ** 1.6
        col = mix(col, "#FFC27A", warm * .85)
        s = rnd.uniform(1.0, 1.45)
        # clumps: the hedge bulges every so often, shaded below each bulge
        bump = math.sin(x * .09 + math.sin(y * .05) * 2) * math.sin(y * .11 + x * .02)
        col = mix(col, "#120D36", max(0.0, -bump) * .7)
        col = mix(col, "#A49AF4", max(0.0, bump) * .35 * (1 - h * .7))
        uses.append((y, f'<use href="#{leaf}" transform="translate({f(x)} {f(y)}) rotate({rnd.randint(0, 359)}) scale({s:.1f})" fill="{col}"/>'))
    uses.sort()
    body = (f'<path d="{d}" fill="{fill}"/><g clip-path="{clip}">' + "".join(u for _, u in uses)
            # sky light along the top, deep shade at the foot, warmth around the door
            + f'<path d="M250 40H490V140Q370 100 250 160Z" fill="#B9A6FF" opacity=".12" filter="{cv.blur(10)}"/>'
            + f'<rect x="240" y="226" width="260" height="40" fill="#0C0828" opacity=".55" filter="{cv.blur(9)}"/>'
            + glow(cv, KX + 6, KY + 30, 120, "#FFB870", .3)
            + "</g>")
    return body, d


def inside_poly(poly, x, y):
    from kit import inside
    return inside(poly, x, y)


def near_frame(x, y, m):
    for dx in (-m, 0, m):
        for dy in (-m, 0, m):
            if in_mark(x + dx, y + dy):
                return True
    return False


def doorway(cv):
    ears, head, foot = mark_paths(KX, KY, K)
    hole = ears + head + foot
    g = ""
    # contact shadow of the frame in the leaves
    g += (f'<path d="{hole}" fill="#05030F" stroke="#05030F" stroke-width="22" stroke-linejoin="round" opacity=".55" '
          f'filter="{cv.blur(5)}" transform="translate(2 3)"/>')
    # bevelled brass frame: dark base, polished face, a bright bevel line
    brass = cv.lin(KX - 60, KY - 90, KX + 60, KY + 90, [(0, "#FFF2C0"), (0.25, "#E2A94A"), (0.5, "#8A5A16"),
                                                        (0.7, "#E9B654"), (1, "#5E3A08")])
    g += f'<path d="{hole}" fill="#3A2205" stroke="#3A2205" stroke-width="17" stroke-linejoin="round"/>'
    g += f'<path d="{hole}" fill="{brass}" stroke="{brass}" stroke-width="14" stroke-linejoin="round"/>'
    g += (f'<path d="{hole}" fill="none" stroke="#FFF6D6" stroke-width="15" stroke-linejoin="round" opacity=".55" '
          f'transform="translate(-1.2 -1.2)" filter="{cv.blur(.7)}"/>')
    g += f'<path d="{hole}" fill="#5E3A08" stroke="#5E3A08" stroke-width="4" stroke-linejoin="round"/>'
    # rivets on the frame
    for a in range(0, 360, 30):
        r = 15 * K + 7.5
        x, y = KX + r * math.cos(math.radians(a)), KY + r * math.sin(math.radians(a))
        if 60 < a < 120 or 230 < a < 310:
            continue
        g += (f'<circle cx="{f(x)}" cy="{f(y)}" r="1.6" fill="#FFF2C0"/>'
              f'<circle cx="{f(x + .4)}" cy="{f(y + .5)}" r="1.6" fill="none" stroke="#5E3A08" stroke-width=".5"/>')

    # ---- inside the doorway
    hc = cv.clip(hole)
    dx, dy = DEPTH
    back = f'<path d="{hole}" transform="translate({dx} {dy})"/>'
    x0, y0, x1, y1 = KX - 70, KY - 100, KX + 70, BASE + 10
    light = cv.rad(KX + 16, KY + 14, 120, [(0, "#FFFFFF"), (0.25, "#FFF8E6"), (0.55, "#FFDDB4"), (1, "#E6B0FF")])
    beyond = (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{light}"/>'
              # Wonderland, washed out by its own light: a lawn, a path, two topiary shapes
              f'<path d="M{x0} {KY + 44}C{KX - 20} {KY + 36} {KX + 30} {KY + 44} {x1} {KY + 38}V{y1}H{x0}Z" fill="#E7C8FF" opacity=".75"/>'
              f'<path d="M{KX + 2} {y1}L{KX + 8} {KY + 42}H{KX + 12}L{KX + 26} {y1}Z" fill="#FFF8EC"/>'
              f'<ellipse cx="{KX - 22}" cy="{KY + 30}" rx="7" ry="12" fill="#C9A8F8" opacity=".7"/>'
              f'<ellipse cx="{KX + 46}" cy="{KY + 32}" rx="6" ry="10" fill="#C9A8F8" opacity=".6"/>'
              + glow(cv, KX + 16, KY + 18, 60, "#FFFFFF", .95))
    # the reveal: the hedge is thick; its brass-lined inner wall shows on the left
    reveal_fill = cv.lin(KX - 50, 0, KX + 10, 0, [(0, "#4A2C06"), (0.6, "#A8711C"), (1, "#F2C766")])
    # the little door, swung inward on its left hinge; backlit, its edge on fire
    hinge = KX - 16 * K + dx
    sx = .34
    leaf_t = f"translate({f(hinge)} 0) scale({sx} 1) translate({f(-hinge)} 0) translate({dx} {dy})"
    wood = cv.lin(KX - 50, 0, KX + 50, 0, [(0, "#2A1A66"), (0.6, "#3E2A8A"), (1, "#5A44B0")])
    planks = "".join(f"M{f(KX - 44 + i * 11)} {f(KY - 90)}V{BASE}" for i in range(9))
    lc = cv.clip(hole, leaf_t)
    leaf_inner = (f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{wood}"/>'
                  f'<path d="{planks}" stroke="#160C40" stroke-width="1.6" opacity=".7"/>'
                  f'<path d="{planks}" stroke="#7A66D0" stroke-width=".6" opacity=".35" transform="translate(1 0)"/>'
                  f'<rect x="{x0}" y="{KY + 34}" width="{x1 - x0}" height="5" fill="#160C40" opacity=".6"/>'
                  f'<rect x="{x0}" y="{KY - 26}" width="{x1 - x0}" height="5" fill="#160C40" opacity=".6"/>')
    ears2, head2, foot2 = mark_paths(KX + 8, KY + 10, .55)
    door = (f'<path d="{hole}" transform="translate({f(hinge)} 0) scale({sx + .05} 1) translate({f(-hinge)} 0) '
            f'translate({dx + 2} {dy})" fill="#FFB060"/>'                                  # lit edge thickness
            f'<g clip-path="{lc}">{leaf_inner}'
            f'</g>'
            f'<path d="{hole}" transform="{leaf_t}" fill="none" stroke="#FFD08A" stroke-width="2" opacity=".8" '
            f'filter="{cv.blur(1.2)}"/>')
    bc = cv.clip(hole, f"translate({dx} {dy})")
    g += (f'<g clip-path="{hc}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{reveal_fill}"/>'
          f'<g clip-path="{bc}">{beyond}{door}</g></g>')
    # light spilling over the brass on the open side
    g += glow(cv, KX + 26, KY + 30, 70, "#FFE6B8", .45)
    return g, hole


def ground(cv, rnd, hole):
    g = ""
    gnd = cv.lin(0, 240, 0, H, [(0, "#3C2A8E"), (0.5, "#231565"), (1, "#110838")])
    g += f'<path d="M0 252C120 244 220 250 300 252S420 256 490 254V330H0Z" fill="{gnd}"/>'
    # fine grass texture: two tiles at different scales so they never line up
    for w, h, sc, op, tf in ((7, 5, 1, .55, "rotate(0)"), (11, 7, 1.4, .35, "rotate(-4)")):
        tile = (f'<path d="M1 {h}q.6 -{h * .6} 1.6 -{h}M4 {h}q-.2 -{h * .5} -.9 -{h * .8}M5.5 {h}q.5 -{h * .4} 1.2 -{h * .6}" '
                f'stroke="#5B48B8" stroke-width=".45" fill="none"/>')
        pat = cv.pattern(w, h, tile, tf)
        g += f'<path d="M0 254C120 246 220 252 300 254S420 258 490 256V330H0Z" fill="{pat}" opacity="{op}"/>'
    # a broad warm wash on the grass, then the keyhole's own shape thrown towards us
    wash = cv.rad(KX, BASE + 4, 190, [(0, "#FFC890", .55), (0.5, "#FFB070", .18), (1, "#FFB070", 0)],
                  tf=f"translate({KX} {BASE + 4}) scale(1.25 .34) translate({-KX} {-(BASE + 4)})")
    g += f'<ellipse cx="{KX}" cy="{BASE + 4}" rx="250" ry="70" fill="{wash}"/>'
    # door light reaches the Rabbit's patch of lawn, so his shadow has somewhere to fall
    reach = cv.rad(410, 300, 90, [(0, "#FFC890", .42), (0.6, "#FFB070", .15), (1, "#FFB070", 0)],
                   tf="translate(410 300) scale(1.3 .3) translate(-410 -300)")
    g += f'<ellipse cx="410" cy="300" rx="130" ry="30" fill="{reach}"/>'
    proj = f"translate({KX + 4} {BASE + 1}) scale(1.6 -.4) translate({-KX} {-BASE})"
    pool = cv.lin(0, BASE, 0, BASE - 190, [(0, "#FFF2D8", .95), (0.5, "#FFD9A0", .55), (1, "#FFC27A", .05)])
    hinge = KX - 16 * K + DEPTH[0]
    leaf_shadow = f"translate({f(hinge)} 0) scale(.34 1) translate({f(-hinge)} 0)"
    g += (f'<g transform="{proj}" filter="{cv.blur(2)}"><path d="{hole}" fill="{pool}"/>'
          f'<path d="{hole}" transform="{leaf_shadow}" fill="#1C0F50" opacity=".38"/></g>')
    # blades: dark in the dusk, gold where the door light falls; bigger towards us
    blades = []
    for _ in range(330):
        x = rnd.uniform(-4, W + 4)
        y = rnd.uniform(254, H + 6)
        depth = (y - 252) / 70
        h = 3 + depth * rnd.uniform(6, 14)
        # lit if the point falls inside the projected keyhole (and not in the door's shadow)
        mx = KX + (x - KX - 4) / 1.6
        my = BASE - (y - BASE - 1) / .4
        lit = in_mark(mx, my) and not (mx < hinge + (KX + 16 * K - hinge) * .34 and my > KY - 30 * K)
        warmth = max(0.0, 1 - math.hypot((x - KX) / 1.6, (y - BASE) * 2.2) / 130)
        in_pool = in_mark(mx, my)
        if lit:
            col = mix("#FFF0CC", "#FFB868", rnd.random() * .7)
            op = .95
        elif in_pool:
            col = mix("#B07A50", "#7A58A8", rnd.random())
            op = .7
        elif warmth > .25 and rnd.random() < warmth:
            col = mix("#6A50C0", "#FFB060", warmth * .8)
            op = .8
        else:
            col = rnd.choice(["#2A1A70", "#33227E", "#4A38A6", "#1C1052"])
            op = .9
        lean = rnd.uniform(-.35, .35) * h
        w = (.35 if in_mark(mx, my) else .5) + depth * .8
        blades.append((y, f'<path d="M{f(x - w)} {f(y)}Q{f(x + lean * .3)} {f(y - h * .6)} {f(x + lean)} {f(y - h)}'
                          f'Q{f(x + lean * .3 + w * .4)} {f(y - h * .55)} {f(x + w)} {f(y)}Z" fill="{col}" opacity="{op}"/>'))
    blades.sort()
    g += "".join(b for _, b in blades)
    # the light pool itself is grass: short gold blades packed inside the keyhole's shadow-shape
    lb = []
    n = 0
    while n < 170:
        x, y = rnd.uniform(KX - 90, KX + 100), rnd.uniform(BASE + 2, H)
        mx = KX + (x - KX - 4) / 1.6
        my = BASE - (y - BASE - 1) / .4
        if not in_mark(mx, my):
            continue
        n += 1
        depth = (y - 252) / 70
        h = 2.5 + depth * rnd.uniform(4, 9)
        lean = rnd.uniform(-.4, .4) * h
        shade = mx < hinge + (KX + 16 * K - hinge) * .34
        col = mix("#FFF4D8", "#FFB868", rnd.random() * .8) if not shade else mix("#C08A60", "#8A68B8", rnd.random())
        lb.append((y, f'<path d="M{f(x - .4)} {f(y)}Q{f(x + lean * .3)} {f(y - h * .6)} {f(x + lean)} {f(y - h)}'
                      f'Q{f(x + lean * .3 + .2)} {f(y - h * .55)} {f(x + .4)} {f(y)}Z" fill="{col}"/>'))
    lb.sort()
    g += "".join(b for _, b in lb)
    return g


def card(cv, x, y, w, h, rot, face, blur=0):
    t = f"rotate({rot} {x} {y})"
    fill = cv.lin(x - w / 2, y - h / 2, x + w / 2, y + h / 2, [(0, "#FFFFFF"), (1, "#E4DCF2")])
    g = (f'<rect x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{w}" height="{h}" rx="2.6" fill="#FFD9A8" opacity=".35" '
         f'transform="{t}" filter="{cv.blur(4)}"/>'
         f'<rect x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{w}" height="{h}" rx="2.6" fill="{fill}" transform="{t}"/>')
    if face == "heart":
        hx, hy, s = x, y + 1, w * .22
        g += (f'<path d="M{f(hx)} {f(hy + s)}C{f(hx - 2.2 * s)} {f(hy - .4 * s)} {f(hx - .9 * s)} {f(hy - 1.8 * s)} {f(hx)} '
              f'{f(hy - .7 * s)}C{f(hx + .9 * s)} {f(hy - 1.8 * s)} {f(hx + 2.2 * s)} {f(hy - .4 * s)} {f(hx)} {f(hy + s)}Z" '
              f'fill="#C2456B" transform="{t}"/>'
              f'<path d="M{f(x - w / 2 + 3)} {f(y - h / 2 + 3)}h3M{f(x - w / 2 + 4.5)} {f(y - h / 2 + 1.6)}v3" stroke="#C2456B" '
              f'stroke-width=".9" transform="{t}"/>')
    else:   # back of a card: violet with a diamond lattice
        pat = cv.pattern(4, 4, '<path d="M2 0L4 2 2 4 0 2Z" fill="none" stroke="#C9B8FF" stroke-width=".4"/>', f"rotate({rot})")
        g += (f'<rect x="{f(x - w / 2 + 2)}" y="{f(y - h / 2 + 2)}" width="{w - 4}" height="{h - 4}" rx="1.6" fill="#5B3BE8" transform="{t}"/>'
              f'<rect x="{f(x - w / 2 + 2)}" y="{f(y - h / 2 + 2)}" width="{w - 4}" height="{h - 4}" rx="1.6" fill="{pat}" transform="{t}"/>')
    g += (f'<rect x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{w}" height="{h}" rx="2.6" fill="none" stroke="#FFF" '
          f'stroke-width=".6" opacity=".8" transform="{t}"/>')
    if blur:
        return f'<g filter="{cv.blur(blur)}">{g}</g>'
    return g


def rabbit_in_light(cv):
    """The Rabbit, defined once and used twice: himself, and his long shadow away from the door."""
    rc = Canvas("swr")
    old = rabbit.DETAIL
    rabbit.DETAIL = .3
    body = rabbit.rabbit(rc, shadow=False)
    rabbit.DETAIL = old
    rid = cv.id("rab")
    cv.defs.append(f'<g id="{rid}">{body}</g>')
    s, tx, ty = .4, 328, 101
    place = f"translate({tx} {ty}) scale({s})"
    fx, fy = tx + 262 * s, ty + 494 * s            # where his feet meet the grass
    # shadow: everything above the grass is laid down to the right and towards us
    k, q = .55, .36
    shadow_m = f"matrix(1 0 {f(-k)} {f(-q)} {f(k * fy)} {f((1 + q) * fy)})"
    sh = cv.id("sh")
    cv.defs.append(f'<filter id="{sh}" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                   f'<feColorMatrix type="matrix" values="0 0 0 0 .04 0 0 0 0 .01 0 0 0 0 .14 0 0 0 .7 0"/>'
                   f'<feGaussianBlur stdDeviation="2.2"/></filter>')
    g = f'<g filter="url(#{sh})"><g transform="{shadow_m}"><use href="#{rid}" transform="{place}"/></g></g>'
    g += f'<ellipse cx="{f(fx - 4)}" cy="{f(fy + 1)}" rx="46" ry="5" fill="#0A0420" opacity=".55" filter="{cv.blur(3)}"/>'
    # door light: a hot rim on every edge that faces the door, and a warm wash over that side
    rim = cv.id("rim")
    cv.defs.append(
        f'<filter id="{rim}" filterUnits="userSpaceOnUse" x="-80" y="-80" width="680" height="680" color-interpolation-filters="sRGB">'
        f'<feOffset in="SourceAlpha" dx="9" dy="2" result="o1"/>'
        f'<feComposite in="SourceAlpha" in2="o1" operator="out" result="e1"/>'
        f'<feGaussianBlur in="e1" stdDeviation="2" result="b1"/>'
        f'<feComposite in="b1" in2="SourceAlpha" operator="in" result="m1"/>'
        f'<feFlood flood-color="#FFD9A0"/><feComposite in2="m1" operator="in" result="rim"/>'
        f'<feOffset in="SourceAlpha" dx="40" dy="6" result="o2"/>'
        f'<feComposite in="SourceAlpha" in2="o2" operator="out" result="e2"/>'
        f'<feGaussianBlur in="e2" stdDeviation="10" result="b2"/>'
        f'<feComposite in="b2" in2="SourceAlpha" operator="in" result="m2"/>'
        f'<feFlood flood-color="#FFB46A" flood-opacity=".28"/><feComposite in2="m2" operator="in" result="wash"/>'
        f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="wash"/><feMergeNode in="rim"/></feMerge></filter>')
    g += f'<g transform="{place}"><g filter="url(#{rim})"><use href="#{rid}"/></g></g>'
    return g, rc


def welcome():
    cv = Canvas("sw", (-60, -60, 600, 440))
    rnd = random.Random(12)
    g = sky(cv) + far_land(cv)
    # two cards adrift over the hedge, catching the light
    g += card(cv, 444, 26, 20, 28, 24, "back", .6) + card(cv, 404, 40, 24, 33, -16, "heart")
    hb, hd = hedge(cv, rnd)
    g += hb
    door, hole = doorway(cv)
    g += door
    g += ground(cv, rnd, hole)
    # volumetric light from the doorway, out over the grass
    beams = ""
    for (ax, ay, bx, by, w0, w1, op) in ((KX + 14, KY - 10, KX + 70, 330, 6, 60, .16), (KX + 26, KY + 20, KX + 150, 330, 5, 50, .12),
                                         (KX, KY + 40, KX - 20, 330, 6, 70, .12), (KX + 30, KY - 40, KX + 120, 250, 3, 30, .1)):
        beams += (f'<path d="M{ax - w0} {ay}L{ax + w0} {ay}L{bx + w1} {by}L{bx - w1} {by}Z" '
                  f'fill="{cv.lin(ax, ay, bx, by, [(0, "#FFE6B8", op * 2), (1, "#FFE6B8", 0)])}"/>')
    g += f'<g filter="{cv.blur(6)}">{beams}</g>'
    rb, rc = rabbit_in_light(cv)
    g += rb
    # dust in the door light
    g += motes(cv, (KX - 10, KY - 60, KX + 120, BASE), 16, 3, "#FFF0D0", 3.2)
    # front grass fringe across the bottom, in silhouette
    fr = ""
    for i in range(120):
        x = i * 4.1 + rnd.uniform(-2, 2)
        h = rnd.uniform(5, 13)
        lean = rnd.uniform(-3, 3)
        fr += f'<path d="M{f(x - 1.1)} {H + 1}Q{f(x + lean * .3)} {f(H - h * .6)} {f(x + lean)} {f(H - h)}Q{f(x + lean * .3 + .5)} {f(H - h * .5)} {f(x + 1.1)} {H + 1}Z"/>'
    g += f'<g fill="#0E0630">{fr}</g>'
    vg = cv.rad(W * .55, H * .4, 360, [(0, "#000", 0), (0.65, "#000", 0), (1, "#06021A", .5)])
    g += f'<rect width="{W}" height="{H}" fill="{vg}"/>'
    return svg(W, H, [cv, rc], g, "Welcome to WolOS")
