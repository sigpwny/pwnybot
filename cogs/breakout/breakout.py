from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator


class Breakout(commands.Cog):
    """Breakout room creator."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.created_channels = []

    @subcommand_decorator({'message': {'rooms': "The number of breakout rooms"}})
    async def start(self, ctx: SlashContext, rooms: int = 2) -> None:
        """Create N breakout rooms"""
        await ctx.defer()
        voice_category = ctx.guild.voice_channels[0].category
        for i in range(rooms):
            chan = await voice_category.create_voice_channel(f"breakout-{i+1}")
            self.created_channels.append(chan)
        await ctx.send(f"Created {rooms} Voice Channels.")

    @subcommand_decorator({})
    async def end(self, ctx: SlashContext) -> None:
        """End breakout rooms"""
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