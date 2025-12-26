"""fake_connectivity.py: Fake implementation for Connectivity"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import lib.connectivity


class FakeConnectivity(lib.connectivity.Connectivity):
    def shutdown(self, timeout: int) -> None:
        print("Host was shutdown")

    def reboot(self, timeout: int) -> None:
        print("Host was reboot")

    def sleep(self, timeout: int) -> None:
        print("Host was sleep")
