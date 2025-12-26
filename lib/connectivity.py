"""connectivity.py: Controlling Magic Packet Worker API"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import abc


class Connectivity(abc.ABC):
    @abc.abstractmethod
    def shutdown(self, timeout: int) -> None:
        pass

    @abc.abstractmethod
    def reboot(self, timeout: int) -> None:
        pass

    @abc.abstractmethod
    def sleep(self, timeout: int) -> None:
        pass
