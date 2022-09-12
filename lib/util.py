import signal
import logging
from logging import RootLogger
import string
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
import inspect
from discord_slash.model import SlashCommandOptionType as OptionType
from functools import wraps
from lib.config import GUILD_IDS, CTF_PREFIX, CTFD_TOKEN, DISCORD_TOKEN
import tempfile
import subprocess

option_types = set(item.value for item in OptionType)

'''
https://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
'''


class Timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


def export_with_dce(channel_id: int, type='html', addl_args=[]):
    '''
    Calls DiscordChatExporter based on a channel_id
    '''

    with Timeout(seconds=60):
        assert type in ['html', 'json']

        _, temp_export_filename = tempfile.mkstemp(suffix=f'.{type}')
        if type == 'json':
            addl_args = ['-f', 'Json']

        chat_exporter_location = 'external/DiscordChatExporter2.34.1'
        cmd = ['dotnet', f'{chat_exporter_location}/DiscordChatExporter.Cli.dll', 'export', '--channel', str(channel_id), '--token', DISCORD_TOKEN, '--output', temp_export_filename, *addl_args]
        _ = subprocess.run(cmd, check=True, capture_output=True, text=True)

        return temp_export_filename


def get_option_type(annotation):
    if annotation == inspect.Parameter.empty:
        raise ValueError('All function parameters must have a annotation')

    if annotation in option_types:
        return annotation
    elif annotation == int:
        return OptionType.INTEGER
    elif annotation == str:
        return OptionType.STRING
    elif annotation == bool:
        return OptionType.BOOLEAN
    elif annotation == float:
        return OptionType.FLOAT

    else:
        raise NotImplementedError("That type isn't implemented yet")


def command_decorator(**kwargs):
    def wrapper(command):
        # Dynamically generate options list
        parameters = list(inspect.signature(command).parameters.items())[2:]
        options = []

        for [_, parameter] in parameters:
            data = {
                "name": parameter.name,
                "required": parameter.default == inspect.Parameter.empty,
                "option_type": get_option_type(parameter.annotation),
                "description": f'{parameter.name} (missing description)'
            }

            merged_data = {**data, **kwargs.get(parameter.name, {})}
            options.append(merged_data)

        options = [
            create_option(**option)
            for option in options
        ] if len(options) > 0 else None
        help_wrapper = cog_ext.cog_slash(
            name=command.__name__,
            guild_ids=GUILD_IDS,
            description=command.__doc__,
            options=options,
        )

        return help_wrapper(command)

    return wrapper


def run_from_ctf(func):
    '''
    This wrapper must be *below* subcommand_decorator to work correctly (have this run first)
    '''
    @wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        category_folder = ctx.channel.category
        if not category_folder.name.startswith(CTF_PREFIX):
            await ctx.send(f"That command must be run inside of a CTF folder (not {category_folder.name}).")
            return
        await func(self, ctx, *args, **kwargs)
    return wrapper


def subcommand_decorator(**kwargs):
    def wrapper(command):
        # Dynamically generate options list
        parameters = list(inspect.signature(command).parameters.items())[2:]
        options = []
        for [_, parameter] in parameters:
            data = {
                "name": parameter.name,
                "required": parameter.default == inspect.Parameter.empty,
                "option_type": get_option_type(parameter.annotation),
                "description": f'{parameter.name} (missing description)'
            }

            merged_data = {**data, **kwargs.get(parameter.name, {})}
            options.append(merged_data)

        class_lower = command.__qualname__.split('.')[0].lower()

        options = [
            create_option(**option)
            for option in options
        ] if len(options) > 0 else None
        help_wrapper = cog_ext.cog_subcommand(
            base=class_lower,
            guild_ids=GUILD_IDS,
            name=command.__name__,
            description=command.__doc__,
            options=options,
        )

        return help_wrapper(command)

    return wrapper


def sanitize_channel_name(name: str) -> str:
    """Filter out characters that aren't allowed by Discord for guild channels.

    Args:
        name: Channel name.

    Returns:
        Sanitized channel name.
    """
    whitelist = string.ascii_lowercase + string.digits + "-_"
    name = name.lower().replace(" ", "-")

    for char in name:
        if char not in whitelist:
            name = name.replace(char, "")

    while "--" in name:
        name = name.replace("--", "-")

    return name


def setup_logger(level: int) -> RootLogger:
    """Set up logging.

    Args:
        level: Logging level.

    Returns:
        The logger.
    """
    log_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s:%(name)-24s] => %(message)s"
    )

    logger = logging.getLogger()
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)

    logger.addHandler(stream_handler)

    return logger







logger = setup_logger(logging.INFO)
