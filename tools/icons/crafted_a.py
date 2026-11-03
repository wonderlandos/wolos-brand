# SPDX-License-Identifier: GPL-2.0-or-later
"""The first eight crafted objects (settings, software, files, terminal, browser, music, mail,
installer): hand-built with explicit ids, from the approved D2 samples (.claude/brand/icons-premium/).
Each function takes the canvas and draws the container and the glyph on it."""
import math
from svgk import *


# ---------------------------------------------------------------- SETTINGS

def settings(cv):
    cx, cy = 512, 498
    container(cv, "#6F7FB6", "#242C52", glow="#B8C4FF", edge="#0B1030"); d = b = ""
    gp = gear_poly(cx, cy)
    sw = 24
    defs = d
    defs += shadow_filter("g-sh", dy=34, blur=24, color="#050A28", op=.55)
    defs += blur_filter("g-b10", 10) + blur_filter("g-b18", 18) + blur_filter("g-b4", 4)
    defs += lingrad("g-face", [(0, "#FFFFFF"), (.28, "#E2E6EE"), (.62, "#B4BBCB"), (1, "#8A93A8")])
    defs += lingrad("g-side", [(0, "#7E8799"), (1, "#2C3350")])
    defs += lingrad("g-bore", [(0, "#06081A"), (.6, "#171C3C"), (1, "#3A4270")])
    defs += lingrad("g-ring", [(0, "#58617B"), (.5, "#C9CFDC"), (1, "#FFFFFF")])
    defs += lingrad("g-ring2", [(0, "#FFFFFF"), (1, "#6D7690")])
    defs += radgrad("g-key", [(0, "#C9BBFF"), (.5, "#8D70FF"), (1, "#5B3CE0")])
    defs += radgrad("g-glow", [(0, "#9B85FF", .9), (1, "#9B85FF", 0)])
    # bevel on the gear alpha, in primitives GTK 4 draws like librsvg (it has no lighting filters):
    # the face dimmed to the diffuse level of a flat top lit at 52 degrees, the flat specular sheen
    # as a white wash, and the lower rim shaded by the face minus its own blurred alpha shifted up
    # (constants fitted to the earlier specular+diffuse lighting at 128 and 512 px)
    defs += ('<filter id="g-bevel" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">'
             '<feColorMatrix in="SourceGraphic" type="matrix" values=".88 0 0 0 0  0 .88 0 0 0  0 0 .88 0 0  0 0 0 1 0" result="m"/>'
             '<feFlood flood-color="#fff" flood-opacity=".09"/><feComposite in2="SourceAlpha" operator="in" result="sp"/>'
             '<feGaussianBlur in="SourceAlpha" stdDeviation="8" result="ab"/><feOffset in="ab" dy="-15" result="ad"/>'
             '<feComposite in="SourceAlpha" in2="ad" operator="out" result="dark"/>'
             '<feMerge><feMergeNode in="m"/><feMergeNode in="sp"/><feMergeNode in="dark"/></feMerge></filter>')
    defs += f'<mask id="g-mask"><path d="{gp}" fill="#fff" stroke="#fff" stroke-width="{sw}" stroke-linejoin="round"/></mask>'
    # brushed rings
    rings = ""
    for i, r in enumerate(range(14, 320, 3)):
        o = .05 + .06 * ((i * 37) % 7) / 7
        col = "#fff" if i % 2 else "#2A3350"
        rings += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="1.6" opacity="{o:.3f}"/>'
    def wedge(a0, a1, r=340):
        p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
        p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
        return f"M{cx} {cy}L{p0[0]:.1f} {p0[1]:.1f}L{p1[0]:.1f} {p1[1]:.1f}Z"
    wedges = (f'<path d="{wedge(-125,-80)}" fill="#fff" opacity=".75" filter="url(#g-b18)"/>'
              f'<path d="{wedge(55,100)}" fill="#fff" opacity=".42" filter="url(#g-b18)"/>'
              f'<path d="{wedge(-10,30)}" fill="#1C2340" opacity=".30" filter="url(#g-b18)"/>'
              f'<path d="{wedge(165,205)}" fill="#1C2340" opacity=".26" filter="url(#g-b18)"/>')
    body = b
    # contact+ambient shadow of the object on the container
    body += f'<g filter="url(#g-sh)"><path d="{gp}" fill="#2C3350" stroke="#2C3350" stroke-width="{sw}" stroke-linejoin="round" transform="translate(0 24)"/></g>'
    # extruded side
    body += f'<path d="{gp}" fill="url(#g-side)" stroke="url(#g-side)" stroke-width="{sw}" stroke-linejoin="round" transform="translate(0 22)"/>'
    # top face (bevelled)
    body += f'<g filter="url(#g-bevel)"><path d="{gp}" fill="url(#g-face)" stroke="url(#g-face)" stroke-width="{sw}" stroke-linejoin="round"/></g>'
    body += f'<g mask="url(#g-mask)">{rings}{wedges}</g>'
    # machined groove ring
    body += f'<circle cx="{cx}" cy="{cy}" r="188" fill="none" stroke="#5B647E" stroke-width="7" opacity=".55"/>'
    body += f'<circle cx="{cx}" cy="{cy+6}" r="188" fill="none" stroke="#fff" stroke-width="3.5" opacity=".6"/>'
    # bore: chamfer ring (lit from above -> lower lip bright)
    body += f'<circle cx="{cx}" cy="{cy}" r="126" fill="url(#g-ring)"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="104" fill="url(#g-ring2)" opacity=".9"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="94" fill="url(#g-bore)"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="94" fill="none" stroke="#000" stroke-opacity=".5" stroke-width="3"/>'
    # keyhole lit inside the bore (the brand motif; the single pop)
    body += f'<circle cx="{cx}" cy="{cy+6}" r="70" fill="url(#g-glow)" opacity=".7"/>'
    kh = f'M{cx} {cy-44}a26 26 0 0 1 14 48l16 44h-60l16 -44a26 26 0 0 1 14 -48z'
    body += f'<path d="{kh}" fill="url(#g-key)"/>'
    body += f'<path d="{kh}" fill="none" stroke="#E4DBFF" stroke-opacity=".7" stroke-width="2"/>'
    return finish(cv, defs, body)


