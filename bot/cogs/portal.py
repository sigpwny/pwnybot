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
        self.prefixes = ['$']
        self.portal_from = None
        self.portal_from_message = None

    def cog_check(self, ctx):
        return ctx.prefix in self.prefixes

    @ commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[pwnyBot] {self.__class__.__name__} is online")

    @ commands.command(aliases=['p'])
    async def portal(self, ctx, location=None):
        if ctx.author == self.client.user:
            return
        if location is not None:
            try:
                await self.client.get_channel(int(location[2:-1])).send(EMOTE_FROM + f'<#{ctx.channel.id}>')
                await ctx.send(f'{location}' + EMOTE_TO)
                await ctx.message.delete()
            except ValueError:
                await ctx.send(f'Channel "{location}" not found.')
                await ctx.message.delete()
            return
        if self.portal_from is None:
            # This is the original portal, just set variable
            self.portal_from = ctx.channel.id
            self.portal_from_message = ctx.message
        else:
            # This is the 'to' portal, do magic.
            await self.client.get_channel(self.portal_from).send(EMOTE_FROM + f'<#{ctx.channel.id}>')
            await ctx.send(f'<#{self.portal_from}>' + EMOTE_TO)
            self.portal_from = None
            await ctx.message.delete()
            await self.portal_from_message.delete()


def setup(client):
    client.add_cog(Portal(client))
