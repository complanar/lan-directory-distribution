#!/usr/bin/python3

import subprocess
import tempfile


class ProgressBar(object):
    """Creates a zenity-based progress bar that can be altered.

pb = ProgressBar('Please Wait', 'Current progress is {0}%, please wait')
pb(0.5)
# later
pb(0.75)
"""

    def __init__(self, title, message, delay=0.1):
        """Initialize the progress bar with 0%, a {title} and a {message}.
Message must contain {0} which is replaced by the percentage value
"""
        # create temporary file for progress
        self.tmpfile = tempfile.NamedTemporaryFile(mode='w')
        self.tmpfile.write(str(0))
        self.tmpfile.flush()

        filename = self.tmpfile.name
        message = message.format('$VAL')

        # create progress bar: fetch progress from tmpfile, update progressbar,
        # loop until 100%
        cmd = f'VAL=0; (while [ $VAL -lt 100 ] ; do VAL2=`cat {filename}`; if [ $VAL -ne $VAL2 ]; then VAL=$VAL2; echo "#{message}"; echo $VAL; fi; sleep {delay}; done)| zenity --progress --title="{title}" --text="Bitte warten" --auto-close --width=500'
        self.process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

    def __call__(self, value):
        """Modify the progress state with [0.0, 1.0]."""
        value = int(value * 100)
        self.tmpfile.seek(0)
        self.tmpfile.write(str(value))
        self.tmpfile.flush()

    def getStatus(self):
        """Query status of the progress bar: True == finished, False == canceld, None == running."""
        p = self.process.poll()
        if p == 1:
            # abort
            return False
        elif p == 0:
            # finished
            return True
        else:
            # running
            return None

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


def choose(title, filename, save=True, overwrite=True, filter=[]):
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


def notify(category, title, message):
    """Trigger a notification.

notify('transfer.complete', 'Finished', 'Upload was finished successfully!')
"""
    subprocess.run(['notify-send', '-c', category, title, message])
