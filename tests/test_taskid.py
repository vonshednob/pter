import unittest

from pter import utils


class FakeSource:
    def __init__(self, taskids):
        self._taskids = taskids

    @property
    def task_ids(self):
        return self._taskids


class TestTaskIDGeneration(unittest.TestCase):
    def setUp(self):
        self.sources = [
                FakeSource({'30', 'prefixed22'}),
                FakeSource({'41'})]

    def test_no_prefix_no_existing(self):
        nextid = utils.new_task_id([FakeSource(set())])
        self.assertEqual(nextid, '1')

    def test_no_prefix_existing(self):
        nextid = utils.new_task_id(self.sources)
        self.assertEqual(nextid, '42')

    def test_prefix_no_existing(self):
        nextid = utils.new_task_id(self.sources, 'project')
        self.assertEqual(nextid, 'project1')

    def test_prefix_existing(self):
        nextid = utils.new_task_id(self.sources, 'prefixed')
        self.assertEqual(nextid, 'prefixed23')

