#!/usr/bin/python3

import subprocess
import threading
import tempfile
import logging


class ProgressBar(threading.Thread):
    """Creates a zenity-based progress bar that can be altered.

pb = ProgressBar('Please Wait', 'Current progress is {0}%, please wait')
pb(0.5)
# later
pb(0.75)
if pb.is_alive():
    # ... check for 'cancel' action
"""

    def __init__(self, title, message, delay=0.1):
        """Initialize the progress bar with 0%, a {title} and a {message}.
Message must contain {0} which is replaced by the percentage value
"""
        super().__init__()
        self.status = None

        # create temporary file for progress
        self.tmpfile = tempfile.NamedTemporaryFile(mode='w')
        self.tmpfile.write(str(0))
        self.tmpfile.flush()

        filename = self.tmpfile.name
        message = message.format('$VAL')

        # create progress bar: fetch progress from tmpfile, update progressbar,
        # loop until 100%
        self.cmd = f'''
VAL=0
(
    while [ $VAL -lt 100 ] ; do
        VAL2=`cat {filename}`
        if [ $VAL -ne $VAL2 ]; then
            VAL=$VAL2
            echo "#{message}"
            echo $VAL
        fi
        sleep {delay}
    done) |
zenity --progress --title="{title}" --text="Bitte warten" --auto-close --width=500
'''

        self.start()

    def run(self):
        """Run zenity progressbar via subprocess."""
        p = subprocess.run(
            self.cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.status = p.returncode == 0

    def __call__(self, value):
        """Modify the progress state with [0.0, 1.0]."""
        value = int(value * 100)
        self.tmpfile.seek(0)
        self.tmpfile.write(str(value))
        self.tmpfile.flush()

    def finish(self, auto_raise=True):
        """Force progressbar to finish. Raise KeyboardInterrupt if
{auto_raise} is True.
"""
        self.__call__(1.0)
        self.join()
        if self.status:
            logging.debug('ProgressBar finished')
        else:
            logging.debug('ProgressBar canceled')
            if auto_raise:
                raise KeyboardInterrupt


# ---------------------------------------------------------------------


def ask(title, question):
    """Show a question via zenity using the {title} and {qestion} text.
Returns whether yes (True) or no (False) were clicked.

answer = ask("Wait a moment", "Do really want this to happen?")
"""
    cmd = f'zenity --question --title="{title}" --text="{question}" --width=500'
    p = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return p.returncode == 0


def confirm(title, statement):
    """Show confirm dialog. On cancel, a KeyboardInterrupt is raised as if
The user canceled the programm with CTRL+Z.
"""
    if not ask(title, statement):
        raise KeyboardInterrupt()


def choose(title, filename, save=True, overwrite=True, filter=[]):
    """Show a file choose dialog.
"""
    cmd = f'zenity --file-selection --title="{title}" --filename="{filename}" '
    if save:
        cmd += '--save '
        if overwrite:
            cmd += '--confirm-overwrite '
    for f in filter:
        cmd += f'--file-filter="{f}"'

    p = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    filename = p.communicate()[0].decode().split('\n')[0]
    if filename == '':
        return None
    return filename


def notify(category, messege):
    """Trigger a notification. Categories are 'error', 'info', 'question'
and 'warning'
"""
    subprocess.run(f'zenity --notification --window-icon="{category}" --text="{messege}"', shell=True)
