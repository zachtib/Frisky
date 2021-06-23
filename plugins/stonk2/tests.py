from frisky.test import FriskyTestCase
from plugins.stonk2.plugin import StonksPlugin


class StonkGameTestCase(FriskyTestCase):

    def test_plugin_is_loaded(self):
        found_plugin = False
        for plugin in self.frisky.get_loaded_plugins():
            if isinstance(plugin, StonksPlugin):
                found_plugin = True
        self.assertTrue(found_plugin, "StonksPlugin was not loaded")

    def test_this_is_tested(self):
        result = self.send_message("?stonkifyme")
        self.assertEqual("Hello, there", result)
