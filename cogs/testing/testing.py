import interactions
from interactions import Extension, SlashContext

from lib.util import command, subcommand, logger


class Testing(Extension):
    @subcommand(channel={"channel_types": [interactions.ChannelType.GUILD_FORUM]})
    async def remove(self, ctx: SlashContext, channel: interactions.GuildForum):
        if (ctx.guild == None):
            await ctx.send("Must be invoked inside a guild")
            return
        await ctx.guild.delete_channel(channel)
        await ctx.send(f"Removed {channel.name}")

    @subcommand()
    async def test(self, ctx: SlashContext, channel: interactions.GuildForum):
        logger.info(channel)
        logger.info(type(channel))
