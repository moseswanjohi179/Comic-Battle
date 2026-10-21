<#
.SYNOPSIS
    Comic-Battle installer (Windows PowerShell)
.DESCRIPTION
    Creates a virtualenv, installs dependencies, registers the graffiti font,
    and creates launcher shortcuts. Works standalone or via one-liner.
.PARAMETER Help
    Show this help message
.PARAMETER Version
    Show installer version
.PARAMETER Quiet
    Suppress non-essential output
.PARAMETER Force
    Recreate the virtualenv even if it already exists
.PARAMETER NoProgress
    Disable progress spinners
.PARAMETER Update
    Re-download the latest files from GitHub and re-run install (upgrade)
#>
[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$Version,
    [switch]$Quiet,
    [switch]$Force,
    [switch]$NoProgress,
    [switch]$Update
)

$INSTALLER_VERSION = "1.0.0"
$RAW_BASE = "https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main"

if ($Help) {
    Write-Host @"
Comic-Battle installer v$INSTALLER_VERSION

Usage: .\install.ps1 [options]

Options:
  -Help        Show this help message
  -Version     Show installer version
  -Quiet       Suppress non-essential output
  -Force       Recreate the virtualenv even if it already exists
  -NoProgress  Disable progress spinners
  -Update      Re-download latest files from GitHub and re-install (upgrade)

Examples:
  .\install.ps1                    # Standard install from a cloned repo
  iex (iwr -Uri <raw install.ps1> -UseBasicParsing)  # One-line install
  .\install.ps1 -Force             # Force rebuild of the virtualenv
  .\install.ps1 -Update            # Upgrade to latest version

After install:
  .venv\Scripts\activate           # (Windows PowerShell)
  python main.py                   # Launch the game

  Or use the shortcut:
  .\comic-battle                   # Runs the game directly (no manual activate)
"@ -ForegroundColor Cyan
    exit 0
}

if ($Version) {
    Write-Host "Comic-Battle installer v$INSTALLER_VERSION" -ForegroundColor Cyan
    exit 0
}

$ErrorActionPreference = "Stop"

function Write-Log {
    if (-not $Quiet) { Write-Host "==> $args" -ForegroundColor Cyan }
}
function Write-Warn {
    Write-Host "[!] $args" -ForegroundColor Yellow
}
function Write-Err {
    Write-Host "[ERROR] $args" -ForegroundColor Red
    exit 1
}

$STEP_TOTAL = 7
$STEP_CURRENT = 0

function Step {
    $script:STEP_CURRENT++
    if (-not $NoProgress -and -not $Quiet) {
        $pct = [math]::Floor($script:STEP_CURRENT * 100 / $STEP_TOTAL)
        $filled = [math]::Floor(40 * $script:STEP_CURRENT / $STEP_TOTAL)
        $bar = "#" * $filled + "-" * (40 - $filled)
        Write-Host -NoNewline "`r[$bar] $pct% $args"
    } else {
        Write-Host "[$script:STEP_CURRENT/$STEP_TOTAL] $args"
    }
}

$spinnerJob = $null
function Start-Spin {
    if ($NoProgress -or $Quiet) { return }
    $msg = $args
    $sp = @("/", "-", "\", "|")
    $spinnerJob = Start-Job -ScriptBlock {
        param($msg, $sp)
        $i = 0
        while ($true) {
            $i = ($i + 1) % 4
            Write-Host -NoNewline "`r[$($sp[$i])] $msg"
            Start-Sleep -Milliseconds 100
        }
    } -ArgumentList $msg, $sp | Out-Null
}

function Stop-Spin {
    if ($spinnerJob) {
        Stop-Job $spinnerJob -ErrorAction SilentlyContinue
        Remove-Job $spinnerJob -ErrorAction SilentlyContinue
        $spinnerJob = $null
        Write-Host -NoNewline "`r"
    }
}

# --- Determine repo directory -------------------------------------------
$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# If -Update or running via one-liner without a cloned repo, download files
$needsDownload = $Update -or (-not (Test-Path (Join-Path $RepoDir "requirements.txt")))
if ($needsDownload) {
    if ($Update) {
        Write-Log "Update mode: downloading latest files from GitHub"
    }
    $TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ("ComicBattle_" + [System.IO.Path]::GetRandomFileName())
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $TmpDir "fonts") -Force | Out-Null

    Step "Downloading project files"
    try {
        Invoke-WebRequest -Uri "$RAW_BASE/requirements.txt" -OutFile (Join-Path $TmpDir "requirements.txt") -ErrorAction Stop
        Invoke-WebRequest -Uri "$RAW_BASE/fonts/graffiti.flf" -OutFile (Join-Path $TmpDir "fonts/graffiti.flf") -ErrorAction Stop
        Invoke-WebRequest -Uri "$RAW_BASE/main.py" -OutFile (Join-Path $TmpDir "main.py") -ErrorAction Stop
        Invoke-WebRequest -Uri "$RAW_BASE/engiene.py" -OutFile (Join-Path $TmpDir "engiene.py") -ErrorAction Stop
        Invoke-WebRequest -Uri "$RAW_BASE/character_manager.py" -OutFile (Join-Path $TmpDir "character_manager.py") -ErrorAction Stop
        Invoke-WebRequest -Uri "$RAW_BASE/characters_main.py" -OutFile (Join-Path $TmpDir "characters_main.py") -ErrorAction Stop
        Invoke-WebRequest -Uri "$RAW_BASE/LICENSE" -OutFile (Join-Path $TmpDir "LICENSE") -ErrorAction Stop
    } catch {
        Write-Err "Failed to download project files. Check your internet connection."
    }
    $RepoDir = $TmpDir
}

