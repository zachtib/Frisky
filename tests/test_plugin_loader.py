from django.test import TestCase

from frisky.bot import Frisky
from plugins.ping import PingPlugin


class PluginLoaderTestCase(TestCase):
    def test_loading_plugins(self):
        frisky = Frisky('frisky')
        ping = frisky.get_plugins_for_command('ping')[0]
        self.assertIsInstance(ping, PingPlugin)
