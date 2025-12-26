"""factory.py: Factory for choose worker implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import platform

import lib.runner


def get_worker_runner() -> lib.runner.Runner:
    current_platform = platform.system()
    if current_platform == "Windows":
        import worker.specific.windows
        return worker.specific.windows.WindowsWorkerRunner()
    elif current_platform == "Darwin":
        import worker.specific.mac
        return worker.specific.mac.MacWorkerRunner()
    elif current_platform == "Linux":
        import worker.specific.linux
        return worker.specific.linux.LinuxWorkerRunner()
