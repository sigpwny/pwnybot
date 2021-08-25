from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import subcommand_decorator, Timeout
import subprocess
import os
import tempfile
import discord


class Binary(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @subcommand_decorator()
    async def rop(self, ctx: SlashContext):
        """Use ROPGadget to analyze file for gadgets
        """
        await ctx.defer()
        try:
            messages = await ctx.channel.history(limit=100).flatten()
            with Timeout(seconds=10):
                to_analyze = [m for m in messages if m.author.id ==
                              ctx.author.id and len(m.attachments) >= 1][0].attachments[0]

                _, temp_to_analyze_name = tempfile.mkstemp()
                await to_analyze.save(temp_to_analyze_name)

                new_file, filename = tempfile.mkstemp()
                cmd = ['ROPgadget', '--binary', temp_to_analyze_name]
                subprocess.run(cmd, stdout=new_file, check=True)
                await ctx.send(file=discord.File(filename, 'gadgets.txt'))

                os.remove(filename)
                os.remove(temp_to_analyze_name)
        except IndexError:
            await ctx.send(":x: Attach the file before analyzing.")
            return
        except TimeoutError:
            await ctx.send(':x: Result timed out')
        except subprocess.CalledProcessError:
            await ctx.send(':x: ROPgadget threw an error')


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Binary(bot))
