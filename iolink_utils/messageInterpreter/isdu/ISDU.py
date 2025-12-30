from datetime import datetime as dt
from abc import abstractmethod

from iolink_utils.octetDecoder.octetDecoder import IService
from iolink_utils.messageInterpreter.transaction import Transaction


class ISDU(Transaction):
    def __init__(self):
        super().__init__()

        self._service: IService = IService()
        self._rawData: bytearray = bytearray()
        self._chkpdu: int = 0
        self._isValid: bool = False
        self._isComplete: bool = False

    @property
    def isValid(self) -> bool:
        return self._isValid

    @property
    def isComplete(self) -> bool:
        return self._isComplete

    def setEndTime(self, endTime: dt):
        self.endTime = endTime

    def _hasExtendedLength(self):
        return self._service.length == 1

    def _getTotalLength(self):
        return int(self._rawData[1]) if self._hasExtendedLength() else self._service.length

    def _calculateCheckByte(self) -> int:
        chk = 0
        for octet in self._rawData[:-1]:  # except chkpdu which is last byte
            chk ^= octet
        return chk

    def _updateInternalData(self):
        if len(self._rawData) > 0:
            self._service = IService(int(self._rawData[0]))

        targetLength = self._getTotalLength()
        if len(self._rawData) >= targetLength:
            self._rawData = self._rawData[:targetLength]
            self._chkpdu = self._rawData[-1]
            self._isValid = self._chkpdu == self._calculateCheckByte()
            self._isComplete = True
            self._onFinished()  # calls derived class to finish its data

    def replaceTrailingOctets(self, requestData: bytearray):
        lengthToReplace = len(requestData)
        if lengthToReplace > 0:
            self._rawData[-lengthToReplace:] = requestData
            self._updateInternalData()

    def appendOctets(self, requestData: bytearray):
        if len(requestData) > 0:
            self._rawData.extend(requestData)
            self._updateInternalData()

    def dispatch(self, handler):
        return handler.handleISDU(self)

    @abstractmethod
    def name(self) -> str:  # pragma: no cover
        return 'ISDU'

    @abstractmethod
    def _onFinished(self) -> None:  # pragma: no cover
        pass
