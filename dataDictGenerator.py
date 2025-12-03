import ctypes

from iolink_utils.octetDecoder.octetStreamDecoderMessages import DeviceMessage, MasterMessage


class DataDictGenerator:
    @staticmethod
    def fromMasterMessage(message: MasterMessage):
        data = {
            'mc': str(message.mc),
            'ckt': str(message.ckt)
        }
        if message.pdOut:
            data['pdOut'] = bytes(message.pdOut).hex()
        if message.od:
            data['od'] = bytes(message.od).hex()
        return data

    @staticmethod
    def fromDeviceMessage(message: DeviceMessage):
        data = {
            'cks': str(message.cks)
        }
        if message.od:
            data['od'] = bytes(message.od).hex()
        if message.pdIn:
            data['pdIn'] = bytes(message.pdIn).hex()
        return data

    @staticmethod
    def fromProcessData(name: str, decoderClass: ctypes.Structure, processData: bytearray):
        decodedPD = decoderClass.from_buffer_copy(processData)
        data = {
            name: processData.hex()
        }
        for field_name in decodedPD.field_names:
            data[field_name] = str(getattr(decodedPD, field_name))  # str otherwise value will be shown as hex
        return data
