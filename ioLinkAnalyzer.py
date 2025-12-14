import os
from pathlib import Path
from pprint import pprint

from typing import List

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, ChoicesSetting
from saleae.data.timing import SaleaeTime

from iolink_utils.iodd.iodd import Iodd

from iolink_utils.octetDecoder.octetStreamDecoder import OctetStreamDecoder
from iolink_utils.octetDecoder.octetStreamDecoderSettings import DecoderSettings
from iolink_utils.octetDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage

from iolink_utils.messageInterpreter.messageInterpreter import MessageInterpreter
from iolink_utils.messageInterpreter.commChannelPage import TransactionPage
from iolink_utils.messageInterpreter.commChannelDiagnosis import TransactionDiagEventMemory, TransactionDiagEventReset
from iolink_utils.messageInterpreter.ISDU import ISDU

from iolink_utils.octetDecoder.processDataDecoder import createDecoderClass_PDOut, createDecoderClass_PDIn

from analyzerMode import AnalyzerMode
from dataDictGenerator import DataDictGenerator


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
            'format': 'PDOut {{data.pdOut}}'
        },
        'pdOUT': {
            'format': 'PDIn {{data.pdIn}}'
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

        filename = Path(str(self.iodd_xml_pathfilename).strip('"')).resolve()
        if not filename.is_file():
            filename_fromFile = IOLinkProtocolAnalyzer._getIoddFilenameFromTextFile()
            filename = Path(filename_fromFile.strip('"')).resolve()
            if not filename.is_file():
                raise FileNotFoundError(f"IODD file '{filename}' not found.")

        self.iodd = Iodd(str(filename))

        # process data
        pdCondition = None
        if self.process_data_condition:
            pdCondition = int(str(self.process_data_condition))

        self.DecoderPDOut = createDecoderClass_PDOut(self.iodd.process_data_definition, pdCondition)
        self.DecoderPDIn = createDecoderClass_PDIn(self.iodd.process_data_definition, pdCondition)


        settings = DecoderSettings.fromIODD(self.iodd)
        self.decoder = OctetStreamDecoder(settings)
        self.interpreter = MessageInterpreter()

        self.printAnalyzerSettings()

    @staticmethod
    def _getIoddFilenameFromTextFile() -> str:
        iodd_filenameFromFile = Path(os.path.dirname(__file__), 'iodd_filename.txt').resolve()
        if iodd_filenameFromFile.is_file():
            with open(iodd_filenameFromFile) as f:
                return f.readline().strip()

    def printAnalyzerSettings(self):
        print(f"Using IODD file: '{self.iodd.filename.value}'")
        print(f"IODD\n"
              f"  {self.iodd.document_info.version} / {self.iodd.document_info.releaseDate} / {self.iodd.document_info.copyright}\n"
              f"Physical connection\n"
              f"  BitRate: {self.iodd.physical_layer.bitrate.name} ({self.iodd.physical_layer.bitrate.value} baud)")

        print(f"Process data")
        pprint(self.iodd.process_data_definition)

        print(f"M-Sequence payload sizes")
        print(f"   Startup:    {self.decoder.settings.startup}")
        print(f"   Preoperate: {self.decoder.settings.preoperate}")
        print(f"   Operate:    {self.decoder.settings.operate}")

    def decode(self, frame: AnalyzerFrame):
        analyzerFrames: List[AnalyzerFrame] = []

        if frame.type == 'data':
            if 'error' in frame.data:
                self.decoder.reset()
                return []

            message_mseq = self.decoder.processOctet(frame.data['data'][0], frame.start_time.as_datetime(),
                                                     frame.end_time.as_datetime())

            if self.analyzerMode == AnalyzerMode.MSequence:
                if isinstance(message_mseq, MasterMessage):
                    analyzerFrames.append(AnalyzerFrame('mseqMASTER', SaleaeTime(message_mseq.start_time),
                                                        SaleaeTime(message_mseq.end_time),
                                                        DataDictGenerator.fromMasterMessage(message_mseq)))
                elif isinstance(message_mseq, DeviceMessage):
                    analyzerFrames.append(AnalyzerFrame('mseqDEVICE', SaleaeTime(message_mseq.start_time),
                                                        SaleaeTime(message_mseq.end_time),
                                                        DataDictGenerator.fromDeviceMessage(message_mseq)))
            elif self.analyzerMode == AnalyzerMode.ProcessData:
                if isinstance(message_mseq, MasterMessage):
                    # we don't know if we are in OPERATE -> check for process data
                    if self.decoder.settings.operate.pdOut == len(message_mseq.pdOut):
                        analyzerFrames.append(
                            AnalyzerFrame('pdOUT', SaleaeTime(message_mseq.start_time),
                                          SaleaeTime(message_mseq.end_time),
                                          DataDictGenerator.fromProcessData('pdOut', self.DecoderPDOut,
                                                                            message_mseq.pdOut)))
                elif isinstance(message_mseq, DeviceMessage):
                    # we don't know if we are in OPERATE -> check for process data
                    if self.decoder.settings.operate.pdIn == len(message_mseq.pdIn):
                        analyzerFrames.append(
                            AnalyzerFrame('pdIN', SaleaeTime(message_mseq.start_time),
                                          SaleaeTime(message_mseq.end_time),
                                          DataDictGenerator.fromProcessData('pdIn', self.DecoderPDIn,
                                                                            message_mseq.pdIn)))
            else:
                commChannelMessages = self.interpreter.processMessage(message_mseq)

                if self.analyzerMode == AnalyzerMode.PageDiagnosis:
                    for msg in commChannelMessages:
                        if isinstance(msg, TransactionPage):
                            analyzerFrames.append(
                                AnalyzerFrame('page', SaleaeTime(msg.start_time), SaleaeTime(msg.end_time), msg.data()))
                        elif isinstance(msg, TransactionDiagEventMemory):
                            analyzerFrames.append(
                                AnalyzerFrame('diagREAD', SaleaeTime(msg.start_time), SaleaeTime(msg.end_time),
                                              msg.data()))
                        elif isinstance(msg, TransactionDiagEventReset):
                            analyzerFrames.append(
                                AnalyzerFrame('diagFINISH', SaleaeTime(msg.start_time), SaleaeTime(msg.end_time),
                                              msg.data()))

                elif self.analyzerMode == AnalyzerMode.ISDU:
                    for msg in commChannelMessages:
                        if isinstance(msg, ISDU):
                            analyzerFrames.append(
                                AnalyzerFrame(msg.name(), SaleaeTime(msg.start_time), SaleaeTime(msg.end_time), msg.data()))

        return analyzerFrames
