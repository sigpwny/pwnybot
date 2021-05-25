# Imports go here
import discord
from discord.ext import commands

# REQUIRED INFORMATION for the bot to work!
NAME = "basiccrypto"
VERSION = "1.0.0"
BOT_PREF = "bc"

def rawhex(val):
    try:
        ret = "`" + str(hex(int(val,10)))[2:]  + "`"
    except Exception as e:
        ret = "rawHex Error: `" + str(e) + "`"
    return ret

class BasicCrypto(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("[pwnyBot] " + NAME + " is online")
    
    @commands.command()
    async def test(self,ctx, content = 'No content found :('):
        await ctx.send('BasicCrypto: `' + content + '`')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        content = message.content
        command = content.split(" ")[0]
        args = content.split(" ")[1:]
        if command[0] != '!':
            return

        response = None
        if command == '!hex':
            response = rawhex(args[0])
        elif command == '!b64':
            response = "WILL ADD b64 tmrw"

        if response != None:
            await message.channel.send(response)

def setup(client):
    client.add_cog(BasicCrypto(client))