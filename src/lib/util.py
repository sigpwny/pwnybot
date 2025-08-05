import logging
from logging import Logger
import string
import inspect
import typing

import interactions
from interactions.models.internal import OptionType

from lib.config import GUILD_IDS

IS_ADMIN = interactions.slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)

option_types = set(item.value for item in OptionType)


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
                "type": interactions.OptionType.from_type(
                    getattr(parameter.annotation, "__args__", [parameter.annotation])[0] # unwrap union types
                ),
                "description": f'{parameter.name} (missing description)'
            }

            merged_data = {**data, **kwargs.get(parameter.name, {})}
            kwargs.pop(parameter.name, None)
            options.append(merged_data)

        options = [
            interactions.SlashCommandOption(**option)
            for option in options
        ] if len(options) > 0 else None
        commandArgs = {
            "name": sanitize_name(command.__name__),
            "scopes": GUILD_IDS,
            "description": command.__doc__,
            "options": options,
            **kwargs,
        }
        help_wrapper = interactions.slash_command(**commandArgs)
        wrapped = help_wrapper(command)

        # inherit attributes set by other decorators
        for attr in dir(command):
            if (attr.startswith("_")):
                continue
            if (getattr(wrapped, attr, None) is not None):
                continue
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
                "type": interactions.OptionType.from_type(parameter.annotation),
                "description": f'{parameter.name} (missing description)'
            }

            merged_data = {**data, **kwargs.get(parameter.name, {})}
            kwargs.pop(parameter.name, None)
            options.append(merged_data)

        class_sanitized = sanitize_name(command.__qualname__.split('.')[0])
        class_doc = command.__self__.__doc__ if hasattr(command, "__self__") else None

        options = [
            interactions.SlashCommandOption(**option)
            for option in options
        ] if len(options) > 0 else None
        commandArgs = {
            "base": class_sanitized,
            "base_description": class_doc,
            "scopes": GUILD_IDS,
            "name": sanitize_name(command.__name__),
            "description": command.__doc__,
            "options": options,
            **kwargs,
        }
        help_wrapper = interactions.subcommand(**commandArgs)
        wrapped = help_wrapper(command)

        # inherit attributes set by other decorators
        for attr in dir(command):
            if (attr.startswith("_")):
                continue
            if (getattr(wrapped, attr, None) is not None):
                continue
            setattr(wrapped, attr, getattr(command, attr))

        return wrapped

    return wrapper


def sanitize_name(name: str, *, max_length=32) -> str:
    """Filter names to conform to Discord name requirements.

    Args:
        name: The name.
        max_length: Maximum allowed length.

    Returns:
        Sanitized name.
    """
    whitelist = string.ascii_lowercase + string.digits + "-_"
    name = name.lower().replace(" ", "-")

    for char in name:
        if char not in whitelist:
            name = name.replace(char, "")

    while "--" in name:
        name = name.replace("--", "-")

    return name[:max_length]


def setup_logger(level: int) -> Logger:
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


async def get_ctf_forum(ctx: interactions.BaseContext) -> interactions.GuildForum | None:
    if (isinstance(ctx.channel, interactions.GuildForumPost) and
            (ctx.channel.parent_channel.name or "").startswith("ctf-")):
        return typing.cast(interactions.GuildForum, ctx.channel.parent_channel)


logger = setup_logger(logging.INFO)
