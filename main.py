# from config import ()
import traceback
import logging
import sys
import os

import discord
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Bot

from discord_slash import SlashCommand, SlashContext

import aiohttp

from lib.util import logger
from lib.config import DISCORD_TOKEN

# Setup logging


# Setup bot
bot = Bot(command_prefix="!", description="Pwnybot - CTF helper bot")
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)


@bot.event
async def on_ready() -> None:

    logger.info(f"{bot.user} connected.")
    logger.info(
        f"Hello, pwnybot is now live... do with that information what you will")
    await bot.change_presence(activity=discord.Game(name="Online!"))


@bot.event
async def on_slash_command_error(ctx: SlashContext, err: Exception) -> None:
    """Handle exceptions."""
    if isinstance(err, commands.errors.CommandNotFound):
        pass
    elif isinstance(err, discord.errors.NotFound):
        pass
    elif isinstance(err, discord.errors.Forbidden):
        await ctx.send("Forbidden.")
    elif isinstance(err, commands.errors.MissingPermissions):
        await ctx.send("Permission denied.")
    elif isinstance(err, commands.errors.BotMissingPermissions):
        await ctx.send("I don't have enough privileges to perform this action :(")
    elif isinstance(err, commands.errors.NoPrivateMessage):
        await ctx.send("This command can't be used in DM.")
    elif isinstance(err, aiohttp.ClientError):
        await ctx.send("HTTP Client error.")
    else:
        await ctx.send(f"❌ An error has occured")

    await ctx.send(f"\n```{''.join(traceback.format_exception(type(err), err, err.__traceback__))}```")
    traceback.print_exception(
        type(err), err, err.__traceback__, file=sys.stderr)


if __name__ == "__main__":
    # for task in os.listdir("tasks"):
    #     task = task.strip(".py")
    #     bot.load_extension(f"tasks.{task}")
    #     logger.info(f"Loaded task: {task}")
    for ext in os.listdir("cogs"):
        bot.load_extension(f"cogs.{ext}.{ext}")
        logger.info(f"Loaded extension: {ext}")

    bot.run(DISCORD_TOKEN)
