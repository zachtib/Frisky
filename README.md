# Frisky: A general purpose Slack bot written in Python

## Running Frisky locally
Frisky uses `pipenv` to manage its Python environment. From the project directory, you can run `pipenv install` to get your environment set up, and then `pipenv run python manage.py runserver`

Because Frisky is event driven, you will need to emulate events coming from Slack in order to test your featured end-to-end. However, a test case class is provided to more easily test simple plugins.

## Writing a plugin
To create a plugin, add a python file underneath the `plugins/` directory. Inside this file, add a function called `handle_message` with the signature: `handle_message(*args, **kwargs) -> str:`. The name of your file determines the command name that will invoke it via Slack, so sending a `?ping` command in Slack would be handled by `ping.py`.

The Slack event handler will parse incoming messages in the form `?command foo bar xyzzy` and pass everyhing after the command name to the plugin as a list to the `*args` parameter. The `**kwargs` parameter will be used for any extra context to pass along to the bot, currently this is just the channel name as `channel`.

### An example plugin
This example is included in the source as `ping.py`
```
def handle_message(*args, **kwargs) -> str:
    return ‘pong’
```
And the tests for this plugin at `test_ping.py`
```
from friskytest import FriskyTestCase


class PingTestCase(FriskyTestCase):

    def test_ping_returns_pong(self):
        reply = self.send_message(‘?ping’)
        self.assertEqual('pong', reply)

```

The base class `FriskyTestCase` has one method, `send_message` which takes in a string and handles it as if it was a message sent in channel.