#!/bin/sh
# Build the perf probes: dmg (screencopy frame hash clock), vk (virtual keyboard), vp (virtual pointer).
# Output: design/tools/perf/bin. Needs cc, wayland-client and xkbcommon.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$here/bin"
flags=$(pkg-config --cflags --libs wayland-client)
cc -O2 -o "$here/bin/dmg" "$here/src/dmg.c" "$here/src/sc.c" $flags
cc -O2 -o "$here/bin/vk" "$here/src/vk.c" "$here/src/vk-proto.c" $flags $(pkg-config --libs xkbcommon)
cc -O2 -o "$here/bin/vp" "$here/src/vp.c" "$here/src/vp-proto.c" $flags
