from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator


class Template(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command_decorator(message={'description': "The message"}, times={'description': "# of times max 3"})
    async def repeat(self, ctx: SlashContext, message: str, times: int = 1) -> None:
        """The repeat command is pretty epic!! (/repeat)

        """
        for _ in range(min(times, 3)):
            await ctx.send(message)

    @subcommand_decorator(message={'description': "The message"})
    async def say(self, ctx: SlashContext, message: str) -> None:
        """The message command is pretty epic!! (/template message)

        """
        await ctx.send(message)


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Template(bot))