# ---------------------------------------------------------------- STORE (paper bag)
def store(cv):
    container(cv, "#FFCB57", "#E0791A", glow="#FFF2C2", edge="#6B2D00", glow_op=.34); d = b = ""
    defs = d + paper_noise("grain", .035, .8)
    defs += shadow_filter("s-sh", dy=30, blur=22, color="#6B2D00", op=.55)
    defs += shadow_filter("s-sh2", dy=8, blur=7, color="#3A1500", op=.45)
    defs += blur_filter("s-b8", 8) + blur_filter("s-b3", 3)
    defs += lingrad("s-paper", [(0, "#FFFAF0"), (.55, "#F6E7CC"), (1, "#E1C8A2")])
    defs += lingrad("s-side", [(0, "#EBD6B3"), (1, "#C49E6C")])
    defs += lingrad("s-fold", [(0, "#FFF6E3"), (1, "#E8D2AE")])
    defs += lingrad("s-rope", [(0, "#8A3A55"), (.5, "#5A1E39"), (1, "#3A1026")])
    defs += lingrad("s-rim", [(0, "#F2DDB8"), (1, "#D9BC8D")])
    defs += lingrad("s-stamp", [(0, "#8C2B52"), (1, "#5B1535")])
    defs += lingrad("s-ao", [(0, "#5A2A00", .0), (1, "#5A2A00", .34)])
    defs += lingrad("s-aot", [(0, "#5A2A00", .30), (1, "#5A2A00", 0)])
    L, R, T, B = 296, 728, 384, 818
    body = b
    # handles (rope) behind the bag, entering the punched holes
    hx1, hx2 = 408, 616
    rope = f'M{hx1} {T+34}C{hx1-34} {T-165} {hx2+34} {T-165} {hx2} {T+34}'
    body += f'<g filter="url(#s-sh2)"><path d="{rope}" fill="none" stroke="url(#s-rope)" stroke-width="26" stroke-linecap="round"/></g>'
    body += f'<path d="{rope}" fill="none" stroke="#C26A8A" stroke-opacity=".55" stroke-width="5" stroke-linecap="round" transform="translate(-2 -6)"/>'
    # bag: drop shadow of the whole object
    bag = f'M{L} {T}H{R}V{B-30}A30 30 0 0 1 {R-30} {B}H{L+30}A30 30 0 0 1 {L} {B-30}Z'
    body += f'<g filter="url(#s-sh)"><path d="{bag}" fill="#EBD6B3"/></g>'
    # right gusset (side panel in shade)
    body += f'<path d="M{R-62} {T}H{R}V{B-30}A30 30 0 0 1 {R-30} {B}H{R-62}Z" fill="url(#s-side)"/>'
    # front panel
    front = f'M{L} {T}H{R-62}V{B}H{L+30}A30 30 0 0 1 {L} {B-30}Z'
    body += f'<path d="{front}" fill="url(#s-paper)"/>'
    body += f'<path d="{front}" fill="#000" filter="url(#grain)" opacity="1"/>'
    # fold crease between front and gusset
    body += f'<rect x="{R-66}" y="{T}" width="8" height="{B-T}" fill="#fff" opacity=".35" filter="url(#s-b3)"/>'
    body += f'<rect x="{R-60}" y="{T}" width="10" height="{B-T}" fill="#7A4A12" opacity=".18" filter="url(#s-b3)"/>'
    # soft light sweep from upper-left
    body += f'<path d="M{L} {T}H{L+170}L{L+30} {B}H{L+30}A30 30 0 0 1 {L} {B-30}Z" fill="#fff" opacity=".22"/>'
    # folded-over top band
    band = 70
    body += f'<path d="M{L} {T}H{R}V{T+band}H{L}Z" fill="url(#s-rim)"/>'
    body += f'<rect x="{L}" y="{T+band}" width="{R-L}" height="26" fill="url(#s-aot)"/>'
    body += f'<rect x="{L}" y="{T+band-3}" width="{R-L}" height="4" fill="#8A5A1C" opacity=".4"/>'
    body += f'<rect x="{L}" y="{T}" width="{R-L}" height="5" fill="#fff" opacity=".85"/>'
    # eyelets
    for hx in (hx1, hx2):
        body += f'<circle cx="{hx}" cy="{T+36}" r="21" fill="#3A1026"/><circle cx="{hx}" cy="{T+36}" r="21" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="3" transform="translate(0 2)"/>'
        body += f'<circle cx="{hx}" cy="{T+36}" r="13" fill="#2A0B1A"/>'
        body += f'<path d="M{hx-13} {T+36}a13 13 0 0 1 26 0" fill="none" stroke="#000" stroke-opacity=".5" stroke-width="3"/>'
    # bottom ambient occlusion on front
    body += f'<rect x="{L}" y="{B-90}" width="{R-62-L}" height="90" fill="url(#s-ao)" clip-path="url(#s-fc)"/>'
    defs += f'<clipPath id="s-fc"><path d="{front}"/></clipPath>'
    # stamp: keyhole badge (pressed ink)
    cxs, cys = (L + R - 62) // 2, 624
    body += f'<g transform="translate({cxs} {cys})">'
    body += f'<circle r="92" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="5" transform="translate(0 3)"/>'
    body += f'<circle r="92" fill="none" stroke="url(#s-stamp)" stroke-width="10"/>'
    body += f'<path d="M0 -50a27 27 0 0 1 14 50l17 52h-62l17 -52a27 27 0 0 1 14 -50z" fill="#fff" fill-opacity=".8" transform="translate(0 3)"/>'
    body += f'<path d="M0 -50a27 27 0 0 1 14 50l17 52h-62l17 -52a27 27 0 0 1 14 -50z" fill="url(#s-stamp)"/>'
    body += '</g>'
    return finish(cv, defs, body)

