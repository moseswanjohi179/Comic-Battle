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
        return "play"
    elif selection == "Reset":
        return "Reset" 
    else:
        return "exit"

def play():
    with open("characters.json","r") as file:
        data = json.load(file)
    character_register = []
    universe_list = []
    for x in data:
        character_register.append(data[x]["biography"]["publisher"])

    character_register = set(character_register)
    universe = questionary.select("\nSelect Your Universe:\n", choices=list(character_register)).ask()
    for x in data:
        if data[x]["biography"]["publisher"] == universe:
            universe_list.append(data[x]["name"])
    avatar = questionary.select("Select Your Avatar", choices=universe_list ).ask()
    universe_list.remove(avatar)
    team = questionary.checkbox("Pick A Maximum of Five Team Mates:", choices=universe_list).ask()












