from iolink_utils.exceptions import InvalidISDUService
from iolink_utils.octetDecoder.octetDecoder import IService
from iolink_utils.definitions.iServiceNibble import IServiceNibble
from iolink_utils.messageInterpreter.isdu.ISDU import ISDU


#
# WRITE
#

class ISDURequest_Write8bitIdx(ISDU):
    def __init__(self):
        super().__init__()
        self.index: int = 0

    def _onFinished(self):
        pos = 2 if self._hasExtendedLength() else 1
        self.index = int(self._rawData[pos])

    def name(self) -> str:
        return 'Write8bitIdx'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': str(self.index),
            'data': self._rawData[3:-1] if self._hasExtendedLength() else self._rawData[2:-1]
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Write8bitIdx(index={self.index} data={self._rawData.hex()})"


class ISDURequest_Write8bitIdxSub(ISDU):
    def __init__(self):
        super().__init__()
        self.index: int = 0
        self.subIndex: int = 0

    def _onFinished(self):
        pos = 2 if self._hasExtendedLength() else 1
        self.index = int(self._rawData[pos])
        self.subIndex = int(self._rawData[pos + 1])

    def name(self) -> str:
        return 'Write8bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': str(self.index),
            'subIndex': str(self.subIndex),
            'data': self._rawData[4:-1] if self._hasExtendedLength() else self._rawData[3:-1]
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Write8bitIdxSub(index={self.index} subIndex={self.subIndex} data={self._rawData.hex()})"


class ISDURequest_Write16bitIdxSub(ISDU):
    def __init__(self):
        super().__init__()
        self.index: int = 0
        self.subIndex: int = 0

    def _onFinished(self):
        pos = 2 if self._hasExtendedLength() else 1
        self.index = int.from_bytes(self._rawData[pos:pos + 2], byteorder='big')
        self.subIndex = int(self._rawData[pos + 2])

    def name(self) -> str:
        return 'Write16bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': str(self.index),
            'subIndex': str(self.subIndex),
            'data': self._rawData[5:-1] if self._hasExtendedLength() else self._rawData[4:-1]
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Write16bitIdxSub(index={self.index} subIndex={self.subIndex} data={self._rawData.hex()})"


#
# READ
#

class ISDURequest_Read8bitIdx(ISDU):
    def __init__(self):
        super().__init__()
        self.index: int = 0

    def _onFinished(self):
        self.index = int(self._rawData[1])

    def name(self) -> str:
        return 'Read8bitIdx'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': str(self.index)
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Read8bitIdx(index={self.index} data={self._rawData.hex()})"


class ISDURequest_Read8bitIdxSub(ISDU):
    def __init__(self):
        super().__init__()
        self.index: int = 0
        self.subIndex: int = 0

    def _onFinished(self):
        self.index = int(self._rawData[1])
        self.subIndex = int(self._rawData[2])

    def name(self) -> str:
        return 'Read8bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': str(self.index),
            'subIndex': str(self.subIndex)
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Read8bitIdxSub(index={self.index} subIndex={self.subIndex} data={self._rawData.hex()})"


class ISDURequest_Read16bitIdxSub(ISDU):
    def __init__(self):
        super().__init__()
        self.index: int = 0
        self.subIndex: int = 0

    def _onFinished(self):
        self.index = int.from_bytes(self._rawData[1:2], byteorder='big')
        self.subIndex = int(self._rawData[3])

    def name(self) -> str:
        return 'Read16bitIdxSub'

    def data(self) -> dict:
        return {
            'valid': self.isValid,
            'index': str(self.index),
            'subIndex': str(self.subIndex)
        }

    def __str__(self):  # pragma: no cover
        return f"ISDURequest_Read16bitIdxSub(index={self.index} subIndex={self.subIndex} data={self._rawData.hex()})"


def createISDURequest(iService: IService):
    _req_map = {
        IServiceNibble.M_WriteReq_8bitIdx: ISDURequest_Write8bitIdx,
        IServiceNibble.M_WriteReq_8bitIdxSub: ISDURequest_Write8bitIdxSub,
        IServiceNibble.M_WriteReq_16bitIdxSub: ISDURequest_Write16bitIdxSub,
        IServiceNibble.M_ReadReq_8bitIdx: ISDURequest_Read8bitIdx,
        IServiceNibble.M_ReadReq_8bitIdxSub: ISDURequest_Read8bitIdxSub,
        IServiceNibble.M_ReadReq_16bitIdxSub: ISDURequest_Read16bitIdxSub,
    }

    if iService.service not in _req_map:
        raise InvalidISDUService(f"Invalid request nibble: {iService}")

    return _req_map[iService.service]()
