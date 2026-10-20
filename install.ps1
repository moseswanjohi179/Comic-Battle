<#
.SYNOPSIS
    Comic-Battle installer (Windows PowerShell)
.DESCRIPTION
    Creates a virtualenv, installs dependencies, and verifies the bundled graffiti font.
#>
$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Python = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { throw "Python 3 not found. Install Python 3.10+ and re-run." }
$VenvDir = Join-Path $RepoDir ".venv"

Write-Host "==> Comic-Battle installer" -ForegroundColor Cyan
Write-Host "==> Repo dir: $RepoDir" -ForegroundColor Cyan

Write-Host "==> Using Python: $Python"
$PyVersion = & $Python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
Write-Host "==> Python version: $PyVersion"

if (-not (Test-Path $VenvDir)) {
    Write-Host "==> Creating virtualenv at $VenvDir"
    & $Python -m venv $VenvDir
} else {
    Write-Host "==> Virtualenv already exists, skipping creation"
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = Join-Path $VenvDir "bin\python"
}

Write-Host "==> Installing dependencies from requirements.txt"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $RepoDir "requirements.txt")

Write-Host "==> Verifying graffiti font loads"
$FontFile = Join-Path $RepoDir "fonts\graffiti.flf"
& $VenvPython - $FontFile - <<'PY'
import sys, pyfiglet
pyfiglet.FigletFont.installFonts(sys.argv[1])
print("graffiti font registered:", "graffiti" in pyfiglet.FigletFont.getFonts())
PY


Write-Host ""
Write-Host "==> Installation complete!" -ForegroundColor Green
Write-Host "==> To run the game:" -ForegroundColor Green
Write-Host "    cd $RepoDir" -ForegroundColor Green
Write-Host "    .venv\Scripts\activate          (Windows PowerShell)" -ForegroundColor Green
Write-Host "    # source .venv/bin/activate     (Linux/macOS)" -ForegroundColor Green
Write-Host "    python main.py" -ForegroundColor Green
Write-Host ""
Write-Host "==> Personal data (.env, data.json, characters.json) is ignored by git" -ForegroundColor Green
