#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python -m PyInstaller --noconfirm --clean \
  --distpath dist \
  --workpath build/pyinstaller \
  pyinstaller/priorityplot.spec
