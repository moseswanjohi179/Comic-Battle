import json
from character_manager import update_characters
import urllib.request
import questionary
import os
import webbrowser
import pyfiglet
import getpass
import time
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet

def reseter():
    os.system('cls' if os.name == 'nt' else 'clear'); title = pyfiglet.figlet_format("Battle_Game", font= "graffiti"); print(title)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "characters.json")

ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
key = b'aymZXEycJZZJC9ctMIGb9FhQGzHu6CyKqj54cGZaXBE='
cipher = Fernet(key)

def initialize_api_key():
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            pass   

    load_dotenv(ENV_FILE, override=True)
    api_key = os.getenv("SUPERHERO_API")

    if not api_key:
        
        print("\n--- First Time Setup ---\n")
        choice = questionary.confirm("Would you like help acquiring an SUPERHERO_API if you don't have one??").ask()
        if choice == True:
            print("Opening Browser, just a sec..")
            webbrowser.open("https://www.superheroapi.com/")
            time.sleep(10)
            
        #Encrypting credential
        
        user_input = getpass.getpass("Enter your API Key: ").strip()
        raw_bytes = cipher.encrypt(f"{user_input}".encode())
        hex_string = raw_bytes.hex()
        user_input = hex_string
        
        
        
        if not user_input:
            raise ValueError("API Key cannot be empty.")
        set_key(ENV_FILE, "SUPERHERO_API", user_input)
        print("API Key saved successfully to .env!\n")
        
        
        load_dotenv(ENV_FILE)
        api_key = os.getenv("SUPERHERO_API")

    return api_key


def mode():
        update_characters() 
        os.system('cls' if os.name == 'nt' else 'clear'); title = pyfiglet.figlet_format("Battle_Game", font= "graffiti"); print(title)
        access_token = initialize_api_key()
        access_token = access_token.strip()
        #Decode credential
        original_bytes = cipher.decrypt(bytes.fromhex(access_token))
        access_token = original_bytes.decode()
        
        choice = questionary.select("Mode", choices=["Search by ID","Search by Name"]).ask()
        if choice == "Search by Name":
            reseter()
            hero_name = questionary.text("Enter a name Key word:").ask()
            
            try:
                url = f"https://superheroapi.com/api/{access_token}/search/{hero_name}"
                
            
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
            except:
                print("!!There was an unforseen error!!")

            try:
                response = urllib.request.urlopen(req)
                raw_response = response.read()
                decoded_response = raw_response.decode("utf-8") 
                hero_archive = json.loads(decoded_response)
                


            except urllib.error.URLError as e:
                print("\n[Network Error]: Could not reach the server.")
                print("Please check your internet connection and verify the URL.")
                return



            character_list = {}

            hero_list = hero_archive.get("results", [])

            for hero in hero_list:
                character_name = hero.get("name")
                character_id = hero.get("id")
                character_list[character_id] = character_name

            try:
                choose = questionary.select("\n--Results--\n", choices=list(character_list.values())).ask()
            except:
                print("\t!!That Character Could Not Be Identified!!")
                time.sleep(2)
                try: 
                    mode()
                except:
                    print("!!Error Please Restart!!")

            for x in list(character_list.values()):
                if choose == x:
                    def what_to_do_with_xter():
                            option = questionary.select("\n--options--\n",choices=["Details","Add to Character List","see image","Back"]).ask()
                            if option == "Details":
                                reseter()
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
                                        try:
                                            what_to_do_with_xter()
                                        except:
                                            print("\nError Plz Restart--\n")
                                            
                            elif option == "see image":
                                reseter()
                                for x in hero_list:
                                    if x.get("name") == choose:
                                        image = x.get("image", {})
                                        image_url = image.get("url")
                                        print("\nOpening browser please wait....\n")
                                        webbrowser.open(image_url)
                                        time.sleep(5)
                                        try:
                                            what_to_do_with_xter()
                                        except:
                                            print("\nError Plz Restart--\n")
                                        
                                    


                            elif option == "Add to Character List":
                                reseter()
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

                                try:
                                    what_to_do_with_xter()
                                except:
                                    print("\nError Plz Restart--\n") 
                            else:
                                return      
                    what_to_do_with_xter()
        else:
            reseter()
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

                def what_to_do_with_xter_2():
                        reseter()
                
                        question = questionary.select("\n--options--\n", choices=["Details","Add to Character List","see image","Back"]).ask()
                        if question == "Details":
                            reseter()
                            
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
                            try:
                                what_to_do_with_xter_2()
                            except:
                                print("\nError Plz Restart--\n")

                        elif question == "see image":
                            reseter()
                            image = hero_archive.get("image", {})
                            image_url = image.get("url")
                            webbrowser.open(image_url)
                            print("\nOpening browser please wait....\n")
                            try:
                                what_to_do_with_xter_2()
                            except:
                                print("\nError Plz Restart--\n")
                            time.sleep(5)


                        elif question == "Add to Character List":
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
                            try:
                                what_to_do_with_xter_2()
                            except:
                                print("\nError Plz Restart--\n")
                        else:
                            return
                what_to_do_with_xter_2()


            except urllib.error.URLError as e:
                print("\n[Network Error]: Could not reach the server.")
                print("Please check your internet connection and verify the URL.")
                return
        

if __name__ == "__main__":
    mode()
     

#6b24282000b8192d8347081aa910d9b4








