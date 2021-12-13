from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator
import discord
from lib.config import HELPER_ROLE_ID, ADMIN_ROLE_ID


class Breakout(commands.Cog):
    """Breakout room creator."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.created_channels = []

    @subcommand_decorator(rooms={"description": "The number of breakout rooms"}, category={"description": "Category name to put breakout rooms under"})
    @commands.has_any_role([HELPER_ROLE_ID, ADMIN_ROLE_ID])
    async def start(self, ctx: SlashContext, rooms: int, category: str = None) -> None:
        """Create N breakout rooms (max 5) """
        await ctx.defer()

        if category:
            voice_category = discord.utils.get(
                ctx.guild.categories, name=category)
            if not voice_category:
                await ctx.send("Could not find that category.")
                return
        else:
            voice_category = ctx.guild.voice_channels[0].category

        for i in range(min(rooms, 5)):
            chan = await voice_category.create_voice_channel(f"breakout-{i+1}")
            self.created_channels.append(chan)

        await ctx.send(f"Created {rooms} Voice Channels.")

    @subcommand_decorator()
    @commands.has_any_role([HELPER_ROLE_ID, ADMIN_ROLE_ID])
    async def end(self, ctx: SlashContext) -> None:
        """End ALL breakout rooms"""
        await ctx.defer()

        if len(self.created_channels) == 0:
            await ctx.send("I don't remember creating any...")
            return

        for chan in self.created_channels:
            await chan.delete()
        self.created_channels = []

        await ctx.send("Ended breakout rooms.")


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Breakout(bot))
