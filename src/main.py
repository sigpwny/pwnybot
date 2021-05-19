# Standard Python Imports
import os
from dotenv import load_dotenv
import json

# Third Party Imports
import discord
from discord.ext import commands

# Load .env file (should be in src/ folder)
load_dotenv()

# Openn and setup our config file
f = open('config.json', 'r')
config = json.load(f)

# Load discord client
client = discord.Client()
client = commands.Bot(command_prefix = config['PREFIX']) 

@client.event
async def on_ready():
	'''
	This happens upon start up of the bot. It prints out a little pwnybot message
	and then prints out the bot version.
	'''
	print("################################")
	print("#                              #")
	print("#           pwnyBot            #")
	print("#    Discord Bot Aggregator    #")
	print("#      Created by SIGPwny      #")
	print("#                              #")
	print("################################")
	print("\n")
	print("Bot version is: " + config['VERSION'])

@client.command()
async def load(ctx, extension):
	'''
	This function loads in a specified cog. 
	'''
	client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
	'''
	This function unloads in a specified cog. 
	'''
	client.unload_extension(f'cogs.{extension}')

# Goes through our folder and just loads in all of the cogs
for filename in os.listdir('./bots'):
	if filename.endswith('.py'):
		client.load_extension(f'bots.{filename[:-3]}')
		print("[pwnyBot] Loaded", filename)

# Login via token
client.run(os.getenv('DISCORD_TOKEN'))