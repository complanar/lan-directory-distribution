#!/usr/bin/python3

import subprocess, threading
import sys, os, time

from uiwrapper import ProgressBar, ask, notify

def getTwoDigits(device):
	"""Return a device string with two digits."""
	return f'0{device}' if device < 10 else str(device)

def getDirName(device):
	"""Return local fetch directory for a device."""
	suffix = getTwoDigits(device)
	return f'S{suffix}'

def getIp(device):
	"""Return IP of a device."""
	suffix = getTwoDigits(device)
	return f'192.168.2.2{suffix}'

def getFetchDir(device):
	"""Return local fetch directory path for the given device."""
	dirname = getDirName(device)
	return f'~/Schreibtisch/Eingesammelt/{dirname}'

def getShareDir(device):
	"""Return local share directory path for the given device."""
	dirname = getDirName(device)
	return f'~/Schreibtisch/Austeilen/{dirname}'

def getShareAllDir(device):
	"""Return local share directory path for ALL devices. The actual device is ignored here"""
	return f'~/Schreibtisch/Austeilen/Alle'

def getExchangeDir(device, user='schueler'):
	"""Return remote path to device's exchange directory."""
	ip = getIp(device)
	return f'{user}@{ip}:~/Schreibtisch/Austausch'

# ---------------------------------------------------------------------

def askFetch(devices):
	devlist = ', '.join(map(str, devices))
	msg = f'Von folgenden Schülercomputern kann eingesammelt werden:\n\n{devlist}\n\nFortfahren?'
	return ask('Einsammeln', msg)

def askShare(devices):
	devlist = ', '.join(map(str, devices))
	msg = f'An folgende Schülercomputern können Daten zurückgegeben werden:\n\n{devlist}\n\nFortfahren?'
	return ask('Zurückgeben', msg)

def askShareAll(devices):
	devlist = ', '.join(map(str, devices))
	msg = f'An folgende Schülercomputern kann ausgeteilt werden werden:\n\n{devlist}\n\nFortfahren?'
	return ask('Austeilen', msg)

# ---------------------------------------------------------------------

class PingWorker(threading.Thread):
	"""Thread to handle pinging a device."""
	def __init__(self, device, count=1, ttl=1):
		super().__init__()
		self.device = device
		self.count  = count
		self.ttl    = ttl
		self.status = None
		
		self.start()
		
	def run(self):
		ip = getIp(self.device)
		cmd = f'ping {ip} -c {self.count} -t {self.ttl}'
		p = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE,
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		self.status = p.returncode == 0

def discover(min_device=1, max_device=15, delay=0.1):
	"""Discovers devices in the given range via ping. Returns a list of available devices.
"""
	# setup workers
	worker = list()
	for device in range(min_device, max_device+1):
		worker.append(PingWorker(device))
	
	# wait and update progress bar
	num_devices = max_device + 1 - min_device
	n = num_devices - 1
	msg = 'Bisher wurden {0}% der Geräte durchsucht. Bitte warten...'
	progress = ProgressBar('Suche nach Schülercomputern', msg)
	while n > 0 and progress.getStatus() is None:
		n = threading.activeCount() - 1
		progress((num_devices - n) / num_devices)
		time.sleep(delay)
	
	# build device list
	devices = list()
	for w in worker:
		if w.status:
			devices.append(w.device)
	
	notify('network', 'Suche', 'Es wurden {0} Schülercomputer gefunden'.format(len(devices)))
	return devices

# ---------------------------------------------------------------------

class ScpWorker(threading.Thread):
	"""Thread to handle copy via SSH."""
	def __init__(self, src, dst, port=32400, timeout=3):
		super().__init__()
		self.src     = src
		self.dst     = dst
		self.port    = port
		self.timeout = timeout
		self.start()

	def run(self):
		cmd = f'scp -o ConnectTimeout={self.timeout} -rP {self.port} {self.src} {self.dst}'
		subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

def batch(src_func, dst_func, devices, progress, delay=0.1):
	# setup workers
	worker = list()
	for device in devices:
		src = src_func(device)
		dst = dst_func(device)
		worker.append(ScpWorker(src, dst))
	
	# wait and update progress bar
	num_devices = len(devices)
	n = num_devices
	while n > 0 and progress.getStatus() is None:
		n = threading.activeCount() - 1
		progress((num_devices - n) / num_devices)
		time.sleep(delay)
	
	# FIXME: progress.getStatus() isn't working correctly; failed SCPs are not checked
	return n == 0

# ---------------------------------------------------------------------

def fetch():
	devices = discover()
	
	ok = askFetch(devices)
	if not ok:
		notify('transfer.error', 'Abgebrochen', 'Der Benutzer hat den Vorgang abgebrochen')
		return
	
	progress = ProgressBar('Einsammeln', '{0}% abgeschlossen. Bitte warten...')
	ok = batch(getExchangeDir, getFetchDir, devices, progress)
	if not ok:
		notify('transfer.error', 'Abgebrochen', 'Der Benutzer hat den Vorgang abgebrochen')
		return
	
	notify('transfer.complete', 'Einsammeln fertig', 'Das Einsammeln wurde abgeschlossen')
	# FIXME: compress to zip


def shareEach():
	devices = discover()
	
	ok = askShare(devices)
	if not ok:
		notify('transfer.error', 'Abgebrochen', 'Der Benutzer hat den Vorgang abgebrochen')
		return
	
	progress = ProgressBar('Zurückgeben', '{0}% abgeschlossen. Bitte warten...')
	ok = batch(getShareDir, getExchangeDir, devices, progress)
	if not ok:
		notify('transfer.error', 'Abgebrochen', 'Der Benutzer hat den Vorgang abgebrochen')
		return
	
	notify('transfer.complete', 'Zurückgeben fertig', 'Das Zurückgeben wurde abgeschlossen')
 	# FIXME: clear shares

def shareAll():
	devices = discover()
	
	ok = askShareAll(devices)
	if not ok:
		notify('transfer.error', 'Abgebrochen', 'Der Benutzer hat den Vorgang abgebrochen')
		return
	
	progress = ProgressBar('Austeilen', '{0}% abgeschlossen. Bitte warten...')
	ok = batch(getShareAllDir, getExchangeDir, devices, progress)
	if not ok:
		notify('transfer.error', 'Abgebrochen', 'Der Benutzer hat den Vorgang abgebrochen')
		return
	
	notify('transfer.complete', 'Austeilen fertig', 'Das Austeilen wurde abgeschlossen')

# ---------------------------------------------------------------------

if __name__ == '__main__':
	try:
		mode = sys.argv[1]
	except:
		os.system('cat USAGE.md')
		sys.exit(0)
	
	if mode == '--fetch':
		fetch()
		
	elif mode == '--share-each':
		shareEach()
		
	elif mode == '--share-all':
		shareAll()
		
	else:
		os.system('cat USAGE.md')

