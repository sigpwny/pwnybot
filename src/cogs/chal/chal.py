import typing

import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand, get_ctf_forum
from lib.config import FORUM_GENERAL_CHANNEL


class Chal(Extension):
    '''Commands for managing challenges in a CTF forum'''

    @subcommand(name={"description": "The name of the challenge"}, category={"description": "the category of the challenge", "autocomplete": True})
    async def create(self, ctx: SlashContext, name: str, category: str) -> None:
        '''Creates a channel for the challenge'''
        forum = await get_ctf_forum(ctx)
        if (forum == None or ctx.channel.name != FORUM_GENERAL_CHANNEL):
            await ctx.send(":x: Must be used inside a CTF forum's general channel.")
            return
        if ("unsolved" in category.lower()):
            await ctx.send(":x: Unsolved cannot be a category.")
            return
        for post in forum.get_posts(exclude_archived=False):
            post_name = post.name or ""
            # remove solved prefix
            if (post_name.startswith("✔-")):
                post_name = post_name[len("✔-"):]
            if (post_name.lower() == name.lower()):
                await ctx.send(f":x: Challenge {post.mention} already exists.")
                return

        # check valid category
        if (not any(tag.name == category for tag in forum.available_tags)):
            await ctx.send(f":x: Could not find category {category}.")
            return

        post = await forum.create_post(name=name, content=name, applied_tags=[category, "unsolved", "unsolved-"+category])
        await ctx.send(f"{ctx.user.mention} created {post.mention}.")

    @create.autocomplete("category")
    async def get_categories(self, ctx: interactions.AutocompleteContext):
        '''Autocomplete that provides challenge categories for chal create'''
        forum = await get_ctf_forum(ctx)
        if (forum == None or ctx.channel.name != FORUM_GENERAL_CHANNEL):
            await ctx.send(["Must be used inside a CTF forum's general channel."])
            return

        categories = [tag.name for tag in forum.available_tags if (ctx.input_text in tag.name) and ("unsolved" not in tag.name)]
        await ctx.send(categories)

    @subcommand(flag={"description": "The flag for the challenge"})
    async def solve(self, ctx: SlashContext, flag: str) -> None:
        '''Marks a challenge as solved with a flag'''
        forum = await get_ctf_forum(ctx)
        if (forum == None):
            await ctx.send(":x: Must be used inside a CTF forum.")
            return
        if (ctx.channel.name == FORUM_GENERAL_CHANNEL):
            await ctx.send(":x: Cannot be used inside a CTF forum's general channel.")
            return
        post = typing.cast(interactions.GuildForumPost, ctx.channel)
        if (not any(tag.name == "unsolved" for tag in post.applied_tags)):
            await ctx.send(":x: Challenge does not have unsolved tag.")
            return

        tags = [tag for tag in post.applied_tags if "unsolved" not in tag.name]
        await ctx.send("Marking challenge as solved.")
        await post.edit(name="✔-" + (post.name or ""), applied_tags=tags, archived=True)

        # send message in general
        for post in forum.get_posts(exclude_archived=False):
            if (post.name == FORUM_GENERAL_CHANNEL):
                await post.send(f"{ctx.user.mention} solved challenge {ctx.channel.mention} with ||{flag}||")
                return
