import datetime
import unittest

from pytodotxt import Task
from pter import utils


class TestPter(unittest.TestCase):
    def test_parse_duration(self):
        text = '1h10m'
        then = utils.parse_duration(text)
        self.assertEqual(then, datetime.timedelta(hours=1, minutes=10))

    def test_update_spent(self):
        then = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime(utils.DATETIME_FMT)
        task = Task(f'Something spent:1h10m tracking:{then}')

        self.assertTrue(utils.update_spent(task))
        self.assertEqual(task.attributes, {'spent': ['1h20m']})


class TestHumanFriendlyDates(unittest.TestCase):
    def today(self, daydiff=0):
        return (datetime.date.today() + datetime.timedelta(days=daydiff)).strftime(Task.DATE_FMT)

    def test_today(self):
        then = self.today()
        self.assertEqual(utils.human_friendly_date(then), "today")

    def test_tomorrow(self):
        then = self.today(+1)
        self.assertEqual(utils.human_friendly_date(then), "tomorrow")

    def test_yesterday(self):
        then = self.today(-1)
        self.assertEqual(utils.human_friendly_date(then), "yesterday")


if __name__ == '__main__':
    unittest.main()

