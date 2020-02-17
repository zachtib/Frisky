from frisky.test import FriskyTestCase
from learns.queries import get_all_learns, get_random_learn
from unittest import mock


class LearnTestCase(FriskyTestCase):

    def test_help(self):
        result = self.send_message("?help learn")
        assert all(s in result for s in ['?lc', '?learn_count', ':brain:', '?learn'])

    def test_learn_noop(self):
        self.assertEqual(self.send_message('?learn'), None)

    def test_randoms_empty(self):
        self.assertEqual(self.send_message('?notinthere'), 'I got nothing, boss')

    def test_randoms_empty_with_errors(self):
        self.send_message('?learn error Finally some good fucking coverage')
        self.assertEqual(self.send_message('?notinthere'), 'Finally some good fucking coverage')

    def test_dont_hurt_me(self):
        self.assertEqual(self.send_message('?learn thing ?test'), "DON'T HURT ME AGAIN")

    def test_double_learn(self):
        self.send_message('?learn test_1 thing1')
        self.assertEqual(self.send_message('?learn test_1 thing1'), None)

    def test_reaction_learn(self):
        self.assertEqual(self.send_reaction('brain', 'jim', 'jarjar'), 'Okay, learned jarjar')

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

    def test_get_random(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        patcher = mock.patch(target='learns.queries.randint', new=lambda *a, **k: 1)
        patcher.start()
        self.assertEqual(self.send_message('?test_1'), 'thing2')
        patcher.stop()

    def test_no_such_thing(self):
        self.send_message('?learn test_1 thing1')
        self.assertEqual(self.send_message('?test_1 100'), 'NO SUCH THING')
