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
            await ctx.send("Must be used inside a CTF forum's general channel")
            return
        if (category == "unsolved"):
            await ctx.send("Unsolved cannot be a category")
            return
        for post in forum.get_posts(exclude_archived=False):
            if ((post.name or "") == name):
                await ctx.send(f"Challenge {name} already exists")
                return

        # check valid category
        for tag in forum.available_tags:
            if (tag.name == category):
                await forum.create_post(name=name, content=name, applied_tags=[tag, "unsolved"])
                await ctx.send(f"Created {name}")
                return

        await ctx.send(f"Could not find category {category}")

    @create.autocomplete("category")
    async def get_categories(self, ctx: interactions.AutocompleteContext):
        forum = await get_ctf_forum(ctx)
        if (forum == None or ctx.channel.name != FORUM_GENERAL_CHANNEL):
            await ctx.send(["Must be used inside a CTF forum's general channel"])
            return

        categories = [tag.name for tag in forum.available_tags if ctx.input_text in tag.name and tag.name != "unsolved"]
        await ctx.send(categories)

    @subcommand(flag={"description": "The flag for the challenge"})
    async def solve(self, ctx: SlashContext, flag: str) -> None:
        '''Marks a challenge as solved with a flag'''
        forum = await get_ctf_forum(ctx)
        if (forum == None):
            await ctx.send("Must be used inside a CTF forum")
            return
        if (ctx.channel.name == FORUM_GENERAL_CHANNEL):
            await ctx.send("Cannot be used inside a CTF forum's general channel")
            return

        post = typing.cast(interactions.GuildForumPost, ctx.channel)
        tags = post.applied_tags
        for tag in tags:
            if (tag.name == "unsolved"):
                tags.remove(tag)
        await ctx.send("Marking channel as solved")
        await post.edit(applied_tags=tags, archived=True)
