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
    plugin = importlib.import_module(f'plugins.{command}')
    if hasattr(plugin, 'handle_message'):
        handler = getattr(plugin, 'handle_message')
        if callable(handler):
            return handler(*arguments, channel=channel, sender=sender)


def handle_message(channel_name, sender, message, reply_channel) -> None:
    if message[0] != '?' and not message.startswith(settings.FRISKY_BOT_NAME):
        return
    reply = get_reply_from_plugin(message, sender, channel_name)
    if reply is not None:
        reply_channel(reply)
