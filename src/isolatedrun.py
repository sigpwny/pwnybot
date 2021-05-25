# Standard Python Imports
import os
import sys

# pwnyBot Imports
from utils import *
from bots import demo

# Third Party Imports
import discord
from discord.ext import commands

FUNC_PATH = None
TOKEN = None
client = None
loaded = []

def main():
    if len(sys.argv) == 0:
        print("Error: missing arguments")
        exit()    

    FUNC_PATH = sys.argv[1].split('.py')[0].replace("/",".")
    print(FUNC_PATH) 

    TOKEN = load_token("token.key")
    client = commands.Bot(command_prefix = '$') 
    if FUNC_PATH.endswith('.py'):
        print("[pwnyBot-I] Loaded",)
	# This is technically cogs but we are calling them bots
    try:
        client.load_extension(FUNC_PATH)
        print("[pwnyBot] Loaded",FUNC_PATH)
        client.run(TOKEN)
    except Exception as e:
        print("[pwnyBot] " + FUNC_PATH + " failed to load\n" + e)

if __name__ == '__main__':
	main()