"""factory.py: Factory for choose server implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import platform

import lib.runner


def get_server_runner() -> lib.runner.Runner:
    current_platform = platform.system()
    if current_platform == "Windows":
        import server.specific.windows
        return server.specific.windows.WindowsServerRunner()
    elif current_platform == "Darwin" or current_platform == "Linux":
        import server.specific.unix
        return server.specific.unix.UNIXServerRunner()
