import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand
from lib.config import CTF_ROLES, UIUC_ROLES


class CTFs(Extension):
    '''Commands for opting in/out of CTFs'''

    @subcommand()
    async def optin(self, ctx: SlashContext):
        '''Get the CTF role. Requires the UIUC role.'''
        if (ctx.guild == None):
            await ctx.send(":x: Must be used inside a guild.")
            return
        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: User not in guild. This should be impossible.")
            return
        if (not any(user.has_role(role) for role in UIUC_ROLES)):
            await ctx.send(":x: Must be UIUC verified.")
            return

        await user.add_roles(CTF_ROLES)
        await ctx.send("Added CTF role.")

    @subcommand()
    async def optout(self, ctx: SlashContext):
        '''Remove the CTF role'''
        if (ctx.guild == None):
            await ctx.send(":x: Must be used inside a guild.")
            return
        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: User not in guild. This should be impossible.")
            return

        await user.remove_roles(CTF_ROLES)
        await ctx.send("Removed CTF role.")
