# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Julia Klee
"""Scenes: the Setup Assistant welcome, the lock-screen peek, the character sheet."""
import math
import random
from kit import Canvas, f, path, sample, sparkle, svg, band
from parts import glow, motes
from keyhole import mark_paths, rays
import rabbit


def stars(cv, box, n, seed, avoid=()):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = ""
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in avoid):
            continue
        r = rnd.choice([.5, .6, .8, 1.0, 1.2])
        out += f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="#fff" opacity="{rnd.uniform(.35, .9):.2f}"/>'
    for _ in range(5):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1 * .8)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in avoid):
            continue
        out += sparkle(x, y, rnd.uniform(3, 5), "#fff", rnd.uniform(.6, .9))
    return out


def peek():
    """320x200: the Rabbit pops up from the bottom edge of the lock screen."""
    W, H = 320, 200
    rc = Canvas("lp")
    body = rabbit.rabbit(rc, shadow=False, arms=False)
    g = f'<g transform="translate(10 4) scale(.6) rotate(-9 252 230)">{body}</g>'
    # paws gripping the edge
    from rabbit import furry, down
    from kit import ellipse_pts
    pw = ""
    for px, rot in ((112, -12), (210, 10)):
        pts = ellipse_pts(px, 194, 21, 14, 10, rot)
        pw += f'<ellipse cx="{px + 3}" cy="200" rx="22" ry="7" fill="#2B1B66" opacity=".35" filter="{rc.blur(3)}"/>'
        s, d, poly = furry(rc, pts, [(0.8, 0.2, .6)], px, down(px, 170), 18, amp=2.5, shade=("#6C58B4", .45, 6, 4))
        pw += s
        pw += (f'<path d="M{px - 7} 186q2 8 0 14M{px + 4} 186q2 8 0 14" stroke="#8C7AC8" stroke-width="1.3" fill="none" '
               f'opacity=".8" transform="rotate({rot} {px} 194)"/>')
    g += pw
    return svg(W, H, [rc], g, "Hello again")


def sheet(cast):
    """1600x1000 character sheet. `cast`: [(file, name, role, line, use)]. Images are referenced, not inlined."""
    W, H = 1600, 1000
    cv = Canvas("cs", (-100, -100, 1800, 1200))
    font = "Inter, 'Adwaita Sans', 'Fira Sans', sans-serif"
    g = ""
    bg = cv.lin(0, 0, W, H, [(0, "#17102E"), (0.5, "#120C24"), (1, "#0B0716")])
    g += f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    g += glow(cv, 380, 520, 560, "#7C5CFF", .35)
    g += glow(cv, 1250, 260, 520, "#FFC9A8", .10)
    text = ((60, 60, 780, 215), (100, 800, 700, 940))
    g += stars(cv, (0, 0, W, 215), 40, 7, text) + stars(cv, (0, 215, 700, H), 30, 8, text)
    g += (f'<text x="80" y="104" font-family="{font}" font-size="18" font-weight="600" letter-spacing="3" '
          f'fill="#9B85FF">WOLOS · WONDERLAND OS</text>'
          f'<text x="80" y="160" font-family="{font}" font-size="50" font-weight="700" fill="#FFFFFF" '
          f'letter-spacing="-1">Meet the cast.</text>'
          f'<text x="80" y="200" font-family="{font}" font-size="20" fill="#B8B0D0">Five characters from Wonderland, '
          f'each with a job to do in the system.</text>')
    # hero: the rabbit, big, with his card under him
    hero = cast[0]
    g += f'<image href="{hero[0]}" x="70" y="226" width="600" height="600"/>'
    g += card(cv, 120, 850, 500, hero, font, big=True)
    # the others on a 2x2 grid
    pos = [(740, 230), (1160, 230), (740, 600), (1160, 600)]
    for (x, y), c in zip(pos, cast[1:]):
        g += (f'<rect x="{x}" y="{y}" width="380" height="350" rx="24" fill="#FFFFFF" fill-opacity=".05" '
              f'stroke="#FFFFFF" stroke-opacity=".10"/>')
        g += f'<image href="{c[0]}" x="{x + 75}" y="{y + 2}" width="230" height="230"/>'
        g += card(cv, x + 28, y + 262, 330, c, font)
    g += (f'<text x="{W - 60}" y="{H - 18}" text-anchor="end" font-family="{font}" font-size="14" fill="#6E6E80">'
          f'© 2026 Julia Klee · Wonderland Brand License 1.0</text>')
    return svg(W, H, [cv], g, "WolOS cast")


def card(cv, x, y, w, c, font, big=False):
    _, name, role, line, use = c
    s = 1.25 if big else 1
    lines = line if isinstance(line, tuple) else (line,)
    out = (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{f(26 * s)}" font-weight="700" fill="#FFFFFF">{name}'
           f'<tspan font-weight="500" fill="#9B85FF" font-size="{f(15 * s)}" dx="12">{role}</tspan></text>')
    yy = y + 28 * s
    for ln in lines:
        out += f'<text x="{x}" y="{f(yy)}" font-family="{font}" font-size="{f(16 * s)}" fill="#D6D0E6">{ln}</text>'
        yy += 21 * s
    out += f'<text x="{x}" y="{f(yy + 4 * s)}" font-family="{font}" font-size="{f(13 * s)}" fill="#8C86A0">{use}</text>'
    return out
