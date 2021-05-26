'''
pwnyBot skeleton code. Please use this as a skeleton for any commands you intend to add.
Yes there is problably a better way to do it, but unless you are willing to refactor EVERYTHING, then dont mess with it.
'''
import discord
from discord.ext import commands
import os, json
NAME = "bounty"
VERSION = "1.2.0"
PREFIX = "!bounty"

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
BOARD_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'storage', 'bountyboard.json')
bounty_params = ['description','goals','deadline','capacity','hunters','contact','link','repeatable']

usage = {
    'new':'`!bounty new <name> <value> [description|goals|deadline|capacity|hunters|contact|link|repeatable]`',
    'create':'See `!bounty new` (identical)',
    'remove':'`!bounty remove <name>`',
    'join':'`!bounty join <name>`',
    'leave':'`!bounty leave <name>`',
    'claim':'`!bounty claim <name>`',
    'board':'`!bounty board` [all|full|empty|**open**|claimed]',
    'list':'See `!bounty board` (identical)',
    'modify':'`!bounty modify <name> [variable=value,...]`',
    'info':'`!bounty info <name>`'
}

help = {
    'new':'Creates new bounty, the only information required is <name> and <value>.\n>     __new Default Values__\n>     Deadline:NONE\n>     Contact:<Creator of bounty>\n>     Capacity:2',
    'create':'Same as `new`',
    'remove':'Removes a bounty',
    'join':'Joins you to a bounty, the bounty must have capacity.',
    'leave':'Leaves a bounty, this can generally be done without issue.',
    'claim':'Submits a bounty to be claimed in exchange for pwnyPoints',
    'board':'Displays the bounty board. By default, it shows all currently open bounties (partially full and empty bounties)',
    'list': 'Same as board',
    'info': 'Gets detailed information for a bounty.'
}

#get_command strips the prefix from the command and returns 
def get_command(message):
    if not message.startswith(PREFIX):
        return None
    else:
        return message[len(PREFIX):]

def has_permission(message):
    role = discord.utils.find(lambda r: r.name == 'Developer',message.guild.roles)
    return role in message.author.roles 
    
def save_board():
    with open(BOARD_PATH, 'w') as f:
        json.dump(board, f, indent=2)
        
def load_board():
    global board
    with open(BOARD_PATH, 'r') as f:
        board = json.load(f)

def generate_bounty(name,value,author,args):
    if name in board:
        raise Invalid("Bounty already exists")
    # print(name, value, author, args)
    board[name] = {'name': name, 'points': value, 'contact': author}
    for arg in args:
        arg = arg.split('=')
        param = arg[0]
        argv = arg[1]
        # print(param, argv)
        if param in bounty_params:
            board[name][param] = argv
    

async def display_bounty(name, ctx):
    bounty = board.get(name,None)
    if bounty == None:
        raise Invalid("Invalid bounty")
    embed=discord.Embed(title=f"{name.capitalize()} ({bounty['points']})", color=0xe0bb00)
    
    for param in ['description','deadline','link','repeatable']:
        if bounty.get(param, None) is not None:
            embed.add_field(name=param.capitalize(), value=str(bounty[param]), inline=True)

    if bounty.get('capacity') or bounty.get('hunters'):
        capacity_left = int(bounty['capacity']) - len(bounty.get("hunters", []))
        embed.add_field(name='Capacity', value=f'{capacity_left}/{bounty["capacity"]}', inline=True)
    if bounty.get('goals'):
        embed.add_field(name='Goals', value='\n + '.join(bounty.get('goals')), inline=True)
        
    embed.set_thumbnail(url="https://img.icons8.com/emoji/452/scroll-emoji.png") # TODO Grab this and put it up on an assets page
    embed.add_field(name="Contact", value="<@" + str(bounty['contact']) + '>', inline=True)
    await ctx.send(embed=embed)

async def display_board(filter="Open"):
    for name,bounty in board.items():
        pass

class Invalid(Exception):
    pass

class Bounty(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        load_board()
        print("[pwnyBot] " + NAME + " is online")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        command = get_command(message.content)

        if command == None:
            return

        response = None
        
        command = command[1:].split(' ')
            
        sections = []
        start_quote = False
        mini_section = []
        for part in command:
            if '"' in part:
                mini_section.append(part.replace('"',''))
                if start_quote: #End quote
                    sections.append(' '.join(mini_section))
                    start_quote = False
                else:
                    start_quote = True
            elif start_quote:
                mini_section.append(part)
            else:
                sections.append(part)
        
        # Edge case where they only provide the starting quote
        if len(mini_section) > 0:
            sections.append(' '.join(mini_section))

        print('Manually parsed sections:', sections)
        action = command[0]

        if board == None:
            load_board()
        
        try:
            if action in ['new','create']:
                if has_permission(message):
                    if len(command) < 3:
                        raise Invalid('Not enough information\nUsage is ' + usage['new'])
                    else:
                        generate_bounty(command[1],command[2],message.author.id,command[3:])
                        save_board()
                else:
                    raise Invalid(f"You do not have permission to execute `{action}`")
            elif action == 'remove':
                if has_permission(message):
                    if len(command) == 2:
                        if command[1] in board:
                            del board[command[1]]
                            response = 'Successfully removed bounty ' + command[1]
                            save_board()
                        else:
                            raise Invalid(f'Error: Unable to locate bounty {command[1]}')
                    else:
                        raise Invalid('Error: Invalid request.')
                else:
                    raise Invalid('Error: Insufficent permissions')
            elif action == 'info':
                if command[1] in board:
                    ctx = await self.client.get_context(message)
                    await display_bounty(command[1],ctx)
                else:
                    raise Invalid(f'Error: Unable to locate bounty {command[1]}')
            elif action == 'claim':
                if len(command) >= 3:
                    raise Invalid('Error: Invalid arguments')
                else:
                    bountyName = command[1]
                    if board.get(bountyName,None) is None:
                        raise Invalid(f'Error: Unable to locate bounty {command[1]}')
                    else:
                        board.get(bountyName)['hunters'].append(message.author.id)
                        response = f'<@{message.author.id>} is now a hunter for {bountyName}'
            elif action in ['list','board']:
                display_board()
            elif action == 'help':
                if len(command) >= 2:
                    response = usage.get(command[1], None)
                    if response == None:
                        raise Invalid(f"No help section for '{command[1]}'")
                else:
                    response = ''
                    for key, value in help.items():
                        response += f'> **{key}** - {value}\n'
            else:
                raise Invalid(f"Error: The command '{subcommand}' does not exist.")
            

            # If there is no response, return. Otherwise send the response
            if response == None:
                return
            else:
                await message.channel.send(response)
        except Invalid as e:
            await message.channel.send(e)

def setup(client):
    client.add_cog(Bounty(client))