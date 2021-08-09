from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType as OptionType
from discord import utils
from lib.util import command_decorator, subcommand_decorator
from lib.config import EMOTE_TO, EMOTE_FROM


def gen_link_msg(msg):
    return f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}"


class Portal(commands.Cog):
    """The Portal Bot system"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command_decorator(location={'description': "The channel to portal to"})
    async def portal(self, ctx: SlashContext, location: OptionType.CHANNEL) -> None:
        """Create a portal to a channel"""
        await ctx.defer()

        is_not_text = utils.get(
            ctx.guild.text_channels, id=location.id) is None
        if is_not_text:
            await ctx.send('That is not a text channel.')
            return

        src_msg = await ctx.send(
            EMOTE_FROM + f" <#{location.id}> "
        )
        dst_msg = await location.send(
            EMOTE_TO +
            f" <#{src_msg.channel.id}> " + gen_link_msg(src_msg)
        )

        await src_msg.edit(
            content=EMOTE_FROM +
            f" <#{dst_msg.channel.id}> " + gen_link_msg(dst_msg)
        )


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Portal(bot))
