"""win.py: Windows specifics"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import time
import typing
import logging
import threading

import win32pipe
import win32file
import pywintypes

import lib.messages
import lib.communication

logger = logging.getLogger("communication")


def _unblock_connect_to_pipe_on_server_side():
    """
    We just try to connect to named pipe just for unblock server side. Have you better solution?
    Used as fast hack. I cannot understand Win API at all.
    """
    try:
        win32file.CreateFile(
            WindowsCommunication.pipe_name,
            win32file.GENERIC_WRITE, 0, None,
            win32file.OPEN_EXISTING, 0, None)
    finally:
        return


class WindowsCommunication(lib.communication.Communication):
    pipe_name = r'\\.\pipe\mpserver'

    def __init__(self, mode: str):
        logger.info(f"we will use {WindowsCommunication.pipe_name} as named pipe")

        self.pipe = None  # type: typing.Optional[int]
        self.mode = mode  # type: str
        if mode == "server":
            self._init_as_server()
        elif mode == "client":
            self._init_as_client()
        else:
            raise Exception(f"unsupported mode: {mode}")

    def __del__(self):
        logger.debug("WindowsCommunication deleting")
        self.disconnect()

    @staticmethod
    def server() -> 'WindowsCommunication':
        comm = WindowsCommunication("server")
        comm.connect()
        return comm

    @staticmethod
    def client() -> 'WindowsCommunication':
        comm = WindowsCommunication("client")
        comm.connect()
        return comm

    def connect(self) -> bool:
        logger.info("try to connect to pipe")

        if self.mode == "client" and self.is_ready():
            logger.debug("already connected")
            return False

        if self.mode == "server":
            return self._start_wait_clients()
        elif self.mode == "client":
            return self._try_connect_client()

    def disconnect(self):
        logger.info("try to disconnect from pipe")

        if not self.is_ready():
            logger.debug("already disconnected")
            return

        if self.mode == "server":
            self._try_disconnect_server()
        elif self.mode == "client":
            self._try_disconnect_client()

    def _init_as_server(self):
        self.clients = []
        self.messages = []
        self.lock = threading.Lock()
        self.is_stop = False

        pipe_open_mode = win32pipe.PIPE_ACCESS_INBOUND  # we want open pipe: client write to server only
        pipe_mode = \
            win32pipe.PIPE_TYPE_MESSAGE |\
            win32pipe.PIPE_READMODE_MESSAGE |\
            win32pipe.PIPE_WAIT                         # not binary data | readonly | enable blocking mode
        buffer_size = 65536                             # buffer size
        no_timeout = None                               # default timeout (50 sec)
        max_instances = 1                               # maximum number of instances that can be created for this pipe

        logger.info(f"creating pipe {WindowsCommunication.pipe_name}")
        try:
            self.pipe = win32pipe.CreateNamedPipe(
                WindowsCommunication.pipe_name,
                pipe_open_mode, pipe_mode, max_instances,
                buffer_size, buffer_size, buffer_size, no_timeout
            )
        except pywintypes.error as error:
            logger.fatal(f"Cannot create named pipe {WindowsCommunication.pipe_name}: {error}")
            raise error
        logger.info("pipe was created")

    # noinspection PyMethodMayBeStatic
    def _init_as_client(self):
        logger.info("initialize as client")
        pass

    def _start_wait_clients(self):
        self.waiter_thread = threading.Thread(target=self._new_client_processing, name="ClientWaiter")
        self.waiter_thread.start()
        return True

    def _new_client_processing(self):
        logger.info("start waiting new client")
        while not self.is_stop:
            new_client = ClientHandler.wait(self.pipe, self)
            if new_client is None:
                time.sleep(1.0)
                continue
            self.clients.append(new_client)
            processing_client = threading.Thread(target=new_client.handle, name="ClientHandler")
            processing_client.start()

    def _try_disconnect_server(self):
        logger.debug("disconnecting from named pipe")

        self.is_stop = True

        for client in self.clients:
            client.stop()

        self.clients.clear()

        _unblock_connect_to_pipe_on_server_side()

        try:
            win32file.CloseHandle(self.pipe)
            self.pipe = None
        except pywintypes.error as error:
            logger.error(f"cannot disconnect from named pipe: {error}")
            return
        logger.info("successful disconnected")

    def _try_connect_client(self) -> bool:
        desired_access = win32file.GENERIC_WRITE  # open for write only
        share_mode = 0  # can be shared
        security_attributes = None  # do not use security attributes
        creation_disposition = win32file.OPEN_EXISTING  # we want fail if pipe do not exist
        flags_and_attributes = 0  # file attributes
        template_file = None  # should be None after Win95

        logger.debug("open named pipe")
        try:
            self.pipe = win32file.CreateFile(
                WindowsCommunication.pipe_name, desired_access, share_mode, security_attributes,
                creation_disposition, flags_and_attributes, template_file
            )
        except pywintypes.error as error:
            logger.warning(f"cannot open named pipe {error}")
            return False

        logger.info("successful opened named pipe")
        return True

    def _try_disconnect_client(self):
        logger.debug("disconnecting from named pipe")
        try:
            win32file.CloseHandle(self.pipe)
            self.pipe = None
        except pywintypes.error as error:
            logger.error(f"cannot disconnect from named pipe: {error}")
            return
        logger.info("successful disconnected")

    def write(self, message: lib.messages.BaseMessage):
        if not self.is_ready():
            logger.warning("we want to write, but not connected to pipe, will try to connect")
            if not self.connect():
                return

        try:
            message_json = message.to_json()
            message_type = type(message).__name__
        except Exception as error:
            logger.error(f"cannot convert message to json: {error}")
            return

        logger.info(f"write message {message_json} with type {message_type}")

        message_data = [
            WindowsCommunication.start.encode(), '\n'.encode(),
            message_type.encode(), '\n'.encode(),
            message_json.encode(), '\n'.encode(),
            WindowsCommunication.end.encode(), '\n'.encode()
        ]

        try:
            win32file.WriteFile(self.pipe, b''.join(message_data))
            win32file.FlushFileBuffers(self.pipe)
        except pywintypes.error as error:
            logger.error(f"cannot write: {error}")
            return

        logger.debug("message send successfully")

    def read(self) -> lib.messages.BaseMessage:
        """
        In Windows version we just try to read every second from client list
        <--
        """
        while not self.is_stop:
            self.lock.acquire(blocking=True, timeout=60.0)

            if len(self.messages) == 0:
                self.lock.release()
                time.sleep(1.0)
                return

            message = self.messages[0]
            del self.messages[0]
            self.lock.release()

            return message

    def is_ready(self):
        return self.pipe is not None

    def new_message(self, message: lib.messages.BaseMessage):
        self.lock.acquire(blocking=True, timeout=60.0)
        self.messages.append(message)
        self.lock.release()

    def remove_handler(self, client):
        logger.debug("search client for remove")
        for i, c in enumerate(self.clients):
            if c is client:
                logger.debug(f"remove client {i}")
                del self.clients[i]


class ClientHandler:
    def __init__(self, pipe, notifier: WindowsCommunication):
        self.pipe = pipe
        self.notifier = notifier
        self.is_stop = False

    def handle(self):
        """
        We expect follow message:

        -->
        ShutdownMessage
        { "timeout": 0 }
        <--
        """
        while not self.is_stop:
            line = self._readline()

            if line is None:
                self.disconnect()
                return

            if line.strip() != WindowsCommunication.start:
                time.sleep(1.0)
                continue

            messages_data = self._continue_read()
            if messages_data is None:
                self.disconnect()
                return

            message = ClientHandler._parsed(messages_data)
            if message is None:
                continue

            logger.info(f"new message was received {type(message)}({message.to_json()})")
            self.notifier.new_message(message)

        self.disconnect()
        self.notifier.remove_handler(self)

    def stop(self):
        self.is_stop = True

    @staticmethod
    def wait(pipe, caller: WindowsCommunication) -> typing.Optional['ClientHandler']:
        logger.debug("waiting new client")
        try:
            win32pipe.ConnectNamedPipe(pipe, None)
        except pywintypes.error as error:
            logger.error(f"cannot connect to named pipe: {error}")
            return

        logger.info("new client connected to named pipe")
        return ClientHandler(pipe, caller)

    def disconnect(self):
        logger.debug("disconnect named pipe")
        try:
            win32pipe.DisconnectNamedPipe(self.pipe)
        except pywintypes.error as error:
            logger.error(f"cannot disconnect from named pipe: {error}")
            return

        logger.info("disconnect client connected to named pipe")

    def _read(self) -> typing.Optional[str]:
        try:
            data = b""
            status = -1
            while status != 0:
                status, current_data = win32file.ReadFile(self.pipe, 1024)
                data += current_data
            return data.decode()
        except pywintypes.error as error:
            logger.info(f"client was disconnected: {error}")
            return

    def _readline_generator(self):
        line = ""
        while True:
            # FIXME: improve algo
            current_string = self._read()
            if current_string is None:
                yield None
            for char in current_string:
                line += char
                if char != "\n":
                    continue
                logging.debug(f"got from client line {line.strip()}")
                yield line
                line = ""

    def _readline(self):
        if not hasattr(self, "_read_generator"):
            self._read_generator = self._readline_generator()
        return next(self._read_generator)

    def _continue_read(self) -> list:
        messages_data = list()
        while True:
            line = self._readline()
            if line.strip() == WindowsCommunication.end:
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
