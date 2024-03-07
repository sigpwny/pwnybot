import os

GUILD_IDS = list(map(int, os.getenv('GUILD_IDS').split(',')))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
