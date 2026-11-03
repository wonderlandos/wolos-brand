# SPDX-License-Identifier: GPL-2.0-or-later
"""Full-colour icons of the WolOS theme: crafted objects on the soft card (apps) and pressed paper
(places, devices, mimetypes), .claude/brand/icons-premium/LANGUAGE-v2.md.

  python3 -I design/tools/icons.py            (the entry: symbolic set, then this)
  python3 -I design/tools/icons/build.py [--check] [--overlay DIR] [-v]

Writes design/icons/apps/wolos-<name>.svg, design/icons/{places,devices,mimetypes}/<name>.svg
(1024 canvas, the full variant), design/icons/apps/small/wolos-<name>.svg (the small variant: a larger
glyph, a lighter ramp on dark tiles, fewer details), design/icons/aliases.tsv, and the app PNGs at
48/128/512 under <overlay>/usr/share/icons/WolOS (tools/icons/overlay.py renders them with
rsvg-convert, the renderer GTK itself loads SVG with: 128 and 512 from the full drawing, 48 from the
small one). Nothing is written when a check fails
(checks.py). --check runs the checks and the renders and also fails when a written SVG differs from
what the generator draws now (CI lock: the drawings come from this tool, never by hand); it writes nothing."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import checks  # noqa: E402
import families  # noqa: E402
from palette import DESIGN  # noqa: E402
from raster import decode_png, render_png  # noqa: E402

ICONS = os.path.join(DESIGN, "icons")
KEEP = {"wolos-mark"}      # the brand mark: design/brand, not drawn here
# Installed copies of the brand drawings (design/brand is the source, drawn by tools/brand/):
# icon file -> brand file. A regeneration copies them again, so it never reverts the logo.
BRAND_COPIES = {
    "apps/wolos-mark.svg": "wolos-mark.svg",
    "symbolic/wolos-glyph-symbolic.svg": "wolos-glyph-symbolic.svg",
    "symbolic/wolos-logo-symbolic.svg": "wolos-glyph-symbolic.svg",
}

# Names other apps and desktop files ask for, installed as symlinks (install.sh, aliases.tsv).
ALIASES = {
    "files": "org.gnome.Nautilus system-file-manager thunar org.xfce.thunar pcmanfm nemo",
    "terminal": "utilities-terminal org.gnome.Terminal foot kitty Alacritty org.wezfurlong.wezterm xfce4-terminal com.mitchellh.ghostty",
    "browser": "helium firefox web-browser org.mozilla.firefox chromium librewolf epiphany",
    "settings": "preferences-system org.gnome.Settings gnome-control-center nwg-look org.wolos.settings",
    "software": "system-software-install org.gnome.Software octopkg org.wolos.store wolos-store",
    "music": "multimedia-audio-player org.gnome.Music audacious rhythmbox elisa io.bassi.Amberol",
    "photos": "multimedia-photo-viewer org.gnome.eog org.gnome.Loupe org.gnome.Shotwell ristretto org.wolos.gallery",
    "notes": "accessories-notes org.gnome.gitlab.cheywood.Iotas xpad org.gnome.Gnote",
    "calendar": "office-calendar org.gnome.Calendar",
    "mail": "internet-mail mail-client thunderbird org.mozilla.Thunderbird evolution org.gnome.Geary",
    "calculator": "accessories-calculator org.gnome.Calculator galculator qalculate-gtk",
    "games": "steam applications-games lutris",
    "text-editor": "accessories-text-editor org.gnome.TextEditor org.gnome.gedit mousepad code codium",
    "system-monitor": "utilities-system-monitor org.gnome.SystemMonitor htop btop",
    "trash": "user-trash user-trash-full",
    "launcher": "system-search fuzzel",
    "installer": "org.wolos.installer",
    "control-center": "org.wolos.control-center",
    "plugin-maker": "org.wolos.plugin-maker",
}


def file_name(icon):
    return f"wolos-{icon.name}.svg" if icon.ctx == "apps" else f"{icon.name}.svg"


def path_of(icon, root=ICONS):
    return os.path.join(root, icon.ctx, file_name(icon))


def render_rgba(name, size):
    """Premultiplied RGBA rows of a written full-colour icon (the symbolic contact sheet uses it)."""
    for ctx in ("apps", "places", "devices", "mimetypes"):
        for fn in (f"wolos-{name}.svg", f"{name}.svg"):
            p = os.path.join(ICONS, ctx, fn)
            if os.path.isfile(p):
                return [[(r * a, g * a, bl * a, a) for r, g, bl, a in row] for row in decode_png(render_png(p, size))[2]]
    raise FileNotFoundError(name)


def generate(deep=True):
    """The icons and the check report; exits 1 (nothing written) when a rule breaks."""
    icons = families.all_icons()
    errs, rows = [], []
    for ic in icons:
        e, m = checks.check(ic, deep)
        errs += e
        rows.append((ic.name, m))
    if errs:
        print("\n".join(errs), file=sys.stderr)
        sys.exit(f"icons: {len(errs)} check(s) failed, nothing written")
    return icons, rows


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode, **({} if mode == "wb" else {"newline": "\n", "encoding": "utf-8"})) as f:
        f.write(data)


def install_brand():
    """Copy the brand mark and glyph from design/brand into the icon set; -> the mark's path."""
    for dst, src in BRAND_COPIES.items():
        with open(os.path.join(DESIGN, "brand", src), encoding="utf-8", newline="") as f:
            text = f.read().replace("\r\n", "\n")
        write(os.path.join(ICONS, dst), text)
    return os.path.join(ICONS, "apps", "wolos-mark.svg")


