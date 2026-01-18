<!-- TOC -->
* [IO-Link Protocol Analyzer](#io-link-protocol-analyzer)
  * [Installation](#installation)
  * [Getting started](#getting-started)
    * [Hardware setup](#hardware-setup)
    * [Decoding UART frames (C/Q wire)](#decoding-uart-frames-cq-wire)
    * [Adding IO-Link Protocol Analyzer(s)](#adding-io-link-protocol-analyzers)
      * [M-Sequences](#m-sequences)
      * [Process Data](#process-data)
      * [Events / Diagnosis](#events--diagnosis)
      * [Direct Parameter (Page 1)](#direct-parameter-page-1)
      * [Indexed Service Data Unit (ISDU)](#indexed-service-data-unit-isdu)
  * [Open points](#open-points)
<!-- TOC -->

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

### Hardware setup

In order to decode IO-Link traffic, you need to attach your 
[Saleae Logic Analyzer](https://saleae.com/logic) to the C/Q wire between the IO-Link Master and the 
IO-Link device. Use a voltage divider to reduce the 24V to e.g. 3V levels. The 
IO-Link traffic can then be interpreted as a UART signal (with Rx and Tx on the same wire).

<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/iolSniffingSetup.drawio.png?raw=true" width="80%" alt="IO-Link Sniffing Setup">

### Decoding UART frames (C/Q wire)

First, the C/Q wire signal is decoded as UART via the built-in 'Async Serial' analyzer. You must configure the 
settings to correspond with your IO-Link transmission rate.

<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_asyncSerialAnalyzerSettings_COM2.drawio.png?raw=true" width="80%" alt="async serial analyzer settings">

### Adding IO-Link Protocol Analyzer(s)

To interpret these UART frames, you can add one or more IO-Link Protocol Analyzers. Each analyzer provides a 
specific type of information. For example, if you want to monitor both diagnostic and ISDU data, you would add 
one analyzer for the diagnostic data and a second one for the ISDU data.

<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_analyzerSettings.png?raw=true">

> If you want to change the output type (Analyzer Mode) later, you can do this by editing the analyzer settings.

<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_multipleAnalyzers.png?raw=true">


#### M-Sequences
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_mSequence.png?raw=true">
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_mSequence_table.png?raw=true">

#### Process Data
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_processData.png?raw=true">
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_processData_table.png?raw=true">

#### Events / Diagnosis
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_diagnosis.png?raw=true">
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_diagnosis_table.png?raw=true">

#### Direct Parameter (Page 1)
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_page.png?raw=true">
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_page_table.png?raw=true">

#### Indexed Service Data Unit (ISDU)
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_isdu.png?raw=true">
<img src="https://github.com/shaag7967/Saleae-IO-Link-Protocol-Analyzer/blob/main/doc/img/saleae_isdu_table.png?raw=true">

## Open points

- Conditional ProcessData: automatically switch between ProcessData definitions by evaluating condition index
