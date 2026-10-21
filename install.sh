#!/usr/bin/env bash
#
# Comic-Battle installer
#   From a cloned repo:   bash install.sh
#   One-liner (curl):     curl -fsSL <raw install.sh> | bash
#
# Options:
#   -h, --help       Show this help message
#   -v, --version    Show installer version
#   -q, --quiet      Suppress non-essential output
#   -f, --force      Recreate the virtualenv even if it exists
#   --no-progress    Disable progress bars / spinners
#
set -uo pipefail

INSTALLER_VERSION="1.0.0"
RAW_BASE="https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main"

# --- CLI flags -----------------------------------------------------------
QUIET=0
FORCE=0
NO_PROGRESS=0
SHOW_HELP=0
SHOW_VERSION=0
UPDATE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) SHOW_HELP=1; shift ;;
    -v|--version) SHOW_VERSION=1; shift ;;
    -q|--quiet) QUIET=1; shift ;;
    -f|--force) FORCE=1; shift ;;
    --no-progress) NO_PROGRESS=1; shift ;;
    -u|--update) UPDATE=1; shift ;;
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
  -u, --update     Re-download latest files from GitHub and re-install (upgrade)
  --no-progress    Disable progress bars / spinners

Examples:
  bash install.sh                    # Standard install from a cloned repo
  curl -fsSL <raw install.sh> | bash # One-line install (downloads files first)
  bash install.sh -f                 # Force rebuild of the virtualenv

After install:
  source .venv/bin/activate          # (Linux/macOS)
  .venv\Scripts\activate             # (Windows)
  python main.py                     # Launch the game

  Or use the shortcut:
  ./comic-battle                     # Runs the game directly (no manual activate)
EOF
  exit 0
fi

if [[ "$SHOW_VERSION" -eq 1 ]]; then
  echo "Comic-Battle installer v$INSTALLER_VERSION"
  exit 0
fi

# --- Logging helpers -----------------------------------------------------
log()   { [[ "$QUIET" -eq 0 ]] && echo "==> $*"; }
warn()  { echo "[!] $*" >&2; }
err()   { echo "[ERROR] $*" >&2; exit 1; }

# --- Progress / step helpers --------------------------------------------
STEP_TOTAL=7
STEP_CURRENT=0

step() {
  STEP_CURRENT=$((STEP_CURRENT + 1))
  if [[ "$NO_PROGRESS" -eq 0 && "$QUIET" -eq 0 ]]; then
    local pct=$((STEP_CURRENT * 100 / STEP_TOTAL))
    local filled=$((40 * STEP_CURRENT / STEP_TOTAL))
    local bar=""
    for ((i=0;i<filled;i++)); do bar+="#"; done
    for ((i=filled;i<40;i++)); do bar+="-"; done
    printf "\r[%s] %d%% %s" "$bar" "$pct" "$1"
  else
    echo "[$STEP_CURRENT/$STEP_TOTAL] $1"
  fi
}

spinner_pid=""
start_spinner() {
  if [[ "$NO_PROGRESS" -eq 1 || "$QUIET" -eq 1 ]]; then return; fi
  local msg="$1"
  local i=0
  local sp="/-\|"
  (
    while true; do
      i=$(((i + 1) % 4))
      printf "\r[%c] %s" "${sp:$i:1}" "$msg"
      sleep 0.1
    done
  ) &
  spinner_pid=$!
}

stop_spinner() {
  if [[ -n "${spinner_pid:-}" ]]; then
    kill "$spinner_pid" 2>/dev/null || true
    wait "$spinner_pid" 2>/dev/null || true
    spinner_pid=""
    printf "\r"
  fi
}

# --- Determine repo directory -------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "$PWD")"

# Download files when: piped via curl (no requirements.txt present) OR --update
DOWNLOAD_FILES=0
if [[ ! -f "$SCRIPT_DIR/requirements.txt" ]]; then
  DOWNLOAD_FILES=1
elif [[ "$UPDATE" -eq 1 ]]; then
  DOWNLOAD_FILES=1
  log "Update mode: re-downloading latest files from GitHub"
fi

if [[ "$DOWNLOAD_FILES" -eq 1 ]]; then
  if [[ "$UPDATE" -eq 1 ]]; then
    # Update in place — download into the current repo dir
    DL_DIR="$SCRIPT_DIR"
    CLEANUP=0
  else
    # Piped via curl | bash — download to a temp dir
    DL_DIR="$(mktemp -d)"
    trap 'rm -rf "$DL_DIR"' EXIT
    CLEANUP=1
  fi
  mkdir -p "$DL_DIR/fonts"

  step "Downloading project files"
  for f in requirements.txt fonts/graffiti.flf main.py engiene.py character_manager.py characters_main.py LICENSE; do
    if ! curl -fsSL "$RAW_BASE/$f" -o "$DL_DIR/$f" 2>/dev/null; then
      err "Failed to download $f. Check your internet connection."
    fi
  done

  if [[ "$CLEANUP" -eq 1 ]]; then
    SCRIPT_DIR="$DL_DIR"
  fi
