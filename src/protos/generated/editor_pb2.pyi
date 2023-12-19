from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    INS: _ClassVar[Operation]
    DEL: _ClassVar[Operation]

class Transmitter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    USER: _ClassVar[Transmitter]
    SERVER: _ClassVar[Transmitter]
INS: Operation
DEL: Operation
USER: Transmitter
SERVER: Transmitter

class Command(_message.Message):
    __slots__ = ["operation", "position", "id", "transmitter", "char", "clock"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TRANSMITTER_FIELD_NUMBER: _ClassVar[int]
    CHAR_FIELD_NUMBER: _ClassVar[int]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    operation: Operation
    position: int
    id: int
    transmitter: Transmitter
    char: str
    clock: int
    def __init__(self, operation: _Optional[_Union[Operation, str]] = ..., position: _Optional[int] = ..., id: _Optional[int] = ..., transmitter: _Optional[_Union[Transmitter, str]] = ..., char: _Optional[str] = ..., clock: _Optional[int] = ...) -> None: ...

class CommandStatus(_message.Message):
    __slots__ = ["status", "content"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    status: int
    content: str
    def __init__(self, status: _Optional[int] = ..., content: _Optional[str] = ...) -> None: ...

class NodeInfo(_message.Message):
    __slots__ = ["ip", "port"]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: str
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class NotifyResponse(_message.Message):
    __slots__ = ["status", "clock"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    status: bool
    clock: int
    def __init__(self, status: bool = ..., clock: _Optional[int] = ...) -> None: ...

class FileInfo(_message.Message):
    __slots__ = ["file_name", "ip", "port"]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    ip: str
    port: int
    def __init__(self, file_name: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class Content(_message.Message):
    __slots__ = ["content"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...

class SyncConfirmation(_message.Message):
    __slots__ = ["answer"]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    answer: bool
    def __init__(self, answer: bool = ...) -> None: ...
