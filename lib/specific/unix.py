"""unix.py: UNIX specifics"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import os
import io
import time
import typing
import logging

import lib.messages
import lib.communication

logger = logging.getLogger("communication")


class UNIXCommunication(lib.communication.Communication):
    pipe_name = '/var/run/mpworker.pipe'

    def __init__(self, mode: str):
        self.communication_mode = mode
        if mode == "server":
            self.mode = "r"
            UNIXCommunication.prepare_for_communication()
        elif mode == "client":
            self.mode = "w"

        self.file = None  # type: typing.Optional[io.StringIO]

    def __del__(self):
        self.disconnect()

    @staticmethod
    def server() -> 'UNIXCommunication':
        logger.info("prepare UNIXCommunication as server")
        comm = UNIXCommunication("server")
        comm.connect()
        return comm

    @staticmethod
    def client() -> 'UNIXCommunication':
        logger.info("prepare UNIXCommunication as client")
        comm = UNIXCommunication("client")
        comm.connect()
        return comm

    def connect(self):
        self._try_open()

    def disconnect(self):
        if self.file is None:
            return
        logger.info(f"unix pipe {UNIXCommunication.pipe_name} was closed")
        self.file.close()

        if self.communication_mode == "server":
            UNIXCommunication.done_for_communication()

    def _try_open(self):
        if self.file is not None:
            return
        if os.path.exists(UNIXCommunication.pipe_name):
            self.file = open(UNIXCommunication.pipe_name, self.mode)
            logger.info(f"unix pipe {UNIXCommunication.pipe_name} was opened")

    def write(self, message: lib.messages.BaseMessage):
        self._try_open()
        if self.file is None:
            return
        message_data = [
            UNIXCommunication.start,
            type(message).__name__,
            message.to_json(),
            UNIXCommunication.end,
        ]
        self.file.write('\n'.join(message_data))
        self.file.write('\n')
        self.file.flush()

    def is_ready(self):
        return self.file is not None

    def read(self) -> lib.messages.BaseMessage:
        """
        We expect follow message:

        -->
        ShutdownMessage
        { "timeout": 0 }
        <--
        """
        self._try_open()
        while True:
            line = self.file.readline()
            if line.strip() != UNIXCommunication.start:
                # readline() is nonblocking operation :(
                time.sleep(1.0)
                continue

            messages_data = self._continue_read()
            message = UNIXCommunication._parsed(messages_data)
            if message is None:
                continue

            print("New message was received {klass}({request})".format(
                klass=type(message).__name__, request=message.to_json()))

            return message

    def _continue_read(self) -> list:
        messages_data = list()
        while True:
            line = self.file.readline()
            if line.strip() == UNIXCommunication.end:
                return messages_data
            messages_data.append(line)

    @staticmethod
    def _parsed(message_data: list) -> typing.Optional[lib.messages.BaseMessage]:
        """
        We expect follow message:

        ShutdownMessage
        { "timeout": 0 }
        """
        if len(message_data) < 2:
            return

        class_name, *payload = message_data
        class_type = getattr(lib.messages, class_name.strip(), None)

        if class_type is None:
            return

        return class_type.from_json(''.join(payload))

    @classmethod
    def prepare_for_communication(cls):
        logger.info(f"prepare for communication named pipe {UNIXCommunication.pipe_name}")
        if not os.path.exists(UNIXCommunication.pipe_name):
            original_mask = os.umask(0o000)
            os.mkfifo(UNIXCommunication.pipe_name, 0o622)
            os.umask(original_mask)
            logger.info(f"pipe {UNIXCommunication.pipe_name} was created")

    @classmethod
    def done_for_communication(cls):
        logger.info(f"done for communication {UNIXCommunication.pipe_name}")
        if os.path.exists(UNIXCommunication.pipe_name):
            os.unlink(UNIXCommunication.pipe_name)
            logger.info(f"pipe {UNIXCommunication.pipe_name} was deleted")
