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
        health = None
    try:
        attack = library[str(card)]['enter']['stats']['attack']
    except:
        attack = None
    try:
        target = library[str(card)]['enter']['target']
    except:
        target = None
    try:
        action = library[str(card)]['enter']['action']
    except:
        action = None
        
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

def onAction(card, player1, player2, playerTurn, opponent, arg=None, arg2=None):
    '''
    Ran when a card uses a action.

    Required field:`card`, `player1`, `player2`, `playerTurn`, `opponent`
    Optional field:`arg`, `arg2`
    '''
    library = get_cards()
    with open("data/action.json") as f:
        data = json.loads(f.read())
    
    action = library[card]['action']
    
    if action == "roll murder":
        pass
    elif action == "stun":
        print(arg)
        print(opponent.attackCards)
        opponent.attackCards.remove(arg)
        print(opponent.attackCards)

    return player1, player2