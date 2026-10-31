# SPDX-License-Identifier: GPL-2.0-or-later
"""WolOS places, devices and mimetype icons (Big Sur style: blue folder with an embossed glyph,
paper documents with a dog-ear and a coloured glyph). 1024 grid, same shadow as the app icons.
usage: python3 -I design/tools/places.py        writes design/icons/{places,devices,mimetypes}
Validates every SVG (XML parse + rsvg-convert render) and exits 1 on failure."""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")

# No SVG filters: GTK's own icon renderer turns them into grey boxes. The drop shadow is the
# shape repeated below, offset and translucent (see `shadowed`).
SHADOW = ""


def shadowed(shape):
    """Shape plus two black offset copies underneath (a filter-free soft drop shadow)."""
    return (f'<g class="s" transform="translate(0 16)" opacity=".08">{shape}</g>'
            f'<g class="s" transform="translate(0 8)" opacity=".12">{shape}</g>{shape}')


def svg(defs, body):
    body = re.sub(r'<g filter="url\(#sh\)">(.*?)</g>', lambda m: shadowed(m.group(1)), body, flags=re.S)
    defs += '<style>.s * { fill: #000 !important; fill-opacity: 1 !important; stroke: none !important; }</style>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
<defs>{SHADOW}{defs}</defs>
{body}
</svg>
'''


# ---- glyphs (drawn in a 300x300 box centred on 0,0) ----
G = {
    "documents": '<path d="M-90-130h120l70 70v190h-190z"/><path d="M30-130v70h70" fill-opacity=".5"/>',
    "download": '<path d="M-30-130h60v130h70l-100 110-100-110h70z"/><rect x="-120" y="105" width="240" height="40" rx="20"/>',
    "music": '<path d="M-60-110l150-35v200a45 40 0 1 1-30-38v-110l-90 20v150a45 40 0 1 1-30-38z"/>',
    "pictures": '<path d="M-140 110l90-130 60 80 40-50 90 100z"/><circle cx="70" cy="-80" r="38"/>',
    "videos": '<rect x="-140" y="-100" width="280" height="200" rx="30"/><path d="M-30-50v100l85-50z" fill="#000" fill-opacity=".35"/>',
    "desktop": '<rect x="-150" y="-120" width="300" height="190" rx="22"/><rect x="-25" y="70" width="50" height="45"/><rect x="-80" y="110" width="160" height="26" rx="13"/>',
    "home": '<path d="M0-140l160 140h-45v130h-75v-90h-80v90h-75v-130h-45z"/>',
    "templates": '<rect x="-120" y="-130" width="240" height="260" rx="24" fill-opacity=".5"/><rect x="-80" y="-90" width="160" height="40" rx="10"/><rect x="-80" y="-20" width="160" height="110" rx="10"/>',
    "public": '<circle cy="-70" r="60"/><path d="M-130 130q0-120 130-120t130 120z"/>',
    "folder": "",
}


def folder(glyph):
    emboss = ""
    if glyph:
        emboss = (f'<g transform="translate(512 600) scale(1.05)" fill="#fff" fill-opacity=".55">{glyph}</g>'
                  f'<g transform="translate(512 594) scale(1.05)" fill="#0b4fa8" fill-opacity=".45">{glyph}</g>')
    defs = '''<linearGradient id="back" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3D9BF0"/><stop offset="1" stop-color="#2373D6"/></linearGradient>
<linearGradient id="front" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7CCBFF"/><stop offset="1" stop-color="#3A97F2"/></linearGradient>'''
    body = f'''<g filter="url(#sh)">
<path d="M120 250q0-50 50-50h220q24 0 40 18l40 46h384q50 0 50 50v420q0 50-50 50H170q-50 0-50-50z" fill="url(#back)"/>
<rect x="148" y="300" width="728" height="120" rx="20" fill="#fff" fill-opacity=".9"/>
<path d="M100 400q0-46 46-46h732q46 0 46 46v374q0 50-50 50H150q-50 0-50-50z" fill="url(#front)"/>
<path d="M100 400q0-46 46-46h732q46 0 46 46v8q0-40-46-40H146q-46 0-46 40z" fill="#fff" fill-opacity=".45"/>
</g>{emboss}'''
    return svg(defs, body)


