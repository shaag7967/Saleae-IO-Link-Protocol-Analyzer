from enum import IntEnum
from typing import Optional
from datetime import datetime as dt

from iolink_utils.octetStreamDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage
from iolink_utils.octetDecoder.octetDecoder import IService
from iolink_utils.definitions.transmissionDirection import TransmissionDirection
from iolink_utils.messageInterpreter.isdu.ISDU import IServiceNibble, FlowCtrl, ISDU
from iolink_utils.messageInterpreter.isdu.ISDUrequests import createISDURequest
from iolink_utils.messageInterpreter.isdu.ISDUresponses import createISDUResponse


class CommChannelISDU:
    class State(IntEnum):
        Idle = 0,
        Request = 1,
        RequestFinished = 2,
        WaitForResponse = 3,
        Response = 4,
        ResponseFinished = 5

    def __init__(self) -> None:
        self.state: CommChannelISDU.State = CommChannelISDU.State.Idle
        self.direction: TransmissionDirection = TransmissionDirection.Read
        self.flowCtrl: FlowCtrl = FlowCtrl()
        self.isduRequest: Optional[ISDU] = None
        self.isduResponse: Optional[ISDU] = None
        self.responseStartTime: Optional[dt] = None

    def reset(self) -> None:
        self.state = CommChannelISDU.State.Idle

    def handleMasterMessage(self, message: MasterMessage):
        self.direction = TransmissionDirection(message.mc.read)
        self.flowCtrl = FlowCtrl(message.mc.address)

        if self.state == CommChannelISDU.State.Idle:
            if self.flowCtrl.state == FlowCtrl.State.Start and self.direction == TransmissionDirection.Write:
                self.isduRequest = createISDURequest(IService(message.od[0]))

                self.isduRequest.setTime(message.start_time, message.end_time)
                self.isduRequest.appendOctets(self.flowCtrl, message.od)

                if self.isduRequest.isComplete:
                    self.state = CommChannelISDU.State.RequestFinished
                else:
                    self.state = CommChannelISDU.State.Request

        elif self.state == CommChannelISDU.State.Request:
            if self.flowCtrl.state == FlowCtrl.State.Count:
                self.isduRequest.setEndTime(message.end_time)
                self.isduRequest.appendOctets(self.flowCtrl, message.od)

                if self.isduRequest.isComplete:
                    self.state = CommChannelISDU.State.RequestFinished

            elif self.flowCtrl.state == FlowCtrl.State.Abort:
                self.state = CommChannelISDU.State.Idle

        elif self.state == CommChannelISDU.State.WaitForResponse:
            if self.flowCtrl.state == FlowCtrl.State.Start and self.direction == TransmissionDirection.Read:
                self.responseStartTime = message.start_time

    def handleDeviceMessage(self, message: DeviceMessage):
        if self.state == CommChannelISDU.State.RequestFinished:
            self.isduRequest.setEndTime(message.end_time)

            self.state = CommChannelISDU.State.WaitForResponse
            return self.isduRequest

        elif self.state == CommChannelISDU.State.WaitForResponse:
            if self.flowCtrl.state == FlowCtrl.State.Start:
                if len(message.od) > 0 and IService(message.od[0]).service != IServiceNibble.NoService:
                    self.isduResponse = createISDUResponse(IService(message.od[0]))

                    self.isduResponse.setTime(self.responseStartTime, message.end_time)
                    self.isduResponse.appendOctets(self.flowCtrl, message.od)

                    if self.isduResponse.isComplete:
                        self.state = CommChannelISDU.State.Idle
                        return self.isduResponse
                    else:
                        self.state = CommChannelISDU.State.Response

        elif self.state == CommChannelISDU.State.Response:
            if self.flowCtrl.state == FlowCtrl.State.Count:
                self.isduResponse.setEndTime(message.end_time)
                self.isduResponse.appendOctets(self.flowCtrl, message.od)

                if self.isduResponse.isComplete:
                    self.state = CommChannelISDU.State.Idle
                    return self.isduResponse

            elif self.flowCtrl.state == FlowCtrl.State.Abort:
                self.state = CommChannelISDU.State.Idle
