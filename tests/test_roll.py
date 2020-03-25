from unittest import mock

from frisky.test import FriskyTestCase


class RollTestCase(FriskyTestCase):

    def test_roll_defaults_to_d20(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('Rolling 1d20 for dummyuser: 10', self.send_message('?roll'))
        patcher.stop()

    def test_roll_takes_param(self):
        def roll(arg1, arg2):
            self.assertEqual(1, arg1)
            self.assertEqual(6, arg2)
            return 0

        patcher = mock.patch(target='plugins.roll.randint', new=roll)
        patcher.start()
        self.send_message('?roll 1d6')
        patcher.stop()

    def test_roll_considers_modifier(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 0)
        patcher.start()
        result = self.send_message('?roll 1d6+1')
        patcher.stop()
        self.assertEqual('dummyuser rolled 1', result)

    def test_roll_considers_negative_modifier(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 0)
        patcher.start()
        result = self.send_message('?roll 1d6-1')
        patcher.stop()
        self.assertEqual('dummyuser rolled -1', result)

    def test_invalid_input_shames_user(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled ???... I don\'t know how to roll potato', self.send_message('?roll potato'))
        patcher.stop()

    def test_multiple_inputs(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled 10, 10, 10', self.send_message('?roll 1d20 1d20 1d20'))
        patcher.stop()

    def test_big_numbers(self):
        self.assertRegexpMatches(self.send_message('?roll 1000000d10000'), '^dummyuser rolled [0-9]+ USING MATH$')

    def test_bad_big_numbers(self):
        self.assertEqual('dummyuser rolled ???... I don\'t know how to roll 11000d-10000', self.send_message('?roll 11000d-10000'))
