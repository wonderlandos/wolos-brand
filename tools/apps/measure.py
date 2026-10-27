"""Traffic lights in app renders must match kit AppWindow: diameter, colour, centre spacing, close-button inset from the window's left and top edge.
usage: measure.py <kit.png> <app.png>...   exits 1 on mismatch (diameter/spacing > 1 px, colour > 12)."""
import sys

from PIL import Image


def lights(path, is_kit=False):
    """(diameter, rgb, centre x) for the three most saturated blobs in the top-left title area."""
    im = Image.open(path).convert("RGB").crop((0, 0, 220, 90))
    px = im.load()
    out = []
    for name, want in (("close", (1, 0, 0)), ("minimize", (1, 0.6, 0)), ("zoom", (0, 1, 0))):
        pts = []
        for y in range(im.height):
            for x in range(im.width):
                r, g, b = px[x, y]
                if max(r, g, b) - min(r, g, b) < 90:
                    continue
                hue_ok = {"close": r > 200 and g < 110 and b < 110,
                          "minimize": r > 200 and 110 <= g < 200 and b < 90,
                          "zoom": g > 150 and r < 120 and b < 140}[name]
                if hue_ok:
                    pts.append((x, y))
        if not pts:
            return None
        xs = [p[0] for p in pts]
        cx = (min(xs) + max(xs)) / 2
        cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
        out.append((max(xs) - min(xs) + 1, px[int(cx), int(cy)], cx))
        if name == "close":
            inset = (cx, cy)
            if not is_kit:  # broadway page: white, window drawn with a soft shadow and a 1 px border
                far = lambda c: max(255 - v for v in c) > 50  # noqa: E731
                left = next(x for x in range(im.width) if far(px[x, int(cy)]))
                top = next(y for y in range(im.height) if far(px[int(cx) + 60, y]))  # past the rounded corner
                inset = (cx - left - 1, cy - top - 1)
    return out, inset


kit, kit_inset = lights(sys.argv[1], is_kit=True)
bad = 0
for app in sys.argv[2:]:
    res = lights(app)
    if res is None:
        print(f"{app}: no traffic lights found")
        bad = 1
        continue
    got, inset = res
    print(f"{app.split('/')[-1]} close inset (left, top) {inset} (kit {kit_inset})")
    if any(abs(a - b) > 1 for a, b in zip(inset, kit_inset)):
        bad = 1
    for (kd, kc, kx), (ad, ac, ax), name in zip(kit, got, ("close", "minimize", "zoom")):
        dc = max(abs(a - b) for a, b in zip(kc, ac))
        print(f"{app.split('/')[-1]} {name}: diameter {ad} (kit {kd}), colour {ac} (kit {kc})")
        if abs(kd - ad) > 1 or dc > 12:
            bad = 1
    ks, gs = kit[1][2] - kit[0][2], got[1][2] - got[0][2]
    print(f"{app.split('/')[-1]} centre spacing {gs} (kit {ks})")
    if abs(ks - gs) > 1:
        bad = 1
sys.exit(bad)