def drift(icons):
    """Written SVGs that differ from what the generator draws now, and drawings that are missing."""
    out = []
    for ic in icons:
        p = path_of(ic)
        want = ic.svg(False)
        try:
            with open(p, encoding="utf-8", newline="") as f:
                have = f.read()
        except OSError:
            out.append(f"{os.path.relpath(p, DESIGN)}: missing")
            continue
        if have != want:
            out.append(f"{os.path.relpath(p, DESIGN)}: differs from the generator (run python3 design/tools/icons.py)")
    for ic in icons:
        if ic.ctx == "apps":
            p = os.path.join(ICONS, "apps", "small", file_name(ic))
            try:
                with open(p, encoding="utf-8", newline="") as f:
                    if f.read() != ic.svg(True):
                        out.append(f"{os.path.relpath(p, DESIGN)}: differs from the generator")
            except OSError:
                out.append(f"{os.path.relpath(p, DESIGN)}: missing")
    return out


def build(overlay=None, check_only=False, verbose=False):
    icons, rows = generate()
    if verbose:
        for name, m in rows:
            for v in ("full", "small"):
                mm = m.get(v, {})
                print(f"  {name:26s} {v:5s} " + "  ".join(f"{k} {x:5.2f}" for k, x in mm.items()))
    if check_only:
        stale = drift(icons)
        if stale:
            print("\n".join(stale), file=sys.stderr)
            sys.exit(f"icons: {len(stale)} drawing(s) out of date")
        print(f"icons: {len(icons)} full-colour icons pass the checks and match the generator (nothing written)")
        return icons
    names = {ctx: {file_name(i) for i in icons if i.ctx == ctx} for ctx in ("apps", "places", "devices", "mimetypes")}
    for ctx, keep in names.items():
        d = os.path.join(ICONS, ctx)
        os.makedirs(d, exist_ok=True)
        for fn in os.listdir(d):   # an icon the set no longer draws is a stale file
            if fn.endswith(".svg") and fn not in keep and fn[:-4] not in KEEP:
                os.remove(os.path.join(d, fn))
    small = os.path.join(ICONS, "apps", "small")
    shutil.rmtree(small, ignore_errors=True)
    for ic in icons:
        write(path_of(ic), ic.svg(False))
        if ic.ctx == "apps":     # the drawing the 48 px PNG is rendered from (overlay.py)
            write(os.path.join(small, file_name(ic)), ic.svg(True))
    mark = install_brand()
    write(os.path.join(ICONS, "aliases.tsv"),
          "# wolos-<icon>\tfreedesktop/app icon names (tab-separated). install.sh symlinks these. Generated by tools/icons.py.\n" +
          "".join(f"{k}\t{v}\n" for k, v in ALIASES.items()))
    pngs = 0
    if overlay:
        import overlay as ov       # the overlay PNGs are renders of the SVGs written above (tools/icons/overlay.py)
        theme = os.path.join(overlay, "usr", "share", "icons", "WolOS")
        if os.path.isdir(os.path.dirname(os.path.dirname(theme))):
            ov.THEME = theme
            pngs = ov.write(ov.sources())
    apps = sum(1 for i in icons if i.ctx == "apps")
    print(f"icons: {apps} app icons, {len(icons) - apps} places/devices/mimetypes, {pngs} PNGs (rsvg-convert)")
    return icons


def main(argv):
    overlay = os.path.normpath(os.path.join(DESIGN, "..", "desktop", "overlay"))
    check_only = "--check" in argv
    if "--overlay" in argv:
        overlay = argv[argv.index("--overlay") + 1]
    build(overlay, check_only=check_only, verbose="-v" in argv)


if __name__ == "__main__":
    main(sys.argv[1:])
