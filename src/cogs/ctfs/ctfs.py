import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand
from lib.config import BOT_COMMANDS_CHANNEL_ID, CTF_ROLES, UIUC_ROLES


class CTFs(Extension):
    '''Commands for opting in/out of CTFs'''

    @subcommand()
    async def optin(self, ctx: SlashContext):
        '''Add yourself to the CTF Team. Requires the UIUC role.'''
        ephemeral = ctx.channel_id != BOT_COMMANDS_CHANNEL_ID
        if (ctx.guild == None):
            await ctx.send(":x: You can only run this command in a server.", ephemeral=ephemeral)
            return
        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: You aren't in the server! Are you a ghost?", ephemeral=ephemeral)
            return
        if (not any(user.has_role(role) for role in UIUC_ROLES)):
            await ctx.send(":x: You need to be UIUC verified to use this command. Verify yourself at <https://sigpwny.com/auth>.", ephemeral=ephemeral)
            return
        if (any(user.has_role(role) for role in CTF_ROLES)):
            await ctx.send(f":x: You already have the **:red_circle: CTF Team** role.", ephemeral=ephemeral)
            return

        await user.add_roles(CTF_ROLES)
        await ctx.send(f":white_check_mark: Added to **:red_circle: CTF Team**.", ephemeral=ephemeral)

    @subcommand()
    async def optout(self, ctx: SlashContext):
        '''Remove yourself from the CTF Team.'''
        ephemeral = ctx.channel_id != BOT_COMMANDS_CHANNEL_ID
        if (ctx.guild == None):
            await ctx.send(":x: You can only run this command in a server.", ephemeral=ephemeral)
            return

        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: You aren't in the server! Are you a ghost?", ephemeral=ephemeral)
            return
        if (not any(user.has_role(role) for role in CTF_ROLES)):
            await ctx.send(f":x: You do not have the **:red_circle: CTF Team** role.", ephemeral=ephemeral)
            return

        await user.remove_roles(CTF_ROLES)
        await ctx.send(f":white_check_mark: Removed from **:red_circle: CTF Team**.", ephemeral=ephemeral)