# ---------------------------------------------------------------- FILES (folder with paper depth)
def files(cv):
    container(cv, "#3FD1BE", "#0A5B66", glow="#CFFFF4", edge="#00302F", glow_op=.30); d = b = ""
    defs = d + paper_noise("grain", .035, .9)
    defs += shadow_filter("f-sh", dy=30, blur=22, color="#02262B", op=.55)
    defs += shadow_filter("f-psh", dy=10, blur=10, color="#02262B", op=.35)
    defs += blur_filter("f-b4", 4)
    defs += lingrad("f-back", [(0, "#1E9C98"), (1, "#0F6E79")])
    defs += lingrad("f-front", [(0, "#B7F7EC"), (.4, "#82E6D6"), (1, "#3FBBB0")])
    defs += lingrad("f-paper", [(0, "#FFFFFF"), (1, "#EAF1F0")])
    defs += lingrad("f-ao", [(0, "#033B40", 0), (1, "#033B40", .45)])
    defs += lingrad("f-fshade", [(0, "#fff", .55), (.06, "#fff", .0), (.7, "#005", 0), (1, "#012E3A", .28)])
    defs += lingrad("f-tabhl", [(0, "#8FF1E2"), (1, "#1E9C98")])
    back = ("M196 366V330a44 44 0 0 1 44-44H390a44 44 0 0 1 33 15L452 335H784a44 44 0 0 1 44 44V716a44 44 0 0 1-44 44H240a44 44 0 0 1-44-44Z")
    front = "M196 500a40 40 0 0 1 40-40H788a40 40 0 0 1 40 40V718a44 44 0 0 1-44 44H240a44 44 0 0 1-44-44Z"
    body = b
    body += f'<g filter="url(#f-sh)"><path d="{back}" fill="#0F6E79"/></g>'
    body += f'<path d="{back}" fill="url(#f-back)"/>'
    body += f'<path d="M240 290H390a44 44 0 0 1 33 15L440 324H196V334a44 44 0 0 1 44-44Z" fill="#fff" opacity=".16"/>'
    # papers
    def paper(x, y, w, h, rot, lines, accent):
        g = f'<g transform="rotate({rot} {x+w/2} {y+h/2})"><g filter="url(#f-psh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#f-paper)"/></g>'
        g += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#000" filter="url(#grain)"/>'
        g += f'<rect x="{x}" y="{y}" width="{w}" height="3" fill="#fff"/>'
        g += f'<rect x="{x+36}" y="{y+40}" width="{w*0.34:.0f}" height="20" rx="10" fill="{accent}" opacity=".9"/>'
        for i in range(lines):
            lw = w - 72 - (i % 2) * 60
            g += f'<rect x="{x+36}" y="{y+86+i*34}" width="{lw}" height="12" rx="6" fill="#8CA3A6" opacity=".55"/>'
        return g + '</g>'
    body += paper(330, 262, 420, 330, -3.6, 4, "#3FB5AC")
    body += paper(380, 226, 430, 340, 3.0, 4, "#7B6CF0")
    # front panel + ao on papers
    body += f'<rect x="196" y="{460-48}" width="632" height="56" fill="url(#f-ao)" clip-path="url(#f-pclip)"/>'
    defs += '<clipPath id="f-pclip"><rect x="200" y="200" width="624" height="260"/></clipPath>'
    body += f'<g filter="url(#f-psh)"><path d="{front}" fill="#3FBBB0"/></g>'
    body += f'<path d="{front}" fill="url(#f-front)"/>'
    body += f'<path d="{front}" fill="url(#f-fshade)"/>'
    body += f'<path d="M236 461.5H788a38 38 0 0 1 38 38" fill="none" stroke="#fff" stroke-width="5" stroke-opacity=".9"/>'
    body += f'<path d="M198 499a38 38 0 0 1 38-38" fill="none" stroke="#fff" stroke-width="5" stroke-opacity=".9"/>'
    body += f'<path d="{front}" fill="none" stroke="#0A5B66" stroke-opacity=".35" stroke-width="2"/>'
    # soft glass sheen on front, lower hem
    body += f'<rect x="212" y="746" width="600" height="6" rx="3" fill="#fff" opacity=".28"/>'
    return finish(cv, defs, body)

