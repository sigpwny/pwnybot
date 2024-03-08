import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand, logger


class CTF(Extension):
    '''Commands for managing ctf forums'''

    @subcommand()
    @interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
    async def auth_check(self, ctx: SlashContext, message: str, aaa: str) -> None:
        '''check if discord permissions is AND or OR'''
        await ctx.send("passed")
