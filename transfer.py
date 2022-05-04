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
        self.status = None
        self.start()

    def run(self):
        """Trigger scp as subprocess and save success status."""
        cmd = f'scp -o ConnectTimeout={self.timeout} -rP {self.port} {self.src}/* {self.dst}/*'
        logging.debug(cmd)
        p = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.status = p.returncode == 0


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
    while n > 0 and progress.is_alive():
        # calculate progress based on number of active workers
        n = sum(1 if w.is_alive() else 0 for w in worker)
        progress((num_devices - n) / num_devices)
        time.sleep(delay)
    progress.finish()

    # count successes and failures
    successes = 0
    failures = 0
    for w in worker:
        w.join()
        if w.status:
            successes += 1
        else:
            failures += 1

    if failures > 0:
        raise SystemExit(
            f'{failures} von {num_devices} Übertragungen sind fehlgeschlagen.')
