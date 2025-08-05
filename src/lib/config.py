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

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or config.get("discord_token")
GUILD_IDS = os.getenv('GUILD_IDS', "").split(",") or config.get("guild_ids", [])
CTF_CATEGORY_CHANNELS = os.getenv("CTF_CATEGORY_CHANNELS", "").split(",") or config.get("ctf_category_channels", [])
CTF_ROLES = os.getenv("CTF_ROLES", "").split(",") or config.get("ctf_roles", [])
UIUC_ROLES = os.getenv("UIUC_ROLES", "").split(",") or config.get("uiuc_roles", [])
HELPER_ROLE = int(os.getenv("HELPER_ROLE", 0) or config.get("helper_role", 0))
PRIVATE_ROLES = config.get("private_roles", [])

CHALLENGE_CATEGORIES = ["crypto", "forensics", "misc", "pwn", "osint", "rev", "web"]
FORUM_GENERAL_CHANNEL = "General"
