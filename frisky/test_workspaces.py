from datetime import datetime, timezone
from unittest import mock

from django.test import TestCase

import responses

from frisky.models import Workspace, Member, Channel
from slack.test_data import user_json

slack_not_ok = '''
{
    "ok": false
}
'''

slack_team_ok = '''
{
    "ok": true,
    "team": {
        "id": "W12345",
        "name": "My Team",
        "domain": "example",
        "email_domain": "example.com",
        "icon": {
            "image_34": "https://...",
            "image_44": "https://...",
            "image_68": "https://...",
            "image_88": "https://...",
            "image_102": "https://...",
            "image_132": "https://...",
            "image_default": true
        },
        "enterprise_id": "E1234A12AB",
        "enterprise_name": "Umbrella Corporation"
    }
}
'''.strip()


class FriskyWorkspaceTestCase(TestCase):

    def setUp(self) -> None:
        self.workspace = Workspace.objects.create(
            updated=datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0),
            kind=Workspace.Kind.SLACK,
            team_id='W12345',
            name='Slack Space',
            domain='example.com',
            access_token='xoxo-my_secret_token',
        )
        expired_date = datetime(year=2021, month=5, day=1, hour=12, minute=0, second=0)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=expired_date)):
            self.expired_workspace = Workspace.objects.create(
                kind=Workspace.Kind.SLACK,
                team_id='W67890',
                name='Expired Slack Space',
                domain='refreshme',
                access_token='xoxo-my_secret_token',
            )

    def test_workspace_string(self):
        self.assertEqual('Slack Workspace Slack Space', str(self.workspace))

    @responses.activate
    def test_getting_workspace_with_no_access_token_is_an_error(self):
        with self.assertRaises(RuntimeError,
                               msg='Cannot create a new Slack Workspace when SLACK_ACCESS_TOKEN is undefined'):
            Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, 'W01234')

    @responses.activate
    def test_getting_workspace_when_none_exists(self):
        responses.add(responses.GET, url='https://slack.com/api/team.info?team=W01234', body=slack_team_ok)
        with self.settings(SLACK_ACCESS_TOKEN='xoxo-my_secret_token'):
            workspace = Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, 'W01234')
        self.assertEqual(workspace.team_id, 'W01234')
        self.assertEqual(workspace.name, 'My Team')
        self.assertEqual(workspace.domain, 'example')

    @responses.activate
    def test_getting_workspace_when_it_is_expired(self):
        responses.add(responses.GET, url='https://slack.com/api/team.info?team=W67890', body=slack_team_ok)
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            workspace = Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, 'W67890')
        self.assertEqual('My Team', workspace.name)
        self.assertEqual('example', workspace.domain)

    @responses.activate
    def test_getting_expired_workspace_returns_even_if_api_fails(self):
        responses.add(responses.GET, url='https://slack.com/api/team.info?team=W67890', body=slack_not_ok)
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            workspace = Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, 'W67890')
        self.assertEqual(self.expired_workspace.name, workspace.name)
        self.assertEqual(self.expired_workspace.domain, workspace.domain)

    @responses.activate
    def test_getting_workspace_when_it_exists(self):
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=2, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            workspace = Workspace.objects.get_or_fetch_by_kind_and_id(Workspace.Kind.SLACK, 'W12345')
        self.assertEqual(self.workspace.id, workspace.id)


user_ok_response = '''
{
    "ok": true,
    "user": {
        "id": "W012A3CDE",
        "team_id": "T012AB3C4",
        "name": "spengler",
        "deleted": false,
        "color": "9f69e7",
        "real_name": "Egon Spengler",
        "tz": "America/Los_Angeles",
        "tz_label": "Pacific Daylight Time",
        "tz_offset": -25200,
        "profile": {
            "avatar_hash": "ge3b51ca72de",
            "status_text": "Print is dead",
            "status_emoji": ":books:",
            "real_name": "Real Name",
            "display_name": "displayname",
            "real_name_normalized": "Real Name Normalized",
            "display_name_normalized": "displaynamenormalized",
            "email": "spengler@ghostbusters.example.com",
            "image_original": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
            "team": "T012AB3C4"
        },
        "is_admin": true,
        "is_owner": false,
        "is_primary_owner": false,
        "is_restricted": false,
        "is_ultra_restricted": false,
        "is_bot": false,
        "updated": 1502138686,
        "is_app_user": false,
        "has_2fa": false
    }
}'''.strip()


