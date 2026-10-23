import json
import os
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

import questionary
from dotenv import load_dotenv, set_key, unset_key

from character_manager import update_characters
from engiene import banner, clear, load_json, pause, save_json
from paths import CHARACTERS_FILE, ENV_FILE

API_BASE = "https://superheroapi.com/api"


class ApiError(Exception):
    pass


class InvalidKey(ApiError):
    pass


# --------------------------------------------------------------------------
# API key
# --------------------------------------------------------------------------
def initialize_api_key():
    ENV_FILE.touch(exist_ok=True)
    load_dotenv(ENV_FILE, override=True)
    api_key = (os.getenv("SUPERHERO_API") or "").strip()
    if api_key:
        return api_key

    print("\n--- First Time Setup ---\n")
    if questionary.confirm("Would you like help acquiring a SUPERHERO_API key if you don't have one?").ask():
        print("Opening browser (https://www.superheroapi.com/) ...")
        webbrowser.open("https://www.superheroapi.com/")

    while True:
        api_key = (questionary.password("Enter your API Key:").ask() or "").strip()
        if api_key:
            break
        print("API Key cannot be empty.")

    set_key(str(ENV_FILE), "SUPERHERO_API", api_key)
    try:
        os.chmod(ENV_FILE, 0o600)
    except OSError:
        pass
    os.environ["SUPERHERO_API"] = api_key
    print("API Key saved.\n")
    return api_key


def forget_api_key():
    try:
        unset_key(str(ENV_FILE), "SUPERHERO_API")
    except Exception:
        pass
    os.environ.pop("SUPERHERO_API", None)


def api_get(token, path):
    url = f"{API_BASE}/{urllib.parse.quote(token, safe='')}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ApiError("Could not reach the server. Check your internet connection.")
    except json.JSONDecodeError:
        raise ApiError("The server sent an unreadable response.")

    if payload.get("response") == "error":
        message = str(payload.get("error", "unknown error"))
        if "token" in message.lower():
            raise InvalidKey(message)
        raise ApiError(message)
    return payload


# --------------------------------------------------------------------------
# Character display / roster
# --------------------------------------------------------------------------
def print_profile(hero):
    bio = hero.get("biography") or {}
    app = hero.get("appearance") or {}
    stats = hero.get("powerstats") or {}
    aliases = bio.get("aliases") or []
    if isinstance(aliases, str):
        aliases = [aliases]

    print("\n" + "=" * 40)
    print(f"  CHARACTER PROFILE: {str(hero.get('name', '?')).upper()} (ID: {hero.get('id')})")
    print("=" * 40)
    print("\n BIOGRAPHY:")
    print(f"  • Real Name : {bio.get('full-name') or 'Unknown'}")
    print(f"  • Publisher : {bio.get('publisher') or 'Unknown'}")
    print(f"  • Alignment : {str(bio.get('alignment') or 'unknown').upper()}")
    print(f"  • Aliases   : {', '.join(aliases)}")
    print("\n APPEARANCE:")
    print(f"  • Gender    : {app.get('gender')}")
    print(f"  • Race      : {app.get('race')}")
    print("\n POWERSTATS:")
    for label in ("Intelligence", "Strength", "Speed", "Durability", "Power", "Combat"):
        print(f"  • {label:<13}: {stats.get(label.lower())} / 100")
    print("=" * 40 + "\n")


def add_to_roster(hero):
    cid = str(hero.get("id"))
    data = load_json(CHARACTERS_FILE, {})
    if cid in data:
        print("\n!!CHARACTER ALREADY REGISTERED!!\n")
    else:
        data[cid] = hero
        save_json(CHARACTERS_FILE, data)
        print(f"\n{hero.get('name')} added to your roster.\n")
        update_characters()  # only calibrates the new character(s)
    pause()


def character_menu(hero):
    while True:
        clear()
        print(banner())
        print(f"Selected: {hero.get('name')} (ID {hero.get('id')})")
        option = questionary.select(
            "\n--options--\n", choices=["Details", "Add to Character List", "See image", "Back"]
        ).ask()

        if option in (None, "Back"):
            return
        if option == "Details":
            clear()
            print_profile(hero)
            pause()
        elif option == "See image":
            url = (hero.get("image") or {}).get("url")
            if url:
                print("\nOpening browser please wait....\n")
                webbrowser.open(url)
            else:
                print("\nNo image available for this character.\n")
            pause()
        elif option == "Add to Character List":
            add_to_roster(hero)


# --------------------------------------------------------------------------
# Search modes
# --------------------------------------------------------------------------
def search_by_name(token):
    clear()
    print(banner())
    keyword = (questionary.text("Enter a name Key word:").ask() or "").strip()
    if not keyword:
        return

    results = api_get(token, f"search/{urllib.parse.quote(keyword)}").get("results") or []
    if not results:
        print("\n\t!!That Character Could Not Be Identified!!")
        pause()
        return

    choices = [
        questionary.Choice(
            title=f"{h.get('name')} - {(h.get('biography') or {}).get('publisher') or 'Unknown'} (ID {h.get('id')})",
            value=h,
        )
        for h in results
    ]
    choices.append(questionary.Choice(title="Back", value=None))
    hero = questionary.select("\n--Results--\n", choices=choices).ask()
    if hero:
        character_menu(hero)


def search_by_id(token):
    clear()
    print(banner())
    reason = questionary.select(
        "\nDo you know the character's ID or would you like to look at the online ID list?\n",
        choices=["I know the ID", "I need the online ID list"],
    ).ask()
    if reason is None:
        return
    if reason == "I need the online ID list":
        webbrowser.open("https://www.superheroapi.com/ids.html")
        print("Opening the browser please wait......")

    character_id = (questionary.text("\nEnter the character ID: ").ask() or "").strip()
    if not character_id.isdigit():
        print("\nThe ID must be a number.")
        pause()
        return

    character_menu(api_get(token, character_id))


def mode():
    update_characters()  # finish calibrating anything left over from earlier
    token = initialize_api_key()

    while True:
        clear()
        print(banner())
        choice = questionary.select(
            "Mode", choices=["Search by Name", "Search by ID", "Back"]
        ).ask()
        if choice in (None, "Back"):
            return

        try:
            if choice == "Search by Name":
                search_by_name(token)
            else:
                search_by_id(token)
        except InvalidKey:
            print("\n[!] The Superhero API rejected your key. Please enter it again.")
            forget_api_key()
            token = initialize_api_key()
        except ApiError as e:
            print(f"\n[API Error]: {e}")
            pause()


if __name__ == "__main__":
    mode()
