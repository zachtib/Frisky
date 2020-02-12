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
To create a plugin, add a python file underneath the `plugins/` directory. Inside this file, import and extend the base
frisky plugin `frisky.plugins.FriskyPlugin`.  This class contains the base functionality you'll need for a new plugin.

Additionally you'll notice several unimplemented functions:

* `register_emoji(cls)` - this no argument class method should define the emoji your plugin will react to, if any
* `register_commands(cls)` - this no argument class method should define the commands your plugin will react to, if any
* `help_text(cls)` - this no argument class method should return helpful information about how to use your plugin in 
   slack
* `handle_message(self, message)` - this method implements handling a message, ie one of the 'commands' you registered
   in the `register_commands` class method above. The `message` argument is a MessageEvent from the `frisky.events`
   package and should contain basic information (slack channel, raw command text sent, user name of sender, etc ...)
* `handle_reaction(self, reaction)` - this method implements handling a reaction, ie one of the 'emoji' you registered
   in the `register_emoji` class method above.  The `message` argument is a `ReactionEvent` from the `frisky.events`
   package and should contain basic information (emoji string, username of the user who received the emoji) as well as 
   a `MessageEvent` instance.            

Note that all 'register' methods are optional, however you must at least implement one and it's corresponding handler
function to do implement any functionality.                  

### An example plugin
This example is included in the source as `ping.py`

```python
from typing import Tuple, Optional

from frisky.plugin import FriskyPlugin


class PingPlugin(FriskyPlugin):

    def register_commands(self) -> Tuple:
        return 'ping',

    def handle_message(self, message) -> Optional[str]:
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
