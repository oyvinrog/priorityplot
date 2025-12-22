#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

VERSION="$(python "$ROOT_DIR/bump_version.py")"
DIST_DIR="$ROOT_DIR/dist"
INSTALLER_DIR="$DIST_DIR/installers"

mkdir -p "$INSTALLER_DIR"

if [ -d "$DIST_DIR/priorityplot.app" ]; then
  SOURCE_PATH="$DIST_DIR/priorityplot.app"
else
  SOURCE_PATH="$DIST_DIR/priorityplot"
fi

hdiutil create -volname "PriorityPlot" -srcfolder "$SOURCE_PATH" \
  "$INSTALLER_DIR/priorityplot_${VERSION}_macos.dmg"
