#!/bin/bash
# Prove third-party app theming on this host: `wol theme light|dark` into private HOMEs, render real
# apps (nautilus, gnome-text-editor, loupe) under broadway with a focusing click, a Qt palette
# harness, then a contact sheet. usage: run.sh <outdir>   (needs: cargo build -p controller)
set -u
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../.." && pwd)
o=$1
mkdir -p "$o"
g++ -std=c++17 -fPIC "$here/qtharness.cpp" -o "$o/qtharness" $(pkg-config --cflags --libs Qt6Widgets)
for v in light dark; do
	h=$o/home-$v
	rm -rf "$h"; mkdir -p "$h/.config" "$h/Documents" "$h/Pictures" "$h/Music"
	printf 'Notes from WolOS\n\nOne look for every app.\n' >"$h/Documents/notes.txt"
	sh "$repo/design/icons/install.sh" "$h/.local/share/icons/WolOS" >/dev/null 2>&1
	: >"$h/Documents/Budget.ods"; : >"$h/Documents/Report.pdf"; : >"$h/Desktop/notes.txt"
	mkdir -p "$h/Downloads" "$h/Videos" "$h/Desktop"
	printf 'XDG_%s_DIR="$HOME/%s"\n' DESKTOP Desktop DOCUMENTS Documents DOWNLOAD Downloads MUSIC Music PICTURES Pictures VIDEOS Videos >"$h/.config/user-dirs.dirs"
	rsvg-convert -w 1600 "$repo/design/wallpapers/wonderland-dusk.svg" -o "$h/Pictures/dusk.png"
	GSETTINGS_BACKEND=memory XDG_CONFIG_HOME=$h/.config "$repo/target/debug/wol" theme "$v" >/dev/null
	[ $v = dark ] && sc=prefer-dark || sc=prefer-light
	export EXTRA_ENV="ADW_DEBUG_COLOR_SCHEME=$sc LANG=en_US.UTF-8"
	# Click the first folder: focuses the window and selects it (accent).
	WAIT=6 bash "$here/render.sh" 7 "$o/nautilus-$v.png" "$h" --click 498,150 -- nautilus --new-window "$h"
	# Click into the text (focus), then Ctrl+A: the selection is drawn in the accent.
	bash "$here/render.sh" 8 "$o/editor-$v.png" "$h" --click 300,150 --click select-all -- gnome-text-editor --standalone "$h/Documents/notes.txt"
	WAIT=6 bash "$here/render.sh" 9 "$o/loupe-$v.png" "$h" --click 400,300 -- loupe "$h/Pictures/dusk.png"
	QT_QPA_PLATFORM=offscreen "$o/qtharness" "$h/.config/qt6ct/qt6ct.conf" "$o/qt-$v.png"
done
python3 -I "$here/sheet.py" "$o" "$o/apps-contact.png"
# Window controls must match kit AppWindow on pixels (diameter, colour, spacing).
g=$repo/crates/shell/tests/golden
python3 -I "$here/measure.py" "$g/settings-about-wide-light.png" "$o"/{nautilus,editor,loupe}-light.png &&
	python3 -I "$here/measure.py" "$g/settings-about-wide-dark.png" "$o"/{nautilus,editor,loupe}-dark.png
