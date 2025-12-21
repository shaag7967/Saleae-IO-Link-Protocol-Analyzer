from typing import Dict
from datetime import datetime as dt

from iolink_utils.octetDecoder.octetDecoder import (StatusCodeType1, StatusCodeType2, Event)
from iolink_utils.definitions.events import EventType, EventMode
from iolink_utils.messageInterpreter.transaction import Transaction


class TransactionDiagEventMemory(Transaction):
    def __init__(self, start_time: dt, end_time: dt, eventMemory: bytearray):
        self.start_time: dt = start_time
        self.end_time: dt = end_time

        self.eventMemory: bytearray = eventMemory

    def _getStatusCode(self):
        statusCode = StatusCodeType2.from_buffer_copy(self.eventMemory, 0)
        if statusCode.details == 0:  # legacy
            statusCode = StatusCodeType1.from_buffer_copy(self.eventMemory, 0)

        return str(statusCode)

    def _getEvents(self):
        events = []

        statusCode = StatusCodeType2.from_buffer_copy(self.eventMemory, 0)
        if statusCode.details == 1:
            event_offsets = [1 + 3 * i for i in range(6)]
            event_flags = [
                statusCode.evt1,
                statusCode.evt2,
                statusCode.evt3,
                statusCode.evt4,
                statusCode.evt5,
                statusCode.evt6,
            ]

            for idx, (flag, offset) in enumerate(zip(event_flags, event_offsets), start=1):
                if flag:
                    evt = Event.from_buffer_copy(self.eventMemory, offset)
                    events.append((idx, f"{EventType(evt.qualifier.type).name}{EventMode(evt.qualifier.mode).name}"
                                        f"({evt.code.code})"))

        return events

    def data(self) -> Dict:
        return {
            'evtStatus': self._getStatusCode(),
            **{f'evt{idx}': info for idx, info in self._getEvents()}
        }

    def dispatch(self, handler):
        return handler.handleDiagEventMemory(self)

    def __str__(self):
        return f"Diag EventMem: '{self.data()}"


class TransactionDiagEventReset(Transaction):
    def __init__(self, start_time: dt, end_time: dt):
        self.start_time: dt = start_time
        self.end_time: dt = end_time

    def data(self) -> Dict:
        return {}

    def dispatch(self, handler):
        return handler.handleDiagEventReset(self)

    def __str__(self):
        return "Diag Reset"
