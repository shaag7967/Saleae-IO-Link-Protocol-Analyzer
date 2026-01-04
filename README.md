# IO-Link Protocol Analyzer

This page describes the usage of an [IO-Link](https://io-link.com/) traffic analyzer extension for 
[Saleae Logic Analyzers](https://saleae.com/logic).

It decodes IO-Link frames into 
- M-Sequences, 
- ISDUs, 
- DirectParameter access (Page1), 
- Diagnosis and 
- Process Data.

Required IO-Link parameters are taken from the device description file (IODD).

> If you don't have an IODD for your device, try out [this IO-Link Analyzer](https://github.com/HBM/saleae-hla-io-link).
> There you can specify all parameters (e.g. on-request data size) manually.

## Installation

Right now, this analyzer (HLA) is not officially released as a 
[Saleae Logic Extension](https://support.saleae.com/product/user-guide/extensions-apis-and-sdks/extensions/high-level-analyzer-extensions/shared-high-level-analyzers-hlas). 
This means you have to download and install it manually. 

1. Download the latest version from GitHub [here](https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/archive/refs/heads/main.zip)
2. Extract the zip file to a place where it can stay (e.g. a folder where you want to keep your custom Saleae extensions)
3. Open Logic 2 software and click on "Extensions" (on the right). Click the three dots on the top right and select "Load existing extensions..."
4. In the newly opened window, find the file "extension.json" inside the extracted IO-Link Analyzer folder and open it

When adding a new analyzer, there is now an entry "IO-Link Protocol Analyzer" in the list of available analyzers.

## Getting started

### Sniffing hardware setup

In order to decode IO-Link traffic, you need to attach your 
[Saleae Logic Analyzer](https://saleae.com/logic) to the C/Q wire between the IO-Link Master and the 
IO-Link device. Use a voltage divider to reduce the 24V (or higher) to e.g. 3V levels. The 
IO-Link traffic can then be interpreted as a UART signal (with Rx and Tx on the same wire).

<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/iolSniffingSetup.drawio.png?raw=true" width="70%" alt="IO-Link Sniffing Setup">

### Decoding UART frames (C/Q wire)

In the first step, the signal on the C/Q wire is interpreted as UART using the builtin "Async Serial" analyzer. You have
to set the correct settings matching your IO-Link communication speed.

<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_asyncSerialAnalyzerSettings_COM2.drawio.png?raw=true" width="70%" alt="async serial analyzer settings">

### Adding IO-Link Protocol Analyzer(s)

To give these UART frames a meaning, you add one or more IO-Link Protocol Analyzer. Every analyzer is giving you only 
one type of information. E.g. if you want to see Diagnosis and ISDU data, add an analyzer for the Diagnosis data 
and another one for the ISDU data.

> If you want to change the output type (Analyzer Mode) later, you can do this by editing the analyzer settings.

To be continued...
