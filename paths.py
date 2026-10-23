"""Shared file locations.

User data (accounts, roster, API key) lives in a per-user folder instead of the
current directory, so the game behaves the same no matter where it is launched
from and updating/reinstalling never touches your saves.

Override the location with the COMIC_BATTLE_HOME environment variable.
"""
import os
import shutil
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("COMIC_BATTLE_HOME") or (Path.home() / ".comic-battle"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "data.json"
CHARACTERS_FILE = DATA_DIR / "characters.json"
ENV_FILE = DATA_DIR / ".env"
APEX_FILE = DATA_DIR / "apex.json"


def _migrate_legacy_files():
    """Copy saves created by older versions (stored next to the code / in the cwd)."""
    for name in ("data.json", "characters.json"):
        target = DATA_DIR / name
        if target.exists():
            continue
        for base in (APP_DIR, Path.cwd()):
            old = base / name
            if old.is_file():
                try:
                    shutil.copy2(old, target)
                except OSError:
                    pass
                break


_migrate_legacy_files()
