from discord.ext.commands import Bot, errors
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator, logger
import os


class Manager(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @command_decorator({'cog': {'description': "The name of the cog. Default: All cogs"}})
    async def reload(self, ctx: SlashContext, cog: str = None) -> None:
        """Reloads a cog, effectively refreshing those slash commands
        """
        if cog is None:
            for cog in os.listdir("cogs"):
                try:
                    self.bot.reload_extension(f"cogs.{cog}.{cog}")
                    logger.info(f"Reloaded extension: {cog}")
                except errors.ExtensionNotLoaded:
                    self.bot.load_extension(f"cogs.{cog}.{cog}")
                    logger.info(f"Loaded new extension: {cog}")

            await ctx.send('All cogs were reloaded.')
        else:
            self.bot.reload_extension(f'cogs.{cog}.{cog}')
            logger.info(f"Reloaded extension: {cog}")
            await ctx.send(f'Cog "{cog}" was reloaded.')


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Manager(bot))
