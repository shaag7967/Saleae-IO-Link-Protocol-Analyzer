from typing import Optional, Tuple

from .iodd_filename import IoddFilename
from .iodd_documentInfo import DocumentInfo
from .iodd_identity import Identity
from .iodd_features import Features
from .iodd_physical_layer import PhysicalLayer
from .ioddXmlDoc import IoddXmlDoc

from iolink_utils.definitions.onRequestDataOctetCount import ODOctetCount


class Iodd:
    def __init__(self, iodd_xml_file_path: Optional[str] = None):
        self.iodd_xml_doc = None

        self.filename = IoddFilename(iodd_xml_file_path)
        self.document_info: DocumentInfo = DocumentInfo()
        self.identity: Identity = Identity()
        self.features: Features = Features()
        self.physical_layer: PhysicalLayer = PhysicalLayer()
        self.process_data_definition = {
            None: {}
        }

        if iodd_xml_file_path is not None:
            self.load(iodd_xml_file_path)

    def load(self, xml_file_path: str):
        self.filename = IoddFilename(xml_file_path)
        self.iodd_xml_doc = IoddXmlDoc(xml_file_path)

        self.document_info = self.iodd_xml_doc.get_document_info()
        self.identity = self.iodd_xml_doc.get_identity()
        self.features = self.iodd_xml_doc.get_device_features()
        self.physical_layer = self.iodd_xml_doc.get_physical_layer()
        self.process_data_definition = self.iodd_xml_doc.get_process_data_definition()

    @property
    def processDataConditionValues(self):
        return list(self.process_data_definition.keys())

    @property
    def size_PDIn(self):
        # note: by spec all process data definitions need to have the same size
        condition = self.processDataConditionValues[0]
        if 'pdIn' in self.process_data_definition[condition]:
            return int(self.process_data_definition[condition]['pdIn']['bitLength'] / 8)
        else:
            return 0

    @property
    def size_PDOut(self):
        # note: by spec all process data definitions need to have the same size
        condition = self.processDataConditionValues[0]
        if 'pdOut' in self.process_data_definition[condition]:
            return int(self.process_data_definition[condition]['pdOut']['bitLength'] / 8)
        else:
            return 0

    @property
    def size_OnRequestData(self) -> Tuple[int, int]:
        """
        Returns number of on-request data octets in PREOPERATE and OPERATE
        :return: Tuple[preoperate, operate]
        """
        ODsize_preoperate: int = ODOctetCount.in_preoperate(self.physical_layer.m_sequence_capability.preoperateCode)[0]
        ODsize_operate: int = ODOctetCount.in_operate(
            self.physical_layer.m_sequence_capability.operateCode, self.size_PDIn, self.size_PDOut)[0]
        return ODsize_preoperate, ODsize_operate

    def __str__(self):
        return (
            f"IODD(\n"
            f"  {self.features}\n"
            f"  {self.physical_layer}\n"
            f")"
        )
