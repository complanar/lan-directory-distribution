#!/usr/bin/python3

import configparser, ipaddress, os, logging

class Settings(object):
    """Holds configuration details."""
    
    def loadFromFile(self, fname):
        cfg = configparser.ConfigParser()
        cfg.read(fname)

        self.first_ip    = ipaddress.ip_address(cfg['network']['first_ip'])
        self.num_clients = int(cfg['network']['num_clients'])
        self.user        = cfg['network']['user']

        self.folder_prefix = cfg['folders']['prefix']
        self.exchange      = cfg['folders']['exchange']
        self.share         = cfg['folders']['share'].replace('~', os.path.expanduser('~'))
        self.fetch         = cfg['folders']['fetch'].replace('~', os.path.expanduser('~'))
        self.shareall      = cfg['folders']['shareall'].replace('~', os.path.expanduser('~'))

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
        return self.folder_prefix + str(device+1).zfill(2)

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
