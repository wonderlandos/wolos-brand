# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests of the scale half of design/tools/tokens.py (type, space, elevation, motion, density as data).

  python3 -I design/tools/test_tokens.py
"""
import copy
import os
import sys
import tomllib
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tokens  # noqa: E402


class Scale(unittest.TestCase):
    def test_the_shipped_sources_pass(self):
        self.assertEqual(tokens.scale_problems(tokens.scale_load()), [])

    def test_the_generated_files_are_current(self):
        S = tokens.scale_load()
        for rel, want in (("tokens/scale.css", tokens.scale_css(S)), ("tokens/scale.sh", tokens.scale_sh(S))):
            with open(os.path.join(tokens.D, rel), encoding="utf-8") as f:
                self.assertEqual(f.read(), want.strip() + "\n", rel)

    def test_each_rule_catches_its_break(self):
        cases = {
            "not a whole number of fen": lambda S: S["space"]["space"].update(s3=11),
            "off the 4 px line": lambda S: S["type"]["roles"]["body"].update(line=21),
            "below 11": lambda S: S["type"]["roles"]["caption"].update(size=10),
            "does not grow": lambda S: S["density"]["metrics"]["row"].update(compact=44),
            "under 20 px": lambda S: S["density"]["metrics"]["target"].update(compact=16),
            "density inset standard is space.inset": lambda S: S["density"]["metrics"]["inset"].update(standard=16),
            "is not a cubic-bezier": lambda S: S["motion"]["curve"].update(ease=[2, 0, 0, 1]),
            "unknown curve": lambda S: S["motion"]["css"].update({"--ease-out": "nope"}),
            "nothing longer than 400": lambda S: S["motion"]["duration"].update(slow=500),
        }
        for want, change in cases.items():
            with self.subTest(want=want):
                S = copy.deepcopy(tokens.scale_load())
                change(S)
                got = tokens.scale_problems(S)
                self.assertTrue(any(want in p for p in got), f"{want!r} not in {got}")

    def test_the_component_specs_use_the_density_metrics(self):
        """A spec's [density.<d>] row is the density row; the two sources cannot drift."""
        S = tokens.scale_load()
        d = os.path.join(tokens.D, "components")
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".toml"):
                continue
            with open(os.path.join(d, fn), "rb") as f:
                spec = tomllib.load(f)
            for dens, m in spec.get("density", {}).items():
                # A spec gives the row that holds it, the control's own height, or both; `row_stack`
                # (a row with its title above the control) has no token and is the spec's own.
                for key in ("row", "control"):
                    if key in m:
                        self.assertEqual(m[key], S["density"]["metrics"][key][dens], f"{fn} density.{dens}.{key}")
                # The menu's `item` is the density token menu-item; other `item` keys (table row, tree row,
                # drawer item) are the component's own and have no token.
                if fn == "menu.toml":
                    self.assertEqual(m["item"], S["density"]["metrics"]["menu-item"][dens], f"{fn} density.{dens}.item")


if __name__ == "__main__":
    unittest.main(verbosity=1)
