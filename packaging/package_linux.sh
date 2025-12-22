#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VERSION="$(python "$ROOT_DIR/bump_version.py")"
ARCH="$(dpkg --print-architecture)"

DIST_DIR="$ROOT_DIR/dist"
INSTALLER_DIR="$DIST_DIR/installers"
PKGROOT="$ROOT_DIR/build/pkgroot"

APP_DIR="$PKGROOT/usr/lib/priorityplot"
BIN_DIR="$PKGROOT/usr/bin"
DESKTOP_DIR="$PKGROOT/usr/share/applications"
DEBIAN_DIR="$PKGROOT/DEBIAN"

rm -rf "$PKGROOT"
mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$DEBIAN_DIR" "$INSTALLER_DIR"

if [ -d "$DIST_DIR/priorityplot" ]; then
  cp -R "$DIST_DIR/priorityplot/." "$APP_DIR/"
else
  cp -R "$DIST_DIR/priorityplot" "$APP_DIR/"
fi

cat > "$BIN_DIR/priorityplot" <<'EOF'
#!/bin/sh
exec /usr/lib/priorityplot/priorityplot "$@"
EOF
chmod 755 "$BIN_DIR/priorityplot"

cp "$ROOT_DIR/packaging/linux/priorityplot.desktop" "$DESKTOP_DIR/priorityplot.desktop"

sed -e "s/__VERSION__/$VERSION/" -e "s/__ARCH__/$ARCH/" \
  "$ROOT_DIR/packaging/linux/control" > "$DEBIAN_DIR/control"

dpkg-deb --build "$PKGROOT" "$INSTALLER_DIR/priorityplot_${VERSION}_${ARCH}.deb"
