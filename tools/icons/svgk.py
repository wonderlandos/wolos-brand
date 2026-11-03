# SPDX-License-Identifier: GPL-2.0-or-later
"""Drawing kit of the WolOS icon language (design/icons/LANGUAGE.md): a 1024 canvas,
one key light straight above, gradients and blurs only (no <image>, <text>, scripts).

Cv is one icon in the making: it collects <defs>, hands out gradient, filter and clip ids, and
renders the SVG. Its body has two layers, the TILE (container or object finish) and the GLYPH; the
glyph is scaled about the optical centre (`scale`), which is how the small variant (16-64 px
renders) gets its larger live area. A glyph can also be left out (tile_only) for the legibility
check in checks.py."""
import math
import re

W = 1024
GLYPH = "\x00glyph\x00"       # marks where the tile ends and the glyph starts


def n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---- paths ----------------------------------------------------------------------------------
def rr_path(x0, y0, x1, y1, tl, tr, br, bl, n_=3.0, steps=24):
    """Rounded rectangle whose corners are superellipse arcs of exponent n_ (2 is a circle; more is
    the continuous 'soft' corner of a squircle)."""
    def arc(cx, cy, r, quad):
        out = []
        for i in range(steps + 1):
            t = (math.pi / 2) * i / steps
            ex, ey = math.cos(t) ** (2 / n_), math.sin(t) ** (2 / n_)
            out.append([(cx - r * ex, cy - r * ey), (cx + r * ey, cy - r * ex),
                        (cx + r * ex, cy + r * ey), (cx - r * ey, cy + r * ex)][quad])
        return out
    pts = (arc(x0 + tl, y0 + tl, tl, 0) + arc(x1 - tr, y0 + tr, tr, 1) +
           arc(x1 - br, y1 - br, br, 2) + arc(x0 + bl, y1 - bl, bl, 3))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


def rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f"M{n(x + r)} {n(y)}H{n(x + w - r)}A{n(r)} {n(r)} 0 0 1 {n(x + w)} {n(y + r)}V{n(y + h - r)}"
            f"A{n(r)} {n(r)} 0 0 1 {n(x + w - r)} {n(y + h)}H{n(x + r)}A{n(r)} {n(r)} 0 0 1 {n(x)} {n(y + h - r)}"
            f"V{n(y + r)}A{n(r)} {n(r)} 0 0 1 {n(x + r)} {n(y)}Z")


def circ(cx, cy, r):
    return f"M{n(cx - r)} {n(cy)}a{n(r)} {n(r)} 0 1 0 {n(2 * r)} 0a{n(r)} {n(r)} 0 1 0 {n(-2 * r)} 0Z"


def poly(pts):
    return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts) + "Z"


def smooth(points, closed=True, t=.5):
    """Catmull-Rom through the points as cubic beziers."""
    k = len(points)
    d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    for i in (range(k) if closed else range(k - 1)):
        p0, p1, p2, p3 = points[(i - 1) % k], points[i], points[(i + 1) % k], points[(i + 2) % k]
        if not closed:
            p0, p3 = points[max(i - 1, 0)], points[min(i + 2, k - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + ("Z" if closed else "")


def gear_poly(cx, cy, teeth=10, r_out=288, r_root=226, base=10.5, tip=6.2):
    pts, pitch = [], 360 / teeth
    for i in range(teeth):
        a = i * pitch - 90
        for r, ang in ((r_root, a - base - 3.5), (r_root, a - base), (r_out, a - tip), (r_out, a + tip),
                       (r_root, a + base), (r_root, a + base + 3.5)):
            t = math.radians(ang)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        for k in range(1, 5):
            t = math.radians(a + base + 3.5 + (pitch - 2 * (base + 3.5)) * k / 5)
            pts.append((cx + r_root * math.cos(t), cy + r_root * math.sin(t)))
    return poly(pts)


def wedge(cx, cy, a0, a1, r=340):
    p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p1 = (cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1)))
    return f"M{cx} {cy}L{p0[0]:.1f} {p0[1]:.1f}L{p1[0]:.1f} {p1[1]:.1f}Z"


