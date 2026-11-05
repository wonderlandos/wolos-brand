# SPDX-License-Identifier: GPL-2.0-or-later
"""WolOS design tokens: the one source of design/tokens/colors.{json,css,sh}.

  python3 -I design/tools/tokens.py           write them
  python3 -I design/tools/tokens.py --check   fail on drift, a lost contrast or a borrowed grey (tokens and tree)

The neutrals are WolOS's own: one ramp on the looking-glass ink hue (OKLCH hue 295, the violet of
the icon ink #221B36), chroma 0.007-0.026, so greys read as a faint lilac on light and plum on dark.
Lines and shadows are the ink (light) or a lilac paper (dark) at low alpha, never pure black/white.
CONTRAST holds the WCAG floors the ramp may not drop below (text, text-2 and border on bg, surface
and surface-2 per mode); they are the ratios the first token set had, so a retune can only gain.

Status hues (red, orange, yellow, green, blue) are the WolOS icon family, not another platform's
system colours: rose, tangerine, marigold, mint and lake from the icon palette below, each
nudged per theme so it holds on its ground. The `icon` block is the Wonderland card palette
(design/tools/icons/palette.py reads it): paper and ink glyph tones, the two grounds the
contrast checks run against, and body/tint/pop per category. radius.icon is the card itself:
32.7% on the top-left and bottom-right corners, 11.5% on the other two (17 and 6 on the 52 card).

type, space, radius, elevation, motion and density are data: design/tokens/{type,space,elevation,motion,density}.json
are hand-edited sources (DS-TOK); this tool validates them and writes design/tokens/scale.{css,sh} from them.
crates/shared/tests/tokens_design.rs holds shared::theme, the Kit stylesheet and kit/widgets.rs to the same JSON.
"""
import json
import os
import re
import sys

D = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ACCENT = "#7452F5"   # looking-glass violet, derived from #7C5CFF (4.9:1 under white)
ACCENT_D = "#7452F5"  # the fill is the same in both modes; text uses a derived ink

ICON = {
    "grid": 64,
    "card": {"x": 6, "y": 6, "size": 52, "radius-big": 17, "radius-small": 6},
    "paper": "#FFF6EA",
    "ink": "#221B36",
    "ground-light": "#F3F1F8",  # light.bg
    "ground-dark": "#191720",   # dark.bg
    "shadow": "rgba(0,0,0,0.22)",
    "categories": {
        "wolos": {"body": "#6A4DF4", "tint": "#C9BCFF", "pop": "#FFC94A"},
        "system": {"body": "#3B4775", "tint": "#AEB8E6", "pop": "#9B85FF"},
        "dev": {"body": "#221B36", "tint": "#6C5FA0", "pop": "#5BE3B0"},
        "files": {"body": "#0C8A80", "tint": "#8FDCCF", "pop": "#FFC94A"},
        "web": {"body": "#1D64B0", "tint": "#8CC3F5", "pop": "#FFC94A"},
        "talk": {"body": "#CF3A68", "tint": "#F7AFC3", "pop": "#FFC94A"},
        "media": {"body": "#E9622A", "tint": "#FFC7A6", "pop": "#6A4DF4"},
        "store": {"body": "#F2B53A", "tint": "#FFE7B0", "pop": "#CF3A68"},
    },
}

