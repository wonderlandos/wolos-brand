# SPDX-License-Identifier: GPL-2.0-or-later
"""Strip SVG filters from icons (GTK, Qt, Firefox clip the filter region into a grey box).
usage: python3 -I design/tools/nofilter.py FILE.svg...   rewrites in place
Elements drawn through a plain blur (shadow or glow copies) are removed; other filters
(lighting, blend modes) are dropped and the element is drawn plainly. Then every <filter> goes."""
import re
import sys
from lxml import etree

SVG = "{http://www.w3.org/2000/svg}"


def ref(el):
    m = re.search(r"url\(#([^)]+)\)", el.get("filter", ""))
    if m:
        return m.group(1)
    m = re.search(r"filter\s*:\s*url\(#([^)]+)\)", el.get("style", ""))
    return m.group(1) if m else None


def is_shadow(f):
    """A blur whose result is not composited back over the shape: a shadow or glow copy."""
    prims = [e for e in f if isinstance(e.tag, str)]
    if not any(e.tag == SVG + "feGaussianBlur" for e in prims):
        return False
    return not any(e.tag in (SVG + "feMerge", SVG + "feComposite", SVG + "feBlend") for e in prims)


def strip(path):
    tree = etree.parse(path)
    filters = {f.get("id"): f for f in tree.iter(SVG + "filter")}
    blurry = {i for i, f in filters.items() if is_shadow(f)}
    for el in list(tree.iter()):
        if not isinstance(el.tag, str):
            continue
        r = ref(el)
        if r is None and "filter" not in el.attrib:
            continue
        if r in blurry and el.getparent() is not None:
            el.getparent().remove(el)
            continue
        el.attrib.pop("filter", None)
        if "style" in el.attrib:
            el.set("style", re.sub(r"filter\s*:[^;]*;?", "", el.get("style")))
    for f in list(tree.iter(SVG + "filter")):
        f.getparent().remove(f)
    tree.write(path, xml_declaration=True, encoding="utf-8")


for p in sys.argv[1:]:
    strip(p)
