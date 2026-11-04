# SPDX-License-Identifier: GPL-2.0-or-later
"""Fork/join for the east tools: fan a function out over items, join the results in order.

  fanout(fn, items)          processes (one per core): files, icons, renders
  fanout(fn, items, threads=True)   threads: the rules of one picture share its arrays

fn must be a module-level function when processes are used (it is pickled)."""
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def fanout(fn, items, threads=False, workers=None):
    items = list(items)
    if len(items) <= 1:
        return [fn(x) for x in items]
    pool = ThreadPoolExecutor if threads else ProcessPoolExecutor
    with pool(max_workers=workers or min(len(items), os.cpu_count() or 4)) as ex:
        return list(ex.map(fn, items))
