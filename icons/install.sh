#!/bin/sh
# Install WolOS icon theme. Usage: install.sh [DESTDIR] (default /usr/local/share/icons/WolOS)
set -eu
src=$(cd "$(dirname "$0")" && pwd)
dst=${1:-/usr/local/share/icons/WolOS}
mkdir -p "$dst/scalable/apps" "$dst/scalable/places" "$dst/symbolic/status" "$dst/symbolic/actions"
cp "$src/index.theme" "$dst/"
cp "$src"/apps/*.svg "$dst/scalable/apps/"
cp "$src"/symbolic/*.svg "$dst/symbolic/status/"
grep -v '^#' "$src/aliases.tsv" | while IFS="$(printf '\t')" read -r base names; do
  for n in $names; do
    case $n in user-trash*) d=places ;; *) d=apps ;; esac
    ln -sf "../apps/wolos-$base.svg" "$dst/scalable/$d/$n.svg"
  done
done
# Places, devices, mimetypes (design/tools/places.py); replace any app-icon alias of the same name.
for ctx in places devices mimetypes; do
  mkdir -p "$dst/scalable/$ctx"
  for f in "$src/$ctx"/*.svg; do
    rm -f "$dst/scalable/$ctx/${f##*/}"
    cp "$f" "$dst/scalable/$ctx/"
  done
done
grep -v '^#' "$src/places-aliases.tsv" | while IFS="$(printf '\t')" read -r ctx base names; do
  for n in $names; do ln -sf "$base.svg" "$dst/scalable/$ctx/$n.svg"; done
done
for n in system-search-symbolic system-shutdown-symbolic; do
  ln -sf "../status/$n.svg" "$dst/symbolic/actions/$n.svg"
done
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$dst" || true
