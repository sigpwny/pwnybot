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
            await ctx.send("Must be used inside a guild")
            return
        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send("User not in guild. This should be impossible.")
            return
        for role in UIUC_ROLES:
            if (user.has_role(role)):
                break
        else:  # this indentation is intentional
            await ctx.send("Must have UIUC role")
            return

        for role in CTF_ROLES:
            role = await ctx.guild.fetch_role(role)
            if (role):
                await user.add_role(role)
        await ctx.send("Added CTF role")

    @subcommand()
    async def optout(self, ctx: SlashContext):
        '''Remove the CTF role'''
        await ctx.send("not implemented")
