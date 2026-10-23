<#
.SYNOPSIS
    Comic-Battle installer (Windows PowerShell)
.DESCRIPTION
    Downloads the game (or uses the cloned repo), creates a virtualenv,
    installs dependencies and creates a `comic-battle` command plus Desktop
    and Start Menu shortcuts.
.PARAMETER Help        Show help
.PARAMETER Version     Show installer version
.PARAMETER Quiet       Suppress non-essential output
.PARAMETER Force       Recreate the virtualenv
.PARAMETER NoProgress  Disable the progress bar
.PARAMETER Update      Re-download the latest files and re-install
.PARAMETER Uninstall   Remove the app and shortcuts (saves are kept)
#>
[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$Version,
    [switch]$Quiet,
    [switch]$Force,
    [switch]$NoProgress,
    [switch]$Update,
    [switch]$Uninstall
)

$INSTALLER_VERSION = "2.0.0"
$RAW_BASE = "https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main"
$RequiredFiles = @("requirements.txt", "fonts/graffiti.flf", "paths.py", "main.py", "engiene.py", "character_manager.py", "characters_main.py")
$OptionalFiles = @("install.ps1", "LICENSE", "README.md")

if ($Help) {
    Write-Host @"
Comic-Battle installer v$INSTALLER_VERSION

Usage: .\install.ps1 [options]

  -Help        Show this help message
  -Version     Show installer version
  -Quiet       Suppress non-essential output
  -Force       Recreate the virtualenv
  -Update      Re-download the latest files and re-install
  -Uninstall   Remove the app and shortcuts (your saves are kept)
  -NoProgress  Disable the progress bar

After install start the game with:  comic-battle
(or use the Desktop / Start Menu shortcut)
"@ -ForegroundColor Cyan
    return
}
if ($Version) { Write-Host "Comic-Battle installer v$INSTALLER_VERSION" -ForegroundColor Cyan; return }

$ErrorActionPreference = "Stop"
try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}

$OnWindows = ($PSVersionTable.PSVersion.Major -le 5) -or $IsWindows

function Write-Log  { param([string]$m) if (-not $Quiet) { Write-Host "==> $m" -ForegroundColor Cyan } }
function Write-Warn { param([string]$m) Write-Host "[!] $m" -ForegroundColor Yellow }
function Fail       { param([string]$m) Write-Host "[ERROR] $m" -ForegroundColor Red; exit 1 }

$StepTotal = 8
$StepCurrent = 0
function Step {
    param([string]$m)
    $script:StepCurrent++
    if ($Quiet) { return }
    if ($NoProgress) { Write-Host "[$script:StepCurrent/$StepTotal] $m"; return }
    Write-Progress -Activity "Installing Comic-Battle" -Status $m -PercentComplete ([math]::Floor($script:StepCurrent * 100 / $StepTotal))
}

# Run a native command without PowerShell turning stderr into exceptions.
function Invoke-Native {
    param([string]$Exe, [string[]]$Arguments)
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $out = & $Exe @Arguments 2>&1 | Out-String
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $old }
    [pscustomobject]@{ Output = $out; ExitCode = $code }
}

# --- Locations -----------------------------------------------------------
$LocalDir = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "requirements.txt")) -and (Test-Path (Join-Path $PSScriptRoot "main.py"))) {
    $LocalDir = $PSScriptRoot
}
if ($LocalDir) { $InstallDir = $LocalDir }
elseif ($env:COMIC_BATTLE_DIR) { $InstallDir = $env:COMIC_BATTLE_DIR }
elseif ($env:LOCALAPPDATA) { $InstallDir = Join-Path $env:LOCALAPPDATA "Comic-Battle" }
else { $InstallDir = Join-Path $HOME ".local/share/comic-battle" }

$DataHome = if ($env:COMIC_BATTLE_HOME) { $env:COMIC_BATTLE_HOME } else { Join-Path $HOME ".comic-battle" }
$DesktopLnk = $null; $StartLnk = $null
if ($OnWindows) {
    $DesktopLnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "Comic-Battle.lnk"
    $StartLnk = Join-Path ([Environment]::GetFolderPath("Programs")) "Comic-Battle.lnk"
}

