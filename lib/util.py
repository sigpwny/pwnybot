import logging
from logging import RootLogger
import string
import inspect

import interactions
from interactions.models.internal import OptionType

from lib.config import GUILD_IDS

option_types = set(item.value for item in OptionType)


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


def command(**kwargs):
    '''Decorator for commands. Auto generates name, description, and scope information based on the function and config.

    Args:
        kwargs: extra args to pass to interactions.SlashCommandOption in the format `optionname={'description': 'optiondescription'}`.
        Additionally, args that do not match an option are passed to `interactions.slash_command`
    '''
    def wrapper(command):
        # Dynamically generate options list
        parameters = list(inspect.signature(command).parameters.items())[2:]
        options = []

        for [_, parameter] in parameters:
            data = {
                "name": parameter.name,
                "required": parameter.default == inspect.Parameter.empty,
                "type": get_option_type(parameter.annotation),
                "description": f'{parameter.name} (missing description)'
            }

            merged_data = {**data, **kwargs.get(parameter.name, {})}
            kwargs.pop(parameter.name, None)
            options.append(merged_data)

        options = [
            interactions.SlashCommandOption(**option)
            for option in options
        ] if len(options) > 0 else None
        help_wrapper = interactions.slash_command(
            name=command.__name__,
            scopes=GUILD_IDS,
            description=command.__doc__,
            options=options,
            **kwargs,
        )
        wrapped = help_wrapper(command)

        # inherit attributes set by other decorators
        for attr in dir(command):
            if (not attr.startswith("_") and (not hasattr(wrapped, attr) or getattr(wrapped, attr) == None)):
                setattr(wrapped, attr, getattr(command, attr))

        return wrapped

    return wrapper


def subcommand(**kwargs):
    '''Decorator for subcommands. See `command` for details about `kwargs`'''
    def wrapper(command):
        # Dynamically generate options list
        parameters = list(inspect.signature(command).parameters.items())[2:]
        options = []
        for [_, parameter] in parameters:
            data = {
                "name": parameter.name,
                "required": parameter.default == inspect.Parameter.empty,
                "type": get_option_type(parameter.annotation),
                "description": f'{parameter.name} (missing description)'
            }

            merged_data = {**data, **kwargs.get(parameter.name, {})}
            kwargs.pop(parameter.name, None)
            options.append(merged_data)

        class_lower = command.__qualname__.split('.')[0].lower()
        class_doc = command.__self__.__doc__ if hasattr(command, "__self__") else None

        options = [
            interactions.SlashCommandOption(**option)
            for option in options
        ] if len(options) > 0 else None
        help_wrapper = interactions.subcommand(
            base=class_lower,
            base_description=class_doc,
            scopes=GUILD_IDS,
            name=command.__name__,
            description=command.__doc__,
            options=options,
            **kwargs,
        )
        wrapped = help_wrapper(command)

        # inherit attributes set by other decorators
        for attr in dir(command):
            if (not attr.startswith("_") and (not hasattr(wrapped, attr) or getattr(wrapped, attr) == None)):
                setattr(wrapped, attr, getattr(command, attr))

        return wrapped

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