class FriskyMemberTestCase(TestCase):

    def setUp(self) -> None:
        self.workspace = Workspace.objects.create(
            kind=Workspace.Kind.SLACK,
            team_id='W12345',
            name='Slack Space',
            domain='example.com',
            access_token='xoxo-my_secret_token',
        )
        self.valid_member = Member.objects.create(
            workspace=self.workspace,
            user_id='W012A3CDE',
            name='fbot',
            real_name='Frisky Bot',
        )
        expired_date = datetime(year=2021, month=5, day=1, hour=12, minute=0, second=0)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=expired_date)):
            self.expired_member = Member.objects.create(
                workspace=self.workspace,
                user_id='W012A3CDF',
                name='rbot',
                real_name='Risky Bot',
            )

    def test_member_string(self):
        self.assertEqual('fbot in Slack Workspace Slack Space', str(self.valid_member))

    @responses.activate
    def test_getting_member_when_none_exists(self):
        self.valid_member.delete()
        responses.add(responses.GET, url='https://slack.com/api/users.info?user=W012A3CDE', body=user_ok_response)
        member = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'W012A3CDE')
        self.assertEqual('W012A3CDE', member.user_id)
        self.assertEqual('spengler', member.name)
        self.assertEqual('Egon Spengler', member.real_name)

    @responses.activate
    def test_getting_member_when_it_is_expired(self):
        responses.add(responses.GET, url='https://slack.com/api/users.info?user=W012A3CDF', body=user_ok_response)
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            member = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'W012A3CDF')
        self.assertEqual('W012A3CDF', member.user_id)
        self.assertEqual('spengler', member.name)
        self.assertEqual('Egon Spengler', member.real_name)

    @responses.activate
    def test_getting_expired_member_returns_even_if_api_fails(self):
        responses.add(responses.GET, url='https://slack.com/api/users.info?user=W012A3CDF', body=slack_not_ok)
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            member = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'W012A3CDF')
        self.assertEqual('W012A3CDF', member.user_id)
        self.assertEqual('rbot', member.name)
        self.assertEqual('Risky Bot', member.real_name)

    @responses.activate
    def test_getting_member_when_it_exists(self):
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=2, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            member = Member.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'W012A3CDE')
        self.assertEqual(self.valid_member.id, member.id)


channel_ok = '''
{
    "ok": true,
    "channel": {
        "id": "C012AB3CD",
        "name": "general",
        "is_channel": true,
        "is_group": false,
        "is_im": false,
        "created": 1449252889,
        "creator": "W012A3BCD",
        "is_archived": false,
        "is_general": true,
        "unlinked": 0,
        "name_normalized": "general",
        "is_read_only": false,
        "is_shared": false,
        "parent_conversation": null,
        "is_ext_shared": false,
        "is_org_shared": false,
        "pending_shared": [],
        "is_pending_ext_shared": false,
        "is_member": true,
        "is_private": false,
        "is_mpim": false,
        "last_read": "1502126650.228446",
        "topic": {
            "value": "For public discussion of generalities",
            "creator": "W012A3BCD",
            "last_set": 1449709364
        },
        "purpose": {
            "value": "This part of the workspace is for fun. Make fun here.",
            "creator": "W012A3BCD",
            "last_set": 1449709364
        },
        "previous_names": [
            "specifics",
            "abstractions",
            "etc"
        ],
        "locale": "en-US"
    }
}'''.strip()

im_ok = '''
{
    "ok": true,
    "channel": {
        "id": "C012AB3CD",
        "created": 1507235627,
        "is_im": true,
        "is_org_shared": false,
        "user": "U27FFLNF4",
        "last_read": "1513718191.000038",
        "latest": {
            "type": "message",
            "user": "U5R3PALPN",
            "text": "Psssst!",
            "ts": "1513718191.000038"
        },
        "unread_count": 0,
        "unread_count_display": 0,
        "is_open": true,
        "locale": "en-US",
        "priority": 0.043016851216706
    }
}'''.strip()


class FriskyChannelTestCase(TestCase):

    def setUp(self) -> None:
        self.workspace = Workspace.objects.create(
            kind=Workspace.Kind.SLACK,
            team_id='W12345',
            name='Slack Space',
            domain='example.com',
            access_token='xoxo-my_secret_token',
        )
        self.valid_channel = Channel.objects.create(
            workspace=self.workspace,
            channel_id='C012AB3CD',
            name='general',
            is_channel=True,
            is_group=False,
            is_private=False,
            is_im=False,
        )
        expired_date = datetime(year=2021, month=5, day=1, hour=12, minute=0, second=0)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=expired_date)):
            self.expired_channel = Channel.objects.create(
                workspace=self.workspace,
                channel_id='C012AB3CE',
                name='hidden',
                is_channel=True,
                is_group=False,
                is_private=True,
                is_im=False,
            )

    def test_channel_string(self):
        self.assertEqual('#general in Slack Workspace Slack Space', str(self.valid_channel))

    @responses.activate
    def test_getting_channel_when_none_exists(self):
        self.valid_channel.delete()
        responses.add(responses.GET, url='https://slack.com/api/conversations.info?channel=C012AB3CD', body=channel_ok)
        channel = Channel.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'C012AB3CD')
        self.assertEqual('C012AB3CD', channel.channel_id)
        self.assertEqual('general', channel.name)

    @responses.activate
    def test_getting_channel_when_it_is_expired(self):
        responses.add(responses.GET, url='https://slack.com/api/conversations.info?channel=C012AB3CE', body=channel_ok)
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            channel = Channel.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'C012AB3CE')
        self.assertEqual('C012AB3CE', channel.channel_id)
        self.assertEqual('general', channel.name)

    @responses.activate
    def test_getting_expired_channel_returns_even_if_api_fails(self):
        responses.add(responses.GET, url='https://slack.com/api/conversations.info?channel=C012AB3CE', body=slack_not_ok)
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=1, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            channel = Channel.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'C012AB3CE')
        self.assertEqual('C012AB3CE', channel.channel_id)
        self.assertEqual('hidden', channel.name)

    @responses.activate
    def test_getting_channel_when_it_exists(self):
        with mock.patch('frisky.models.timezone') as mock_datetime:
            mock_datetime.now.return_value = datetime(year=2021, month=6, day=2, hour=12, minute=0, second=0,
                                                      tzinfo=timezone.utc)
            channel = Channel.objects.get_or_fetch_by_workspace_and_id(self.workspace, 'C012AB3CD')
        self.assertEqual('general', channel.name)
        self.assertTrue(channel.is_channel)
