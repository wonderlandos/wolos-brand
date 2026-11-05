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
        }
        for want, change in cases.items():
            with self.subTest(want=want):
                got = self.broken(change)
                self.assertTrue(any(want in p for p in got), f"{want!r} not in {got}")


class RulesMd(unittest.TestCase):
    """The generated docs/RULES-ui.md block (DS-RULE-1)."""

    def cat(self):
        return components.catalog()[0]

    def test_every_rule_is_a_row_and_the_manual_ones_are_listed(self):
        md = components.rules_md(self.cat())
        rules = [r for c in self.cat()["components"] for r in c["rules"]]
        for r in rules:
            self.assertEqual(sum(1 for l in md.splitlines() if l.startswith(f"| {r['id']} | ")), 1, r["id"])
        manual = [r for r in rules if r["enforced"] == "manual"]
        listed = md.split("#### Component rules a person checks")[1]
        self.assertTrue(manual)
        for r in manual:
            self.assertIn(f"- {r['id']} (Switch): {r['text']}", listed)
        for r in rules:
            if r["enforced"] != "manual":
                self.assertNotIn(f"- {r['id']} ", listed)

    def test_without_manual_rules_the_list_says_none(self):
        cat = self.cat()
        for r in cat["components"][0]["rules"]:
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
