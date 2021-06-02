import json
import discord
from discord.ext import commands
from bot import config, logger

NAME = "reaction-role"
VERSION = config["VERSION"]


class reactionRoles(commands.Cog):
    '''
    This class contains all the code for the reaction role system. This class should
    allow users to create embedded messages and specify the emojis the users should respond to
    and what role each will add.
    '''

    def __init__(self, client):
        '''
        Basic constructor.
        @param client The Discord client
        '''
        self.client = client
        self.prefix = "$react "

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        Upon ready, the bot will seend out a quick response to the terminal
        to indicate that it is ready.
        '''
        logger.info("[pwnyBot] " + NAME + " is online")

    @commands.command()
    async def react(self, ctx):
        '''
        This function aims to create an interactive system/loop that asks the user
        a series of questions regarding where or what they want in an embed. It also asks
        about what emojis should be added along with their corresponding roles.

        @param ctx The context of the command. Handled by Discord.py
        '''
        await ctx.send('Please reply with a reaction role description!')
        description = await ctx.bot.wait_for('message')

        # Embed
        myEmbed = discord.Embed(
            title="Reaction Message!",
            description=description.content,
            colour=0x00bd03
        )
        myEmbed.set_footer(text="Message by: " + ctx.message.author.name)
        reactionMessage = await ctx.send(embed=myEmbed)

        # while True:
        #     await ctx.send('Please reply with the emoji you want to add. If finished, type FINISH.')
        #     response = await ctx.bot.wait_for('message')

        #     if (response.content == 'FINISH'):
        #         await ctx.send('Finished')
        #         break

        #     await reactionMessage.add_reaction(response.content)


def setup(client):
    '''
    Cog setup
    '''
    client.add_cog(reactionRoles(client))
