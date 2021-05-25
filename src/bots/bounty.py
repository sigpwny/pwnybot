'''
pwnyBot skeleton code. Please use this as a skeleton for any commands you intend to add.
Yes there is problably a better way to do it, but unless you are willing to refactor EVERYTHING, then dont mess with it.
'''
import discord
from discord.ext import commands

NAME = "Demo"
VERSION = "1.0.0"
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

board = {}
BOARD_PATH = './storage/bountyboard.json'

usage = {
    'new':'`!bounty new <name> <value> [description|goals|deadline|capacity|hunters|contact|link|repeatable]`',
    'create':'See `!bounty new` (identical)',
    'remove':'`!bounty remove <name>`',
    'join':'`!bounty join <name>`',
    'leave':'`!bounty leave <name>`',
    'claim':'`!bounty claim <name>`',
    'board':'`!bounty board` [all|full|empty|**open**|claimed]',
    'list':'See `!bounty board` (identical)',
}

help = {
    'new':'Creates new bounty, the only information required is <name> and <value>.\n__Default Values__\nDeadline:NONE\nContact:<Creator of bounty>\nCapacity:2',
    'create':'Same as `new`',
    'remove':'Removes a bounty',
    'join':'Joins you to a bounty, the bounty must have capacity.',
    'leave':'Leaves a bounty, this can generally be done without issue.',
    'claim':'Submits a bounty to be claimed in exchange for pwnyPoints',
    'board':'Displays the bounty board. By default, it shows all currently open bounties (partially full and empty bounties)',
    'list': 'Same as board'
}

#get_command strips the prefix from the command and returns 
def get_command(message):
    if not message.startswith(PREFIX):
        return None
    else:
        return message[len(PREFIX):]

def has_permission(message):
    role = discord.utils.find(lambda r: r.name == 'Admin',message.guild.roles)
    return role in message.sender.roles 

def generate_bounty(name,value,args):
    print(name,value,args)
    bounty[name]['name'] = name
    bounty[name]['points'] = points
    for arg in args:
        arg = arg.split('=')
        param = arg[0]
        argv = arg[1]
        

class Bounty(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
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
        if command[0] == 'new':
            if has_permission(message):
                if len(command) < 3:
                    response = 'Not enough information\nUsage is ' + usage['new']
                else:
                    board[command[1]] = generate_bounty(command[1],command[2],command[3:])

            else:
                response = f"You do not have permission to execute `{command[0]}`"
        
        # If there is no response, return. Otherwise send the response
        if response == None:
            return
        else:
            await message.channel.send(response)

def setup(client):
    client.add_cog(Bounty(client))