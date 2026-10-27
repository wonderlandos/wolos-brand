# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Julia Klee
"""Generate the WolOS illustrations and their PNG exports.
usage: python3 -I design/tools/illus/build.py [OUT_DIR] [name...]
OUT_DIR defaults to design/illustrations. Needs rsvg-convert."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import Canvas, svg  # noqa: E402
import rabbit  # noqa: E402
import keyhole  # noqa: E402
import cheshire  # noqa: E402
import teacup  # noqa: E402
import watch  # noqa: E402
import scenes  # noqa: E402
import welcome  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.normpath(os.path.join(HERE, "..", "..", "illustrations"))


def char_rabbit():
    cv = Canvas("wr")
    return svg(512, 512, [cv], rabbit.rabbit(cv), "The White Rabbit")


def char_keyhole():
    cv = Canvas("kh")
    return svg(512, 512, [cv], keyhole.keyhole(cv), "The Keyhole")


def char_cheshire():
    cv = Canvas("cc")
    return svg(512, 512, [cv], cheshire.cheshire(cv), "The Cheshire Cat")


def char_teacup():
    cv = Canvas("tc")
    return svg(512, 512, [cv], teacup.teacup(cv), "The Teacup")


def char_watch():
    cv = Canvas("pw")
    return svg(512, 512, [cv], watch.pocket_watch(cv), "The Pocket Watch")


CAST = [
    ("white-rabbit.svg", "The White Rabbit", "guide",
     "Curious, quick, always late, a little mad.", "Setup Assistant · About · lock screen"),
    ("keyhole.svg", "The Keyhole", "the way in",
     ("The small door into Wonderland.", "Light comes through."), "About This Computer · sign-in"),
    ("cheshire.svg", "The Cheshire Cat", "thinking",
     ("Grins while the work happens.", "Tail first, he vanishes."), "loading and thinking states"),
    ("pocket-watch.svg", "The Pocket Watch", "updating",
     ("Opens up and shows you", "the gears turning."), "Software Update · progress"),
    ("teacup.svg", "The Teacup", "nothing here yet",
     ("Clean, empty, still warm.", "Pour something in."), "empty states"),
]


# name -> (builder, [(png suffix, width, height)])
ITEMS = {
    "white-rabbit": (char_rabbit, [("@1x", 256, 256), ("@2x", 512, 512)]),
    "keyhole": (char_keyhole, [("@1x", 256, 256), ("@2x", 512, 512)]),
    "cheshire": (char_cheshire, [("@1x", 160, 160), ("@2x", 320, 320)]),
    "teacup": (char_teacup, [("@1x", 160, 160), ("@2x", 320, 320)]),
    "pocket-watch": (char_watch, [("@1x", 160, 160), ("@2x", 320, 320)]),
    "setup-welcome": (welcome.welcome, [("@1x", 480, 320), ("@2x", 960, 640)]),
    "lock-peek": (scenes.peek, [("@1x", 320, 200), ("@2x", 640, 400)]),
    "character-sheet": (lambda: scenes.sheet(CAST), [("@1x", 1600, 1000), ("@2x", 3200, 2000)]),
}


def main():
    args = sys.argv[1:]
    out = DEFAULT
    if args and ("/" in args[0] or args[0].startswith(".")):
        out = args.pop(0)
    names = args or list(ITEMS)
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    for n in names:
        build, sizes = ITEMS[n]
        s = build()
        p = os.path.join(out, f"{n}.svg")
        with open(p, "w") as fh:
            fh.write(s)
        kb = len(s.encode()) / 1024
        print(f"{n}.svg {kb:.0f} KB" + ("  TOO BIG" if kb > 300 else ""))
        for suf, w, h in sizes:
            subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o",
                            os.path.join(out, "png", f"{n}{suf}.png"), p], check=True)


if __name__ == "__main__":
    main()
