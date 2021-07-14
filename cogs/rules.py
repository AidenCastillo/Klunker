import os
import sys
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:-5]
sys.path.insert(1, dir_path)

from cogs.cog import *

import discord
from discord.ext import commands

class rules(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(rules(client))

def checkEnter(card):
    library = get_cards()

    health = library[str(card)]['enter']['stats']['health']
    attack = library[str(card)]['enter']['stats']['attack']
    target = library[str(card)]['enter']['target']

    return health, attack, target

def onAttack(card1, card2):
    library = get_cards()
    data = []

    for x in [card1, card2]:
        try:
            attack = library[x]['stats']['attack']
        except:
            attack = 0
        try:
            health = library[x]['stats']['health']
        except:
            health = 1
        data.append(attack, health)
    return data

def onAction():
    return