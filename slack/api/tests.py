import json
from typing import Union

import pytest
import responses

from app import settings
from slack.api.client import SlackApiClient
from slack.api.models import Conversation, Message, User, Team

URL = 'https://slack.com/api'
USER_OK = """{
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
            "real_name": "Egon Spengler",
            "display_name": "spengler",
            "real_name_normalized": "Egon Spengler",
            "display_name_normalized": "spengler",
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
}"""
USER_OK_MODEL = User.from_dict(json.loads(USER_OK)['user'])


class TestClient:

    @pytest.fixture()
    def client(self) -> SlackApiClient:
        yield SlackApiClient('test-token')

    @pytest.mark.parametrize('cid, payload, expected', [
        ('test_ok', {'ok': True, 'messages': [{'user': 'jim', 'text': 'Im great', 'ts': '1581947248'}]},
         Message(user='jim', text='Im great', ts='1581947248')),
        ('test_not_ok', {'ok': False}, None),
    ])
    @pytest.mark.django_db
    def test_get_message(self, client: SlackApiClient, cid: str, payload: dict, expected: Union[None, Message]):
        """Tests SlackApiClient.get_message"""
        with responses.RequestsMock() as rm:
            ts = '1581947248'
            api = f'{URL}/conversations.history?channel={cid}&oldest={ts}&latest={ts}&inclusive=true&limit=1'
            rm.add('GET', api, body=json.dumps(payload))
            if not payload['ok']:
                rm.add('POST', f'{URL}/chat.postMessage')
            assert client.get_message(Conversation(id=cid, name='test'), ts) == expected
            assert 'Authorization' in rm.calls[0].request.headers
            # Should be from cache, because we in a requests mock context, if we hit the API again the test wil fail
            # with a connection issue
            assert client.get_message(Conversation(id=cid, name='test'), ts) == expected

    @pytest.mark.parametrize('uid, payload, expected', [
        ('test_ok', USER_OK, USER_OK_MODEL),
        ('test_not_ok', '{"ok": false}', None),
    ])
    @pytest.mark.django_db
    def test_get_user(self, client: SlackApiClient, uid: str, payload: str, expected: Union[None, Message]):
        """Tests SlackApiClient.get_user"""
        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/users.info?user={uid}', body=payload)
            if not json.loads(payload)['ok']:
                rm.add('POST', f'{URL}/chat.postMessage')
            assert client.get_user(uid) == expected
            assert 'Authorization' in rm.calls[0].request.headers
            # Should be from cache, because we in a requests mock context, if we hit the API again the test wil fail
            # with a connection issue
            assert client.get_user(uid) == expected

    @pytest.mark.parametrize('cid, payload, expected', [
        ('test_ok', {'ok': True, 'channel': {'id': 'test_ok', 'name': 'test'}},
         Conversation(id='test_ok', name='test')),
        ('test_not_ok', {'ok': False}, None),
    ])
    @pytest.mark.django_db
    def test_get_channel(self, client: SlackApiClient, cid: str, payload: dict, expected: Union[None, Message]):
        """Tests SlackApiClient.get_channel"""
        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/conversations.info?channel={cid}', body=json.dumps(payload))
            if not payload['ok']:
                rm.add('POST', f'{URL}/chat.postMessage')
            assert client.get_channel(cid) == expected
            assert 'Authorization' in rm.calls[0].request.headers
            # Should be from cache, because we in a requests mock context, if we hit the API again the test wil fail
            # with a connection issue
            assert client.get_channel(cid) == expected

    @pytest.mark.parametrize('tid, payload, expected', [
        ('test_ok', {'ok': True, 'team': {'id': 'test_ok', 'name': 'test', 'domain': '502nerds.com'}},
         Team(id='test_ok', name='test', domain='502nerds.com')),
        ('test_not_ok', {'ok': False}, None),
    ])
    @pytest.mark.django_db
    def test_get_team(self, client: SlackApiClient, tid: str, payload: dict, expected: Union[None, Message]):
        """Tests SlackApiClient.get_team"""
        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/team.info?team={tid}', body=json.dumps(payload))
            if not payload['ok']:
                rm.add('POST', f'{URL}/chat.postMessage')
            assert client.get_workspace(tid) == expected
            assert 'Authorization' in rm.calls[0].request.headers
            # Should be from cache, because we in a requests mock context, if we hit the API again the test wil fail
            # with a connection issue
            assert client.get_workspace(tid) == expected

    @pytest.mark.django_db
    def test_post_message(self, client: SlackApiClient):
        """Tests SlackApiClient.post_message"""
        with responses.RequestsMock() as rm:
            rm.add('POST', f'{URL}/chat.postMessage')
            client.post_message(Conversation(id='test', name='test'), 'message')
            assert 'Authorization' in rm.calls[0].request.headers
            assert json.loads(rm.calls[0].request.body) == {'channel': 'test', 'text': 'message'}

    @pytest.mark.django_db
    def test_update_message(self, client: SlackApiClient):
        """Tests SlackApiClient.update_message"""
        with responses.RequestsMock() as rm:
            rm.add('POST', f'{URL}/chat.update')
            client.update_message(Conversation(id='test', name='test'),
                                  Message(user='jcarreer', text='I never test mah code', ts='12345.67890'),
                                  text='I always test mah code')
            assert 'Authorization' in rm.calls[0].request.headers
            assert json.loads(rm.calls[0].request.body) == {
                'channel': 'test',
                'text': 'I always test mah code',
                'ts': '12345.67890'
            }

    @pytest.mark.django_db
    def test_delete_message(self, client: SlackApiClient):
        """Tests SlackApiClient.delete_message"""
        with responses.RequestsMock() as rm:
            rm.add('POST', f'{URL}/chat.delete')
            client.delete_message(
                Conversation(id='test', name='test'),
                Message(user='jcarreer', text='I never test mah code', ts='12345.67890')
            )
            assert 'Authorization' in rm.calls[0].request.headers
            assert json.loads(rm.calls[0].request.body) == {'channel': 'test', 'ts': '12345.67890'}

    @pytest.mark.django_db
    def test_post_image(self, client: SlackApiClient):
        with responses.RequestsMock() as rm:
            rm.add('POST', f'{URL}/chat.postMessage')
            client.post_image(Conversation(id='test', name='test'), 'http://i.imgflip.com/blah.jpg', 'Image')
            assert 'Authorization' in rm.calls[0].request.headers
            assert json.loads(rm.calls[0].request.body) == {'channel': 'test', 'blocks': [{
                "type": "image",
                "image_url": 'http://i.imgflip.com/blah.jpg',
                "alt_text": "Image"
            }]}

    @pytest.mark.django_db
    def test_post_emergency_log(self, client: SlackApiClient):
        """Tests SlackApiClient.emergency_log"""
        with responses.RequestsMock() as rm:
            rm.add('POST', f'{URL}/chat.postMessage')
            client.emergency_log('FUCK')
            expected = {'channel': settings.FRISKY_LOGGING_CHANNEL, 'text': '```FUCK```'}
            assert 'Authorization' in rm.calls[0].request.headers
            assert json.loads(rm.calls[0].request.body) == expected
