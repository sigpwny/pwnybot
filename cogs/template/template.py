import interactions

import lib.util


class Template(interactions.Extension):
    @interactions.slash_command(scopes=lib.config.GUILD_IDS)
    async def asd(self, ctx: interactions.SlashContext):
        await ctx.send("aosidjw")
