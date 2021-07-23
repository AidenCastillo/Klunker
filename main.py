#Please copy the variable.py file from the templates folder, and place it in the
#same directory as klunker.py. MUST BE IN THE SAVE DIRECTORY. Fill out the 
#information accordingly to get the bot to work.
from operator import truediv
import os
import sys


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, dir_path)

from variable import *

from cogs.cog import *
from cogs.rules import *

import discord 
import discord.ext 
from discord import guild
from discord import Color
from discord import member, user
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from discord.ext.commands.core import check
from discord import embeds, message
from discord.activity import CustomActivity
from discord.channel import DMChannel
from requests.models import Response

import json
import time
import datetime as dt
import random
import asyncio
from asyncio.tasks import ensure_future
import requests
from pprint import pprint
import traceback

client = commands.Bot(command_prefix = ['~'])


for filename in os.listdir('./cogs'):
    if filename.endswith('py'):
        client.load_extension(f'cogs.{filename[:-3]}')


#testing



#listening commands and events
@client.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="Suggest new cards, ~add")
    await client.change_presence(status=discord.Status.online, activity=activity)
    print('We have logged in as {0.user}'.format(client))

    with open('data/guilds.json') as f:
        guilds = json.loads(f.read())
    for x in guilds:
        guilds[x]['battleState'] = False
        with open('data/guilds.json', 'w') as f:
            json.dump(guilds, f, indent=4)
    reset.start()

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')

@tasks.loop(minutes=10)
async def reset():
    with open("data/users.json") as f:
        users = json.loads(f.read())
        
    for x in users:
        users[x]['claimed'] = False
        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=4)
        pprint(users[x]['claimed'])

    print("reset")


@reset.before_loop
async def before_reset():
    for _ in range(60*60):
        if dt.datetime.now().hour == 22:
            print("Claim Reset started")
            return
        await asyncio.sleep(1)

#Magic discord commands
@client.command()
@commands.has_permissions(kick_members=True)
async def magic(ctx, arg):
    author_guild_id = str(ctx.guild.id)
    with open("data/guilds.json") as f:
        guilds  = json.load(f)

    discord_guild_id = guilds
    guild = {}
    guild[str(ctx.guild.id)] = {}
    if author_guild_id in discord_guild_id:
        if arg == str('true'):
            guild[str(ctx.guild.id)]['magic'] = guild[str(ctx.guild.id)]['magic'] = True
            msg = "Magic is enabled"
        else:
            guild[str(ctx.guild.id)]['magic'] = guild[str(ctx.guild.id)]['magic'] = False
            msg = "Magic is disabled"
        guild[str(ctx.guild.id)]['battleState'] = False
    else:
        
        if arg == str('true'):
            guild[str(ctx.guild.id)]['magic'] = True
            msg = "Magic is enabled"
        else:
            guild[str(ctx.guild.id)]['magic'] = False
            msg = "Magic is not enabled"

        guild[str(ctx.guild.id)]['battleState'] = False

    guilds.update(guild)
    with open("data/guilds.json", "w", encoding="utf8") as f:
        json.dump(guilds, f, indent=4)
    await ctx.send(f"Your server has changed its settings in our system. {msg}. Contact mcjarjar35#5378 if you need help or would like to enable or disable magic.")

@client.command()
async def register(ctx):
    author_id = str(ctx.author.id)
    with open("data/users.json") as f:
        users = json.load(f)
        
    discord_id = users
    if author_id in discord_id:
        with open("data/users.json", "w") as f:
            users[str(ctx.author.id)]['uses'] = users[str(ctx.author.id)]['uses']+1
            json.dump(users, f, indent=4)
    else:
        user = {}
        user[str(ctx.author.id)] = {}
        user[str(ctx.author.id)]['library'] = {"name": []}
        user[str(ctx.author.id)]['deck'] = {"name": []}
        user[str(ctx.author.id)]['claim'] = False
        user[str(ctx.author.id)]['rolls'] = 0
        user[str(ctx.author.id)]['rank'] = ["Apprentice"]
        user[str(ctx.author.id)]['level'] = 0
        user[str(ctx.author.id)]['exp'] = 0
        user[str(ctx.author.id)]['uses'] = 0
        users.update(user)
        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=4)
            
        await ctx.send(f"You have now been registered into our system. Contact mcjarjar35#5378 if you need help or would like to be removed from our system.")
