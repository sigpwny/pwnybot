import discord
from discord.ext import commands
import time
import random
from bot import EMOJI_NUMS, logger
NAME = "breakout"
VERSION = "1.0.0"
HELP_STR = '''
```
!breakout start <ROOMS> (prefix) - Creates ROOMS breakout rooms
!breakout end - Ends all breakout rooms
!breakout random - Move people into random breakout rooms that are currently waiting
```
'''


class BreakoutRooms(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.prefix = "$breakout "

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    async def destroy_channels(self, ctx):
        channels = ctx.guild.voice_channels
        for channel in channels:
            if 'VOICE' in channel.name:
                await channel.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"[pwnyBot] {NAME} is online")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        pass

    @commands.command()
    async def end(self, ctx):
        await self.destroy_channels(ctx)

    @commands.command()
    async def random(self, ctx):
        conn_members = next(
            filter(lambda x: 'WAITING' in x.name, ctx.guild.voice_channels)).members

        random.shuffle(conn_members)
        possible_chans = []
        for channel in ctx.guild.voice_channels:
            if '-VOICE-' in channel.name:
                possible_chans.append(channel)
        random.shuffle(possible_chans)
        for i, member in enumerate(conn_members):
            await member.move_to(possible_chans[i % len(possible_chans)])

    @commands.command()
    async def start(self, ctx, num, name=None):
        await self.destroy_channels(ctx)
        channel_prefix = ctx.author.name.split('#')[0]
        if name is not None:
            channel_prefix = name
        n = int(num)

        msg = await ctx.channel.send(f"Creating {n} Voice Channels ({''.join(EMOJI_NUMS[:n])}).")
        await ctx.guild.create_voice_channel("WAITING-VOICE")
        # Create a voice channel and reaction for each channel
        chans = []
        for i, e in enumerate(EMOJI_NUMS[:n]):
            await msg.add_reaction(e)
            chan = await ctx.guild.create_voice_channel(f"{channel_prefix}-VOICE-{i}")
            chans.append(chan)

        # Ensure that their reaction is one of the channel emojis
        def check_reply(reaction, user):
            return reaction.emoji in EMOJI_NUMS[:n]

        while True:
            # Every time someone reacts,
            # Move them to the correct channel, then send emoji of channel
            reaction, user = await self.client.wait_for('reaction_add', timeout=60*5, check=check_reply)
            logger.debug('Reacted to my ctx!')
            await ctx.channel.send(EMOJI_NUMS.index(reaction.emoji))
            await user.move_to(chans[EMOJI_NUMS.index(reaction.emoji)])


def setup(client):
    client.add_cog(BreakoutRooms(client))
