# SPDX-License-Identifier: GPL-2.0-or-later
"""Guards for the screens study: python3 -I -m unittest test_screens (run build.py first: it needs screens/*/scores.json)."""
import glob
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "east"))
import calculus as K  # noqa: E402

SCORES = {os.path.basename(os.path.dirname(f)): json.load(open(f)) for f in glob.glob(os.path.join(D, "screens", "*", "scores.json"))}


class Screens(unittest.TestCase):
    def test_built(self):
        self.assertGreaterEqual(len(SCORES), 15)

    def test_no_screen_loses_more_than_noise(self):
        # the pixel scorer moves about +-3 with a one-pixel change of the backdrop regions: a proposal may not lose more than that
        for k, s in SCORES.items():
            for m in ("light", "dark"):
                self.assertGreaterEqual(s[m]["new"]["total"], s[m]["cur"]["total"] - 3.0, (k, m))

    def test_no_rule_touches_the_frame_in_the_proposal(self):
        for k, s in SCORES.items():
            for m in ("light", "dark"):
                self.assertEqual(s[m]["tree_new"]["edge_lines"], 0, (k, m))

    def test_tree_proportion_improves_or_holds(self):
        for k, s in SCORES.items():
            for m in ("light", "dark"):
                self.assertGreaterEqual(s[m]["tree_new"]["module"] + 5, s[m]["tree_cur"]["module"], (k, m))

    def test_assistant_card_is_on_the_ruler(self):
        t = json.load(open(os.path.join(D, "screens", "installer-account", "new-light-tree.json")))
        card = max((n for n in t["nodes"] if n["role"] == "opening"), key=lambda n: n["rect"][2] * n["rect"][3])
        w, h = card["rect"][2:]
        self.assertEqual((w, h), (576, 540))
        self.assertIn(K.band(w)[0], K.GOOD_BANDS)
        self.assertIn(K.band(h)[0], K.GOOD_BANDS)

    def test_named_panel_widths(self):
        for v in (576, 336, 240, 120, 60):
            self.assertIn(v // K.U, K.NAMED, v)
        for v in (576, 540, 900, 280, 336, 320, 840, 240, 600):
            self.assertIn(K.band(v)[0], K.GOOD_BANDS, v)

    def test_controls_on_named_heights(self):
        for v in (16, 24, 40, 60, 84, 120):
            self.assertIn(v // K.U, K.NAMED, v)


if __name__ == "__main__":
    unittest.main()
