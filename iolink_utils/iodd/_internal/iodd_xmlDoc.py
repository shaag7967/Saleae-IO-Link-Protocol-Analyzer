from typing import Tuple
import xml.etree.ElementTree as elTree
from datetime import date

from .iodd_documentInfo import DocumentInfo
from .iodd_identity import Identity, DeviceVariant
from .iodd_features import Features
from .iodd_physical_layer import PhysicalLayer

from iolink_utils.exceptions import UnsupportedComplexDataType, UnsupportedSimpleDataType
from iolink_utils.utils.version import Version
from iolink_utils.definitions.bitRate import BitRate
from iolink_utils.definitions.profiles import ProfileID
from iolink_utils.octetDecoder.octetDecoder import MSequenceCapability


class IoddXmlDoc:
    def __init__(self, iodd_xml_file_path: str):
        self._tree = elTree.parse(iodd_xml_file_path)
        self._root = self._tree.getroot()

        # namespaces
        self._namespaces = {
            'iolink': self._root.tag.split('}')[0].strip('{'),
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xml': 'http://www.w3.org/XML/1998/namespace'
        }

        # local name of root
        self._docType = self._root.tag.split('}')[-1]

    @property
    def docType(self) -> str:
        return self._docType

    def get_document_info(self) -> DocumentInfo:
        xml_document_info = self._root.find(".//iolink:DocumentInfo", self._namespaces)

        doc_info = DocumentInfo()
        if xml_document_info is not None:
            doc_info.version = Version(xml_document_info.get("version"))
            doc_info.releaseDate = date.fromisoformat(
                xml_document_info.get("releaseDate").strip()
            )
            doc_info.copyright = xml_document_info.get("copyright")

        return doc_info

    def get_identity(self) -> Identity:
        xml_identity = self._root.find(".//iolink:DeviceIdentity", self._namespaces)
        identity = Identity()

        if xml_identity is not None:
            identity.vendorId = int(xml_identity.get("vendorId"))
            identity.deviceId = int(xml_identity.get("deviceId"))
            identity.vendorName = xml_identity.get("vendorName")

            identity.vendorText = self._getTextTuple(xml_identity, 'VendorText')
            identity.vendorUrl = self._getTextTuple(xml_identity, 'VendorUrl')

            xml_vendorLogo = xml_identity.find(".//iolink:VendorLogo", self._namespaces)
            identity.vendorLogo = "" if xml_vendorLogo is None else xml_vendorLogo.get('name')

            identity.deviceName = self._getTextTuple(xml_identity, 'DeviceName')
            identity.deviceFamily = self._getTextTuple(xml_identity, 'DeviceFamily')

            for xml_deviceVariant in xml_identity.findall(".//iolink:DeviceVariant", self._namespaces):
                variant = DeviceVariant()
                variant.productId = xml_deviceVariant.get('productId')
                variant.deviceSymbol = xml_deviceVariant.get('deviceSymbol')
                variant.deviceIcon = xml_deviceVariant.get('deviceIcon')
                variant.name = self._getTextTuple(xml_deviceVariant, 'Name')
                variant.description = self._getTextTuple(xml_deviceVariant, 'Description')
                identity.deviceVariants.append(variant)

        return identity

    def get_device_features(self) -> Features:
        xml_features = self._root.find(".//iolink:Features", self._namespaces)
        features = Features()

        if xml_features is not None:
            features.blockParameter = xml_features.get("blockParameter") == "true"
            features.dataStorage = xml_features.get("dataStorage") == "true"
            features.profileIDs = [
                ProfileID(int(c))
                for c in xml_features.get("profileCharacteristic", "").split()
            ]

            xml_locks = xml_features.find("iolink:SupportedAccessLocks", self._namespaces)
            if xml_locks is not None:
                features.supportedAccessLocks.parameter = xml_locks.get("parameter")
                features.supportedAccessLocks.dataStorage = xml_locks.get("dataStorage")
                features.supportedAccessLocks.localParameterization = xml_locks.get("localParameterization")
                features.supportedAccessLocks.localUserInterface = xml_locks.get("localUserInterface")

        return features

    def get_physical_layer(self) -> PhysicalLayer:
        xml_physical_layer = self._root.find(".//iolink:PhysicalLayer", self._namespaces)
        physical_layer = PhysicalLayer()

        if xml_physical_layer is not None:
            bitrate = xml_physical_layer.get("bitrate") or xml_physical_layer.get("baudrate")
            physical_layer.bitrate = BitRate(bitrate)
            physical_layer.min_cycle_time = int(xml_physical_layer.get("minCycleTime"))
            physical_layer.sio_supported = xml_physical_layer.get("sioSupported") == "true"

            capa = xml_physical_layer.get("mSequenceCapability")
            physical_layer.m_sequence_capability = (
                MSequenceCapability(int(capa)) if capa else None
            )

        return physical_layer

    def get_process_data_definition(self):
        pdDefs = {}

        for xml_process_data in self._root.findall(".//iolink:ProcessData", self._namespaces):
            xml_cond = xml_process_data.find("iolink:Condition", self._namespaces)
            condition = None if xml_cond is None else int(xml_cond.get("value"))

            processData_json = {'id': xml_process_data.get("id")}

            pdIn = xml_process_data.find("iolink:ProcessDataIn", self._namespaces)
            if pdIn is not None:
                processData_json['pdIn'] = self._getProcessDataInOutAsJSON(pdIn)

            pdOut = xml_process_data.find("iolink:ProcessDataOut", self._namespaces)
            if pdOut is not None:
                processData_json['pdOut'] = self._getProcessDataInOutAsJSON(pdOut)

            pdDefs[condition] = processData_json

        return pdDefs

    def _getTextTuple(self, xml_element, textXmlTag: str) -> Tuple[str, str]:
        textTag = xml_element.find(f'iolink:{textXmlTag}', self._namespaces)
        if textTag is not None:
            text_id = textTag.get('textId')
            return text_id, self._getTextForTextID(text_id)
        return "", ""

    def _getTextForTextID(self, text_id: str, language: str = "en") -> str:
        for coll in self._root.findall(".//iolink:ExternalTextCollection", self._namespaces):
            for lang in coll.findall("iolink:PrimaryLanguage", self._namespaces):
                if lang.get(f"{{{self._namespaces['xml']}}}lang") == language:
                    for text in lang.findall("iolink:Text", self._namespaces):
                        if text.get("id") == text_id:
                            return text.get("value", "")
        return ""

    def _getDatatype(self, xml_element):
        for tag in ("Datatype", "SimpleDatatype", "DatatypeRef"):
            el = xml_element.find(f"iolink:{tag}", self._namespaces)
            if el is not None:
                if tag == "DatatypeRef":
                    ref_id = el.get("datatypeId")
                    for dt in self._root.findall(".//iolink:Datatype", self._namespaces):
                        if dt.get("id") == ref_id:
                            return dt
                return el
        return None

    def _getProcessDataInOutAsJSON(self, xml_processData):
        text_id = xml_processData.find('iolink:Name', self._namespaces).get('textId')

        dataType = self._getDatatype(xml_processData)

        return {
            "id": xml_processData.get("id"),
            "bitLength": int(xml_processData.get("bitLength")),
            "name": (text_id, self._getTextForTextID(text_id)),
            "dataFormat": self._getDatatypeAsJSON(dataType)
        }

    def _getDatatypeAsJSON(self, xml_dataType):
        xsi_type = xml_dataType.get(f"{{{self._namespaces['xsi']}}}type")

        if xsi_type in ('RecordT', 'ArrayT'):
            return self._getComplexDatatypeAsJSON(xml_dataType)

        return [{
            'bitOffset': 0,
            'data': self._getSimpleDatatypeAsJSON(xml_dataType)
        }]

    def _getComplexDatatypeAsJSON(self, xml_complex_datatype):
        xsi_type = xml_complex_datatype.get(f"{{{self._namespaces['xsi']}}}type")

        if xsi_type == 'RecordT':
            return self._getRecordTypeAsJSON(xml_complex_datatype)
        if xsi_type == 'ArrayT':
            return self._getArrayTypeAsJSON(xml_complex_datatype)

        raise UnsupportedComplexDataType(f"Unsupported complex data type ({xsi_type})")

    def _getRecordTypeAsJSON(self, xml_record_datatype):
        items = []

        for recordItem in xml_record_datatype.findall(".//iolink:RecordItem", self._namespaces):
            text_id = recordItem.find('iolink:Name', self._namespaces).get('textId')
            dataType = self._getDatatype(recordItem)

            items.append({
                'bitOffset': int(recordItem.get("bitOffset")),
                'subIndex': int(recordItem.get("subindex")),
                'name': (text_id, self._getTextForTextID(text_id)),
                'data': self._getSimpleDatatypeAsJSON(dataType)
            })

        return items

    def _getArrayTypeAsJSON(self, xml_array_datatype):
        items = []
        count = int(xml_array_datatype.get('count'))

        dataType = self._getDatatype(xml_array_datatype)
        datatype_json = self._getSimpleDatatypeAsJSON(dataType)

        for i in range(count):
            items.append({
                'bitOffset': datatype_json['bitLength'] * i,
                'data': datatype_json
            })

        return items

    def _getSimpleDatatypeAsJSON(self, xml_simple_datatype):
        xsi_type = xml_simple_datatype.get(f"{{{self._namespaces['xsi']}}}type")

        if xsi_type == 'BooleanT':
            return {'type': bool, 'bitLength': 1}
        if xsi_type in ('UIntegerT', 'IntegerT'):
            return {'type': int, 'bitLength': int(xml_simple_datatype.get("bitLength"))}
        if xsi_type == 'Float32T':
            return {'type': float, 'bitLength': 32}
        if xsi_type in ('StringT', 'OctetStringT'):
            return {
                'type': bytearray,
                'bitLength': int(xml_simple_datatype.get("fixedLength")) * 8
            }

        raise UnsupportedSimpleDataType(f"Not supported '{xsi_type}'")
