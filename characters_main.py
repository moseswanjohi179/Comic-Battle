import json
import urllib.request
import questionary
import os
import webbrowser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, "characters.json")




def mode(access_token="bf8491949df3916503b0ccf7c7a30265"):
    query = questionary.confirm("Do you have a superhero api key?").ask()
    if query == True:
        test_token = questionary.password("Enter your Key Below:").ask()
        if len(test_token) == len(access_token):
            access_token = test_token
        else:
            print("Invalid Key!!")
    else:
        
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
                                    with open("charcters.json","r") as file:
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




            except urllib.error.URLError as e:
                print("\n[Network Error]: Could not reach the server.")
                print("Please check your internet connection and verify the URL.")
                exit()



mode()
       