def page(color, glyph, label=""):
    """White sheet with a dog-ear; coloured glyph and optional label band."""
    text = ""
    if label:
        text = (f'<rect x="262" y="700" width="500" height="110" rx="24" fill="{color}"/>'
                f'<text x="512" y="782" font-family="Inter, sans-serif" font-weight="700" font-size="80" '
                f'text-anchor="middle" fill="#fff">{label}</text>')
    body = f'''<g filter="url(#sh)">
<path d="M232 120h400l160 160v600q0 40-40 40H272q-40 0-40-40V160q0-40 40-40z" fill="#fff"/>
<path d="M232 120h400l160 160v600q0 40-40 40H272q-40 0-40-40V160q0-40 40-40z" fill="none" stroke="#000" stroke-opacity=".10" stroke-width="6"/>
<path d="M632 120v120q0 40 40 40h120z" fill="#E3E6EC"/>
</g>
<g transform="translate(512 {470 if label else 540})" fill="{color}">{glyph}</g>{text}'''
    return svg("", body)


LINES = '<g>' + "".join(f'<rect x="-130" y="{y}" width="{w}" height="26" rx="13"/>' for y, w in
                        [(-120, 260), (-60, 220), (0, 260), (60, 180)]) + '</g>'
MIMES = {
    "text-x-generic": page("#8A90A0", LINES),
    "image-x-generic": page("#34C759", G["pictures"]),
    "audio-x-generic": page("#FF375F", G["music"]),
    "video-x-generic": page("#5856D6", G["videos"]),
    "application-pdf": page("#E5322D", LINES, "PDF"),
    "package-x-generic": page("#A2845E", '<rect x="-120" y="-130" width="240" height="260" rx="30"/><rect x="-20" y="-130" width="40" height="260" fill="#fff" fill-opacity=".6"/>', "ZIP"),
    "x-office-document": page("#2B7CD3", LINES, "DOC"),
    "x-office-spreadsheet": page("#21A366", '<g>' + "".join(f'<rect x="{x}" y="{y}" width="70" height="50" rx="8"/>' for x in (-120, -35, 50) for y in (-120, -50, 20, 90)) + '</g>', "SHEET"),
    "x-office-presentation": page("#F0742E", '<rect x="-140" y="-110" width="280" height="180" rx="16"/><rect x="-10" y="70" width="20" height="60"/>', "SLIDES"),
    "application-x-executable": page("#3A3A42", '<rect x="-140" y="-110" width="280" height="220" rx="24"/><path d="M-90-40l60 50-60 50" fill="none" stroke="#3CE37A" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>'),
    "application-x-generic": page("#B8BCC6", '<circle r="110" fill-opacity=".7"/>'),
}

PLACES = {
    "folder": folder(""),
    "folder-documents": folder(G["documents"]),
    "folder-download": folder(G["download"]),
    "folder-music": folder(G["music"]),
    "folder-pictures": folder(G["pictures"]),
    "folder-videos": folder(G["videos"]),
    "folder-templates": folder(G["templates"]),
    "folder-publicshare": folder(G["public"]),
    "user-desktop": folder(G["desktop"]),
    "user-home": folder(G["home"]),
}

TRASH = '''<g filter="url(#sh)"><path d="M262 300h500l-40 520q-4 60-64 60H366q-60 0-64-60z" fill="#F4F5F8"/>
<path d="M262 300h500l-40 520q-4 60-64 60H366q-60 0-64-60z" fill="none" stroke="#000" stroke-opacity=".12" stroke-width="6"/>
<rect x="232" y="230" width="560" height="90" rx="30" fill="#D5D8DF"/></g>
<path d="M400 400l20 380M512 400v380M624 400l-20 380" stroke="#B5BAC4" stroke-width="18" stroke-linecap="round"/>'''
PAPERS = '<g transform="rotate(-8 512 260)"><rect x="340" y="120" width="220" height="260" rx="14" fill="#fff" stroke="#c7cbd3" stroke-width="6"/></g><g transform="rotate(10 512 260)"><rect x="470" y="110" width="220" height="260" rx="14" fill="#EAF4FF" stroke="#c7cbd3" stroke-width="6"/></g>'
PLACES["user-trash"] = svg("", TRASH)
PLACES["user-trash-full"] = svg("", PAPERS + TRASH)
PLACES["network-workgroup"] = svg('<radialGradient id="g" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#7CCBFF"/><stop offset="1" stop-color="#1E6FD9"/></radialGradient>', '''<g filter="url(#sh)"><circle cx="512" cy="512" r="380" fill="url(#g)"/></g>
<g fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="22"><ellipse cx="512" cy="512" rx="160" ry="380"/><path d="M132 512h760M180 330h664M180 694h664M512 132v760"/></g>''')

