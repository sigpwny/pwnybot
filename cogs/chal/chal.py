from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator, run_from_ctf, sanitize_channel_name, export_with_dce
import discord
from datetime import datetime
from lib.config import AUTOGENERATED_CHANNELS, HELPER_ROLE_ID, ADMIN_ROLE_ID
import os
import subprocess

class Chal(commands.Cog):
    """Challenge management for CTF"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.bot_has_permissions(manage_channels=True)
    @subcommand_decorator(name={'description': "The name of the challenge to create"})
    @run_from_ctf
    async def create(self, ctx: SlashContext, name: str) -> None:
        """
            Creates a new challenge inside a CTF
        """

        await ctx.defer()
        # Get CTF category called in
        category_folder = ctx.channel.category

        channel_name = sanitize_channel_name(name)

        if channel_name in AUTOGENERATED_CHANNELS.values():
            await ctx.send('Cannot create a challenge with the same name as an autogenerated channel.')
            return
        await ctx.guild.create_text_channel(
            name=channel_name,
            category=category_folder,
        )

        # Get bot channel and send embed

        embed = discord.Embed(
            title="🔔 New challenge created!",
            description=(
                f"**Challenge name:** {name}\n"
            ),
            colour=discord.Colour.dark_gold(),
        ).set_footer(text=datetime.strftime(datetime.now(), "%a, %d %B %Y, %H:%M UTC"))
        await ctx.send(embed=embed)

    @subcommand_decorator(flag={'description': "The flag for this challenge."})
    @run_from_ctf
    async def solve(self, ctx: SlashContext, flag: str) -> None:
        """Solves a CTF challenges

        """
        await ctx.defer()
        challenge = ctx.channel

        if challenge.name in AUTOGENERATED_CHANNELS.values():
            await challenge.send(f'You cannot solve the channel {challenge.name}!')
            return
        elif challenge.name.startswith('✔️'):
            await challenge.send(f'This challenge was already solved!')
            return

        embed = discord.Embed(
            title=f":white_check_mark: '{challenge.name}' was solved with the flag ||{flag}||"
        )
        await challenge.edit(name='✔️ ' + challenge.name)
        await ctx.send('Marked channel as solved.')
        logs_channel = discord.utils.get(
            challenge.category.text_channels, name=AUTOGENERATED_CHANNELS['logs'])

        await logs_channel.send(embed=embed)

        # TODO ctfd integration
        # raise NotImplementedError()

    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_any_role(HELPER_ROLE_ID, ADMIN_ROLE_ID)
    @subcommand_decorator()
    @run_from_ctf
    async def delete(self, ctx: SlashContext) -> None:
        """
        Deletes a CTF challenge channel
        """
        challenge = ctx.channel

        if challenge.name in AUTOGENERATED_CHANNELS.values():
            await challenge.send(f'You cannot delete the channel {challenge.name}!')
            return
        await ctx.channel.delete()

    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_any_role(HELPER_ROLE_ID, ADMIN_ROLE_ID)
    @subcommand_decorator()
    @run_from_ctf
    async def archive(self, ctx: SlashContext) -> None:
        """Archives a CTF challenge and puts data in log channel

        """
        challenge = ctx.channel

        logs_channel = discord.utils.get(
            challenge.category.text_channels, name=AUTOGENERATED_CHANNELS['logs'])
    
        if challenge.name in AUTOGENERATED_CHANNELS.values():
            await challenge.send(f'❌ You cannot archive {challenge.name}!')
            return
        
        progress_msg = await ctx.send(embed=discord.Embed(
                title="🔃 The challenge is being archived..."
            ))
        discord_filename_base = f'{challenge.id}_{challenge.category.name}_{sanitize_channel_name(challenge.name)}'

        try:
            filename_html = export_with_dce(challenge.id, type='html')
            filename_json = export_with_dce(challenge.id, type='json')
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
            
        await logs_channel.send(embed=discord.Embed(
            title=f"🗃️ The challenge '{challenge.name}' has been archived and is attached below."
        ))
        await logs_channel.send(file=discord.File(filename_html,f'{discord_filename_base}.html' ))
        await logs_channel.send(file=discord.File(filename_json, f'{discord_filename_base}.json' ))
        
        await ctx.channel.delete()
        
        os.remove(filename_html)
        os.remove(filename_json)



def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Chal(bot))
