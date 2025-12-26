"""communication.py: Communication channel API"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import abc
import lib.messages


class Communication(abc.ABC):
    start = "-->"
    end = "<--"

    @abc.abstractmethod
    def is_ready(self) -> bool:
        pass

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def read(self) -> lib.messages.BaseMessage:
        pass

    @abc.abstractmethod
    def write(self, message: lib.messages.BaseMessage) -> None:
        pass
