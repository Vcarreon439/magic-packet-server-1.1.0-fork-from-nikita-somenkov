"""factory.py: Build connectivity object based on platform"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import typing
import platform

import lib.connectivity
import lib.communication


def get_communication(server_or_client: bool) -> typing.Optional[lib.communication.Communication]:
    current_platform = platform.system()
    if current_platform == "Windows":
        import lib.specific.win
        return lib.specific.win.WindowsCommunication.server() if server_or_client else \
            lib.specific.win.WindowsCommunication.client()
    elif current_platform == "Darwin" or current_platform == "Linux":
        import lib.specific.unix
        return lib.specific.unix.UNIXCommunication.server() if server_or_client else \
            lib.specific.unix.UNIXCommunication.client()


def get_connectivity(server_or_client: bool) -> lib.connectivity.Connectivity:
    import lib.simple_connectivity
    communicator = get_communication(server_or_client)
    return lib.simple_connectivity.SimpleConnectivity(communicator)