TOKENS = {
    "accent": {"light": ACCENT, "dark": ACCENT_D},
    # oklch(L C 295): bg .962/.009, surface-2 .932/.012, menubar .970/.007, text .205/.024, text-2 .515/.026
    "light": {"bg": "#F1F1FA", "surface": "#FFFFFF", "surface-2": "#EBEBF3", "sidebar": "rgba(235,235,243,0.92)", "menubar": "rgba(241,241,250,0.72)", "dock": "rgba(255,255,255,0.55)", "border": "rgba(21,21,32,0.12)", "text": "#151520", "text-2": "#565563", "shadow": "rgba(21,21,32,0.18)", "red": "#BB3F27", "orange": "#C06400", "yellow": "#C58A00", "green": "#00863C", "blue": "#007292", "accent": ACCENT, "accent-fg": "#FFFFFF", "selection": "rgba(116,82,245,0.22)"},
    # oklch(L C 295): bg .212/.017, surface .282/.020, surface-2 .342/.022, dock .270/.019,
    # text .972/.009, text-2 .735/.022; border is lilac paper #EDE8FF
    "dark": {"bg": "#15151D", "surface": "#292932", "surface-2": "#383741", "sidebar": "rgba(32,32,42,0.92)", "menubar": "rgba(21,21,29,0.62)", "dock": "rgba(41,41,50,0.5)", "border": "rgba(248,248,252,0.12)", "text": "#F8F8FC", "text-2": "#B4B4BB", "shadow": "rgba(2,2,6,0.45)", "red": "#EE7E66", "orange": "#F2944C", "yellow": "#FFD189", "green": "#6BC681", "blue": "#35BEEE", "accent": ACCENT_D, "accent-fg": "#FFFFFF", "selection": "rgba(145,129,255,0.3)"},
    "icon": ICON,
    "radius": {"sm": "8px", "md": "12px", "lg": "16px", "window": "12px", "dock": "24px", "icon": "32.7% 11.5%"},
    "blur": {"menubar": "20px", "dock": "24px", "popover": "30px", "hyprland_size": 8, "hyprland_passes": 3},
    "font": {"ui": "Inter", "ui-fallback": ["Inter", "Cantarell", "Noto Sans", "DejaVu Sans", "sans-serif"],
             "mono": "JetBrains Mono", "mono-fallback": ["JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "monospace"],
             "size": "13px", "size-menubar": "13px",
             "ports": ["x11-fonts/inter", "x11-fonts/jetbrains-mono", "x11-fonts/noto-basic"]},
    "wallpaper": {"light": "wonderland-day.svg", "dark": "wonderland-night.svg"},
}


def icon_flat():
    """(name, value) pairs of the icon palette, e.g. ('icon-files-body', '#0C8A80')."""
    out = [(f"icon-{k}", v) for k, v in ICON.items() if isinstance(v, str)]
    for cat, roles in ICON["categories"].items():
        out += [(f"icon-{cat}-{r}", v) for r, v in roles.items()]
    return out


def fonts(key):
    return ", ".join(f'"{f}"' if " " in f else f for f in TOKENS["font"][key])


def css():
    block = lambda p: [f"  --wol-{k}: {v};" for k, v in TOKENS[p].items()]
    out = ["/* WolOS design tokens. Generated by design/tools/tokens.py with colors.json/colors.sh; do not edit. */", ":root {"]
    out += block("light")
    out += [f"  --wol-{k}: {v};" for k, v in icon_flat()]
    out += [f"  --wol-radius-{k}: {v};" for k, v in TOKENS["radius"].items()]
    out += [f"  --wol-blur-{k}: {v};" for k, v in TOKENS["blur"].items() if str(v).endswith("px")]
    out += [f"  --wol-font-ui: {fonts('ui-fallback')};", f"  --wol-font-mono: {fonts('mono-fallback')};",
            f"  --wol-font-size: {TOKENS['font']['size']};", "}",
            "@media (prefers-color-scheme: dark) {", "  :root {"] + ["  " + l for l in block("dark")] + ["  }", "}",
            '[data-theme="dark"] {'] + block("dark") + ["}"]
    return "\n".join(out)


def sh():
    up = lambda k: k.upper().replace("-", "_")
    out = ["# WolOS design tokens (POSIX sh). Usage: . /usr/local/share/wolos/tokens/colors.sh", ': "${WOL_THEME:=light}"']
    for p in ("light", "dark"):
        out += [f"WOL_{p.upper()}_{up(k)}='{v}'" for k, v in TOKENS[p].items()]
    out += ['if [ "$WOL_THEME" = dark ]; then _p=DARK; else _p=LIGHT; fi']
    out += [f'eval "WOL_{up(k)}=\\${{WOL_${{_p}}_{up(k)}}}"' for k in TOKENS["light"]]
    out += [f"WOL_{up(k)}='{v}'" for k, v in icon_flat()]
    out += [f"WOL_RADIUS_{up(k)}='{v}'" for k, v in TOKENS["radius"].items()]
    out += [f"WOL_BLUR_{up(k)}='{v}'" for k, v in TOKENS["blur"].items()]
    out += [f"WOL_FONT_UI='{TOKENS['font']['ui']}'", f"WOL_FONT_MONO='{TOKENS['font']['mono']}'", "unset _p"]
    return "\n".join(out)


# ---- scale tokens (DS-TOK): JSON is the source, scale.{css,sh} are generated ----------------------
SCALE_FILES = ("type", "space", "elevation", "motion", "density")
DENSITIES = ("compact", "standard", "comfortable")


def scale_load():
    out = {}
    for n in SCALE_FILES:
        with open(os.path.join(D, "tokens", n + ".json"), encoding="utf-8") as f:
            out[n] = json.load(f)
    return out


def bezier(c):
    return "linear" if c is None else "cubic-bezier(" + ", ".join(f"{float(v):g}" for v in c) + ")"


def scale_vars(S):
    """[(name, value)] for scale.css; the shell variable is WOL_<NAME upper, - to _>."""
    v = []
    for k, r in S["type"]["roles"].items():
        v += [(f"type-{k}-size", f"{r['size']}px"), (f"type-{k}-line", f"{r['line']}px"),
              (f"type-{k}-weight", str(r["weight"])), (f"type-{k}-tracking", f"{r['tracking']}px")]
    v += [(f"space-{k[1:]}", f"{n}px") for k, n in S["space"]["space"].items()]
    v += [("fen", f"{S['space']['fen']}px"), ("inset", f"{S['space']['inset']}px")]
    v += [(f"radius-{k}", f"{n}px") for k, n in S["space"]["radius"].items()]
    v += [(f"icon-{k}", f"{n}px") for k, n in S["space"]["icon"].items()]
    for k, n in S["space"]["surface"].items():
        v += [(f"surface-{k}-{a}", f"{x}px") for a, x in zip("wh", n)] if isinstance(n, list) else [(f"surface-{k}", f"{n}px")]
    e = S["elevation"]
    ink = ",".join(str(c) for c in e["ink"])
    v += [(f"elev-{k}", f"{l['x']}px {l['y']}px {l['blur']}px rgba({ink},{l['alpha']})") for k, l in e["levels"].items()]
    v += [(f"duration-{k}", f"{n}ms") for k, n in S["motion"]["duration"].items()]
    v += [(f"curve-{k}", bezier(c)) for k, c in S["motion"]["curve"].items()]
    for m, per in S["density"]["metrics"].items():
        v += [(f"density-{m}-{d}", f"{per[d]}px") for d in DENSITIES]
    return v


def scale_css(S):
    out = ["/* WolOS design scale tokens. Generated by design/tools/tokens.py from tokens/{type,space,elevation,motion,density}.json; do not edit. */", ":root {"]
    out += [f"  --wol-{k}: {x};" for k, x in scale_vars(S)]
    return "\n".join(out + ["}"])


def scale_sh(S):
    out = ["# WolOS design scale tokens (POSIX sh). Generated by design/tools/tokens.py from tokens/*.json; do not edit."]
    out += [f"WOL_{k.upper().replace('-', '_')}='{x}'" for k, x in scale_vars(S)]
    return "\n".join(out)


def scale_problems(S):
    """Sentences for everything wrong with the scale sources (empty when fine)."""
    bad = []
    fen = S["space"]["fen"]
    for k, n in S["space"]["space"].items():
        if n % fen:
            bad.append(f"space.{k} {n} is not a whole number of fen ({fen})")
    for k in ("inset",):
        if S["space"][k] % fen:
            bad.append(f"space.{k} {S['space'][k]} is not a whole number of fen")
    for k, n in S["space"]["radius"].items():
        if k != "pill" and n % fen:
            bad.append(f"radius.{k} {n} is not a whole number of fen")
    for k, r in S["type"]["roles"].items():
        if r["line"] % fen:
            bad.append(f"type.{k} line {r['line']} is off the 4 px line")
        if r["size"] < 11:
            bad.append(f"type.{k} size {r['size']} is below 11 (RU-059)")
    m = S["density"]["metrics"]
    for name, per in m.items():
        if set(per) != set(DENSITIES):
            bad.append(f"density.{name} needs compact, standard, comfortable")
            continue
        if not per["compact"] <= per["standard"] <= per["comfortable"]:
            bad.append(f"density.{name} does not grow from compact to comfortable")
        for d in DENSITIES:
            if per[d] % fen:
                bad.append(f"density.{name}.{d} {per[d]} is not a whole number of fen")
    for d in DENSITIES:
        if m["target"][d] < 20:
            bad.append(f"density target {d} is under 20 px")
    if S["density"]["metrics"]["inset"]["standard"] != S["space"]["inset"]:
        bad.append("density inset standard is space.inset")
    for k, c in S["motion"]["curve"].items():
        if c is not None and (len(c) != 4 or not 0 <= c[0] <= 1 or not 0 <= c[2] <= 1):
            bad.append(f"motion.curve.{k} is not a cubic-bezier (x1, y1, x2, y2 with x in 0..1)")
    for var, c in S["motion"]["css"].items():
        if c not in S["motion"]["curve"]:
            bad.append(f"motion.css {var} names an unknown curve {c}")
    for k, n in S["motion"]["duration"].items():
        if n > 400 and k != "glass":
            bad.append(f"motion.duration.{k} {n} ms: nothing longer than 400")
    return bad


def write(rel, s):
    with open(os.path.join(D, rel), "w", newline="\n", encoding="utf-8") as f:
        f.write(s.strip() + "\n")


# WCAG floors: (foreground, ground) -> minimum ratio per mode. Values are the first token set's
# ratios rounded down; alpha foregrounds are composited over the ground first.
CONTRAST = {
    "light": {("text", "bg"): 15.63, ("text", "surface"): 17.01, ("text", "surface-2"): 14.43,
              ("text-2", "bg"): 4.66, ("text-2", "surface"): 5.07, ("text-2", "surface-2"): 4.30,
              ("border", "bg"): 1.25, ("border", "surface"): 1.25, ("border", "surface-2"): 1.25},
    "dark": {("text", "bg"): 15.63, ("text", "surface"): 12.80, ("text", "surface-2"): 10.42,
             ("text-2", "bg"): 6.61, ("text-2", "surface"): 5.42, ("text-2", "surface-2"): 4.41,
             ("border", "bg"): 1.35, ("border", "surface"): 1.37, ("border", "surface-2"): 1.37},
}

# Another platform's stock greys: the WolOS ramp must not reuse any of them, at any alpha.
FOREIGN_NEUTRALS = {
    (0x1D, 0x1D, 0x1F), (0xF5, 0xF5, 0xF7), (0x6E, 0x6E, 0x73), (0x1C, 0x1C, 0x1E), (0x2C, 0x2C, 0x2E),
    (0x3A, 0x3A, 0x3C), (0xA1, 0xA1, 0xA6), (0xEC, 0xEC, 0xEF), (0x86, 0x86, 0x8B), (0xD2, 0xD2, 0xD7),
    (0x48, 0x48, 0x4A), (0x63, 0x63, 0x66), (0x8E, 0x8E, 0x93), (0xAE, 0xAE, 0xB2), (0xC7, 0xC7, 0xCC),
    (0xD1, 0xD1, 0xD6), (0xE5, 0xE5, 0xEA), (0xF2, 0xF2, 0xF7), (0xF6, 0xF6, 0xF8), (0x28, 0x28, 0x2C),
}


# The tree sweep: every text file of the product repository (the one that has design/ as a
# submodule) is searched for the FOREIGN_NEUTRALS values as #rrggbb[aa] or rgb[a](r, g, b) with
# decimal or 0x channels. Not searched: build output, VCS data, licence texts, and the literal
# denylists that name the borrowed colours on purpose (a `BANNED` or `FOREIGN_NEUTRALS` literal).
SWEEP_SKIP_DIRS = {".git", "target", "node_modules", "__pycache__", "dist", "vendor", "third_party", "LICENSES"}
SWEEP_SKIP_FILE = re.compile(r"^(LICEN[CS]E|COPYING|NOTICE)([.-].*)?$|\.(lock|png|jpe?g|gif|ico|woff2?|ttf|otf|pdf|gz|xz|zst)$",
                             re.IGNORECASE)
SWEEP_HEX = re.compile(r"#([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?(?![0-9a-fA-F])")
SWEEP_TRIPLE = re.compile(r"rgba?\(\s*" + r"\s*,\s*".join([r"(0[xX][0-9a-fA-F]{1,2}|\d{1,3})"] * 3))
SWEEP_DENYLIST = re.compile(r"\b(BANNED|FOREIGN_NEUTRALS)\b[^=\n]*=")


def sweep_root():
    """The product repository root (design/'s parent when it is a submodule there), else design/."""
    up = os.path.dirname(D)
    return up if os.path.exists(os.path.join(up, ".gitmodules")) else D


def borrowed_in(line):
    cols = [tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) for m in SWEEP_HEX.finditer(line)]
    cols += [tuple(int(v, 0) for v in m.groups()) for m in SWEEP_TRIPLE.finditer(line)]
    return [c for c in cols if c in FOREIGN_NEUTRALS]


