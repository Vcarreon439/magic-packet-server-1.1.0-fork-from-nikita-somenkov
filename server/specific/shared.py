"""shared.py: Shared start point of Magic Packet Server Server"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import abc
import logging
import typing
import flask

import server.api.info
import server.api.control
import lib.runner
import lib.factory
import lib.messages
import lib.connectivity


class ServerRunner(lib.runner.Runner):
    def __init__(self):
        self.app: typing.Optional[flask.Flask] = None
        self.port = 5154
        self.logger = logging.getLogger(__name__)

    def handle_args(self):
        pass

    def setup(self):
        logger_options = self.get_specific_logger_options()
        logging.basicConfig(format='[%(asctime)-15s] %(threadName)s: %(message)s', **logger_options)
        logging.getLogger("communication").setLevel(logging.DEBUG)

        self.app = flask.Flask("mpserver")
        self.app.register_blueprint(server.api.control.control)
        self.app.register_blueprint(server.api.info.info)
        self.app.connectivity = lib.factory.get_connectivity(server_or_client=False)

    def run(self):
        self.app.run(host="0.0.0.0", port=self.port)

    @abc.abstractmethod
    def get_specific_logger_options(self) -> dict:
        pass
