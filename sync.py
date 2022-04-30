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
from ui import ProgressBar, ask, choose, notify


def queryDevices(settings):
    progress = ProgressBar(
        'Suche Schülercomputer',
        '{0}% durchsucht. Bitte warten...')
    return discover(settings, progress)


def getDevicesList(devices):
    return ', '.join(map(str, devices))


# ---------------------------------------------------------------------

def shareEach(settings):
    devices = queryDevices(settings)
    devlist = getDevicesList(devices)

    msg = f'An folgende Schülercomputern können Daten zurückgegeben werden:\n\n{devlist}\n\nFortfahren?'
    ok = ask('Einsammeln', msg)
    if not ok:
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')
        return

    progress = ProgressBar(
        'Zurückgeben',
        '{0}% abgeschlossen. Bitte warten...')

    src = settings.getShareDir
    dst = settings.getExchangeDir
    ok = batch(devices, src, dst, progress)
    if not ok:
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')
        return

    notify('transfer.complete', 'Zurückgeben fertig',
           'Das Zurückgeben wurde abgeschlossen')
    # FIXME: clear shares


def shareAll(settings):
    devices = queryDevices(settings)
    devlist = getDevicesList(devices)

    msg = f'An folgende Schülercomputern kann ausgeteilt werden werden:\n\n{devlist}\n\nFortfahren?'
    ok = ask('Einsammeln', msg)
    if not ok:
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')
        return

    progress = ProgressBar('Austeilen', '{0}% abgeschlossen. Bitte warten...')

    def src(device): return settings.getShareDir()  # force 'all'
    dst = settings.getExchangeDir
    ok = batch(devices, src, dst, progress)
    if not ok:
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')
        return

    notify(
        'transfer.complete',
        'Austeilen fertig',
        'Das Austeilen wurde abgeschlossen')


def fetch(settings):
    devices = queryDevices(settings)
    devlist = getDevicesList(devices)

    msg = f'Von folgenden Schülercomputern kann eingesammelt werden:\n\n{devlist}\n\nFortfahren?'
    ok = ask('Einsammeln', msg)
    if not ok:
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')
        return

    progress = ProgressBar('Einsammeln', '{0}% abgeschlossen. Bitte warten...')

    src = settings.getExchangeDir
    dst = settings.getFetchDir
    ok = batch(devices, src, dst, progress)
    if not ok:
        notify(
            'transfer.error',
            'Abgebrochen',
            'Der Benutzer hat den Vorgang abgebrochen')
        return

    notify('transfer.complete', 'Einsammeln fertig',
           'Das Einsammeln wurde abgeschlossen')

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


if __name__ == '__main__':
    # enable verbosity
    if '-v' in sys.argv:
        logging.basicConfig(level=logging.DEBUG)

    s = Settings()
    s.loadFromFile('settings.cfg')
    s.ensureFolders()

    cli = CliArgs()
    cli.register('--share-each', shareEach)
    cli.register('--share-all', shareAll)
    cli.register('--fetch', fetch)

    if not cli(sys.argv, settings=s):
        os.system('cat USAGE.md')
