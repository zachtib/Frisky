from unittest import TestCase


class PluginLoaderTestCase(TestCase):
    def test_loading_plugins(self):
        from frisky.plugin import PLUGINS
        print(PLUGINS)
