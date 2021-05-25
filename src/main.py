# Standard Python Imports
import os
import sys

# pwnyBot Imports
from utils import *

# Third Party Imports
import discord
from discord.ext import commands

OUT_PATH = "./out_files/"
TOKEN = None
client = None
loaded = []

def main():
	print_startup()
	print_version()
	
	TOKEN = load_token("./assets/token.key")
	client = commands.Bot(command_prefix = get_prefix) 
	

	@client.command()
	async def bot(ctx, cmd, name):
		cmd = cmd.lower()
		if cmd in {'enable','e'}:
			try:
				client.load_extension(f'bots.{name}')
				await ctx.send(f'Bot `{name}` enabled successfully')
			except Exception as e:
				await ctx.send(f'Bot `{name}` failed to load (error message follows)\n```{e}```')
		elif cmd in {'disable','d'}:
			try:
				client.unload_extension(f'bots.{name}')
				await ctx.send(f'Bot `{name}` disabled successfully')
			except Exception as e:
				await ctx.send(f'Bot `{name}` could not be disabled (error message follows)\n```{e}```')
		elif cmd in {'reload','r'}:
			try:
				client.unload_extension(f'bots.{name}')
				client.load_extension(f'bots.{name}')
				await ctx.send(f'Bot `{name}` reloaded successfully')
			except Exception as e:
				await ctx.send(f'Bot `{name}` could not be reloaded (error message follows)\n```{e}```')
				
	# This is technically cogs but we are calling them bots
	# Stolen from https://www.youtube.com/watch?v=vQw8cFfZPx0 at 6:00
	if len(sys.argv) > 1:
		loaded = load_conf(sys.argv[1])
	else:
		loaded = load_conf()
	
	for fname in os.listdir('./bots'):
		if fname.endswith('.py') and fname.split('.py')[0] in loaded:
			try:
				client.load_extension(f'bots.{fname[:-3]}')
				print("[pwnyBot] Loaded",fname)
			except Exception as e:
				print("[pwnyBot] Could not load",fname,"\n" + e)

	client.run(TOKEN)



if __name__ == '__main__':
	main()