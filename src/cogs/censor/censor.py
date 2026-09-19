import interactions
from interactions import Extension, SlashContext

from lib.config import CENSOR_ROLE_ID
from lib.util import command


class Censor(Extension):
    """Commands for temporarily censoring members."""

    def __init__(self, _):
        self.censored_members: set[tuple[int, int]] = set()

    async def _can_manage_censorship(self, ctx: SlashContext) -> bool:
        if ctx.guild is None:
            await ctx.send(":x: You can only run this command in a server.", ephemeral=True)
            return False

        invoking_member = ctx.guild.get_member(ctx.user.id)
        if invoking_member is None or not invoking_member.has_role(CENSOR_ROLE_ID):
            await ctx.send(":x: You do not have permission to use this command.", ephemeral=True)
            return False

        return True

    @command(member={"description": "Member whose messages to delete"})
    async def censor(self, ctx: SlashContext, member: interactions.User) -> None:
        """Delete a member's messages in this channel until the bot restarts."""
        if not await self._can_manage_censorship(ctx):
            return

        censor_entry = (int(ctx.channel_id), int(member.id))
        if censor_entry in self.censored_members:
            await ctx.send(f":x: {member.mention} is already censored in this channel.", ephemeral=True)
            return

        self.censored_members.add(censor_entry)
        await ctx.send(
            f":white_check_mark: Censoring {member.mention} in this channel until the bot restarts.",
            ephemeral=True,
        )

    @command(member={"description": "Member whose messages to stop deleting"})
    async def uncensor(self, ctx: SlashContext, member: interactions.User) -> None:
        """Stop deleting a member's messages in this channel."""
        if not await self._can_manage_censorship(ctx):
            return

        censor_entry = (int(ctx.channel_id), int(member.id))
        if censor_entry not in self.censored_members:
            await ctx.send(f":x: {member.mention} is not censored in this channel.", ephemeral=True)
            return

        self.censored_members.remove(censor_entry)
        await ctx.send(
            f":white_check_mark: No longer censoring {member.mention} in this channel.",
            ephemeral=True,
        )

    @interactions.listen(interactions.api.events.MessageCreate)
    async def on_message_create(self, event: interactions.api.events.MessageCreate) -> None:
        message = event.message
        if (int(message.channel.id), int(message.author.id)) in self.censored_members:
            await message.delete()
