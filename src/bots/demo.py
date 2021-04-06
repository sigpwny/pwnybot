# Imports go here
import discord
from discord.ext import commands

# REQUIRED INFORMATION for the bot to work!
NAME = "demo"
VERSION = "1.0.0"

class Demo(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("[pwnyBot] " + NAME + " is online")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content == '!demo':
            response = "Demo response!"
            await message.channel.send(response)

def setup(client):
    client.add_cog(Demo(client))