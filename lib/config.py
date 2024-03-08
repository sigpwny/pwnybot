import os


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS = os.getenv('GUILD_IDS', "").split(",")
CTF_CATEGORY_CHANNELS = os.getenv("CTF_CATEGORY_CHANNELS", "").split(",")
CHALLENGE_CATEGORIES = os.getenv("CHALLENGE_CATEGORIES", "").split(",")
FORUM_GENERAL_CHANNEL = "General"