def sweep(root=None):
    """['path:line: #rrggbb', ...] for every borrowed stock grey outside the exemptions."""
    root = root or sweep_root()
    hits = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in SWEEP_SKIP_DIRS)
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if SWEEP_SKIP_FILE.search(fn) or os.path.islink(p) or os.path.getsize(p) > 4 << 20:
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    text = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            depth = 0  # > 0 inside a denylist literal (open brackets not yet closed)
            for n, line in enumerate(text.splitlines(), 1):
                if depth or SWEEP_DENYLIST.search(line):
                    depth = max(0, depth + sum(map(line.count, "[{(")) - sum(map(line.count, "]})")))
                    continue
                for c in borrowed_in(line):
                    hits.append(f"{os.path.relpath(p, root)}:{n}: #{c[0]:02X}{c[1]:02X}{c[2]:02X}")
    return hits


def sweep_selftest():
    """True when the sweep misses a planted grey or flags an exempt one (so --check cannot pass vacuously).
    The planted colours are formatted at run time, so this file holds none of them as text."""
    import tempfile
    a, b, c, d = (0x1D, 0x1D, 0x1F), (0x1C, 0x1C, 0x1E), (0xF5, 0xF5, 0xF7), (0x63, 0x63, 0x66)
    hx = lambda t: "#%02X%02X%02X" % t
    fixture = (f"a {{ color: {hx(a).lower()}cc; }}\nb = Color::rgb(0x{b[0]:02x}, 0x{b[1]:02x}, 0x{b[2]:02x})\n"
               f"c = rgba({c[0]}, {c[1]}, {c[2]}, .5)\nok = \"{TOKENS['light']['bg']}\"\nBANNED = {{\n  \"{hx(d)}\",\n}}\n"
               f"late = \"{hx(d)}\"\nx = \"{hx(a)}0\"\n")
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "target"))
        for rel, body in (("a.rs", fixture), ("LICENSE", hx(a) + "\n"), ("target/b.css", hx(a) + "\n")):
            with open(os.path.join(t, rel), "w", encoding="utf-8") as f:
                f.write(body)
        got = sweep(t)
    return got != [f"a.rs:1: {hx(a)}", f"a.rs:2: {hx(b)}", f"a.rs:3: {hx(c)}", f"a.rs:8: {hx(d)}"]

