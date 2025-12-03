from enum import IntEnum
from ._internal import AutoNameConvertMeta


class BitRate(IntEnum, metaclass=AutoNameConvertMeta):
    Undefined = 0
    COM1 = 4800
    COM2 = 38400
    COM3 = 230400
