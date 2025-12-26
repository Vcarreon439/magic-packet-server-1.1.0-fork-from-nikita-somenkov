"""unix.py: UNIX worker specific implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import abc

import worker.specific.shared


class UNIXWorkerRunner(worker.specific.shared.WorkerRunner, abc.ABC):
    def get_specific_logger_options(self) -> dict:
        return dict()
