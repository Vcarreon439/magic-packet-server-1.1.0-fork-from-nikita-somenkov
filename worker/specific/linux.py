"""linux.py: Linux worker specific implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import os
import time

import lib.messages
import worker.specific.unix


class LinuxWorkerRunner(worker.specific.unix.UNIXWorkerRunner):
    def system_shutdown(self, message: lib.messages.ShutdownMessage):
        time.sleep(message.timeout)
        os.system(f"shutdown -h now")

    def system_reboot(self,  message: lib.messages.RebootMessage):
        time.sleep(message.timeout)
        os.system(f"shutdown -r now")

    def system_sleep(self,  message: lib.messages.SleepMessage):
        time.sleep(message.timeout)
        os.system("systemctl suspend")