@client.command()
async def cards(ctx, *, arg=None):
    search = arg
    msg = []

    async def get_library(arg=None):
        arg = arg
        gMsg = []
        
        try:
            with open(f"data/cards/{arg}.json") as f:
                library = json.loads(f.read())
            for x in library:
                gMsg.append(x)

            msg = str(gMsg).replace('[',' ').replace(']',' ').replace("'", " ")
            embed=discord.Embed(title=f"{arg.capitalize()} Card Library", description=msg, color=0xff0000)   
        
        except:
            msg = get_cards()
            msg = str(msg).replace('[',' ').replace(']',' ').replace("'", " ")
            embed=discord.Embed(title="Full Card Library", description=msg, color=0xff0000)
        
        await ctx.send(embed=embed)
    
    await get_library(search)
    

@client.command()
async def library(ctx):
    msg = []
    
    try:
        with open("data/users.json") as f:
            user = json.loads(f.read())
            library = user[str(ctx.author.id)]['library']['name']
        for x in library:
            msg.append(x)
        msg  = str(msg).replace('[',' ').replace(']',' ').replace("'", " ")
        embed=discord.Embed(title=f"{ctx.author}'s Library", description=msg, color=0xff0000)
    
        await ctx.send(embed=embed)
    except Exception:
        traceback.print_exc()
        await ctx.send("Must use ~register to preform magic commands. If you have done this already, please claim a card before using again.")

@client.command()
async def roll(ctx):
    path = dir_path + "/data/cards/"
    
    cards = get_cards()
    rolled = random.choice(cards)
    
    library = {}
    for x in os.listdir(path):
        with open(f"data/cards/{x}") as f:
            info = json.loads(f.read())
        
        library.update(info)

    msg = library[str(rolled)]['description']

    try:
        image = library[str(rolled)]['image']
    except:
        image = "https://imgur.com/Q90fcUP.gif"

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["🧙"] and reaction.message == drop

    embed=discord.Embed(title=rolled, description=msg, color=0xff0000)
    embed.set_image(url=image)
    drop = await ctx.send(embed=embed)
    await drop.add_reaction("🧙")
    confirmation = await client.wait_for("reaction_add", check=check)

    if confirmation:
        if testmode == True:
            with open("data/users.json") as f:
                users = json.loads(f.read())
            discord_id = users

            await drop.edit(content="*" + drop.content + "*" + " **\nClaimed**")
            await ctx.send(ctx.author.mention + " took the card.")

            if str(ctx.author.id) in discord_id:
                library = users[str(ctx.author.id)]['library']['name']
                library.append(rolled)
                with open("data/users.json", "w") as f:
                    users[str(ctx.author.id)]['library']['name'] = library
                    json.dump(users, f, indent=4)
            else:
                await ctx.send("Please use the ~register command before claiming cards.")
            return
        else:
            with open("data/users.json") as f:
                users = json.loads(f.read())
            discord_id = users

            if users[str(ctx.author.id)]['claimed'] == True:
                await ctx.send("Already claimed")
            else:
                await drop.edit(content="*" + drop.content + "*" + " \nClaimed**")
                await ctx.send(ctx.author.mention + " took the card.")

                if str(ctx.author.id) in discord_id:
                    library = users[str(ctx.author.id)]['library']['name']
                    library.append(rolled)
                    with open("data/users.json", "w") as f:
                        users[str(ctx.author.id)]['library']['name'] = library
                        users[str(ctx.author.id)]['claimed'] = True
                        json.dump(users, f, indent=4)
                else:
                    await ctx.send("Please use the ~register command before claiming cards.")

