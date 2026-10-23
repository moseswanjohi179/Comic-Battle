import json
import os

import pyfiglet
import questionary

from paths import CHARACTERS_FILE, DATA_FILE

# Weights for each Superhero-API powerstat (they sum to 1.0).
STAT_WEIGHTS = {
    "intelligence": 0.15,
    "strength": 0.10,
    "speed": 0.20,
    "durability": 0.15,
    "power": 0.10,
    "combat": 0.30,
}


# --------------------------------------------------------------------------
# Small helpers shared by every module
# --------------------------------------------------------------------------
def banner(text="Battle_Game"):
    """Render ASCII title using the graffiti font, with fallbacks."""
    for font in ("graffiti", "standard"):
        try:
            return pyfiglet.figlet_format(text, font=font)
        except Exception:
            continue
    return text


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def to_num(value, default=0.0):
    """Convert API values such as "85", 85, "null", None or "" to a float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {} if default is None else default


def save_json(path, data):
    """Write atomically so a crash can never leave a half-written save file."""
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, path)


def pause(message="Press any key to continue..."):
    try:
        questionary.press_any_key_to_continue(message).ask()
    except Exception:
        try:
            input(f"\n{message} (Enter) ")
        except EOFError:
            pass


# --------------------------------------------------------------------------
# Accounts
# --------------------------------------------------------------------------
def character_del(identity):
    """Delete the account called `identity` from data.json."""
    data = load_json(DATA_FILE, {})
    data = {k: v for k, v in data.items() if v.get("user_name") != identity}
    save_json(DATA_FILE, data)


def lobby(name):
    clear()
    print(banner())
    selection = questionary.select(
        f"\n---Options---  (logged in as {name})\n",
        choices=["Play", "Character Enlist", "Reset Account", "Log out", "Exit"],
    ).ask()

    return {
        "Play": "play",
        "Character Enlist": "enlist",
        "Reset Account": "reset",
        "Log out": "logout",
    }.get(selection, "exit")


# --------------------------------------------------------------------------
# Battle
# --------------------------------------------------------------------------
def fighter_score(info):
    stats = info.get("powerstats") or {}
    return sum(weight * to_num(stats.get(stat)) for stat, weight in STAT_WEIGHTS.items())


def team_score(ids, characters):
    """Average weighted score per fighter, so squad size can't decide a fight."""
    scores = [fighter_score(characters[c]) for c in ids if c in characters]
    return sum(scores) / len(scores) if scores else 0.0


def _universe_of(info):
    return (info.get("biography") or {}).get("publisher") or "Other"


def _choices(characters, ids):
    """Build menu choices keyed by character ID (names are not unique)."""
    counts = {}
    for cid in ids:
        name = characters[cid].get("name", "Unknown")
        counts[name] = counts.get(name, 0) + 1
    choices = []
    for cid in ids:
        name = characters[cid].get("name", "Unknown")
        title = f"{name} (ID {cid})" if counts[name] > 1 else name
        choices.append(questionary.Choice(title=title, value=cid))
    return sorted(choices, key=lambda c: c.title.lower())


def _pick_team(message, choices, minimum=1, maximum=5):
    while True:
        picked = questionary.checkbox(message, choices=choices).ask()
        if picked is None:
            return None
        if minimum <= len(picked) <= maximum:
            return picked
        print(f"\n[!] Please select between {minimum} and {maximum}.\n")


def play():
    """Run one battle. Returns "enlist" if the player should add characters first."""
    clear()
    print(banner())

    raw = load_json(CHARACTERS_FILE, {})
    characters = {
        cid: info
        for cid, info in raw.items()
        if isinstance(info, dict) and info.get("name")
    }

    if not characters:
        print("\n!! The Character Register is Empty !!\n")
        if questionary.confirm("Enlist characters now?").ask():
            return "enlist"
        return None

    universes = sorted({_universe_of(info) for info in characters.values()})

    # 1. Player universe + avatar
    universe = questionary.select("\nSelect Your Universe:\n", choices=universes).ask()
    if universe is None:
        return None
    pool = [cid for cid, info in characters.items() if _universe_of(info) == universe]

    avatar = questionary.select("Select Your Avatar", choices=_choices(characters, pool)).ask()
    if avatar is None:
        return None

    # 2. Teammates
    mates_pool = [cid for cid in pool if cid != avatar]
    team = []
    if not mates_pool:
        print("\nNo other characters available in this universe for teammates.")
        if questionary.confirm("Enlist characters?").ask():
            return "enlist"
    else:
        team = _pick_team("Pick 1 to 5 Team Mates:", _choices(characters, mates_pool))
        if team is None:
            return None

    # 3. Enemy universe + enemy team (never the same fighter on both sides)
    enemy_universe = questionary.select(
        "\nSelect The Enemy's Universe:\n", choices=universes
    ).ask()
    if enemy_universe is None:
        return None

    taken = {avatar, *team}
    enemy_pool = [
        cid
        for cid, info in characters.items()
        if _universe_of(info) == enemy_universe and cid not in taken
    ]
    if not enemy_pool:
        print("\nThere are no available enemy characters in this universe.")
        if questionary.confirm("Enlist characters?").ask():
            return "enlist"
        return None

    enemy_team = _pick_team("Pick 1 to 5 Enemies:", _choices(characters, enemy_pool))
    if enemy_team is None:
        return None

    # 4. Fight
    hero_ids = [avatar] + team
    hero_score = team_score(hero_ids, characters)
    enemy_score = team_score(enemy_team, characters)

    def names(ids):
        return ", ".join(characters[c]["name"] for c in ids)

    print(f"\nHero Team  : {names(hero_ids)}")
    print(f"Enemy Team : {names(enemy_team)}\n")
    print(f"Hero Score: {hero_score:.2f}")
    print(f"Enemy Score: {enemy_score:.2f}")

    if hero_score > enemy_score:
        print("Result: Winner - Hero Team")
    elif enemy_score > hero_score:
        print("Result: Winner - Enemy Team")
    else:
        print("Result: Tie")

    print()
    pause("Press any key to return to the lobby...")
    return None


if __name__ == "__main__":
    play()
