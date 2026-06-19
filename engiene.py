import os
import json
import pyfiglet
import questionary
import g4f
import time


def character_del(identity):
    
        with open("data.json") as file:
            data = json.load(file)
        for x in list(data.keys()):
            if data[x].get("user_name") == identity:
                del data[x]
        with open("data.json","w") as file:
            json.dump(data, file, indent=4)
    







def lobby(name):
    os.system('cls' if os.name == 'nt' else 'clear'); title = pyfiglet.figlet_format("Battle_Game", font= "graffiti"); print(title)
    selection = questionary.select("\n---Options---\n", choices=["Play","Reset","Character Enlist","Exit"]).ask()
    if selection == "Play":
        return "play"
    elif selection == "Reset":
        return "Reset" 
    elif selection == "Character Enlist":
        return "Enlist"
    else:
        return "log out"

def play():
    os.system('cls' if os.name == 'nt' else 'clear'); title = pyfiglet.figlet_format("Battle_Game", font= "graffiti"); print(title)
    with open("characters.json","r") as file:
        data = json.load(file)
    character_register = []
    universe_list = []
    for x in data:
        character_register.append(data[x]["biography"]["publisher"])

    character_register = set(character_register)
    while character_register == False:
        print("!!The List is Empty!!")
        decision = questionary.confirm("Would You Like To Quit?").ask()
        if decision == True:
            exit()
    universe = questionary.select("\nSelect Your Universe:\n", choices=list(character_register)).ask()
    for x in data:
        if data[x]["biography"]["publisher"] == universe:
            universe_list.append(data[x]["name"])
    avatar = questionary.select("Select Your Avatar", choices=universe_list ).ask()
    universe_list.remove(avatar)
    
    while universe_list == False:
        print("!!The Universe List is Empty!!")
        decision = questionary.confirm("\nWould You Like To Quit?\n").ask()
        if decision == True:
            exit()

    try:
        team = questionary.checkbox("Pick A Maximum of Five Team Mates:", choices=universe_list).ask()
    except:   
        choice = questionary.confirm("\nThere Are No other Characters In this Universe.Enlist characters?\n").ask()
        if choice == True:
            return "character_enlist"
        










