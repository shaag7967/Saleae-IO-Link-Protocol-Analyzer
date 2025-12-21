from abc import ABC, abstractmethod


class Transaction(ABC):
    @abstractmethod
    def dispatch(self, handler):  # pragma: no cover
        pass
