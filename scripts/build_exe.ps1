# Build Azkar.exe with PyInstaller. Run from anywhere; paths are resolved
# relative to the project root.
#
#   .\scripts\build_exe.ps1
#
$ErrorActionPreference = "Stop"

$root   = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$icon   = Join-Path $root "assets\icons\azkar.ico"
$entry  = Join-Path $root "launcher.py"

Push-Location $root
try {
    # Generate the .ico / sound if missing (best-effort).
    if (-not (Test-Path $icon)) {
        & $python (Join-Path $root "scripts\make_icon.py")
    }
    if (-not (Test-Path (Join-Path $root "assets\sounds\knock.wav"))) {
        & $python (Join-Path $root "scripts\make_sound.py")
    }

    $pyArgs = @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "Azkar",
        "--paths", "src",
        "--hidden-import", "windows_toasts",
        "--hidden-import", "hijridate",
        "--collect-submodules", "hijridate",
        "--add-data", "src/azkar/content/data;azkar/content/data",
        "--add-data", "assets;assets"
    )
    if (Test-Path $icon) { $pyArgs += @("--icon", $icon) }
    $pyArgs += $entry

    & $python @pyArgs
    Write-Host "`nBuilt: $(Join-Path $root 'dist\Azkar.exe')"
}
finally {
    Pop-Location
}
