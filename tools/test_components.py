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
            "is in RU-100..999": lambda s: s["rules"][0].update(id="RU-099"),
            "has no | and no line break": lambda s: s["rules"][0].update(text="A | B."),
            "enforced is manual, an RH-nnn": lambda s: s["rules"][0].update(enforced="Some Test"),
            "density.compact.control is a whole fen": lambda s: s["density"]["compact"].update(control=22),
            "density.compact gives a row or a control height": lambda s: s["density"].update(compact={"pad_y": 4}),
            "needs `why`": lambda s: s["sizes"]["regular"].update(off_grid=["height"]),
            "names width or height": lambda s: s["sizes"]["regular"].update(off_grid=["thumb"], why="Round."),
        }
        for want, change in cases.items():
            with self.subTest(want=want):
                got = self.broken(change)
                self.assertTrue(any(want in p for p in got), f"{want!r} not in {got}")

    def test_an_off_grid_length_needs_its_reason(self):
        s = copy.deepcopy(spec())
        s["sizes"]["regular"].update(height=26, off_grid=["height"], why="An optical size, 26 px.")
        self.assertEqual(components.problems(s, "switch.toml"), [])
        s["sizes"]["regular"].update(width=34)
        self.assertTrue(any("sizes.regular.width is a whole fen" in p for p in components.problems(s, "switch.toml")))

    def test_a_control_height_alone_is_a_density(self):
        s = copy.deepcopy(spec())
        s["density"]["compact"] = {"control": 20}
        self.assertEqual(components.problems(s, "switch.toml"), [])

    def test_rule_ids_are_unique_across_specs(self):
        cat, _ = components.catalog()
        ids = [r["id"] for c in cat["components"] for r in c["rules"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_a_rule_id_stays_in_its_category_block(self):
        # RU-100..199 actions and selection, 200..299 input, 500..599 communication (ARCHITECTURE 5).
        blocks = {"actions": (100, 199), "selection": (100, 199), "input": (200, 299), "communication": (500, 599)}
        cat, _ = components.catalog()
        for c in cat["components"]:
            lo, hi = blocks.get(c["category"], (0, 999))
            for r in c["rules"]:
                self.assertTrue(lo <= int(r["id"][3:]) <= hi, f"{r['id']} is outside the {c['category']} block {lo}-{hi}")


class RulesMd(unittest.TestCase):
    """The generated docs/RULES-ui.md block (DS-RULE-1)."""

    def cat(self):
        return components.catalog()[0]

    def test_every_rule_is_a_row_and_the_manual_ones_are_listed(self):
        md = components.rules_md(self.cat())
        # Every spec's rules, named by their component (the catalog grows past the switch).
        named = [(c["name"], r) for c in self.cat()["components"] for r in c["rules"]]
        rules = [r for _, r in named]
        for r in rules:
            self.assertEqual(sum(1 for l in md.splitlines() if l.startswith(f"| {r['id']} | ")), 1, r["id"])
        manual = [(n, r) for n, r in named if r["enforced"] == "manual"]
        listed = md.split("#### Component rules a person checks")[1]
        self.assertTrue(manual)
        for n, r in manual:
            self.assertIn(f"- {r['id']} ({n}): {r['text']}", listed)
        for r in rules:
            if r["enforced"] != "manual":
                self.assertNotIn(f"- {r['id']} ", listed)

    def test_without_manual_rules_the_list_says_none(self):
        cat = self.cat()
        for c in cat["components"]:
            for r in c["rules"]:
                r["enforced"] = "kit_components"
        self.assertIn("\nNone.\n", components.rules_md(cat))

    def test_rows_are_sorted_by_id(self):
        cat = self.cat()
        cat["components"][0]["rules"].reverse()
        ids = [l.split(" | ")[0] for l in components.rules_md(cat).splitlines() if l.startswith("| RU-")]
        self.assertEqual(ids, sorted(ids))

    def test_the_shipped_document_has_the_current_block(self):
        if not os.path.exists(components.DOC):
            self.skipTest("the design repository alone has no docs/")
        doc = open(components.DOC, encoding="utf-8").read()
        at = components.doc_block(doc)
        self.assertIsNotNone(at, "docs/RULES-ui.md has no component-rules block")
        self.assertEqual(doc[at[0]:at[1]], components.rules_md(self.cat()))

    def test_write_replaces_only_the_block(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            doc = os.path.join(d, "RULES-ui.md")
            with open(doc, "w", encoding="utf-8") as f:
                f.write(f"before\n\n{components.BEGIN}\nold\n{components.END}\n\nafter\n")
            old = components.DOC
            components.DOC = doc
            try:
                self.assertEqual(components.main(["--rules-md", "--write"]), 0)
                text = open(doc, encoding="utf-8").read()
            finally:
                components.DOC = old
            self.assertTrue(text.startswith("before\n\n" + components.BEGIN))
            self.assertTrue(text.endswith(components.END + "\n\nafter\n"))
            self.assertNotIn("\nold\n", text)
            self.assertIn("| RU-110 | Switch | Do |", text)


if __name__ == "__main__":
    unittest.main(verbosity=1)
