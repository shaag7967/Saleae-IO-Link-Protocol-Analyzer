from datetime import datetime as dt
from enum import IntEnum

from iolink_utils.octetStreamDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.definitions.transmissionDirection import TransmissionDirection

from .transactionDiagnosis import TransactionDiagEventMemory, TransactionDiagEventReset


class CommChannelDiagnosis:
    class State(IntEnum):
        Idle = 0,
        ReadEventMemory = 1,
        ResetEventFlag = 2

    def __init__(self):
        self.state: CommChannelDiagnosis.State = CommChannelDiagnosis.State.Idle

        self.read_startTime: dt = dt(1970, 1, 1)
        self.read_endTime: dt = dt(1970, 1, 1)

        self.reset_startTime: dt = dt(1970, 1, 1)
        self.reset_endTime: dt = dt(1970, 1, 1)

        self.direction: TransmissionDirection = TransmissionDirection.Read
        self.eventMemory: bytearray = bytearray()
        self.eventMemoryIndex: int = 0

    def handleMasterMessage(self, message: MasterMessage):
        self.direction = TransmissionDirection(message.mc.read)
        self.eventMemoryIndex = message.mc.address

        if self.state == CommChannelDiagnosis.State.Idle:
            self.eventMemory = bytearray()

            if self.direction == TransmissionDirection.Write and self.eventMemoryIndex == 0:
                self.reset_startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ResetEventFlag
            elif self.direction == TransmissionDirection.Read:
                self.read_startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ReadEventMemory

        elif self.state == CommChannelDiagnosis.State.ReadEventMemory:
            if self.direction == TransmissionDirection.Write and self.eventMemoryIndex == 0:
                self.reset_startTime = message.start_time
                self.state = CommChannelDiagnosis.State.ResetEventFlag

        return []

    def handleDeviceMessage(self, message: DeviceMessage):
        transactions = []

        if self.state == CommChannelDiagnosis.State.ReadEventMemory:
            self.read_endTime = message.end_time
            if self.eventMemoryIndex == len(self.eventMemory):
                self.eventMemory.append(message.od[0])
            else:  # something is wrong TODO reset received data / error handling
                self.state = CommChannelDiagnosis.State.Idle
        elif self.state == CommChannelDiagnosis.State.ResetEventFlag:
            self.reset_endTime = message.end_time
            transactions.append(TransactionDiagEventMemory(self.read_startTime, self.read_endTime, self.eventMemory))
            transactions.append(TransactionDiagEventReset(self.reset_startTime, self.reset_endTime))
            self.state = CommChannelDiagnosis.State.Idle

        return transactions
