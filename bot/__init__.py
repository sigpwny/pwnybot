from dotenv import load_dotenv
from discord.ext import commands
from discord import Game
import json
import logging
import glob
import os

# Load main public config
config = json.load(open(os.path.join('data', 'config.json')))
EMOJI_NUMS = ['0️⃣', '1️⃣', '2️⃣', '3️⃣',
              '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']

# Load secret config
load_dotenv(os.path.join('data', '.env'))
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Set logging up
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('pwnybot')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord').setLevel(logging.WARNING)


class PwnyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.bot_dict = {}
        super().__init__(*args, **kwargs)
        for cog in os.listdir(os.path.join('bot', 'cogs')):
            if cog.endswith('.py'):
                extension = cog[:-3]
                logger.debug(extension)
                self.bot_dict[extension] = True
                try:
                    self.load_extension(f'{config["COG_PREFIX"]}.{extension}')
                except Exception as e:
                    logger.error(e)
                logger.info(f'{extension}')

    async def on_ready(self):
        pass

    async def on_member_join(self, member):
        pass

    # More general client handling can be added here


# Export client
client = PwnyBot(
    command_prefix=config['PREFIX'], activity=Game(name="Online!"))
