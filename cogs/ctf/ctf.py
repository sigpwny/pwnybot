import interactions
from interactions import Extension, SlashContext

from lib.util import subcommand, sanitize_name
from lib.config import CTF_CATEGORY_CHANNELS, CHALLENGE_CATEGORIES

class CTF(Extension):
    '''Commands for managing ctf forums'''

    @subcommand(name={"description": "The name of the ctf"})
    @interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
    async def create(self, ctx: SlashContext, name: str):
        '''Creates a forum for the ctf'''
        if (ctx.guild == None):
            await ctx.send("Must be invoked inside a guild")
            return

        ctf_name = sanitize_name("ctf-"+name, 100)
        # find category channel
        category_channel = None
        for cat in CTF_CATEGORY_CHANNELS:
            if (ctx.guild.get_channel(cat) != None):
                category_channel = cat
        tags = [variant+cat for variant in ["unsolved-", "solved-"] for cat in CHALLENGE_CATEGORIES]
        tags = [interactions.ThreadTag.create(tag) for tag in tags]
        forum = await ctx.guild.create_forum_channel(name=ctf_name, position=1000, category=category_channel, available_tags=tags)

        general = await forum.create_post(name="General", content=name)
        await general.pin()

        await ctx.send(f"Created {ctf_name}")
