import interactions
from interactions import Extension, SlashContext

from lib.util import command, subcommand, sanitize_name
from lib.config import CTF_CATEGORY_CHANNEL

class CTF(Extension):
    '''Commands for managing ctf forums'''

    @subcommand(name={"description": "The name of the ctf"})
    # TODO uncomment
    # @interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
    async def create(self, ctx: SlashContext, name: str):
        '''Creates a forum for the ctf'''
        if (ctx.guild == None):
            await ctx.send("Must be invoked inside a guild")
            return

        name = sanitize_name("ctf-"+name, 100)
        forum = await ctx.guild.create_forum_channel(name=name, position=1000, category=CTF_CATEGORY_CHANNEL, available_tags=[

        ])
        # create tags
        # interactions.ThreadTag.create("web",emoji=interactions.PartialEmoji.)
        # pinned general

        await ctx.send(f"Created {name}")
