# Standard Python Imports
import os
import json
import sys

# pwnyBot Imports


# Third Party Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load .env file (should be in src/ folder)
load_dotenv()

# Openn and setup our config file
f = open('config.json', 'r')
config = json.load(f)
load_configs = config['CONFIGS']

botDict = {}
for filename in os.listdir('./bots'):
	if filename.endswith('.py'):
		botDict[filename[:-3]] = False

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
	This function loads in a specified cog. Note: cogs are basically just files
	that we are adding into our code individually. Why is this beneficial? Well,
	it allows us to 'unnload the file' when we need to do some development.
	'''
	try:
		client.load_extension(f'bots.{extension}')
		botDict[extension] = True

		await log_and_respond(ctx, 'Loaded ' + extension + ' successfully')
	except Exception as e:
		await log_and_respond(ctx, 'Could not load ' + extension + ': `' + str(e) + '`')
	

@client.command()
async def unload(ctx, extension):
	'''
	This function unloads in a specified cog. 
	'''
	try:
		client.unload_extension(f'bots.{extension}')
		botDict[extension] = False

		await log_and_respond(ctx, 'Un-loaded ' + extension + ' successfully')
	except Exception as e:
		await log_and_respond(ctx,'Could not un-load ' + extension + ': `' + str(e) + '`')

@client.command()
async def reload(ctx, extension):
	'''
	This function unloads and load a specified cog
	'''
	try:
		client.unload_extension(f'bots.{extension}')
	except Exception as _: # This is probably not correct, TODO bug check
		pass
	try: 
		client.load_extension(f'bots.{extension}')
		await log_and_respond(ctx, 'Re-loaded ' + extension + ' successfully')
	except Exception as e:
		await log_and_respond(ctx,'Could not reload ' + extension + ': `' + str(e) + '`')

@client.command()
async def botlist(ctx):
	try:
		response = "> __Current Bot List__\n"
		for bot in botDict.keys():
			if botDict[bot] == True:
				response += '> :green_circle: ' + bot + '\n'
			else:
				response += '> :red_circle: ' + bot + '\n'
		await ctx.send(response)
	except Exception as e:
		await ctx.send(f'Could not get bot list: {str(e)}')


# Log the message and respond in chat.
async def log_and_respond(ctx, msg):
	print('[pwnyBot]', msg)
	await ctx.send(msg)

# If there is a load config, then try loading it. Otherwise just load every bot.
to_load = None
if len(sys.argv) > 1:
	to_load = load_configs.get(sys.argv[1],None)
if to_load == None:
	to_load = botDict.keys()
for bot in to_load:
	try:
		client.load_extension(f'bots.{bot}')
		botDict[bot] = True
	except Exception as e:
		print(str(e))

	
# Login via token
client.run(os.getenv('DISCORD_TOKEN'))
