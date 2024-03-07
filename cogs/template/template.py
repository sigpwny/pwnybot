from interactions import Extension, SlashContext

from lib.util import command_decorator, subcommand_decorator


class Template(Extension):
    '''Describe the cog'''

    @command_decorator(message={'description': "The message"}, times={'description': "# of times max 3"})
    async def reverserepeat(self, ctx: SlashContext, message: str, times: int = 1) -> None:
        """The reverserepeat command is pretty epic!! (/reverserepeat)

        """
        for _ in range(min(times, 3)):
            await ctx.send(message[::-1])

    @subcommand_decorator(message={'description': "The message"})
    async def say(self, ctx: SlashContext, message: str) -> None:
        """The message command is pretty epic!! (/template say)

        """
        await ctx.send(message)
