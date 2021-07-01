import discord
from discord.ext import commands
from bot import logger
import os
import json


'''
Example bounty
Points are distributed evenly between
"example" : {
    "name": "example",
    "description": "Perform club related task",
    "goals": ["Thing 1", "Thing 2", "Thing 3"],
    "points": 3000,
    "deadline": "DATE or NONE",
    "capacity": 3,
    "hunters": ["@Sam","@Justin","@Noelle"],
    "contact": "@Thomas",
    "link": https://sigpwny.com,
    "repeatable": True
}
'''


board = None
BOARD_PATH = os.path.join('data', 'bountyboard.json')
bounty_params = ['description', 'goals', 'deadline', 'capacity',
                 'hunters', 'contact', 'link', 'repeatable']  # TODO Need an ID, or a link

usage = {
    'new': '`!bounty new <name> <value> [description|goals|deadline|capacity|hunters|contact|link|repeatable]`',
    'create': 'See `!bounty new` (identical)',
    'remove': '`!bounty remove <name>`',
    'join': '`!bounty join <name>`',
    'leave': '`!bounty leave <name>`',
    'claim': '`!bounty claim <name>`',
    'board': '`!bounty board` [all|full|empty|**open**|claimed]',
    'list': 'See `!bounty board` (identical)',
    'modify': '`!bounty modify <name> [variable=value,...]`',
    'info': '`!bounty info <name>`',
    'hunter': '`!bounty hunter <hunter\'s @>`'
}

help_dict = {
    'new': 'Creates new bounty, required information is <name> and <value>.\n__new Default Values__\n>     Deadline:NONE\n>     Contact:<creator @>\n>     Capacity:2',
    'create': 'Same as `new`',
    'remove': 'Removes a bounty',
    'join': 'Joins you to a bounty, the bounty must have capacity.',
    'leave': 'Leaves a bounty, this can generally be done without issue.',
    'claim': 'Submits a bounty to be claimed in exchange for pwnyPoints',
    'board': 'Displays the bounty board. By default, it shows all currently open bounties (partially full and empty bounties)',
    'list': 'Same as `board`',
    'info': 'Gets detailed information for a bounty.',
    'hunter': 'Shows information on a hunter'
}


def has_permission(ctx):
    role = discord.utils.find(
        lambda r: r.name == 'Developer', ctx.guild.roles)
    return role in ctx.author.roles


def save_board():
    with open(BOARD_PATH, 'w') as f:
        json.dump(board, f, indent=2)


def load_board():
    global board
    try:
        with open(BOARD_PATH, 'r') as f:
            board = json.load(f)
    except TypeError:
        raise Invalid('Could not load board.')

def generate_bounty(name, value, author, args):
    print('We did it boys')
    if name in board:
        raise Invalid("Bounty already exists")
    # logger.debug(name, value, author, args)
    board[name] = {'name': name, 'points': int(value),
                   'contact': author, 'capacity': 2}
    args = args or []
    print(len(args))
    for arg in args:
        arg = arg.split('=')
        # logger.debug(arg)
        param = arg[0]
        argv = arg[1]
        # logger.debug(param, argv)
        if param in bounty_params:
            board[name][param] = argv