@client.command(description="~deck is used to show and edit your deck. \n\n~deck add [Card] is used to add a card to your deck. \n~deck rm [Card]is used to remove a card from your deck. \n~deck with no attributes shows your deck.\n Is character specific.", brief="Shows/edit Deck.", aliases=['d'])
async def deck(ctx, command=None, *, Card=None):
    with open("data/users.json") as f:
        users = json.loads(f.read())
    def checkCards():
        card = (str(Card))
        fullLibrary = get_cards()
        if card in fullLibrary:
            if card in users[str(ctx.author.id)]['library']['name']:
                    totalLibrary = users[str(ctx.author.id)]['library']['name'].count(card)
                    totalDeck = users[str(ctx.author.id)]['deck']['name'].count(card)

                    if (totalDeck + 1) <= totalLibrary:
                        rsp = "Card passed"
                        return [True, rsp]
                    else:
                        rsp = f"You do not own enough {card} cards to add to your deck"
                        return [False, rsp]
            else:
                rsp = f"{card} is not in your library"
                return [False, rsp]
        else:
            rsp = f"{card} is not a card I have in my system"
            return [False, rsp]
            
    
    if command == "add":
        rsp = checkCards()
        if rsp[0] == True:
            deck = users[str(ctx.author.id)]['deck']['name']
            deck.append(Card)

            with open("data/users.json", "w") as f:
                users[str(ctx.author.id)]['deck']['name'] = deck
                json.dump(users, f, indent=4)
            await ctx.send(f"{Card} was added to your deck")
        else:
            await ctx.send(f"{rsp[1]}")
        


    elif command == "rm":
        rsp = checkCards()
        rsp[0] = True
        if rsp[0] == True:
            deck = users[str(ctx.author.id)]['deck']['name']
            deck.remove(Card)

            with open("data/users.json", "w") as f:
                users[str(ctx.author.id)]['deck']['name'] = deck
                json.dump(users, f, indent=4)
            await ctx.send(f"{Card} was removed from your deck")
        else:
            await ctx.send(f"{rsp[1]}")
    else:
        with open("data/users.json") as f:
            users = json.loads(f.read())
        try:
            msg = users[str(ctx.author.id)]['deck']['name']
            msg  = str(msg).replace('[',' ').replace(']',' ').replace("'", " ")
            await ctx.send(msg)
        except:
            await ctx.send("Please use ~deck add [card] before trying to view your deck.")
        