# ---------------------------------------------------------------- TERMINAL (dark glass)
def terminal(cv):
    container(cv, "#3A2D6E", "#0B0818", glow="#9B85FF", edge="#000", glow_op=.30); d = b = ""
    defs = d
    defs += shadow_filter("t-sh", dy=34, blur=26, color="#000", op=.7)
    defs += blur_filter("t-b14", 14) + blur_filter("t-b30", 30)
    defs += lingrad("t-win", [(0, "#5046A0"), (.12, "#3A3274"), (1, "#1E1848")] if cv.small else [(0, "#352D66"), (.12, "#241E48"), (1, "#0F0B24")])
    defs += lingrad("t-bar", [(0, "#fff", .14), (1, "#fff", .03)])
    defs += lingrad("t-rim", [(0, "#fff", .75), (.16, "#fff", .22), (.55, "#fff", .05), (1, "#fff", .20)])
    defs += lingrad("t-sheen", [(0, "#fff", .20), (1, "#fff", 0)], x1=0, y1=0, x2=.7, y2=1)
    defs += lingrad("t-mint", [(0, "#B8FFE6"), (1, "#2FD6A0")])
    defs += lingrad("t-dim", [(0, "#8B7FC9"), (1, "#5E52A0")])
    x0, y0, x1, y1, r = 186, 246, 838, 786, 62
    win = f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{r}"/>'
    defs += f'<clipPath id="t-clip">{win}</clipPath>'
    body = b
    body += f'<g filter="url(#t-sh)"><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{r}" fill="#0B0818"/></g>'
    body += f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="{r}" fill="url(#t-win)"/>'
    body += '<g clip-path="url(#t-clip)">'
    body += f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="92" fill="url(#t-bar)"/>'
    body += f'<rect x="{x0}" y="{y0+92}" width="{x1-x0}" height="3" fill="#000" opacity=".45"/>'
    body += f'<rect x="{x0}" y="{y0+95}" width="{x1-x0}" height="2" fill="#fff" opacity=".07"/>'
    # title pill
    body += f'<rect x="{(x0+x1)/2-90}" y="{y0+32}" width="180" height="26" rx="13" fill="#fff" opacity=".13"/>'
    # diagonal glass sheen
    body += f'<path d="M{x0} {y0}H{x0+380}L{x0+60} {y1}H{x0}Z" fill="url(#t-sheen)"/>'
    # dim output lines
    body += f'<rect x="{x0+70}" y="{y0+160}" width="300" height="24" rx="12" fill="url(#t-dim)" opacity=".7"/>'
    body += f'<rect x="{x0+70}" y="{y0+214}" width="200" height="24" rx="12" fill="url(#t-dim)" opacity=".45"/>'
    # glowing prompt
    chev = f'M{x0+98} {y0+300}L{x0+226} {y0+398}L{x0+98} {y0+496}'
    body += f'<path d="{chev}" fill="none" stroke="#2FD6A0" stroke-width="76" stroke-linecap="round" stroke-linejoin="round" opacity=".55" filter="url(#t-b30)"/>'
    body += f'<rect x="{x0+312}" y="{y0+414}" width="170" height="88" rx="14" fill="#2FD6A0" opacity=".6" filter="url(#t-b30)"/>'
    body += f'<path d="{chev}" fill="none" stroke="#0A3F33" stroke-width="58" stroke-linecap="round" stroke-linejoin="round" transform="translate(0 7)" opacity=".6"/>'
    body += f'<path d="{chev}" fill="none" stroke="url(#t-mint)" stroke-width="{70 if cv.small else 56}" stroke-linecap="round" stroke-linejoin="round"/>'
    body += f'<path d="{chev}" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" opacity=".55" transform="translate(-6 -10)"/>'
    body += f'<rect x="{x0+318}" y="{y0+418}" width="158" height="80" rx="14" fill="url(#t-mint)"/>'
    body += f'<rect x="{x0+318}" y="{y0+418}" width="158" height="13" rx="6" fill="#fff" opacity=".6"/>'
    body += '</g>'
    body += f'<rect x="{x0+1.5}" y="{y0+1.5}" width="{x1-x0-3}" height="{y1-y0-3}" rx="{r-1.5}" fill="none" stroke="url(#t-rim)" stroke-width="3"/>'
    return finish(cv, defs, body)


