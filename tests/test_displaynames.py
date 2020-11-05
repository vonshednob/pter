import unittest
import pathlib

from pter import utils


class FakeSource:
    def __init__(self, location):
        self.filename = pathlib.Path(location)
        self.displayname = self.filename.name


class TestDisplayNames(unittest.TestCase):
    def setUp(self):
        pass

    def test_case1(self):
        sources = [FakeSource('/home/me/some/place/todo.txt'),
                   FakeSource('/home/me/other.txt')]
        utils.update_displaynames(sources)

        self.assertEqual(sources[0].displayname, 'todo.txt')
        self.assertEqual(sources[1].displayname, 'other.txt')

    def test_case2(self):
        sources = [FakeSource('/home/me/some/todo.txt')]
        utils.update_displaynames(sources)
        self.assertEqual(sources[0].displayname, 'todo.txt')


    def test_case3(self):
        sources = [FakeSource('/home/me/some/todo.txt'),
                   FakeSource('/home/me/other/todo.txt')]
        utils.update_displaynames(sources)
        self.assertEqual(sources[0].displayname, 'some/todo.txt')
        self.assertEqual(sources[1].displayname, 'other/todo.txt')

    def test_case4(self):
        sources = [FakeSource('/me/some/todo.txt'),
                   FakeSource('/me/todo.txt'),
                   FakeSource('/me/other/todo.txt')]
        utils.update_displaynames(sources)
        self.assertEqual(sources[0].displayname, 'some/todo.txt')
        self.assertEqual(sources[1].displayname, 'me/todo.txt')
        self.assertEqual(sources[2].displayname, 'other/todo.txt')

