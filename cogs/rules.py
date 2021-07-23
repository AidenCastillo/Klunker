from asyncio.windows_events import NULL
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

    try:
        health = library[str(card)]['enter']['stats']['health']
    except:
        health = NULL
    try:
        attack = library[str(card)]['enter']['stats']['attack']
    except:
        attack = NULL
    try:
        target = library[str(card)]['enter']['target']
    except:
        target = NULL
    try:
        action = library[str(card)]['enter']['action']
    except:
        action = NULL
        
    return health, attack, target, action

def onAttack(card1, card2=None):
    library = get_cards()
    data = []
    
    if card2 == None:
        try:
            attack = library[card1]['stats']['attack']
        except:
            attack = 0
        try:
            health = library[card1]['stats']['health']
        except:
            health = 1
        data.append(attack)
        data.append(health)
    else:
        for x in [card1, card2]:
            try:
                attack = library[x]['stats']['attack']
            except:
                attack = 0
            try:
                health = library[x]['stats']['health']
            except:
                health = 1
            data.append(attack)
            data.append(health)
    return data

def onAction(card):
    library = get_cards()
    with open("data/action.json") as f:
        data = json.load(f.read())
    
    action = library[card]['action']
    data = data[action]

    return action, data