# ---------------------------------------------------------------- BROWSER (glossy globe)
def browser(cv):
    container(cv, "#2C5FC8", "#0A1B4F", glow="#7FB4FF", edge="#000A30", glow_op=.30); d = b = ""
    cx, cy, R = 512, 520, 290
    defs = d
    defs += blur_filter("w-b12", 12) + blur_filter("w-b30", 30) + blur_filter("w-b5", 5) + blur_filter("w-b40", 40)
    defs += radgrad("w-ocean", [(0, "#8CE4FF"), (.30, "#37A0F5"), (.62, "#1B5FD4"), (1, "#0B2A84")], cx=.36, cy=.28, r=.95)
    defs += radgrad("w-shade", [(0, "#001040", 0), (.55, "#001040", 0), (.86, "#001040", .38), (1, "#001040", .72)], cx=.40, cy=.34, r=.82)
    defs += radgrad("w-halo", [(.80, "#5CC8FF", .75), (1, "#5CC8FF", 0)])
    defs += lingrad("w-land", [(0, "#D9FBE2"), (.55, "#7EDDB0"), (1, "#2FA580")])
    defs += lingrad("w-rimlight", [(0, "#9BE7FF", 0), (.6, "#9BE7FF", 0), (1, "#BFF3FF", .95)])
    defs += lingrad("w-dome1", [(0, "#fff", .85), (1, "#fff", 0)])
    defs += lingrad("w-dome2", [(0, "#fff", .30), (1, "#fff", 0)])
    defs += f'<clipPath id="w-clip"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
    defs += shadow_filter("w-sh", dy=34, blur=24, color="#000A30", op=.6)
    lands = [
      smooth([(300,336),(346,292),(420,282),(476,306),(462,348),(424,376),(414,414),(446,446),(424,472),(386,448),(350,426),(316,398),(284,370)]),
      smooth([(436,490),(486,512),(512,562),(494,626),(458,690),(432,744),(410,700),(414,628),(392,566),(404,520)]),
      smooth([(548,318),(586,286),(640,292),(660,326),(622,350),(572,352)]),
      smooth([(556,396),(618,384),(674,408),(704,456),(676,520),(656,596),(624,672),(594,696),(578,628),(574,548),(544,494),(536,438)]),
      smooth([(690,320),(744,328),(786,384),(752,436),(710,412),(676,362)]),
    ]
    body = b
    # atmosphere glow behind the sphere
    body += f'<circle cx="{cx}" cy="{cy}" r="{R+34}" fill="#4FB6FF" opacity=".55" filter="url(#w-b30)"/>'
    body += f'<g filter="url(#w-sh)"><circle cx="{cx}" cy="{cy}" r="{R}" fill="#0B2A84"/></g>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#w-ocean)"/>'
    body += '<g clip-path="url(#w-clip)">'
    # graticule
    for rx in (90, 190, 270):
        body += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{R}" fill="none" stroke="#fff" stroke-opacity=".12" stroke-width="3"/>'
    for dy_ in (-150, 0, 150):
        body += f'<ellipse cx="{cx}" cy="{cy+dy_}" rx="{R}" ry="{70 + abs(dy_)*0.0}" fill="none" stroke="#fff" stroke-opacity=".10" stroke-width="3"/>' if dy_ != 0 else f'<line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="#fff" stroke-opacity=".10" stroke-width="3"/>'
    # land with its own bevel shadow
    for l in lands:
        body += f'<path d="{l}" fill="#002E70" opacity=".55" transform="translate(0 9)" filter="url(#w-b5)"/>'
        body += f'<path d="{l}" fill="url(#w-land)"/>'
        body += f'<path d="{l}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2.5" transform="translate(0 -2)" clip-path="url(#w-clip)"/>'
    # shading toward lower-right, rim light at the lower edge
    body += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#w-shade)"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R-10}" fill="none" stroke="url(#w-rimlight)" stroke-width="22" filter="url(#w-b12)"/>'
    # glass dome reflection (top) and specular
    body += f'<path d="M{cx-R+36} {cy-70}A{R-36} {R-36} 0 0 1 {cx+R-36} {cy-70}Q{cx} {cy-170} {cx-R+36} {cy-70}Z" fill="url(#w-dome2)" transform="translate(0 -14)"/>'
    body += f'<ellipse cx="{cx-100}" cy="{cy-170}" rx="96" ry="46" fill="url(#w-dome1)" transform="rotate(-32 {cx-100} {cy-170})" opacity=".9"/>'
    body += '</g>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R-1.5}" fill="none" stroke="#fff" stroke-opacity=".4" stroke-width="3" clip-path="url(#w-clip)"/>'
    return finish(cv, defs, body)

