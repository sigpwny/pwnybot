# Standard Python Imports
import logging
from bot import client, logger, DISCORD_TOKEN
import os

# Log level we want to see
if __name__ == '__main__':
    logger.info('Starting PWNYBOT.')
    client.run(DISCORD_TOKEN)
