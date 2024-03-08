from interactions import Extension, SlashContext

from lib.util import command, subcommand


class Chal(Extension):
    '''Commands for managing challenges in a ctf forum'''

    @subcommand(name={"description": "The name of the challenge"}, category={"description": "the category of the challenge"})
    async def create(self, ctx: SlashContext, name: str, category: None) -> None:
        '''Creates a channel for the challenge'''
        await ctx.send("not implemented")

    @subcommand(flag={"description": "The flag for the challenge"})
    async def solve(self, ctx: SlashContext, flag: str) -> None:
        '''Marks a challenge as solved with a flag'''
        await ctx.send("not implemented")
