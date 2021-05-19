# Standard Python Imports
import os
from dotenv import load_dotenv
import json

# pwnyBot Imports
from utils import *
from bots import demo

# Third Party Imports
import discord
from discord.ext import commands

# OUT_PATH = "./files/"
load_dotenv()

f = open('config.json', 'r')
config = json.load(f)

client = discord.Client()
client = commands.Bot(command_prefix = config['PREFIX']) 

# loaded = []

@client.event
async def on_ready():
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
	client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./bots'):
	if filename.endswith('.py'):
		client.load_extension(f'bots.{filename[:-3]}')
		print("[pwnyBot] Loaded", filename)

print(os.getenv('DISCORD_TOKEN'))
print(config['PREFIX'])

client.run(os.getenv('DISCORD_TOKEN'))

# def main():
# 	os.chdir("src")
# 	print_startup()
# 	print_version()
	
# 	TOKEN = load_token("token.key")
# 	client = commands.Bot(command_prefix = '$') 

# 	@client.command()
# 	async def bot(ctx, cmd, name):
# 		cmd = cmd.lower()
# 		if cmd in {'enable','e'}:
# 			try:
# 				client.load_extension(f'bots.{name}')
# 				await ctx.send(f'Bot `{name}` enabled successfully')
# 			except Exception as e:
# 				await ctx.send(f'Bot `{name}` failed to load (error message follows)\n```{e}```')
# 		elif cmd in {'disable','d'}:
# 			try:
# 				client.unload_extension(f'bots.{name}')
# 				await ctx.send(f'Bot `{name}` disabled successfully')
# 			except Exception as e:
# 				await ctx.send(f'Bot `{name}` could not be disabled (error message follows)\n```{e}```')
# 		elif cmd in {'reload','r'}:
# 			try:
# 				client.unload_extension(f'bots.{name}')
# 				client.load_extension(f'bots.{name}')
# 				await ctx.send(f'Bot `{name}` reloaded successfully')
# 			except Exception as e:
# 				await ctx.send(f'Bot `{name}` could not be reloaded (error message follows)\n```{e}```')
				
# 	# This is technically cogs but we are calling them bots
# 	# Stolen from https://www.youtube.com/watch?v=vQw8cFfZPx0 at 6:00
# 	loaded = load_conf()
# 	for fname in os.listdir('./bots'):
# 		if fname.endswith('.py') and fname.split('.py')[0] in loaded:
# 			client.load_extension(f'bots.{fname[:-3]}')
# 			print("[pwnyBot] Loaded",fname)

# 	client.run(TOKEN)



# if __name__ == '__main__':
# 	main()