# SPDX-License-Identifier: GPL-2.0-or-later
"""The lock backdrop at 1280 x 800, taken from the shell's own golden (lock-{light,dark}.png) with the clock and the
avatar painted out by normalised convolution. Written to cache/backdrop-real-{mode}.png.
  python3 -I backdrop.py [GOLDEN_DIR]"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = "/home/ubuntu/wolos/wt/webapp-int/crates/shell/tests/golden"


def make(mode, golden=GOLDEN):
    im = Image.open(f"{golden}/lock-{mode}.png").convert("RGB")
    a = np.asarray(im).astype(float)
    big = np.asarray(im.filter(ImageFilter.GaussianBlur(25))).astype(float)
    d = np.abs(a - big).sum(-1)
    mask = ndimage.binary_dilation(d > (40 if mode == "light" else 25), iterations=14)
    keep = np.zeros_like(mask)
    keep[30:215, 280:640] = True      # clock and date
    keep[255:600, 280:640] = True     # avatar, name, field
    mask &= keep
    w = (~mask).astype(float)
    out, fill, done = a.copy(), np.zeros_like(a), np.zeros(a.shape[:2], bool)
    for s in (15, 30, 60):
        num = np.stack([ndimage.gaussian_filter(a[..., i] * w, s) for i in range(3)], -1)
        den = ndimage.gaussian_filter(w, s)
        use = (den > 0.05) & ~done
        fill[use] = (num / np.maximum(den, 1e-6)[..., None])[use]
        done |= use
    out[mask] = fill[mask]
    os.makedirs(os.path.join(HERE, "cache"), exist_ok=True)
    p = os.path.join(HERE, "cache", f"backdrop-real-{mode}.png")
    Image.fromarray(out.clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(4)).resize((1280, 800), Image.BICUBIC).save(p)
    return p


if __name__ == "__main__":
    g = sys.argv[1] if len(sys.argv) > 1 else GOLDEN
    for m in ("light", "dark"):
        print(make(m, g))
