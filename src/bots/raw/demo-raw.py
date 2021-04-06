# Imports go here
import discord
from discord.ext import commands

# REQUIRED INFORMATION for the bot to work!
NAME = "demo-raw"
VERSION = "1.0.0"
TOKEN = ... # TODO REPLACE THIS WITH YOUR TOKEN

client = discord.Client()
def load_token(path):
	f = open(path,"r")
	ret = f.read()
	f.close()
	return ret

@client.event
async def on_ready():
    print("[pwnyBot] " + NAME + " is online")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!demo':
        response = ">>Original<< Demo response!"
        await message.channel.send(response)

def main():
    TOKEN = load_token('../../token.key')
    client.run(TOKEN)

if __name__ == '__main__':
    main()