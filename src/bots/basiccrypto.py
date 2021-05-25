# Imports go here
import discord
from discord.ext import commands
from base64 import b32encode, b64encode

# REQUIRED INFORMATION for the bot to work!
NAME = "basiccrypto"
VERSION = "1.0.0"
BOT_PREF = "bc"


class BasicCrypto(commands.Cog):
    def __init__(self, client):
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

        try:
            if command == '!hex':
                response = str(hex(int(args[0])))[2:]
            elif command == '!b64':
                response = b64encode(args[0])
            elif command == '!b32':
                response = b32encode(args[0])
            response = f'`{response}`'
        except Exception as e:
            print(f'WARNING: {e} on message: `{message}`')
            response = e
        await message.channel.send(response)


def setup(client):
    client.add_cog(BasicCrypto(client))
