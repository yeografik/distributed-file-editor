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
    __slots__ = ["operation", "position", "user_id", "transmitter", "char", "clock"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSMITTER_FIELD_NUMBER: _ClassVar[int]
    CHAR_FIELD_NUMBER: _ClassVar[int]
    CLOCK_FIELD_NUMBER: _ClassVar[int]
    operation: Operation
    position: int
    user_id: int
    transmitter: Transmitter
    char: str
    clock: int
    def __init__(self, operation: _Optional[_Union[Operation, str]] = ..., position: _Optional[int] = ..., user_id: _Optional[int] = ..., transmitter: _Optional[_Union[Transmitter, str]] = ..., char: _Optional[str] = ..., clock: _Optional[int] = ...) -> None: ...

class CommandStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: int
    def __init__(self, status: _Optional[int] = ...) -> None: ...

class NodeInfo(_message.Message):
    __slots__ = ["ip", "port"]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: str
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[str] = ...) -> None: ...

class NotifyResponse(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class FileInfo(_message.Message):
    __slots__ = ["file_name"]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    def __init__(self, file_name: _Optional[str] = ...) -> None: ...

class Content(_message.Message):
    __slots__ = ["content"]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: str
    def __init__(self, content: _Optional[str] = ...) -> None: ...
