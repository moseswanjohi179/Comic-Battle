import json
import os
import time
import g4f
import pyfiglet
import questionary


def character_del(identity):
    try:
        with open("data.json", "r") as file:
            data = json.load(file)

        # Filter out keys belonging to the user
        data = {
            key: val
            for key, val in data.items()
            if val.get("user_name") != identity
        }

        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        print("data.json not found.")


def lobby(name):
    os.system("cls" if os.name == "nt" else "clear")
    print(pyfiglet.figlet_format("Battle_Game", font="graffiti"))

    selection = questionary.select(
        "\n---Options---\n",
        choices=["Play", "Reset", "Character Enlist", "Exit"],
    ).ask()

    if selection == "Play":
        return "play"
    elif selection == "Reset":
        return "Reset"
    elif selection == "Character Enlist":
        return "Enlist"
    else:
        return "log out"


def play():
    os.system("cls" if os.name == "nt" else "clear")
    print(pyfiglet.figlet_format("Battle_Game", font="graffiti"))

    try:
        with open("characters.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("!! characters.json file not found !!")
        return

    # Extract available publishers/universes
    character_register = list(
        {
            char_info.get("biography", {}).get("publisher")
            for char_info in data.values()
            if char_info.get("biography", {}).get("publisher")
        }
    )

    if not character_register:
        print("!! The Character Register is Empty !!")
        if questionary.confirm("Would You Like To Quit?").ask():
            return
        return "character_enlist"

    # --- 1. Player Universe & Avatar Selection ---
    universe = questionary.select(
        "\nSelect Your Universe:\n", choices=character_register
    ).ask()

    player_universe_list = [
        char_info["name"]
        for char_info in data.values()
        if char_info.get("biography", {}).get("publisher") == universe
    ]

    avatar = questionary.select(
        "Select Your Avatar", choices=player_universe_list
    ).ask()
    player_universe_list.remove(avatar)

    # --- 2. Teammate Selection ---
    if not player_universe_list:
        print("\nNo other characters available in this universe for teammates.")
        if questionary.confirm("Enlist characters?").ask():
            return "character_enlist"
        team = []
    else:
        while True:
            team = questionary.checkbox(
                "Pick A Maximum of Five Team Mates:",
                choices=player_universe_list,
            ).ask()

            if team is None:  # User cancelled prompt
                return

            if 1 <= len(team) <= 5:
                break
            print("\n[!] Please select between 1 and 5 teammates.\n")

    # --- 3. Enemy Universe Selection ---
    enemy_universe = questionary.select(
        "\nSelect The Enemy's Universe:\n", choices=character_register
    ).ask()

    if enemy_universe == universe:
        # Exclude selected avatar & teammates from available enemies
        excluded = set([avatar] + team)
        available_enemies = [
            char_info["name"]
            for char_info in data.values()
            if char_info.get("biography", {}).get("publisher") == enemy_universe
            and char_info["name"] not in excluded
        ]
    else:
        available_enemies = [
            char_info["name"]
            for char_info in data.values()
            if char_info.get("biography", {}).get("publisher") == enemy_universe
        ]

    # --- 4. Enemy Team Selection ---
    if not available_enemies:
        print("\nThere are no available enemy characters in this universe.")
        if questionary.confirm("Enlist characters?").ask():
            return "character_enlist"
        return

    while True:
        enemy_team = questionary.checkbox(
            "Pick 1 to 5 Enemies:", choices=available_enemies
        ).ask()

        if enemy_team is None:  # User cancelled prompt
            return

        if 1 <= len(enemy_team) <= 5:
            break
        print("\n[!] Please select between 1 and 5 enemies.\n")

    print("\n--- Battle Setup Complete ---")
    print(f"Avatar: {avatar}")
    print(f"Teammates: {team}")
    print(f"Enemies: {enemy_team}")


if __name__ == "__main__":
    play()
