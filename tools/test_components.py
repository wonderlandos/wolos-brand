# SPDX-License-Identifier: GPL-2.0-or-later
"""Tests of design/tools/components.py: the shipped specs pass, and each schema rule catches its break.

  python3 -I design/tools/test_components.py
"""
import copy
import os
import sys
import tomllib
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import components  # noqa: E402

SWITCH = os.path.join(components.SPECS, "switch.toml")


def spec():
    with open(SWITCH, "rb") as f:
        return tomllib.load(f)


class Schema(unittest.TestCase):
    def test_the_shipped_specs_pass(self):
        cat, bad = components.catalog()
        self.assertEqual(bad, [])
        self.assertIn("switch", [c["id"] for c in cat["components"]])

    def broken(self, change):
        s = copy.deepcopy(spec())
        change(s)
        return components.problems(s, "switch.toml")

    def test_each_rule_catches_its_break(self):
        cases = {
            "needs `states`": lambda s: s.pop("states"),
            "id is the file name": lambda s: s.update(id="Switch"),
            "category is one of": lambda s: s.update(category="widgets"),
            "density.compact.row is a whole fen": lambda s: s["density"]["compact"].update(row=30),
            "sizes.regular.width is a whole fen": lambda s: s["sizes"]["regular"].update(width=35),
            "which [states] does not describe": lambda s: s["tests"]["states"].append("hover"),
            "which [density] does not give": lambda s: s["density"].pop("comfortable"),
            "is RU-nnn": lambda s: s["rules"][0].update(id="RU-1100"),
            "kind is do or dont": lambda s: s["rules"][0].update(kind="should"),
            "says what enforces it": lambda s: s["rules"][0].pop("enforced"),
            "a path inside the repository": lambda s: s["implementations"]["gtk"].update(file="/usr/lib/x"),
        }
        for want, change in cases.items():
            with self.subTest(want=want):
                got = self.broken(change)
                self.assertTrue(any(want in p for p in got), f"{want!r} not in {got}")


if __name__ == "__main__":
    unittest.main(verbosity=1)
