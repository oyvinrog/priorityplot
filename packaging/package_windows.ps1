$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

$version = & python "$rootDir\\bump_version.py"
$distDir = Join-Path $rootDir "dist"
$installerDir = Join-Path $distDir "installers"
$inputDir = if (Test-Path (Join-Path $distDir "priorityplot")) { Join-Path $distDir "priorityplot" } else { $distDir }

New-Item -ItemType Directory -Force $installerDir | Out-Null

$outFile = Join-Path $installerDir ("PriorityPlot_{0}.exe" -f $version)

$nsisPath = Join-Path ${env:ProgramFiles(x86)} "NSIS\\makensis.exe"
if (-not (Test-Path $nsisPath)) {
  $nsisPath = Join-Path $env:ProgramFiles "NSIS\\makensis.exe"
}
if (-not (Test-Path $nsisPath)) {
  $nsisPath = (Get-Command makensis -ErrorAction SilentlyContinue).Source
}
if (-not $nsisPath) {
  throw "NSIS not found. Install NSIS or ensure makensis is on PATH."
}

& $nsisPath /DVERSION=$version /DINPUT_DIR="$inputDir" /DOUTFILE="$outFile" "$rootDir\\packaging\\windows\\priorityplot.nsi"
