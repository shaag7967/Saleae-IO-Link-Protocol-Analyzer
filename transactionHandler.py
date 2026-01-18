import copy

from saleae.analyzers import AnalyzerFrame
from saleae.data.timing import SaleaeTime

from typing import Dict

from iolink_utils.messageInterpreter.page.transactionPage import TransactionPage
from iolink_utils.messageInterpreter.process.transactionProcess import TransactionProcess
from iolink_utils.messageInterpreter.diagnosis.transactionDiagnosis import (
    TransactionDiagEventMemory,
    TransactionDiagEventReset
)
from iolink_utils.messageInterpreter.isdu.ISDU import ISDU
from iolink_utils.iodd.iodd import Variable


class TransactionHandler:
    def handlePage(self, transaction: TransactionPage):
        return []

    def handleDiagEventMemory(self, transaction: TransactionDiagEventMemory):
        return []

    def handleDiagEventReset(self, transaction: TransactionDiagEventReset):
        return []

    def handleISDU(self, transaction: ISDU):
        return []

    def handleProcess(self, transaction: TransactionProcess):
        return []


class DiagnosisHandler(TransactionHandler):
    def handleDiagEventMemory(self, transaction: TransactionDiagEventMemory):
        return [AnalyzerFrame(
            'DiagRead',
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            transaction.data()
        )]

    def handleDiagEventReset(self, transaction: TransactionDiagEventReset):
        return [AnalyzerFrame(
            'DiagReset',
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            transaction.data()
        )]


class PageHandler(TransactionHandler):
    def handlePage(self, transaction: TransactionPage):
        return [AnalyzerFrame(
            'Page',
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            transaction.data()
        )]


class ISDUHandler(TransactionHandler):
    def __init__(self, stdVariableCollection: Dict[int, Variable], variableCollection: Dict[int, Variable]):
        self.standardVariableCollection: Dict[int, Variable] = stdVariableCollection
        self.variableCollection: Dict[int, Variable] = variableCollection

    def _getIndexInfo(self, index: int) -> str:
        indexInfo = f"{index}"
        variable = (self.variableCollection.get(index) or self.standardVariableCollection.get(index))
        return f"{indexInfo}: {variable.name}" if variable else indexInfo

    def handleISDU(self, transaction: ISDU):
        data = copy.deepcopy(transaction.data())
        if 'index' in data:
            idx = data['index']
            data['index'] = f"0x{idx:04X}"
            data['info'] = self._getIndexInfo(idx)
        if 'subIndex' in data:
            data['subIndex'] = f"0x{data['subIndex']:02X}"

        return [AnalyzerFrame(
            transaction.name(),
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            data
        )]


class ProcessHandler(TransactionHandler):
    def handleProcess(self, transaction: TransactionProcess):
        return [AnalyzerFrame(
            'Process',
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            transaction.data()
        )]
