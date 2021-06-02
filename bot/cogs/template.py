'''
pwnyBot skeleton code. Please use this as a skeleton for any commands you intend to add.
Yes there is problably a better way to do it, but unless you are willing to refactor EVERYTHING, then dont mess with it.
'''
import discord
from discord.ext import commands
from bot import logger

NAME = "Template"


class Template(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.prefix = "$test "

    async def cog_check(self, ctx):
        success = ctx.prefix == self.prefix
        return success

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("[pwnyBot] " + NAME + " is online")

    @commands.command()
    async def demo(self, ctx):
        await ctx.send('Demo response!')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def sum(self, ctx, *numbers):
        await ctx.send(sum(map(int, numbers)))


def setup(client):
    client.add_cog(Template(client))
