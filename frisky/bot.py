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


def get_reply_from_plugin(message, channel):
    command, arguments = parse_message_string(message)
    plugin = importlib.import_module(f'plugins.{command}')
    if hasattr(plugin, 'handle_message'):
        handler = getattr(plugin, 'handle_message')
        if callable(handler):
            return handler(*arguments, channel=channel)


def handle_message(event, reply_channel) -> None:
    text = event['text']
    if text[0] != '?' and not text.startswith(settings.FRISKY_BOT_NAME):
        return
    channel = event['channel']
    reply = get_reply_from_plugin(text, channel)
    if reply is not None:
        reply_channel(reply)
