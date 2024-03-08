import os


def strToIntList(s: str) -> list[int]:
    return list(map(int, s.split(',')))


DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS = strToIntList(os.getenv('GUILD_IDS', ""))
CTF_CATEGORY_CHANNEL = os.getenv("CTF_CATEGORY_CHANNEL", "")
