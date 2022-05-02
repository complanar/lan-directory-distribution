#!/usr/bin/python3

import unittest
import ipaddress

from settings import Settings
from discovery import PingWorker, discover


class DummyProgress(object):
    def __init__(self):
        self.value = 0.0

    def __call__(self, value):
        self.value = value

    def is_alive(self):
        return self.value == 1.0

    def finish(self):
        self.value = 1.0

# ---------------------------------------------------------------------


class DiscoveryTest(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.first_ip = ipaddress.ip_address('127.0.0.0')
        self.settings.num_clients = 5

    def tearDown(self):
        del self.settings

    def test_PingWorker(self):
        w = PingWorker(5, '127.0.0.1')
        w.join()
        self.assertTrue(w.status)

        w = PingWorker(5, '0.0.0.1')
        w.join()
        self.assertFalse(w.status)

    def test_discover(self):
        p = DummyProgress()
        available, missing = discover(self.settings, p)
        self.assertEqual(p.value, 1.0)
        self.assertEqual(available, [1, 2, 3, 4])
        self.assertEqual(missing, [0])

        self.settings.first_ip = ipaddress.ip_address('0.0.0.1')
        p = DummyProgress()
        with self.assertRaises(SystemExit):
            devices = discover(self.settings, p)
        
