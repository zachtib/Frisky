from django.test import TestCase

from frisky.models import Workspace, Channel
from frisky.test import FriskyTestCase
from plugins.betterstonks.models import BetterStonkGame
from plugins.betterstonks.plugin import StonksPlugin


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

    def test_db(self):
        BetterStonkGame.objects.create(channel=self.channel, starting_balance=1000.00)
        games = BetterStonkGame.objects.all()
        self.assertEqual(1, games.count())


class MultiWorkspaceStonkGameTestCase(TestCase):

    def setUp(self) -> None:
        self.ws1 = Workspace.objects.create(kind=Workspace.Kind.SLACK, team_id='T1', name='One',
                                            domain='one', access_token='xoxo-my_secret_token')
        self.ws2 = Workspace.objects.create(kind=Workspace.Kind.SLACK, team_id='T2', name='Two',
                                            domain='two', access_token='xoxo-my_secret_token')

        self.c1 = Channel.objects.create(workspace=self.ws1, channel_id='C1XXXXXXX', name='general',
                                         is_channel=True, is_group=False, is_private=False, is_im=False)
        self.c2 = Channel.objects.create(workspace=self.ws2, channel_id='C2XXXXXXX', name='general',
                                         is_channel=True, is_group=False, is_private=False, is_im=False)

    def test_creation_from_queryset_sets_workspace(self):
        BetterStonkGame.objects.in_workspace(self.ws1).create(channel=self.c1, starting_balance=500.00)

        self.assertEqual(1, BetterStonkGame.objects.count())
        record = BetterStonkGame.objects.first()
        self.assertEqual(self.ws1, record.workspace)

    def test_filtering_by_workspace(self):
        BetterStonkGame.objects.create(workspace=self.ws1, channel=self.c1, starting_balance=250.00)
        BetterStonkGame.objects.create(workspace=self.ws2, channel=self.c2, starting_balance=500.00)
