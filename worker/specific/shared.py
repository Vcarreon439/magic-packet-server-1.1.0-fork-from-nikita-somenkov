"""shared.py: Shared start point of Magic Packet Server Worker"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import sys
import abc
import time
import typing
import logging

import lib.runner
import lib.factory
import lib.messages
import lib.communication


class WorkerRunner(lib.runner.Runner):
    def __init__(self):
        self.communication_object: typing.Optional[lib.communication.Communication] = None
        self.logger = logging.getLogger(__name__)
        self.is_stop = False

    def handle_args(self):
        pass

    def setup(self):
        logger_options = self.get_specific_logger_options()
        logging.basicConfig(format='[%(asctime)-15s] %(threadName)s: %(message)s', **logger_options)
        logging.getLogger("communication").setLevel(logging.DEBUG)

        self.communication_object = lib.factory.get_communication(server_or_client=True)

    def run(self):
        while not self.is_stop:
            if not self.communication_object.is_ready():
                self.communication_object.connect()
                time.sleep(1.0)
                continue
            message = self.communication_object.read()
            if message:
                self.process_message(message)
            else:
                time.sleep(1.0)

        time.sleep(1.0)
        self.logger.info("worker was shutdown")

    def stop(self):
        self.is_stop = True
        self.communication_object.disconnect()

    def process_message(self, message):
        if isinstance(message, lib.messages.ShutdownMessage):
            self.system_shutdown(message)
        elif isinstance(message, lib.messages.RebootMessage):
            self.system_reboot(message)
        elif isinstance(message, lib.messages.SleepMessage):
            self.system_sleep(message)

    @abc.abstractmethod
    def get_specific_logger_options(self) -> dict:
        pass

    @abc.abstractmethod
    def system_shutdown(self, message: lib.messages.ShutdownMessage):
        pass

    @abc.abstractmethod
    def system_reboot(self, message: lib.messages.RebootMessage):
        pass

    @abc.abstractmethod
    def system_sleep(self, message: lib.messages.SleepMessage):
        pass
