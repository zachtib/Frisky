import jwt
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--learn',
        )
        parser.add_argument(
            '--general',
            action='store_true'
        )

    def handle(self, *args, **options):
        if options['learn'] is not None:
            result = jwt.encode(
                payload={
                    'label': options['learn']
                },
                key=settings.JWT_SECRET,
                algorithm='HS256'
            )

            print(f'learn: {result}')
        if options['general']:
            result = jwt.encode(
                payload={
                    'general': 'true'
                },
                key=settings.JWT_SECRET,
                algorithm='HS256'
            )

            print(f'general: {result}')