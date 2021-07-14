import json
import sys
import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:-5]
sys.path.insert(1, dir_path)

import discord
from discord.ext import commands
class cog(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(cog(client))

def get_cards():
    data = {}
    
    for filename in os.listdir(dir_path + "/data/cards/"):
        with open(f"data/cards/{filename}") as f:
            x = json.loads(f.read())
        data.update(x)
    return data