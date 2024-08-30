import os
import yaml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

config = {}
try:
    with open("config.yml", "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error loading config: {e}")
            exit(1)
except FileNotFoundError:
    logger.warning("No config file found.")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_IDS = os.getenv('GUILD_IDS', "").split(",")
CTF_CATEGORY_CHANNELS = os.getenv("CTF_CATEGORY_CHANNELS", "").split(",")
CTF_ROLES = os.getenv("CTF_ROLES", "").split(",")
UIUC_ROLES = os.getenv("UIUC_ROLES", "").split(",")
PRIVATE_ROLES = config.get("private_roles", [])

CHALLENGE_CATEGORIES = ["crypto", "forensics", "misc", "pwn", "osint", "rev", "web"]
FORUM_GENERAL_CHANNEL = "General"
