from frisky.test import FriskyTestCase
from learns.queries import get_all_learns, get_random_learn


class LearnTestCase(FriskyTestCase):

    def test_help(self):
        result = self.send_message("?help learn")
        assert all(s in result for s in ['?lc', '?learn_count', ':brain:', '?learn'])

    def test_get_nonexistant_learn(self):
        self.assertRaises(ValueError, lambda: get_random_learn('xyzzy'))

    def test_adding_a_learn(self):
        self.send_message("?learn test foobar")
        count = get_all_learns('test').count()

        self.assertEqual(count, 1)

    def test_adding_a_learn_and_reading_it_back(self):
        self.send_message("?learn test foobar")
        result = self.send_message("?learn test 0")

        self.assertEqual(result, "foobar")

    def test_learn_ignores_case(self):
        self.send_message("?learn test foobar")
        result = self.send_message("?learn Test 0")

        self.assertEqual(result, "foobar")

    def test_adding_a_learn_and_reading_it_back_shorthand(self):
        self.send_message("?learn test foobar")
        result = self.send_message("?test 0")

        self.assertEqual(result, "foobar")

    def test_negative_indexing(self):
        self.send_message('?learn test thing1')
        self.send_message('?learn test thing2')
        self.send_message('?learn test thing3')

        result = self.send_message('?test -1')

        self.assertEqual(result, 'thing3')

    def test_learn_count_alias(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        self.assertEqual(self.send_message('?lc'), '*Counts*\n • test_1: 3\n • test_2: 2')

    def test_learn_count(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        self.assertEqual(self.send_message('?learn_count'), '*Counts*\n • test_1: 3\n • test_2: 2')
