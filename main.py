import os
import json
import pyfiglet
import questionary
import characters
import time
import getpass
from engiene import lobby
from alive_progress import alive_bar
import bcrypt





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
        data[x] = {"user_name":user_name,"password":hashed}
        with open("data.json","w") as file:
            json.dump(data, file, indent=4)




def regstration():
    global user_name
    global hashed
    

    user_name = questionary.text("\nWhat is Your Name ?").ask()
    security = questionary.password("\nSecure your account with a password: ").ask()
    bytes_pw = security.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes_pw, salt).decode('utf-8')
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
            pass_confirm = getpass.getpass("Enter Your Password: ")
            bytes_entered = pass_confirm.encode('utf-8')
            

            for x in data.values():
                if x["user_name"] == identity:
                    possibility = x["password"]

            if bcrypt.checkpw(bytes_entered, possibility.encode('utf-8')):
                action = lobby(identity)
                if action == "Reset":
                    character_del(identity)
                    regstration()
            else:
                print("\n!!!Wrong Password!!!!!\n")
                introduction()
        except(json.JSONDecodeError, FileNotFoundError):
            print("No user data found please Register.")
            regstration()
    
if __name__ == "__main__":
    introduction()









