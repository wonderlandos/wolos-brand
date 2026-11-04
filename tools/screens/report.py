# SPDX-License-Identifier: GPL-2.0-or-later
"""Write the per-screen score table (screens/*/scores.json) into .claude/v012/brand-east/screens-report.md.
  python3 -I report.py"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.normpath(os.path.join(HERE, "..", ".."))
RULES = ("qi", "sha", "forms", "zones", "palette", "light", "proportion", "density")


def table():
    rows = ["| screen | light: mock now | light: proposal | light: golden | dark: mock now | dark: proposal | dark: golden |", "|---|---|---|---|---|---|---|"]
    tot = {"l0": [], "l1": [], "d0": [], "d1": []}
    for f in sorted(glob.glob(os.path.join(D, "screens", "*", "scores.json"))):
        s = json.load(open(f))
        g = lambda m: ("%.1f" % s[m]["golden"]["total"]) if "golden" in s[m] else "-"
        rows.append("| %s | %.1f | %.1f | %s | %.1f | %.1f | %s |" % (s["screen"], s["light"]["cur"]["total"], s["light"]["new"]["total"], g("light"),
                                                                    s["dark"]["cur"]["total"], s["dark"]["new"]["total"], g("dark")))
        for k, (m, v) in {"l0": ("light", "cur"), "l1": ("light", "new"), "d0": ("dark", "cur"), "d1": ("dark", "new")}.items():
            tot[k].append(s[m][v]["total"])
    mean = lambda a: sum(a) / len(a)
    rows.append("| **mean** | %.1f | %.1f | | %.1f | %.1f | |" % (mean(tot["l0"]), mean(tot["l1"]), mean(tot["d0"]), mean(tot["d1"])))
    return "\n".join(rows)


def rules():
    out = ["| screen | mode | " + " | ".join(RULES) + " | total |", "|---|---|" + "---|" * (len(RULES) + 1)]
    for f in sorted(glob.glob(os.path.join(D, "screens", "*", "scores.json"))):
        s = json.load(open(f))
        for m in ("light", "dark"):
            a, b = s[m]["cur"], s[m]["new"]
            out.append("| %s | %s | " % (s["screen"], m) + " | ".join("%.0f > %.0f" % (a[r], b[r]) for r in RULES) + " | %.1f > %.1f |" % (a["total"], b["total"]))
    return "\n".join(out)


if __name__ == "__main__":
    print(table())
    print()
    print(rules())
