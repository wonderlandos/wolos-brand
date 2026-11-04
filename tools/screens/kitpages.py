# SPDX-License-Identifier: GPL-2.0-or-later
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402
from scene import TOK  # noqa: E402


def _render(v, m):
    return kit.sheet(m, kit.K_CUR if v == "cur" else kit.K_NEW, TOK[v], "kit")


PAGES = {"kit": dict(title="Kit: widgets e tokens globais (kit.css)", render=_render, golden=None,
                     sub="960 x 640, 1x; mesma funcao desenha atual e proposto")}
