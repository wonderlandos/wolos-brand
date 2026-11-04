# SPDX-License-Identifier: GPL-2.0-or-later
"""Score a drawing against the east calculus (docs/adr/brand-east.md section 7).

  python3 -I design/tools/east/score.py FILE.svg|FILE.png [--kind icon|mark|screen|wallpaper]
                                        [--tree TREE.json] [--json]

Eight rules, each 0-100 (formulas in docs/adr/brand-east.md section 7 and in each r_* below):
  qi (attention path), sha (straight and sharp aggression), forms (water and mountain),
  zones (nine-zone balance), palette (five phases), light (one source, back never brighter
  than front), proportion (module and door-light ruler), density (layered planes); total = mean.
An SVG is rendered with rsvg-convert and measured as pixels; a layout tree (JSON, see
tree_scores) adds exact lengths, gaps and adjacency. Needs numpy, scipy and Pillow.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.cluster.vq import kmeans2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculus as K  # noqa: E402
from colour import element, relation, rgb2hex  # noqa: E402

RULES = ("qi", "sha", "forms", "zones", "palette", "light", "proportion", "density")


# ---------------------------------------------------------------- pixels
def load(path, size=None, bg=None):
    """RGBA float array. SVGs are rendered by rsvg-convert at `size` (longest side)."""
    if path.endswith(".svg"):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "r.png")
            args = ["rsvg-convert", path, "-o", out]
            if size:
                args[1:1] = ["-w", str(size)]
            if bg:
                args[1:1] = ["-b", bg]
            subprocess.run(args, check=True)
            im = Image.open(out).convert("RGBA")
            im.load()
    else:
        im = Image.open(path).convert("RGBA")
    if size and max(im.size) != size and not path.endswith(".svg"):
        r = size / max(im.size)
        im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
    return np.asarray(im).astype(np.float64) / 255.0


def oklab(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    lms = np.cbrt(c @ M1.T)
    return lms @ M2.T


def lab2hex(lab):
    L, a, b = lab
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    g = [12.92 * v if v <= 0.0031308 else 1.055 * max(v, 0) ** (1 / 2.4) - 0.055 for v in lin]
    return rgb2hex([min(1, max(0, v)) for v in g])


class Px:
    """Measured picture: OKLab pixels, opacity mask, colour regions, salience."""

    def __init__(self, arr, kind):
        self.kind = kind
        self.h, self.w = arr.shape[:2]
        self.alpha = arr[..., 3]
        self.mask = self.alpha > 0.5
        rgb = arr[..., :3]
        # composite translucent edges on the dominant colour so they do not form regions
        self.lab = oklab(rgb)
        self.u = (min(self.w, self.h) / 16) if kind in ("icon", "mark") else K.U * (self.w / max(self.w, 1))
        self._regions()
        self._field()
        self._salience()

    def _field(self):
        """Ground colour at every pixel: a quadratic fit (x, y) to the ground pixels. For an icon the
        ground is the card body, sampled in a ring 1 to 2 fen inside its silhouette."""
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        if self.kind == "icon":
            fen = (np.nonzero(self.mask.any(0))[0].ptp() + 1) / K.ZUCAI
            e1 = ndimage.binary_erosion(self.mask, iterations=max(1, round(0.6 * fen)))
            e2 = ndimage.binary_erosion(self.mask, iterations=max(2, round(1.6 * fen)))
            sel = e1 & ~e2
        else:
            sel = self.rid == self.ground if self.ground is not None else self.mask
        X = np.stack([np.ones(sel.sum()), xs[sel] / self.w, ys[sel] / self.h,
                      (xs[sel] / self.w) ** 2, (ys[sel] / self.h) ** 2, xs[sel] * ys[sel] / self.w / self.h], 1)
        coef = []
        for i in range(3):
            y = self.lab[..., i][sel]
            c, *_ = np.linalg.lstsq(X, y, rcond=None)
            # one refit without the worst 20 % (content that touches the ring)
            r = np.abs(X @ c - y)
            keep = r <= np.quantile(r, 0.8)
            c, *_ = np.linalg.lstsq(X[keep], y[keep], rcond=None)
            coef.append(c)
        A = np.stack([np.ones_like(xs, float), xs / self.w, ys / self.h, (xs / self.w) ** 2, (ys / self.h) ** 2, xs * ys / self.w / self.h], -1)
        self.field = np.stack([A @ c for c in coef], -1)
        self.de = np.sqrt(((self.lab - self.field) ** 2).sum(-1))
        self.de[~self.mask] = 0

    def _regions(self, k=8):
        pts = self.lab[self.mask]
        rng = np.random.default_rng(7)
        sample = pts[rng.choice(len(pts), min(len(pts), 6000), replace=False)]
        cent, _ = kmeans2(sample, k, minit="++", seed=7)
        d = ((self.lab[..., None, :] - cent[None, None]) ** 2).sum(-1)
        lab_ = d.argmin(-1)
        lab_[~self.mask] = -1
        self.cluster = lab_
        self.centres = cent
        regions, rid = [], np.zeros(lab_.shape, int) - 1
        area = self.mask.sum()
        for c in range(len(cent)):
            comp, n = ndimage.label(lab_ == c)
            if n == 0:
                continue
            sizes = ndimage.sum(np.ones_like(comp), comp, range(1, n + 1))
            for i, s in enumerate(sizes, 1):
                if s >= 0.003 * area:
                    m = comp == i
                    rid[m] = len(regions)
                    ys, xs = np.nonzero(m)
                    regions.append({"cluster": c, "area": float(s) / area, "mask": m,
                                    "bbox": (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1),
                                    "lab": self.lab[m].mean(0)})
        self.regions, self.rid = regions, rid
        self.ground = max(range(len(regions)), key=lambda i: regions[i]["area"]) if regions else None

    def _salience(self):
        sig = max(self.w, self.h) / 8
        blur = np.stack([ndimage.gaussian_filter(np.where(self.mask, self.lab[..., i], 0), sig) for i in range(3)], -1)
        wsum = ndimage.gaussian_filter(self.mask.astype(float), sig) + 1e-9
        blur = blur / wsum[..., None]
        s = np.sqrt(((self.lab - blur) ** 2).sum(-1)) + 0.5 * np.hypot(self.lab[..., 1], self.lab[..., 2])
        s[~self.mask] = 0
        self.sal = s


# ---------------------------------------------------------------- rules on pixels
def r_palette(p):
    regs = p.regions
    if len(regs) < 2:
        return 100.0, {"pairs": 0}
    # adjacency by boundary length (4-neighbour)
    pairs = {}
    for a, b in ((p.rid[:, 1:], p.rid[:, :-1]), (p.rid[1:, :], p.rid[:-1, :])):
        m = (a != b) & (a >= 0) & (b >= 0)
        for x, y in zip(a[m], b[m]):
            key = (min(x, y), max(x, y))
            pairs[key] = pairs.get(key, 0) + 1
    tot = sws = 0.0
    bad = []
    for (i, j), n in pairs.items():
        ei = element(_lch(regs[i]["lab"]))
        ej = element(_lch(regs[j]["lab"]))
        rel = relation(ei, ej)
        small = min(regs[i]["area"], regs[j]["area"])
        if rel in ("same", "sheng"):
            s = 1.0
        else:
            cap = K.ACCENT_SHARE if rel == "ke" else 2 * K.ACCENT_SHARE
            s = 1.0 if small <= cap else max(0.0, 1 - (small - cap) / (2 * cap))
            if s < 1:
                bad.append((lab2hex(regs[i]["lab"]), lab2hex(regs[j]["lab"]), rel, round(small, 3)))
        tot += n * s
        sws += n
    return 100 * tot / sws, {"pairs": len(pairs), "over_budget": bad[:6]}


def _lch(lab):
    L, a, b = lab
    return float(L), float(math.hypot(a, b)), math.degrees(math.atan2(b, a)) % 360


def r_light(p):
    """Shading agrees with the one light (upper left): the ground field's slope, and the slope inside
    objects (pixels well off the ground, so cast shadows on the ground do not count against it)."""
    L = p.lab[..., 0]
    lx, ly = K.LIGHT
    fy, fx = np.gradient(p.field[..., 0])
    fm = np.hypot(fx, fy)[p.mask]
    if fm.sum() < 1e-6 * p.mask.sum():
        ground = 70.0
    else:
        ground = 50 + 50 * float(((fx[p.mask] * lx + fy[p.mask] * ly)).sum() / fm.sum())
    gy, gx = np.gradient(ndimage.gaussian_filter(L, 1.0))
    obj = ndimage.binary_erosion(p.mask & (p.de > 0.12), iterations=2)
    for r in p.regions:
        pass
    inner = np.zeros_like(p.mask)
    for r in p.regions:
        inner |= ndimage.binary_erosion(r["mask"], iterations=2)
    sel = obj & inner
    mag = np.hypot(gx, gy)
    sel &= mag > 1e-3
    if sel.sum() < 0.01 * p.mask.sum() or mag[sel].sum() < 1e-6:
        objs = 70.0
    else:
        objs = 50 + 50 * float((gx[sel] * lx + gy[sel] * ly).sum() / mag[sel].sum())
    shade = (ground + objs) / 2
    shade_note = f"ground {ground:.0f}, objects {objs:.0f}"
    # shadow side: just outside each non-ground region, the side away from the light is darker
    agree = n = 0.0
    off = max(2, round(min(p.w, p.h) / 40))
    for i, r in enumerate(p.regions):
        if i == p.ground or r["area"] < 0.01:
            continue
        m = r["mask"]
        sh = np.roll(np.roll(m, round(-lx * off * 1.4), 1), round(-ly * off * 1.4), 0) & ~m & p.mask
        li = np.roll(np.roll(m, round(lx * off * 1.4), 1), round(ly * off * 1.4), 0) & ~m & p.mask
        if sh.sum() < 4 or li.sum() < 4:
            continue
        d = L[li].mean() - L[sh].mean()
        agree += r["area"] * (1.0 if d > 0.004 else 0.6 if d > -0.004 else 0.0)
        n += r["area"]
    shadow = 100 * agree / n if n else 70.0
    # back never brighter than front: a plane (>= 2 % of the frame) lying inside another plane's
    # box must not be darker than it by more than 0.02 in OKLab L
    planes = [r for r in p.regions if r["area"] >= 0.02]
    pairs = okp = 0
    for fr in planes:
        for bk in planes:
            if fr is bk or bk["area"] <= fr["area"]:
                continue
            fx0, fy0, fx1, fy1 = fr["bbox"]
            bx0, by0, bx1, by1 = bk["bbox"]
            if fx0 >= bx0 and fy0 >= by0 and fx1 <= bx1 and fy1 <= by1:
                pairs += 1
                okp += fr["lab"][0] >= bk["lab"][0] - 0.02
                break
    order = 100 * okp / pairs if pairs else 100.0
    v = 0.45 * shade + 0.3 * shadow + 0.25 * order
    return v, {"shading": shade_note, "shadow_side": round(shadow, 1), "back_not_brighter": f"{okp}/{pairs}"}


def _blobs(p, k=6):
    """The heaviest salient masses (top 15 % salience, connected), heaviest first."""
    s = p.sal
    thr = np.quantile(s[p.mask], 0.85)
    comp, n = ndimage.label(s >= thr)
    out = []
    for i in range(1, n + 1):
        m = comp == i
        mass = float(s[m].sum())
        ys, xs = np.nonzero(m)
        out.append({"mass": mass, "c": (xs.mean() / p.w, ys.mean() / p.h), "n": len(xs),
                    "box": (xs.min() / p.w, ys.min() / p.h, (xs.max() + 1) / p.w, (ys.max() + 1) / p.h)})
    out.sort(key=lambda b: -b["mass"])
    tot = sum(b["mass"] for b in out) or 1
    return [b for b in out[:k] if b["mass"] / tot > 0.02], tot


def _path(blobs):
    """Attention path: start at the entry (the mass nearest the upper-left, reading order), walk to
    the nearest unvisited mass, end at the landing (the heaviest). Returns the node list."""
    if len(blobs) < 2:
        return list(blobs)
    land = blobs[0]
    start = min(blobs, key=lambda b: b["c"][0] + b["c"][1])
    rest = [b for b in blobs if b is not start and b is not land]
    seq, cur = [start], start
    while rest:
        nx = min(rest, key=lambda b: math.dist(b["c"], cur["c"]))
        seq.append(nx); rest.remove(nx); cur = nx
    if land is not start:
        seq.append(land)
    return seq


def _turns(seq):
    t = []
    for a, b, c in zip(seq, seq[1:], seq[2:]):
        v1 = (b["c"][0] - a["c"][0], b["c"][1] - a["c"][1])
        v2 = (c["c"][0] - b["c"][0], c["c"][1] - b["c"][1])
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        if n1 > 1e-6 and n2 > 1e-6:
            t.append(math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2))))))
    return t


def _zones(p):
    """Salience share of the 3 x 3 zones of the drawn area (the mask's box)."""
    ys, xs = np.nonzero(p.mask)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    s = p.sal[y0:y1, x0:x1]
    H, W = s.shape
    tot = s.sum() + 1e-9
    return np.array([[s[r * H // 3:(r + 1) * H // 3, c * W // 3:(c + 1) * W // 3].sum() / tot for c in range(3)] for r in range(3)])


def r_qi(p):
    """qi = 0.25 entry + 0.25 landing + 0.2 turn + 0.15 (100 - 34 stagnant) + 0.15 (100 - 25 dead_ends)
    entry   : the upper-left quadrant (menu bar, title, first word) pulls more than its two side
              quadrants: 100 * clip(0.5 + (tl - (tr + bl) / 2) / 0.06), 0 if tl < 8 %
    landing : one primary mass, heavier than the next by the zucai ratio 7:5: 100 * clip((m1/m2 - 1) / 0.4)
    turn    : the path entry -> ... -> landing bends at least once by >= 25 deg (the spirit screen:
              qi meanders, it does not shoot): 100, else 50
    stagnant: a corner zone holding > 1.5/9 of the weight that the path never visits (dense, no exit)
    dead end: a path node where the walk reverses by > 135 deg"""
    blobs, tot = _blobs(p)
    s = p.sal
    H, W = s.shape
    total = s.sum() + 1e-9
    q = lambda a, b: s[a * H // 2:(a + 1) * H // 2, b * W // 2:(b + 1) * W // 2].sum() / total
    tl, tr, bl = q(0, 0), q(0, 1), q(1, 0)
    entry = 100 * min(1.0, max(0.0, 0.5 + (tl - (tr + bl) / 2) / 0.06)) if tl > 0.08 else 0.0
    if len(blobs) >= 2:
        landing = 100 * min(1.0, max(0.0, (blobs[0]["mass"] / blobs[1]["mass"] - 1) / (K.ZUCAI / K.CAI - 1)))
    else:
        landing = 100.0 if blobs else 0.0
    seq = _path(blobs)
    turns = _turns(seq)
    turn = 100.0 if (len(seq) < 3 or any(t >= 25 for t in turns)) else 50.0
    z = _zones(p)
    stagnant = 0
    for r, c in ((0, 0), (0, 2), (2, 0), (2, 2)):
        if z[r, c] > 1.5 / 9:
            on = any(r * 1 / 3 <= b["c"][1] < (r + 1) / 3 and c / 3 <= b["c"][0] < (c + 1) / 3 for b in seq)
            stagnant += 0 if on else 1
    dead = sum(1 for t in turns if t > 135)
    v = 0.25 * entry + 0.25 * landing + 0.2 * turn + 0.15 * max(0, 100 - 34 * stagnant) + 0.15 * max(0, 100 - 25 * dead)
    return v, {"entry": round(entry), "landing": round(landing), "turns": [round(t) for t in turns],
               "stagnant": stagnant, "dead_ends": dead}


def _corners(p):
    """Sharp corners: Harris-style response of the luminance structure tensor at the scale of
    1/4 fen; a rounded corner (radius >= 1 fen) spreads its response under the threshold."""
    L = ndimage.gaussian_filter(p.lab[..., 0], 0.7)
    gy, gx = np.gradient(L)
    sig = max(1.0, p.u / 4)
    a, b, c = (ndimage.gaussian_filter(v, sig) for v in (gx * gx, gx * gy, gy * gy))
    tr, det = a + c, a * c - b * b
    lam = tr / 2 - np.sqrt(np.maximum(0, (tr / 2) ** 2 - det))     # the smaller eigenvalue
    lam[~ndimage.binary_erosion(p.mask, iterations=3)] = 0
    pk = (lam == ndimage.maximum_filter(lam, size=max(3, round(p.u)))) & (lam > 2e-4)
    ys, xs = np.nonzero(pk)
    return list(zip(xs / p.w, ys / p.h, lam[pk]))


def r_sha(p):
    """sha = 100 - 15 arrows - 10 cuts - min(30, 300 * aimed)
    arrows : straight edges longer than 1/3 of the frame that run into its border (they lead the
             eye off the screen; an edge lying on the border itself is the frame, not an arrow)
    cuts   : straight edges longer than 1/2 of the frame that do not touch the border, with weight
             on both sides within 3 fen (a dividing line through content)
    aimed  : sharp corners, each weighted by its closeness to the primary mass (1 - d / 0.5),
             as a share of the drawn area in fen^2"""
    arrows = _arrows(p)
    cuts = _cuts(p)
    blobs, _ = _blobs(p)
    land = blobs[0]["c"] if blobs else (0.5, 0.45)
    cs = _corners(p)
    area_fen = p.mask.sum() / (p.u ** 2) + 1e-9
    aimed = sum(max(0.0, 1 - math.dist((x, y), land) / 0.5) for x, y, _ in cs) / area_fen
    v = max(0.0, 100 - 15 * arrows - 10 * cuts - min(30.0, 300 * aimed))
    return v, {"arrows": arrows, "cuts": cuts, "sharp_corners": len(cs), "aimed": round(aimed, 4)}


def _cuts(p):
    L = np.where(p.mask, p.lab[..., 0], np.nan)
    count = 0
    for axis in (0, 1):
        d = np.nan_to_num(np.abs(np.diff(L, axis=axis))) > 0.05
        lines = d if axis == 0 else d.T
        sal = p.sal if axis == 0 else p.sal.T
        n = lines.shape[1]
        band = max(2, round(3 * p.u))
        seen = -10
        for i in range(band, lines.shape[0] - band):
            row = lines[i]
            if row[:2].any() or row[-2:].any():
                continue
            # longest run
            r = np.diff(np.concatenate(([0], row.astype(int), [0])))
            starts, ends = np.flatnonzero(r == 1), np.flatnonzero(r == -1)
            if len(starts) == 0:
                continue
            k = np.argmax(ends - starts)
            if ends[k] - starts[k] >= n / 2 and i - seen > band:
                seg = slice(starts[k], ends[k])
                above, below = sal[i - band:i, seg].mean(), sal[i + 1:i + 1 + band, seg].mean()
                if min(above, below) > 0.5 * sal[p.mask.T if axis else p.mask].mean():
                    count += 1
                    seen = i
    return count


def r_forms(p):
    """forms = 0.4 mountain + 0.3 support + 0.3 water
    mountain: anchors have a base: the lower half carries 45-65 % of the weight (100 inside,
              -4 per point outside)
    support : no heavy over light without support: for each of the top masses, a mass above
              another (overlapping columns) may not outweigh it by > 2x unless it rests on the frame
              bottom or on a container; share of masses that pass
    water   : flowing content is continuous: consecutive path steps are <= 1/3 of the diagonal
              (no jump the eye cannot follow); share of steps that pass"""
    s = p.sal
    ys = np.arange(p.h)[:, None]
    tot = s.sum() + 1e-9
    low = s[ys[:, 0] >= p.h / 2].sum() / tot
    mountain = max(0.0, 100 - 400 * max(0.0, 0.45 - low, low - 0.65))
    blobs, _ = _blobs(p)
    bad = 0
    for a in blobs:
        for b in blobs:
            if a is b:
                continue
            overlap = min(a["box"][2], b["box"][2]) - max(a["box"][0], b["box"][0])
            if overlap > 0 and a["box"][3] <= b["box"][1] + 0.02 and a["mass"] > 2 * b["mass"]:
                bad += 1
                break
    support = 100 * (1 - bad / len(blobs)) if blobs else 100.0
    seq = _path(blobs)
    steps = [math.dist(a["c"], b["c"]) for a, b in zip(seq, seq[1:])]
    water = 100 * (sum(d <= math.sqrt(2) / 3 for d in steps) / len(steps)) if steps else 100.0
    v = 0.4 * mountain + 0.3 * support + 0.3 * water
    return v, {"lower_half": round(low, 2), "heavy_over_light": bad, "jumps": sum(d > math.sqrt(2) / 3 for d in steps)}


def r_zones(p):
    """zones = 100 - 8 empty - 12 overloaded - 150 mean|w - neighbours| - 20 (centre not content)
    Nine zones (3 x 3, the luoshu / bagua grid) of the drawn area. w = salience share per zone.
    empty: w < 0.2/9 (corner zones of an icon card are exempt: the card's own rounding);
    overloaded: w > 3/9; neighbour deviation: each zone against the mean of its 4-neighbours;
    centre: the middle zone holds content (w >= 1/9) or it costs 20."""
    z = _zones(p)
    empty = over = 0
    dev = []
    for r in range(3):
        for c in range(3):
            w = z[r, c]
            corner = r != 1 and c != 1
            if w < 0.2 / 9 and not (corner and p.kind == "icon"):
                empty += 1
            if w > 3 / 9:
                over += 1
            nb = [z[r + dr, c + dc] for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)) if 0 <= r + dr < 3 and 0 <= c + dc < 3]
            dev.append(abs(w - sum(nb) / len(nb)))
    centre = 0 if z[1, 1] >= 1 / 9 else 20
    v = max(0.0, 100 - 8 * empty - 12 * over - 150 * float(np.mean(dev)) - centre)
    return v, {"zones": [[round(float(x), 2) for x in row] for row in z], "empty": empty, "overloaded": over}


def _arrows(p):
    L = np.where(p.mask, p.lab[..., 0], np.nan)
    count = 0
    H, W = L.shape
    for axis in (0, 1):
        d = np.abs(np.diff(L, axis=axis))
        d = np.nan_to_num(d) > 0.05
        lines = d if axis == 0 else d.T            # rows of the edge map along the edge direction
        n = lines.shape[1]
        seen = -10
        for i in range(lines.shape[0]):
            row = lines[i]
            if not row[0] and not row[-1]:
                continue
            # run length touching an end
            run_l = np.argmin(row) if not row.all() else n
            run_r = np.argmin(row[::-1]) if not row.all() else n
            if max(run_l, run_r) >= n / 3 and i - seen > 3:
                if 2 < i < lines.shape[0] - 3:     # an edge along the frame border itself is not an arrow
                    count += 1
                    seen = i
    return count


def r_density(p):
    s = p.sal
    tot = s.sum() + 1e-9
    ys, xs = np.mgrid[0:p.h, 0:p.w]
    cx, cy = (s * xs).sum() / tot / p.w, (s * ys).sum() / tot / p.h
    tx, ty = (0.5, 0.47) if p.kind in ("icon", "mark") else (0.5, 0.45)
    d = math.hypot(cx - tx, cy - ty)
    gravity = 100 * max(0.0, 1 - d / 0.25)
    # three planes by colour distance to the ground
    if p.ground is None:
        return 0.0, {}
    de = p.de[p.mask]
    shares = np.array([(de < 0.04).mean(), ((de >= 0.04) & (de < 0.18)).mean(), (de >= 0.18).mean()])
    planes = 100 * max(0.0, 1 - np.abs(shares - np.array(K.PLANES)).sum())
    # rhythm: the salience profile along the main axis; gaps between bands should repeat
    prof = s.sum(0) if p.w >= p.h else s.sum(1)
    on = prof > 0.25 * prof.max()
    edges = np.flatnonzero(np.diff(on.astype(int)))
    gaps = np.diff(edges)[1::2] if len(edges) > 2 else np.array([])
    if len(gaps) >= 2:
        cv = gaps.std() / (gaps.mean() + 1e-9)
        rhythm = 100 * max(0.0, 1 - cv)
    else:
        rhythm = 75.0
    # breathing: ground share between 1/3 and 3/5 (full without bloat)
    gs = shares[0]
    breath = 100.0 if 1 / 3 <= gs <= 0.6 else max(0.0, 100 - 250 * (1 / 3 - gs if gs < 1 / 3 else gs - 0.6))
    v = (gravity + planes + rhythm + breath) / 4
    return v, {"gravity": (round(cx, 2), round(cy, 2)), "planes": [round(x, 2) for x in shares],
               "rhythm": round(rhythm), "breathing": round(breath)}


def r_proportion(p):
    """Masses measured in fen: the content box against the frame, and the big regions' sides."""
    content = p.mask & (p.rid != p.ground) if p.ground is not None else p.mask
    if p.kind == "icon":
        # The icon canvas is 24 fen; the art box is the zucai, 21 fen, with 1.5 fen of air around.
        # fill  : the art's long side against 21 fen (1 - |L - 21| / 4)
        # ratio : the art box in a cai-fen ratio (1:1, 3:2, 7:5, 2:1), 6 % tolerance
        # module: sides of every plane (region >= 1 % of the art) on the fen grid: named 1, whole 0.6
        fen = p.w / 24
        ys, xs = np.nonzero(p.mask)
        aw, ah = (xs.max() + 1 - xs.min()) / fen, (ys.max() + 1 - ys.min()) / fen
        fill = max(0.0, 1 - abs(max(aw, ah) - K.ZUCAI) / 4)
        ratio = K.ratio_fit(aw, ah, 0.06)
        fits = []
        for r in p.regions:
            if r["area"] < 0.01:
                continue
            x0, y0, x1, y1 = r["bbox"]
            for L in ((x1 - x0) / fen, (y1 - y0) / fen):
                near = min(abs(L - n) for n in K.NAMED)
                fits.append(1.0 if near <= 0.15 else 0.6 if abs(L - round(L)) <= 0.15 else 0.0)
        module = sum(fits) / len(fits) if fits else 0.5
        v = 100 * (0.35 * fill + 0.25 * ratio + 0.4 * module)
        return v, {"art_fen": (round(aw, 1), round(ah, 1)), "module": round(module, 2), "planes": len(fits) // 2}
    if p.kind == "mark":
        # lines of ink (row profile) and the gaps between them: their heights should stand in
        # ratios of named fen lengths (15 : 2 : 4 for the stack), within 4 %
        ink = (p.de > 0.15) & p.mask
        rows = ink.any(1)
        runs, cur, start = [], rows[0], 0
        for y in range(1, len(rows)):
            if rows[y] != cur:
                runs.append((cur, y - start)); start, cur = y, rows[y]
        runs.append((cur, len(rows) - start))
        inner = [n for on, n in runs[1:-1]] if not runs[0][0] else [n for on, n in runs]
        inner = [n for n in inner if n >= 2]
        names = [n for n in K.NAMED if n <= K.ZUCAI]
        ratios = sorted({a / b for a in names for b in names if a != b})
        hits = []
        for a, b in zip(inner, inner[1:]):
            r = a / b
            hits.append(any(abs(r - q) / q <= 0.04 for q in ratios))
        v = 100 * sum(hits) / len(hits) if hits else 50.0
        return v, {"bands_px": inner, "ratio_hits": f"{sum(hits)}/{len(hits)}"}
    # screens, wallpapers: the big regions' sides on the module, openings on the ruler
    scale = p.w / p._frame_w if hasattr(p, "_frame_w") else 1.0
    fits, doors = [], []
    for i, r in enumerate(p.regions):
        if i == p.ground or r["area"] < 0.004:
            continue
        x0, y0, x1, y1 = r["bbox"]
        for L in (x1 - x0, y1 - y0):
            fits.append(K.module_fit(L / scale, tol=1.0))
        if min(x1 - x0, y1 - y0) / scale >= 72:
            doors.append(all(K.band((L) / scale)[0] in K.GOOD_BANDS for L in (x1 - x0, y1 - y0)))
    mod = 100 * (sum(fits) / len(fits)) if fits else 50.0
    door = 100 * (sum(doors) / len(doors)) if doors else 75.0
    return 0.7 * mod + 0.3 * door, {"module": round(mod), "door_bands": round(door), "n": len(fits)}


def score_pixels(path, kind, size=None):
    if size is None:
        size = 256 if kind == "icon" else 960 if kind == "mark" else None
    arr = load(path, size, "#FFFFFF" if kind == "mark" else None)
    if kind == "mark" and not path.endswith(".svg"):
        arr[..., 3] = 1.0
    p = Px(arr, kind)
    if not path.endswith(".svg") and kind not in ("icon", "mark"):
        p._frame_w = p.w
    out = {}
    for name, fn in (("qi", r_qi), ("sha", r_sha), ("forms", r_forms), ("zones", r_zones),
                     ("palette", r_palette), ("light", r_light), ("proportion", r_proportion), ("density", r_density)):
        v, why = fn(p)
        out[name] = {"score": round(float(v), 1), "why": why}
    return out


# ---------------------------------------------------------------- layout tree
def tree_scores(tree):
    """tree = {"frame": [w, h], "nodes": [{"id", "rect": [x, y, w, h], "fill": "#hex",
    "parent": id|None, "role": "opening"|"text"|"line"|"control"|..., "plane": 1|2|3, "radius": r,
    "group": id}]}. Returns exact proportion and rhythm scores (0-100) and the palette adjacency
    of each node with its parent."""
    W, H = tree["frame"]
    nodes = tree["nodes"]
    by = {n["id"]: n for n in nodes}
    lens = []
    for n in nodes:
        x, y, w, h = n["rect"]
        if n.get("role") == "text":
            continue
        lens += [w, h]
        if n.get("radius") is not None:
            lens.append(n["radius"])
        par = by.get(n.get("parent"))
        if par:
            px_, py_, pw_, ph_ = par["rect"]
            for inset in (x - px_, y - py_):
                if inset > 0:
                    lens.append(inset)
    mod = 100 * sum(K.module_fit(v) for v in lens) / max(1, len(lens))
    doors = [n for n in nodes if n.get("role") == "opening" and min(n["rect"][2:]) >= 72]
    door = 100 * sum(all(K.band(v)[0] in K.GOOD_BANDS for v in n["rect"][2:]) for n in doors) / max(1, len(doors)) if doors else 75.0
    # rhythm: gaps between siblings stacked in one group fall on at most two values
    groups = {}
    for n in nodes:
        if n.get("group"):
            groups.setdefault(n["group"], []).append(n)
    rs = []
    for g in groups.values():
        g = sorted(g, key=lambda n: (n["rect"][1], n["rect"][0]))
        gaps = []
        for a, b in zip(g, g[1:]):
            vert = b["rect"][1] >= a["rect"][1] + a["rect"][3] - 1
            gaps.append(round(b["rect"][1] - (a["rect"][1] + a["rect"][3])) if vert else round(b["rect"][0] - (a["rect"][0] + a["rect"][2])))
        if gaps:
            distinct = len(set(gaps))
            rs.append(1.0 if distinct <= 2 and all(K.module_fit(v) > 0 for v in gaps) else 0.5 if distinct <= 3 else 0.2)
    rhythm = 100 * sum(rs) / len(rs) if rs else 75.0
    # palette: node against its parent
    pal = []
    for n in nodes:
        par = by.get(n.get("parent"))
        if not (par and n.get("fill") and par.get("fill")):
            continue
        rel = relation(element(n["fill"]), element(par["fill"]))
        share = n["rect"][2] * n["rect"][3] / (W * H)
        pal.append(1.0 if rel in ("same", "sheng") or share <= K.ACCENT_SHARE else 0.0)
    palette = 100 * sum(pal) / len(pal) if pal else 75.0
    # arrows: lines that touch the frame edge
    arrows = sum(1 for n in nodes if n.get("role") == "line" and
                 (n["rect"][0] <= 0 or n["rect"][0] + n["rect"][2] >= W or n["rect"][1] <= 0 or n["rect"][1] + n["rect"][3] >= H))
    return {"proportion": round(0.7 * mod + 0.3 * door, 1), "rhythm": round(rhythm, 1),
            "palette_adjacency": round(palette, 1), "edge_lines": arrows,
            "lengths": len(lens), "module": round(mod, 1), "door_bands": round(door, 1)}


def total(scores):
    return round(sum(scores[r]["score"] for r in RULES) / len(RULES), 1)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--kind", default="icon")
    ap.add_argument("--tree")
    ap.add_argument("--size", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    s = score_pixels(a.file, a.kind, a.size)
    if a.tree:
        t = tree_scores(json.load(open(a.tree)))
        s["proportion"]["score"] = round(0.5 * s["proportion"]["score"] + 0.5 * t["proportion"], 1)
        s["proportion"]["why"]["tree"] = t
        s["density"]["score"] = round(0.75 * s["density"]["score"] + 0.25 * t["rhythm"], 1)
        s["palette"]["score"] = round(0.5 * s["palette"]["score"] + 0.5 * t["palette_adjacency"], 1)
        s["sha"]["score"] = round(max(0.0, s["sha"]["score"] - 5 * t["edge_lines"]), 1)
    s["total"] = total(s)
    if a.json:
        print(json.dumps(s, default=str))
    else:
        for r in RULES:
            print(f"{r:11s} {s[r]['score']:5.1f}  {s[r]['why']}")
        print(f"{'total':11s} {s['total']:5.1f}")


if __name__ == "__main__":
    main(sys.argv[1:])
