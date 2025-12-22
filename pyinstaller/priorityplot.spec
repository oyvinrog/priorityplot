# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path.cwd()
if not (project_root / "run_app.py").exists():
    if (project_root / "pyinstaller").exists():
        project_root = project_root
    else:
        project_root = project_root.parent

datas = []
datas += collect_data_files("matplotlib")

hiddenimports = []
hiddenimports += collect_submodules("matplotlib")

block_cipher = None

a = Analysis(
    [str(project_root / "run_app.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="priorityplot",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
