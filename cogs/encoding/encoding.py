from base64 import b64encode, b64decode, b32encode, b32decode
from binascii import hexlify, unhexlify, Error as BinasciiError
import urllib.parse

from discord.ext import commands
from discord.ext.commands import Bot

from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from lib.util import command_decorator, subcommand_decorator


class Encoding(commands.Cog):
    """This cog provides simple encoding/decoding utilities."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @subcommand_decorator({'mode': {'description': 'Operation mode', "choices": ["encode", "decode"]}, 'data': {
        'description': "The data to encode or decode"
    }})
    async def base64(self, ctx: SlashContext, mode: str, data: str) -> None:
        '''Base64 encoding/decoding'''
        if mode == "encode":
            data = b64encode(data.encode()).decode()
        else:
            data = b64decode(data)
            try:
                data = data.decode()
            except UnicodeDecodeError:
                data = str(data)

        await ctx.send(f"```\n{data}\n```")

    @subcommand_decorator({'mode': {'description': 'Operation mode', "choices": ["encode", "decode"]}, 'data': {
        'description': "The data to encode or decode"
    }})
    async def base32(self, ctx: SlashContext, mode: str, data: str) -> None:
        '''Base32 encoding/decoding'''
        if mode == "encode":
            data = b32encode(data.encode()).decode()
        else:
            try:
                data = b32decode(data)
                data = data.decode()
            except BinasciiError as error:
                data = f"Error: {error}"
            except UnicodeDecodeError:
                data = str(data)

        await ctx.send(f"```\n{data}\n```")

    @subcommand_decorator({'mode': {'description': 'Operation mode', "choices": ["encode", "decode"]}, 'data': {
        'description': "The data to encode or decode"
    }})
    async def binary(self, ctx: SlashContext, mode: str, data: str) -> None:
        '''Binary encoding/decoding'''
        if mode == "encode":
            data = bin(int.from_bytes(data.encode(), "big"))[2:]
            data = "0" * (8 - len(data) % 8) + data
        else:
            data = data.strip().replace(" ", "")
            if all(digit in ("0", "1") for digit in data):
                data = int(data, 2)
                data = data.to_bytes(data.bit_length() // 8 + 1, "big")
                try:
                    data = data.decode()
                except UnicodeDecodeError:
                    data = str(data)
            else:
                data = "Error: Non-binary digits found"

        await ctx.send(f"```\n{data}\n```")

    @subcommand_decorator({'mode': {'description': 'Operation mode', "choices": ["encode", "decode"]}, 'data': {
        'description': "The data to encode or decode"
    }})
    async def hex(self, ctx: SlashContext, mode: str, data: str) -> None:
        '''Hex encoding/decoding'''

        if mode == "encode":
            data = hexlify(data.encode()).decode()
        else:
            data = data.strip().replace(" ", "")
            try:
                data = unhexlify(data)
                data = data.decode()
            except BinasciiError as error:
                data = f"Error: {error}"
            except UnicodeDecodeError:
                data = str(data)

        await ctx.send(f"```\n{data}\n```")

    @subcommand_decorator({'mode': {'description': 'Operation mode', "choices": ["encode", "decode"]}, 'data': {
        'description': "The data to encode or decode"
    }})
    async def url(self, ctx: SlashContext, mode: str, data: str) -> None:
        '''URL encoding/decoding'''
        if mode == "encode":
            data = urllib.parse.quote(data)
        else:
            data = urllib.parse.unquote(data)

        await ctx.send(f"```\n{data}\n```")


def setup(bot: Bot) -> None:
    bot.add_cog(Encoding(bot))