@client.command()
async def battle(ctx, player2=None, *, mode=None):
    await ctx.send("WARNING: ~battle is in beta, beware of bugs and not working mechanics.")
    allCards = get_cards()

    with open('data/users.json') as f:
        users = json.loads(f.read())
    with open('data/guilds.json') as f:
        guilds = json.loads(f.read())

    class Player:
        def __init__(self, id, name, deck, hand, field, attackCards, graveYard,health):
            self.id = id
            self.name = name
            self.deck = deck
            self.hand = hand
            self.field = field
            self.attackCards = attackCards
            self.graveYard = graveYard
            self.health = health

    class game:
        def __init(self, mode, maxhealth, maxcards):
            self.mode = mode
            self.maxhealth = maxhealth
            self.maxcards = maxcards
    #player1 = Player(id, name, deck, hand, field, attackCards, health)
    player1 = Player(str(ctx.author.id), str(await client.fetch_user(ctx.author.id)), users[str(ctx.author.id)]['deck']['name'], [], ['Goblin', 'Mio', 'Yui'], ['Goblin'], [], 20)

    playerId = str(player2).replace('@', '').replace('!', '').replace('<', '').replace('>', '')
    player2 = Player(playerId, await client.fetch_user(player2), users[str(playerId)]['deck']['name'], [], ['Goblin'],  ['Goblin'], [], 20)

    playerTurn = player1
    opponent = player2

    if mode == None:
        mode == 'standard'
    if mode == 'standard':
        Game = game(mode, 20, 60)

    for card in playerTurn.field:
        print(card)
    
    guild = str(ctx.guild.id)
    battleState = guilds[str(ctx.guild.id)]['battleState']

    if guild in guild:
        if guilds[str(ctx.guild.id)]['battleState'] == False:

            if player1.id and player2.id in users:
                with open("data/guilds.json") as f:
                    guilds = json.loads(f.read())

                guilds[str(ctx.guild.id)]['battleState'] = True

                with open("data/guilds.json", "w") as f:
                    json.dump(guilds, f, indent=4)
                

                
                def createMain(first, second, turn, action="No last action"):
                    global main
                    main=discord.Embed(title=f"{first.name} vs {second.name}", description=f"{turn.name}'s Turn \n{action}", color=0xff0000)
                    main.add_field(name=f"{first.name}'s cards", value="value", inline=True)
                    main.add_field(name=f"{first.name}'s cards", value="value", inline=True)
                    main.add_field(name="Field", value=f"{first.name}:{first.field}\n{second.name}:{second.field}", inline=False)
                    return main


                
                
                
                main = createMain(player1, player2, playerTurn)

                global battle
                battle = await ctx.send(embed=main)

                msg = []
                global historyList
                historyList= []
                reactions = ["✅", "💖", "💥", "🗺", "📢", "🎛", "📜", "🏳", "❌","❔", "↩"]

                for reaction in reactions:
                    msg.append(reaction)
                    
                    await battle.add_reaction(reaction)
                    
                await asyncio.sleep(1)
                
                

                battleState = guilds[str(ctx.guild.id)]['battleState']
                while battleState == True:
                    
                    @client.event
                    async def on_message(message):
                        instant = []
                        with open(f"data/cards/instant.json") as f:
                            library = json.loads(f.read())
                        for x in library:
                            instant.append(x)

                        if message.content in instant:
                            
                            historyList.append(f'{message.author} played {message.content}')
                            
                            await ctx.send(f"{message.author} played {message.content}")
                            card = checkEnter(message.content)

                            if card[4] == 'destroy':


                                if card[3] == 'any':
                                    def check(m):
                                        return m.author == ctx.author and m.channel == ctx.channel
                                    typemsg = await ctx.send("Type Target creature. Format: ~Goblin")
                                    msg = await client.wait_for('message', timeout=20.0, check=check)
                                    target = msg.content
                                    target = target.replace("~", "")

                                    if playerTurn.name == player1.name:
                                        player = player2
                                    else:
                                        player = player1

                                    if str(target) in player.field:
                                        player.field.remove(target)

                                        await ctx.send(f"{playerTurn.name} has used {card[0]['name']} on {target}")


                                        await message.delete()
                                        await typemsg.delete()
                                        await msg.delete()

                                        main = createMain(player1, player2, playerTurn)
                                        await battle.edit(embed=main)

                                    else:
                                        await ctx.send(f"{target} is not a creature your opponent has in their field") 

                        elif message.content in allCards and str(message.author) == str(playerTurn.name):

                            card = str(message.content)
                            if playerTurn.name == player1.name:
                                player = player1
                            elif playerTurn.name == player2.name:
                                player = player2

                            if card in player.deck:
                                deckCount = player.deck.count(card)
                                print(deckCount)
                                fieldCount = player.field.count(card)
                                print(fieldCount)
                                if (fieldCount + 1) <= deckCount:
                                    player.field.append(card)
                                    
                                    checkEnter(message.content)



                                else:
                                    print("not enough in deck")
                            else:
                                print("not in deck")
                                
                                

                    def check(reaction, user):
                        return user == ctx.author or player2.name and str(reaction.emoji) in reactions and reaction.message == battle




                    

                    reaction, user = await client.wait_for("reaction_add", check=check)
                    
                    #below are if statements that when a user reacts with a specific reaction, it will do something like change turn, show question page, or initiate battle phase

                    if str(reaction) == str("✅"):
                        #End Turn
                        if str(user) == str(playerTurn.name):
                            for card in playerTurn.field:
                                if card in playerTurn.attackCards:
                                    pass
                                else:
                                    playerTurn.attackCards.append(card)
                                    print(playerTurn.attackCards)

                            if playerTurn.name == player1.name:
                                playerTurn = player2
                                opponent = player1
                            elif playerTurn.name == player2.name:
                                playerTurn = player1
                                opponent = player2
                            
                            main = createMain(player1, player2, playerTurn)
                            await battle.edit(embed=main)
                        else:
                            pass

                    elif str(reaction) == "💖":
                        print("sparkle")
                    elif str(reaction) == "💥":
                        battlePhase = True
                        while battlePhase == True:
                        #battle phase
                            attackCards = str(playerTurn.attackCards).replace('[', '').replace(']', '').replace("'", '')

                            attackPhase=discord.Embed(title="Attack Phase", description="Type the name of the card you want to attack with. Click the Back button to return to the main screen" ,color=0xff0000)
                            attackPhase.add_field(name="Attackable Cards", value=f"{attackCards}")
                            attackPhase.add_field(name="Target Cards", value=f"value")

                            await battle.edit(embed=attackPhase)

                            #cards will have two different options on attack. They can use their normal attack that is traditional, and a action move with special attributes.
                            global selecting
                            selecting = False
                            @client.event
                            async def on_message(message):

                                global selecting
                                if selecting == False:
                                    selecting = True
                                    card1 = message.content
                                    if str(card1) in playerTurn.field:
                                        def check(user):
                                            return user == player1.name or player2.name

                                        enter = await ctx.send("Enter 'attack' or 'action'")
                                        msg = await client.wait_for("message", check=check)
                                        await msg.delete()

                                        if str(msg.content) == 'attack':

                                            options = await ctx.send(f"{opponent.name} Type creature you want to block with, type a instant, or type No/no for no blocking")
                                            msg = await client.wait_for("message", check=check)
                                            await msg.delete()
                                            
                                            card2 = msg.content

                                            if str(card2) in opponent.field:
                                                data = onAttack(card1, card2)

                                                if data[0] >= data[3]:
                                                    if data[0] == data[3]:
                                                        player1.field.remove(card1)
                                                        player2.field.remove(card2)
                                                    else:
                                                        player2.field.remove()


                                                    main = createMain(player1, player2, playerTurn, f"{card1} attacked {card2}")
                                                    await battle.edit(embed=main)
                                                    await enter.delete()
                                                    await options.delete()
                                                    await message.delete()
                                            if msg.content == "No" or 'no':
                                                data = onAttack(card1)

                                                opponent.health -= data[0]
                                                await enter.delete()
                                                await options.delete()
                                                await message.delete()

                                                main = createMain(player1, player2, playerTurn, f"{card1} attacked Opponent's health.")
                                                await battle.edit(embed=main)
                                        elif str(msg.content) == 'action':
                                            data = onAction(card)
                                else:
                                    pass


                            reaction, user = await client.wait_for("reaction_add", check=check)

                            if str(reaction) == "↩":
                                main = createMain(player1, player2, playerTurn)
                                battlePhase = False
                                await battle.edit(embed=main)
                    elif str(reaction) == "🗺":
                        #History Panel
                        
                        historyList = str(historyList).replace('[', '').replace(']', '').replace("'", '')
                        print(historyList)
                        history=discord.Embed(title="Game Action History", description="", color=0x1abc9c)
                        history.add_field(name="History", value=f"{historyList}", inline=False)


                        await battle.edit(embed=history)
                        print("🗺")
                    elif str(reaction) == "📢":
                        print("📢")
                    elif str(reaction) == "🎛":
                        #Control Panel

                        controlPanel=discord.Embed(title="Control Panel", description="This panel you can change game settings and values.\nTo change settings, type ~{setting name} {attribute}", color=0xf1c40f)
                        controlPanel.add_field(name="Settings", value=f"battlestate:{battleState}\n maxhealth:")
                        await battle.edit(embed=controlPanel)
                        @client.event
                        async def on_message(message):
                            if str(message.content) == '~battlestate false':
                                print("battle state: false")
                                global battleState
                                battleState = False
                    elif str(reaction) == "📜":
                        print("📜")
                    elif str(reaction) == "🏳":
                        #Surrender

                        battleState = False
                    elif str(reaction) == "❌":
                        print("x")
                    elif str(reaction) == "❔":
                        #Question panel

                        questionEm=discord.Embed(title=f"Magic The Gathering Help")
                        questionEm.add_field(name=f"Links", value="How to Play: https://www.youtube.com/watch?v=RZyXU1L3JXk\n Wiki: https://github.com/AidenCastillo/klunker/wiki \n Card Wiki: https://github.com/AidenCastillo/klunker/wiki/Card-Wiki", inline=True)
                        questionEm.add_field(name=f"Emote Commands and written Commands:", value="✅=End Turn\n💥=Attack Phase", inline=True)

                        await battle.edit(embed=questionEm)
                        
                    elif str(reaction) == str("↩"):
                        #Back Command, brings back to main
                        main = createMain(player1, player2, playerTurn)
                        await battle.edit(embed=main)

                    reactions = ["✅", "💖", "💥", "🗺", "📢", "🎛", "📜", "🏳", "❌","❔", "↩"]

            else:
                await ctx.send('Player 1 or Player 2 is in not registered. Please use ~register')
        else:
            await ctx.send('There is already a battle happening in your server')
    else:
        await ctx.send('Your server is not registered in my system. Use ~magic true')
    
