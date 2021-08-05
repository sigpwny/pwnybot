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

        response = None
        print(args[0:])
        join_arg = ' '.join(args[0:])
        try:
            if command == '!hex':
                response = ''.join([hex(ord(c))[2:] for c in join_arg])
            if command == '!unhex':
                response = ''.join([chr(int(join_arg[i:i+2], 16))
                                    for i in range(0, len(join_arg), 2)])
            elif command == '!b64':
                response = b64encode(args[0].encode()).decode()
            elif command == '!b32':
                response = b32encode(args[0].encode()).decode()
            elif command == '!b64d':
                response = b64decode(args[0])
            elif command == '!b32d':
                response = b32decode(args[0])
            elif command == "!crypto":
                response = HELP
            else:
                return
            response = f'`{response}`'
        except Exception as e:
            logger.warning(f'WARNING: {e} on message: `{message}`')
            response = e

        print('Sending basiccrypto')
        await message.channel.send(response)


def setup(client):
    client.add_cog(BasicCrypto(client))
