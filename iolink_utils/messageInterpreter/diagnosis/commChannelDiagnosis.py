from datetime import datetime as dt
from enum import IntEnum

from iolink_utils.octetStreamDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.definitions.transmissionDirection import TransmissionDirection
from iolink_utils.definitions.eventMemory import EventMemory

from .transactionDiagnosis import TransactionDiagEventMemory, TransactionDiagEventReset


class CommChannelDiagnosis:
    class State(IntEnum):
        Idle = 0,
        ReadEventMemory = 1,
        ResetEventFlag = 2

    def __init__(self):
        self.state: CommChannelDiagnosis.State = CommChannelDiagnosis.State.Idle

        self.startTime: dt = dt(1970, 1, 1)
        self.endTime: dt = dt(1970, 1, 1)

        self.eventMemory: EventMemory = EventMemory()
        self.eventMemoryIndex: int = 0

    def reset(self) -> None:
        self.state = CommChannelDiagnosis.State.Idle

    def handleMasterMessage(self, message: MasterMessage):
        self.eventMemoryIndex = message.mc.address

        if self.state == CommChannelDiagnosis.State.Idle:
            direction = TransmissionDirection(message.mc.read)

            # read event memory
            if direction == TransmissionDirection.Read:
                self.eventMemory.clear()
                self.startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ReadEventMemory
            # reset event flag
            elif direction == TransmissionDirection.Write and self.eventMemoryIndex == 0:
                self.startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ResetEventFlag

    def handleDeviceMessage(self, message: DeviceMessage):
        if self.state == CommChannelDiagnosis.State.ReadEventMemory:
            self.endTime = message.end_time
            self.eventMemory.setMemory(self.eventMemoryIndex, message.od[0])

            if self.eventMemory.isComplete():
                self.state = CommChannelDiagnosis.State.Idle
                return TransactionDiagEventMemory(self.startTime, self.endTime, self.eventMemory)

        elif self.state == CommChannelDiagnosis.State.ResetEventFlag:
            self.endTime = message.end_time
            self.state = CommChannelDiagnosis.State.Idle
            return TransactionDiagEventReset(self.startTime, self.endTime)
