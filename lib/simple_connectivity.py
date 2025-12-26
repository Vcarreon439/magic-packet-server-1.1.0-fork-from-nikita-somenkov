"""simple_connectivity.py: Simple connectivity based on communication"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import typing

import lib.connectivity
import lib.communication
import lib.messages


class SimpleConnectivity(lib.connectivity.Connectivity):
    def __init__(self, communicator: lib.communication.Communication):
        self.communicator = communicator
        pass

    def shutdown(self, timeout: int) -> None:
        message = lib.messages.ShutdownMessage(timeout=timeout)
        self.communicator.write(message)

    def reboot(self, timeout: int) -> None:
        message = lib.messages.RebootMessage(timeout=timeout)
        self.communicator.write(message)

    def sleep(self, timeout: int) -> None:
        message = lib.messages.SleepMessage(timeout=timeout)
        self.communicator.write(message)
