"""runner.py: Run service API"""

__author__ = "Armine Balian"
__email__ = "balian.armine@gmail.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import abc


class Runner(abc.ABC):
    @abc.abstractmethod
    def handle_args(self):
        pass

    @abc.abstractmethod
    def setup(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass
