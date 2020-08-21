from django.test import TestCase

from learns.models import Learn


class LearnModelTestCase(TestCase):

    def test_tostring(self):
        learn = Learn(label='foo', content='bar')
        self.assertEqual(str(learn), 'foo: "bar"')
