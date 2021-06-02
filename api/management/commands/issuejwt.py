import jwt
from django.conf import settings
from django.core.management import BaseCommand

from api.models import ApiToken


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--workspace_id',
            required=True,
        )
        parser.add_argument(
            '--name',
            required=True,
        )
        parser.add_argument(
            '--learn',
        )
        parser.add_argument(
            '--general',
            action='store_true',
        )

    def handle(self, *args, **options):
        payload = None
        if options['learn'] is not None:
            payload = {
                'label': options['learn']
            }
        elif options['general']:
            payload = {
                'general': 'true'
            }

        if payload is not None:
            api_token = ApiToken.objects.create(name=options['name'])
            payload['uuid'] = str(api_token.uuid)
            payload['workspace_id'] = options['workspace_id']
            result = jwt.encode(
                payload=payload,
                key=settings.JWT_SECRET,
                algorithm='HS256'
            )
            result = result.decode('UTF-8')
            print(f'token: {result}', file=self.stdout)
