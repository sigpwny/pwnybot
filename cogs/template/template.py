from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator


class Template(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command_decorator({'message': {'description': "The message (description is optional)"}})
    async def ping(self, ctx: SlashContext, message: str, times: int = 1) -> None:
        """The ping command is pretty epic!! (/echo)

        """
        for _ in range(times):
            await ctx.send(message)

    @subcommand_decorator({'message': {'description': "The message (description is optional)"}})
    async def sub_echo(self, ctx: SlashContext, message: str, times: int = 1) -> None:
        """The sub_echo command is pretty epic!! (/template sub_echo)

        """
        for _ in range(times):
            await ctx.send(message)


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Template(bot))
