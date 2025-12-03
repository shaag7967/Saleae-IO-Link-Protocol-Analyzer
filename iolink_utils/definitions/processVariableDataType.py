from enum import IntEnum


# IO-Link Common Profile
# See Table B.5 – Coding of PVinD or PVoutD
class ProcessVariableDataType(IntEnum):
    OctetStringT = 0
    SetOfBoolT = 1
    UIntegerT = 2
    IntegerT = 3
    Float32T = 4
    StringT = 5
    TimeT = 6
    TimeSpanT = 7
