
class IOLinkUtilsException(Exception):
    """Basic exception for errors raised by iolink_utils"""


class InvalidProcessDataDefinition(IOLinkUtilsException):
    """Raised if invalid ProcessData definition is detected"""

    def __init__(self, message, pd_def):
        super().__init__(message)
        self.pd_def = pd_def

class InvalidProcessDataSize(IOLinkUtilsException):
    """Raised if size of ProcessData is not as expected"""


class InvalidMSeqCodePDSizeCombination(IOLinkUtilsException):
    """Raised if no on-request data size could be found for the provided combination of MSeqCode and ProcessData octet count"""


class InvalidMSeqCode(IOLinkUtilsException):
    """Raised if m-sequence code cannot be handled/is unknown"""


class InvalidCycleTime(IOLinkUtilsException):
    """Raised if cycle time cannot be converted to CycleTime octet"""


class InvalidOctetValue(IOLinkUtilsException):
    """Raised if an octet can not be initialized with the provided value"""
