#!/usr/bin/python3

import threading
import subprocess
import time
import logging


class PingWorker(threading.Thread):
    """Thread to handle pinging a device."""

    def __init__(self, device, ip, count=1, wait=1):
        """Setup threaded ping to the given IP."""
        super().__init__()
        self.device = device
        self.ip = ip
        self.count = count
        self.wait = wait
        self.status = None

        self.start()

    def run(self):
        """Trigger ping as subprocess and save reachability status."""
        cmd = f'ping {self.ip} -c {self.count} -W {self.wait}'
        logging.debug(cmd)
        p = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.status = p.returncode == 0


def discover(settings, progress, delay=0.1):
    """Discovers devices in the given range via ping. Returns a list of available devices."""
    # setup workers
    worker = list()
    for device in range(settings.num_clients):
        ip = settings.getIp(device)
        worker.append(PingWorker(device, ip))

    # wait and update progress bar
    n = settings.num_clients - 1
    while n > 0 and progress.getStatus() is None:
        # calculate progress based on number of active threads
        n = threading.activeCount() - 1
        progress((settings.num_clients - n) / settings.num_clients)
        time.sleep(delay)

    # build device list
    devices = list()
    for w in worker:
        if w.status:
            devices.append(w.device)

    return devices