function Remove-FromUserPath {
    param([string]$Dir)
    $path = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $path) { return }
    $parts = $path.Split(";") | Where-Object { $_ -and ($_.TrimEnd("\") -ne $Dir.TrimEnd("\")) }
    [Environment]::SetEnvironmentVariable("Path", ($parts -join ";"), "User")
}

# --- Uninstall -----------------------------------------------------------
if ($Uninstall) {
    Write-Log "Removing shortcuts and command"
    foreach ($f in @($DesktopLnk, $StartLnk)) { if ($f -and (Test-Path $f)) { Remove-Item $f -Force } }
    if ($OnWindows) { Remove-FromUserPath $InstallDir }
    if ($LocalDir) {
        foreach ($n in @(".venv", "comic-battle.cmd", "comic-battle.ps1")) {
            $p = Join-Path $InstallDir $n
            if (Test-Path $p) { Remove-Item $p -Recurse -Force }
        }
    } elseif ($InstallDir -and (Test-Path $InstallDir)) {
        Remove-Item $InstallDir -Recurse -Force
    }
    Write-Host "Comic-Battle removed. Your accounts and roster were kept in: $DataHome" -ForegroundColor Green
    return
}

# --- Step 1: project files -----------------------------------------------
function Get-ProjectFile {
    param([string]$Rel, [bool]$Required)
    $dest = Join-Path $InstallDir ($Rel -replace "/", [IO.Path]::DirectorySeparatorChar)
    New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
    $lastErr = ""
    foreach ($attempt in 1..3) {
        try {
            Invoke-WebRequest -Uri "$RAW_BASE/$Rel" -OutFile $dest -UseBasicParsing -ErrorAction Stop
            return
        } catch { $lastErr = $_.Exception.Message; Start-Sleep -Seconds 1 }
    }
    if ($Required) { Fail "Could not download '$Rel' ($lastErr). Check your internet connection. URL: $RAW_BASE/$Rel" }
    else { Write-Warn "Optional file '$Rel' could not be downloaded - skipping." }
}

Step "Preparing project files"
if ((-not $LocalDir) -or $Update) {
    if ($Update) { Write-Log "Update mode: downloading the latest files" }
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    foreach ($f in $RequiredFiles) { Get-ProjectFile $f $true }
    foreach ($f in $OptionalFiles) { Get-ProjectFile $f $false }
}
$VenvDir = Join-Path $InstallDir ".venv"
Write-Log "Comic-Battle installer v$INSTALLER_VERSION"
Write-Log "Install dir: $InstallDir"

# --- Step 2: Python ------------------------------------------------------
Step "Checking Python"
$PyExe = $null; $PyPrefix = @()
foreach ($cand in @(@("py", "-3"), @("python"), @("python3"))) {
    if (-not (Get-Command $cand[0] -ErrorAction SilentlyContinue)) { continue }
    $extra = @(); if ($cand.Count -gt 1) { $extra = $cand[1..($cand.Count - 1)] }
    $r = Invoke-Native $cand[0] ($extra + @("-c", "import sys; print(sys.version_info[0]*100+sys.version_info[1])"))
    if ($r.ExitCode -eq 0 -and ($r.Output.Trim() -match '^\d+$') -and ([int]$r.Output.Trim() -ge 310)) {
        $PyExe = $cand[0]; $PyPrefix = $extra; break
    }
}
if (-not $PyExe) { Fail "Python 3.10+ was not found. Install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH') and re-run." }
Write-Log "Using $PyExe $($PyPrefix -join ' ')"

# --- Step 3: virtualenv --------------------------------------------------
Step "Creating virtualenv"
if ((Test-Path $VenvDir) -and $Force) { Write-Log "Removing existing virtualenv (-Force)"; Remove-Item $VenvDir -Recurse -Force }
if (-not (Test-Path $VenvDir)) {
    $r = Invoke-Native $PyExe ($PyPrefix + @("-m", "venv", $VenvDir))
    if ($r.ExitCode -ne 0) { if (Test-Path $VenvDir) { Remove-Item $VenvDir -Recurse -Force }; Fail "Failed to create the virtualenv.`n$($r.Output)" }
    Write-Log "Virtualenv created"
} else { Write-Log "Virtualenv already exists (use -Force to rebuild)" }

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) { $VenvPython = Join-Path $VenvDir "bin/python" }
if (-not (Test-Path $VenvPython)) { Fail "Virtualenv python not found in $VenvDir (try -Force)" }

# --- Step 4/5: pip + dependencies ----------------------------------------
Step "Upgrading pip"
$r = Invoke-Native $VenvPython @("-m", "pip", "install", "--upgrade", "pip", "-q")
if ($r.ExitCode -ne 0) { Write-Warn "pip upgrade failed - continuing with the existing pip" }

Step "Installing dependencies (this may take a few minutes)"
$r = Invoke-Native $VenvPython @("-m", "pip", "install", "-r", (Join-Path $InstallDir "requirements.txt"))
if ($r.ExitCode -ne 0) { Write-Host $r.Output; Fail "Dependency install failed (see output above)." }
Write-Log "Dependencies installed"

# --- Step 6: graffiti font (optional) --------------------------------------
Step "Registering graffiti font"
$FontFile = Join-Path $InstallDir "fonts\graffiti.flf"
if (Test-Path $FontFile) {
    $fontPy = Join-Path ([IO.Path]::GetTempPath()) "cb_font.py"
    @'
import os, shutil, sys, pyfiglet
src = sys.argv[1]
def ok():
    try:
        pyfiglet.figlet_format("x", font="graffiti"); return True
    except Exception:
        return False
if not ok():
    try: pyfiglet.FigletFont.installFonts(src)
    except Exception: pass
if not ok():
    base = os.path.dirname(pyfiglet.__file__)
    for sub in ("fonts-contrib", "fonts-standard", "fonts"):
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            shutil.copy(src, d); break
sys.exit(0 if ok() else 1)
'@ | Set-Content -Path $fontPy -Encoding ASCII
    $r = Invoke-Native $VenvPython @($fontPy, $FontFile)
    Remove-Item $fontPy -ErrorAction SilentlyContinue
    if ($r.ExitCode -eq 0) { Write-Log "Graffiti font registered" }
    else { Write-Warn "Could not register the graffiti font - the game will use the standard title font." }
} else { Write-Warn "fonts\graffiti.flf missing - the game will use the standard title font." }

# --- Step 7: launchers + shortcuts -----------------------------------------
Step "Creating shortcuts"
$CmdLauncher = Join-Path $InstallDir "comic-battle.cmd"
@"
@echo off
"$VenvPython" "$InstallDir\main.py" %*
if errorlevel 1 pause
"@ | Set-Content -Path $CmdLauncher -Encoding ASCII

$PsLauncher = Join-Path $InstallDir "comic-battle.ps1"
@"
& "$VenvPython" "$InstallDir\main.py" @args
"@ | Set-Content -Path $PsLauncher -Encoding ASCII

$PathNote = ""
if ($OnWindows) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not $userPath -or -not (($userPath.Split(";") | ForEach-Object { $_.TrimEnd("\") }) -contains $InstallDir.TrimEnd("\"))) {
        [Environment]::SetEnvironmentVariable("Path", ((@($userPath, $InstallDir) | Where-Object { $_ }) -join ";"), "User")
        $PathNote = "Open a NEW terminal window so the 'comic-battle' command is found."
    }
    try {
        $shell = New-Object -ComObject WScript.Shell
        foreach ($lnk in @($DesktopLnk, $StartLnk)) {
            $s = $shell.CreateShortcut($lnk)
            $s.TargetPath = $CmdLauncher
            $s.WorkingDirectory = $InstallDir
            $s.Description = "Comic-Battle - terminal comic character battle simulator"
            $s.Save()
        }
        Write-Log "Desktop and Start Menu shortcuts created"
    } catch { Write-Warn "Could not create shortcuts: $($_.Exception.Message)" }
}

# --- Step 8: done ----------------------------------------------------------
Step "Installation complete"
Write-Progress -Activity "Installing Comic-Battle" -Completed
Write-Host ""
Write-Host "==============================================" -ForegroundColor Green
Write-Host "  Comic-Battle is installed!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Start the game:" -ForegroundColor Cyan
Write-Host "  comic-battle                 (from any terminal)" -ForegroundColor Cyan
Write-Host "  or use the Desktop / Start Menu shortcut" -ForegroundColor Cyan
if ($PathNote) { Write-Host "  NOTE: $PathNote" -ForegroundColor Yellow }
Write-Host ""
Write-Host "First time?" -ForegroundColor Cyan
Write-Host "  1. Register a new account when prompted" -ForegroundColor Cyan
Write-Host "  2. Use 'Character Enlist' to add characters via the Superhero API" -ForegroundColor Cyan
Write-Host "  3. Get a free API key at https://www.superheroapi.com/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your saves live in: $DataHome" -ForegroundColor Cyan
Write-Host "Upgrade: .\install.ps1 -Update   |   Remove: .\install.ps1 -Uninstall" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Green
