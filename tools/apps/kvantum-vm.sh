#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-or-later
# Render the Qt harness with the generated Kvantum theme inside the FreeBSD VM (Kvantum is not on
# the Linux dev host). Needs the VM up (image/vm/up.sh) and `pkg install -y Kvantum qt6-base` there.
# Uses /tmp/wol-kv in the VM only. usage: kvantum-vm.sh <outdir>   -> <outdir>/kv-{light,dark}.png
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../.." && pwd)
o=$1
ssh="sh $repo/image/vm/ssh.sh"
w=$(mktemp -d)
for v in light dark; do
	GSETTINGS_BACKEND=memory XDG_CONFIG_HOME=$w/$v "$repo/target/debug/wol" theme "$v" >/dev/null
done
cp "$here/qtharness.cpp" "$w/"
(cd "$w" && tar chf - .) | $ssh 'rm -rf /tmp/wol-kv && mkdir -p /tmp/wol-kv && tar xf - -C /tmp/wol-kv'
$ssh 'cd /tmp/wol-kv && c++ -std=c++17 -fPIC qtharness.cpp -o qtharness $(pkg-config --cflags --libs Qt6Widgets) &&
	for v in light dark; do
		sed -i "" "s|^color_scheme_path=.*|color_scheme_path=/tmp/wol-kv/$v/qt6ct/colors/WolOS.conf|" $v/qt6ct/qt6ct.conf
		XDG_CONFIG_HOME=/tmp/wol-kv/$v HOME=/tmp/wol-kv/$v QT_QPA_PLATFORM=offscreen QT_STYLE_OVERRIDE=kvantum \
			./qtharness $v/qt6ct/qt6ct.conf kv-$v.png 2>/dev/null
	done'
for v in light dark; do $ssh "cat /tmp/wol-kv/kv-$v.png" >"$o/kv-$v.png"; done
rm -rf "$w"
ls -la "$o"/kv-*.png
