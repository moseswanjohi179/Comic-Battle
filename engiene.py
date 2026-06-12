import os
import json
import pyfiglet
import questionary
import characters
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
        pass