import os

AUTOGENERATED_CHANNELS = {'general': 'general',
                          'logs': 'logs-📝', 'access': 'access-requests-✔️'}
ARCHIVE_CATEGORY = 'ctf-archive'
INTERNAL_CTFD_URL = 'http://localhost:8000'
GUILD_IDS = list(map(int, os.getenv('GUILD_IDS').split(',')))
# , 485104508175646751]
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CTFD_TOKEN = os.getenv('CTFD_TOKEN')
DEFAULT_ARCHIVE_ID = int(os.getenv('DEFAULT_ARCHIVE_ID'))

EMOTE_FROM = "<:pwnyPortalFrom:846826010561478657> "
EMOTE_TO = "<:pwnyPortalTo:846826010241794102> "
CTF_ROLE_ID = 1234
UIUC_ROLE_ID = 5678
