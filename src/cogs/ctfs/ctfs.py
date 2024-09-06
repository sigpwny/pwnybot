import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand
from lib.config import CTF_ROLES, UIUC_ROLES


class CTFs(Extension):
    '''Commands for opting in/out of CTFs'''

    @subcommand()
    async def optin(self, ctx: SlashContext):
        '''Add yourself to the CTF Team. Requires the UIUC role.'''
        if (ctx.guild == None):
            await ctx.send(":x: You can only run this command in a server.", ephemeral=True)
            return
        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: You aren't in the server! Are you a ghost?", ephemeral=True)
            return
        if (not any(user.has_role(role) for role in UIUC_ROLES)):
            await ctx.send(":x: You need to be UIUC verified to use this command. Verify yourself at <https://sigpwny.com/auth>.", ephemeral=True)
            return
        if (any(user.has_role(role) for role in CTF_ROLES)):
            await ctx.send(f":x: You already have the **:red_circle: CTF Team** role.", ephemeral=True)
            return

        await user.add_roles(CTF_ROLES)
        await ctx.send(f":white_check_mark: Added to **:red_circle: CTF Team**.")

    @subcommand()
    async def optout(self, ctx: SlashContext):
        '''Remove yourself from the CTF Team.'''
        if (ctx.guild == None):
            await ctx.send(":x: You can only run this command in a server.", ephemeral=True)
            return

        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: You aren't in the server! Are you a ghost?", ephemeral=True)
            return
        if (not any(user.has_role(role) for role in CTF_ROLES)):
            await ctx.send(f":x: You do not have the **:red_circle: CTF Team** role.", ephemeral=True)
            return

        await user.remove_roles(CTF_ROLES)
        await ctx.send(f":white_check_mark: Removed from **:red_circle: CTF Team**.")