@client.command()
async def exit(ctx):
    with open("data/guilds.json") as f:
        guilds = json.loads(f.read())

    guilds[str(ctx.guild.id)]['battleState'] = False

    with open("data/guilds.json", "w") as f:
        json.dump(guilds, f, indent=4)

#command for suggesting cards to add to main system and main library
@client.command()
async def add(ctx):
    question = ['Card name.','What catagory is the card in', 'What is the description', 'What is the type. (creature)', 'Health Stat. (creature)', 'Attack Stat. (creature)', 'Energy Cost', 'Image link. (i.imgur.com/). No picture use NA']
    answers = []
    fullLibrary = get_cards()
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in question:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You didn't answer in time. Be quciker next time.")
            return
        else:
            answers.append(msg.content)

    if str(answers[0]) not in fullLibrary:
        pass
    else:
        await ctx.send("Card name is already in data base.")
        return
    
    location = str(answers[1])
    location = location.lower()
    if location in ['artifact', 'creature', 'enchantment', 'instant', 'land', 'sorcery']:
        pass
    else:
        await ctx.send('Not valid catagory.')
        return
    
    newcard = {}
    newcard[str(answers[0])] = {}
    newcard[str(answers[0])]['name'] = str(answers[0])
    newcard[str(answers[0])]['description'] = str(answers[2])
    newcard[str(answers[0])]['type'] = str(answers[3])
    newcard[str(answers[0])]['stats'] = {}
    try:
        newcard[str(answers[0])]['stats']['health'] = int(answers[4])
        newcard[str(answers[0])]['stats']['attack'] = int(answers[5])
        newcard[str(answers[0])]['cost'] = int(answers[6])
    except:
        await ctx.send('Stats or cost is not a integer')
    newcard[str(answers[0])]['image'] = str(answers[7])
    newcard[str(answers[0])]['action'] = ""
    
    if ctx.author.id == 593615922330075146:

        with open(f'data/cards/{answers[1]}.json') as f:
            library = json.loads(f.read())
        library.update(newcard)
        pprint(library)
        with open(f'data/cards/{answers[1]}.json', 'w') as f:
            json.dump(library, f, indent=4)
    else:
        with open(f'suggest/cards.json') as f:
            library = json.loads(f.read())
        library.update(newcard)
        pprint(library)
        with open(f'suggest/cards.json', 'w') as f:
            json.dump(library, f, indent=4)
    await ctx.send('Your card has been send for review to be added into my full library and to be used by others. Please wait some Time for someone to look over it.')


