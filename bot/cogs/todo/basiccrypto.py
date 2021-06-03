# Imports go here
import discord
from discord.ext import commands
from base64 import b32encode, b64encode
from bot import logger
# REQUIRED INFORMATION for the bot to work!


class BasicCrypto(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[pwnyBot] {self.__class__.__name__} is online")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        content = message.content
        command = content.split(" ")[0]
        args = content.split(" ")[1:]
        if command[0] != '!':
            return

        try:
            if command == '!hex':
                response = str(hex(int(args[0])))[2:]
            elif command == '!b64':
                response = b64encode(args[0])
            elif command == '!b32':
                response = b32encode(args[0])
            else:
                return
            response = f'`{response}`'
        except Exception as e:
            logger.warning(f'WARNING: {e} on message: `{message}`')
            response = e
        await message.channel.send(response)


def setup(client):
    client.add_cog(BasicCrypto(client))
