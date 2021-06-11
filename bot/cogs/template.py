'''
This class is intended to be used as a template to create other cogs. Copy paste, then modify
'''
import discord
from discord.ext import commands
from bot import logger

# Each 'bot' is actually a cog. Docs here: https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html


class Template(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.prefix = "$test "  # Note the space

    # Runs before any command is checked in this cog
    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    # An event listener. Docs here: https://discordpy.readthedocs.io/en/stable/api.html#discord-api-events
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[pwnyBot] {self.__class__.__name__} is online")

    # A command. Docs here: https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def sum(self, ctx, *numbers):
        await ctx.send(sum(map(int, numbers)))

    @commands.command()
    async def echo(self, ctx, *args):
        await ctx.send(' '.join(args))


def setup(client):
    client.add_cog(Template(client))
