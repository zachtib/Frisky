# Frisky: A general purpose Slack bot written in Python

1. [Running Frisky Locally](#running-frisky-locally)
2. [Writing a Plugin](#writing-a-plugin)
   1. [An example plugin](#an-example-plugin)
3. [Troubleshooting](#troubleshooting)

## Running Frisky Locally
Before you get started, make sure you have python 3.8.1 installed.  Frisky is a modern ~~cat~~ bot with modern needs!

Frisky uses `pipenv` to manage its Python environment. This is just a standard pip package that can be installed with
`pip install pipenv`, the python runtime you install it to does not matter.  From the project directory, you can run
`pipenv install` to get your environment set up, and then `pipenv run python manage.py runserver`

Because Frisky is event driven, you will need to emulate events coming from Slack in order to test your featured
end-to-end. However, a test case class is provided to more easily test simple plugins.

## Writing a plugin
To create a plugin, add a python file underneath the `plugins/` directory. Inside this file, add a function called
`handle_message` with the signature: `handle_message(*args, **kwargs) -> str:`. The name of your file determines the
command name that will invoke it via Slack, so sending a `?ping` command in Slack would be handled by `ping.py`.

The Slack event handler will parse incoming messages in the form `?command foo bar xyzzy` and pass everything after the 
command name to the plugin as a list to the `*args` parameter. The `**kwargs` parameter will be used for any extra 
context to pass along to the bot, currently this is just the channel name as `channel`.

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

The base class `FriskyTestCase` has one method, `send_message` which takes in a string and handles it as if it was a
message sent in channel.

## Troubleshooting
When running `pipenv install` you may encounter an error like:
```
[pipenv.exceptions.InstallError]: ['Collecting psycopg2==2.8.4', '  Using cached psycopg2-2.8.4.tar.gz (377 kB)']
[pipenv.exceptions.InstallError]: ['ERROR: Command errored out with exit status 1:', ... more setuptools gibberish ... ]
...
ERROR: ERROR: Package installation failed...
```
You can safely ignore this error.  The root cause is a transitive dependency of `django-heroku` however you will
generally use sqlite when testing Frisky locally.  If you would like to remove these errors you can install the 
postgres development header package appropriate for you distribution (`libpq-dev` on Ubuntu, `postgresql-devel` on
CentOS).
