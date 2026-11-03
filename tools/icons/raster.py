# SPDX-License-Identifier: GPL-2.0-or-later
"""Rendering and pixel reading for the icon generator: rsvg-convert (the renderer GTK loads SVG
with) writes PNGs; a small stdlib PNG reader gives the checks their pixels."""
import shutil
import struct
import subprocess
import sys
import zlib


def rsvg():
    exe = shutil.which("rsvg-convert")
    if not exe:
        sys.exit("icons: rsvg-convert not found (librsvg); it renders the app PNGs")
    return exe


def render_png(svg_path, size):
    """PNG bytes of an SVG file at size x size."""
    r = subprocess.run([rsvg(), "-w", str(size), "-h", str(size), svg_path], capture_output=True)
    if r.returncode != 0 or not r.stdout.startswith(b"\x89PNG"):
        raise RuntimeError(f"{svg_path} @{size}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def render_text(svg_text, size, tmpdir):
    """PNG bytes of SVG markup (written to tmpdir first)."""
    import os
    p = os.path.join(tmpdir, "r.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write(svg_text)
    return render_png(p, size)


def decode_png(data):
    """(w, h, rows) of an 8-bit RGBA PNG; rows are lists of (r, g, b, a) floats 0..1, NOT premultiplied."""
    w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    if depth != 8 or ctype != 6:
        raise ValueError("decode_png: only 8-bit RGBA")
    raw, pos = b"", 8
    while pos < len(data):
        ln, = struct.unpack(">I", data[pos:pos + 4])
        if data[pos + 4:pos + 8] == b"IDAT":
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
        rows.append([(line[x] / 255, line[x + 1] / 255, line[x + 2] / 255, line[x + 3] / 255) for x in range(0, stride, 4)])
        prev = line
    return w, h, rows


def rel_lum(rgb):
    def ch(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_lum(a, b):
    a, b = max(a, b), min(a, b)
    return (a + 0.05) / (b + 0.05)
