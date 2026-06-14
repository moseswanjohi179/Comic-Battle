import os
import json
import pyfiglet
import questionary
import time
from alive_progress import alive_bar

def character_del(identity):
    
        with open("data.json") as file:
            data = json.load(file)
        for x in list(data.keys()):
            if data[x].get("user_name") == identity:
                del data[x]
        with open("data.json","w") as file:
            json.dump(data, file, indent=4)
    







def lobby(name):
    selection = questionary.select("\n---Options---\n", choices=["Play","Reset","Exit"]).ask()
    if selection == "Play":
        pass
    elif selection == "Reset":
        return "Reset" 
    else:
        return "exit"

def play():
    pass












def test():
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