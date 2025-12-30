from typing import Dict, Tuple

from .iodd_fileInfo import IoddFileInfo
from ._internal.iodd_documentInfo import DocumentInfo
from ._internal.iodd_identity import Identity
from ._internal.iodd_features import Features
from ._internal.iodd_physical_layer import PhysicalLayer
from ._internal.iodd_xmlDoc import IoddXmlDoc

from iolink_utils.definitions.onRequestDataOctetCount import ODOctetCount
from iolink_utils.definitions.profiles import ProfileID
from iolink_utils.exceptions import IoddFileNotFound, InvalidIoddFile, MSequenceCapabilityMissing


class Iodd:
    def __init__(self, iodd_xml_file_path: str):
        self._fileInfo: IoddFileInfo = IoddFileInfo(iodd_xml_file_path)

        if not self._fileInfo.fileExists:
            raise IoddFileNotFound(f"IODD file not found: {self._fileInfo.fullPathFilename}")

        iodd_xml_doc = IoddXmlDoc(self._fileInfo.fullPathFilename)
        if iodd_xml_doc.docType == 'IODevice':
            self._documentInfo: DocumentInfo = iodd_xml_doc.get_document_info()
            self._identity: Identity = iodd_xml_doc.get_identity()
            self._features: Features = iodd_xml_doc.get_device_features()
            self._physicalLayer: PhysicalLayer = iodd_xml_doc.get_physical_layer()
            self._processDataDefinition: Dict = iodd_xml_doc.get_process_data_definition()
        else:
            # e.g. language file
            raise InvalidIoddFile(f"Expected IODevice inside XML file, got {iodd_xml_doc.docType}.")  # pragma: no cover

    @property
    def fileInfo(self) -> IoddFileInfo:
        return self._fileInfo

    @property
    def documentInfo(self) -> DocumentInfo:
        return self._documentInfo

    @property
    def identity(self) -> Identity:
        return self._identity

    @property
    def features(self) -> Features:
        return self._features

    @property
    def physicalLayer(self) -> PhysicalLayer:
        return self._physicalLayer

    @property
    def processDataDefinition(self) -> Dict:
        return self._processDataDefinition

    @property
    def processDataConditionValues(self) -> list:
        return list(self._processDataDefinition.keys())

    @property
    def size_PDin(self) -> int:
        # note: by spec all process data definitions need to have the same size
        condition = self.processDataConditionValues[0]
        if 'pdIn' in self._processDataDefinition[condition]:
            return int(self._processDataDefinition[condition]['pdIn']['bitLength'] / 8)
        else:
            return 0

    @property
    def size_PDout(self) -> int:
        # note: by spec all process data definitions need to have the same size
        condition = self.processDataConditionValues[0]
        if 'pdOut' in self._processDataDefinition[condition]:
            return int(self._processDataDefinition[condition]['pdOut']['bitLength'] / 8)
        else:
            return 0

    @property
    def size_OnRequestData(self) -> Tuple[int, int]:
        """
        Returns number of on-request data octets in PREOPERATE and OPERATE
        :return: Tuple[preoperate, operate]
        """
        if self._physicalLayer.m_sequence_capability is None:
            raise MSequenceCapabilityMissing("M-sequence capability required to calculate on-request data size.")

        ODsize_preoperate: int = ODOctetCount.in_preoperate(self._physicalLayer.m_sequence_capability.preoperateCode)[0]
        ODsize_operate: int = ODOctetCount.in_operate(
            self._physicalLayer.m_sequence_capability.operateCode, self.size_PDin, self.size_PDout)[0]
        return ODsize_preoperate, ODsize_operate

    def isSafetyDevice(self) -> bool:
        return ProfileID.SafetyDevice in self._features.profileIDs

    def __str__(self):  # pragma: no cover
        return (
            f"IODD(\n"
            f"  {self._fileInfo}\n"
            f"  {self._features}\n"
            f"  {self._physicalLayer}\n"
            f")"
        )
