# SPDX-License-Identifier: GPL-2.0-or-later
"""Scene: one drawing API that writes an SVG mock AND the layout tree the scorer reads.

The same code draws the current screen (measured from the shell source and goldens) and the
proposed one (named lengths), so a score compares like with like. Stdlib + Pillow (tools only).

  s = Scene(1280, 800, "light", TOK["new"], "installer-begin")
  card = s.panel(352, 150, 576, 504, 24, fill="glass", shadow="e3", role="opening")
  s.text(card, 40, 40, 400, 40, "Welcome", 27, 700)
  s.save(OUTDIR)  ->  NAME-MODE.svg / .png / -tree.json
"""
import base64
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FONT = "Inter, 'Noto Sans CJK JP', sans-serif"

# ---- token sets: the 13-token contract (current = shipped wol-light/wol-dark, new = brand) ----
TOK = {
    "cur": {
        "light": dict(surface="#f3f1f8", sidebar="#e9e7f1", card="#ffffff", line="#e1dfe8", text="#181521",
                      dim="#686575", accent="#7c5cff", accent_ink="#7c5cff", accent_text="#181521",
                      glass="#f5f4fb", control="#e9e9f3", success="#1c9a6e", warning="#d9541e", danger="#cf3a68",
                      shadow="0,0,0", tint="#6a4df4"),
        "dark": dict(surface="#1b1924", sidebar="#272531", card="#2a2834", line="#3a3748", text="#f6f5fb",
                     dim="#aaa7b6", accent="#8b6cff", accent_ink="#8b6cff", accent_text="#181521",
                     glass="#23212d", control="#393647", success="#5be3b0", warning="#ff8a55", danger="#f2678f", on_danger="#181521",
                     shadow="0,0,0", tint="#8b6cff"),
    },
    "new": {  # tokens/tokens-east.json
        "light": dict(surface="#F1F1FA", sidebar="#EBEBF3", card="#FFFFFF", line="#D9D9E1", text="#151520",
                      dim="#565563", accent="#7452F5", accent_ink="#6D48EB", accent_text="#FFFFFF",
                      glass="#F1F1FA", control="#EBEBF3", success="#00863C", warning="#C06400", danger="#BB3F27",
                      shadow="21,21,32", tint="#7452F5"),
        "dark": dict(surface="#15151D", sidebar="#20202A", card="#292932", line="#3F3F49", text="#F8F8FC",
                     dim="#B4B4BB", accent="#7452F5", accent_ink="#9181FF", accent_text="#FFFFFF",
                     glass="#292932", control="#383741", success="#6BC681", warning="#F2944C", danger="#EE7E66", on_danger="#151520",
                     shadow="2,2,6", tint="#9181FF"),
    },
}

# elevation presets: list of (dx, dy, blur, alpha); colour comes from the token set
SHADOWS = {
    "cur-glass": [(0, 6, 18, 0.24), (0, 1, 4, 0.16)],
    "cur-card": [(0, 1, 2, 0.08)],
    "cur-sheet": [(0, 6, 18, 0.24), (0, 1, 4, 0.16)],
    "e1": [(1, 2, 4, 0.14)],
    "e2": [(2, 4, 12, 0.18)],
    "e3": [(3, 6, 24, 0.24)],
}


_FONTS = {}


def wrap(text, width, size=13, weight=400):
    """Greedy word wrap with Inter metrics (PIL), so mock paragraphs break like GTK labels."""
    from PIL import ImageFont
    key = (size, weight >= 600)
    if key not in _FONTS:
        f = "/usr/share/fonts/opentype/inter/Inter-%s.otf" % ("SemiBold" if weight >= 600 else "Regular")
        _FONTS[key] = ImageFont.truetype(f, size)
    ft = _FONTS[key]
    lines, cur = [], ""
    for w_ in text.split():
        t = (cur + " " + w_).strip()
        if ft.getlength(t) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def _data_uri(svg_text):
    return "data:image/svg+xml;base64," + base64.b64encode(svg_text.encode()).decode()