#Non Magic commands

#Osu
def get_token():
    TOKEN_URL = 'https://osu.ppy.sh/oauth/token'
    data = token_data

    response = requests.post(TOKEN_URL, data=data)

    return response.json().get('access_token')

@client.command(aliases=['top_play'])
async def topplay(ctx, arg):
    API_URL = 'https://osu.ppy.sh/api/v2'

    token = get_token()

    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'mode': 'osu',
        'limit': 5
    }

    response = requests.get(f'{API_URL}/users/{arg}/scores/best', params=params, headers=header)

    pprint(response.json(), indent=2, depth=2)
    
    embed=discord.Embed(title=f"{arg}'s Top Play", description="description", color=0xff0000)
    embed.add_field(name="field", value="value", inline=False)
    await ctx.send(embed=embed)

#Crypto
@client.command()
async def crypto(ctx):
    embed=discord.Embed(title="title", description="description", color=0xff0000)
    embed.add_field(name="field", value="value", inline=False)
    await ctx.send(embed=embed)

#Admin and server
@client.command()
@commands.has_permissions(kick_members=True)
async def server_stats(ctx):
    questions = ["Should I create a Discord Stats channel? y/n"]
    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    for i in questions:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You didn't answer in time. Be quicker next time.")
            return
        else:
            answers.append(msg.content)

