import responses
from django.test import TestCase

from .api.tests import URL
from .api.tests import USER_OK
from .tasks import sanitize_message_text


class EventHandlingTestCase(TestCase):

    def test_username_substitution(self):
        with responses.RequestsMock() as rm:
            rm.add('GET', f'{URL}/users.info?user=W012A3CDE', body=USER_OK)
            result = sanitize_message_text('<@W012A3CDE> is a jerk')
            self.assertEqual('spengler is a jerk', result)
