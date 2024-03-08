from interactions import Extension, SlashContext

from lib.util import command, subcommand


class Template(Extension):
    '''Describe the cog'''

    @command(message={'description': "The message"}, times={'description': "# of times max 3", "max_value": 3, "min_value": 1})
    async def reverserepeat(self, ctx: SlashContext, message: str, times: int = 1) -> None:
        '''The reverserepeat command is pretty epic!! (/reverserepeat)'''
        for _ in range(times):
            await ctx.send(message[::-1])

    @subcommand(message={'description': "The message"})
    async def say(self, ctx: SlashContext, message: str) -> None:
        '''The message command is pretty epic!! (/template say)'''
        await ctx.send(message)
