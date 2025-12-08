class IOLinkUtilsException(Exception):
    """Basic exception for errors raised by iolink_utils"""


class InvalidProcessDataSize(IOLinkUtilsException):
    """Raised if size of ProcessData is not as expected"""


class InvalidProcessDataDefinition(IOLinkUtilsException):
    """Raised if data format of ProcessData is not as expected/invalid"""


class InvalidMSeqCodePDSizeCombination(IOLinkUtilsException):
    """Raised if no on-request data size could be found for the provided combination of MSeqCode and ProcessData octet count"""


class InvalidMSeqCode(IOLinkUtilsException):
    """Raised if m-sequence code cannot be handled/is unknown"""


class InvalidCycleTime(IOLinkUtilsException):
    """Raised if cycle time cannot be converted to CycleTime octet"""


class InvalidOctetValue(IOLinkUtilsException):
    """Raised if an octet can not be initialized with the provided value"""


class InvalidOctetCount(IOLinkUtilsException):
    """Raised if the number of octets is invalid"""


class InvalidBitRate(IOLinkUtilsException):
    """Raised if bitrate is invalid / unsupported"""
