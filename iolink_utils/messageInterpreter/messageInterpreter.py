from typing import Union, List

from iolink_utils.octetStreamDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.definitions.communicationChannel import CommChannel
from iolink_utils.messageInterpreter.diagnosis.commChannelDiagnosis import CommChannelDiagnosis, TransactionDiagEventMemory, TransactionDiagEventReset
from iolink_utils.messageInterpreter.isdu.commChannelISDU import CommChannelISDU
from iolink_utils.messageInterpreter.isdu.ISDU import ISDU
from iolink_utils.messageInterpreter.page.commChannelPage import CommChannelPage, TransactionPage


class CommChannelProcess:
    def handleMasterMessage(self, message: MasterMessage):  # pragma: no cover
        return []

    def handleDeviceMessage(self, message: DeviceMessage):  # pragma: no cover
        return []


class MessageInterpreter:
    def __init__(self):
        self.channelHandler = {
            CommChannel.Process: CommChannelProcess(),
            CommChannel.Page: CommChannelPage(),
            CommChannel.Diagnosis: CommChannelDiagnosis(),
            CommChannel.ISDU: CommChannelISDU()
        }
        self.activeChannel: CommChannel = CommChannel.Process

    def processMessage(self, message: Union[MasterMessage, DeviceMessage]) -> List[
            Union[TransactionPage, TransactionDiagEventMemory, TransactionDiagEventReset, ISDU]]:

        channel = message.channel()
        if channel is not None:
            self.activeChannel = channel
        return message.dispatch(self.channelHandler[self.activeChannel])
