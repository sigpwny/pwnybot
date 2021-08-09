from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType as OptionType
from discord import utils
from lib.util import command_decorator, subcommand_decorator

EMOTE_FROM = "<:pwnyPortalFrom:846831813720932383> "
EMOTE_TO = '<:pwnyPortalTo:846831813136613376> '

def gen_link(message):
    return (
        "https://discord.com/channels/"
        + str(message.guild.id)
        + "/"
        + str(message.channel.id)
        + "/"
        + str(message.id)
        )

async def handle_portal(args, message):
    src_channel = message.channel

    if len(args) < 2:
        await src_channel.send("!portal #channel-name")
        return

    if len(args) > 2:
        await send_error_message(
            "Error",
            "Invalid channel name. Valid channel names are only one word long.",
            message,
        )
        return

    if message.channel_mentions:
        dst_channel = message.channel_mentions[0]
    else:
        dst_channel_name = (
            args[1] if args[1][1] != "#" else args[1][1:]
        )  # Skip starting '#'
        dst_channel = discord.utils.get(
            message.guild.text_channels, name=dst_channel_name
        )
        if dst_channel is None:
            try:
                dst_thread_id = int(args[1][2:-1])
                dst_channel = discord.utils.get(
                    message.guild.threads, id=dst_thread_id
                )
            except ValueError:
                pass
        if dst_channel is None:
            # TODO: Permissions & Confirmation/Undo
            if message.author.guild_permissions.manage_channels:
                try:
                    dst_channel = await message.guild.create_text_channel(
                        dst_channel_name, category=src_channel.category
                    )
                    # For some reason, setting position=0 in the creation doesn't update any other channel positions
                    await dst_channel.edit(position=0)
                except discord.errors.Forbidden as e:
                    await send_error_message(
                        "Error",
                        "Portals does not have permission to create channels in [{}]({}). If you believe that it should, talk to your server administrator.",
                        message,
                    )
                    return
            else:
                await send_error_message(
                    "Permission Error",
                    "You do not have the mannage channels permission in [{}]({}). If you believe that you should, talk to your server administrator.",
                    message,
                )
                return

    portalto, portalfrom = await get_emojis(message.guild)

    try:
        dst_message = await dst_channel.send(
            portalto + " " + src_channel.mention + " " + gen_link(message)
        )
        src_message = await src_channel.send(
            portalfrom + " " + dst_channel.mention + " " + gen_link(dst_message)
        )
        await dst_message.edit(
            content=portalto + " " + src_channel.mention + " " + gen_link(src_message)
        )
    except discord.errors.Forbidden as e:
        await send_error_message(
            "Error",
            "Portals does not have permission to send messages in [{}]({}). If you believe that is an error, talk to your server administrator.",
            message,
        )
        return

class Portal(commands.Cog):
    """The Portal Bot system"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.guild_only()
    @command_decorator({'location': {'description': "The channel to portal to"}})
    async def portal(self, ctx: SlashContext, location: OptionType.CHANNEL) -> None:
        """Create a portal to a channel"""
        # await ctx.send(EMOTE_FROM + f'<#{location.id}>')
        # await location.send(f'<#{ctx.channel.id}>' + EMOTE_TO)
        dst_msg = await location.send(
            EMOTE_TO + " " + ctx.message + " " + gen_link(ctx)
        )
        src_msg = await ctx.send(
            EMOTE_FROM # + " " + location.mention + " " 
        )


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Portal(bot))
