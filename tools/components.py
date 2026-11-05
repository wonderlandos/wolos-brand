# SPDX-License-Identifier: GPL-2.0-or-later
"""WolOS Design System: the component specs (design/components/*.toml) as one catalog.

  python3 -I design/tools/components.py           write design/components/catalog.json
  python3 -I design/tools/components.py --check   fail when catalog.json is not what the specs say,
                                                   or a spec breaks the schema

The catalog is the one source the docs site (wolos.org/design), the Kit widget tests
(crates/shell/tests/kit_components.rs), the libWolkit component snapshots and the web kit node tests
read; none of them parses TOML. Standard library only (tomllib, Python 3.11+), like tools/tokens.py.
"""
import json
import os
import re
import sys
import tomllib

D = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SPECS = os.path.join(D, "components")
OUT = os.path.join(SPECS, "catalog.json")

CATEGORIES = {"actions", "selection", "input", "navigation", "containment", "communication",
              "data", "layout", "system"}
STATUS = {"proposal", "beta", "stable", "deprecated"}
DENSITIES = ("compact", "standard", "comfortable")
VARIANTS = ("light", "dark")
KITS = {"gtk", "wolkit", "web", "view"}
REQUIRED = ("schema", "id", "name", "category", "status", "summary", "implementations",
            "states", "keyboard", "a11y", "rules", "tests")
KEBAB = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
RULE = re.compile(r"^RU-\d{3}$")
FEN = 4


def problems(spec, name):
    """Sentences for everything wrong with one spec (empty when it is fine)."""
    out = []
    say = lambda s: out.append(f"{name}: {s}")
    for k in REQUIRED:
        if k not in spec:
            say(f"needs `{k}`")
    if out:
        return out
    if spec["schema"] != 1:
        say("schema is 1")
    if not KEBAB.match(spec["id"]) or f"{spec['id']}.toml" != name:
        say("id is the file name, lower-case kebab-case")
    if spec["category"] not in CATEGORIES:
        say(f"category is one of {sorted(CATEGORIES)}")
    if spec["status"] not in STATUS:
        say(f"status is one of {sorted(STATUS)}")
    if not set(spec["implementations"]) <= KITS or not spec["implementations"]:
        say(f"implementations are some of {sorted(KITS)}")
    for kit, impl in spec["implementations"].items():
        f = impl.get("file")
        if f is not None and (f.startswith("/") or ".." in f.split("/")):
            say(f"{kit} file is a path inside the repository")
    for size, dims in spec.get("sizes", {}).items():
        for k in ("width", "height", "thumb", "padding"):
            v = dims.get(k)
            if v is not None and (not isinstance(v, int) or v % FEN and k in ("width", "height")):
                say(f"sizes.{size}.{k} is a whole fen (a multiple of {FEN} px)")
    for d, m in spec.get("density", {}).items():
        if d not in DENSITIES:
            say(f"density {d} is one of {DENSITIES}")
        if not isinstance(m.get("row"), int) or m["row"] % FEN:
            say(f"density.{d}.row is a whole fen")
    t = spec["tests"]
    for s in t.get("states", []):
        if s not in spec["states"]:
            say(f"tests.states names {s}, which [states] does not describe")
    for d in t.get("densities", []):
        if d not in spec.get("density", {}):
            say(f"tests.densities names {d}, which [density] does not give")
    for v in t.get("variants", []):
        if v not in VARIANTS:
            say(f"tests.variants are {VARIANTS}")
    for r in spec["rules"]:
        if not RULE.match(r.get("id", "")):
            say(f"rule id {r.get('id')!r} is RU-nnn")
        if r.get("kind") not in ("do", "dont"):
            say(f"rule {r.get('id')} kind is do or dont")
        if not r.get("text", "").endswith("."):
            say(f"rule {r.get('id')} text is one sentence with a full stop")
        if not r.get("enforced"):
            say(f"rule {r.get('id')} says what enforces it (a test, a ratchet id, or manual)")
    return out


def catalog():
    """(catalog dict, problems) from every spec file."""
    specs, bad, seen = [], [], {}
    for name in sorted(os.listdir(SPECS)):
        if not name.endswith(".toml"):
            continue
        with open(os.path.join(SPECS, name), "rb") as f:
            try:
                spec = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                bad.append(f"{name}: not TOML ({e})")
                continue
        bad += problems(spec, name)
        for r in spec.get("rules", []):
            rid = r.get("id")
            if rid in seen:
                bad.append(f"{name}: rule {rid} is also in {seen[rid]}")
            seen[rid] = name
        specs.append(spec)
    return {"schema": 1, "components": specs}, bad


def main(argv):
    cat, bad = catalog()
    text = json.dumps(cat, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if bad:
        print("\n".join(bad), file=sys.stderr)
        return 1
    if "--check" in argv:
        have = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if have != text:
            print("design/components/catalog.json is not what the specs say: run design/tools/components.py",
                  file=sys.stderr)
            return 1
        print(f"{len(cat['components'])} component specs, catalog up to date")
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {os.path.relpath(OUT, D)} ({len(cat['components'])} components)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
