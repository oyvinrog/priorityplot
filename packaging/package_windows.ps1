$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

$version = & python "$rootDir\\bump_version.py"
$distDir = Join-Path $rootDir "dist"
$installerDir = Join-Path $distDir "installers"
$inputDir = if (Test-Path (Join-Path $distDir "priorityplot")) { Join-Path $distDir "priorityplot" } else { $distDir }

New-Item -ItemType Directory -Force $installerDir | Out-Null

$outFile = Join-Path $installerDir ("PriorityPlot_{0}.exe" -f $version)

& makensis /DVERSION=$version /DINPUT_DIR="$inputDir" /DOUTFILE="$outFile" "$rootDir\\packaging\\windows\\priorityplot.nsi"
