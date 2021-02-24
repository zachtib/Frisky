from django.core.management import BaseCommand

from slack.tasks import process_from_cli


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--channel',
        )
        parser.add_argument(
            '--username',
        )
        parser.add_argument(
            '--repeat',
            type=int,
            default=1
        )
        parser.add_argument(
            'message',
            nargs='+'
        )

    def handle(self, *args, **options):
        message = ' '.join(options['message'])
        for _ in range(options['repeat']):
            process_from_cli({
                'channel': options.get('channel', 'bot-testing'),
                'username': options.get('username', 'system'),
                'message': message
            })
