#!/usr/bin/python3

import sys
import os
import logging
import datetime
import shutil

from settings import Settings
from discovery import discover
from transfer import batch
from args import CliArgs
from ui import ProgressBar, ask, confirm, choose, notify

def queryDevices(settings):
    """Discover all available devices and warn if not every device is
reachable. Returns a list of available device IDs.
"""
    # show progress bar while discovering devices
    progress = ProgressBar(
        'Suche Schülercomputer',
        '{0}% durchsucht. Bitte warten...')
    available, missing = discover(settings, progress)
    logging.debug(f'Available clients: {available}')
    logging.debug(f'Missing clients: {missing}')

    if len(missing) > 0:
        devlist = ', '.join(map(settings.getDirName, missing))
        msg = f'Folgende Schülercomputer sind nicht erreichbar:\n\n{devlist}\n\nDennoch fortfahren?'
        confirm('Einsammeln', msg)

    return available

# ---------------------------------------------------------------------

def clearShareDirectories(settings, devices):
    for device in devices:
        directory = settings.getShareDir(device)
        cmd = f'rm -r {directory}/*'
        logging.debug(cmd)
        os.system(cmd)
    if len(devices) > 1:
        notify('info', 'Die Austeil-Ordner wurden geleert.')
    else:
        notify('info', 'Der Austeil-Ordner wurde geleert.')

# ---------------------------------------------------------------------

def shareEach(settings):
    """Share individual files with available devices."""
    
    devices = queryDevices(settings)
    first = settings.getDirName(devices[0])
    last = settings.getDirName(devices[-1])

    if len(devices) > 1:
        directories = f'{settings.share}/{first} bis …/{last}'
        clear = 'Die genannten Ordner werden'
    elif len(devices) == 1:
        directories = f'{settings.share}/{first}'
        clear = 'Der genannte Ordner wird'
    else:
        notify('info', 'Es wurden keine verbundenen Schülercomputer gefunden.')
        return
    
    msg = f'Die Dateien in in \n\n    {directories} \n\n' + \
        'werden ausgeteilt. Dies kann einen Moment dauern. Sie werden ' + \
        'benachrichtigt, wenn das Austeilen abgeschlossen ist. \n\nWARNUNG: ' + \
        f'{clear} anschließend VOLLSTÄNDIG GELEERT. Stellen ' + \
        'Sie sicher, dass Sie eine KOPIE der Daten besitzen. \n\n' + \
        '    Fortfahren?'
    ok = ask('Warnung', msg)
    if ok:
        # show progressbar while sharing
        progress = ProgressBar(
            'Zurückgeben',
            '{0}% abgeschlossen. Bitte warten …')
        src = settings.getShareDir
        dst = settings.getExchangeDir
        remote_port = settings.remote_port
        batch(devices, src, dst, remote_port, progress)

        notify('info', 'Das Zurückgeben wurde abgeschlossen.')
        
        # clear share directories
        clearShareDirectories(settings, devices)
        
    else:
         notify('info', 'Der Benutzer hat den Vorgang abgebrochen.')


def shareAll(settings):
    """Share common files with available devices."""
    msg = f'Die Dateien in in \n\n    {settings.shareall} \n\n' + \
        'werden ausgeteilt. Dies kann einen Moment dauern. Sie werden ' + \
        'benachrichtigt, wenn das Austeilen abgeschlossen ist. \n\nWARNUNG: ' + \
        'Der Austeil-Ordner wird anschließend VOLLSTÄNDIG GELEERT. Stellen ' + \
        'Sie sicher, dass Sie eine KOPIE der Daten besitzen. \n\n' + \
        '    Fortfahren?'
    ok = ask('Warnung', msg)
    if ok:
        # helper to force sharing from force 'all'-directory
        def src(device):
            return settings.getShareDir()

        devices = queryDevices(settings)

        # show progress bar while sharing
        progress = ProgressBar('Austeilen', '{0}% abgeschlossen. Bitte warten …')
        dst = settings.getExchangeDir
        remote_port = settings.remote_port
        batch(devices, src, dst, remote_port, progress)

        notify('info', 'Das Austeilen wurde abgeschlossen.')
        # clear share directories
        clearShareDirectories(settings, [None])
    else:
        notify('info', 'Der Benutzer hat den Vorgang abgebrochen.')


def fetch(settings):
    """Fetch files from available devices."""
    devices = queryDevices(settings)

    # show progress bar while fetching
    progress = ProgressBar('Einsammeln', '{0}% abgeschlossen. Bitte warten …')
    src = settings.getExchangeDir
    dst = settings.getFetchDir
    remote_port = settings.remote_port
    batch(devices, src, dst, remote_port, progress)

    notify('info', 'Das Einsammeln wurde abgeschlossen')

    # nach ZIP fragen
    msg = f'Sollen die eingesammelten Dateien zu einem ZIP-Archiv komprimiert werden?'
    ok = ask('ZIP-Archiv', msg)
    if ok:
        zipname = datetime.datetime.now().strftime('%Y-%m-%d_%H-%m-%S.zip')
        zipname = choose('ZIP-Archiv', zipname, filter=['*.zip'])
        if zipname is None:
            notify(
                'error',
                'Der Benutzer hat den Vorgang abgebrochen.')
            return

        shutil.make_archive(zipname, 'zip', settings.fetch)
        logging.debug(f'{zipname} created')
        notify('info', 'Das ZIP-Archiv wurde erstellt')

# ---------------------------------------------------------------------


if __name__ == '__main__':
    try:
        s = Settings()
        fname = s.getPrefDir()

        # make logging verbose
        if '-v' in sys.argv:
            logging.basicConfig(level=logging.DEBUG)

        # load settings or create them from user input
        try:
            s.loadFromFile(fname)
        except FileNotFoundError as e:
            # allow settings creation
            s.setup()

        s.ensureFolders()

        # parse command line arguments to trigger correct mode
        cli = CliArgs()
        cli.register('--share-each', shareEach)
        cli.register('--share-all', shareAll)
        cli.register('--fetch', fetch)

        if not cli(sys.argv, settings=s):
            os.system('cat USAGE.md')

    except KeyboardInterrupt:
        notify('info', 'Der Benutzer hat den Vorgang abgebrochen')

    except SystemExit as e:
        notify('error', e.code)
