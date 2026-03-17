import asyncio
import http.client

import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand, IS_ADMIN


class Manager(Extension):
    '''Commands for managing the discord server'''

    @subcommand(channel={'description': 'The channel to send the message in', 'channel_types': [interactions.ChannelType.GUILD_TEXT]})
    @IS_ADMIN
    async def say(self, ctx: SlashContext, channel: interactions.GuildText) -> None:
        '''
        Says your previous message in the channel you specify
        '''
        await ctx.defer()
        try:
            messages = await ctx.channel.history(limit=100).flatten()
            message = [m for m in messages if m.author.id == ctx.author.id][0].content
        except IndexError:
            await ctx.send(":x: Send the message in the current channel before calling /manager edit.")
            return

        confirm_message = await ctx.send(f'Should I send this in {channel.mention}? (60s expiry):\n{message}\n')

        await confirm_message.add_reaction('✅')

        def check(event: interactions.events.MessageReactionAdd):
            return event.message.id == confirm_message.id and \
                event.author == ctx.author and event.emoji.name == '✅'
        try:
            await self.bot.wait_for(interactions.events.MessageReactionAdd, checks=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send(':x: Timed out, did not send.')
            return

        await channel.send(message)
        await ctx.send(f':white_check_mark: sent message in {channel.mention}')

    @subcommand(message_channel={'description': 'The channel of the original message', 'channel_types': [interactions.ChannelType.GUILD_TEXT]}, message_id={'description': 'The ID of the message to edit'})
    @IS_ADMIN
    async def edit(self, ctx: SlashContext, message_channel: interactions.GuildText, message_id: str) -> None:
        '''
        Edits a message said by the bot, must specify the messageID 
        '''
        await ctx.defer()
        try:
            bot_message = await message_channel.fetch_message(message_id)
        except (http.client.HTTPException, ValueError):
            await ctx.send(":x: Invalid message_id")
            return
        if (bot_message is None):
            await ctx.send(":x: Unable to find message")
            return
        if (bot_message.author != self.bot.user):
            await ctx.send(":x: Message must be from the bot")
            return

        try:
            messages = await ctx.channel.history(limit=100).flatten()
            message = [m for m in messages if m.author.id == ctx.author.id][0].content
        except IndexError:
            await ctx.send(":x: Send the message in the current channel before calling /manager edit.")
            return

        confirm_message = await ctx.send(f'Should I edit the message you specified to say this? (60s expiry):\n{message}\n')

        await confirm_message.add_reaction('✅')

        def check(event: interactions.events.MessageReactionAdd):
            return event.message.id == confirm_message.id and \
                event.author == ctx.author and event.emoji.name == '✅'
        try:
            await self.bot.wait_for(interactions.events.MessageReactionAdd, checks=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send(':x: Timed out, did not edit message.')
            return

        await bot_message.edit(content=message)
        await ctx.send(f':white_check_mark: edited message.')

    @subcommand(
        role_name={'description': 'The name of the role to assign'},
        usernames={'description': 'A comma-separated list of usernames (e.g. "user1, user2")'}
    )
    @IS_ADMIN
    async def assign_roles(self, ctx: SlashContext, role_name: str, usernames: str) -> None:
        '''
        Assigns a role to a list of users by username.
        '''
        await ctx.defer()

        user_list = [u.strip() for u in usernames.replace(", ", ",").split(",") if u.strip()]
        if not user_list:
            await ctx.send(":x: Please provide a comma-separated list of usernames.")
            return

        guild = ctx.guild
        if guild is None:
            await ctx.send(":x: Could not determine the guild context.")
            return
        
        role = next((r for r in guild.roles if r.name == role_name), None)
        if not role:
            await ctx.send(f":x: Role '{role_name}' not found.")
            return

        assigned = []
        not_found = []
        for username in user_list:
            member = next((m for m in guild.members if m.user.username == username), None)
            if member:
                try:
                    await member.add_role(role)
                    assigned.append(username)
                except Exception:
                    not_found.append(username)
            else:
                not_found.append(username)

        msg = ""
        if assigned:
            msg += f":white_check_mark: Assigned role '{role_name}' to: {', '.join(assigned)}\n"
        if not_found:
            msg += f":x: Could not find or assign role to: {', '.join(not_found)}"
        await ctx.send(msg or ":x: No users processed.")
