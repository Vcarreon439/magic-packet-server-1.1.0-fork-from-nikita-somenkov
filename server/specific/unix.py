"""unix.py: UNIX server specific implementation"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import server.specific.shared


class UNIXServerRunner(server.specific.shared.ServerRunner):
    def get_specific_logger_options(self) -> dict:
        return dict()
