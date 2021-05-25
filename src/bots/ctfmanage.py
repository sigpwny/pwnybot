import discord
from discord.ext import commands

NAME = "ctfmanage"
VERSION = "1.0.0"

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)

class CTFManage(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("[pwnyBot] " + NAME + " is online")

    @commands.command(name='new', help='Creates category and channels for new ctf event.')
    async def new(self,ctx, ctfname):
        guild = ctx.guild # define guild

        # check if category exists before creating it
        existing_category = discord.utils.get(guild.categories, name=ctfname)
        if not existing_category:
            print(f'Creating a new category: {ctfname}')
            await guild.create_category(ctfname) # create category
            category = discord.utils.get(ctx.guild.categories, name=ctfname) # create category object

            # define-channels
            channels = [f'{ctfname}-general', f'{ctfname}-i-solved-a-chal', f'{ctfname}-pwn-🔨', f'{ctfname}-re-🔬', f'{ctfname}-web-🕸', f'{ctfname}-crypto-🧮', f'{ctfname}-forensics-🔍', f'{ctfname}-misc-🤡']
            for channel in channels:
                # check if channel exists before making the channel
                existing_channel = discord.utils.get(guild.channels, name=channel)
                if not existing_channel:
                    print(f'Creating a new channel: {channel}')
                    await guild.create_text_channel(channel, category=category) # make channels under category
                else:
                    await ctx.send(f'You already created {channel}.')
        else:
            await ctx.send('You already created this event.')

    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have the correct role for this command.')

def setup(client):
    client.add_cog(CTFManage(client))