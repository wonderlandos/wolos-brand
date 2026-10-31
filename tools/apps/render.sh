#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
# Render a real GTK app under broadway with a private HOME and screenshot it (dev proof of app theming).
# usage: render.sh <display-num> <out.png> <home> [--click x,y ...] -- <cmd...>
# env: WAIT (s, default 5), EXTRA_ENV ("K=V ..."), CHROME (default: Playwright headless shell).
here=$(cd "$(dirname "$0")" && pwd)
n=$1 out=$2 home=$3; shift 3
clicks=()
while [ "$1" != "--" ]; do [ "$1" = --click ] && shift; clicks+=("$1"); shift; done
shift
export CHROME=${CHROME:-$(ls -d ~/.cache/ms-playwright/chromium_headless_shell-*/*/ | head -1)chrome-headless-shell}
gtk4-broadwayd :$n >/dev/null 2>&1 & B=$!
sleep 1
env HOME=$home XDG_CONFIG_HOME=$home/.config XDG_DATA_HOME=$home/.local/share XDG_CACHE_HOME=$home/.cache \
	GDK_BACKEND=broadway BROADWAY_DISPLAY=:$n GSETTINGS_BACKEND=memory $EXTRA_ENV \
	dbus-run-session -- "$@" >"$out.log" 2>&1 & A=$!
sleep "${WAIT:-5}"
timeout 40 node "$here/shot.mjs" "http://127.0.0.1:$((8080 + n))/" "$out" 1000 700 3000 "${clicks[@]}" >/dev/null
pkill -P $A 2>/dev/null; kill $A $B 2>/dev/null; wait 2>/dev/null
