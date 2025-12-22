#!/usr/bin/env python3
"""
Update version strings across project files.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


VERSION_FILES = {
    Path("pyproject.toml"): re.compile(r'^(version\s*=\s*")([^"]+)(")\s*$'),
    Path("priorityplot/__init__.py"): re.compile(r'^(__version__\s*=\s*")([^"]+)(")\s*$'),
}


def update_file(path: Path, pattern: re.Pattern[str], new_version: str) -> None:
    original = path.read_text(encoding="utf-8").splitlines()
    updated = []
    replaced = False

    for line in original:
        match = pattern.match(line)
        if match:
            updated.append(f"{match.group(1)}{new_version}{match.group(3)}")
            replaced = True
        else:
            updated.append(line)

    if not replaced:
        raise RuntimeError(f"Version string not found in {path}")

    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump project version.")
    parser.add_argument("version", help="New version (e.g. 0.1.3)")
    args = parser.parse_args()

    for path, pattern in VERSION_FILES.items():
        if not path.exists():
            raise SystemExit(f"Missing file: {path}")
        update_file(path, pattern, args.version)

    print(f"Updated version to {args.version}")


if __name__ == "__main__":
    main()
