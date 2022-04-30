#!/usr/bin/python3

import unittest

from args import CliArgs


class ArgsTest(unittest.TestCase):

    def setCall(self, value):
        self.called = value

    def setUp(self):
        self.called = None
        self.args = CliArgs()
        self.args.register('--foo-bar', lambda: self.setCall('first'))
        self.args.register('--test', lambda: self.setCall('second'))

    def tearDown(self):
        del self.called
        del self.args

    def test_call(self):
        ok = self.args(['./me.py', '--foo-bar'])
        self.assertTrue(ok)
        self.assertEqual(self.called, 'first')

        self.called = None
        ok = self.args(['./me.py', '--foo-bar', '--test'])
        self.assertTrue(ok)
        self.assertEqual(self.called, 'first')

        self.called = None
        ok = self.args(['./me.py', '--crap', '--test'])
        self.assertTrue(ok)
        self.assertEqual(self.called, 'second')

        self.called = None
        ok = self.args(['./me.py', '--crap', '--bullshit'])
        self.assertFalse(ok)
        self.assertEqual(self.called, None)
