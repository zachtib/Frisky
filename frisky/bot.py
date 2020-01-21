import importlib

from django.conf import settings


def parse_message_string(message):
    if message[0] == '?':
        message = message[1:]
    elif message.startswith(settings.FRISKY_BOT_NAME):
        message = message[len(settings.FRISKY_BOT_NAME):]
    message.strip()
    split = message.split()
    command = split[0]
    arguments = split[1:]
    return command, arguments


def get_reply_from_plugin(message, sender, channel):
    command, arguments = parse_message_string(message)
    try:
        plugin = importlib.import_module(f'plugins.{command}')
        if hasattr(plugin, 'handle_message'):
            handler = getattr(plugin, 'handle_message')
            if callable(handler):
                return handler(*arguments, channel=channel, sender=sender)
    except ModuleNotFoundError:
        plugin = importlib.import_module(f'plugins.learn')
        if hasattr(plugin, 'handle_message'):
            handler = getattr(plugin, 'handle_message')
            if callable(handler):
                return handler(command)


def get_reply_for_reaction(reaction, reacting_user, commenting_user, comment, added):
    reactjis = {
        'upvote': 'votes',
        'downvote': 'votes',
        'brain': 'learn',
    }
    if reaction in reactjis.keys():
        plugin_name = reactjis[reaction]
        plugin = importlib.import_module(f'plugins.{plugin_name}')
        if hasattr(plugin, 'handle_reaction'):
            handler = getattr(plugin, 'handle_reaction')
            if callable(handler):
                return handler(reaction, reacting_user, commenting_user, comment, added)


def handle_message(channel_name, sender, message, reply_channel) -> None:
    if message[0] != '?' and not message.startswith(settings.FRISKY_BOT_NAME):
        return
    reply = get_reply_from_plugin(message, sender, channel_name)
    if reply is not None:
        reply_channel(reply)


def handle_reaction(reaction, reacting_user, commenting_user, comment, added, reply_channel):
    """

    This function is EXPERIMENTAL. Please don't base your plugins on it at this time

    :param comment:
    :param reaction:
    :param reacting_user:
    :param commenting_user:
    :param added:
    :param reply_channel:
    :return:
    """
    reply = get_reply_for_reaction(reaction, reacting_user, commenting_user, comment, added)
    if reply is not None:
        reply_channel(reply)
