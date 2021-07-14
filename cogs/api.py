import discord
from discord.ext import commands

class api(commands.Cog):
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(api(client))