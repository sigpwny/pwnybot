# Imports go here
import discord
from discord.ext import commands
import time

NAME = "breakout"
VERSION = "1.0.0"
HELP_STR = '''
```
!breakout <number> <prefix> <random/choice>
!breakout start
!breakout end
```
'''

# reaction_emoji_map = [
#     :a::b::regional_indicator_c::regional_indicator_d:
# ]


class BreakoutRooms(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[pwnyBot] {NAME} is online")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # reaction.user().flatten()
        if reaction.message.author == self.client.user:
            await reaction.message.channel.send('I reacted to me?')
        print(reaction, user)

    @commands.Cog.listener()
    async def on_message(self, message):
        print(type(self.client))
        print(message)
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
            await message.channel.send('Duplicating process...')
        elif args[1] == 'start':
            await message.channel.send('Killing process...')
        else:
            emojiset = ['0️⃣', '1️⃣', '2️⃣', '3️⃣',
                        '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
            n = 3
            msg = await message.channel.send("Creating 2 Voice Channels, A, and B. React to go to that one.")
            chans = []
            for i, e in enumerate(emojiset[:n]):
                print(e)
                await msg.add_reaction(e)
                chan = await message.guild.create_voice_channel(f"VOICE CHANNEL TEST{i}")
                chans.append(chan)

            def check_reply(reaction, user):
                print(reaction, user, message.author)
                return user == message.author and reaction.emoji in emojiset[:n]

            reaction, user = await self.client.wait_for('reaction_add', check=check_reply)
            await user.move_to(chan[emojiset.index(reaction)])
            await message.channel.send(reaction)


def setup(client):
    client.add_cog(BreakoutRooms(client))
