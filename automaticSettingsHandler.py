from dataclasses import replace
from typing import Callable, Dict
from transactionHandler import TransactionHandler

from iolink_utils.definitions.transmissionDirection import TransmissionDirection
from iolink_utils.definitions.onRequestDataOctetCount import ODOctetCount
from iolink_utils.definitions.directParameterPage import DirectParameterPage1Index
from iolink_utils.utils.calculateProcessDataLength import calculateProcessDataLength
from iolink_utils.octetDecoder.octetDecoder import MSequenceCapability, ProcessDataIn, ProcessDataOut
from iolink_utils.octetStreamDecoder.octetStreamDecoderSettings import DecoderSettings
from iolink_utils.messageInterpreter.page.transactionPage import TransactionPage
from iolink_utils.exceptions import InvalidMSeqCode, InvalidMSeqCodePDSizeCombination

GetterType = Callable[[], DecoderSettings]
SetterType = Callable[[DecoderSettings], None]


class AutomaticSettingsHandler(TransactionHandler):
    def __init__(self, getter: GetterType, setter: SetterType):
        super().__init__()
        self._getSettings = getter
        self._setSettings = setter

        self._mSeqOperateCode: int = 0xFF  # invalid

    @staticmethod
    def _update_operateODSize(settings: DecoderSettings, mSeqOperateCode: int):
        try:
            odSizeInOperate = ODOctetCount.in_operate(mSeqOperateCode, settings.operate.pdIn, settings.operate.pdOut)[0]
        except InvalidMSeqCodePDSizeCombination:
            pass
        else:
            operate = replace(settings.operate, od=odSizeInOperate)
            settings = replace(settings, operate=operate)

        return settings

    def _update_mseq(self, settings: DecoderSettings, value: int) -> DecoderSettings:
        mSeq = MSequenceCapability(value)

        # preoperate
        try:
            odSizeInPreoperate = ODOctetCount.in_preoperate(mSeq.preoperateCode)[0]
            preoperate = replace(settings.preoperate, od=odSizeInPreoperate)
            settings = replace(settings, preoperate=preoperate)
        except InvalidMSeqCode:
            pass

        # operate
        self._mSeqOperateCode = mSeq.operateCode
        settings = self._update_operateODSize(settings, self._mSeqOperateCode)

        return settings

    def _update_pdIn(self, settings: DecoderSettings, value: int) -> DecoderSettings:
        operate = replace(settings.operate, pdIn=calculateProcessDataLength(ProcessDataIn(value)))
        settings = replace(settings, operate=operate)
        return self._update_operateODSize(settings, self._mSeqOperateCode)

    def _update_pdOut(self, settings: DecoderSettings, value: int) -> DecoderSettings:
        operate = replace(settings.operate, pdOut=calculateProcessDataLength(ProcessDataOut(value)))
        settings = replace(settings, operate=operate)
        return self._update_operateODSize(settings, self._mSeqOperateCode)

    def handlePage(self, transaction: TransactionPage):
        if transaction.direction == TransmissionDirection.Write:
            return []

        handlers: Dict[int, Callable[[DecoderSettings, int], DecoderSettings]] = {
            DirectParameterPage1Index.MSequenceCapability.value: self._update_mseq,
            DirectParameterPage1Index.ProcessDataIn.value: self._update_pdIn,
            DirectParameterPage1Index.ProcessDataOut.value: self._update_pdOut,
        }

        updateHandler = handlers.get(transaction.index)
        if updateHandler:
            settings = self._getSettings()
            updatedSettings = updateHandler(settings, transaction.value)
            if settings != updatedSettings:
                self._setSettings(updatedSettings)

        return []
