"""Contact sheet of run.sh renders: rows = apps, columns = light, dark. usage: sheet.py <dir> <out.png>"""
import os
import sys

from PIL import Image, ImageDraw

d, out = sys.argv[1], sys.argv[2]
rows = [("Files (nautilus)", "nautilus"), ("Text Editor", "editor"), ("Image Viewer (loupe)", "loupe"),
        ("Qt, Fusion + qt6ct palette (Linux host)", "qt"), ("Qt, Kvantum WolOS theme (FreeBSD VM)", "kv")]


def trim(im):
    """Crop the white broadway page around the window."""
    bg = Image.new("RGB", im.size, (255, 255, 255))
    from PIL import ImageChops
    box = ImageChops.difference(im, bg).getbbox()
    return im.crop(box) if box else im


cells = []
for title, n in rows:
    r = []
    for v in ("light", "dark"):
        p = os.path.join(d, f"{n}-{v}.png")
        if os.path.exists(p):
            r.append((f"{title} - {v}", trim(Image.open(p).convert("RGB"))))
    if r:
        cells.append(r)
cw = [max(r[i][1].width for r in cells if len(r) > i) for i in range(2)]
H = sum(max(c[1].height for c in r) + 34 for r in cells) + 16
img = Image.new("RGB", (sum(cw) + 48, H), (200, 200, 205))
dr = ImageDraw.Draw(img)
y = 8
for r in cells:
    x = 16
    for i, (label, im) in enumerate(r):
        dr.text((x, y), label, fill=(0, 0, 0))
        img.paste(im, (x, y + 18))
        x += cw[i] + 16
    y += max(c[1].height for c in r) + 34
img.save(out)
print(out, img.size)
