from django.test import TestCase

from frisky.bot import get_plugin


class PluginLoaderTestCase(TestCase):
    def test_loading_plugins(self):
        print('Trying to load plugins')
        ping = get_plugin('ping')
        print(ping)
