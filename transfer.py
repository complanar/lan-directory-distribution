#!/usr/bin/python3

import subprocess
import threading
import time
import logging


class TransferWorker(threading.Thread):
    """Thread to handle copy via SSH."""

    def __init__(self, src, dst, port=32400, timeout=3):
        """Transer files from {src} to {dst}."""
        super().__init__()
        self.src = src
        self.dst = dst
        self.port = port
        self.timeout = timeout
        self.start()

    def run(self):
        cmd = f'scp -o ConnectTimeout={self.timeout} -rP {self.port} {self.src}/* {self.dst}/*'
        logging.debug(cmd)
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)


def batch(devices, src_lambda, dst_lambda, progress, delay=0.1):
    """Batch transfer for {devices}. Source and destination folders will
be picked based on the actual device using {src_lambda} and {dst_lambda}.
"""
    # setup workers
    worker = list()
    for device in devices:
        src = src_lambda(device)
        dst = dst_lambda(device)
        worker.append(TransferWorker(src, dst))

    # wait and update progress bar
    num_devices = len(devices)
    n = num_devices
    while n > 0 and progress.getStatus() is None:
        n = threading.activeCount() - 1
        progress((num_devices - n) / num_devices)
        time.sleep(delay)

    # FIXME: progress.getStatus() isn't working correctly; failed SCPs are not
    # checked
    return n == 0
