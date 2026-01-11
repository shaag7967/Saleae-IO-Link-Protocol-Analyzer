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
from automaticSettingsHandler import AutomaticSettingsHandler


class IOLinkProtocolAnalyzer(HighLevelAnalyzer):
    iodd_xml_pathAndFilename = StringSetting(label='IODD XML file')
    analyzer_mode_setting = ChoicesSetting(AnalyzerMode.descriptions())
    process_data_condition = StringSetting(label='Condition value to select ProcessData definition (default: empty)')

    # only result types with a special display format are listed. Everything else just shows content of data dictionary
    result_types = {
        'PD in': {
            'format': 'PDin({{data.pdIn}})'
        },
        'PD out': {
            'format': 'PDout({{data.pdOut}})'
        },
        'Page': {
            'format': 'Page({{data.pageDir}} {{data.pageInfo}})'
        },
        'DiagRead': {
            'format': 'Diagnosis({{data.events}})'
        },
        'DiagReset': {
            'format': 'Diagnosis(Reset)'
        }
    }

    def __init__(self, *args, **kwargs):
        self.analyzerMode: AnalyzerMode = AnalyzerMode(self.analyzer_mode_setting)

        iodd_filename_setting = str(self.iodd_xml_pathAndFilename).strip('"')
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
        self.automaticSettingsHandler = AutomaticSettingsHandler(
            getter=lambda: self.decoder.settings,
            setter=self._setDecoderSettings
        )

        self.printAnalyzerSettings()

    def printAnalyzerSettings(self):
        print(f"IODD\n"
              f"  {self.iodd.fileInfo.filename}"
              f"  {self.iodd.documentInfo.version} / {self.iodd.documentInfo.releaseDate} / {self.iodd.documentInfo.copyright}\n"
              f"Physical connection\n"
              f"  BitRate: {self.iodd.physicalLayer.bitrate.name} ({self.iodd.physicalLayer.bitrate.value} baud)")

        print(f"Process data")
        pprint(self.iodd.processDataDefinition)

        print(f"M-Sequence payload sizes")
        self._printDecoderSettings()

    def _printDecoderSettings(self):
        print(f"   Startup:    {self.decoder.settings.startup}")
        print(f"   Preoperate: {self.decoder.settings.preoperate}")
        print(f"   Operate:    {self.decoder.settings.operate}")

    def _setDecoderSettings(self, settings: DecoderSettings):
        self.decoder.setSettings(settings)
        print(f"M-Sequence payload sizes (updated)")
        self._printDecoderSettings()

    def _dispatchMessage(self, message):
        if message is None:
            return []

        # interpret messages
        transaction = self.interpreter.processMessage(message)
        if transaction:
            transaction.dispatch(self.automaticSettingsHandler)  # this updates decoder settings

            # convert transactions into saleae frames
            if self.analyzerMode == AnalyzerMode.Diagnosis:
                return transaction.dispatch(DiagnosisHandler())
            if self.analyzerMode == AnalyzerMode.Page:
                return transaction.dispatch(PageHandler())
            if self.analyzerMode == AnalyzerMode.ISDU:
                return transaction.dispatch(ISDUHandler())

        # convert messages into saleae frames
        if self.analyzerMode == AnalyzerMode.MSequence:
            return message.dispatch(MSequenceHandler())
        if self.analyzerMode == AnalyzerMode.ProcessData:
            return message.dispatch(ProcessDataHandler(self.decoder, self.DecoderPDOut, self.DecoderPDIn))

        return []

    def decode(self, frame: AnalyzerFrame):
        if frame.type != 'data':
            return []

        if 'error' in frame.data:
            self.decoder.reset()
            self.interpreter.reset()
            return []

        try:
            message = self.decoder.processOctet(
                frame.data['data'][0],
                frame.start_time.as_datetime(),
                frame.end_time.as_datetime()
            )
            return self._dispatchMessage(message)
        except (IOLinkUtilsException, ValueError, IndexError) as e:
            print(e)
            self.decoder.reset()
            self.interpreter.reset()
            return []
