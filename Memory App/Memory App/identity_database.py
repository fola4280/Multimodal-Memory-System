import json
import os

if os.path.exists("people.json"):

    with open("people.json","r") as file:

        identity_map = json.load(file)

else:

    identity_map = {}