DEVICES = {
    "drive-harddisk": svg('<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9EBEF"/><stop offset="1" stop-color="#B9BEC7"/></linearGradient>',
                          '''<g filter="url(#sh)"><rect x="132" y="312" width="760" height="400" rx="60" fill="url(#g)"/></g>
<rect x="132" y="560" width="760" height="8" fill="#000" fill-opacity=".08"/><circle cx="790" cy="640" r="20" fill="#30D158"/>
<rect x="212" y="625" width="300" height="30" rx="15" fill="#000" fill-opacity=".15"/>'''),
    "drive-removable-media": svg('<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9B85FF"/><stop offset="1" stop-color="#5B3BE8"/></linearGradient>',
                                 '''<g filter="url(#sh)"><rect x="332" y="352" width="360" height="540" rx="60" fill="url(#g)"/>
<rect x="392" y="152" width="240" height="220" rx="20" fill="#D5D8DF"/></g>
<rect x="452" y="212" width="40" height="40" rx="6" fill="#8A90A0"/><rect x="532" y="212" width="40" height="40" rx="6" fill="#8A90A0"/>
<circle cx="512" cy="640" r="60" fill="#fff" fill-opacity=".35"/>'''),
}

# freedesktop names (and common aliases) -> generated file, per context dir.
SETS = {"places": PLACES, "devices": DEVICES, "mimetypes": MIMES}
ALIASES = {
    "places": {"folder-download": ["folder-downloads"], "network-workgroup": ["network-server", "folder-remote"],
               "user-home": ["folder-home"]},
    "devices": {"drive-harddisk": ["drive-harddisk-system", "drive-multidisk"], "drive-removable-media": ["drive-removable-media-usb", "media-removable"]},
    "mimetypes": {"text-x-generic": ["text-plain", "text-x-script"], "image-x-generic": ["image-png", "image-jpeg", "image-svg+xml"],
                  "audio-x-generic": ["audio-mpeg", "audio-flac"], "video-x-generic": ["video-mp4", "video-x-matroska"],
                  "package-x-generic": ["application-zip", "application-x-compressed-tar", "application-x-tar"],
                  "x-office-document": ["application-vnd.oasis.opendocument.text", "application-vnd.openxmlformats-officedocument.wordprocessingml.document"],
                  "x-office-spreadsheet": ["application-vnd.oasis.opendocument.spreadsheet", "application-vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
                  "x-office-presentation": ["application-vnd.oasis.opendocument.presentation", "application-vnd.openxmlformats-officedocument.presentationml.presentation"],
                  "application-x-executable": ["application-x-sharedlib", "application-x-shellscript"],
                  "application-x-generic": ["application-octet-stream", "unknown"]},
}


def main():
    bad = 0
    for ctx, icons in SETS.items():
        os.makedirs(os.path.join(D, ctx), exist_ok=True)
        for name, text in icons.items():
            p = os.path.join(D, ctx, f"{name}.svg")
            with open(p, "w") as f:
                f.write(text)
            try:
                ET.parse(p)
                r = subprocess.run(["rsvg-convert", "-w", "64", p], capture_output=True)
                if r.returncode != 0 or not r.stdout.startswith(b"\x89PNG"):
                    raise ValueError(r.stderr.decode())
            except Exception as e:  # noqa: BLE001 - report every broken icon
                print(f"invalid {p}: {e}")
                bad = 1
    with open(os.path.join(D, "places-aliases.tsv"), "w") as f:
        f.write("# context\tfile\taliases (generated by design/tools/places.py; install.sh symlinks these)\n")
        for ctx, m in ALIASES.items():
            for name, al in m.items():
                f.write(f"{ctx}\t{name}\t{' '.join(al)}\n")
    print(f"{sum(len(v) for v in SETS.values())} icons")
    sys.exit(bad)


main()
