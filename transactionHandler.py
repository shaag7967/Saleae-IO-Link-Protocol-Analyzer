from saleae.analyzers import AnalyzerFrame
from saleae.data.timing import SaleaeTime

from iolink_utils.messageInterpreter.page.transactionPage import TransactionPage
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


class DiagnosisHandler(TransactionHandler):
    def handleDiagEventMemory(self, transaction: TransactionDiagEventMemory):
        return [AnalyzerFrame(
            'diagREAD',
            SaleaeTime(transaction.start_time),
            SaleaeTime(transaction.end_time),
            transaction.data()
        )]

    def handleDiagEventReset(self, transaction: TransactionDiagEventReset):
        return [AnalyzerFrame(
            'diagFINISH',
            SaleaeTime(transaction.start_time),
            SaleaeTime(transaction.end_time),
            transaction.data()
        )]


class PageHandler(TransactionHandler):
    def handlePage(self, transaction: TransactionPage):
        return [AnalyzerFrame(
            'page',
            SaleaeTime(transaction.start_time),
            SaleaeTime(transaction.end_time),
            transaction.data()
        )]


class ISDUHandler(TransactionHandler):
    def handleISDU(self, transaction: ISDU):
        return [AnalyzerFrame(
            transaction.name(),
            SaleaeTime(transaction.start_time),
            SaleaeTime(transaction.end_time),
            transaction.data()
        )]
