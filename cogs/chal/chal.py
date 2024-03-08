import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand, get_ctf_forum, logger


class Chal(Extension):
    '''Commands for managing challenges in a ctf forum'''

    @subcommand(name={"description": "The name of the challenge"}, category={"description": "the category of the challenge", "autocomplete": True})
    async def create(self, ctx: SlashContext, name: str, category: str) -> None:
        '''Creates a channel for the challenge'''
        await ctx.send("not implemented")

    @create.autocomplete("category")
    async def get_categories(self, ctx: interactions.AutocompleteContext):
        forum = await get_ctf_forum(ctx)
        if (forum == None or ctx.channel.name != "General"):
            await ctx.send(["Must be used inside a ctf forum's general channel"])
            return

        categories = set()
        for tag in forum.available_tags:
            categories.add(tag.name.removeprefix("solved-").removeprefix("unsolved-"))
        await ctx.send(categories)

    @subcommand(flag={"description": "The flag for the challenge"})
    async def solve(self, ctx: SlashContext, flag: str) -> None:
        '''Marks a challenge as solved with a flag'''
        await ctx.send("not implemented")
