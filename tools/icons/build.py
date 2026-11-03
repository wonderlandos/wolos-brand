# SPDX-License-Identifier: GPL-2.0-or-later
"""Full-colour icons of the WolOS theme: the Wonderland card (.claude/brand/icons-apps/LANGUAGE.md).

  python3 -I design/tools/icons.py            (the entry: symbolic set, then this)
  python3 -I design/tools/icons/build.py [--check] [--overlay DIR]

Writes design/icons/apps/wolos-<name>.svg, design/icons/{places,devices,mimetypes}/<name>.svg,
design/icons/aliases.tsv, and the app PNGs at 48/128/512 under <overlay>/usr/share/icons/WolOS
(rendered from the SVGs with rsvg-convert, the renderer GTK itself loads them with). Nothing is
written when a check fails (checks.py); --check runs the checks and the renders only."""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import checks  # noqa: E402
import families  # noqa: E402
from palette import DESIGN  # noqa: E402

ICONS = os.path.join(DESIGN, "icons")
PNG_SIZES = (48, 128, 512)
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
    "photos": "multimedia-photo-viewer org.gnome.eog org.gnome.Loupe org.gnome.Shotwell ristretto",
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


def rsvg():
    exe = shutil.which("rsvg-convert")
    if not exe:
        sys.exit("icons: rsvg-convert not found (librsvg); it renders the app PNGs")
    return exe


def render_png(svg_path, size):
    """PNG bytes of an SVG at size x size (rsvg-convert)."""
    r = subprocess.run([rsvg(), "-w", str(size), "-h", str(size), svg_path], capture_output=True)
    if r.returncode != 0 or not r.stdout.startswith(b"\x89PNG"):
        raise RuntimeError(f"{svg_path} @{size}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def decode_png(data):
    """RGBA rows (floats 0..1, premultiplied) of an 8-bit RGBA PNG (what rsvg-convert writes)."""
    w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    if depth != 8 or ctype != 6:
        raise ValueError("decode_png: only 8-bit RGBA")
    raw, pos = b"", 8
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        if tag == b"IDAT":
            raw += data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    raw = zlib.decompress(raw)
    stride, rows, prev = w * 4, [], bytearray(w * 4)
    for y in range(h):
        ft, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - 4] if i >= 4 else 0
            b = prev[i]
            c = prev[i - 4] if i >= 4 else 0
            if ft == 1:
                line[i] = (line[i] + a) & 255
            elif ft == 2:
                line[i] = (line[i] + b) & 255
            elif ft == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append([(line[x] / 255 * line[x + 3] / 255, line[x + 1] / 255 * line[x + 3] / 255,
                      line[x + 2] / 255 * line[x + 3] / 255, line[x + 3] / 255) for x in range(0, stride, 4)])
        prev = line
    return rows


def render_rgba(name, size):
    """Premultiplied RGBA rows of a written full-colour icon (the symbolic contact sheet uses it)."""
    for ctx in ("apps", "places", "devices", "mimetypes"):
        for fn in (f"wolos-{name}.svg", f"{name}.svg"):
            p = os.path.join(ICONS, ctx, fn)
            if os.path.isfile(p):
                return decode_png(render_png(p, size))
    raise FileNotFoundError(name)


def generate():
    """The icons and the check report; exits 1 (nothing written) when a rule breaks."""
    icons = families.all_icons()
    errs, rows = checks.check_all(icons)
    with tempfile.TemporaryDirectory() as t:
        for ic in icons:
            p = os.path.join(t, file_name(ic))
            with open(p, "w", encoding="utf-8") as f:
                f.write(ic.svg)
            try:
                render_png(p, 32)
            except RuntimeError as e:
                errs.append(f"{ic.name}: does not render: {e}")
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


def build(overlay=None, check_only=False, verbose=False):
    icons, rows = generate()
    if verbose:
        for name, m in rows:
            print(f"  {name:26s} " + "  ".join(f"{k} {v:5.2f}" for k, v in m.items()))
    if check_only:
        print(f"icons: {len(icons)} full-colour icons pass the checks (nothing written)")
        return icons
    names = {ctx: {file_name(i) for i in icons if i.ctx == ctx} for ctx in ("apps", "places", "devices", "mimetypes")}
    for ctx, keep in names.items():
        d = os.path.join(ICONS, ctx)
        os.makedirs(d, exist_ok=True)
        for fn in os.listdir(d):   # an icon the set no longer draws is a stale file
            if fn.endswith(".svg") and fn not in keep and fn[:-4] not in KEEP:
                os.remove(os.path.join(d, fn))
    for ic in icons:
        write(path_of(ic), ic.svg)
    mark = install_brand()
    write(os.path.join(ICONS, "aliases.tsv"),
          "# wolos-<icon>\tfreedesktop/app icon names (tab-separated). install.sh symlinks these. Generated by tools/icons.py.\n" +
          "".join(f"{k}\t{v}\n" for k, v in ALIASES.items()))
    pngs = 0
    if overlay:
        theme = os.path.join(overlay, "usr", "share", "icons", "WolOS")
        if os.path.isdir(os.path.dirname(os.path.dirname(theme))):
            for size in PNG_SIZES:
                for ic in icons:
                    if ic.ctx == "apps":
                        write(os.path.join(theme, f"{size}x{size}", "apps", f"wolos-{ic.name}.png"),
                              render_png(path_of(ic), size))
                        pngs += 1
                write(os.path.join(theme, f"{size}x{size}", "apps", "wolos-mark.png"), render_png(mark, size))
                pngs += 1
    apps = sum(1 for i in icons if i.ctx == "apps")
    print(f"icons: {apps} app cards, {len(icons) - apps} places/devices/mimetypes, {pngs} PNGs (rsvg-convert)")
    return icons


def main(argv):
    overlay = os.path.normpath(os.path.join(DESIGN, "..", "desktop", "overlay"))
    check_only = "--check" in argv
    if "--overlay" in argv:
        overlay = argv[argv.index("--overlay") + 1]
    build(overlay, check_only=check_only, verbose="-v" in argv)


if __name__ == "__main__":
    main(sys.argv[1:])
