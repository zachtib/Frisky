import importlib

from slack.webhooks import post_message


def parse_message_string(message):
    split = message.split()
    command = split[0][1:]
    arguments = split[1:]
    return command, arguments


def get_reply_from_plugin(message, channel):
    command, arguments = parse_message_string(message)
    plugin = importlib.import_module(f'plugins.{command}')
    if hasattr(plugin, 'handle_message'):
        handler = getattr(plugin, 'handle_message')
        if callable(handler):
            return handler(*arguments, channel=channel)


def handle_message(event) -> None:
    text = event['text']
    if text[0] != '?':
        return
    channel = event['channel']
    reply = get_reply_from_plugin(text, channel)
    if reply is not None:
        post_message(channel, reply)
