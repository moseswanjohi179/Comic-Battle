#!/usr/bin/env bash
# Comic-Battle installer
# Sets up a virtualenv, installs dependencies, and verifies the bundled graffiti font.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
VENV_DIR="$REPO_DIR/.venv"

echo "==> Comic-Battle installer"
echo "==> Repo dir: $REPO_DIR"

# 1. Python availability
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Error: $PYTHON not found. Install Python 3.10+ and try again."
  exit 1
fi
PY_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "==> Using Python $PY_VERSION"

# 2. Create virtualenv
if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtualenv at $VENV_DIR"
  "$PYTHON" -m venv "$VENV_DIR"
else
  echo "==> Virtualenv already exists, skipping creation"
fi

# 3. Install dependencies
VENV_PYTHON="$VENV_DIR/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
  # macOS/Windows-style layout fallback
  VENV_PYTHON="$VENV_DIR/Scripts/python.exe"
fi

echo "==> Installing dependencies from requirements.txt"
"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r "$REPO_DIR/requirements.txt"

# 4. Register the graffiti font with pyfiglet (it isn't bundled by default)
echo "==> Registering graffiti font with pyfiglet"
FONT_FILE="$REPO_DIR/fonts/graffiti.flf"
"$VENV_PYTHON" - "$FONT_FILE" <<'PY'
import sys, pyfiglet
font_file = sys.argv[1]
pyfiglet.FigletFont.installFonts(font_file)
print("graffiti font registered:", "graffiti" in pyfiglet.FigletFont.getFonts())
PY

# 5. Verify the graffiti font loads
echo "==> Verifying graffiti font loads"
"$VENV_PYTHON" - <<'PY'
import pyfiglet
try:
    print(pyfiglet.figlet_format("Battle_Game", font="graffiti").splitlines()[0])
    print("graffiti font loads OK")
except Exception as e:
    print("WARNING: graffiti font not available, falling back to standard font:", e)
PY

# 6. Done
echo
echo "==> Installation complete!"
echo "==> To run the game:"
echo "    cd $REPO_DIR"
echo "    source .venv/bin/activate      (Linux/macOS)"
echo "    # or .venv\\Scripts\\activate   (Windows)"
echo "    python main.py"
echo
echo "==> Personal data (.env, data.json, characters.json) is ignored by git"
