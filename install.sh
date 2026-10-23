#!/usr/bin/env bash
#
# Comic-Battle installer (Linux / macOS / Git Bash)
#
#   One-liner:   curl -fsSL https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main/install.sh | bash
#   From clone:  bash install.sh
#
# One-liner installs go to ~/.local/share/comic-battle (override with COMIC_BATTLE_DIR).
# A "comic-battle" command is added to ~/.local/bin plus an application-menu
# / desktop shortcut, so you can launch the game like any other program.
#
set -uo pipefail

INSTALLER_VERSION="2.0.0"
RAW_BASE="https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main"
REQUIRED_FILES=(requirements.txt fonts/graffiti.flf paths.py main.py engiene.py character_manager.py characters_main.py)
OPTIONAL_FILES=(install.sh LICENSE README.md)

QUIET=0; FORCE=0; NO_PROGRESS=0; SHOW_HELP=0; SHOW_VERSION=0; UPDATE=0; UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) SHOW_HELP=1; shift ;;
    -v|--version) SHOW_VERSION=1; shift ;;
    -q|--quiet) QUIET=1; shift ;;
    -f|--force) FORCE=1; shift ;;
    -u|--update) UPDATE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --no-progress) NO_PROGRESS=1; shift ;;
    *) echo "Unknown option: $1" >&2; echo "Run 'install.sh --help' for usage." >&2; exit 2 ;;
  esac
done

if [[ "$SHOW_HELP" -eq 1 ]]; then
  cat <<EOF
Comic-Battle installer v$INSTALLER_VERSION

Usage: bash install.sh [options]

Options:
  -h, --help       Show this help message
  -v, --version    Show installer version
  -q, --quiet      Suppress non-essential output
  -f, --force      Recreate the virtualenv even if it already exists
  -u, --update     Re-download the latest files from GitHub and re-install
  --uninstall      Remove the app, command and shortcuts (your saves are kept)
  --no-progress    Disable progress bars / spinners

Examples:
  curl -fsSL $RAW_BASE/install.sh | bash   # one-line install
  bash install.sh                          # install from a cloned repo
  bash install.sh -u                       # upgrade to the latest version

After install, start the game with:   comic-battle
(or from your application menu / desktop shortcut)
EOF
  exit 0
fi

if [[ "$SHOW_VERSION" -eq 1 ]]; then
  echo "Comic-Battle installer v$INSTALLER_VERSION"
  exit 0
fi

# --- Terminal helpers ----------------------------------------------------
if [[ -t 1 ]]; then CLR=$'\r\033[K'; IS_TTY=1; else CLR=""; IS_TTY=0; fi
FANCY=0
[[ "$IS_TTY" -eq 1 && "$NO_PROGRESS" -eq 0 && "$QUIET" -eq 0 ]] && FANCY=1

spinner_pid=""
stop_spinner() {
  if [[ -n "${spinner_pid:-}" ]]; then
    kill "$spinner_pid" 2>/dev/null || true
    wait "$spinner_pid" 2>/dev/null || true
    spinner_pid=""
    printf '%s' "$CLR"
  fi
}
start_spinner() {
  [[ "$FANCY" -eq 1 ]] || return 0
  local msg="$1"
  (
    local i=0 sp='/-\|'
    while true; do
      i=$(((i + 1) % 4))
      printf '\r[%s] %s' "${sp:$i:1}" "$msg"
      sleep 0.1
    done
  ) &
  spinner_pid=$!
}
trap 'stop_spinner' EXIT
trap 'stop_spinner; echo; exit 130' INT TERM

log()  { stop_spinner; [[ "$QUIET" -eq 0 ]] && echo "${CLR}==> $*"; return 0; }
warn() { stop_spinner; echo "${CLR}[!] $*" >&2; }
err()  { stop_spinner; echo "${CLR}[ERROR] $*" >&2; exit 1; }

