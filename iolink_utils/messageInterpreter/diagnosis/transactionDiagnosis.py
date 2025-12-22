import copy
from typing import Dict
from datetime import datetime as dt

from iolink_utils.octetDecoder.octetDecoder import (StatusCodeType1, StatusCodeType2)
from iolink_utils.definitions.eventInfo import EventType, EventMode
from iolink_utils.definitions.eventMemory import EventMemory
from iolink_utils.messageInterpreter.transaction import Transaction


class TransactionDiagEventMemory(Transaction):
    def __init__(self, start_time: dt, end_time: dt, eventMemory: EventMemory):
        self.start_time: dt = start_time
        self.end_time: dt = end_time
        self.eventMemory: EventMemory = copy.deepcopy(eventMemory)

    def _getEvents(self):
        event_flags = [
            self.eventMemory.statusCode.evt1,
            self.eventMemory.statusCode.evt2,
            self.eventMemory.statusCode.evt3,
            self.eventMemory.statusCode.evt4,
            self.eventMemory.statusCode.evt5,
            self.eventMemory.statusCode.evt6,
        ]

        events = []
        for idx, (flag, event) in enumerate(zip(event_flags, self.eventMemory.events), start=1):
            if flag:
                events.append((idx, f"{EventType(event.qualifier.type).name}{EventMode(event.qualifier.mode).name}"
                                    f"({event.code})"))
        return events

    def data(self) -> Dict:
        return {
            'evtStatus': str(self.eventMemory.statusCode),
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
