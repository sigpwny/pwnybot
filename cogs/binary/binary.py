from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import subcommand_decorator
import subprocess
import os
import tempfile
import discord


class Binary(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @subcommand_decorator()
    async def rop(self, ctx: SlashContext) -> None:
        """Use ROPGadget to analyze file for gadgets

        """
        await ctx.defer()
        messages = await ctx.channel.history(limit=100).flatten()
        try:
            to_analyze = [m for m in messages if m.author.id ==
                          ctx.author.id and len(m.attachments) >= 1][0].attachments[0]
            await to_analyze.save('to_analyze')
            cmd = ['ROPgadget', '--binary', 'to_analyze']
            new_file, filename = tempfile.mkstemp()
            subprocess.run(cmd, stdout=new_file)

            await ctx.send(file=discord.File(filename, 'gadgets.txt'))
            # Cleanup
            os.remove(filename)
            os.remove(to_analyze)
        except IndexError:
            await ctx.send(":x: Attach the file before analyzing.")
            return


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Binary(bot))