STEP_TOTAL=8
STEP_CURRENT=0
step() {
  STEP_CURRENT=$((STEP_CURRENT + 1))
  if [[ "$FANCY" -eq 1 ]]; then
    local pct=$((STEP_CURRENT * 100 / STEP_TOTAL))
    local filled=$((40 * STEP_CURRENT / STEP_TOTAL))
    local bar="" i
    for ((i=0;i<filled;i++)); do bar+="#"; done
    for ((i=filled;i<40;i++)); do bar+="-"; done
    printf '%s[%s] %d%% %s' "$CLR" "$bar" "$pct" "$1"
  elif [[ "$QUIET" -eq 0 ]]; then
    echo "[$STEP_CURRENT/$STEP_TOTAL] $1"
  fi
}

# --- Locations -----------------------------------------------------------
# "Local" mode = running install.sh from a cloned repo. Otherwise (curl | bash)
# the files are downloaded into a permanent folder - NOT a temp dir.
LOCAL_DIR=""
SRC="${BASH_SOURCE[0]:-}"
if [[ -n "$SRC" && -f "$SRC" ]]; then
  cand="$(cd "$(dirname "$SRC")" 2>/dev/null && pwd)"
  if [[ -n "$cand" && -f "$cand/requirements.txt" && -f "$cand/main.py" ]]; then
    LOCAL_DIR="$cand"
  fi
fi

if [[ -n "$LOCAL_DIR" ]]; then
  INSTALL_DIR="$LOCAL_DIR"
else
  INSTALL_DIR="${COMIC_BATTLE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/comic-battle}"
fi

BIN_DIR="$HOME/.local/bin"
APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DATA_HOME="${COMIC_BATTLE_HOME:-$HOME/.comic-battle}"
DESKTOP_DIR=""
if command -v xdg-user-dir >/dev/null 2>&1; then DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || true)"; fi
[[ -z "$DESKTOP_DIR" ]] && DESKTOP_DIR="$HOME/Desktop"

# --- Uninstall -----------------------------------------------------------
if [[ "$UNINSTALL" -eq 1 ]]; then
  log "Removing command and shortcuts"
  rm -f "$BIN_DIR/comic-battle" "$APPS_DIR/comic-battle.desktop" \
        "$DESKTOP_DIR/Comic-Battle.desktop" "$DESKTOP_DIR/Comic-Battle.command"
  if [[ -n "$LOCAL_DIR" ]]; then
    rm -rf "$INSTALL_DIR/.venv" "$INSTALL_DIR/comic-battle"
  elif [[ -n "$INSTALL_DIR" && "$INSTALL_DIR" != "/" && "$INSTALL_DIR" != "$HOME" ]]; then
    rm -rf "$INSTALL_DIR"
  fi
  echo "Comic-Battle removed. Your accounts and roster were kept in: $DATA_HOME"
  echo "(delete that folder if you want them gone too)"
  exit 0
fi

# --- Step 1: get the project files ---------------------------------------
command -v curl >/dev/null 2>&1 || [[ -n "$LOCAL_DIR" && "$UPDATE" -eq 0 ]] || err "curl is required. Install it (e.g. 'sudo apt install curl') and re-run."

fetch() {  # fetch <relative path> <required: 1|0>
  local f="$1" required="$2" dest="$INSTALL_DIR/$1" tmp why attempt
  mkdir -p "$(dirname "$dest")" || err "Cannot create $(dirname "$dest")"
  tmp="$(mktemp)"
  for attempt in 1 2 3; do
    if curl -fsSL --connect-timeout 15 "$RAW_BASE/$f" -o "$tmp" 2>"$tmp.err"; then
      mv -f "$tmp" "$dest"; chmod 644 "$dest"; rm -f "$tmp.err"
      return 0
    fi
    sleep 1
  done
  why="$(tr '\n' ' ' <"$tmp.err" 2>/dev/null)"
  rm -f "$tmp" "$tmp.err"
  if [[ "$required" -eq 1 ]]; then
    err "Could not download '$f' (${why:-no details}). Check your internet connection. URL: $RAW_BASE/$f"
  else
    warn "Optional file '$f' could not be downloaded - skipping."
  fi
}

