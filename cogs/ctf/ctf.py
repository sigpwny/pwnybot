import interactions
from interactions import Extension, SlashContext

from lib.util import command, subcommand


class CTF(Extension):
    '''Commands for managing ctf forums'''

    @subcommand(name={"description": "The name of the ctf"})
    @interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
    async def create(self, ctx: SlashContext, name: str):
        '''Creates a forum for the ctf'''
        await ctx.send("not implemented")
