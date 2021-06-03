from discord.ext import commands
from bot import logger, config
import os


class Manager(commands.Cog):
    def __init__(self, bot):
        logger.debug('Starting Manager')
        self.bot = bot
        self.prefix = "$"

    async def cog_check(self, ctx):
        return ctx.prefix == self.prefix

    # Note: this runs regardless of cog_check
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.prefix == '$':
            pass
        """The event triggered when an error is raised while invoking a command."""
        # Note specific command _error handling exists, this is just faster
        if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
            await ctx.send(f'That command is invalid. The error was: {error} {ctx.message.content}')
        elif isinstance(error, commands.CommandNotFound):
            if ctx.prefix != '$':
                await ctx.send(f'{error}')
        else:
            await ctx.send(f'Uh oh: {error}. {type(error)}')

    @commands.Cog.listener()
    async def on_error(self, ctx, error):
        await ctx.send(f'Normal error: {error}')

    @commands.command()
    async def unload(self, ctx, extension):
        '''
        This function unloads in a specified cog. 
        '''
        try:
            if extension == 'manager':
                raise ValueError('Hey don\'t unload the unloader!')
            self.bot.unload_extension(f'{config["COG_PREFIX"]}.{extension}')
            self.bot.bot_dict[extension] = False
            await ctx.send('Un-loaded ' + extension + ' successfully')
        except Exception as e:
            await ctx.send('Could not un-load ' + extension + ': `' + str(e) + '`')

    @commands.command(aliases=['r'])
    async def reload(self, ctx, extension=None):
        '''
        This function unloads and load a specified cog
        '''
        try:
            extensions = []
            if extension is None:
                extensions = list(self.bot.bot_dict.keys())
            else:
                extensions = [extension]
            for ext in extensions:
                self.bot.reload_extension(
                    f'{config["COG_PREFIX"]}.{ext}')
            await ctx.send(f'Cogs: [{",".join(extensions)}] were reloaded.')
        except Exception as e:
            await ctx.send(f'Could not reload {ext}: `{e}`')

    @commands.command()
    async def load(self, ctx, extension):
        '''
        This function loads a specified cog
        '''
        try:
            self.bot.load_extension(f'{config["COG_PREFIX"]}.{extension}')
            self.bot.bot_dict[extension] = True
            await ctx.send(f'loaded {extension} successfully')
        except Exception as e:
            await ctx.send(f'Could not load {extension}: `{e}`')

    @commands.command()
    async def botlist(self, ctx):
        try:
            response = "> __Current Bot List__\n"
            for bot, online in self.bot.bot_dict.items():
                if online:
                    response += '> :green_circle: ' + bot + '\n'
                else:
                    response += '> :red_circle: ' + bot + '\n'
            await ctx.send(response)
        except Exception as e:
            await ctx.send(f'Could not get bot list: {str(e)}')


def setup(client):
    client.add_cog(Manager(client))