fi

REPO_DIR="$SCRIPT_DIR"
PYTHON="${PYTHON:-python3}"
VENV_DIR="$REPO_DIR/.venv"

log "Comic-Battle installer v$INSTALLER_VERSION"
log "Repo dir: $REPO_DIR"

# --- Step 1: Python ------------------------------------------------------
step "Checking Python"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  err "$PYTHON not found. Install Python 3.10+ and re-run."
fi
PY_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null) || err "Cannot run $PYTHON"
log "Using Python $PY_VERSION"

# --- Step 2: Virtualenv --------------------------------------------------
step "Creating virtualenv"
if [[ -d "$VENV_DIR" && "$FORCE" -eq 1 ]]; then
  log "Removing existing virtualenv (--force)"
  rm -rf "$VENV_DIR"
fi
if [[ ! -d "$VENV_DIR" ]]; then
  start_spinner "Creating virtualenv"
  if ! "$PYTHON" -m venv "$VENV_DIR" >/dev/null 2>&1; then
    stop_spinner
    err "Failed to create virtualenv."
  fi
  stop_spinner
  log "Virtualenv created at $VENV_DIR"
else
  log "Virtualenv already exists (use -f to rebuild)"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
fi
if [[ ! -x "$VENV_PYTHON" ]]; then
  err "Virtualenv python not found at $VENV_PYTHON"
fi

# --- Step 3: Upgrade pip -------------------------------------------------
step "Upgrading pip"
start_spinner "Upgrading pip"
if ! "$VENV_PYTHON" -m pip install --upgrade pip -q >/dev/null 2>&1; then
  stop_spinner
  warn "pip upgrade failed — continuing with existing pip"
else
  stop_spinner
fi

# --- Step 4: Install dependencies ----------------------------------------
step "Installing dependencies"
start_spinner "Installing Python packages (this may take a minute)"
PIP_LOG="$(mktemp)"
if ! "$VENV_PYTHON" -m pip install -r "$REPO_DIR/requirements.txt" >"$PIP_LOG" 2>&1; then
  stop_spinner
  err "Dependency install failed. Full log saved to: $PIP_LOG"
fi
stop_spinner
rm -f "$PIP_LOG"
log "Dependencies installed"

# --- Step 5: Register graffiti font --------------------------------------
step "Registering graffiti font"
FONT_FILE="$REPO_DIR/fonts/graffiti.flf"
if [[ ! -f "$FONT_FILE" ]]; then
  err "fonts/graffiti.flf not found in $REPO_DIR"
fi
start_spinner "Registering fonts/graffiti.flf with pyfiglet"
FONT_OUT="$("$VENV_PYTHON" - "$FONT_FILE" 2>&1 <<'PY'
import sys, pyfiglet
pyfiglet.FigletFont.installFonts(sys.argv[1])
print("OK")
PY
)" || { stop_spinner; err "Failed to register graffiti font"; }
stop_spinner
log "Graffiti font registered"

# --- Step 6: Create shortcut launcher ------------------------------------
step "Creating shortcut launcher"
cat > "$REPO_DIR/comic-battle" <<'LAUNCHER'
#!/usr/bin/env bash
# Comic-Battle launcher — runs the game without manually activating the venv
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON="$SCRIPT_DIR/.venv/Scripts/python.exe"
fi
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "[ERROR] Virtualenv not found. Run install.sh first." >&2
  exit 1
fi
exec "$VENV_PYTHON" "$SCRIPT_DIR/main.py" "$@"
LAUNCHER
chmod +x "$REPO_DIR/comic-battle"
log "Shortcut created: ./comic-battle"

# --- Step 7: Done + guidance ---------------------------------------------
step "Installation complete"
printf "\r"
echo
echo "=============================================="
echo "  Comic-Battle is installed!"
echo "=============================================="
echo
echo "Run the game:"
echo "  ./comic-battle                 (shortcut — no manual activate needed)"
echo "  # or:"
echo "  source .venv/bin/activate      # Linux/macOS"
echo "  # .venv\Scripts\activate       # Windows"
echo "  python main.py"
echo
echo "First time?"
echo "  1. Run ./comic-battle"
echo "  2. Register a new account when prompted"
echo "  3. Use 'Enlist' to add characters via the Superhero API"
echo "  4. Get a free API key at https://www.superheroapi.com/"
echo
echo "Need help?  ./comic-battle --help   |   bash install.sh --help"
echo "=============================================="
