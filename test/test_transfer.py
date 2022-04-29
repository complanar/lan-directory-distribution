#!/usr/bin/python3

import unittest, ipaddress

from settings import Settings
from transfer import TransferWorker, batch

class DummyProgress(object):
    def __init__(self):
        self.value = 0.0
    
    def __call__(self, value):
        self.value = value

    def getStatus(self):
        if self.value == 1.0:
            return True
        return None

# ---------------------------------------------------------------------

class TransferTest(unittest.TestCase):
        
    def setUp(self):
        self.settings = Settings()
        self.settings.first_ip    = ipaddress.ip_address('0.0.0.1')
        self.settings.num_clients = 5 
        self.settings.user        = 'tester'

        self.settings.folder_prefix = 'PC'
        self.settings.exchange      = '~/exchange'
        self.settings.fetch         = '~/fetch'
        self.settings.share         = '~/share'
        self.settings.shareall      = '~/shareAll'
        
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
        status = batch(devices, src_lambda, dst_lambda, p)
        self.assertTrue(status) 
