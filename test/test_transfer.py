#!/usr/bin/python3

import unittest
import ipaddress
import pathlib

from settings import Settings
from transfer import TransferWorker, batch


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


class TransferTest(unittest.TestCase):

    def setUp(self):
        self.settings = Settings()
        self.settings.first_ip = ipaddress.ip_address('0.0.0.1')
        self.settings.num_clients = 5
        self.settings.user = 'tester'

        self.settings.folder_prefix = 'PC'
        self.settings.exchange = pathlib.Path('~/exchange')
        self.settings.fetch = pathlib.Path('~/fetch')
        self.settings.share = pathlib.Path('~/share')
        self.settings.shareall = pathlib.Path('~/shareAll')

    def tearDown(self):
        del self.settings

    def test_TransferWorker(self):
        w = TransferWorker('/tmp/from', 'tester@0.0.0.1:/tmp/to')
        w.join()

    def test_batch(self):
        p = DummyProgress()
        devices = [1, 3, 4]
        src_lambda = self.settings.getExchangeDir
        dst_lambda = self.settings.getFetchDir
        with self.assertRaises(SystemExit):
            # may fail anyway because there is no SSH server available
            # during unittest
            batch(devices, src_lambda, dst_lambda, p)
        
