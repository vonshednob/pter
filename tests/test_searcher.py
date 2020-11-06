import unittest
import pathlib

from pytodotxt import Task

from pter import utils
from pter.searcher import Searcher
from pter.source import Source


class FakeSource:
    def __init__(self, tasks):
        self.tasks = tasks
        self.filename = pathlib.Path('/tmp/test.txt')


class SearcherTest(unittest.TestCase):
    def setUp(self):
        self.searcher = Searcher('', False)

    def search(self, text, tasks):
        self.searcher.text = text
        self.searcher.parse()
        result = []
        source = Source(FakeSource(tasks))
        source.update_contexts_and_projects()
        self.searcher.update_sources([source])
        for task in source.tasks:
            if self.searcher.match(task):
                result.append(task)
        return result


class TestAfter(SearcherTest):
    def test_show_all(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 after:1')]
        results = self.search('after:', tasks)
        self.assertEqual(len(results), 2)

    def test_hide_after(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 after:1')]
        results = self.search('', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['1'])

    def test_recursion(self):
        tasks = [Task('a id:1 after:3'),
                 Task('b id:2 after:1'),
                 Task('c id:3 after:2')]
        results = self.search('', tasks)
        self.assertEqual(len(results), 0)

    def test_more_parents(self):
        tasks = [Task('a id:1'),
                 Task('b id:2'),
                 Task('c after:1,2')]
        results = self.search('', tasks)
        self.assertEqual(len(results), 2)

        results = self.search('after:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertIn('c', str(results[0]))

    def test_parent_completed(self):
        tasks = [Task('x a id:1'),
                 Task('b after:1 id:test')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['test'])

    def test_some_parents_completed(self):
        tasks = [Task('x a id:1'),
                 Task('b id:2'),
                 Task('c id:3 after:1,2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_some_parents_completed2(self):
        tasks = [Task('x a id:1'),
                 Task('b id:2'),
                 Task('c id:3 after:1 after:2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_all_parents_completed(self):
        tasks = [Task('x a id:1'),
                 Task('x b id:2'),
                 Task('c id:3 after:1,2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['3'])

    def test_all_parents_completed2(self):
        tasks = [Task('x a id:1'),
                 Task('x b id:2'),
                 Task('c id:3 after:1 after:2')]
        results = self.search('done:n', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['3'])


class TestIDs(SearcherTest):
    def test_id(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['1'])

    def test_id_not_there(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:3', tasks)
        self.assertEqual(len(results), 0)

    def test_ids(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:1,2', tasks)
        self.assertEqual(len(results), 2)

    def test_ids2(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('id:1 id:2', tasks)
        self.assertEqual(len(results), 2)

    def test_not_id(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('-id:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_not_ids(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('-id:1,2', tasks)
        self.assertEqual(len(results), 0)

    def test_not_ids2(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('-id:1 -id:2', tasks)
        self.assertEqual(len(results), 0)

    def test_has_id(self):
        tasks = [Task('a id:1'),
                 Task('b')]
        results = self.search('id:', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['1'])

    def test_has_no_id(self):
        tasks = [Task('a id:1'),
                 Task('b')]
        results = self.search('-id:', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(str(results[0]), 'b')


class TestRef(SearcherTest):
    def test_ref_not_there(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('ref:2', tasks)
        self.assertEqual(len(results), 0)

    def test_ref_search(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1')]
        results = self.search('ref:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_after_search(self):
        tasks = [Task('x a id:1'),
                 Task('t id:2 after:1')]
        results = self.search('ref:1', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_ref_multiple(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1,4')]
        results = self.search('ref:4', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

    def test_ref_multiple2(self):
        tasks = [Task('a id:1'),
                 Task('b id:2 ref:1 ref:4')]
        results = self.search('ref:4', tasks)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].attr_id, ['2'])