async def display_bounty(name, ctx):
    bounty = board.get(name, None)
    if bounty == None:
        raise Invalid("Invalid bounty")
    embed = discord.Embed(title=f"{name} ({bounty['points']})", color=0xe0bb00)

    for param in ['description', 'deadline', 'link', 'repeatable']:
        if bounty.get(param, None) is not None:
            embed.add_field(name=param.capitalize(),
                            value=str(bounty[param]), inline=True)

    if bounty.get('capacity'):
        capacity_left = int(bounty['capacity']) - \
            len(bounty.get("hunters", []))
        embed.add_field(
            name='Capacity', value=f'{capacity_left}/{bounty["capacity"]}', inline=True)
    if bounty.get('goals'):
        embed.add_field(
            name='Goals', value='\n + '.join(bounty.get('goals')), inline=True)
    if bounty.get('hunters'):
        hunter_list = ' '.join(
            ["<@" + str(hunter) + '>' for hunter in bounty.get('hunters')])
        embed.add_field(name='Hunters', value=hunter_list, inline=True)

    # TODO Grab this and put it up on an assets page
    embed.set_thumbnail(
        url="https://img.icons8.com/emoji/452/scroll-emoji.png")
    embed.add_field(name="Contact", value="<@" +
                    str(bounty['contact']) + '>', inline=True)

    # TODO Add hunters and goals as seperate sections.
    await ctx.send(embed=embed)


async def display_board(ctx, filter="Open"):
    embed = discord.Embed(title=f"Bounty Board", color=0xe0bb00)
    embed.set_thumbnail(url="https://i.imgur.com/RaZwe1F.jpeg")
    i = 0
    for name, bounty in board.items():
        # If it is open
        bounty_content = None
        if bounty.get('capacity', None) != None:
            capacity_left = int(bounty['capacity']) - \
                len(bounty.get("hunters", []))
            if capacity_left > 0:
                bounty_content = f'Point Value: {bounty["points"]}\nCapacity: ({capacity_left}/{bounty["capacity"]})'

            else:
                continue
        else:
            bounty_content = f'Point Value: {bounty["points"]}'
        embed.add_field(
            name=f'{name}', value=bounty_content, inline=(i % 2 != 1))
        i += 1
    await ctx.send(embed=embed)

class Invalid(Exception):
    pass


