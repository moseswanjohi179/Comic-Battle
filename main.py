import argparse
import sys
import time

import bcrypt
import questionary

from engiene import banner, character_del, clear, load_json, lobby, play, save_json
from paths import DATA_FILE

VERSION = "1.1.0"


def show_help():
    print("""
Comic-Battle — Terminal comic character battle simulator

Usage:
  comic-battle              Start the game (interactive)
  comic-battle --help       Show this help message
  comic-battle --version    Show version

Game flow:
  1. Register or log in with a username + password (hashed with bcrypt)
  2. From the lobby: Play, Character Enlist, Reset Account, Log out or Exit
  3. Play: pick your avatar + up to 5 teammates vs up to 5 enemies
  4. Enlist: search the Superhero API and add characters to your roster

First time?
  - You'll need a free API key from https://www.superheroapi.com/ to enlist
  - Your key, accounts and roster are stored in ~/.comic-battle
    (set COMIC_BATTLE_HOME to use another folder)
""")


# --------------------------------------------------------------------------
# Accounts
# --------------------------------------------------------------------------
def load_users():
    data = load_json(DATA_FILE, {})
    return data if isinstance(data, dict) else {}


def _check_password(plain, stored_hash):
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def register():
    """Create an account. Returns the new user name, or None if cancelled."""
    clear()
    print(banner())
    users = load_users()
    taken = {u.get("user_name", "").lower() for u in users.values()}

    while True:
        name = questionary.text("\nWhat is Your Name ?").ask()
        if name is None:
            return None
        name = name.strip()
        if not name:
            print("Name cannot be empty.")
        elif name.lower() in taken:
            print("That name is already taken, pick another one.")
        else:
            break

    while True:
        password = questionary.password("\nSecure your account with a password: ").ask()
        if password is None:
            return None
        if len(password) < 4:
            print("Password must be at least 4 characters.")
            continue
        if len(password.encode("utf-8")) > 72:  # bcrypt hard limit
            print("Password is too long (72 bytes max).")
            continue
        again = questionary.password("Confirm password: ").ask()
        if again is None:
            return None
        if again != password:
            print("Passwords do not match, try again.")
            continue
        break

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    n = 0
    while f"profile_{n}" in users:
        n += 1
    users[f"profile_{n}"] = {"user_name": name, "password": hashed}
    save_json(DATA_FILE, users)
    return name


def login(users):
    """Returns the user name on success, otherwise None."""
    names = [u["user_name"] for u in users.values() if u.get("user_name")]
    if not names:
        print("No usable accounts found.")
        time.sleep(1.5)
        return None

    identity = questionary.select("\nPick Your Profile: ", choices=names).ask()
    if identity is None:
        return None
    record = next(u for u in users.values() if u.get("user_name") == identity)

    for _ in range(3):
        password = questionary.password("Enter Your Password: ").ask()
        if password is None:
            return None
        if _check_password(password, record.get("password", "")):
            return identity
        print("\n!!! Wrong Password !!!\n")
    time.sleep(1.5)
    return None


def authenticate():
    """Log in or register. Returns a user name, or None to quit."""
    while True:
        clear()
        print(banner())
        users = load_users()

        if not users:
            print("No accounts found - let's create one.\n")
            return register()

        choice = questionary.select(
            "\nWelcome!", choices=["Log in", "Register a new account", "Exit"]
        ).ask()
        if choice in (None, "Exit"):
            return None

        user = login(users) if choice == "Log in" else register()
        if user:
            return user


# --------------------------------------------------------------------------
# Main loop
# --------------------------------------------------------------------------
def enlist():
    from characters_main import mode  # lazy: pulls in g4f, which is slow to import

    mode()


def session(user):
    """Lobby loop for a logged-in user. Returns "logout", "reset" or "exit"."""
    while True:
        action = lobby(user)

        if action == "play":
            if play() == "enlist":
                enlist()
        elif action == "enlist":
            enlist()
        elif action == "reset":
            confirmed = questionary.confirm(
                "This permanently deletes your account. Continue?", default=False
            ).ask()
            if confirmed:
                character_del(user)
                print("\nAccount deleted.")
                time.sleep(1.5)
                return "reset"
        elif action == "logout":
            return "logout"
        else:
            return "exit"


def splash():
    if not sys.stdout.isatty():
        return
    from alive_progress import alive_bar

    with alive_bar(100, title="Loading Game: ") as bar:
        for _ in range(100):
            time.sleep(0.015)
            bar()


def run():
    splash()
    while True:
        user = authenticate()
        if user is None:
            break
        if session(user) == "exit":
            break
    clear()
    print("Goodbye!")


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-v", "--version", action="store_true")
    args, _ = parser.parse_known_args()

    if args.help:
        show_help()
        return
    if args.version:
        print(f"Comic-Battle v{VERSION}")
        return

    try:
        run()
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
