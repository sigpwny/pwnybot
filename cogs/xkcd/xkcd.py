from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import subcommand_decorator
import aiohttp
import discord
import random


class Xkcd(commands.Cog):
    """Get XKCDs."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.aiohttp = aiohttp.ClientSession()

    @staticmethod
    def generate_embed(data):
        title = f'xkcd #{data.get("num")} - {data.get("title")}'
        embed = discord.Embed(
            title=title, url=f'https://xkcd.com/{data.get("num")}')
        embed.set_image(url=data.get("img"))
        embed.set_footer(text=data.get("alt"))
        return embed

    async def fetch(self, url):
        response = await self.aiohttp.get(url)
        try:
            return await response.json()
        except aiohttp.ContentTypeError:
            return None

    async def get_xkcd(self, _id: int):
        return await self.fetch(f"http://xkcd.com/{_id}/info.0.json")

    async def get_latest(self):
        return await self.fetch("http://xkcd.com/info.0.json")

    async def get_max_xkcd(self):
        data = await self.get_latest()
        return data.get("num")

    @subcommand_decorator()
    async def random(self, ctx: SlashContext) -> None:
        """A random XKCD

        """
        await ctx.defer()
        max_xkcd = await self.get_max_xkcd()
        _id = random.randint(1, max_xkcd)
        data = await self.get_xkcd(_id)
        embed = self.generate_embed(data)
        await ctx.send(embed=embed)

    @subcommand_decorator()
    async def latest(self, ctx: SlashContext) -> None:
        """The most recent XKCD

        """
        await ctx.defer()
        data = await self.get_latest()
        embed = self.generate_embed(data)
        await ctx.send(embed=embed)

    @subcommand_decorator(num={'description': "XKCD comic num"})
    async def num(self, ctx: SlashContext, num: int) -> None:
        """Get XKCD by number

        """

        await ctx.defer()
        data = await self.get_xkcd(num)
        if data is None:
            await ctx.send(f"❌ xkcd #{num} not found. Please try another one.")
            return
        embed = self.generate_embed(data)
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Xkcd(bot))
