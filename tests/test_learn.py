from unittest import mock

from frisky.test import FriskyTestCase
from learns.models import Learn
from plugins.learn import LearnPlugin


class LearnTestCase(FriskyTestCase):

    def test_help(self):
        result = self.send_message("?help learn")
        assert all(s in result for s in ['?lc', '?learn_count', ':brain:', '?learn'])

    def test_learn_noop(self):
        self.assertEqual(self.send_message('?learn'), None)

    def test_randoms_empty(self):
        self.assertIsNone(self.send_message('?notinthere'))

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

    def test_learn_free_zone(self):
        self.assertEqual(self.send_reaction('brain', 'george', 'john', reacted_message=None),
                         'This is a learning-free zone!')

    def test_get_nonexistant_learn(self):
        self.assertRaises(ValueError, lambda: Learn.objects.random('?xyzzy'))

    def test_adding_a_learn(self):
        self.send_message("?learn test foobar")
        count = Learn.objects.for_label('test').count()

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
        self.assertEqual(self.send_message('?lc'), '*Learn Counts*\n • test_1: 3\n • test_2: 2')

    def test_learn_count_with_arg(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        self.assertEqual(self.send_message('?lc test_1'), 'Count: 3')

    def test_learn_count_with_nonexistant_arg(self):
        self.assertEqual(self.send_message('?lc test_1'), None)

    def test_learn_count_with_multiple_nonexistant_arga(self):
        self.assertEqual(self.send_message('?lc test_1 test_2'), None)

    def test_learn_count_with_args(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        self.send_message('?learn test_3 thing1')
        self.send_message('?learn test_3 thing2')
        self.assertEqual(self.send_message('?lc test_1 test_2'), '*Learn Counts*\n • test_1: 3\n • test_2: 2')

    def test_learn_count(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        self.assertEqual(self.send_message('?learn_count'), '*Learn Counts*\n • test_1: 3\n • test_2: 2')

    def test_get_random_labeled(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        patcher = mock.patch(target='learns.models.randint', new=lambda *a, **k: 1)
        patcher.start()
        self.assertEqual(self.send_message('?test_1'), 'thing2')
        patcher.stop()

    def test_get_random(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_2 thing2')
        self.send_message('?learn test_3 thing3')
        patcher = mock.patch(target='learns.models.randint', new=lambda *a, **k: 1)
        patcher.start()
        self.assertEqual(self.send_message('?random'), 'test_2: thing2')
        patcher.stop()

    def test_get_random_no_learns_returns_none(self):
        self.assertIsNone(self.send_message('?random'))

    def test_no_such_thing(self):
        self.send_message('?learn test_1 thing1')
        self.assertEqual(self.send_message('?test_1 100'), 'NO SUCH THING')

    def test_that_learn_drop_at_from_username(self):
        reply = self.send_message('?learn @jcarreer I dont test')
        self.assertEqual(reply, 'Okay, learned jcarreer')

    def test_learn_search(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 thing3')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        response = self.send_message('?learn_search test_1 thing')
        self.assertEqual(response, 'thing1\nthing2\nthing3')

    def test_learn_search_exclusion(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 bananaphone')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        response = self.send_message('?learn_search test_1 thing')
        self.assertEqual(response, 'thing1\nthing2')

    def test_learn_search_without_label(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 bananaphone')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        response = self.send_message('?learn_search - thing')
        self.assertEqual(response, 'test_1: thing1\ntest_1: thing2\ntest_2: thing1\ntest_2: thing2')

    def test_that_no_match_falls_back_to_global_search(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 bananaphone')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        response = self.send_message('?ls thing')
        self.assertEqual(response, 'test_1: thing1\ntest_1: thing2\ntest_2: thing1\ntest_2: thing2')

    def test_that_wildcard_syntax_does_not_create_a_learn(self):
        self.send_message('?this should not do anything')
        count = Learn.objects.for_label('this').count()

        self.assertEqual(count, 0)

    def test_learn_search_with_zero_args_returns_the_help_text(self):
        self.send_message('?learn test_1 thing1')
        self.send_message('?learn test_1 thing2')
        self.send_message('?learn test_1 bananaphone')
        self.send_message('?learn test_2 thing1')
        self.send_message('?learn test_2 thing2')
        response = self.send_message('?learn_search')
        self.assertEqual(response, LearnPlugin.help)
