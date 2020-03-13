from unittest import mock

from frisky.test import FriskyTestCase


class ShuffleTestCase(FriskyTestCase):

    def test_shuffle(self):
        patcher = mock.patch(target='plugins.shuffle.randint', new=lambda a, b: a)
        patcher.start()
        self.assertEqual('x, y, z', self.send_message('?shuffle x y z'))
        patcher.stop()

    def test_shuffle_inverse(self):
        patcher = mock.patch(target='plugins.shuffle.randint', new=lambda a, b: b)
        patcher.start()
        self.assertEqual('z, y, x', self.send_message('?shuffle x y z'))
        patcher.stop()
