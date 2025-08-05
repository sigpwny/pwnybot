import asyncio
import traceback
import sys
import os
import tempfile

from cogs.reminders.watcher import reminder_watcher
import interactions
import aiohttp

from lib.util import logger
from lib.config import DISCORD_TOKEN


# Setup bot
bot = interactions.Client()


@interactions.listen()
async def on_ready() -> None:
    logger.info(f"{bot.user} connected.")
    logger.info(f"Hello, pwnybot is now live... do with that information what you will")

    asyncio.create_task(reminder_watcher(bot))

    await bot.change_presence(activity="Online!")


@interactions.listen(interactions.api.events.CommandError)
async def on_slash_command_error(event: interactions.api.events.CommandError) -> None:
    """Handle exceptions."""
    err = event.error
    ctx = event.ctx
    if isinstance(err, interactions.client.errors.NotFound):
        pass
    elif isinstance(err, interactions.client.errors.Forbidden):
        await ctx.send(":x: I don't have enough privileges to perform this action.")
    elif isinstance(err, interactions.client.errors.InteractionMissingAccess):
        await ctx.send(":x: I don't have enough privileges to perform this action :(")
    elif isinstance(err, aiohttp.ClientError):
        await ctx.send(":x: HTTP Client error.")
    else:
        await ctx.send(f":x: An error has occured.")
        body = ''.join(traceback.format_exception(
            type(err), err, err.__traceback__))
        if len(body) > 2000 - 6:
            new_file, filename = tempfile.mkstemp()
            os.write(new_file, body.encode('utf-8'))
            await ctx.send(file=interactions.File(filename, 'errors.txt'))
            os.remove(filename)
        else:
            await ctx.send(f"```{body}```")
    traceback.print_exception(
        type(err), err, err.__traceback__, file=sys.stderr)



if __name__ == "__main__":
    for ext in os.listdir("cogs"):
        bot.load_extension(f"cogs.{ext}.{ext}")
        logger.info(f"Loaded extension: {ext}")

    bot.start(DISCORD_TOKEN)
