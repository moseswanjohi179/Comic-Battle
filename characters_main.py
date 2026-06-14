import json
import urllib.request
import questionary
import os
import webbrowser
import getpass
import time
from dotenv import load_dotenv, set_key

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "characters.json")

ENV_FILE = ".env"

def initialize_api_key():
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            pass   

    load_dotenv(ENV_FILE)
    api_key = os.getenv("SUPERHERO_API")

    if not api_key:
        print("--- First Time Setup ---")
        user_input = getpass.getpass("Enter your API Key: ").strip()
        
        if not user_input:
            raise ValueError("API Key cannot be empty.")
        set_key(ENV_FILE, "SUPERHERO_API", user_input)
        print("API Key saved successfully to .env!\n")
        
        
        load_dotenv(ENV_FILE)
        api_key = os.getenv("SUPERHERO_API")

    return api_key


def mode():
    
        access_token = initialize_api_key()
        access_token = access_token.strip()
        choice = questionary.select("Mode", choices=["Search by ID","Search by Name"]).ask()
        if choice == "Search by Name":
            hero_name = questionary.text("Enter a name Key word:").ask()
            
    
            url = f"https://superheroapi.com/api/{access_token}/search/{hero_name}"
            
        
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            try:
                response = urllib.request.urlopen(req)
                raw_response = response.read()
                decoded_response = raw_response.decode("utf-8") 
                hero_archive = json.loads(decoded_response)


            except urllib.error.URLError as e:
                print("\n[Network Error]: Could not reach the server.")
                print("Please check your internet connection and verify the URL.")
                exit()



            character_list = {}

            hero_list = hero_archive.get("results", [])

            for hero in hero_list:
                character_name = hero.get("name")
                character_id = hero.get("id")
                character_list[character_id] = character_name


            choose = questionary.select("\n--Results--\n", choices=list(character_list.values())).ask()

            for x in list(character_list.values()):
                if choose == x:
                    option = questionary.select("\n--options--\n",choices=["Details","Add to Character List","see image"]).ask()
                    if option == "Details":
                        for x in hero_list:
                            if x.get("name") == choose:
                                
                                            
                                stats = x.get("powerstats", {})
                                bio = x.get("biography", {})
                                app = x.get("appearance", {})
                                            
                                            
                                print("\n" + "="*40)
                                print(f"  CHARACTER PROFILE: {x.get('name').upper()} (ID: {x.get('id')})")
                                print("="*40)
                                            
                                print("\n BIOGRAPHY:")
                                print(f"  • Real Name : {bio.get('full-name') if bio.get('full-name') else 'Unknown'}")
                                print(f"  • Publisher : {bio.get('publisher')}")
                                print(f"  • Alignment : {bio.get('alignment').upper()}")
                                print(f"  • Aliases   : {', '.join(bio.get('aliases', []))}")
                                            
                                print("\n APPEARANCE:")
                                print(f"  • Gender    : {app.get('gender')}")
                                print(f"  • Race      : {app.get('race')}")
                                            
                                print("\n POWERSTATS:")
                                print(f"  • Intelligence : {stats.get('intelligence')} / 100")
                                print(f"  • Strength     : {stats.get('strength')} / 100")
                                print(f"  • Speed        : {stats.get('speed')} / 100")
                                print(f"  • Durability   : {stats.get('durability')} / 100")
                                print(f"  • Power        : {stats.get('power')} / 100")
                                print(f"  • Combat       : {stats.get('combat')} / 100")
                                print("="*40 + "\n")
                                    
                    elif option == "see image":
                        for x in hero_list:
                            if x.get("name") == choose:
                                image = x.get("image", {})
                                image_url = image.get("url")
                                webbrowser.open(image_url)

                    else:
                        for x in hero_list:
                              if x.get("name") == choose:
                                info = x
                                try:
                                    with open("characters.json","r") as file:
                                        data = json.load(file)

                                except(json.JSONDecodeError, FileNotFoundError):
                                    data = {}


                                n = 0 
                                    

                                while f"{x.get('id')}" in data.keys():
                                        print("\n!!CHARACTER ALREADY REGISTERED!!\n")
                                        break
                                else:
                                    x = f"{x.get('id')}"
                                    data[x] = info
                                    with open("characters.json","w") as file:
                                        json.dump(data, file, indent=4)
                                
            
        else:
            reason = questionary.select("\nDo you know the characters ID or would you like to look at the online ID list?\n",choices=["I know the ID","I need the online ID list"]).ask()
            if reason == "I need the online ID list":
                webbrowser.open("https://www.superheroapi.com/ids.html")
                print("Opening the browser please wait......")
                time.sleep(5)
            character_id = questionary.text("\nEnter a the character ID: ").ask()  
            url = f"https://superheroapi.com/api/{access_token}/{character_id}"
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
                )
            
            try:
                response = urllib.request.urlopen(req)
                raw_response = response.read()
                decoded_response = raw_response.decode("utf-8") 
                hero_archive = json.loads(decoded_response)
                
                question = questionary.select("\n--options--\n", choices=["Details","Add to Character List","see image"]).ask()
                if question == "Details":
                    
                    stats = hero_archive.get("powerstats", {})
                    bio = hero_archive.get("biography", {})
                    app = hero_archive.get("appearance", {})
                    
                    
                    print("\n" + "="*40)
                    print(f"  CHARACTER PROFILE: {hero_archive.get('name').upper()} (ID: {hero_archive.get('id')})")
                    print("="*40)
                    
                    print("\nHN BIOGRAPHY:")
                    print(f"  • Real Name : {bio.get('full-name') if bio.get('full-name') else 'Unknown'}")
                    print(f"  • Publisher : {bio.get('publisher')}")
                    print(f"  • Alignment : {bio.get('alignment').upper()}")
                    print(f"  • Aliases   : {', '.join(bio.get('aliases', []))}")
                    
                    print("\n APPEARANCE:")
                    print(f"  • Gender    : {app.get('gender')}")
                    print(f"  • Race      : {app.get('race')}")
                    
                    print("\n POWERSTATS:")
                    print(f"  • Intelligence : {stats.get('intelligence')} / 100")
                    print(f"  • Strength     : {stats.get('strength')} / 100")
                    print(f"  • Speed        : {stats.get('speed')} / 100")
                    print(f"  • Durability   : {stats.get('durability')} / 100")
                    print(f"  • Power        : {stats.get('power')} / 100")
                    print(f"  • Combat       : {stats.get('combat')} / 100")
                    print("="*40 + "\n")

                elif question == "see image":
                    image = hero_archive.get("image", {})
                    image_url = image.get("url")
                    webbrowser.open(image_url)
                else:
                    info = hero_archive
                    try:
                        with open("characters.json","r") as file:
                            data = json.load(file)

                    except(json.JSONDecodeError, FileNotFoundError):
                        data = {}


                    n = 0 
                                    

                    while f"{hero_archive.get('id')}" in data.keys():
                                        print("\n!!CHARACTER ALREADY REGISTERED!!\n")
                                        break
                    else:
                        x = f"{hero_archive.get('id')}"
                        data[x] = info
                        with open("characters.json","w") as file:
                            json.dump(data, file, indent=4)


            except urllib.error.URLError as e:
                print("\n[Network Error]: Could not reach the server.")
                print("Please check your internet connection and verify the URL.")
                exit()



mode()
       