$Python = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { Write-Err "Python 3 not found. Install Python 3.10+ and re-run." }
$VenvDir = Join-Path $RepoDir ".venv"

Write-Log "Comic-Battle installer v$INSTALLER_VERSION"
Write-Log "Repo dir: $RepoDir"

# --- Step 1: Python ------------------------------------------------------
Step "Checking Python"
try {
    $PyVersion = & $Python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
    Write-Log "Using Python $PyVersion"
} catch {
    Write-Err "Cannot run $Python"
}

# --- Step 2: Virtualenv --------------------------------------------------
Step "Creating virtualenv"
if (Test-Path $VenvDir -and $Force) {
    Write-Log "Removing existing virtualenv (-Force)"
    Remove-Item $VenvDir -Recurse -Force
}
if (-not (Test-Path $VenvDir)) {
    Start-Spin "Creating virtualenv"
    try {
        & $Python -m venv $VenvDir | Out-Null
    } catch {
        Stop-Spin
        Write-Err "Failed to create virtualenv."
    }
    Stop-Spin
    Write-Log "Virtualenv created at $VenvDir"
} else {
    Write-Log "Virtualenv already exists (use -Force to rebuild)"
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = Join-Path $VenvDir "bin\python"
}
if (-not (Test-Path $VenvPython)) {
    Write-Err "Virtualenv python not found at $VenvPython"
}

# --- Step 3: Upgrade pip -------------------------------------------------
Step "Upgrading pip"
Start-Spin "Upgrading pip"
try {
    & $VenvPython -m pip install --upgrade pip -q | Out-Null
} catch {
    Stop-Spin
    Write-Warn "pip upgrade failed — continuing with existing pip"
}
Stop-Spin

# --- Step 4: Install dependencies ----------------------------------------
Step "Installing dependencies"
Start-Spin "Installing Python packages (this may take a minute)"
$PipLog = [System.IO.Path]::GetTempFileName()
try {
    & $VenvPython -m pip install -r (Join-Path $RepoDir "requirements.txt") > $PipLog 2>&1 | Out-Null
} catch {
    Stop-Spin
    Write-Err "Dependency install failed. Full log saved to: $PipLog"
}
Stop-Spin
Remove-Item $PipLog -ErrorAction SilentlyContinue
Write-Log "Dependencies installed"

# --- Step 5: Register graffiti font --------------------------------------
Step "Registering graffiti font"
$FontFile = Join-Path $RepoDir "fonts\graffiti.flf"
if (-not (Test-Path $FontFile)) {
    Write-Err "fonts/graffiti.flf not found in $RepoDir"
}
Start-Spin "Registering fonts/graffiti.flf with pyfiglet"
try {
    & $VenvPython - $FontFile <<'PY'
import sys, pyfiglet
pyfiglet.FigletFont.installFonts(sys.argv[1])
print("OK")
PY
} catch {
    Stop-Spin
    Write-Err "Failed to register graffiti font"
}
Stop-Spin
Write-Log "Graffiti font registered"

# --- Step 6: Create shortcut launchers -----------------------------------
Step "Creating shortcut launchers"
$PShellLauncher = @"
# Comic-Battle launcher (PowerShell) — runs the game without manually activating the venv
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $VenvPython = Join-Path $ScriptDir ".venv\bin\python"
}
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Virtualenv not found. Run install.ps1 first." -ForegroundColor Red
    exit 1
}
& $VenvPython (Join-Path $ScriptDir "main.py") @args
"@
$PShellLauncher | Set-Content -Path (Join-Path $RepoDir "comic-battle.ps1") -Encoding utf8NoBOM

# Bash-style launcher for Git Bash / WSL
$BashLauncher = @"
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="\$SCRIPT_DIR/.venv/Scripts/python.exe"
if [[ ! -x "\$VENV_PYTHON" ]]; then
  VENV_PYTHON="\$SCRIPT_DIR/.venv/bin/python"
fi
if [[ ! -x "\$VENV_PYTHON" ]]; then
  echo "[ERROR] Virtualenv not found. Run install.ps1 first." >&2
  exit 1
fi
exec "\$VENV_PYTHON" "\$SCRIPT_DIR/main.py" "\$@"
"@
$BashLauncher | Set-Content -Path (Join-Path $RepoDir "comic-battle") -Encoding utf8NoBOM

Write-Log "Shortcuts created: .\comic-battle  .\comic-battle.ps1"

# --- Step 7: Done + guidance ---------------------------------------------
Step "Installation complete"
Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Comic-Battle is installed!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Run the game:" -ForegroundColor Cyan
Write-Host "  .\comic-battle                 (shortcut — no manual activate needed)" -ForegroundColor Cyan
Write-Host "  # or:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\activate" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "First time?" -ForegroundColor Cyan
Write-Host "  1. Run .\comic-battle" -ForegroundColor Cyan
Write-Host "  2. Register a new account when prompted" -ForegroundColor Cyan
Write-Host "  3. Use 'Enlist' to add characters via the Superhero API" -ForegroundColor Cyan
Write-Host "  4. Get a free API key at https://www.superheroapi.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Need help?  .\comic-battle --help   |   .\install.ps1 -Help" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Green