# ---- colour ---------------------------------------------------------------------------------
def _rgb(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    x, y = _rgb(a), _rgb(b)
    return "#%02X%02X%02X" % tuple(round(x[i] + (y[i] - x[i]) * t) for i in range(3))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in _rgb(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


# ---- the GTK pass ---------------------------------------------------------------------------
# GTK 4 draws SVG icons with its own renderer, which sizes a filter's source from the geometry
# bounds of what is filtered: on a thin stroke (a bare vertical stem) or an offset copy those
# bounds collapse and the shadow floods a grey or dark block (design/tools/icons/gtkcheck). Every
# filtered element therefore draws inside a group that opens with this rect: canvas-sized, no
# pixels (fill-opacity 0), so librsvg draws exactly the same.
PAD = '<rect width="1024" height="1024" fill="#000" fill-opacity="0"/>'
_FILTERED_G = re.compile(r'(<g\b[^>]*\sfilter="url\(#[^)]+\)"[^>]*>)(?!' + re.escape(PAD) + ')')
_FILTERED_LEAF = re.compile(r'<(?!g\b)[a-z]+\b[^>]*\sfilter="url\(#[^)]+\)"[^>]*/>')
# Applied after the filter (SVG order: filter, clip, mask, opacity) or around it (transform): these
# move from a filtered leaf to the wrapping group.
_OUTER = ("transform", "clip-path", "mask", "opacity")


def _wrap_leaf(m):
    el = m.group(0)
    outer = []
    for a in _OUTER:
        v = re.search(rf'\s{a}="([^"]*)"', el)
        if v:
            outer.append(f' {a}="{v.group(1)}"')
            el = el.replace(v.group(0), "", 1)
    f = re.search(r'\sfilter="([^"]*)"', el)
    el = el.replace(f.group(0), "", 1)
    inner = f'<g filter="{f.group(1)}">{PAD}{el}</g>'
    return f'<g{"".join(outer)}>{inner}</g>' if outer else inner


def gtk_safe(svg):
    """Every filtered element of svg drawn the same by GTK 4 and librsvg (PAD above)."""
    svg = _FILTERED_G.sub(lambda m: m.group(1) + PAD, svg)
    return _FILTERED_LEAF.sub(_wrap_leaf, svg)


# ---- the Qt pass ----------------------------------------------------------------------------
# QtSvg (Qt 6.12: the renderer Qt apps load SVG theme icons with) draws masks and the blur filters
# but ignores clip-path, so a clipped glow or mesh spills over the card (qtcheck/check.sh). Every
# clipPath is therefore written as the same shape in a white luminance mask: librsvg and GTK draw
# it pixel for pixel like the clip, Qt draws it at all. The mask region is three canvases wide, so
# a clip used inside a moved or rotated group never cuts its content. A clipPath holds one shape.
_CLIP = re.compile(r'<clipPath id="([^"]+)">(<(?:path|rect|circle|ellipse)\b[^>]*/>)</clipPath>')
_REGION = 'maskUnits="userSpaceOnUse" x="-1024" y="-1024" width="3072" height="3072"'


def _white(shape):
    shape = re.sub(r'\s(?:fill|fill-opacity|stroke|stroke-width|opacity)="[^"]*"', "", shape)
    return shape[:-2] + ' fill="#fff"/>'


def qt_safe(svg):
    """Every clipPath of svg as a luminance mask of the same shape (QtSvg ignores clip-path)."""
    ids = []

    def mask(m):
        ids.append(m.group(1))
        return f'<mask id="{m.group(1)}" {_REGION}>{_white(m.group(2))}</mask>'
    svg = _CLIP.sub(mask, svg)
    if "<clipPath" in svg:
        raise ValueError("qt_safe: a clipPath that is not one plain shape")
    for i in ids:
        svg = svg.replace(f'clip-path="url(#{i})"', f'mask="url(#{i})"')
    return svg


# ---- the canvas -----------------------------------------------------------------------------
class Cv:
    def __init__(self, small=False):
        self.small = small
        self.defs, self.tile, self.glyph = [], [], []
        self._ids = {}
        self._to = self.tile        # add() writes here

    # ids
    def _def(self, key, prefix, make):
        if key not in self._ids:
            self._ids[key] = f"{prefix}{len(self._ids)}"
            self.defs.append(make(self._ids[key]))
        return f"url(#{self._ids[key]})"

    @staticmethod
    def _stops(stops):
        return "".join(f'<stop offset="{t[0]}" stop-color="{t[1]}"' + (f' stop-opacity="{t[2]}"' if len(t) > 2 else "") + "/>"
                       for t in stops)

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, user=False):
        u = ' gradientUnits="userSpaceOnUse"' if user else ""
        return self._def(("lin", tuple(stops), x1, y1, x2, y2, user), "g",
                         lambda i: f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{self._stops(stops)}</linearGradient>')

    def rad(self, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, user=False):
        u = ' gradientUnits="userSpaceOnUse"' if user else ""
        f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
        return self._def(("rad", tuple(stops), cx, cy, r, fx, fy, user), "r",
                         lambda i: f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{self._stops(stops)}</radialGradient>')

    def blur(self, sd):
        return self._def(("blur", sd), "b",
                         lambda i: f'<filter id="{i}" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1224" height="1224"><feGaussianBlur stdDeviation="{sd}"/></filter>')

    def clip(self, d):
        return self._def(("clip", d), "c", lambda i: f'<clipPath id="{i}"><path d="{d}"/></clipPath>')

    def raw(self, key, make):
        """A one-off def (filter, mask) built by make(id) -> markup; -> url(#id)."""
        return self._def(("raw", key), "x", make)

    def grain(self, op=.035, freq=.85):
        def make(i):
            return (f'<filter id="{i}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                    f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="7"/>'
                    f'<feColorMatrix values="0 0 0 0 .25  0 0 0 0 .18  0 0 0 0 .1  0 0 0 {op * 3:.3f} {-op * .9:.3f}" result="n"/>'
                    f'<feComposite in="n" in2="SourceAlpha" operator="in"/></filter>')
        return self._def(("grain", op, freq), "n", make)

    # layers
    def add(self, s):
        self._to.append(s)

    def begin_glyph(self):
        self._to = self.glyph

    def svg(self, title, scale=1.0, cy=512, tile_only=False):
        g = "".join(self.glyph)
        if scale != 1.0:
            g = f'<g transform="translate(512 {n(cy)}) scale({scale:.3f}) translate(-512 {n(-cy)})">{g}</g>'
        body = "".join(self.tile) + ("" if tile_only else g)
        return qt_safe(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">'
                       f'<title>{title}</title><defs>{"".join(self.defs)}</defs>{gtk_safe(body)}</svg>\n')


# ---- lighting helpers (the light model, LANGUAGE.md sections 1 and 2) ----------------------------
def shadow(cv, d, dy=28, sd=22, color="#000000", op=.55, dx=0, extra=""):
    """A soft cast shadow of path d, straight down (the key light is above)."""
    return (f'<path d="{d}" fill="{color}" opacity="{op}" filter="{cv.blur(sd)}" '
            f'transform="translate({dx} {dy})"{extra}/>')


def shadows(cv, d, color, amb=(30, 22, .55), con=(9, 7, .42)):
    """Ambient plus contact shadow, both the object's own darkest tone."""
    out = shadow(cv, d, amb[0], amb[1], color, amb[2])
    if con:
        out += shadow(cv, d, con[0], con[1], color, con[2])
    return out


def rimlight(cv, d, w=5, top=.85, mid=.0, bot=0.0, clip=True):
    """The lit lip: a white stroke on the inside of the edge, bright at the top, gone by mid height."""
    g = cv.lin([(0, "#fff", top), (.35, "#fff", mid), (.8, "#fff", 0), (1, "#fff", bot)])
    s = f'<path d="{d}" fill="none" stroke="{g}" stroke-width="{w * 2}"/>'
    return f'<g clip-path="{cv.clip(d)}">{s}</g>' if clip else s


def solid(cv, d, top, bot, shade=None, edge=None, lip=5, amb=(30, 22, .55), con=(9, 7, .42), x1=0, y1=0, x2=0, y2=1):
    """A lit object: shadows, ramp body, lit lip, hairline. -> markup."""
    sc = shade or mix(bot, "#000000", .55)
    out = shadows(cv, d, sc, amb, con) if amb else ""
    out += f'<path d="{d}" fill="{cv.lin([(0, top), (1, bot)], x1, y1, x2, y2)}"/>'
    if lip:
        out += rimlight(cv, d, lip)
    if edge:
        out += f'<path d="{d}" fill="none" stroke="{edge}" stroke-opacity=".35" stroke-width="2"/>'
    return out


def ellipse_spec(cv, x, y, rx, ry, rot=0, op=.8, sd=0):
    return (f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rx)}" ry="{n(ry)}" fill="#fff" opacity="{op}" '
            f'transform="rotate({rot} {n(x)} {n(y)})"' + (f' filter="{cv.blur(sd)}"' if sd else "") + "/>")


def soft_ring(cv, cx, cy, r, w, sd, color, op, clip=None):
    """A ring of width w and radius r blurred by sd, as a radial gradient (the blur across the
    radius, Gaussian against the band): GTK 4 and librsvg blur a thin stroke differently at icon
    sizes, a gradient they draw the same."""
    phi = lambda x: .5 * (1 + math.erf(x / (sd * math.sqrt(2))))
    lo, hi = max(0.0, r - w / 2 - 3 * sd), r + w / 2 + 3 * sd
    stops = []
    for i in range(25):
        t = lo + (hi - lo) * i / 24
        a = op * (phi(t - (r - w / 2)) - phi(t - (r + w / 2)))
        stops.append((round(t / hi, 4), color, round(a, 4)))
    g = cv.rad(stops, cx, cy, hi, user=True)
    ring = f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(hi)}" fill="{g}"/>'
    return f'<g clip-path="{clip}">{ring}</g>' if clip else ring


