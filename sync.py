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

    if len(missing) > 0:
        devlist = ', '.join(map(str, missing))
        msg = f'Folgende Schülercomputer sind nicht erreichbar:\n\n{devlist}\n\nDennoch fortfahren?'
        confirm('Einsammeln', msg)

    return available


# ---------------------------------------------------------------------

def shareEach(settings):
    """Share individual files with available devices."""
    devices = queryDevices(settings)

    # show progressbar while sharing
    progress = ProgressBar(
        'Zurückgeben',
        '{0}% abgeschlossen. Bitte warten...')
    src = settings.getShareDir
    dst = settings.getExchangeDir
    batch(devices, src, dst, progress)

    notify('transfer.complete', 'Zurückgeben fertig',
           'Das Zurückgeben wurde abgeschlossen')
    # FIXME: clear shares


def shareAll(settings):
    """Share common files with available devices."""
    devices = queryDevices(settings)

    # show progress bar while sharing
    progress = ProgressBar('Austeilen', '{0}% abgeschlossen. Bitte warten...')
    def src(device): return settings.getShareDir()  # force 'all'
    dst = settings.getExchangeDir
    batch(devices, src, dst, progress)

    notify(
        'transfer.complete',
        'Austeilen fertig',
        'Das Austeilen wurde abgeschlossen')


def fetch(settings):
    """Fetch files from available devices."""
    devices = queryDevices(settings)

    # show progress bar while fetching
    progress = ProgressBar('Einsammeln', '{0}% abgeschlossen. Bitte warten...')
    src = settings.getExchangeDir
    dst = settings.getFetchDir
    batch(devices, src, dst, progress)

    notify('transfer.complete', 'Einsammeln fertig',
           'Das Einsammeln wurde abgeschlossen')

    """
    # nach ZIP fragen
    msg = f'Sollen die eingesammelten Dateien zu einem ZIP-Archiv komprimiert werden?'
    ok = ask('ZIP-Archiv', msg)
    if ok:
        zipname = datetime.datetime.now().strftime('%Y-%m-%d_%H-%m-%S.zip')
        zipname = choose('ZIP-Archiv', zipname, filter=['*.zip'])
        if zipname is None:
            notify(
                'transfer.error',
                'Abgebrochen',
                'Der Benutzer hat den Vorgang abgebrochen')
            return

        shutil.make_archive(zipname, 'zip', settings.fetch)
        logging.debug(f'{zipname} created')
        notify(
            'transfer.complete',
            'ZIP erstellt',
            'Das ZIP-Archiv wurde erstellt')
    """

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
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')

    except SystemExit as e:
        notify(
            'transfer.error',
            e.args[0], e.args[1])
