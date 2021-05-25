# Imports go here
import discord
from discord.ext import commands

NAME = "breakout"
VERSION = "1.0.0"
HELP_STR = '''
!breakout <number> <prefix> <random/choice>
!breakout start
!breakout end
'''


class BreakoutRooms(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[pwnyBot] {NAME} is online")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Init
        if message.author == self.client.user:
            return
        isbreakout = message.lower().startswith('!breakout')
        args = message.split(' ')
        if not isbreakout:
            return

        if args == 1:
            await message.channel.send(HELP_STR)
        elif args[1] == 'ping':
            await message.channel.send("Pong!")
        else:
            await message.channel.send("That hasn't been coded yet...")


def setup(client):
    client.add_cog(BreakoutRooms(client))
