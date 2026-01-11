"""mpworker.py: Magic Packet Worker entry point"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import worker.workerlib.factory


if __name__ == "__main__":
    runner = worker.workerlib.factory.get_worker_runner()
    runner.handle_args()
    runner.setup()
    runner.run()
