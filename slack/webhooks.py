import requests
from django.conf import settings


# POST https://slack.com/api/chat.postMessage
# Content-type: application/json
# Authorization: Bearer YOUR_TOKEN_HERE
# {
#   "channel": "YOUR_CHANNEL_ID",
#   "text": "Hello, world"
# }

def post_message(channel, message, token):
    if settings.SLACK_ACCESS_TOKEN is None:
        pass
    else:
        headers = {'Authorization': f'Bearer {token}'}
        payload = {
            'channel': channel,
            'text': message,
        }
        requests.post('https://slack.com/api/chat.postMessage', json=payload, headers=headers)
