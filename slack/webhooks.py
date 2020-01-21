import requests
from django.conf import settings


# POST https://slack.com/api/chat.postMessage
# Content-type: application/json
# Authorization: Bearer YOUR_TOKEN_HERE
# {
#   "channel": "YOUR_CHANNEL_ID",
#   "text": "Hello, world"
# }

def post_message(channel, message):
    if settings.SLACK_ACCESS_TOKEN is None:
        pass
    else:
        headers = {'Authorization': f'Bearer {settings.SLACK_ACCESS_TOKEN}'}
        payload = {
            'channel': channel,
            'text': message,
        }

        requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)


def conversations_info(channel_id):
    if settings.SLACK_ACCESS_TOKEN is None:
        pass
    else:
        headers = {'Authorization': f'Bearer {settings.SLACK_ACCESS_TOKEN}'}
        response = requests.get(f'https://slack.com/api/conversations.info?channel={channel_id}', headers=headers)
        json = response.json()
        if json['ok']:
            return json['channel']


def user_info(user_id):
    """
    Example API Response:
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
        }
    :param user_id:
    :return:
    """
    if settings.SLACK_ACCESS_TOKEN is None:
        pass
    else:
        headers = {'Authorization': f'Bearer {settings.SLACK_ACCESS_TOKEN}'}
        response = requests.get(f'https://slack.com/api/users.info?user={user_id}', headers=headers)
        json = response.json()
        if json['ok']:
            return json['user']


def get_message(channel, timestamp):
    """
    {
        "ok": true,
        "messages": [
            {
                "type": "message",
                "user": "U012AB3CDE",
                "text": "I find you punny and would like to smell your nose letter",
                "ts": "1512085950.000216"
            },
            {
                "type": "message",
                "user": "U061F7AUR",
                "text": "What, you want to smell my shoes better?",
                "ts": "1512104434.000490"
            }
        ],
        "has_more": true,
        "pin_count": 0,
        "response_metadata": {
            "next_cursor": "bmV4dF90czoxNTEyMDg1ODYxMDAwNTQz"
        }
    }
    :param channel:
    :param timestamp:
    :return:
    """
    if settings.SLACK_ACCESS_TOKEN is None:
        pass
    else:
        headers = {'Authorization': f'Bearer {settings.SLACK_ACCESS_TOKEN}'}
        response = requests.get(f'https://slack.com/api/conversations.history?channel=' +
                                f'{channel}&oldest={timestamp}&latest={timestamp}&inclusive=true&limit=1',
                                headers=headers)
        json = response.json()
        if json['ok']:
            return json['messages'][0]


# This is for emergency debugging, and should not be used in a plugin, ever
def log_to_slack(message):
    if settings.DEBUG:
        print(message)
        post_message('frisky-logs', f'```{message}```')