step "Preparing project files"
if [[ -z "$LOCAL_DIR" || "$UPDATE" -eq 1 ]]; then
  [[ "$UPDATE" -eq 1 ]] && log "Update mode: downloading the latest files"
  mkdir -p "$INSTALL_DIR/fonts" || err "Cannot create $INSTALL_DIR"
  for f in "${REQUIRED_FILES[@]}"; do fetch "$f" 1; done
  for f in "${OPTIONAL_FILES[@]}"; do fetch "$f" 0; done
fi

REPO_DIR="$INSTALL_DIR"
VENV_DIR="$REPO_DIR/.venv"
log "Comic-Battle installer v$INSTALLER_VERSION"
log "Install dir: $REPO_DIR"

# --- Step 2: Python ------------------------------------------------------
step "Checking Python"
PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PYTHON="$cand"; break
    fi
  done
fi
[[ -n "$PYTHON" ]] || err "Python 3.10 or newer was not found. Install it (e.g. 'sudo apt install python3 python3-venv python3-pip') and re-run."
PY_VERSION="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)" || err "Cannot run $PYTHON"
log "Using Python $PY_VERSION"

# --- Step 3: Virtualenv --------------------------------------------------
step "Creating virtualenv"
if [[ -d "$VENV_DIR" && "$FORCE" -eq 1 ]]; then
  log "Removing existing virtualenv (--force)"
  rm -rf "$VENV_DIR"
fi
if [[ ! -d "$VENV_DIR" ]]; then
  start_spinner "Creating virtualenv"
  VENV_LOG="$("$PYTHON" -m venv "$VENV_DIR" 2>&1)" || {
    rm -rf "$VENV_DIR"
    err "Failed to create the virtualenv. On Debian/Ubuntu/Parrot run: sudo apt install python3-venv python3-pip
$VENV_LOG"
  }
  stop_spinner
  log "Virtualenv created"
else
  log "Virtualenv already exists (use -f to rebuild)"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
[[ -x "$VENV_PYTHON" ]] || VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
[[ -x "$VENV_PYTHON" ]] || err "Virtualenv python not found in $VENV_DIR (try --force)"

# --- Step 4: pip ---------------------------------------------------------
step "Upgrading pip"
start_spinner "Upgrading pip"
"$VENV_PYTHON" -m pip install --upgrade pip -q >/dev/null 2>&1 || warn "pip upgrade failed - continuing with the existing pip"
stop_spinner

# --- Step 5: dependencies ------------------------------------------------
step "Installing dependencies"
start_spinner "Installing Python packages (this may take a few minutes)"
PIP_LOG="$(mktemp)"
if ! "$VENV_PYTHON" -m pip install -r "$REPO_DIR/requirements.txt" >"$PIP_LOG" 2>&1; then
  stop_spinner
  tail -n 15 "$PIP_LOG" >&2
  err "Dependency install failed. Full log: $PIP_LOG"
fi
stop_spinner
rm -f "$PIP_LOG"
log "Dependencies installed"

# --- Step 6: graffiti font (optional - the game falls back to a standard font)
step "Registering graffiti font"
FONT_FILE="$REPO_DIR/fonts/graffiti.flf"
if [[ -f "$FONT_FILE" ]]; then
  if "$VENV_PYTHON" - "$FONT_FILE" >/dev/null 2>&1 <<'PY'
import os, shutil, sys, pyfiglet
src = sys.argv[1]
try:
    pyfiglet.figlet_format("x", font="graffiti")
    sys.exit(0)
except Exception:
    pass
try:
    pyfiglet.FigletFont.installFonts(src)
except Exception:
    pass
try:
    pyfiglet.figlet_format("x", font="graffiti")
    sys.exit(0)
except Exception:
    pass
base = os.path.dirname(pyfiglet.__file__)
for sub in ("fonts-contrib", "fonts-standard", "fonts"):
    d = os.path.join(base, sub)
    if os.path.isdir(d):
        shutil.copy(src, d)
        break
pyfiglet.figlet_format("x", font="graffiti")
PY
  then
    log "Graffiti font registered"
  else
    warn "Could not register the graffiti font - the game will use the standard title font."
  fi
