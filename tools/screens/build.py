# SPDX-License-Identifier: GPL-2.0-or-later
"""Build one screen: render current and proposed (light, dark), score them, write the board and scores.json.

  python3 -I build.py SCREEN [SCREEN ...]        SCREEN = a key of REG below (see each module's PAGES)
  -> screens/SCREEN/{cur,new}-{light,dark}.{svg,png}, -tree.json; screens/SCREEN/board.png; screens/SCREEN/scores.json

A screen module exposes PAGES = {key: dict(title, render=fn(variant, mode)->Scene, golden=fn(mode)->png|None, frame=(w, h))}."""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheets as SH  # noqa: E402
from scene import TOK  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "screens"))
MODULES = ("kitpages", "installer", "setup", "lockscreen", "settingspages", "storepages")


def registry():
    reg = {}
    for m in MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name == m:
                continue
            raise
        reg.update(mod.PAGES)
    return reg


def build(key, thumb_w=620):
    reg = registry()
    pg = reg[key]
    d = os.path.join(OUT, key)
    os.makedirs(d, exist_ok=True)
    files, jobs = {}, []
    for v in ("cur", "new"):
        for m in ("light", "dark"):
            s = pg["render"](v, m)
            s.name = v
            base = s.save(d)
            files[(v, m)] = base
            jobs.append((base + ".png", base + "-tree.json"))
    gold = {m: pg["golden"](m) if pg.get("golden") else None for m in ("light", "dark")}
    for m in ("light", "dark"):
        if gold[m]:
            jobs.append((gold[m], files[("cur", m)] + "-tree.json"))
    res = SH.run_scores(jobs)
    sc = {}
    k = 0
    for v in ("cur", "new"):
        for m in ("light", "dark"):
            sc[(v, m)] = res[k]; k += 1
    gsc = {}
    for m in ("light", "dark"):
        if gold[m]:
            gsc[m] = res[k]; k += 1
    summary = {"screen": key, "title": pg["title"]}
    for m in ("light", "dark"):
        summary[m] = {"cur": {r: sc[("cur", m)][r]["score"] for r in SH.RULES} | {"total": sc[("cur", m)]["total"]},
                      "new": {r: sc[("new", m)][r]["score"] for r in SH.RULES} | {"total": sc[("new", m)]["total"]}}
        if m in gsc:
            summary[m]["golden"] = {r: gsc[m][r]["score"] for r in SH.RULES} | {"total": gsc[m]["total"]}
        summary[m]["tree_cur"] = sc[("cur", m)].get("tree")
        summary[m]["tree_new"] = sc[("new", m)].get("tree")
        summary[m]["why_new"] = {r: sc[("new", m)][r]["why"] for r in SH.RULES}
    json.dump(summary, open(os.path.join(d, "scores.json"), "w"), indent=1, default=str)
    left = lambda m: gold[m] or files[("cur", m)] + ".png"
    panels = [[("Atual (" + ("golden real" if gold["light"] else "medido") + "), claro", left("light")), ("Proposto, claro", files[("new", "light")] + ".png")],
              [("Atual, escuro", left("dark")), ("Proposto, escuro", files[("new", "dark")] + ".png")]]
    scores = {"light": (sc[("cur", "light")], sc[("new", "light")], "Claro: atual (medido) -> proposto"),
              "dark": (sc[("cur", "dark")], sc[("new", "dark")], "Escuro: atual (medido) -> proposto")}
    sub = pg.get("sub", "")
    if gsc:
        sub += "  |  golden real (claro/escuro): %.1f / %.1f" % (gsc["light"]["total"], gsc["dark"]["total"])
    SH.compose(pg["title"], panels, os.path.join(d, "board.png"), scores, thumb_w=thumb_w, sub=sub)
    return summary


if __name__ == "__main__":
    for k in sys.argv[1:]:
        s = build(k)
        for m in ("light", "dark"):
            print(k, m, "cur %.1f -> new %.1f" % (s[m]["cur"]["total"], s[m]["new"]["total"]), "golden", s[m].get("golden", {}).get("total"))
