from discord.ext.commands import Bot, errors
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator, logger
import os
import discord
from discord_slash.model import SlashCommandOptionType as OptionType
import DEFAULT_ARCHIVE_ID from lib.config


class Manager(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @subcommand_decorator(cog={'description': "The name of the cog. Default: All cogs"})
    async def reload(self, ctx: SlashContext, cog: str = None) -> None:
        """Reloads a cog, effectively refreshing those slash commands
        """
        if cog is None:
            for cog in os.listdir("cogs"):
                try:
                    self.bot.reload_extension(f"cogs.{cog}.{cog}")
                    logger.info(f"Reloaded extension: {cog}")
                except errors.ExtensionNotLoaded:
                    self.bot.load_extension(f"cogs.{cog}.{cog}")
                    logger.info(f"Loaded new extension: {cog}")

            await ctx.send('All cogs were reloaded.')
        else:
            self.bot.reload_extension(f'cogs.{cog}.{cog}')
            logger.info(f"Reloaded extension: {cog}")
            await ctx.send(f'Cog "{cog}" was reloaded.')

    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True, manage_roles=True)
    @subcommand_decorator(channel={'description': 'The channel to archive'}, archive_location={'description': 'The location to send the archival to'})
    async def archive(self, ctx: SlashContext, channel: OptionType.CHANNEL, archive_location: OptionType.CHANNEL = None) -> None:
        """Archives any channel but requires more permissions. This is very dangerous, use with caution.

        """
        await ctx.defer()
        is_not_text = discord.utils.get(
            ctx.guild.text_channels, id=channel.id) is None
        if is_not_text:
            ctx.send('That is not a text channel.')
            return

        if archive_location is None:
            archive_location = discord.utils.get(
                ctx.guild.channels, id=DEFAULT_ARCHIVE_ID)

        fname = f"{ctx.channel.category.name}_{ctx.channel.name}_log.txt"
        with open(fname, 'w') as fw:
            async for m in ctx.channel.history(limit=10000, oldest_first=True):
                fw.write(
                    f"[{m.created_at.replace().strftime('%Y-%m-%d %I:%M %p')} UTC] {m.author.display_name}: {m.content}\n{' '.join(map(lambda x: x.url, m.attachments))}\n"
                )
        # with open(fname, 'rb') as f:
        await archive_location.send(
            embed=discord.Embed(
                title=f"Discussion for the challenge {ctx.channel.name} has been archived. A text log of the conversation is attached."
            ),
            file=discord.File(fname),
        )

        os.remove(fname)

        await ctx.channel.delete()


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Manager(bot))
