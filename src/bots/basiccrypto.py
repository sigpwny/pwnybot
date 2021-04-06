# Imports go here
import discord
from discord.ext import commands

# REQUIRED INFORMATION for the bot to work!
NAME = "basiccrypto"
VERSION = "1.0.0"

def rawhex(val):
    try:
        ret = "`" + str(hex(int(val,10)))[2:]  + "`"
    except Exception as e:
        ret = e
    return ret

class BasicCrypto(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("[pwnyBot] " + NAME + " is online")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        content = message.content
        command = content.split(" ")[0]
        args = content.split(" ")[1:]
        if command[0] != '!':
            return
        
        if command == '!hex':
            response = rawhex(args[0])
        elif command == '!b64':
            response = "WILL ADD b64 tmrw"
        
        await message.channel.send(response)

def setup(client):
    client.add_cog(BasicCrypto(client))