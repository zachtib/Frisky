import json
import logging

from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.util import get_jwt_from_headers
from frisky.events import MessageEvent
from frisky.models import Workspace, Member, Channel
from learns.models import Learn
from slack.tasks import SlackWrapper


@csrf_exempt
def get_response(request):
    if request.method != 'POST':
        raise Http404()

    api_token = get_jwt_from_headers(request.headers)
    if api_token.get('general', None) != 'true':
        logging.debug('Token was valid, but not for general api')
        raise Http404()
    workspace_id = api_token.get('workspace_id', None)
    if workspace_id is None:
        logging.debug('Old Token did not contain a workspace_id')
        raise Http404()
    workspace = Workspace.objects.get(id=workspace_id)
    if workspace.kind == Workspace.Kind.SLACK:
        received_json_data = json.loads(request.body.decode("utf-8"))

        message = received_json_data['message']
        username = received_json_data['username']
        channel_name = received_json_data['channel']

        user = Member.objects.get(workspace=workspace, name=username)
        channel = Channel.objects.get(workspace=workspace, name=channel_name)

        if not message.startswith(settings.FRISKY_PREFIX):
            message = f'{settings.FRISKY_PREFIX}{message}'

        wrapper = SlackWrapper(workspace, channel, user)
        responses = wrapper.handle_raw(message)

        return JsonResponse({
            'replies': responses,
        })
    else:
        logging.debug('API only supports Slack workspaces for now')
        raise Http404()


def random_learn(request):
    jwt = get_jwt_from_headers(request.headers)
    label = jwt.get('label', None)
    workspace_id = jwt.get('workspace_id', None)
    if workspace_id is None:
        logging.debug('Old Token did not contain a workspace_id')
        raise Http404()
    try:
        Workspace.objects.get(id=workspace_id)
    except Workspace.DoesNotExist:
        logging.debug(f'Workspace with id {workspace_id} did not exist')
        raise Http404()
    try:
        learn = Learn.objects.random(label)
    except ValueError:
        raise Http404()
    return JsonResponse({
        'result': learn.content,
    })
