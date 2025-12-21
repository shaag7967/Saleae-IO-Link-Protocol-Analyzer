from saleae.analyzers import AnalyzerFrame
from saleae.data.timing import SaleaeTime

from iolink_utils.messageInterpreter.page.transactionPage import TransactionPage
from iolink_utils.messageInterpreter.diagnosis.transactionDiagnosis import TransactionDiagEventMemory, TransactionDiagEventReset
from iolink_utils.messageInterpreter.isdu.ISDU import ISDU


class TransactionHandler:
    def handlePage(self, msg: TransactionPage):
        return []

    def handleDiagEventMemory(self, msg: TransactionDiagEventMemory):
        return []

    def handleDiagEventReset(self, msg: TransactionDiagEventReset):
        return []

    def handleISDU(self, msg: ISDU):
        return []


class PageDiagnosisHandler(TransactionHandler):
    def handlePage(self, msg: TransactionPage):
        return [AnalyzerFrame(
            'page',
            SaleaeTime(msg.start_time),
            SaleaeTime(msg.end_time),
            msg.data()
        )]

    def handleDiagEventMemory(self, msg: TransactionDiagEventMemory):
        return [AnalyzerFrame(
            'diagREAD',
            SaleaeTime(msg.start_time),
            SaleaeTime(msg.end_time),
            msg.data()
        )]

    def handleDiagEventReset(self, msg: TransactionDiagEventReset):
        return [AnalyzerFrame(
            'diagFINISH',
            SaleaeTime(msg.start_time),
            SaleaeTime(msg.end_time),
            msg.data()
        )]


class ISDUHandler(TransactionHandler):
    def handleISDU(self, msg: ISDU):
        return [AnalyzerFrame(
            msg.name(),
            SaleaeTime(msg.start_time),
            SaleaeTime(msg.end_time),
            msg.data()
        )]
