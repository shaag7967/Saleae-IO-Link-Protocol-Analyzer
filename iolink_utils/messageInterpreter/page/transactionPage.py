from typing import List, Dict
from datetime import datetime as dt

from iolink_utils.messageInterpreter.transaction import Transaction


class TransactionPage(Transaction):
    def __init__(self, name: str, value: str):
        self.start_time: dt = dt(1970, 1, 1)
        self.end_time: dt = dt(1970, 1, 1)

        self.name: str = name
        self.value: str = value

    def data(self) -> Dict:
        return {
            'page': ' '.join(filter(None, [self.name, self.value]))
        }

    def dispatch(self, handler):
        return handler.handlePage(self)

    def __str__(self):
        return f"Page: {' '.join(filter(None, [self.name, self.value]))}"
