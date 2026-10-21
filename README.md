# Comic-Battle

A terminal-based comic character battle simulator. Register, pick your avatar and teammates from a universe of DC/Marvel/Dark Horse characters, then let weighted powerstats decide the winner against an enemy team.

Built with Python + `pyfiglet`, `questionary`, `bcrypt`, `numpy`, `g4f`, and `alive-progress`.

## Features

- **Auth**: register/login with hashed passwords (`bcrypt`), stored in `data.json`
- **Character enlistment**: search and add characters via the Superhero API
- **Battle**: pick avatar + up to 5 teammates vs up to 5 enemies; weighted powerstat scoring declares a winner
- **Graffiti ASCII title** powered by a bundled `fonts/graffiti.flf` (not included with pyfiglet by default)

## Quick start

### One-liner (Linux / macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main/install.sh | bash
```

Then activate and run:

```bash
cd Comic-Battle
source .venv/bin/activate
python main.py
```

### One-liner (Windows PowerShell)

```powershell
Invoke-WebRequest -Uri https://raw.githubusercontent.com/moseswanjohi179/Comic-Battle/main/install.ps1 -OutFile install.ps1; ./install.ps1
```

Then activate and run:

```powershell
cd Comic-Battle
.venv\Scripts\activate
python main.py
```

### From a cloned repo

```bash
# Clone
git clone https://github.com/moseswanjohi179/Comic-Battle.git
cd Comic-Battle

# Run the installer (creates venv, installs deps, registers the graffiti font)
bash install.sh          # Linux/macOS
# .\install.ps1          # Windows PowerShell

# Activate and play
source .venv/bin/activate   # (Linux/macOS)
# .venv\Scripts\activate    # (Windows)
python main.py
```

## Manual install

```bash
python3 -m venv .venv
source .venv/bin/activate      # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -c "import pyfiglet; pyfiglet.FigletFont.installFonts('fonts/graffiti.flf')"
python main.py
```

## Installer flags (install.sh / install.ps1)

Both installers accept the same flags:

| Flag | Meaning |
|------|---------|
| `-h, --help` | Show help message |
| `-v, --version` | Show installer version |
| `-q, --quiet` | Suppress non-essential output |
| `-f, --force` | Recreate the virtualenv even if it exists |
| `-u, --update` | Re-download latest files from GitHub and re-install (upgrade) |
| `--no-progress` | Disable progress bars / spinners |

Example upgrade:
```bash
bash install.sh -u        # Linux/macOS
.\install.ps1 -Update     # Windows PowerShell
```

## Shortcut launcher

The installer creates a `comic-battle` script so you never have to manually activate the venv:

```bash
./comic-battle        # Linux/macOS + Git Bash
.\comic-battle.ps1    # Windows PowerShell
```

## Superhero API key

The enlistment feature needs a free key from [superheroapi.com](https://www.superheroapi.com/).

1. Run the game and choose **Enlist** → follow the first-time setup, or
2. Create `.env` in the repo root:
   ```
   SUPERHERO_API=your_key_here
   ```

`.env`, `data.json`, `characters.json`, `.hash_cache`, and `.venv/` are all gitignored — your personal data never leaves your machine.

## Project structure

```
Comic-Battle/
├── main.py            # Entry point: auth, lobby, play flow
├── engiene.py         # Lobby menu, battle scoring, banner rendering
├── character_manager.py   # Character publisher validation + AI power ranking
├── characters_main.py # Superhero API enlistment (search/add characters)
├── fonts/graffiti.flf # Bundled figlet font (not in pyfiglet by default)
├── install.sh         # Linux/macOS installer
├── install.ps1        # Windows PowerShell installer
├── comic-battle       # Shortcut launcher (created by installer)
├── comic-battle.ps1   # Shortcut launcher (created by installer)
├── requirements.txt   # Pinned Python dependencies
├── .env               # Your SUPERHERO_API key (gitignored)
├── .gitignore
└── LICENSE            # MIT
```

## License

MIT License. See [LICENSE](LICENSE).
