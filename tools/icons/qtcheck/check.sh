#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Qt render check: every full-colour icon (design/icons/apps, apps/small, places, devices,
# mimetypes) drawn by QtSvg, the renderer Qt apps on WolOS load the same icon theme with, must stay
# within QTCHECK_RMSE (default 0.03) of its librsvg render at 48 and 128 px (premultiplied RGBA, as
# gtkcheck). QtSvg 6.12 draws masks and the blur filters but ignores clip-path, so a clipped glow or
# mesh spills over the card (RMSE up to 0.12 on 2026-11-03): the generator writes every clipPath as
# the same shape in a luminance mask (svgk.qt_safe), after which the worst icon is 0.020. A Qt
# without filters (before 6.7) is the case icons_v2::full_colour_icons_read_with_their_filters_ignored
# covers. The companion of gtkcheck/check.sh.
#   bash design/tools/icons/qtcheck/check.sh [svg ...]     (default: the whole set)
# Needs: c++, pkg-config + the Qt 6 Svg and Gui headers (Arch: qt6-svg), rsvg-convert. Missing one:
# prints "SKIPPED: ..." and exits 77. Exit 1 when an icon fails.
# QTCHECK_OUT=<dir> keeps the Qt renders for review.
# Arch lane: .claude/bin/local-lane.sh run 'pacman -S --noconfirm --needed qt6-svg && bash design/tools/icons/qtcheck/check.sh'
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
MAX=${QTCHECK_RMSE:-0.03}

for t in c++ pkg-config rsvg-convert; do
  command -v "$t" >/dev/null || { echo "SKIPPED: qtcheck needs $t"; exit 77; }
done
pkg-config --exists Qt6Svg Qt6Gui || { echo "SKIPPED: qtcheck needs the Qt 6 Svg development files (pkg-config Qt6Svg)"; exit 77; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
# shellcheck disable=SC2046
c++ -std=c++17 -O1 -fPIC -o "$tmp/qtcheck" "$HERE/qtcheck.cpp" $(pkg-config --cflags --libs Qt6Svg Qt6Gui)

if [ $# -gt 0 ]; then
  svgs=("$@")
else
  shopt -s nullglob
  svgs=("$ROOT"/design/icons/apps/*.svg "$ROOT"/design/icons/apps/small/*.svg
        "$ROOT"/design/icons/places/*.svg "$ROOT"/design/icons/devices/*.svg "$ROOT"/design/icons/mimetypes/*.svg)
fi
[ ${#svgs[@]} -gt 0 ] || { echo "qtcheck: no icons found" >&2; exit 2; }

known=()
[ -f "$HERE/known-failures.txt" ] && mapfile -t known < <(sed 's/#.*//; s/[[:space:]]*$//; /^$/d' "$HERE/known-failures.txt")
is_known() { local k; for k in "${known[@]}"; do [ "$k" = "$1" ] && return 0; done; return 1; }

rc=0
: >"$tmp/out"
for size in 48 128; do
  args=()
  i=0
  for s in "${svgs[@]}"; do
    i=$((i + 1))
    rsvg-convert -w "$size" -h "$size" "$s" -o "$tmp/ref-$size-$i.png"
    args+=("$s" "$tmp/ref-$size-$i.png")
  done
  QT_QPA_PLATFORM=offscreen "$tmp/qtcheck" "$MAX" "$size" "${args[@]}" 2>>"$tmp/err" | sed "s|$ROOT/||" >>"$tmp/out" || true
done
declare -A failed=()
while read -r rmse size path flag; do
  if [ "${flag:-}" = FAIL ]; then
    failed[$path]=1
    if is_known "$path"; then echo "$rmse $size $path  KNOWN"; else echo "$rmse $size $path  FAIL"; rc=1; fi
  else
    echo "$rmse $size $path"
  fi
done <"$tmp/out"
grep -v '^qt\.\|^$' "$tmp/err" || true
[ "$(grep -c '^[0-9]' "$tmp/out")" -eq $((2 * ${#svgs[@]})) ] || { echo "qtcheck: Qt did not draw every icon"; rc=1; }
if [ $# -eq 0 ]; then
  for k in "${known[@]}"; do
    [ -n "${failed[$k]:-}" ] || { echo "qtcheck: $k now matches librsvg: remove it from known-failures.txt"; rc=1; }
  done
fi
qv=$(pkg-config --modversion Qt6Svg)
if [ $rc -ne 0 ]; then
  echo "qtcheck: FAIL: QtSvg $qv draws an icon too far from librsvg (RMSE > $MAX, lines marked FAIL)"
else
  echo "qtcheck: ${#svgs[@]} icons, QtSvg $qv within RMSE $MAX of librsvg at 48 and 128 px${known:+ except the known failures listed}"
fi
exit $rc
