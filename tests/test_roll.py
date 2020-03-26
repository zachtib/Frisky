from unittest import mock

from frisky.test import FriskyTestCase


class RollTestCase(FriskyTestCase):
    def test_roll_defaults_to_d20(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled 10 on 1d20 with a chance of 5%', self.send_message('?roll'))
        patcher.stop()

    def test_roll_takes_param(self):
        def roll(arg1, arg2):
            self.assertEqual(1, arg1)
            self.assertEqual(6, arg2)
            return 0

        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=roll)
        patcher.start()
        self.send_message('?roll 1d6')
        patcher.stop()

    def test_roll_considers_modifier(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 0)
        patcher.start()
        result = self.send_message('?roll 1d6+1')
        patcher.stop()
        self.assertEqual('dummyuser rolled 1 on 1d6+1 with a chance of 16.67%', result)

    def test_roll_considers_negative_modifier(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 0)
        patcher.start()
        result = self.send_message('?roll 1d6-1')
        patcher.stop()
        self.assertEqual('dummyuser rolled -1 on 1d6-1 with a chance of 16.67%', result)

    def test_invalid_input_shames_user(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled ???... I don\'t know how to roll potato', self.send_message('?roll potato'))
        patcher.stop()

    def test_multiple_inputs(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 10)
        patcher.start()
        self.assertEqual('dummyuser rolled 10 on 1d20 with a chance of 5%, 10 on 1d20 with a chance of 5%, 10 on 1d20 with a chance of 5% for a total of 30', self.send_message('?roll 1d20 1d20 1d20'))
        patcher.stop()

    def test_big_numbers(self):
        self.assertRegexpMatches(self.send_message('?roll 1000000d10000'), '^dummyuser rolled [0-9]+ USING MATH on [0-9]+d[0-9]+ with a chance of [0-9.e-]+%ish$')

    def test_bad_big_numbers(self):
        self.assertEqual('dummyuser rolled ???... I don\'t know how to roll 11000d-10000', self.send_message('?roll 11000d-10000'))

    def test_critical(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 20)
        patcher.start()
        result = self.send_message('?roll 2d20+1')
        patcher.stop()
        self.assertEqual('dummyuser rolled CRITICAL 41 on 2d20+1 with a chance of 0.25%', result)

    def test_quiet(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 20)
        patcher.start()
        result = self.send_message('?roll 2d20+1q')
        patcher.stop()
        self.assertEqual('dummyuser rolled 41 on 2d20+1', result)

    def test_reasonable_estimation(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 4)
        patcher.start()
        result = self.send_message('?roll 10d6')
        patcher.stop()
        self.assertEqual('dummyuser rolled 40 on 10d6 with a chance of 4.81%ish', result)

    def test_slowest_possible(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 50)
        patcher.start()
        result = self.send_message('?roll 4d50')
        patcher.stop()
        self.assertEqual('dummyuser rolled CRITICAL 200 on 4d50 with a chance of 0.000016%', result)


    def test_weird_result(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 100)
        patcher.start()
        result = self.send_message('?roll 100d100')
        patcher.stop()
        # I mean, this is wrong - the estimator gets bad values close to the extremes
        self.assertEqual('dummyuser rolled CRITICAL 10000 on 100d100 with a chance of 0%ish', result)


    def test_critical_fail(self):
        patcher = mock.patch(target='plugins.roll.die_roll.randint', new=lambda *a, **k: 1)
        patcher.start()
        result = self.send_message('?roll 2d50')
        patcher.stop()
        self.assertEqual('dummyuser rolled CRITICAL FAIL 2 on 2d50 with a chance of 0.04%', result)

    def test_zero_dice(self):
        result = self.send_message('?roll 0d10')
        self.assertEqual('dummyuser rolled CRITICAL 0 on 0d10 with a chance of 100%', result)
