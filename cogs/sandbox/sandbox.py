from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator


'''
compile_restricted uses a predefined policy that checks and modify the source code and checks
 against a restricted subset of the Python language. The compiled source code is still 
 executed against the full available set of library modules and methods.
'''
# Zope security imports
from RestrictedPython import compile_restricted
from RestrictedPython import Eval
from RestrictedPython import Guards
from RestrictedPython import safe_globals
from RestrictedPython import utility_builtins
from RestrictedPython.PrintCollector import PrintCollector
import builtins
import math
import json
from lib.util import Timeout
from .zope_sandbox import protected_inplacevar


def execute_untrusted(code):
    """Interprets the given python code inside a safe execution environment"""

    def safe_import(name, *args, **kwargs):
        whitelist = ['math', 'json', 'string', 're',
                     'random', 'datetime', 'itertools', 'time', 'requests']
        if name in whitelist:
            return __import__(name, *args, **kwargs)
        raise ImportError(
            f'Only allowed to import from `{", ".join(whitelist)}`')
    code += "\nresults = printed"
    byte_code = compile_restricted(
        code,
        filename="<string>",
        mode="exec",
    )
    policy_globals = {**safe_globals, **utility_builtins}
    policy_globals['__builtins__']['__metaclass__'] = type
    policy_globals['__builtins__']['__name__'] = type
    policy_globals['__builtins__']['__import__'] = safe_import
    policy_globals['_getattr_'] = Guards.safer_getattr
    policy_globals['_getiter_'] = Eval.default_guarded_getiter
    policy_globals['_getitem_'] = Eval.default_guarded_getitem
    policy_globals['_write_'] = Guards.full_write_guard
    policy_globals['_print_'] = PrintCollector
    policy_globals['_iter_unpack_sequence_'] = Guards.guarded_iter_unpack_sequence
    policy_globals['_unpack_sequence_'] = Guards.guarded_unpack_sequence
    policy_globals['enumerate'] = enumerate
    policy_globals['_inplacevar_'] = protected_inplacevar
    exec(byte_code, policy_globals, None)
    return policy_globals["results"]


class Sandbox(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command_decorator({})
    async def exec(self, ctx: SlashContext) -> None:
        """Execute your last code block message in a restricted python environment.

        """
        await ctx.defer()
        messages = await ctx.channel.history(limit=100).flatten()
        try:
            last_code_block = [m for m in messages if m.author.id ==
                               ctx.author.id and m.content.startswith('```')][0].content
        except IndexError:
            await ctx.send(f":x: You haven't made any code blocks!")
            return
        code = last_code_block[3:-3]

        try:
            with Timeout(seconds=10):
                exec_result = execute_untrusted(code)
                await ctx.send(f':white_check_mark: Executed:```\n{code}\n```\nResult:```{exec_result if exec_result else "None"}```')

        except TimeoutError:
            await ctx.send(':x: Error: Timeout of 10s exceeded')


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Sandbox(bot))
