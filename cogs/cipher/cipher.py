from string import ascii_lowercase, ascii_uppercase

from discord.ext import commands
from discord.ext.commands import Bot

from lib.util import subcommand_decorator, Timeout
from ciphey import decrypt
from ciphey.iface import Config
from ciphey import iface
from rich.console import Console

console = Console(color_system=None, no_color=True, width=120)


class ClassicCiphers:
    """Implementation of some basic classic ciphers."""

    @staticmethod
    def caesar(message: str, key: int) -> str:
        return "".join(
            chr((ord(i) - (97, 65)[i.isupper()] + key) %
                26 + (97, 65)[i.isupper()])
            if i.isalpha()
            else i
            for i in message
        )

    @staticmethod
    def rot13(message: str) -> str:
        return ClassicCiphers.caesar(message, 13)

    @staticmethod
    def atbash(message: str) -> str:
        return message.translate(
            {
                **str.maketrans(ascii_lowercase, ascii_lowercase[::-1]),
                **str.maketrans(ascii_uppercase, ascii_uppercase[::-1]),
            }
        )


class Cipher(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @subcommand_decorator(message={'description': 'The message to encrypt/decrypt'}, key={'description': 'The key to encrypt/decrypt with (default: brute-force)'})
    async def caesar(self, ctx, message: str, key: int = None):
        '''
        Caesar Cipher
        '''
        if key is None:
            result = "\n".join(
                f"{key:>2} | {ClassicCiphers.caesar(message, key)}"
                for key in range(1, 26)
            )
        else:
            result = ClassicCiphers.caesar(message, int(key))

        await ctx.send(f"```\n{result}\n```")

    @subcommand_decorator(message={'description': 'The message to encrypt/decrypt'})
    async def auto(self, ctx, message: str):
        '''
        Decodes message using ciphey
        '''
        await ctx.defer()
        await ctx.send('Decoding using ciphey for 30 seconds...')
        try:
            with Timeout(seconds=30):
                config = Config().library_default().complete_config()
                res = config.objs["searcher"].search(message)
                body = iface.pretty_search_results(res)
                with console.capture() as capture:
                    console.print(body)

                await ctx.send(f'```\n{capture.get()}\n```')
        except TimeoutError:
            await ctx.send('Could not decrypt :/')

    @subcommand_decorator(message={'description': 'The message to encrypt/decrypt'})
    async def rot13(self, ctx, message: str):
        '''
        Rot13 (caesar) cipher
        '''
        await ctx.send(f"```\n{ClassicCiphers.rot13(message)}\n```")

    @subcommand_decorator(message={'description': 'The message to encrypt/decrypt'})
    async def atbash(self, ctx, message: str):
        '''
        Atbash cipher
        '''
        await ctx.send(f"```\n{ClassicCiphers.atbash(message)}\n```")


def setup(bot: Bot) -> None:
    bot.add_cog(Cipher(bot))
