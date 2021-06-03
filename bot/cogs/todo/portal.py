'''
pwnyBot skeleton code. Please use this as a skeleton for any commands you intend to add.
Yes there is problably a better way to do it, but unless you are willing to refactor EVERYTHING, then dont mess with it.
'''
import discord
from discord.ext import commands
from bot import logger

EMOTE_FROM = "<:pwnyPortalFrom:846831813720932383> "
EMOTE_TO = '<:pwnyPortalTo:846831813136613376> '


class Portal(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.prefix = '$portal '

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[pwnyBot] {self.__class__.__name__} is online")

    @commands.command()
    async def portal(self, ctx, channel):
        if ctx.author == self.client.user:
            return

        # Get the portal channel and format the response
        response = EMOTE_FROM + channel

        # Check if portal channel exists, send message in both the channels if so
        try:
            portalChannel = self.client.get_channel(int(channel))
            await ctx.channel.send(response)
            await portalChannel.send(f'<#{ctx.channel.id}>' + EMOTE_TO)
        except Exception:
            response = 'Channel does not exist!'
            await ctx.channel.send(response)


def setup(client):
    client.add_cog(Portal(client))