# ---------------------------------------------------------------- MUSIC (vinyl + tonearm)
def music(cv):
    container(cv, "#FF9553", "#D8381C", glow="#FFE0B8", edge="#5A0F00", glow_op=.34); d = b = ""
    cx, cy, R = 452, 560, 268
    defs = d
    defs += shadow_filter("m-sh", dy=34, blur=22, color="#4A0C00", op=.6)
    defs += shadow_filter("m-sh2", dy=16, blur=10, color="#000", op=.55)
    defs += blur_filter("m-b14", 14) + blur_filter("m-b8", 8) + blur_filter("m-b3", 3)
    defs += radgrad("m-vinyl", [(0, "#2C2C34"), (.5, "#121218"), (1, "#050508")], cx=.4, cy=.32, r=.85)
    defs += lingrad("m-label", [(0, "#FFF3E0"), (1, "#F9C795")])
    defs += lingrad("m-metal", [(0, "#FFFFFF"), (.45, "#D5D9E2"), (1, "#8B93A6")])
    defs += lingrad("m-metalh", [(0, "#9AA2B5"), (.35, "#FFFFFF"), (.7, "#C8CDD9"), (1, "#7B849A")], x1=0, y1=0, x2=1, y2=0)
    defs += lingrad("m-brass", [(0, "#FFF0B3"), (.5, "#E5A93B"), (1, "#8A5A12")])
    defs += lingrad("m-mat", [(0, "#FFFFFF", .55), (1, "#FFFFFF", .05)])
    defs += f'<clipPath id="m-clip"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
    body = b
    body += f'<g filter="url(#m-sh)"><circle cx="{cx}" cy="{cy}" r="{R+14}" fill="#2A0600"/></g>'
    # platter edge (aluminium) + record
    body += f'<circle cx="{cx}" cy="{cy}" r="{R+14}" fill="url(#m-metal)"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R+3}" fill="#1C1C22"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#m-vinyl)"/>'
    body += '<g clip-path="url(#m-clip)">'
    for i, r in enumerate(range(112, R, 5)):
        o = .10 + .10 * ((i * 53) % 5) / 5
        body += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{"#fff" if i%3 else "#000"}" stroke-opacity="{o:.2f}" stroke-width="1.6"/>'
    # track gaps
    for r in (170, 214):
        body += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#000" stroke-opacity=".8" stroke-width="5"/>'
    # anisotropic sheen wedges
    def wedge(a0, a1, r=300):
        p0 = (cx + r*math.cos(math.radians(a0)), cy + r*math.sin(math.radians(a0)))
        p1 = (cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1)))
        return f"M{cx} {cy}L{p0[0]:.1f} {p0[1]:.1f}L{p1[0]:.1f} {p1[1]:.1f}Z"
    body += f'<path d="{wedge(-150,-112)}" fill="#fff" opacity=".42" filter="url(#m-b14)"/>'
    body += f'<path d="{wedge(30,68)}" fill="#fff" opacity=".28" filter="url(#m-b14)"/>'
    body += '</g>'
    body += f'<circle cx="{cx}" cy="{cy}" r="{R-1.5}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="3"/>'
    # label
    body += f'<circle cx="{cx}" cy="{cy+3}" r="104" fill="#000" opacity=".4" filter="url(#m-b8)"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="104" fill="url(#m-label)"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="78" fill="none" stroke="#E0501F" stroke-width="10" opacity=".85"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="48" fill="#7C5CFF"/><circle cx="{cx}" cy="{cy}" r="48" fill="none" stroke="#fff" stroke-opacity=".45" stroke-width="3"/>'
    body += f'<path d="M{cx-48} {cy}a48 48 0 0 1 96 0z" fill="#fff" opacity=".18"/>'
    body += f'<circle cx="{cx}" cy="{cy+2}" r="17" fill="#000" opacity=".45"/>'
    body += f'<circle cx="{cx}" cy="{cy}" r="16" fill="url(#m-brass)"/><circle cx="{cx-5}" cy="{cy-6}" r="5" fill="#fff" opacity=".9"/>'
    # tonearm: pivot base, tube, headshell
    px, py = 782, 270
    tube = f'M{px} {py}L{px} {py+250}L{px-104} {py+362}'
    body += f'<g filter="url(#m-sh2)">'
    body += f'<path d="{tube}" fill="none" stroke="#9AA2B5" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/></g>'
    body += f'<path d="{tube}" fill="none" stroke="url(#m-metal)" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>'
    body += f'<path d="M{px-5} {py+10}L{px-5} {py+240}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity=".9"/>'
    body += f'<path d="M{px+8} {py+20}L{px+8} {py+250}L{px-92} {py+352}" fill="none" stroke="#5E667A" stroke-opacity=".5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    # counterweight
    body += f'<g filter="url(#m-sh2)"><rect x="{px-30}" y="{py-96}" width="60" height="92" rx="12" fill="#6C7488"/></g>'
    body += f'<rect x="{px-30}" y="{py-96}" width="60" height="92" rx="12" fill="url(#m-metalh)"/>'
    body += f'<rect x="{px-30}" y="{py-96}" width="60" height="9" rx="4" fill="#fff" opacity=".8"/>'
    # pivot cylinder
    body += f'<g filter="url(#m-sh2)"><circle cx="{px}" cy="{py}" r="58" fill="#6C7488"/></g>'
    body += f'<circle cx="{px}" cy="{py}" r="58" fill="url(#m-metal)"/>'
    body += f'<circle cx="{px}" cy="{py}" r="42" fill="url(#m-metalh)" opacity=".9"/>'
    body += f'<circle cx="{px}" cy="{py}" r="42" fill="none" stroke="#5E667A" stroke-width="3"/>'
    body += f'<circle cx="{px}" cy="{py}" r="15" fill="url(#m-brass)"/>'
    # headshell
    hx, hy = px-104, py+362
    body += f'<g transform="rotate(38 {hx} {hy})"><g filter="url(#m-sh2)"><rect x="{hx-30}" y="{hy-12}" width="60" height="84" rx="12" fill="#222"/></g>'
    body += f'<rect x="{hx-30}" y="{hy-12}" width="60" height="84" rx="12" fill="#2B2B33"/><rect x="{hx-30}" y="{hy-12}" width="60" height="9" rx="4" fill="#fff" opacity=".35"/>'
    body += f'<rect x="{hx-9}" y="{hy+60}" width="18" height="30" rx="4" fill="url(#m-brass)"/></g>'
    return finish(cv, defs, body)


