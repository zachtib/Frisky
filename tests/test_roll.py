from unittest import mock

from frisky.test import FriskyTestCase


class RollTestCase(FriskyTestCase):

    def test_roll_defaults_to_d20(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled 10', self.send_message('?roll'))
        patcher.stop()

    def test_roll_takes_param(self):
        def roll(arg1, arg2):
            self.assertEqual(1, arg1)
            self.assertEqual(6, arg2)

        patcher = mock.patch(target='plugins.roll.randint', new=roll)
        patcher.start()
        self.send_message('?roll 6')
        patcher.stop()

    def test_invalid_input_rolls_20(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled 10', self.send_message('?roll potato'))
        patcher.stop()

    def test_multiple_inputs(self):
        patcher = mock.patch(target='plugins.roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled 10, 10, 10', self.send_message('?roll 20 20 20'))
        patcher.stop()
