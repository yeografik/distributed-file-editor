from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    INS: _ClassVar[Operation]
    DEL: _ClassVar[Operation]
INS: Operation
DEL: Operation

class Command(_message.Message):
    __slots__ = ["type", "position", "timeStamp", "userID"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    USERID_FIELD_NUMBER: _ClassVar[int]
    type: Operation
    position: int
    timeStamp: int
    userID: int
    def __init__(self, type: _Optional[_Union[Operation, str]] = ..., position: _Optional[int] = ..., timeStamp: _Optional[int] = ..., userID: _Optional[int] = ...) -> None: ...

class CommandStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: int
    def __init__(self, status: _Optional[int] = ...) -> None: ...
