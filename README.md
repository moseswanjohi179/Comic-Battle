# Comic-Battle

A terminal-based comic character battle simulator. Register, pick your avatar and teammates from a universe of DC/Marvel/Dark Horse characters, then let weighted powerstats decide the winner against an enemy team.

Built with Python + `pyfiglet`, `questionary`, `bcrypt`, `g4f`, and `alive-progress`.

## Install

### Linux / macOS (one line)

```bash
curl -fsSL https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main/install.sh | bash
```

This installs into `~/.local/share/comic-battle`, adds a **`comic-battle`** command to `~/.local/bin` (and your PATH if needed) and creates an application-menu / desktop shortcut. Then just run:

```bash
comic-battle
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -Command "iwr https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main/install.ps1 -OutFile $env:TEMP\cb-install.ps1; & $env:TEMP\cb-install.ps1"
```

Installs into `%LOCALAPPDATA%\Comic-Battle`, adds `comic-battle` to your PATH and creates Desktop + Start Menu shortcuts.

### From a cloned repo

```bash
git clone https://github.com/moseswanjohi179/Comic-Battle.git
cd Comic-Battle
bash install.sh          # Linux/macOS      (.\install.ps1 on Windows)
comic-battle
```

Requires Python 3.10+ (on Debian/Ubuntu/Parrot: `sudo apt install python3 python3-venv python3-pip`).

### Installer flags (install.sh / install.ps1)

| install.sh | install.ps1 | Meaning |
|------|------|---------|
| `-h, --help` | `-Help` | Show help |
| `-v, --version` | `-Version` | Show installer version |
| `-q, --quiet` | `-Quiet` | Suppress non-essential output |
| `-f, --force` | `-Force` | Recreate the virtualenv |
| `-u, --update` | `-Update` | Re-download the latest files and re-install |
| `--uninstall` | `-Uninstall` | Remove the app + shortcuts (saves are kept) |
| `--no-progress` | `-NoProgress` | Disable progress bars / spinners |

## Manual install

```bash
python3 -m venv .venv
source .venv/bin/activate      # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

## Superhero API key

The enlistment feature needs a free key from [superheroapi.com](https://www.superheroapi.com/). Choose **Character Enlist** in the lobby and the game asks for it once and stores it locally. An invalid key is detected and re-requested automatically.

## Where your data lives

Accounts, your roster and your API key are stored in `~/.comic-battle` (`%USERPROFILE%\.comic-battle` on Windows), independent of where the game is installed or launched from, so updating never touches them. Set `COMIC_BATTLE_HOME` to use another folder. Nothing in there is ever committed to this repo.

## How a battle works

Each fighter's score is a weighted sum of their powerstats (intelligence 15%, strength 10%, speed 20%, durability 15%, power 10%, combat 30%). A team's score is the **average** of its fighters, so squad size can't decide a fight. Newly enlisted characters are calibrated once by an AI (strength / durability / power relative to the strongest character; the original API numbers are kept as `powerstats_original`).

## Project structure

```
Comic-Battle/
├── main.py                # Entry point: accounts, lobby loop
├── engiene.py             # Lobby menu, battle scoring, shared helpers
├── character_manager.py   # One-time AI calibration of new characters
├── characters_main.py     # Superhero API enlistment (search/add characters)
├── paths.py               # Where user data is stored
├── fonts/graffiti.flf     # Bundled figlet font
├── install.sh             # Linux/macOS installer
├── install.ps1            # Windows installer
├── requirements.txt
└── LICENSE                # MIT
```

## License

MIT License. See [LICENSE](LICENSE).
