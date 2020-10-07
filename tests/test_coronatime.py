from datetime import date
from unittest.mock import patch

from frisky.test import FriskyTestCase


class CoronaTimeTestCase(FriskyTestCase):

    def test_ctime(self):
        with patch('plugins.coronatime.date') as mock_date:
            mock_date.today.return_value = date(2020, 10, 7)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?coronatime')
            self.assertEqual('It is the 221st of March, 2020', response)

    def test_ctime_past(self):
        with patch('plugins.coronatime.date') as mock_date:
            mock_date.today.return_value = date(2020, 2, 2)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?coronatime')
            self.assertIsNone(response)

    def test_march_2(self):
        with patch('plugins.coronatime.date') as mock_date:
            mock_date.today.return_value = date(2020, 3, 2)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            response = self.send_message('?coronatime')
            self.assertEqual('It is the 2nd of March, 2020', response)
