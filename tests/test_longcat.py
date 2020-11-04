from frisky.test import FriskyTestCase


class LearnTestCase(FriskyTestCase):

    def test_no_arguments_returns_nothing(self):
        self.assertIsNone(self.send_message('?longcat'))

    def test_two_arguments_returns_nothing(self):
        self.assertIsNone(self.send_message('?longcat banana pudding'))

    def test_nonint_argument_returns_nothing(self):
        self.assertIsNone(self.send_message('?longcat pudding'))

    def test_longcat_1(self):
        actual = self.send_message('?longcat 1')
        expected = (
            ':longcat-begin:\n'
            ':longcat-middle:\n'
            ':longcat-end:'
        )
        self.assertEqual(expected, actual)

    def test_longcat_3(self):
        actual = self.send_message('?longcat 3')
        expected = (
            ':longcat-begin:\n'
            ':longcat-middle:\n'
            ':longcat-middle:\n'
            ':longcat-middle:\n'
            ':longcat-end:'
        )
        self.assertEqual(expected, actual)

    def test_tacgnol_1(self):
        actual = self.send_message('?longcat -1')
        expected = (
            ':dne-tacgnol:\n'
            ':elddim-tacgnol:\n'
            ':nigeb-tacgnol:'
        )
        self.assertEqual(expected, actual)

    def test_tacgnol_3(self):
        actual = self.send_message('?longcat -3')
        expected = (
            ':dne-tacgnol:\n'
            ':elddim-tacgnol:\n'
            ':elddim-tacgnol:\n'
            ':elddim-tacgnol:\n'
            ':nigeb-tacgnol:'
        )
        self.assertEqual(expected, actual)