def tube(cv, d, w, top, bot, shade, hl=.7, amb=(16, 10, .5)):
    """A stroked tube: shadow, body, a highlight line on its upper edge."""
    ln = 'stroke-linecap="round" stroke-linejoin="round" fill="none"'
    out = f'<path d="{d}" {ln} stroke="{shade}" stroke-width="{w}" opacity="{amb[2]}" filter="{cv.blur(amb[1])}" transform="translate(0 {amb[0]})"/>'
    out += f'<path d="{d}" {ln} stroke="{bot}" stroke-width="{w}"/>'
    out += f'<path d="{d}" {ln} stroke="{top}" stroke-width="{w * .62:.1f}" transform="translate(0 {-w * .12:.1f})"/>'
    if hl:
        out += f'<path d="{d}" {ln} stroke="#fff" stroke-width="{max(3, w * .14):.1f}" opacity="{hl}" transform="translate(0 {-w * .26:.1f})"/>'
    return out


def knob(cv, cx, cy, r, c0="#FFF3C0", c1="#F0B13C", c2="#8A5A12", sh="#2A1500", dy=12):
    """A round lit boss (brass, by default)."""
    return (shadow(cv, circ(cx, cy, r), dy, max(4, r * .35), sh, .55) +
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{cv.rad([(0, c0), (.5, c1), (1, c2)], .35, .3, .8)}"/>'
            f'<circle cx="{n(cx - r * .28)}" cy="{n(cy - r * .32)}" r="{n(max(2.5, r * .2))}" fill="#fff" opacity=".85"/>')