def rgba(s):
    """'#RRGGBB' or 'rgba(r,g,b,a)' -> ((r, g, b), a)."""
    if s.startswith("#"):
        return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5)), 1.0
    m = re.fullmatch(r"rgba?\((\d+),(\d+),(\d+)(?:,([\d.]+))?\)", s.replace(" ", ""))
    if not m:
        raise ValueError(f"colour {s!r}")
    return tuple(int(m.group(i)) for i in (1, 2, 3)), float(m.group(4) or 1)


def luminance(c):
    lin = lambda v: v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v / 255) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, ground):
    """WCAG 2 ratio of token value `fg` (alpha composited) on the opaque token value `ground`."""
    (g, _), (f, a) = rgba(ground), rgba(fg)
    f = tuple(round(x * a + y * (1 - a)) for x, y in zip(f, g))
    hi, lo = sorted((luminance(f), luminance(g)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def check():
    bad = []
    for rel, want in (("tokens/colors.json", json.dumps(TOKENS, indent=2)), ("tokens/colors.css", css()),
                      ("tokens/colors.sh", sh())):
        with open(os.path.join(D, rel), encoding="utf-8") as f:
            if f.read() != want.strip() + "\n":
                bad.append(f"{rel} is stale: run python3 -I design/tools/tokens.py")
    S = scale_load()
    for rel, want in (("tokens/scale.css", scale_css(S)), ("tokens/scale.sh", scale_sh(S))):
        with open(os.path.join(D, rel), encoding="utf-8") as f:
            if f.read() != want.strip() + "\n":
                bad.append(f"{rel} is stale: run python3 -I design/tools/tokens.py")
    bad += [f"tokens/*.json: {p}" for p in scale_problems(S)]
    for mode, floors in CONTRAST.items():
        for (fg, ground), floor in floors.items():
            r = contrast(TOKENS[mode][fg], TOKENS[mode][ground])
            ok = r >= floor
            print(f"  {mode:5} {fg:6} on {ground:9} {r:5.2f} (floor {floor:5.2f}){'' if ok else '  LOW'}")
            if not ok:
                bad.append(f"{mode}.{fg} on {mode}.{ground} is {r:.2f}, below {floor}")
    vals = [(f"{m}.{k}", v) for m in ("light", "dark") for k, v in TOKENS[m].items()]
    vals += [(k, v) for k, v in icon_flat()]
    for name, v in vals:
        if rgba(v)[0] in FOREIGN_NEUTRALS:
            bad.append(f"{name} {v} is a borrowed stock grey, not the WolOS ramp")
    if sweep_selftest():
        bad.append("the tree sweep no longer finds a planted stock grey (sweep_selftest)")
    hits = sweep()
    print(f"  tree   {len(hits)} borrowed stock grey(s) under {os.path.relpath(sweep_root(), os.getcwd())}")
    bad += [f"{h} is a borrowed stock grey: use the WolOS ramp (design/tokens)" for h in hits]
    for b in bad:
        print("tokens.py: " + b)
    print("tokens.py: " + ("FAIL" if bad else "tokens match, contrast holds, no borrowed greys in the tree"))
    return 1 if bad else 0


def main():
    if "--check" in sys.argv[1:]:
        sys.exit(check())
    os.makedirs(os.path.join(D, "tokens"), exist_ok=True)
    write("tokens/colors.json", json.dumps(TOKENS, indent=2))
    write("tokens/colors.css", css())
    write("tokens/colors.sh", sh())
    S = scale_load()
    if scale_problems(S):
        print("\n".join("tokens.py: tokens/*.json: " + p for p in scale_problems(S)))
        sys.exit(1)
    write("tokens/scale.css", scale_css(S))
    write("tokens/scale.sh", scale_sh(S))
    print("tokens.py: tokens/colors.{json,css,sh}, tokens/scale.{css,sh}")


if __name__ == "__main__":
    main()