class Scene:
    def __init__(self, W, H, mode, tok, name, backdrop="wonder", scale=1):
        self.W, self.H, self.mode, self.t, self.name = W, H, mode, tok[mode], name
        self.dark = mode == "dark"
        self.nodes, self.out, self.defs = [], [], []
        self._id = 0
        self._f = 0
        self.scale = scale
        if backdrop:
            self.backdrop(backdrop)

    # ------------------------------------------------------------ tree
    def _node(self, role, rect, parent=None, **k):
        self._id += 1
        n = {"id": self._id, "role": role, "rect": [round(v, 2) for v in rect], "parent": parent}
        n.update({a: b for a, b in k.items() if b is not None})
        self.nodes.append(n)
        return self._id

    def rect_of(self, nid):
        return next(n["rect"] for n in self.nodes if n["id"] == nid)

    def _abs(self, parent, x, y):
        if parent is None:
            return x, y
        px, py, _, _ = self.rect_of(parent)
        return px + x, py + y

    # ------------------------------------------------------------ paint
    def backdrop(self, kind):
        """The shell's lock backdrop (ui/lock.rs: wallpaper blurred) at 1280 x 800, from its own golden (backdrop.py)."""
        out = os.path.join(HERE, "cache", f"backdrop-real-{self.mode}.png")
        if not os.path.exists(out):
            import backdrop
            backdrop.make(self.mode)
        self.image(0, 0, self.W, self.H, png_path=out, tree=False, fit="none")

    def _shadow(self, x, y, w, h, r, preset):
        if not preset:
            return
        rgb = self.t["shadow"]
        for dx, dy, bl, a in SHADOWS[preset]:
            self._f += 1
            fid = f"sh{self._f}"
            pad = bl * 2
            self.defs.append(f'<filter id="{fid}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{bl / 2}"/></filter>')
            a2 = min(0.9, a * (1.8 if self.dark else 1))
            mid = fid + "m"
            self.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x - 200}" y="{y - 200}" width="{w + 400}" height="{h + 400}">'
                             f'<rect x="{x - 200}" y="{y - 200}" width="{w + 400}" height="{h + 400}" fill="white"/>'
                             f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="black"/></mask>')
            self.out.append(f'<g mask="url(#{mid})"><rect x="{x + dx}" y="{y + dy}" width="{w}" height="{h}" rx="{r}" fill="rgb({rgb})" fill-opacity="{a2:.3f}" filter="url(#{fid})"/></g>')

    def color(self, c):
        return self.t.get(c, c) if isinstance(c, str) and not c.startswith("#") and not c.startswith("rgb") else c

    def panel(self, x, y, w, h, r=0, fill="card", parent=None, shadow=None, stroke=None, opacity=1.0, role="box",
              group=None, rim=False, tree=True, stroke_w=1, clip=None, stroke_op=1.0):
        """A filled rounded rect. x, y are relative to `parent` (absolute when None). Returns the node id."""
        ax, ay = self._abs(parent, x, y)
        col = self.color(fill)
        self._shadow(ax, ay, w, h, r, shadow)
        st = ""
        if stroke:
            st = f' stroke="{self.color(stroke)}" stroke-width="{stroke_w}" stroke-opacity="{stroke_op}"'
            ax2, ay2, w2, h2, r2 = ax + .5, ay + .5, w - 1, h - 1, max(0, r - .5)
        else:
            ax2, ay2, w2, h2, r2 = ax, ay, w, h, r
        self.out.append(f'<rect x="{ax2}" y="{ay2}" width="{w2}" height="{h2}" rx="{r2}" fill="{col}" fill-opacity="{opacity}"{st}/>')
        if rim:  # gloss on the lit rim only: the top and left edges (light from the upper left)
            self._f += 1
            cid = f"rim{self._f}"
            self.defs.append(f'<clipPath id="{cid}"><rect x="{ax}" y="{ay}" width="{w}" height="{h}" rx="{r}"/></clipPath>')
            a = 0.20 if self.dark else 0.85
            self.out.append(f'<g clip-path="url(#{cid})" fill="white" fill-opacity="{a}"><rect x="{ax}" y="{ay}" width="{w}" height="1"/>'
                            f'<rect x="{ax}" y="{ay}" width="1" height="{h}"/></g>')
        if not tree:
            return None
        return self._node(role, (ax, ay, w, h), parent, fill=col if col.startswith("#") else None, radius=r or None, group=group)

    def line(self, x, y, w, h=1, color="line", parent=None, role="line", tree=True):
        ax, ay = self._abs(parent, x, y)
        self.out.append(f'<rect x="{ax}" y="{ay}" width="{w}" height="{h}" fill="{self.color(color)}"/>')
        if tree:
            self._node(role, (ax, ay, w, h), parent)

    def text(self, parent, x, y, w, h, s, size=13, weight=400, color="text", anchor="start", group=None,
             ls=0, opacity=1, tree=True, lines=None, lh=None, italic=False):
        """Text in a line box (w x h at x, y relative to parent). `lines`: list of strings for a paragraph."""
        ax, ay = self._abs(parent, x, y)
        ls_ = lines if lines is not None else [s]
        lh = lh or h / max(1, len(ls_))
        tx = ax if anchor == "start" else ax + w / 2 if anchor == "middle" else ax + w
        for i, ln in enumerate(ls_):
            by = ay + i * lh + lh / 2 + size * 0.35
            ln = ln.replace("&", "&amp;").replace("<", "&lt;")
            self.out.append(f'<text x="{tx}" y="{by:.1f}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
                            f'fill="{self.color(color)}" fill-opacity="{opacity}" text-anchor="{anchor}" letter-spacing="{ls}"'
                            f'{" font-style=\"italic\"" if italic else ""}>{ln}</text>')
        if tree:
            self._node("text", (ax, ay, w, h), parent, group=group)

    def image(self, x, y, w, h, svg_path=None, png_path=None, parent=None, color=None, role="box", tree=True, fill=None, shadow=None, radius=None, fit="xMidYMid meet"):
        ax, ay = self._abs(parent, x, y)
        if svg_path:
            txt = open(svg_path).read()
            if color:
                txt = txt.replace("currentColor", self.color(color))
                import re
                txt = re.sub(r'style="color:[^"]*"', "", txt, count=1)
            uri = _data_uri(txt)
        else:
            uri = "data:image/png;base64," + base64.b64encode(open(png_path, "rb").read()).decode()
        self._shadow(ax, ay, w, h, radius or 0, shadow)
        self.out.append(f'<image x="{ax}" y="{ay}" width="{w}" height="{h}" href="{uri}" preserveAspectRatio="{fit}"/>')
        if tree:
            return self._node(role, (ax, ay, w, h), parent, fill=fill, radius=radius)

    def raw(self, svg):
        self.out.append(svg)

    # ------------------------------------------------------------ kit widgets
    def button(self, parent, x, y, w, h, label, kind="default", r=None, size=13, weight=500, shadow=None, group=None, disabled=False):
        r = h / 2 if r is None else r
        fills = {"default": "control", "primary": "accent", "plain": None, "destructive": "danger"}
        fill = fills[kind]
        nid = None
        if fill:
            nid = self.panel(x, y, w, h, r, fill=fill, parent=parent, shadow=shadow, role="control", group=group,
                             opacity=0.45 if disabled else 1)
        else:
            ax, ay = self._abs(parent, x, y)
            nid = self._node("control", (ax, ay, w, h), parent, group=group, radius=r)
        col = {"default": "text", "primary": "accent_text", "plain": "accent_ink", "destructive": self.t.get("on_danger", "accent_text")}[kind]
        self.text(nid, 0, 0, w, h, label, size, weight, col, "middle", tree=False)
        return nid

    def field(self, parent, x, y, w, h, value="", placeholder="", r=8, size=13, trailing=None, group=None, focus=False, rim=True):
        nid = self.panel(x, y, w, h, r, fill="control", parent=parent, stroke="accent" if focus else "line", role="control", group=group)
        txt, col = (value, "text") if value else (placeholder, "dim")
        self.text(nid, 12, 0, w - 24 - (24 if trailing else 0), h, txt, size, 400, col, tree=False)
        if trailing:
            self.sym(nid, w - 12 - 16, (h - 16) / 2, 16, trailing, "text", tree=False)
        return nid

    def switch(self, parent, x, y, w, h, on=False, thumb=None, pad=2, group=None):
        nid = self.panel(x, y, w, h, h / 2, fill="accent" if on else "#8a8a94", parent=parent, role="control", group=group,
                         opacity=1 if on else (0.38 if not self.dark else 0.5))
        th = thumb or h - 2 * pad
        tx = x + w - pad - th if on else x + pad
        ax, ay = self._abs(parent, tx, y + (h - th) / 2)
        self.out.append(f'<circle cx="{ax + th / 2}" cy="{ay + th / 2 + .5}" r="{th / 2}" fill="white"/>')
        return nid

    def sym(self, parent, x, y, size, name, color="text", tree=False):
        p = os.path.join(ROOT, "icons", "symbolic", name + "-symbolic.svg")
        return self.image(x, y, size, size, svg_path=p, parent=parent, color=color, tree=tree, role="box")

    def icon(self, parent, x, y, size, name, tree=True, shadow=None):
        for d in ("east/types/A2-bold", "east/fullset"):
            for n in (f"wolos-{name}.svg", f"{name}.svg"):
                p = os.path.join(ROOT, d, n)
                if os.path.exists(p):
                    return self.image(x, y, size, size, svg_path=p, parent=parent, tree=tree, role="box", shadow=shadow)
        raise FileNotFoundError(name)

    # ------------------------------------------------------------ output
    def svg(self):
        W, H = self.W, self.H
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
                f'<defs>{"".join(self.defs)}</defs>' + "".join(self.out) + "</svg>")

    def tree(self):
        return {"frame": [self.W, self.H], "nodes": self.nodes}

    def save(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        base = os.path.join(outdir, f"{self.name}-{self.mode}")
        open(base + ".svg", "w").write(self.svg())
        json.dump(self.tree(), open(base + "-tree.json", "w"))
        subprocess.run(["rsvg-convert", base + ".svg", "-o", base + ".png"], check=True)
        return base
