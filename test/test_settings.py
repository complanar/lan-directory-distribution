#!/usr/bin/python3

import unittest
import ipaddress

from settings import Settings


class SettingTest(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.first_ip = ipaddress.ip_address('1.1.1.10')
        self.settings.num_clients = 50
        self.settings.user = 'tester'

        self.settings.folder_prefix = 'PC'
        self.settings.exchange = '~/exchange'
        self.settings.fetch = '~/fetch'
        self.settings.share = '~/share'
        self.settings.shareall = '~/shareAll'

    def tearDown(self):
        del self.settings

    def test_getDirName(self):
        self.assertEqual(self.settings.getDirName(2), 'PC03')
        self.assertEqual(self.settings.getDirName(11), 'PC12')

    def test_getIp(self):
        self.assertEqual('1.1.1.10', str(self.settings.getIp(0)))
        self.assertEqual('1.1.1.11', str(self.settings.getIp(1)))
        self.assertEqual('1.1.1.30', str(self.settings.getIp(20)))

    def test_getFetchDir(self):
        self.assertEqual('~/fetch/PC03', self.settings.getFetchDir(2))
        self.assertEqual('~/fetch/PC21', self.settings.getFetchDir(20))

    def test_getShareDir(self):
        self.assertEqual('~/share/PC03', self.settings.getShareDir(2))
        self.assertEqual('~/share/PC24', self.settings.getShareDir(23))
        self.assertEqual('~/shareAll', self.settings.getShareDir())

    def getExchangeDir(self):
        self.assertEqual(
            'tester@1.1.1.10:~/exchange',
            self.settings.getExchangeDir(0))
        self.assertEqual(
            'tester@1.1.1.23:~/exchange',
            self.settings.getExchangeDir(11))
