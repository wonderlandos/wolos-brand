# SPDX-License-Identifier: GPL-2.0-or-later
"""Guards for the icon generator lock: python3 -I design/tools/icons/test_generator.py

The full-colour folders (icons/apps, apps/small, places, devices, mimetypes) are written by
tools/icons/build.py and by nothing else. This once failed silently: the Type A2 set was installed
over the generator's output, build.py kept drawing the old icons, and a plain run would have reverted
the set. These tests fail when (1) a committed SVG is not the generator's bytes, (2) an SVG sits in
the folders that no generator draws, (3) the check itself stopped noticing either, (4) a brand
generator output depends on the installed icons (the loop that made the A2 set unreproducible).
Stdlib only; reads the committed tree and writes nothing there."""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import a2  # noqa: E402
import build  # noqa: E402
import families  # noqa: E402

SET = build.DESIGN
A2_FROM_TYPES = {"settings", "software", "files", "terminal", "browser"}


class Lock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.icons = families.all_icons()

    def test_every_committed_icon_is_the_generators(self):
        self.assertEqual(build.drift(self.icons), [])

    def test_a2_set_is_drawn_by_the_generator(self):
        names = {(i.ctx, i.name) for i in self.icons if isinstance(i, a2.A2Icon)}
        for must in [("apps", n) for n in A2_FROM_TYPES | {"calculator", "trash", "kit-ai", "games"}] + \
                [("places", "folder"), ("places", "user-trash"), ("devices", "drive-harddisk"), ("mimetypes", "text-x-generic")]:
            self.assertIn(must, names, f"{must} is not drawn by a brand generator")
        self.assertEqual(sum(1 for c, _ in names if c == "mimetypes"), 11)

    def test_folio_app_icon_stays_the_crafted_one(self):
        folio = next(i for i in self.icons if i.ctx == "apps" and i.name == "atlas")
        self.assertNotIsInstance(folio, a2.A2Icon)
        with open(build.path_of(folio), encoding="utf-8", newline="") as f:
            self.assertEqual(f.read(), folio.svg(False))

    def test_a_hand_installed_icon_is_caught(self):
        icon = next(i for i in self.icons if isinstance(i, a2.A2Icon) and i.name == "calculator")
        real = icon.svg

        def tampered(small=False, tile_only=False):
            return real(small, tile_only).replace("<title>", "<title>x", 1)
        icon.svg = tampered
        try:
            stale = build.drift(self.icons)
        finally:
            del icon.svg
        self.assertTrue(any("wolos-calculator.svg" in s and "differs" in s for s in stale), stale)

    def test_an_icon_no_generator_draws_is_caught(self):
        names = build.unowned(self.icons)
        self.assertEqual(names, [])
        fewer = [i for i in self.icons if i.name != "folder-videos"]
        self.assertTrue(any("folder-videos.svg" in s for s in build.unowned(fewer)))

    def test_a2_output_does_not_read_the_installed_icons(self):
        # a fresh interpreter, every open() recorded from the first import: drawing the A2 set may read
        # code and tokens, never design/icons/** (icons_brand once read the installed wolos-settings.svg
        # for the card, so the generator's input was its own output)
        code = (
            "import builtins, os, sys\n"
            "seen = []\n"
            "real = builtins.open\n"
            "def spy(f, *a, **k):\n"
            "    seen.append(os.path.abspath(f) if isinstance(f, (str, bytes, os.PathLike)) else '')\n"
            "    return real(f, *a, **k)\n"
            "builtins.open = spy\n"
            f"sys.path.insert(0, {HERE!r})\n"
            "import families\n"
            "icons = families.all_icons()\n"
            "for i in icons:\n"
            "    i.svg(False); i.svg(True)\n"
            f"root = os.path.join({SET!r}, 'icons') + os.sep\n"
            "print('\\n'.join(p for p in seen if p.startswith(root)))\n"
        )
        out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(out, "", "the generators read the installed icons:\n" + out)


if __name__ == "__main__":
    unittest.main()