# ---- the container (LANGUAGE.md section 3) -----------------------------------------------------
X0, Y0, X1, Y1 = 100, 100, 924, 924
CARD = rr_path(X0, Y0, X1, Y1, 236, 150, 236, 150, n_=3.1)


def lift(c, t):
    return mix(c, "#FFFFFF", t)


def container(cv, top, bot, glow="#fff", edge="#000", glow_op=.26, kit=False):
    """The soft card: ramp, top glow, bottom darkening, inner rim light, hairline, two shadows. The
    small variant lifts a dark ramp so a dark glyph still separates from its tile."""
    if cv.small and lum(bot) < .05:
        top, bot = lift(top, .16), lift(bot, .20)
        glow_op += .06
    p = CARD
    clip = cv.clip(p)
    out = (shadow(cv, p, 26, 26, "#000", .42) + shadow(cv, p, 8, 6, "#000", .50) +
           f'<path d="{p}" fill="{cv.lin([(0, top), (1, bot)])}"/>'
           f'<g clip-path="{clip}">'
           f'<rect x="0" y="0" width="1024" height="620" fill="{cv.rad([(0, glow, glow_op), (1, glow, 0)], .5, 0, .75)}"/>'
           f'<rect x="0" y="0" width="1024" height="1024" fill="{cv.lin([(.55, "#000", 0), (1, "#000", .22)])}"/>')
    if kit:     # a lid: a seam across the top fifth, the band above it a step lighter
        ly = 262
        out += (f'<rect x="0" y="0" width="1024" height="{ly}" fill="#fff" opacity=".10"/>'
                f'<rect x="0" y="{ly}" width="1024" height="5" fill="#000" opacity=".38"/>'
                f'<rect x="0" y="{ly + 5}" width="1024" height="3" fill="#fff" opacity=".28"/>')
    out += (f'<path d="{p}" fill="none" stroke="{cv.lin([(0, "#fff", .70), (.12, "#fff", .30), (.45, "#fff", 0), (.78, "#fff", 0), (1, "#fff", .16)])}" stroke-width="7"/>'
            f'</g><path d="{p}" fill="none" stroke="{edge}" stroke-opacity=".38" stroke-width="2"/>')
    cv.add(out)
    cv.begin_glyph()


