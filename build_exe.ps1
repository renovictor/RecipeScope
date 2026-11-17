param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

if ($Clean) {
    if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
    if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }
}

$exeName = python -c "from version import get_executable_name; print(get_executable_name())"
if (-not $exeName) {
    throw "Failed to resolve executable name from version.py"
}

$exeBase = [System.IO.Path]::GetFileNameWithoutExtension($exeName.Trim())

$buildArgs = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", $exeBase,
    "--icon", ".\assets\recipescope.ico",
    "--add-data", ".\assets\sample_recipe.json;assets",
    "--add-data", ".\assets\ASM-logo-small.gif;assets",
    "--add-data", ".\assets\recipescope.ico;assets",
    ".\main.py"
)

$pyInstallerByModule = python -m PyInstaller --version 2>$null
if ($LASTEXITCODE -eq 0) {
    python -m PyInstaller @buildArgs
}
else {
    $pyinstallerCmd = Get-Command pyinstaller -ErrorAction SilentlyContinue
    if ($null -ne $pyinstallerCmd) {
        pyinstaller @buildArgs
    }
    else {
        throw "PyInstaller is not installed. Run: python -m pip install pyinstaller"
    }
}

$outputPath = Join-Path ".\dist" $exeName.Trim()
if (-not (Test-Path $outputPath)) {
    throw "Build failed: expected output not found at $outputPath"
}

Write-Host "Build complete: $outputPath"
