#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# GTK render check: every full-colour icon (design/icons/apps, apps/small, places, devices,
# mimetypes) drawn by GTK's own icon path must match its librsvg render, RMSE <= GTKCHECK_RMSE
# (default 0.02) at 48 and 128 px. GTK 4.24 draws SVG itself, and some filter chains that librsvg
# draws right come out as grey or dark blocks there (the reason this check exists).
#   bash design/tools/icons/gtkcheck/check.sh [svg ...]     (default: the whole set)
# Needs: cc, pkg-config + the gtk4 headers, gtk4-broadwayd, rsvg-convert. Missing one: prints
# "SKIPPED: ..." and exits 77 (the icons_v2 test reports that loudly). Exit 1 when an icon fails.
# Arch lane: .claude/bin/local-lane.sh run 'bash design/tools/icons/gtkcheck/check.sh'
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
MAX=${GTKCHECK_RMSE:-0.02}

for t in cc pkg-config gtk4-broadwayd rsvg-convert; do
  command -v "$t" >/dev/null || { echo "SKIPPED: gtkcheck needs $t"; exit 77; }
done
pkg-config --exists gtk4 || { echo "SKIPPED: gtkcheck needs the gtk4 development files (pkg-config gtk4)"; exit 77; }

tmp=$(mktemp -d)
bpid=
cleanup() { [ -z "$bpid" ] || kill "$bpid" 2>/dev/null || true; rm -rf "$tmp"; }
trap cleanup EXIT
# shellcheck disable=SC2046
cc -O1 -o "$tmp/gtkcheck" "$HERE/gtkcheck.c" $(pkg-config --cflags --libs gtk4) -lm

if [ $# -gt 0 ]; then
  svgs=("$@")
else
  shopt -s nullglob
  svgs=("$ROOT"/design/icons/apps/*.svg "$ROOT"/design/icons/apps/small/*.svg
        "$ROOT"/design/icons/places/*.svg "$ROOT"/design/icons/devices/*.svg "$ROOT"/design/icons/mimetypes/*.svg)
fi
[ ${#svgs[@]} -gt 0 ] || { echo "gtkcheck: no icons found" >&2; exit 2; }

# A private broadway display (the golden harness uses its own; pick one from the pid).
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/tmp}
n=$((60 + $$ % 30))
gtk4-broadwayd ":$n" --port $((9100 + n)) >/dev/null 2>&1 &
bpid=$!
for _ in $(seq 100); do [ -S "$XDG_RUNTIME_DIR/broadway$((n + 1)).socket" ] && break; sleep 0.05; done

# known-failures.txt: icons GTK still draws wrong (one path per line, relative to the repo, # comments).
# A listed icon that fails is reported as KNOWN; a listed icon that passes at both sizes is an error,
# so the list only ever shrinks.
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
  GDK_BACKEND=broadway BROADWAY_DISPLAY=":$n" "$tmp/gtkcheck" "$MAX" "$size" "${args[@]}" | sed "s|$ROOT/||" >>"$tmp/out" || true
done
# GTK before its own SVG renderer loads icons through gdk-pixbuf, i.e. librsvg itself: every render
# is then identical and there is nothing to compare (an older GTK on a CI runner).
if ! grep '^[0-9]' "$tmp/out" | grep -qv '^0\.0000 '; then
  echo "SKIPPED: GTK $(pkg-config --modversion gtk4) draws SVG icons through librsvg (every render identical), nothing to compare"
  exit 77
fi
declare -A failed=()
while read -r rmse size path flag; do
  if [ "${flag:-}" = FAIL ]; then
    failed[$path]=1
    if is_known "$path"; then echo "$rmse $size $path  KNOWN"; else echo "$rmse $size $path  FAIL"; rc=1; fi
  else
    echo "$rmse $size $path"
  fi
done <"$tmp/out"
grep -v '^[0-9]' "$tmp/out" || true
[ "$(grep -c '^[0-9]' "$tmp/out")" -eq $((2 * ${#svgs[@]})) ] || { echo "gtkcheck: GTK did not draw every icon"; rc=1; }
if [ $# -eq 0 ]; then
  for k in "${known[@]}"; do
    [ -n "${failed[$k]:-}" ] || { echo "gtkcheck: $k now matches librsvg: remove it from known-failures.txt"; rc=1; }
  done
fi
[ ${#known[@]} -eq 0 ] || echo "gtkcheck: ${#known[@]} known failure(s) listed in design/tools/icons/gtkcheck/known-failures.txt"
if [ $rc -ne 0 ]; then
  echo "gtkcheck: FAIL: GTK draws an icon differently from librsvg (RMSE > $MAX, lines marked FAIL)"
else
  echo "gtkcheck: ${#svgs[@]} icons, GTK matches librsvg at 48 and 128 px (RMSE <= $MAX)${known:+ except the known failures listed}"
fi
exit $rc