# ---- string builders with explicit ids (the hand-built objects in crafted_a.py use these) ----------
def lingrad(gid, stops, x1=0, y1=0, x2=0, y2=1, units=None):
    u = f' gradientUnits="{units}"' if units else ""
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{Cv._stops(stops)}</linearGradient>'


def radgrad(gid, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, units=None):
    u = f' gradientUnits="{units}"' if units else ""
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    return f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{Cv._stops(stops)}</radialGradient>'


def blur_filter(fid, sd):
    return f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1224" height="1224"><feGaussianBlur stdDeviation="{sd}"/></filter>'


def shadow_filter(fid, dy=24, blur=20, color="#000", op=.4, dx=0):
    return (f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1224" height="1224" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur in="SourceAlpha" stdDeviation="{blur}"/><feOffset dx="{dx}" dy="{dy}" result="o"/>'
            f'<feFlood flood-color="{color}" flood-opacity="{op}"/><feComposite in2="o" operator="in" result="s"/>'
            f'<feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def paper_noise(fid="grain", op=.07, freq=.9):
    """Paper grain: noise over the filter region, not tied to the source's alpha. Draw it with
    grained(), which clips it to the shape, so a renderer that ignores filters draws nothing."""
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="7"/>'
            f'<feColorMatrix values="0 0 0 0 .25  0 0 0 0 .18  0 0 0 0 .1  0 0 0 {op * 3} {-op * 0.9}"/></filter>')


def grained(cid, shape, fid="grain"):
    """Grain on one shape (a self-closing <path>/<rect>): the clipPath def with id cid and the markup,
    the shape itself invisible (fill-opacity 0) and filtered, the noise clipped to its outline.
    -> (defs, markup)."""
    clip = f'<clipPath id="{cid}">{shape}</clipPath>'
    el = shape[:-2] + f' fill-opacity="0" filter="url(#{fid})"/>'
    return clip, f'<g clip-path="url(#{cid})">{el}</g>'


def finish(cv, defs, body):
    """Hand-built icons: their defs and glyph markup go onto the canvas."""
    cv.defs.append(defs)
    cv.glyph.append(body)
    return cv