else
  warn "fonts/graffiti.flf missing - the game will use the standard title font."
fi

# --- Step 7: launcher + shortcuts ----------------------------------------
step "Creating shortcuts"
LAUNCHER="$REPO_DIR/comic-battle"
cat > "$LAUNCHER" <<LAUNCHER_EOF
#!/usr/bin/env bash
# Comic-Battle launcher - runs the game without activating the venv by hand
APP_DIR="$REPO_DIR"
PY="\$APP_DIR/.venv/bin/python"
[[ -x "\$PY" ]] || PY="\$APP_DIR/.venv/Scripts/python.exe"
if [[ ! -x "\$PY" ]]; then
  echo "[ERROR] Comic-Battle is not installed correctly. Re-run install.sh" >&2
  exit 1
fi
exec "\$PY" "\$APP_DIR/main.py" "\$@"
LAUNCHER_EOF
chmod +x "$LAUNCHER"

SHORTCUT_NOTE=""
mkdir -p "$BIN_DIR" && cp -f "$LAUNCHER" "$BIN_DIR/comic-battle" && chmod +x "$BIN_DIR/comic-battle"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  case "${SHELL:-}" in *zsh) RC="$HOME/.zshrc" ;; *) RC="$HOME/.bashrc" ;; esac
  PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
  if ! grep -qsF "$PATH_LINE" "$RC" 2>/dev/null; then
    printf '\n# Added by Comic-Battle installer\n%s\n' "$PATH_LINE" >> "$RC"
  fi
  SHORTCUT_NOTE="Open a new terminal (or run: source $RC) so the 'comic-battle' command is found."
fi

case "$(uname -s)" in
  Darwin)
    if [[ -d "$HOME/Desktop" ]]; then
      printf '#!/usr/bin/env bash\nexec "%s"\n' "$BIN_DIR/comic-battle" > "$HOME/Desktop/Comic-Battle.command"
      chmod +x "$HOME/Desktop/Comic-Battle.command"
    fi
    ;;
  Linux)
    mkdir -p "$APPS_DIR"
    cat > "$APPS_DIR/comic-battle.desktop" <<DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=Comic-Battle
Comment=Terminal comic character battle simulator
Exec="$BIN_DIR/comic-battle"
Icon=utilities-terminal
Terminal=true
Categories=Game;
DESKTOP_EOF
    chmod +x "$APPS_DIR/comic-battle.desktop"
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
    if [[ -d "$DESKTOP_DIR" ]]; then
      cp -f "$APPS_DIR/comic-battle.desktop" "$DESKTOP_DIR/Comic-Battle.desktop" && chmod +x "$DESKTOP_DIR/Comic-Battle.desktop"
      command -v gio >/dev/null 2>&1 && gio set "$DESKTOP_DIR/Comic-Battle.desktop" metadata::trusted true >/dev/null 2>&1 || true
    fi
    ;;
esac
log "Shortcuts created"

# --- Step 8: done ----------------------------------------------------------
step "Installation complete"
stop_spinner
printf '%s' "$CLR"
echo
echo "=============================================="
echo "  Comic-Battle is installed!"
echo "=============================================="
echo
echo "Start the game:"
echo "  comic-battle                  (from any terminal)"
echo "  or open 'Comic-Battle' from your application menu / desktop"
[[ -n "$SHORTCUT_NOTE" ]] && { echo; echo "  NOTE: $SHORTCUT_NOTE"; echo "  Until then you can run: $BIN_DIR/comic-battle"; }
echo
echo "First time?"
echo "  1. Register a new account when prompted"
echo "  2. Use 'Character Enlist' to add characters via the Superhero API"
echo "  3. Get a free API key at https://www.superheroapi.com/"
echo
echo "Your saves live in: $DATA_HOME"
echo "Upgrade later:  bash \"$REPO_DIR/install.sh\" -u   |   Remove:  bash \"$REPO_DIR/install.sh\" --uninstall"
echo "=============================================="
