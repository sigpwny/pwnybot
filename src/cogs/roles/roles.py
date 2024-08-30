import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand
from lib.config import UIUC_ROLES, PRIVATE_ROLES


class Roles(Extension):
    '''Commands for managing private roles'''

    def __init__(self, _):
        self.roles = PRIVATE_ROLES

    @subcommand(role={"description": "Role to add","autocomplete": True})
    async def add(self, ctx: SlashContext, role: str) -> None:
        """Add a private role. Requires the UIUC role."""
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
        for valid_role in self.roles:
            valid_role_name = valid_role.get("name")
            valid_role_id = valid_role.get("discord_role_id")
            if not valid_role_name or not valid_role_id:
                continue
            if role == valid_role_name:
                if user.has_role(valid_role_id):
                    await ctx.send(f":x: You already have the **{role}** role.", ephemeral=True)
                    return
                await user.add_role(valid_role_id)
                await ctx.send(f":white_check_mark: Added you to **{role}**.", ephemeral=True)
                return
        await ctx.send(":x: Invalid role.")

    @subcommand(role={"description": "Role to remove","autocomplete": True})
    async def remove(self, ctx: SlashContext, role: str) -> None:
        """Removes a private role."""
        if (ctx.guild == None):
            await ctx.send(":x: You can only run this command in a server.", ephemeral=True)
            return
        user = ctx.guild.get_member(ctx.user.id)
        if (user == None):
            await ctx.send(":x: You aren't in the server! Are you a ghost?", ephemeral=True)
            return
        for valid_role in self.roles:
            valid_role_name = valid_role.get("name")
            valid_role_id = valid_role.get("discord_role_id")
            if not valid_role_name or not valid_role_id:
                continue
            if role == valid_role_name:
                if not user.has_role(valid_role_id):
                    await ctx.send(f":x: You do not have the **{role}** role.", ephemeral=True)
                    return
                await user.remove_role(valid_role_id)
                await ctx.send(f":white_check_mark: Removed you from **{role}**.", ephemeral=True)
                return
        await ctx.send(":x: Invalid role.")

    @add.autocomplete("role")
    @remove.autocomplete("role")
    async def find_role(self, ctx: interactions.AutocompleteContext):
        current_input = ctx.kwargs.get("role")
        autocomplete_options = []
        for valid_role in self.roles:
            valid_role_name = valid_role.get("name")
            if valid_role_name and current_input in valid_role_name:
                autocomplete_options.append(valid_role_name)
        await ctx.send(autocomplete_options[:25])
