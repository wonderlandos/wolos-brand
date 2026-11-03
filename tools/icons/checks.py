# SPDX-License-Identifier: GPL-2.0-or-later
"""The rules every full-colour icon is held to before anything is written (LANGUAGE.md 5):
the SVG parses, sits on the 64 grid and has no filter, image or text; the glyph primary holds
3:1 on its plane; the silhouette (body or rim) holds 1.8:1 on the light and the dark ground;
no colour is another platform's system colour."""
import re
import xml.etree.ElementTree as ET

from palette import EDGE_MIN, GLYPH_MIN, GROUND_DARK, GROUND_LIGHT, contrast, rim

# Colours the set left behind (INVENTORY.md): never again in a shipped icon.
BANNED = {"#FF3B30", "#FF9500", "#FFCC00", "#34C759", "#007AFF", "#FF453A", "#FF9F0A", "#FFD60A",
          "#30D158", "#0A84FF", "#FF5F57", "#FEBC2E", "#28C840", "#FF2D55", "#5AC8FA", "#8E8E93"}


def check(icon):
    """-> (errors, metrics) for one families.Icon."""
    err, m = [], {}
    try:
        root = ET.fromstring(icon.svg)
    except ET.ParseError as e:
        return [f"{icon.name}: does not parse: {e}"], m
    if root.get("viewBox") != "0 0 64 64":
        err.append(f"{icon.name}: not on the 64 grid")
    tags = {el.tag.split("}")[-1] for el in root.iter()}
    for bad in ("filter", "image", "text", "foreignObject"):
        if bad in tags:
            err.append(f"{icon.name}: <{bad}>")
    for c in set(re.findall(r"#[0-9A-Fa-f]{6}\b", icon.svg)):
        if c.upper() in BANNED:
            err.append(f"{icon.name}: banned colour {c}")
    for label, fg, plane in icon.glyphs:
        cr = contrast(fg, plane)
        m[label] = cr
        if cr < GLYPH_MIN:
            err.append(f"{icon.name}: {label} {fg} on {plane} is {cr:.2f}:1 (< {GLYPH_MIN})")
    for k, body in enumerate(icon.bodies):
        for gname, ground in (("light", GROUND_LIGHT), ("dark", GROUND_DARK)):
            best = max(contrast(body, ground), contrast(rim(body), ground))
            m[f"edge{k}/{gname}"] = best
            if k == 0 and best < EDGE_MIN:
                err.append(f"{icon.name}: silhouette {body} on {gname} is {best:.2f}:1 (< {EDGE_MIN})")
    return err, m


def check_all(icons):
    errs, rows = [], []
    for ic in icons:
        e, m = check(ic)
        errs += e
        rows.append((ic.name, m))
    return errs, rows
