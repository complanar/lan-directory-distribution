#!/usr/bin/python3

import configparser
import ipaddress
import os
import logging
import pathlib
import sys


def input_default(msg, default):
    v = input(msg)
    if v == '':
        v = default
    return v


class Settings(object):
    """Holds configuration details."""

    def getPrefDir(self, appname='lan_share'):
        """Return path to ~/.local/share/<appname>/settings.cfg"""
        # setup filename
        p = pathlib.Path.home()
        if sys.platform.startswith('linux'):
            p = p / ".local" / "share"
        else:
            raise NotImplementedError('only linux supported')
        p = p / appname

        if not p.exists():
            p.mkdir()

        return p / 'settings.cfg'
    
    def loadFromFile(self, fname):
        cfg = configparser.ConfigParser()
        if not os.path.exists(fname):
            raise FileNotFoundError(fname)
        cfg.read(fname)

        self.first_ip = ipaddress.ip_address(cfg['network']['first_ip'])
        self.num_clients = int(cfg['network']['num_clients'])
        self.user = cfg['network']['user']

        self.folder_prefix = cfg['folders']['prefix']
        self.exchange = cfg['folders']['exchange']
        self.share = cfg['folders']['share'].replace(
            '~', os.path.expanduser('~'))
        self.fetch = cfg['folders']['fetch'].replace(
            '~', os.path.expanduser('~'))
        self.shareall = cfg['folders']['shareall'].replace(
            '~', os.path.expanduser('~'))

    def saveToFile(self, fname):
        cfg = configparser.ConfigParser()
        cfg['network'] = {
            'first_ip': self.first_ip,
            'num_clients': self.num_clients,
            'user': self.user
        }
        cfg['folders'] = {
            'prefix': self.folder_prefix,
            'exchange': self.exchange,
            'share': self.share,
            'fetch': self.fetch,
            'shareall': self.shareall
        }

        with open(fname, 'w') as handle:
            cfg.write(handle)

    def setup(self):
        """Prompt settings creation wizard."""

        print('Settings cannot not found but can be created:')

        self.first_ip = input_default('IP of the first Client [192.168.2.100]: ', '192.168.2.100')
        self.num_clients = int(input_default('Number of total clients [15]: ', 15))
        self.user = input_default('Remote username to login to [schueler]: ', 'schueler')

        self.folder_prefix = input_default('Prefix of local folders per device [S]: ', 'S')
        self.exchange = input_default('Remote exchange directory [~/Schreibtisch/Austausch]', '~/Schreibtisch/Austausch')
        self.share = input_default('Local share base directory [~/Schreibtisch/Austeilen]:', '~/Schreibtisch/Austeilen')
        self.fetch = input_default('Local fetch base directory [~/Schreibtisch/Eingesammelt]:', '~/Schreibtisch/Eingesammelt')
        self.shareall = input_default('Local share-all directory [~/Schreibtisch/Austeilen/Alle]:', '~/Schreibtisch/Austausch/Alle')

        fname = self.getPrefDir()
        self.saveToFile(fname)

        logging.debug(f'Saved to {fname}')

    
    def ensureFolders(self):
        for folder in [self.share, self.fetch, self.shareall]:
            if not os.path.isdir(folder):
                os.makedirs(folder)
                logging.debug(f'{folder} created')

        for folder in [self.share, self.fetch]:
            for device in range(self.num_clients):
                subfolder = self.getDirName(device)
                tmp = os.path.join(folder, subfolder)
                if not os.path.isdir(tmp):
                    os.mkdir(tmp)
                    logging.debug(f'{tmp} created')

    def getDirName(self, device):
        """Return local fetch directory for a device, e.g. S03 for device #2"""
        return self.folder_prefix + str(device + 1).zfill(2)

    def getIp(self, device):
        """Return IP of a device."""
        return self.first_ip + device

    def getFetchDir(self, device):
        """Return local fetch directory path for the given device."""
        return os.path.join(self.fetch, self.getDirName(device))

    def getShareDir(self, device=None):
        """Return local share directory path for the given device. Use common share folder if no device is specified. """
        if device is None:
            return self.shareall
        else:
            return os.path.join(self.share, self.getDirName(device))

    def getExchangeDir(self, device):
        """Return remote path to device's exchange directory."""
        return f'{self.user}@{self.getIp(device)}:{self.exchange}'
