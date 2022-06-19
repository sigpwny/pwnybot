from discord.ext.commands import Bot, errors
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import sanitize_channel_name, subcommand_decorator, logger, export_with_dce
import os
import subprocess
import discord
from discord_slash.model import SlashCommandOptionType as OptionType
from lib.config import DEFAULT_ARCHIVE_ID, HELPER_ROLE_ID, ADMIN_ROLE_ID


class Manager(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot


    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_any_role(HELPER_ROLE_ID, ADMIN_ROLE_ID)
    @subcommand_decorator(channel={'description': 'The channel to archive'}, archive_location={'description': 'The location to send the archival to'})
    async def archive(self, ctx: SlashContext, channel: OptionType.CHANNEL, archive_location: OptionType.CHANNEL = None) -> None:
        """Archives any channel

        """

        if archive_location is None:
            archive_location = discord.utils.get(
                ctx.guild.text_channels, id=DEFAULT_ARCHIVE_ID)
    
        progress_msg = await ctx.send(embed=discord.Embed(
                title=f"🔃 The channel is currently being archived..."
            ))
        discord_filename_base = f'{channel.id}_{channel.category.name}_{sanitize_channel_name(channel.name)}'

        try:
            filename_html = export_with_dce(channel.id, type='html')
            filename_json = export_with_dce(channel.id, type='json')
        except TimeoutError:
            await progress_msg.edit(
                embed=discord.Embed(
                    title=f"❌ The command timed out."
                )
            )
            return
        except subprocess.CalledProcessError:
            await progress_msg.edit(
                embed=discord.Embed(
                    title=f"❌ The export application failed!"
                )
            )
            return
            
        await archive_location.send(
            embed=discord.Embed(
                title=f"🗃️ The channel #{channel.name} has been archived and is attached below."
            )
        )
        await archive_location.send(file=discord.File(filename_html,f'{discord_filename_base}.html' ))
        await archive_location.send(file=discord.File(filename_json, f'{discord_filename_base}.json' ))
        
        await progress_msg.edit(
            embed=discord.Embed(
                title=f"✅ The channel #{channel.name} has been archived and is ready for removal!"
            )
        )
        
        os.remove(filename_html)
        os.remove(filename_json)

    @commands.has_any_role(HELPER_ROLE_ID, ADMIN_ROLE_ID)
    @subcommand_decorator(cog={'description': "The name of the cog. Default: All cogs"})
    async def reload(self, ctx: SlashContext, cog: str = None) -> None:
        """Reloads a cog, effectively refreshing those slash commands
        """
        await ctx.defer()
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

    # @commands.bot_has_permissions(manage_channels=True)
    # @commands.has_any_role(HELPER_ROLE_ID, ADMIN_ROLE_ID)
    # @subcommand_decorator(channel={'description': 'The channel to archive'}, archive_location={'description': 'The location to send the archival to'})
    # async def archive(self, ctx: SlashContext, channel: OptionType.CHANNEL, archive_location: OptionType.CHANNEL = None) -> None:
    #     """Archives any channel but requires more permissions. This is dangerous, use with caution.

    #     """
    #     await ctx.defer()
    #     is_not_text = discord.utils.get(
    #         ctx.guild.text_channels, id=channel.id) is None
    #     if is_not_text:
    #         ctx.send('That is not a text channel.')
    #         return



    #     fname = f"{channel.id}_{channel.category.name}_{channel.name}_log.txt"
    #     with open(fname, 'w') as fw:
    #         async for m in channel.history(limit=10000, oldest_first=True):
    #             fw.write(
    #                 f"[{m.created_at.replace().strftime('%Y-%m-%d %I:%M %p')} UTC] {m.author.display_name}: {m.content}\n{' '.join(map(lambda x: x.url, m.attachments))}\n"
    #             )

    #     await archive_location.send(
    #         embed=discord.Embed(
    #             title=f"The channel '{channel.name}' has been archived. A text log of the conversation is attached."
    #         ),
    #         file=discord.File(fname),
    #     )

    #     os.remove(fname)

    #     await ctx.send(f"The channel <#{channel.id}> is ready to be archived, a text log of the channel can be found in <#{archive_location.id}>")


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Manager(bot))