#raffle functions
def convert(time):
    pos = ('s', 'm', 'h', 'd')
    time_dict = {'s' : 1, 'm' : 60, 'h' : 3600, 'd' : 3600*24}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2
    
    return val * time_dict[unit]

#raffle

@client.command()
async def raffle(ctx):
    await ctx.send("Answer the following questions in the next 30 seconds")

    questions = ["What channel do I host your giveaway in? Enter like #General", "How long should the duration be? (s|m|h|d), Example: 60s", "What is the prize?"]

    answers = []

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    for i in questions:
        await ctx.send(i)

        try:
            msg = await client.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You didn't answer in under the time limit.")
            return
        else:
            answers.append(msg.content)

    try:
        c_id = int(answers[0][2:-1])
        print(c_id)
        print(answers[0])
    except:
        await ctx.send(f"you didn't metnion a channel properly. Do it like this {ctx.channel.mention} next time.")
        return

    channel = client.get_channel(c_id)

    time = convert(answers[1])
    if time == -1:
        await ctx.send(f"You didn't answer with a proper unit. Use (s|m|h|d) next time.")
        return 
    elif time == -2:
        await ctx.send(f"The time must be a integer. Please enter a integer next time.")
        return

    prize = answers[2]

    await ctx.send(f"the raffle will be in {channel.mention} and will last {answers[1]} seconds!")

    Embed = discord.Embed(title = "Raffle!", description = f"{prize}", color = ctx.author.color)
    Embed.add_field(name = "Hosted by:", value = ctx.author.mention)
    Embed.set_footer(text = f"Ends {answers[1]} from now!")

    my_msg = await channel.send(embed = Embed)

    await my_msg.add_reaction("🎉")

    await asyncio.sleep(time)

    new_msg = await channel.fetch_message(my_msg.id)

    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await channel.send(f"Congratulations! {winner.mention} won the prize: {prize}!")
        
@client.command()
async def reroll(ctx, channel : discord.TextChannel, id_ : int):
    try:
        new_msg = await channel.fetch_message(id_)
    except:
        await ctx.send("The ID that was entered was incorrect, make sure you have entered the correct raffle message ID.")
    users = await new_msg.reaction[0].users().flatten()
    users.pop(users.indexx(client.user))

    winner = random.choice(users)

    await channel.send(f"Congratulations the winner is: {winner.mention} for the raffle reroll!")

client.run(Token)
