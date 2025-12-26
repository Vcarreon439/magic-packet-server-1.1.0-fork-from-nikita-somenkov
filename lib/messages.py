"""messages.py: Shared messages types for talking between Web server and Worker"""

__author__ = "Nikita Somenkov"
__email__ = "somenkov.nikita@icloud.com"
__copyright__ = "Copyright 2020, Nikita Somenkov"
__license__ = "GPL"

import json


class BaseMessage:
    def __init__(self, **kwargs):
        pass

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str: str) -> 'BaseMessage':
        json_dict = json.loads(json_str)
        return cls(**json_dict)


class ShutdownMessage(BaseMessage):
    def __init__(self, timeout=0):
        super().__init__()
        self.timeout = timeout


class RebootMessage(BaseMessage):
    def __init__(self, timeout=0):
        super().__init__()
        self.timeout = timeout


class SleepMessage(BaseMessage):
    def __init__(self, timeout=0):
        super().__init__()
        self.timeout = timeout
