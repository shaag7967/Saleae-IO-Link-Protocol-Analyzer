from saleae.analyzers import AnalyzerFrame
from saleae.data.timing import SaleaeTime

from iolink_utils.messageInterpreter.page.transactionPage import TransactionPage
from iolink_utils.messageInterpreter.process.transactionProcess import TransactionProcess
from iolink_utils.messageInterpreter.diagnosis.transactionDiagnosis import TransactionDiagEventMemory, TransactionDiagEventReset
from iolink_utils.messageInterpreter.isdu.ISDU import ISDU


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
    def handleISDU(self, transaction: ISDU):
        return [AnalyzerFrame(
            transaction.name(),
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            transaction.data()
        )]


class ProcessHandler(TransactionHandler):
    def handleProcess(self, transaction: TransactionProcess):
        return [AnalyzerFrame(
            'Process',
            SaleaeTime(transaction.startTime),
            SaleaeTime(transaction.endTime),
            transaction.data()
        )]
