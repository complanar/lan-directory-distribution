#!/usr/bin/python3

import unittest
import ipaddress
import os
import pathlib
import tempfile


from settings import Settings


class SettingTest(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.first_ip = ipaddress.ip_address('1.1.1.10')
        self.settings.num_clients = 50
        self.settings.user = 'tester'

        self.settings.folder_prefix = 'PC'
        self.settings.exchange = pathlib.Path('~/exchange')
        self.settings.fetch = pathlib.Path('~/fetch')
        self.settings.share = pathlib.Path('~/share')
        self.settings.shareall = pathlib.Path('~/shareAll')

    def tearDown(self):
        del self.settings

    def test_loadSave(self):
        tmpfile = tempfile.NamedTemporaryFile(mode='w')
        p = pathlib.Path(tmpfile.name)
        self.settings.saveToFile(p)

        loaded = Settings()
        loaded.loadFromFile(p)

        self.assertEqual(self.settings.first_ip, loaded.first_ip)
        self.assertEqual(self.settings.num_clients, loaded.num_clients)
        self.assertEqual(self.settings.user, loaded.user)
        self.assertEqual(self.settings.folder_prefix, loaded.folder_prefix)
        self.assertEqual(self.settings.exchange, loaded.exchange)
        self.assertEqual(self.settings.fetch, loaded.fetch)
        self.assertEqual(self.settings.share, loaded.share)
        self.assertEqual(self.settings.shareall, loaded.shareall)

    def test_getDirName(self):
        self.assertEqual(self.settings.getDirName(2), 'PC03')
        self.assertEqual(self.settings.getDirName(11), 'PC12')

    def test_getIp(self):
        self.assertEqual(
            ipaddress.ip_address('1.1.1.10'),
            self.settings.getIp(0))
        self.assertEqual(
            ipaddress.ip_address('1.1.1.11'),
            self.settings.getIp(1))
        self.assertEqual(
            ipaddress.ip_address('1.1.1.30'),
            self.settings.getIp(20))

    def test_getFetchDir(self):
        self.assertEqual(
            pathlib.Path('~/fetch/PC03'),
            self.settings.getFetchDir(2))
        self.assertEqual(
            pathlib.Path('~/fetch/PC21'),
            self.settings.getFetchDir(20))

    def test_getShareDir(self):
        self.assertEqual(
            pathlib.Path('~/share/PC03'),
            self.settings.getShareDir(2))
        self.assertEqual(
            pathlib.Path('~/share/PC24'),
            self.settings.getShareDir(23))
        self.assertEqual(
            pathlib.Path('~/shareAll'),
            self.settings.getShareDir())

    def getExchangeDir(self):
        self.assertEqual(
            'tester@1.1.1.10:~/exchange',
            self.settings.getExchangeDir(0))
        self.assertEqual(
            'tester@1.1.1.23:~/exchange',
            self.settings.getExchangeDir(11))
