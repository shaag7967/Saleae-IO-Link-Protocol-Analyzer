from saleae.analyzers import AnalyzerFrame
from saleae.data.timing import SaleaeTime

from iolink_utils.octetStreamDecoder.octetStreamDecoderMessages import MasterMessage, DeviceMessage


class MSequenceHandler:
    def handleMasterMessage(self, msg: MasterMessage):
        data = {
            'mc': str(msg.mc),
            'ckt': str(msg.ckt)
        }
        if msg.pdOut:
            data['pdOut'] = bytes(msg.pdOut).hex()
        if msg.od:
            data['od'] = bytes(msg.od).hex()

        return [AnalyzerFrame(
            'MasterMsg',
            SaleaeTime(msg.startTime),
            SaleaeTime(msg.endTime),
            data
        )]

    def handleDeviceMessage(self, msg: DeviceMessage):
        data = {
            'cks': str(msg.cks)
        }
        if msg.od:
            data['od'] = bytes(msg.od).hex()
        if msg.pdIn:
            data['pdIn'] = bytes(msg.pdIn).hex()

        return [AnalyzerFrame(
            'DeviceMsg',
            SaleaeTime(msg.startTime),
            SaleaeTime(msg.endTime),
            data
        )]


class ProcessDataHandler:
    def __init__(self, decoder, DecoderPDOut, DecoderPDIn):
        self.decoder = decoder
        self.DecoderPDOut = DecoderPDOut
        self.DecoderPDIn = DecoderPDIn

    def handleMasterMessage(self, msg: MasterMessage):
        if self.decoder.settings.operate.pdOut == len(msg.pdOut):
            decodedPD = self.DecoderPDOut.from_buffer_copy(msg.pdOut)
            data = {
                'pdOut': msg.pdOut.hex()
            }
            for field_name in decodedPD.field_names:
                data[field_name] = str(getattr(decodedPD, field_name))  # str otherwise value will be shown as hex

            return [AnalyzerFrame(
                'PD out',
                SaleaeTime(msg.startTime),
                SaleaeTime(msg.endTime),
                data
            )]
        return []

    def handleDeviceMessage(self, msg: DeviceMessage):
        if self.decoder.settings.operate.pdIn == len(msg.pdIn):
            decodedPD = self.DecoderPDIn.from_buffer_copy(msg.pdIn)
            data = {
                'pdIn': msg.pdIn.hex()
            }
            for field_name in decodedPD.field_names:
                data[field_name] = str(getattr(decodedPD, field_name))  # str otherwise value will be shown as hex

            return [AnalyzerFrame(
                'PD in',
                SaleaeTime(msg.startTime),
                SaleaeTime(msg.endTime),
                data
            )]
        return []