# ---------------------------------------------------------------- MAIL (envelope + wax seal)
def mail(cv):
    container(cv, "#FF7C9D", "#B01F4F", glow="#FFD3DF", edge="#4A0620", glow_op=.34); d = b = ""
    L, R, T, B = 184, 840, 322, 740
    cx = (L + R) / 2
    tip = 566
    defs = d + paper_noise("grain", .035, .85)
    defs += shadow_filter("e-sh", dy=32, blur=22, color="#4A0620", op=.6)
    defs += shadow_filter("e-sh2", dy=14, blur=12, color="#5B2A18", op=.42)
    defs += shadow_filter("e-sh3", dy=10, blur=8, color="#2A0010", op=.6)
    defs += blur_filter("e-b4", 4) + blur_filter("e-b12", 12)
    defs += lingrad("e-body", [(0, "#F6E7D0"), (1, "#DCC3A0")])
    defs += lingrad("e-side", [(0, "#FBEFDB"), (1, "#E6D0B0")], x1=0, y1=0, x2=1, y2=0)
    defs += lingrad("e-sider", [(0, "#E6D0B0"), (1, "#FBEFDB")], x1=0, y1=0, x2=1, y2=0)
    defs += lingrad("e-bottom", [(0, "#FFF8EC"), (1, "#F0DDC0")])
    defs += lingrad("e-flap", [(0, "#FFFDF7"), (1, "#F5E5CB")])
    defs += radgrad("e-wax", [(0, "#F0597E"), (.5, "#C42049"), (1, "#7C0F33")], cx=.38, cy=.30, r=.9)
    defs += radgrad("e-waxin", [(0, "#8A1237"), (1, "#C42049")], cx=.5, cy=.3, r=.8)
    env = f'M{L+26} {T}H{R-26}A26 26 0 0 1 {R} {T+26}V{B-26}A26 26 0 0 1 {R-26} {B}H{L+26}A26 26 0 0 1 {L} {B-26}V{T+26}A26 26 0 0 1 {L+26} {T}Z'
    defs += f'<clipPath id="e-clip"><path d="{env}"/></clipPath>'
    body = b
    body += f'<g filter="url(#e-sh)"><path d="{env}" fill="#DCC3A0"/></g>'
    body += f'<path d="{env}" fill="url(#e-body)"/>'
    body += '<g clip-path="url(#e-clip)">'
    # inside colour hint (darker) under the flap
    # side flaps
    body += f'<path d="M{L} {T}L{cx-6} {tip-20}L{L} {B}Z" fill="url(#e-side)"/>'
    body += f'<path d="M{R} {T}L{cx+6} {tip-20}L{R} {B}Z" fill="url(#e-sider)"/>'
    # bottom flap (rises to the centre), casts a shadow upward-free: light from above so it lights its upper edge
    body += f'<g filter="url(#e-sh2)"><path d="M{L-4} {B+4}L{cx} {T+190}L{R+4} {B+4}Z" fill="#F0DDC0"/></g>'
    body += f'<path d="M{L-4} {B+4}L{cx} {T+190}L{R+4} {B+4}Z" fill="url(#e-bottom)"/>'
    body += f'<path d="M{L+2} {B}L{cx} {T+194}L{R-2} {B}" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" opacity=".9"/>'
    # top flap (closed) with shadow
    flap = f'M{L-4} {T-4}H{R+4}L{cx} {tip}Z'
    body += f'<g filter="url(#e-sh2)"><path d="{flap}" fill="#F5E5CB"/></g>'
    body += f'<path d="{flap}" fill="url(#e-flap)"/>'
    body += f'<path d="{flap}" fill="#000" filter="url(#grain)"/>'
    body += f'<path d="M{L+4} {T+4}L{cx} {tip-6}L{R-4} {T+4}" fill="none" stroke="#D2B58C" stroke-opacity=".7" stroke-width="3" stroke-linejoin="round" transform="translate(0 3)"/>'
    body += f'<path d="M{L} {T}H{R}" stroke="#fff" stroke-width="6" opacity=".95"/>'
    body += '</g>'
    # paper rim highlight on whole envelope
    body += f'<path d="{env}" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="3" clip-path="url(#e-clip)" transform="translate(0 2)"/>'
    body += f'<path d="{env}" fill="none" stroke="#7A4A22" stroke-opacity=".25" stroke-width="2"/>'
    # wax seal
    sx, sy = cx, tip - 4
    pts = []
    for k in range(120):
        t = 2 * math.pi * k / 120
        r = 82 + 4.5 * math.sin(7 * t + .6) + 2.8 * math.sin(11 * t + 2) + 1.8 * math.sin(3 * t)
        pts.append((sx + r * math.cos(t), sy + r * math.sin(t)))
    seal = "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
    body += f'<g filter="url(#e-sh3)"><path d="{seal}" fill="#7C0F33"/></g>'
    body += f'<path d="{seal}" fill="url(#e-wax)"/>'
    body += f'<path d="{seal}" fill="none" stroke="#FF9DB4" stroke-opacity=".6" stroke-width="3" transform="translate(0 -2)"/>'
    body += f'<circle cx="{sx}" cy="{sy}" r="56" fill="url(#e-waxin)"/>'
    body += f'<circle cx="{sx}" cy="{sy}" r="56" fill="none" stroke="#FF9DB4" stroke-opacity=".7" stroke-width="3" transform="translate(0 3)"/>'
    body += f'<circle cx="{sx}" cy="{sy}" r="56" fill="none" stroke="#5E0A25" stroke-opacity=".75" stroke-width="3" transform="translate(0 -1.5)"/>'
    # embossed door arch (brand motif)
    arch = f'M{sx-22} {sy+34}V{sy-6}a22 22 0 0 1 44 0V{sy+34}Z'
    body += f'<path d="{arch}" fill="#FF9DB4" opacity=".8" transform="translate(0 3)"/>'
    body += f'<path d="{arch}" fill="#6A0C2A" opacity=".95"/>'
    body += f'<ellipse cx="{sx-30}" cy="{sy-40}" rx="26" ry="11" fill="#fff" opacity=".55" transform="rotate(-35 {sx-30} {sy-40})"/>'
    return finish(cv, defs, body)

