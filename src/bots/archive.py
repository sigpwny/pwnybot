'''
pwnyBot skeleton code. Please use this as a skeleton for any commands you intend to add.
Yes there is problably a better way to do it, but unless you are willing to refactor EVERYTHING, then dont mess with it.
'''
import discord
from discord.ext import commands

NAME = "Archive"
VERSION = "1.0.0"
PREFIX = "!archive"


#get_command strips the prefix from the command and returns 
def get_command(message):
    if not message.startswith(PREFIX):
        return None
    else:
        return message[len(PREFIX):]

class Demo(commands.Cog):
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

        # Replace this with your code
        if command == 'demo':
            response = 'Demo response!'
        elif command == 'ping':
            response = 'pong!'
        elif command == 'sum':
            numbers = command.split(' ')[1:]
            try:
                response = sum(map(int, numbers))
            except:
                response = "One of your inputs was not a number!"
        
        # If there is no response, return. Otherwise send the response
        if response == None:
            return
        else:
            await message.channel.send(response)

def setup(client):
    client.add_cog(Archive(client))