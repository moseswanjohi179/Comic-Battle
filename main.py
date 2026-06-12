import os
import json
import pyfiglet
import questionary
import characters
import time
from engiene import lobby
from alive_progress import alive_bar
print("""

""")

with alive_bar(100, title="Loading Game: ") as bar:
    for i in range(100):
        time.sleep(0.1)
        bar()

print("""

""")

title = pyfiglet.figlet_format("Battle_Game", font= "graffiti")
print(title)


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
        data[x] = {"user_name":user_name,"avatar":avatar,"universe":universe,"team":team}
        with open("data.json","w") as file:
            json.dump(data, file, indent=4)




def regstration():
    global user_name
    global avatar
    global universe
    global team

    user_name = questionary.text("\nWhat is Your Name ?").ask()

    universe = questionary.select("\nPick your Universe:", choices=["DC","Marvel"]).ask()



    if universe == "Marvel":
        avatar = questionary.select(f"\nPick Your Avatar {user_name} :", choices = characters.avengers).ask()
        team_members = characters.avengers.copy()
        team_members.remove(avatar)
        team = questionary.checkbox("Pick Your 4 Team Mates",choices= team_members).ask()
        while len(team) > 4:
            team = questionary.checkbox("Please Select only 4 Members",choices= team_members).ask()

                

    else:
        avatar = questionary.select(f"\nPick Your Avatar {user_name} :", choices = characters.justice_league).ask()
        team_members = characters.justice_league.copy()
        team_members.remove(avatar)
        team = questionary.checkbox("Pick Your 4 Team Mates",choices= team_members).ask()
        while len(team) > 4:
            team = questionary.checkbox("Please Select only 4 Members",choices= team_members).ask()

    storage_function()



def introduction():
    from engiene import character_del
    answer = questionary.confirm("Are you new here?").ask()
    if answer == True:
        regstration()
        action = lobby(user_name)
        if action == "Reset":
            character_del(user_name)
            regstration()
    else: 
        try:
            with open("data.json","r") as file:
                    data = json.load(file)

            profiles = []
            for info in data.values():
                profiles.append(info["user_name"])
                

            identity = questionary.select("\nPick Your Profile: ", choices = profiles).ask()
            action = lobby(identity)
            if action == "Reset":
                character_del(identity)
                regstration()
        except(json.JSONDecodeError, FileNotFoundError):
            print("No user data found please Register.")
            regstration()
    
if __name__ == "__main__":
    introduction()









