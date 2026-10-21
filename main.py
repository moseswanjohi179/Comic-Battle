import os
import json
import sys
import argparse
import pyfiglet
import questionary
import time
import getpass
from engiene import lobby, banner
from alive_progress import alive_bar
import bcrypt


def show_help():
    print("""
Comic-Battle — Terminal comic character battle simulator

Usage:
  python main.py           Start the game (interactive)
  python main.py --help    Show this help message
  python main.py --version Show version

Game flow:
  1. Register or log in with a username + password (hashed with bcrypt)
  2. From the lobby: Play, Reset, Character Enlist, or Exit
  3. Play: pick your avatar + up to 5 teammates vs up to 5 enemies
  4. Enlist: search the Superhero API and add characters to your roster

First time?
  - You'll need a free API key from https://www.superheroapi.com/ to enlist
  - The key is stored in .env (gitignored — never uploaded)
  - Your account data is saved in data.json (gitignored — never uploaded)

Shortcut:
  ./comic-battle   # Runs the game without manually activating the venv
""")


def show_version():
    print("Comic-Battle v1.0.0")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-v", "--version", action="store_true")
    args, _ = parser.parse_known_args()

    if args.help:
        show_help()
        sys.exit(0)
    if args.version:
        show_version()
        sys.exit(0)

print("""

""")
with alive_bar(100, title="Loading Game: ") as bar:
    for i in range(100):
        time.sleep(0.03)
        bar()


def storage_function():
    try:
        with open("data.json","r") as file:
            data = json.load(file)

    except(json.JSONDecodeError, FileNotFoundError):
        data = {}

    n = 0

    while f"profile_{n}" in data.keys():
        n = n + 1
    else:
        x = f"profile_{n}"
        data[x] = {"user_name":user_name,"password":hashed}
        with open("data.json","w") as file:
            json.dump(data, file, indent=4)


def regstration():
    os.system('cls' if os.name == 'nt' else 'clear'); print(banner())
    global user_name
    global hashed

    user_name = questionary.text("\nWhat is Your Name ?").ask()
    security = questionary.password("\nSecure your account with a password: ").ask()
    bytes_pw = security.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes_pw, salt).decode('utf-8')
    storage_function()


def introduction():
    os.system('cls' if os.name == 'nt' else 'clear'); print(banner())
    from engiene import character_del, play
    answer = questionary.confirm("Are you new here?").ask()
    if answer == True:
        regstration()
        action = lobby(user_name)
        if action == "Reset":
            character_del(user_name)
            regstration()
        elif action == "log out":
            introduction()
        elif action == "Enlist":
            from characters_main import mode
            mode()
        elif action == "play":
            play()
            lobby(user_name)
    else:
        try:
            with open("data.json","r") as file:
                    data = json.load(file)

            profiles = []
            for info in data.values():
                profiles.append(info["user_name"])

            identity = questionary.select("\nPick Your Profile: ", choices = profiles).ask()
            pass_confirm = getpass.getpass("Enter Your Password: ")
            bytes_entered = pass_confirm.encode('utf-8')

            for x in data.values():
                if x["user_name"] == identity:
                    possibility = x["password"]

            if bcrypt.checkpw(bytes_entered, possibility.encode('utf-8')):
                def lobby_handle():
                    action = lobby(identity)
                    if action == "Reset":
                        character_del(identity)
                        regstration()

                    elif action == "exit":
                        introduction()

                    elif action == "Enlist":
                        from characters_main import mode
                        mode()

                    elif action == "play":
                        enlist = play()
                        if enlist == "character_enlist":
                            from characters_main import mode
                            mode()
                            try:
                                lobby_handle()
                            except:
                                print("!!Error..Please Restart!!")
                                exit()

                        else:
                            try:
                                lobby_handle()
                            except:
                                print("!!Error..Please Restart!!")
                                exit()
                lobby_handle()
            else:
                print("\n!!!Wrong Password!!!!!\n")
                time.sleep(2)
                introduction()
        except(json.JSONDecodeError, FileNotFoundError):
            print("No user data found please Register.")
            regstration()
