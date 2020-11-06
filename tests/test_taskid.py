import unittest
import pathlib

from pytodotxt import Task

from pter import utils
from pter.source import Source


class FakeSource:
    def __init__(self, tasks):
        self.tasks = tasks
        self.filename = pathlib.Path('/tmp/test.txt')


class TestTaskIDGeneration(unittest.TestCase):
    def setUp(self):
        self.sources = [
                Source(FakeSource([Task('task id:30'), Task('task id:prefixed22')])),
                Source(FakeSource([Task('task id:41')]))]
        self.sources[0].update_contexts_and_projects()
        self.sources[1].update_contexts_and_projects()

    def test_no_prefix_no_existing(self):
        sources = [Source(FakeSource([]))]
        sources[0].update_contexts_and_projects()
        nextid = utils.new_task_id(sources)
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

    def test_decimals(self):
        sources = [Source(FakeSource([Task('task id:9'), Task('task id:12')]))]
        sources[0].update_contexts_and_projects()
        nextid = utils.new_task_id(sources)
        self.assertEqual(nextid, '13')

