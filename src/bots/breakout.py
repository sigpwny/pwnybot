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
        pass


def setup(client):
    client.add_cog(BreakoutRooms(client))
