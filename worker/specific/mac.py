"""mac.py: Linux worker specific implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import os
import time

import lib.messages
import worker.specific.unix


class MacWorkerRunner(worker.specific.unix.UNIXWorkerRunner):
    def system_shutdown(self, message: lib.messages.ShutdownMessage):
        os.system(f"shutdown -h +{message.timeout}")

    def system_reboot(self, message: lib.messages.RebootMessage):
        os.system(f"shutdown -r +{message.timeout}")

    def system_sleep(self, message: lib.messages.SleepMessage):
        time.sleep(message.timeout)
        os.system("pmset sleepnow")
