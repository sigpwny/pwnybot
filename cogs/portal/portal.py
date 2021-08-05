from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType as OptionType
from discord import utils
from lib.util import command_decorator, subcommand_decorator

EMOTE_FROM = "<:pwnyPortalFrom:846831813720932383> "
EMOTE_TO = '<:pwnyPortalTo:846831813136613376> '


class Portal(commands.Cog):
    """The Portal Bot system"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.guild_only()
    @command_decorator({'location': {'description': "The channel to portal to"}})
    async def portal(self, ctx: SlashContext, location: OptionType.CHANNEL) -> None:
        """Create a portal to a channel"""
        await ctx.send(EMOTE_FROM + f'<#{location.id}>')
        await location.send(f'<#{ctx.channel.id}>' + EMOTE_TO)


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Portal(bot))