class Bounty(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = ["$bounty ", "$b "]

    async def cog_check(self, ctx):
        return ctx.prefix in self.prefix

    @commands.Cog.listener()
    async def on_ready(self):
        logger.debug('Loading board...')
        self.update_board()
        logger.debug('Done.')
        logger.info(f"[pwnyBot] {self.__class__.__name__} is online")

    def update_board(self):
        if board is None:
            load_board()
            print('Loading board.')
        else:
            save_board()
            print('Saved board.')
    @commands.Cog.listener()
    async def on_message(self, msg):
        pass
    @commands.command()
    async def create(self, ctx, name, points, *args):
        self.update_board()
        if has_permission(ctx):
            if not points.isdigit():
                raise Invalid('Must assign a numeric point value!')
            generate_bounty(
                name, points, ctx.author.id, args)
            await ctx.send(f'Successfully added bounty `{name}`')
        else:
            raise Invalid("You do not have permission to execute `create`")


    @commands.command()
    async def scoreboard(self, ctx):
        self.update_board()
        embed = discord.Embed(title="Top Bounty Hunters", color=0x9808c4)
        embed.set_thumbnail(
            url="https://assets-prd.ignimgs.com/2020/09/16/mandalorian-button-1600277980032.jpg")

        # TODO Presave in the JSON instead of this O[n] operation
        for hunter in board.get('hunters', {}):
            embed.add_field(name=f'{self.bot.get_user(int(hunter))}',
                            value=f'{board["hunters"][hunter]}', inline=True)

        await ctx.send(embed=embed)
    @commands.command()
    async def remove(self, ctx, bounty_name):
        self.update_board()
        if has_permission(ctx):
            if bounty_name in board:
                del board[bounty_name]
                await ctx.send('Successfully removed bounty ' + bounty_name)
            else:
                raise Invalid(f'Error: Unable to locate bounty {bounty_name}')

    @commands.command()
    async def info(self, ctx, bounty_name):
        self.update_board()
        if bounty_name in board:
            await display_bounty(bounty_name, ctx)
        else:
            raise Invalid(
                f'Error: Unable to locate bounty {bounty_name}')

    @commands.command()
    async def join(self, ctx, bounty_name):
        self.update_board()
        if board.get(bounty_name, None) is None:
            raise Invalid(
                f'Error: Unable to locate bounty {bounty_name}')
        else:
            if board[bounty_name].get('hunters', None) is None:
                board[bounty_name]['hunters'] = []
            if ctx.author.id in board[bounty_name]['hunters']:
                response = f'<@{ctx.author.id}> is already a hunter for {bounty_name}'
            else:
                board[bounty_name]['hunters'].append(ctx.author.id)
                response = f'<@{ctx.author.id}> is now a hunter for {bounty_name}'
            await ctx.send(response)

    @commands.command()
    async def list(self, ctx):
        self.update_board()
        await display_board(ctx)

    @commands.command()
    async def helpme(self, ctx, command=None):
        embed = discord.Embed(title=f"!bounty help", color=0x3238e6)
        embed.set_thumbnail(url="https://i.imgur.com/RaZwe1F.jpeg")
        if command is not None:
            use = usage.get(command, None)
            if use == None:
                raise Invalid(f"No help section for '{command}'")
            else:
                embed.add_field(command,)
        else:
            for key, v in help_dict.items():
                embed.add_field(
                    name=f'{key}', value=f'{v}', inline=False)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def claim(self, ctx, bounty_name):
        self.update_board()
        bounty = board.get(bounty_name, None)
        if bounty is None:
            raise Invalid(
                f'Error: Unable to locate bounty {bounty_name}')
            # TODO Assert that the person submitting the bounty was actually a hunter ??? or dont what are your thoughts?
        if ctx.author.id not in bounty['hunters']:
            raise Invalid(
                f"Error: You must actually be a bounty hunter for challenge {bounty_name}")
        else:
            # TODO PM the Contact to say that @Person requested to claim the bounty, and create a DM between those two people
            msg = f'<@{ctx.author.id}> requested to claim the bounty of {bounty["points"]} points for challenge `{bounty_name}`.'
            embed = discord.Embed(
                title=f"Claim Attempt", color=0xf56942)
            embed.add_field(name="ALERT!!!", value=msg)
            embed.set_thumbnail(
                url="https://i.kym-cdn.com/photos/images/newsfeed/001/431/821/579.jpg")
            approval = await ctx.channel.send(f'<@{bounty["contact"]}>', embed=embed)
            await approval.add_reaction('✅')
            await approval.add_reaction('❌')
            logger.debug(bounty['contact'])
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: not u.bot and r.emoji in ['✅', '❌'])
            logger.debug(user)  # TODO Translate user NAME into user ID
            logger.debug(reaction)
            if reaction.emoji == '✅':
                bounty['claimed'] = True
                if 'hunters' not in board:
                    board['hunters'] = {}
                if ctx.author.id not in board['hunters']:
                    board['hunters'][ctx.author.id] = 0
                board['hunters'][ctx.author.id] += bounty['points']
                response = 'Bounty successfully claimed!!!'  # TODO Make better
            elif reaction.emoji == '❌':
                response = 'Bounty claim was rejected, try again later!'
            else:
                await ctx.send('WHHAHASTHSDFFASHASHFFs')
            await ctx.send(response)

    @commands.command()
    async def leave(self, ctx, bounty_name):
        self.update_board()

        if board.get(bounty_name, None) is None:
            raise Invalid(
                f'Error: Unable to locate bounty `{bounty_name}`')
        else:
            if board[bounty_name].get('hunters', None) is None:
                board[bounty_name]['hunters'] = []
            if ctx.author.id in board[bounty_name]['hunters']:
                response = f'<@{ctx.author.id}> is no longer a hunter for "{bounty_name}"'

                board[bounty_name]['hunters'].remove(
                    ctx.author.id)
            else:
                response = f'Hey, <@{ctx.author.id}>! you are not a hunter for the bounty "{bounty_name}"'
            await ctx.send(response)


def setup(client):
    client.add_cog(Bounty(client))
