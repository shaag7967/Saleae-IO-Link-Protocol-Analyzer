from enum import IntEnum


# See Table B.8 – Index assignment of data objects (Device parameter)
# See IOL CommonProfile: Table B.1 – General profile relevant Device parameters
# See Firmware Update Profile: Table 1 – Index assignment of the BLOB parameters
# See Firmware Update Profile: Table 12 – Device parameters reserved for FW-Update
# See Safety Spec: Table A.1 – Indices for SDCI-FS
class IOLinkIndex(IntEnum):
    SystemCommand = 0x0002
    DataStorageIndex = 0x0003
    DeviceAccessLocksR = 0x000C
    ProfileCharacteristic = 0x000D
    PDInputDescriptor = 0x000E
    PDOutputDescriptor = 0x000F
    VendorName = 0x0010
    VendorText = 0x0011
    ProductName = 0x0012
    ProductID = 0x0013
    ProductText = 0x0014
    SerialNumber = 0x0015
    HardwareRevision = 0x0016
    FirmwareRevision = 0x0017
    ApplicationSpecificTag = 0x0018
    FunctionTag = 0x0019
    LocationTag = 0x001A
    ProductURI = 0x001B
    ErrorCount = 0x0020
    DeviceStatus = 0x0024
    DetailedDeviceStatus = 0x0025
    ProcessDataInput = 0x0028
    ProcessDataOutput = 0x0029
    OffsetTime = 0x0030
    # BLOB / firmware update
    BLOB_ID = 0x0031
    BLOB_CH = 0x0032
    # Safety Device
    FSP_Authenticity = 0x4200
    FSP_Protocol = 0x4201
    FSP_VerifyRecord = 0x4202
    FSP_TimeToReady = 0x4210
    FSP_MinShutDownTime = 0x4211
    FSP_ParamDescCRC = 0x4212
    FSP_WCDT = 0x4213
    FSP_OFDT = 0x4214
    # BLOB / firmware update
    FWPassword = 0x43BD
    HW_ID_Key = 0x43BE
    BootmodeStatus = 0x43BF