# ---------------------------------------------------------------- INSTALLER (open door, light spill)
def installer(cv):
    container(cv, "#9A80FF", "#3B20B8", glow="#D9CEFF", edge="#150560", glow_op=.30); d = b = ""
    defs = d
    defs += shadow_filter("i-sh", dy=26, blur=20, color="#150560", op=.6)
    defs += shadow_filter("i-sh2", dy=14, blur=16, color="#0A0230", op=.65)
    defs += blur_filter("i-b6", 6) + blur_filter("i-b30", 30) + blur_filter("i-b50", 50) + blur_filter("i-b3", 3)
    defs += lingrad("i-frame", [(0, "#F6F1FF"), (.5, "#D9CEFA"), (1, "#A794EC")])
    defs += radgrad("i-room", [(0, "#FFFDF0"), (.30, "#FFE98A"), (.65, "#FFB84A"), (1, "#FF8A3D")], cx=.5, cy=.78, r=.85)
    defs += lingrad("i-beam", [(0, "#FFE9A0", .95), (.55, "#FFD070", .38), (1, "#FFC060", 0)])
    defs += lingrad("i-reveal", [(0, "#4A2D10", .55), (.22, "#7A4A10", 0)])
    defs += lingrad("i-leaf", [(0, "#4B2AB8"), (1, "#7B5CF0")], x1=0, y1=0, x2=1, y2=0)
    defs += lingrad("i-leafv", [(0, "#fff", .22), (.2, "#fff", 0), (.85, "#0A0230", 0), (1, "#0A0230", .30)])
    defs += radgrad("i-knob", [(0, "#FFF3C0"), (.5, "#F0B13C"), (1, "#8A5A12")], cx=.35, cy=.3, r=.8)
    fx0, fx1, fy_top, fy_bot, fr = 352, 672, 238, 782, 160   # frame outer
    ix0, ix1, ir = 392, 632, 120                               # opening
    iy_top = 280
    frame = f'M{fx0} {fy_bot}V{fy_top+fr}A{fr} {fr} 0 0 1 {fx1} {fy_top+fr}V{fy_bot}Z'
    op = f'M{ix0} {fy_bot}V{iy_top+ir}A{ir} {ir} 0 0 1 {ix1} {iy_top+ir}V{fy_bot}Z'
    defs += f'<clipPath id="i-op"><path d="{op}"/></clipPath>'
    body = b
    # light bloom leaking around the frame
    body += f'<ellipse cx="512" cy="560" rx="280" ry="340" fill="#FFD36B" opacity=".30" filter="url(#i-b50)"/>'
    # floor beam spilling toward the viewer
    body += f'<path d="M{ix0} {fy_bot-4}L{ix1} {fy_bot-4}L836 872L318 872Z" fill="url(#i-beam)"/>'
    body += f'<path d="M{ix0+20} {fy_bot}L{ix1-20} {fy_bot}L770 850L360 850Z" fill="#FFF6D0" opacity=".30" filter="url(#i-b30)"/>'
    # frame (stone, with thickness)
    body += f'<g filter="url(#i-sh)"><path d="{frame}" fill="#A794EC"/></g>'
    body += f'<path d="{frame}" fill="url(#i-frame)"/>'
    body += f'<path d="M{fx0+3} {fy_bot}V{fy_top+fr}A{fr-3} {fr-3} 0 0 1 {fx1-3} {fy_top+fr}V{fy_bot}" fill="none" stroke="#fff" stroke-width="5" opacity=".9"/>'
    # opening: warm room
    body += f'<path d="{op}" fill="url(#i-room)"/>'
    body += '<g clip-path="url(#i-op)">'
    # inner reveal shadow (top and left sides get shade; light comes from the room)
    body += f'<path d="{op}" fill="none" stroke="#3A1F00" stroke-opacity=".5" stroke-width="30" filter="url(#i-b6)"/>'
    body += f'<rect x="{ix0}" y="{iy_top}" width="{ix1-ix0}" height="150" fill="url(#i-reveal)"/>'
    # floor line + glow
    body += f'<rect x="{ix0}" y="{fy_bot-34}" width="{ix1-ix0}" height="34" fill="#fff" opacity=".6" filter="url(#i-b6)"/>'
    body += '</g>'
    # open door leaf swung toward the viewer on the left (hinge on the opening's left)
    hx, htop, hbot = ix0 + 6, 316, fy_bot - 4
    ex, etop, ebot = 250, 262, 842
    def P(u, v):
        x = hx + (ex - hx) * u
        top = htop + (etop - htop) * u; bot = hbot + (ebot - hbot) * u
        return (x, top + (bot - top) * v)
    # leaf outline: slightly arched top
    a = P(0, 0); bb = P(1, 0); c = P(1, 1); dd = P(0, 1)
    mid = P(.5, 0)
    leaf = f'M{a[0]:.1f} {a[1]:.1f}Q{mid[0]:.1f} {mid[1]-26:.1f} {bb[0]:.1f} {bb[1]:.1f}L{c[0]:.1f} {c[1]:.1f}L{dd[0]:.1f} {dd[1]:.1f}Z'
    body += f'<g filter="url(#i-sh2)"><path d="{leaf}" fill="#2A1478"/></g>'
    body += f'<path d="{leaf}" fill="url(#i-leaf)"/>'
    body += f'<path d="{leaf}" fill="url(#i-leafv)"/>'
    # inset panels (bilinear mapped)
    def panel(u0, u1, v0, v1):
        q = [P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)]
        return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in q) + "Z", q
    for (u0, u1, v0, v1) in ((.18, .84, .10, .44), (.18, .84, .54, .90)):
        pth, q = panel(u0, u1, v0, v1)
        body += f'<path d="{pth}" fill="#1B0B60" opacity=".38"/>'
        body += f'<path d="M{q[3][0]:.1f} {q[3][1]:.1f}L{q[2][0]:.1f} {q[2][1]:.1f}L{q[1][0]:.1f} {q[1][1]:.1f}" fill="none" stroke="#C9BBFF" stroke-width="4" stroke-opacity=".75" stroke-linejoin="round"/>'
        body += f'<path d="M{q[3][0]:.1f} {q[3][1]:.1f}L{q[0][0]:.1f} {q[0][1]:.1f}L{q[1][0]:.1f} {q[1][1]:.1f}" fill="none" stroke="#0A0230" stroke-width="4" stroke-opacity=".6" stroke-linejoin="round"/>'
    # free edge highlight
    body += f'<path d="M{bb[0]:.1f} {bb[1]:.1f}L{c[0]:.1f} {c[1]:.1f}" stroke="#E9E1FF" stroke-width="6" opacity=".95"/>'
    body += f'<path d="M{a[0]:.1f} {a[1]:.1f}Q{mid[0]:.1f} {mid[1]-26:.1f} {bb[0]:.1f} {bb[1]:.1f}" fill="none" stroke="#fff" stroke-width="4" opacity=".6"/>'
    # knob
    kx, ky = P(.74, .52)
    body += f'<circle cx="{kx:.1f}" cy="{ky+5:.1f}" r="19" fill="#0A0230" opacity=".55" filter="url(#i-b3)"/>'
    body += f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="19" fill="url(#i-knob)"/>'
    body += f'<circle cx="{kx-5:.1f}" cy="{ky-6:.1f}" r="5" fill="#fff" opacity=".9"/>'
    return finish(cv, defs, body)

