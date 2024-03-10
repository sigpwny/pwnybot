import os


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS = os.getenv('GUILD_IDS', "").split(",")
CTF_CATEGORY_CHANNELS = os.getenv("CTF_CATEGORY_CHANNELS", "").split(",")
CTF_ROLES = os.getenv("CTF_ROLES", "").split(",")
UIUC_ROLES = os.getenv("UIUC_ROLES", "").split(",")

CHALLENGE_CATEGORIES = ["crypto", "forensics", "misc", "pwn", "osint", "rev", "web"]
FORUM_GENERAL_CHANNEL = "General"
