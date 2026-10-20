import json
import os
import time
import g4f
import pyfiglet
import questionary
import numpy as np


def banner(text="Battle_Game"):
    """Render ASCII title using the graffiti font, with fallbacks."""
    for font in ("graffiti", "standard"):
        try:
            return pyfiglet.figlet_format(text, font=font)
        except Exception:
            continue
    return text

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
    print(banner())

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
    print(banner())

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
    if avatar is None:
        return
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


    # -- 5. Fight Calculation ---



    Weights = np.array([0.15, 0.10, 0.20, 0.15, 0.10, 0.30])

    # Hero Team Calculation
    total_output = np.zeros(6)
    team.append(avatar)
    for each_name in team:
        for character in data.values():
            if character.get("name") == each_name:
                stats = character.get("powerstats", {})
                stat_vals = [
                    float(v) if v != "null" else 0.0 for v in stats.values()
                ]
                total_output += Weights * np.array(stat_vals)

    hero_score = np.sum(total_output)

    # Enemy Team Calculation
    total_enemy_output = np.zeros(6)
    for each_name in enemy_team:
        for character in data.values():
            if character.get("name") == each_name:
                stats = character.get("powerstats", {})
                stat_vals = [
                    float(v) if v != "null" else 0.0 for v in stats.values()
                ]
                total_enemy_output += Weights * np.array(stat_vals)

    enemy_score = np.sum(total_enemy_output)

    # Output Scores
    print(f"Hero Score: {hero_score:.2f}")
    print(f"Enemy Score: {enemy_score:.2f}")

    # Comparison
    if hero_score > enemy_score:
        print("Result: Winner - Hero Team")
    elif enemy_score > hero_score:
        print("Result: Winner - Enemy Team")
    else:
        print("Result: Tie")

    def exiting():
        while True:
            move_on = questionary.confirm("\nExit?").ask()
            if move_on != False:
                return
            time.sleep(10)
    exiting()




if __name__ == "__main__":
    play()






