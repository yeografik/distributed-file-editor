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
    __slots__ = ["type", "position", "time_stamp", "user_id", "transmitter"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSMITTER_FIELD_NUMBER: _ClassVar[int]
    type: Operation
    position: int
    time_stamp: int
    user_id: int
    transmitter: Transmitter
    def __init__(self, type: _Optional[_Union[Operation, str]] = ..., position: _Optional[int] = ..., time_stamp: _Optional[int] = ..., user_id: _Optional[int] = ..., transmitter: _Optional[_Union[Transmitter, str]] = ...) -> None: ...

class CommandStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: int
    def __init__(self, status: _Optional[int] = ...) -> None: ...
