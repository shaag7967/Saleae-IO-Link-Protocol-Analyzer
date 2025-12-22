import os
from pathlib import Path
from pprint import pprint

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, ChoicesSetting

from iolink_utils.iodd.iodd import Iodd
from iolink_utils.octetStreamDecoder.octetStreamDecoder import OctetStreamDecoder
from iolink_utils.octetStreamDecoder.octetStreamDecoderSettings import DecoderSettings
from iolink_utils.messageInterpreter.messageInterpreter import MessageInterpreter
from iolink_utils.processDataDecoder.processDataDecoder import createDecoderClass_PDOut, createDecoderClass_PDIn
from iolink_utils.exceptions import IOLinkUtilsException

from analyzerMode import AnalyzerMode
from messageHandler import MSequenceHandler, ProcessDataHandler
from transactionHandler import DiagnosisHandler, PageHandler, ISDUHandler


class IOLinkProtocolAnalyzer(HighLevelAnalyzer):
    iodd_xml_pathfilename = StringSetting(label='IODD XML file')
    analyzer_mode_setting = ChoicesSetting(AnalyzerMode.descriptions())
    process_data_condition = StringSetting(label='Condition value to select ProcessData definition (default: empty)')

    result_types = {
        'mseqMASTER': {
            'format': 'MST {{data.mc}} {{data.ckt}} OD({{data.od}}) PD({{data.pdOut}})'
        },
        'mseqDEVICE': {
            'format': 'DEV OD({{data.od}}) PD({{data.pdIn}}) {{data.cks}}'
        },
        'pdIN': {
            'format': 'PDIn {{data.pdIn}}'
        },
        'pdOUT': {
            'format': 'PDOut {{data.pdOut}}'
        },
        'page': {
            'format': 'Page {{data.page}}'
        },
        'diagREAD': {
            'format': 'Diagnose {{data.evtStatus}}'
        },
        'diagFINISH': {
            'format': 'Diagnose Reset'
        },
        'Write8bitIdx': {
            'format': 'Write8bitIdx valid={{data.valid}} index={{data.index}} data={{data.data}}'
        },
        'Write8bitIdxSub': {
            'format': 'Write8bitIdxSub valid={{data.valid}} index={{data.index}} subIndex={{data.subIndex}} data={{data.data}}'
        },
        'Write16bitIdxSub': {
            'format': 'Write16bitIdxSub valid={{data.valid}} index={{data.index}} subIndex={{data.subIndex}} data={{data.data}}'
        },
        'Read8bitIdx': {
            'format': 'Read8bitIdx valid={{data.valid}} index={{data.index}}'
        },
        'Read8bitIdxSub': {
            'format': 'Read8bitIdxSub valid={{data.valid}} index={{data.index}} subIndex={{data.subIndex}}'
        },
        'Read16bitIdxSub': {
            'format': 'Read16bitIdxSub valid={{data.valid}} index={{data.index}} subIndex={{data.subIndex}}'
        },
        'WriteResp_M': {
            'format': 'WriteResp_M valid={{data.valid}} errorCode={{data.errorCode}} additionalCode={{data.additionalCode}}'
        },
        'WriteResp_P': {
            'format': 'WriteResp_P valid={{data.valid}}'
        },
        'ReadResp_M': {
            'format': 'ReadResp_M valid={{data.valid}} errorCode={{data.errorCode}} additionalCode={{data.additionalCode}}'
        },
        'ReadResp_P': {
            'format': 'ReadResp_P valid={{data.valid}} data={{data.data}}'
        }
    }

    def __init__(self):
        self.analyzerMode: AnalyzerMode = AnalyzerMode(self.analyzer_mode_setting)

        iodd_filename_setting = str(self.iodd_xml_pathfilename).strip('"')
        if len(iodd_filename_setting) < 5:
            raise ValueError(f"Invalid IODD filename: '{iodd_filename_setting}' (length: {len(iodd_filename_setting)})")

        filename = Path(iodd_filename_setting).resolve()
        if not filename.is_file():
            raise FileNotFoundError(f"IODD file '{filename}' not found.")

        self.iodd = Iodd(str(filename))

        # process data
        pdCondition = None
        if self.process_data_condition:
            pdCondition = int(str(self.process_data_condition))
        if pdCondition not in self.iodd.processDataConditionValues:
            raise ValueError(f"Invalid ProcessDataCondition: {pdCondition}. "
                             f"Allowed values are: {', '.join(self.iodd.processDataConditionValues)}.")

        self.DecoderPDOut = createDecoderClass_PDOut(self.iodd.processDataDefinition, pdCondition)
        self.DecoderPDIn = createDecoderClass_PDIn(self.iodd.processDataDefinition, pdCondition)

        settings = DecoderSettings.fromIODD(self.iodd)
        self.decoder = OctetStreamDecoder(settings)
        self.interpreter = MessageInterpreter()

        self.printAnalyzerSettings()

    def printAnalyzerSettings(self):
        print(f"Using IODD file: '{self.iodd.fileInfo.filename}'")
        print(f"IODD\n"
              f"  {self.iodd.documentInfo.version} / {self.iodd.documentInfo.releaseDate} / {self.iodd.documentInfo.copyright}\n"
              f"Physical connection\n"
              f"  BitRate: {self.iodd.physicalLayer.bitrate.name} ({self.iodd.physicalLayer.bitrate.value} baud)")

        print(f"Process data")
        pprint(self.iodd.processDataDefinition)

        print(f"M-Sequence payload sizes")
        print(f"   Startup:    {self.decoder.settings.startup}")
        print(f"   Preoperate: {self.decoder.settings.preoperate}")
        print(f"   Operate:    {self.decoder.settings.operate}")

    def _dispatchMessage(self, message):
        if message is None:
            return []

        # convert messages into saleae frames
        if self.analyzerMode == AnalyzerMode.MSequence:
            return message.dispatch(MSequenceHandler())

        if self.analyzerMode == AnalyzerMode.ProcessData:
            return message.dispatch(ProcessDataHandler(self.decoder, self.DecoderPDOut, self.DecoderPDIn))

        # interpret messages and create transactions from it
        if self.analyzerMode == AnalyzerMode.Diagnosis:
            handler = DiagnosisHandler()
        elif self.analyzerMode == AnalyzerMode.Page:
            handler = PageHandler()
        elif self.analyzerMode == AnalyzerMode.ISDU:
            handler = ISDUHandler()
        else:
            return []

        # convert transactions into saleae frames
        transactions = self.interpreter.processMessage(message)
        analyzerFrames = []
        for tx in transactions:
            analyzerFrames.extend(tx.dispatch(handler))

        return analyzerFrames

    def decode(self, frame: AnalyzerFrame):
        if frame.type != 'data':
            return []

        if 'error' in frame.data:
            self.decoder.reset()
            return []

        try:
            message = self.decoder.processOctet(
                frame.data['data'][0],
                frame.start_time.as_datetime(),
                frame.end_time.as_datetime()
            )
            return self._dispatchMessage(message)
        except IOLinkUtilsException:
            self.decoder.reset()
            # TODO self.interpreter.reset()
            return []
