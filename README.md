# Frisky: A general purpose Slack bot written in Python
![image build](https://api.travis-ci.org/zachtib/Frisky.svg?branch=main)
![image cover](https://codecov.io/gh/zachtib/Frisky/branch/main/graph/badge.svg)

1. [Running Frisky Locally](#running-frisky-locally)
2. [Writing a Plugin](#writing-a-plugin)
   1. [An example plugin](#an-example-plugin)
3. [Troubleshooting](#troubleshooting)

## Running Frisky Locally
Before you get started, make sure you have python 3.8 installed.  Frisky is a modern ~~cat~~ bot with modern needs!

Frisky uses `pipenv` to manage its Python environment. This is just a standard pip package that can be installed with
`pip install pipenv`, the python runtime you install it to does not matter.  From the project directory, you can run
`pipenv install` to get your environment set up, and then `pipenv run python manage.py runserver`

Because Frisky is event driven, you will need to emulate events coming from Slack in order to test your featured
end-to-end. However, a test case class is provided to more easily test simple plugins.

When running locally, Frisky uses a sqlite database by default. If you wish to use a Postgres database, you will need
to install the psycopg2 bindings.

## Writing a plugin
To create a plugin, add a python file underneath the `plugins/` directory. Inside this file, import and extend the base
frisky plugin `frisky.plugins.FriskyPlugin`.  This class contains the base functionality you'll need for a new plugin.

To implement your plugin, implement any of the following properties and methods:

* `reactions: List[str]` - a list of emoji reactions you want to handle
* `commands: List[str]` - a list of commands you want to handle
* `help: str` - helpful information about how to use your plugin in slack
* `command_aliases: Dict[str, str]` - a dictionary in order to alias commands to others (see learn.py for an example)
* `def command_{command_name}(self, message)` - for each command you want to handle in your plugin. The `message`
   argument is a MessageEvent from the `frisky.events` package and should contain basic information (slack channel, raw
   command text sent, user name of sender, etc ...)
* `def reaction_{emoji}(self, reaction)` - for each reaction you want to handle in your plugin. The `message` argument
   is a `ReactionEvent` from the `frisky.events` package and should contain basic information (emoji string, username of
   the user who received the emoji) as well as a `MessageEvent` instance.            

Note that all of these properties are optional, however you must at least implement one and it's corresponding handler
function to do implement any functionality.                  

### An example plugin
This example is included in the source as `ping.py`

```python
from frisky.plugin import FriskyPlugin


class PingPlugin(FriskyPlugin):
    
    commands = ['ping']

    def command_ping(self, message):
        return 'pong'
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
