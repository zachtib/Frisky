from frisky.test import FriskyTestCase
from learns.queries import get_all_learns


class LearnTestCase(FriskyTestCase):

    def test_adding_a_learn(self):
        self.send_message("?learn test foobar")
        count = get_all_learns('test').count()

        self.assertEqual(count, 1)

    def test_adding_a_learn_and_reading_it_back(self):
        self.send_message("?learn test foobar")
        result = self.send_message("?learn test 0")

        self.assertEqual(result, "foobar")

    def test_adding_a_learn_and_reading_it_back_shorthand(self):
        self.send_message("?learn test foobar")
        result = self.send_message("?test 0")

        self.assertEqual(result, "foobar")
