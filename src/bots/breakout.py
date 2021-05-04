# Imports go here
import discord
from discord.ext import commands
import time
import random
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

    async def destroy_channels(self, message):
        channels = message.guild.voice_channels
        for channel in channels:
            if 'VOICE' in channel.name:
                await channel.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[pwnyBot] {NAME} is online")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        txt = message.content
        isbreakout = txt.lower().startswith('!breakout')
        args = txt.split(' ')
        if not isbreakout:
            return

        if len(args) == 1:
            await message.channel.send(HELP_STR)
        elif args[1] == 'ping':
            await message.channel.send("Pong!")
        elif args[1] == 'end':
            await self.destroy_channels(message)
        elif args[1] == 'random':
            conn_members = next(
                filter(lambda x: 'WAITING' in x.name, message.guild.voice_channels)).members

            random.shuffle(conn_members)
            possible_chans = []
            for channel in message.guild.voice_channels:
                if '-VOICE-' in channel.name:
                    possible_chans.append(channel)
            random.shuffle(possible_chans)
            for i, member in enumerate(conn_members):
                await member.move_to(possible_chans[i % len(possible_chans)])
        elif args[1] == 'start':
            if len(args) < 3 or not args[2].isdigit():
                await message.channel.send('!breakout start <N> (name?)')
                return
            await self.destroy_channels(message)
            channel_prefix = message.author.name.split('#')[0]
            if len(args) >= 4:
                channel_prefix = args[3]
            n = int(args[2])
            emojiset = ['0️⃣', '1️⃣', '2️⃣', '3️⃣',
                        '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
            msg = await message.channel.send(f"Creating {n} Voice Channels ({''.join(emojiset[:n])}).")
            await message.guild.create_voice_channel("WAITING-VOICE")
            # Create a voice channel and reaction for each channel
            chans = []
            for i, e in enumerate(emojiset[:n]):
                await msg.add_reaction(e)
                chan = await message.guild.create_voice_channel(f"{channel_prefix}-VOICE-{i}")
                chans.append(chan)

            # Ensure that their reaction is one of the channel emojis
            def check_reply(reaction, user):
                return reaction.emoji in emojiset[:n]

            while True:
                # Every time someone reacts,
                # Move them to the correct channel, then send emoji of channel
                reaction, user = await self.client.wait_for('reaction_add', timeout=60*5, check=check_reply)
                print('Reacted to my message!')
                await message.channel.send(emojiset.index(reaction.emoji))
                await user.move_to(chans[emojiset.index(reaction.emoji)])


def setup(client):
    client.add_cog(BreakoutRooms(client))
