# SPDX-License-Identifier: GPL-2.0-or-later
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assistant as A  # noqa: E402

PAGES = A.make_pages(A.PAGES_I)
