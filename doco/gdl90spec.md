# GDL 90

# Data Interface

# Specification

June 5, 2007
560-1058-00 Rev A


¤ 2004-2007 Garmin Ltd. or its subsidiaries. All rights reserved. Printed in the U.S.A.

Garmin International, Inc., 1200 East 151st Street, Olathe Kansas 66062, U.S.A.
Tel: 913/397.8200 Fax: 913/397.

Garmin (Europe) Ltd., Unit 5, The Quadrangle, Abbey Park Industrial Estate, Romsey, Hampshire S051 9DL, U.K.
Tel: 44/1794.519944 Fax: 44/1794.

Garmin Corporation, No. 68, Jangshu 2nd Road, Shijr, Taipei County, Taiwan
Tel: 886/02.2642.9199 Fax: 886/02.2642.

Garmin AT, Inc., 2345 Turner Road, S.E., Salem, OR 97302, U.S.A.
Tel: 800/525.6726 Fax: 503/364.
Canada Tel: 800/654.
International Tel: 503/391.

Cage Code: 0XCJ

Visit our web pages at [http://www.garmin.com](http://www.garmin.com)

Send comments about this manual by email to: techpubs.salem@garmin.com

Garmin£, Garmin AT, and GNS are trademarks of Garmin Ltd. or its subsidiaries. These trademarks may not be
used without the express permission of Garmin.


## June 5, 2007 Page i



June 5, 2007 Page iii

- 1. INTRODUCTION.............................................................................................................. Table of Contents
- 1.1. Purpose...............................................................................................................................
- 1.2. Scope...................................................................................................................................
- 1.3. Interface Types..................................................................................................................
- 1.4. Disclaimer for Display Vendors.......................................................................................
- 1.5. DISCLAIMER; NO WARRANTY; LIMITATION OF LIABILITY
- 1.6. Glossary
- 2. RS-422 BUS MESSAGE STRUCTURE ..........................................................................
- 2.1. Physical Interface..............................................................................................................
- 2.2. Message Structure Overview
   - 2.2.1. Datalink Structure and Processing ..............................................................................
   - 2.2.2. Message ID ..................................................................................................................
   - 2.2.3. FCS Calculation...........................................................................................................
   - 2.2.4. Message Example.........................................................................................................
- 2.3. Bandwidth Management
- 3. MESSAGE DEFINITIONS...............................................................................................
- 3.1. Heartbeat Message..........................................................................................................
   - 3.1.1. Status Byte 1...............................................................................................................
   - 3.1.2. Status Byte 2...............................................................................................................
   - 3.1.3. UAT Time Stamp ........................................................................................................
   - 3.1.4. Received Message Counts..........................................................................................
- 3.2. Initialization Message
   - 3.2.1. Configuration Byte 1..................................................................................................
   - 3.2.2. Configuration Byte 2..................................................................................................
- 3.3. Uplink Data Message
   - 3.3.1. Time of Reception (TOR) ...........................................................................................
   - 3.3.2. Uplink Payload ..........................................................................................................1
- 3.4. Ownship Report Message...............................................................................................
- 3.5. Traffic Report..................................................................................................................
   - 3.5.1. Traffic and Ownship Report Data Format.................................................................
   - 3.5.2. Traffic Report Example..............................................................................................
- 3.6. Pass-Through Reports
- 3.7. Height Above Terrain.....................................................................................................
- 3.8. Ownship Geometric Altitude Message..........................................................................
- 4. UPLINK PAYLOAD FORMAT ....................................................................................
- 4.1. Uplink Message
   - 4.1.1. UAT-Specific Header .................................................................................................
   - 4.1.2. Application Data ........................................................................................................3
- 4.2. Information Frames........................................................................................................
   - 4.2.1. Length Field ...............................................................................................................
   - 4.2.2. Reserved Field
   - 4.2.3. Frame Type Field.......................................................................................................
   - 4.2.4. Frame Data Field ......................................................................................................
- Page ii June 5,
- 4.3. FIS-B Product Encoding (APDUs)
   - 4.3.1. APDU Header ............................................................................................................
   - 4.3.2. APDU Payload...........................................................................................................
- 4.4. FIS-B Products
   - 4.4.1. Textual METAR and TAF Products ...........................................................................
   - 4.4.2. NEXRAD Graphic Product ........................................................................................
- 4.5. Future Products
- 5. FIS-B PRODUCT APDU DEFINITION .......................................................................
- 5.1. Type 4 NEXRAD Precipitation Image – Global Block Representation.....................
   - 5.1.1. Definition ...................................................................................................................
   - 5.1.2. Assumptions ...............................................................................................................
   - 5.1.3. APDU Payload Format..............................................................................................
   - 5.1.4. FIS-B Graphical Example..........................................................................................
- 5.2. Generic Textual Data Product – Type 2 (DLAC)
   - 5.2.1. Definition ...................................................................................................................
   - 5.2.2. APDU Payload Format..............................................................................................
   - 5.2.3. METAR / TAF Composition .......................................................................................
   - 5.2.4. FIS-B Text Example ...................................................................................................
- 6. CONTROL PANEL INTERFACE ................................................................................
- 6.1. Physical Interface............................................................................................................
- 6.2. Control Messages ............................................................................................................
   - 6.2.1. Call Sign Message......................................................................................................
   - 6.2.2. Mode Message ...........................................................................................................
   - 6.2.3. VFR Code Message....................................................................................................
- FIGURE1-MESSAGESTRUCTURE..................................................................................................... Table of Figures
- FIGURE2-TRAFFICREPORT DATA.................................................................................................
- FIGURE3-COMPOSITION OF THE GROUND UPLINKMESSAGEPAYLOAD.......................................
- TABLE 1-INTERFACE CONNECTIONS................................................................................................ Table of Tables
- TABLE 2-MESSAGESUMMARY........................................................................................................
- TABLE 3-HEARTBEAT MESSAGE(OUTPUT) ...................................................................................
- TABLE 4-INITIALIZATIONMESSAGE(INPUT) .................................................................................
- TABLE 5-UPLINKDATAMESSAGE(OUTPUT) ................................................................................
- TABLE 6-OWNSHIP REPORT MESSAGE(OUTPUT)..........................................................................
- TABLE 7-TRAFFICREPORT MESSAGE(OUTPUT) ...........................................................................
- TABLE 8-TRAFFICREPORT FIELDS................................................................................................
- TABLE 9-MISCELLANEOUS FIELD..................................................................................................
- TABLE 10 - INTEGRITY AND ACCURACY.........................................................................................
- TABLE 11 - EMITTER CATEGORIES..................................................................................................
- TABLE 12 - TRAFFIC REPORT EXAMPLE..........................................................................................
- TABLE 13 - BASICUAT REPORT (OUTPUT) ....................................................................................
- TABLE 14 - LONGUAT REPORT (OUTPUT).....................................................................................
- TABLE 15 - HEIGHTABOVE TERRAIN MESSAGE(INPUT) ................................................................
- TABLE 16 - OWNSHIP GEOALTITUDEMESSAGE(OUTPUT) ............................................................
- TABLE 17 - I-FRAME STRUCTURE...................................................................................................
- TABLE 18 - FRAME TYPES...............................................................................................................
- TABLE 19 - APDU HEADER - NEXRAD GRAPHICS.......................................................................
- TABLE 20 - INTENSITYENCODING OF NEXRAD COMPOSITE REFLECTIVITY PRODUCT.................
- TABLE 21 - SAMPLE BLOCK DECODING..........................................................................................
- TABLE 22 - APDU HEADER -GENERIC TEXT.................................................................................
- TABLE 23 - METAR/TAF STRUCTURE...........................................................................................
- TABLE 24 - CONTROLMESSAGES....................................................................................................
- TABLE 25 - CALLSIGNMESSAGEFORMAT.....................................................................................
- TABLE 26 - MODEMESSAGEFORMAT............................................................................................
- TABLE 27 - MODEFIELD.................................................................................................................
- TABLE 28 - IDENTFIELD.................................................................................................................
- TABLE 29 - EMERGENCY FIELD.......................................................................................................
- TABLE 30 - VFR CODE MESSAGEFORMAT.....................................................................................


Page iv June 5, 2007

**HISTORY OF REVISIONS**

**Part No. Revision Date Description**
560-1058-00 -- 8/23/04 Initial Release.
560-1058-00 A 6/04/2007 Update for GDL 90 Version 2.1 & 2.2 application software.

**ORDERINGINFORMATION**
To receive additional copies of this publication, order part # **560-1058-00 Rev A,** _GDL 90 Data
Interface Specification_.

**OTHERPUBLICATIONS**
RTCA/DO-282A UAT MOPS
RTCA/DO-267A FIS-B MASPS
RTCA/DO-286 TIS-B MASPS
Garmin P/N 560-1049-xx GDL 90 Installation Manual


June 5, 2007 1

## 1. Introduction

## 1.1. Purpose...............................................................................................................................

The purpose of this document is to define the data interface to the serial communication and
control panel ports of the Garmin AT UAT Data Link Sensor, model GDL 90 (P/N 430-6081-
1xx-xxx). The GDL 90 complies with the requirements of this document when configured for the
“Traffic Alert” and "Pass-through" interfaces (see §1.3 for a summary of these interfaces).

## 1.2. Scope...................................................................................................................................

This document describes the format of the serial data sent to and received by the GDL 90. Not
all serial messages defined will necessarily be supported in any given installation of the GDL 90.
Some configurations only have a subset of these messages. See the GDL 90 Installation Manual
for the configuration options.

The control panel interface is included in this document. Information on altitude sources can be
found in the GDL 90 Installation Manual.

For the purposes of this document, the device to which the GDL 90 is attached is assumed to be a
multi-function display, and is referred to here as “the Display” or “MFD” interchangeably.

Certain features described in this document apply only to specific GDL 90 software versions.
GDL 90 units are marked on the configuration label with SW Mod Level. Features that apply to
certain version of GDL 90 are identified by the text “ **SW Mod x** ”, where ‘ **x** ’ is replaced with the
appropriate level. Unless otherwise stated, the specifications apply to **SW Mod B** only.

**Summary of SW Mod Levels:**

```
SW Mod B = Ver 2.0 (supports the Public IC)
SW Mod C = Ver 2.1 (adds Ownship Geometric Altitude, additional status bits)
SW Mod D = Ver 2.2. (converts TIS-B call sign ‘dash’ to ‘space’ for less display clutter)
```
## 1.3. Interface Types..................................................................................................................

This specification describes two types of interfaces to the Display. The type of interface being
used is specified by the GDL 90 installation configuration.

The first is the “Traffic Alert” interface. When enabled by the GDL 90 configuration, this
interface provides conflict alerts for proximate traffic that are projected to enter the protected
zone surrounding the ownship position.

The second interface is the “Pass-through” interface. This interface does not provide conflict
alerts. The output reports under this interface consist of the message payloads that are received
over the UAT data link, without modification. Due to constraints on the interface bandwidth,
received UAT messages are filtered by range from ownship.

See Table 2 for a listing of which Messages the GDL 90 uses for each of these interface types.


Page 2 June 5, 2007

## 1.4. Disclaimer for Display Vendors.......................................................................................

Manufacturers of display devices that use the information contained in this document for
interface to the GDL 90 UAT transceiver are required to ensure that their display devices show
the following message every time such display device is turned on or activated. This message
may not be altered, changed, or abbreviated.

Traffic and weather information displayed is advisory only; it is the pilot’s responsibility to see
and avoid traffic and to determine the weather conditions. You assume total responsibility and
risk associated with using all such information. You agree with and accept the content of this
disclaimer by using this equipment.

## 1.5. DISCLAIMER; NO WARRANTY; LIMITATION OF LIABILITY

#### ALL TRAFFIC AND WEATHER INFORMATION MADE AVAILABLE THROUGH

#### USE OF THE GDL 90 IS ADVISORY ONLY. IT IS THE PILOT’S RESPONSIBILITY

#### TO SEE AND AVOID TRAFFIC AND TO DETERMINE THE WEATHER

#### CONDITIONS. ALL SUCH INFORMATION IS DEEMED RELIABLE BUT IS NOT

#### GUARANTEED AND SHOULD BE INDEPENDENTLY VERIFIED. THE GDL 90

#### CANNOT, AND DOES NOT, VERIFY THE INFORMATION TRANSMITTED OR

#### DISPLAYED. THE USER ASSUMES TOTAL RESPONSIBILITY AND RISK

#### ASSOCIATED WITH USING ALL SUCH INFORMATION.

#### USE OF THIS DOCUMENT IS AT THE USER’S SOLE RISK. THIS DOCUMENT IS

#### PROVIDED ON AN “AS IS” AND “AS AVAILABLE” BASIS. TO THE MAXIMUM

#### EXTENT PERMITTED BY APPLICABLE LAW, GARMIN AT AND ITS

#### AFFILIATES EXPRESSLY DISCLAIM ALL WARRANTIES AND CONDITIONS,

#### WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT NOT

#### LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR

#### A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT OF THIRD

#### PARTY RIGHTS. GARMIN AT AND ITS AFFILIATES DO NOT MAKE ANY

#### WARRANTY WITH REGARD TO THIS DOCUMENT AND THE INFORMATION

#### CONTAINED THEREIN. NEITHER GARMIN AT NOR ITS AFFILIATES

#### WARRANT THAT THIS DOCUMENT WILL MEET ANY USER’S NEEDS OR

#### REQUIREMENTS, OR THAT ANY DEVICE CAN BE MADE TO INTERFACE

#### WITH THE GDL 90, OR THAT THE INFORMATION CONTAINED IN THIS

#### DOCUMENT IS ERROR-FREE, OR THAT DEFECTS WILL BE CORRECTED.

#### SOME JURISDICTIONS DO NOT ALLOW LIMITATIONS ON IMPLIED

#### WARRANTIES, SO THE ABOVE LIMITATIONS MAY NOT APPLY TO YOU AND

#### YOU MAY HAVE OTHER LEGAL RIGHTS THAT VARY BY JURISDICTION.


June 5, 2007 Page 3

#### IN NO EVENT SHALL GARMIN AT OR ITS AFFILIATES BE LIABLE FOR ANY

#### SPECIAL, INCIDENTAL, CONSEQUENTIAL, INDIRECT, EXEMPLARY OR

#### PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION LOSS OF USE,

#### PROFITS, REVENUE OR DATA, HOWEVER CAUSED AND ON ANY THEORY OF

#### LIABILITY, EVEN IF GARMIN AT AND/OR ITS AFFILIATES HAS/HAVE BEEN

#### SPECIFICALLY ADVISED IN ADVANCE OF THE POSSIBILITY OF SUCH

#### DAMAGES. REGARDLESS OF THE FORM OF THE DAMAGE, THE ONLY

#### LIABILITY GARMIN AT OR ITS AFFILIATES WILL HAVE TO LICENSEE OR

#### ANY OTHER PERSON WILL BE LIMITED TO $100. THESE DAMAGE

#### LIMITATIONS SHALL APPLY NOTWITHSTANDING ANY FAILURE OF

#### ESSENTIAL PURPOSE OF ANY LIMITED REMEDY. BECAUSE SOME STATES

#### AND JURISDICTIONS DO NOT ALLOW THE EXCLUSION OR LIMITATION OF

#### LIABILITY, THE ABOVE LIMITATIONS MAY NOT APPLY TO YOU.

## 1.6. Glossary

ADS-B : Automatic Dependant Surveillance - Broadcast

CSA : Conflict Situational Awareness.

FIS-B : Flight Information System - Broadcast

MASPS : Minimum Aviation System Performance Specifications

MOPS : Minimum Operational Performance Specifications

TIS-B : Traffic Information System - Broadcast

UAT : Universal Access Transceiver


Page 4 June 5, 2007

## 2. RS-422 BUS MESSAGE STRUCTURE ..........................................................................

## 2.1. Physical Interface..............................................................................................................

The GDL 90 supports a bi-directional asynchronous communication interface using RS-
signaling. The communication port is configured for the following characteristics:

```
Baud Rate: 38,400 (nominal)
Start Bits: 1
Data length: 8 bits
Stop Bits: 1
Parity: None
Flow Control: None
```
Electrically, RS-422 uses a differential signal pair driven from a single +5.0 volt supply. The two
signals of the pair are referred to as ‘A’ and ‘B’. The Mark (or ONE) condition is indicated by
the ‘A’ signal being at a higher voltage than the ‘B’ signal.

**Bit and Byte order:**

By convention, asynchronous serial communication transmits byte-wise data over the interface
with the least-significant bit first, immediately following the Start bit. The most significant bit is
followed by the Stop bit.

In this document, the least significant bit of a byte is referred to as Bit 0, carries a weight of

(^1) (decimal), and is depicted as the right-most bit. The most-significant bit of a byte is referred to as
Bit 7, carries a weight of 128(decimal), and is depicted as the left-most bit.
In this document, use of hexadecimal notation is indicated by preceding the data with the
characters "0x--". The leftmost character represents the 4 most significant bits.
**Electrical Connections:**
The electrical connections to the GDL 90 RS-422 port are shown in Table 1.
**Table 1 - Interface Connections
Signal Name Direction Connector Pin**
Tx-A Out of GDL 90 J2 - Pin 11
Tx-B Out of GDL 90 J2 - Pin 29
Rx-A Into GDL 90 J2 - Pin 10
Rx-B Into GDL 90 J2 - Pin 28


June 5, 2007 Page 5

## 2.2. Message Structure Overview

The datalink message structure is based on "Async HDLC", as described in RTCA/DO-
(Section 3.4.3.2). Certain modifications have been made where appropriate for the intended
application. Since the UAT datalink is intended for broadcast services only, an avionics datalink
interface need support only a datagram service, with no provisions for addressed or connected
modes of communication. These modifications serve to optimize the avionics data interface for
simplicity and data flow efficiency.

### 2.2.1. Datalink Structure and Processing ..............................................................................

The basic message structure is as follows (see Figure 1):
1) A Flag Byte character (0x7E).
2) A one-byte Message ID which specifies the type of message being transmitted.
3) The Message Data, which can be of variable lengths.
4) A message Frame Check Sequence (FCS). The FCS is a 16-bit CRC with the least significant byte
first.
5) Another Flag Byte character (0x7E).

```
Figure 1 - Message Structure
```
Binary transparency is provided by use of the "byte-stuffing" technique. To include a data byte
that coincides with either a Flag Byte (0x7E) or Control-Escape character (0x7D) within a
message, each is converted into a unique two-byte sequence.

To prepare a message for transmission, wherever a 0x7D or 0x7E byte is found in between the
two Flag Bytes, a Control-Escape character is inserted, followed by the original byte XOR’ed
with the value 0x20. Using this method, the Control-Escape and Flag Byte characters only
appear in a message for framing or byte-stuffing purposes.

On reception, any Control-Escape characters found are discarded, and the following byte is
included in the message after being converted to its original form by XOR’ing with the value
0x20.

For example:
start of message ID #2 with second byte 0x7E: “0x7E 0x02 0x7D 0x5E ...”
start of message ID #3 with second byte 0x7D: “0x7E 0x03 0x7D 0x5D ...”
end of message with CRC value of 0x7D 0x7E: “...0x7D 0x5D 0x7D 0x5E 0x7E”

Note that on transmit, the FCS must be calculated on the message data prior to the byte-stuffing
process. Similarly, on reception the byte-stuffing must be removed prior to checking the FCS.

The steps to construct a message for transmission are as follows:
1) Assemble the message with the Message ID byte included.
2) Calculate the FCS and append it to the end of the message (least significant byte first).


Page 6 June 5, 2007

```
3) Find all of the Control-Escape and Flag Byte characters in the message and make the conversion.
4) Frame the message by adding Flag Byte characters to the beginning and the end of the message.
```
If two messages are being sent back-to-back, it is necessary to have two Flag Bytes in a row.
Several messages sent in sequence should appear as:

“0x7E <message1> 0x7E 0x7E <message2> 0x7E ... 0x7E <messageN> 0x7E”

The steps for message reception are as follows:
1) Look for a Flag Byte character.
2) Save all characters until another Flag Byte character is received.
3) Look for all Control-Escape characters in the saved string. Discard each one found, and XOR the
following character with 0x20. The resulting character should equal either 0x7D or 0x7E.
4) Calculate the FCS on the clear message– not including the Start Flag, End Flag, or the FCS itself. The
calculated FCS should match the FCS characters in the message. If not, discard the message.
5) The message has been authenticated and is ready for use.

### 2.2.2. Message ID ..................................................................................................................

In order to provision for future inclusion of a data link address field, the Message ID is
represented by the 7 least-significant bits of the byte immediately following the initial Flag byte.
In equipment that complies with this version of this interface document, the most significant bit
of the Message ID will always be ZERO, so that the Message ID can be treated as an 8-bit value
with a range of 0-127 (decimal). Any messages that have a Message ID outside of this range
should be discarded.

Within this document, Message IDs are stated in decimal notation.


June 5, 2007 Page 7

### 2.2.3. FCS Calculation...........................................................................................................

The FCS used in this interface is a CRC-CCITT. For processing efficiency, a table-generated
CRC calculation can be used. This table contains 256 elements. The table should be calculated
at startup and left unchanged afterward. The following C code shows one method the table can
be constructed. “Crc16Table” is an unsigned 16-bit integer array of 256 elements. An “int” is a
16-bit integer. A “long int” is a 32-bit integer.

void crcInit( void )
{
unsigned int i, bitctr, crc;
for (i = 0; i < 256; i++)
{
crc = (i << 8);
for (bitctr = 0; bitctr < 8; bitctr++)
{
crc = (crc << 1) ^ ((crc & 0x8000)? 0x1021 : 0);
}
Crc16Table[i] = crc;
}
}

The actual calculation of the CRC can be accomplished using the following function.

unsigned int crcCompute( // Return – CRC of the block
unsigned char *block, // i – Starting address of message
unsigned long int length, // i – Length of message
)
{
unsigned long int i;
unsigned int crc = 0;

for (i = 0; i < length; i++)
{
crc = Crc16Table[crc >> 8] ^ (crc << 8) ^ block[i];
}

return crc;
}

### 2.2.4. Message Example.........................................................................................................

The byte sequence [0x7E 0x00 0x81 0x41 0xDB 0xD0 0x08 0x02 0xB3 0x8B 0x7E] represents
a Heartbeat message including the Flags and the CRC value.


Page 8 June 5, 2007

## 2.3. Bandwidth Management

The GDL 90 implements a method of managing the use of the data interface bandwidth. This is
necessary because the UAT data link is capable of more throughput than the interface to the
Display can provide. The bandwidth management method is described below:

The GDL 90 application software limits the use of the data interface to 90% of the maximum
capacity. For example, with 38400 baud, and 10 bauds per byte (1 start + 8 data + 1 stop), this
gives 3,840 bytes per second. Ninety percent of this value is approximately 3,500 bytes per
second.

The 10% margin allows for some excess capacity for the byte-stuffing provisions of the datalink
interface, and acquisition of new target tracks.

Within this 90% limit, the GDL 90 will output the following messages:

```
x one Heartbeat message per second,
x followed by the Ownship report,
x followed by any Traffic Alert reports (if enabled),
x followed by a number of Uplink messages (configurable, maximum of 0 to 4 per second),
x followed by proximate Traffic reports,
x followed by additional Uplink messages (if extra bandwidth capacity is available).
```
The proximate Traffic reports are prioritized on the interface by range proximity to the ownship
position. Proximate Traffic reports can be either for non-alert targets when the “Traffic Alert”
interface is in use, or are normal targets when the “Pass-through” interface is in use.

The Uplink messages that are output first are those received from the most proximate ground
stations. If more than one Uplink message is received from the same ground station, priority is
given to the messages received in the earliest time slots. Since the ground stations rotate their
time slot usage every second, all co-located time slots are given equal service.

Note that only Uplink messages marked in the UAT Specific Header (see §4.1.1) as containing
valid application data are eligible to be output.

Certain parameters of the Bandwidth Management method (e.g. the number of Uplinks per
second) can be customized for a given installation through the GDL 90 configuration process.


June 5, 2007 Page 9

## 3. MESSAGE DEFINITIONS...............................................................................................

There are several different types of messages that may be passed on the data interface. The
following tables describe the possible message formats. The sections that follow give definitions
of the report contents, and recommendations for the use of these messages by the Display.

In general, multi-byte fields are transmitted most-significant byte first, unless otherwise stated.

Table 2 presents a summary of the messages defined in this section, and for which interface
types the messages are supported. The Message ID is used as defined in Section 2.2.1. The
GDL 90 is configured at installation for which type of interface is in use.

## TABLE 2-MESSAGESUMMARY........................................................................................................

```
Message ID & Name I/O
Traffic Alert
Interface
```
```
Pass-Through
Interface
```
**Section
Reference**
010 - Heartbeat Out Yes Yes §3.
210 - Initialization In Yes Yes §3.
710 - Uplink Data Out Yes Yes §3.
910 - Height Above Terrain In Yes _(see note)_ §3.
1010 - Ownship Report Out Yes Yes §3.
1110 - Ownship Geometric
Altitude
Out Yes Yes §3.

2010 - Traffic Report Out Yes - §3.
3010 - Basic Report Out - Yes §3.
3110 - Long Report Out - Yes §3.

_Note: The Height Above Terrain message is not used with the Pass-through interface._

The message directions “In” and “Out” are with respect to the GDL 90. The following sections
define and discuss each message in detail.


Page 10 June 5, 2007

## 3.1. Heartbeat Message..........................................................................................................

The GDL 90 outputs a Heartbeat message at the beginning of each UTC second. The message
format is given in Table 3, and discussed further in the remainder of this section.

## TABLE 3-HEARTBEAT MESSAGE(OUTPUT) ...................................................................................

```
Byte # Name Size Value
1 Message ID 1 0 10 = Heartbeat
2 Status Byte 1
Bit 7: GPS Pos Valid
Bit 6: Maint Req'd
Bit 5: IDENT
Bit 4: Addr Type
Bit 3: GPS Batt Low
Bit 2: RATCS
Bit 1: reserved
Bit 0: UAT Initialized
```
#### 1

```
1 = Position is available for ADS-B Tx
1 = GDL 90 Maintenance Req'd
1 = IDENT talkback
1 = Address Type talkback
1 = GPS Battery low voltage
1 = ATC Services talkback
```
-
1 = GDL 90 is initialized
3 Status Byte 2
Bit 7: Time Stamp
(MS bit)
Bit 6: CSA Requested
Bit 5: CSA Not Available
Bit 4: reserved
Bit 3: reserved
Bit 2: reserved
Bit 1: reserved
Bit 0: UTC OK

#### 1

- Seconds since 0000Z, bit 16

```
1 = CSA has been requested
1 = CSA is not available at this time
```
-
-
-
-
1 = UTC timing is valid
4-5 Time Stamp 2

```
Seconds since 0000Z, bits 15-
(LS byte first)
6-7 Message Counts 2 See §3.1.
```
```
Total Length 7
```
The Heartbeat message provides real-time indications to the Display of the status and operation
of the GDL 90. The Heartbeat message is sent once per second in response to the UTC timing
reference signal. The Time Stamp field provides the absolute time reference in integer seconds
for the Traffic reports that follow it during the remainder of this second.

Each of the fields is described below:

### 3.1.1. Status Byte 1...............................................................................................................

```
a) Bit 7: GPS Position Valid: This bit is set to ONE by the GDL 90 when it has a valid position
fix that is being included in its transmitted ADS-B messages. MFD Recommendation:
Annunciate to the flight crew when this bit is ZERO, since it indicates that no valid ownship
data is being transmitted to other participants.
```

June 5, 2007 Page 11

```
b) Bit 6: Maintenance Required: This bit is set to ONE when the GDL 90 has detected a
problem that requires maintenance. MFD Recommendation: Post a message to the flight
crew when this bit is ONE, to indicate that maintenance is required.
```
```
c) Bit 5: IDENT talkback: This bit is set to ONE when the GDL 90 has set the IDENT
indication in its transmitted ADS-B messages. This provides feedback to the display when
the IDENT function has been activated from the control source.
```
```
d) Bit 4: SW Mod C: Address Type: This talkback bit is set to ONE to indicate that the GDL 90
is transmitting ADS-B messages using a temporary self-assigned (“anonymous”) address.
This provides feedback to the display regarding which type of ownship identity is being
transmitted.
```
```
If SW Mod C is not installed, this bit is undefined and is always set to ZERO.
```
```
e) Bit 3: GPS Battery Low: This bit is set to ONE to indicate that the GDL 90 needs
maintenance to replace its internal GPS battery. The GDL 90 continues to be capable of
normal operation, except that the time for initial GPS acquisition will be much longer than
normal.
```
```
f) Bit 2: SW Mod C: RATCS: This talkback bit is set to the present state of the Receiving ATC
Services indication in the transmitted ADS-B messages. This provides feedback to the display
regarding whether the RATCS feature is enabled and operating.
```
```
If SW Mod C is not installed, this bit is undefined and is always set to ZERO.
```
```
g) Bit 1: Reserved: This bit is set to ZERO in equipment that complies with this version of the
specification.
```
```
h) Bit 0: UAT Initialized: This bit is set to ONE in all Heartbeat messages.
```
### 3.1.2. Status Byte 2...............................................................................................................

```
a) Bit 7: UAT Time Stamp - Bit 16: This is the Most Significant Bit of the UAT Time Stamp,
in seconds elapsed since UTC midnight (0000Z).
```
```
b) Bit 6: CSA Requested: When set to ONE, this bit acknowledges to the Display that the GDL
90 Conflict Situational Awareness (CSA) algorithm has been requested. See §3.2.2 for
reference.
```
```
c) Bit 5: CSA Not Available: When set to ONE, this bit indicates to the Display that the CSA
algorithm has been requested but is not available.
```
```
MFD Recommendation: Annunciate changes in the CSA operational status to the flight crew,
including but not limited to the case where CSA has been requested but is not available.
```
```
d) Bit 4..1: Reserved: These bits are set to ZERO in equipment that complies with this version
of the specification.
```
```
e) Bit 0: UTC OK: This bit is set to ONE when the GDL 90 is using a valid UTC timing
reference.
```

Page 12 June 5, 2007

### 3.1.3. UAT Time Stamp ........................................................................................................

The Heartbeat message includes the current time-of-day in whole seconds elapsed since UTC
midnight (0000Z). This requires a 17-bit data field. The most significant bit (bit 16) is in Status
Byte 2 bit 7. The remaining 16 bits are conveyed least significant byte first, using the two Time
Stamp bytes.

### 3.1.4. Received Message Counts..........................................................................................

Two bytes are used to report the number of UAT messages received by the GDL 90 during the
previous second. The count fields are formatted as follows:

```
a) Uplink receptions: Bits 7..3 of the first Message Count byte contain the count of Uplink
Messages received. Bit 7 is the most significant bit.
```
```
b) Reserved: Bit 2 of the first Message Count byte is reserved, and is set to ZERO.
```
```
c) Basic and Long receptions: The total number of Basic and Long messages together is
contained in a 10-bit field. The two most significant bits are in Bit 1..0 of the first Message
Count byte, and the eight least significant bits are contained in the second Message Count
byte. The counter value will hold at the maximum value if the number of received messages
exceeds 1,023.
```
These counters represent all of the UAT messages that have been successfully received and
validated, regardless of whether they result in an output report on the GDL 90 interfaces.

Example:
If 4 Uplink messages and a total of 567 Basic and Long messages were received in the previous second, the
Heartbeat message Byte 6 value will be 0x22, and the Byte 7 value will be 0x37.


June 5, 2007 Page 13

## 3.2. Initialization Message

The Init message is sent by the Display once per second, and is described in Table 4.

## TABLE 4-INITIALIZATIONMESSAGE(INPUT) .................................................................................

```
Byte # Name Size Value
1 Message ID 1 2 10 = Initialization
2 Configuration Byte 1
Bit 7: reserved
Bit 6: Audio Test
Bit 5: reserved
Bit 4: reserved
Bit 3: reserved
Bit 2: reserved
Bit 1: Audio Inhibit
Bit 0: CDTI OK
```
#### 1

-
1 = Initiate audio test
-
-
-
-
1 = Suppress GDL 90 audio output
1 = CDTI capability is operating
3 Configuration Byte 2
Bit 7: reserved
Bit 6: reserved
Bit 5: reserved
Bit 4: reserved
Bit 3: reserved
Bit 2: reserved
Bit 1: CSA Audio Disable
Bit 0: CSA Disable

#### 1 - - - - - -

```
1 = Disable GDL 90 audible traffic alerts
1 = Disable CSA traffic alerting
Total Length 3
```
The Init message provides the GDL 90 with various control signals.

### 3.2.1. Configuration Byte 1..................................................................................................

Configuration Byte 1 provides the following control signals.

```
a) Bits 7, 5, 4, 3, 2: These bits are reserved for future use, and should be set to ZERO by the
Display.
```
```
b) Bit 6: Audio Test: This bit is set to ONE to invoke the “PlayAudio” test as described in the GDL
90 Installation Manual.
```
```
c) Bit 1: Audio Inhibit: This bit is set to ONE when the GDL 90 audio output is inhibited. This
function is similar to the Audio Inhibit discrete input (see the GDL 90 Installation Manual).
```
```
d) Bit 0: CDTI OK: This bit is set to ONE by the Display when a cockpit traffic display (CDTI)
function is available. This bit is included in the GDL 90 transmitted ADS-B messages, for use by
other participants as appropriate.
```

Page 14 June 5, 2007

### 3.2.2. Configuration Byte 2..................................................................................................

Configuration Byte 2 provides control of the GDL 90 traffic alerting functions.

```
a) Bits 7..2: These bits are reserved for future use, and should be set to ZERO by the Display.
```
```
b) Bit 1: CSA Audio Disable: This bit is set to ONE by the Display when the flight crew elects to
suppress the audio traffic alerts generated by the CSA algorithm.
```
```
c) Bit 0: CSA Disable: This bit is set to ONE by the Display when the flight crew elects to turn off
the generation of all traffic alerts by the CSA algorithm.
```

June 5, 2007 Page 15

## 3.3. Uplink Data Message

Uplink messages received from UAT Ground Broadcast Transceivers are reported to the Display
using the Uplink Data message, as described in Table 5.

## TABLE 5-UPLINKDATAMESSAGE(OUTPUT) ................................................................................

```
Byte # Name Size Value
1 Message ID 1 7 10 = Uplink Data
```
```
2-4 Time of Reception 3
```
```
24-bit binary fraction
Resolution = 80 nsec
5-436 Uplink Payload 432 See §3.3.2
```
```
Total Length 436
```
The Uplink message provides the Display with the Time of Reception value, followed by the
entire contents of the Uplink message received over the air.

Note that the Uplink message must be marked as containing valid Application Data in order to be
output to the Display by the GDL 90. Refer to §4.1.1 "UAT-Specific Header" for more
information.

### 3.3.1. Time of Reception (TOR) ...........................................................................................

The TOR is a 24-bit value, with a resolution of 80 nanoseconds. The valid range is 0 to 1 second
(values 0 10 through 12,499,999 10 ). The TOR is conveyed as three bytes, with the least significant
byte transmitted first.

A TOR of "all ONES" (0xFFFFFF, or 16,777,215 10 ) indicates that the TOR value is not valid
(i.e. the ownship GDL 90 does not have sufficient timing accuracy to output a useful time value).

The complete Time of Applicability of a message is determined by combining the Time Stamp
from the Heartbeat message (which gives the integer seconds since UTC midnight), with the
seconds fraction found in the TOR field of the report.

**3.3.2. Uplink Payload**

The Uplink Data consists of the entire contents of the Uplink message received over the air. As
defined by RTCA/DO-282, the Uplink message consists of the UAT-Specific Header (8 bytes),
followed by 424 bytes of generic binary data. See §4 "Uplink Payload Format" for further
specifications of the Uplink Payload field contents.


Page 16 June 5, 2007

## 3.4. Ownship Report Message...............................................................................................

The GDL 90 will always output an Ownship Report message once per second. The message
uses the same format as the Traffic Report, with the Message ID set to the value 10 (See Table
6). See §3.5.1 for specification of the Traffic Report field.

## TABLE 6-OWNSHIP REPORT MESSAGE(OUTPUT)..........................................................................

```
Byte # Name Size Value
1 Message ID 1 10 10 = Ownship Report
```
```
2 - 28
Ownship
Report
27 See §3.5.1
```
```
Total Length 28
```
The Ownship Report is output by the GDL 90 regardless of whether a valid GPS position fix is
available. If the ownship GPS position fix is invalid, the Latitude, Longitude, and NIC fields in
the Ownship Report all have the ZERO value.

Ownship geometric altitude is provided in a separate message ( **SW Mod C** ).

## 3.5. Traffic Report..................................................................................................................

When the Traffic Alert interface is in use, a Traffic Report message is output from the GDL 90
in each second for each alerted or proximate target. The Traffic Report message is defined in
Table 7. Reports are output for at least 32 targets, up to the maximum number that the interface
can support (depending on the baud rate and the Uplink configuration).

## TABLE 7-TRAFFICREPORT MESSAGE(OUTPUT) ...........................................................................

```
Byte # Name Size Value
1 Message ID 1 20 10 = Traffic Report
2 - 28 Traffic Report 27 See §3.5.1
Total Length 28
```
All Traffic Reports output from the GDL 90 have a Time of Applicability of the beginning of the
current second. Therefore, there is no explicit Time of Reception field in the Traffic Report. The
Time Stamp conveyed in the most recent Heartbeat message is the Time of Applicability for all
Traffic Reports output in that second.

A Traffic Report is generated for each tracked target every second, as long as the target is
identified by CSA as a priority target. If no ADS-B message is received for a tracked target, an
extrapolated report is generated for that target. Each target is extrapolated until its track is
discontinued by CSA.


June 5, 2007 Page 17

### 3.5.1. Traffic and Ownship Report Data Format.................................................................

The Traffic Report data consists of 27 bytes of binary data as shown in Figure 2. Each field that
makes up the report is a multiple of 4 bits. Each lower case character represents a 4-bit value.
Each pair of lower-case characters represents a single byte value.

For example, Byte 2 of this message is the first byte of the Traffic Report data, and contains the
value "0xst", where "s" represents the Traffic Alert Status and occupies Byte 2 bits 7..4, and 't'
represents the Address Type and occupies Byte 2 bits 3..0. Similarly, Byte 28 contains the value
"0xpx".

## FIGURE2-TRAFFICREPORT DATA.................................................................................................

**Traffic Report data = st aa aa aa ll ll ll nn nn nn dd dm ia hh hv vv tt ee cc cc
cc cc cc cc cc cc px**

Table 8 defines the Traffic Report fields. In the descriptions that follow, all fields are encoded
with the most significant digit first unless otherwise noted. See §3.5.2 for an example that
illustrates the byte packing and ordering.


Page 18 June 5, 2007

## TABLE 8-TRAFFICREPORT FIELDS................................................................................................

**Field Definition**

s Traffic Alert Status. s = 1 indicates that a Traffic Alert is active for this target.

t Address Type: Describes the type of address conveyed in the Participant Address
field:

aa aa aa Participant Address (24 bits).

ll ll ll Latitude: 24-bit signed binary fraction. Resolution = 180 / 2^23 degrees.

nn nn nn Longitude: 24-bit signed binary fraction. Resolution = 180 / 2^23 degrees.

ddd Altitude: 12-bit offset integer. Resolution = 25 feet.
Altitude (ft) = ("ddd" * 25) - 1,000

m Miscellaneous indicators: (see text)

i Navigation Integrity Category (NIC):

a Navigation Accuracy Category for Position (NACp):

hhh Horizontal velocity. Resolution = 1 kt.

vvv Vertical Velocity: Signed integer in units of 64 fpm.

tt Track/Heading: 8-bit angular weighted binary. Resolution = 360/256 degrees.
0 = North, 128 = South. See Miscellaneous field for Track/Heading indication.

ee Emitter Category

cc cc cc cc

cc cc cc cc

```
Call Sign: 8 ASCII characters, '0' through '9' and 'A' through 'Z'.
```
p Emergency/Priority Code:

x Spare (reserved for future use)

**3.5.1.1 TRAFFICALERT STATUS**

This is a 4-bit field "s" which indicates whether CSA has identified this target with an alert. The
following values for this field are defined:
s = 0 : No alert
s = 1 : Traffic Alert
s = 2 through 15 : reserved
MFD Recommendation: The Display should depict targets for which a Traffic Alert exists
using a flashing yellow traffic symbol.
Traffic Annunciation: An increase in the number of targets that are in the Traffic Alert status
should cause an audible annunciation.


June 5, 2007 Page 19

**3.5.1.2 TARGETIDENTITY**

The identity of a target is formed by the combination of the Address Type “t” along with the
Participant Address "aaaaaa". Together these form a 28-bit field that uniquely identifies a given
ADS-B or TIS-B participant. The Address Types are defined as follows:
t = 0 : ADS-B with ICAO address
t = 1 : ADS-B with Self-assigned address
t = 2 : TIS-B with ICAO address
t = 3 : TIS-B with track file ID.
t = 4 : Surface Vehicle
t = 5 : Ground Station Beacon
t = 6-15 : reserved

MFD Recommendation: The Display should determine the appropriate style of traffic symbol
for a target by using a combination of Address Type, Emitter Category, NIC value, Air/Ground
state, and Traffic Alert status.

MFD Recommendation: The uniqueness of the Target Identity depends primarily on the
equipment installer configuring the ADS-B equipment with the correct ICAO address. For TIS-
B targets, uniqueness also depends on the ability of the ground-based TIS-B processor to fuse
radar and ADS-B reports into track file IDs accurately. Neither of these processes can be
expected to always generate a unique identification. Therefore, Display vendors are advised to
take appropriate measures to cope with the possibility that the Target Identity alone may not
always be sufficient to uniquely identify duplicate targets. This caution includes the possibility
of reception of an ownship “shadow” TIS-B target.

**3.5.1.3 LATITUDE AND LONGITUDE**

The "'llllll" and "nnnnnn"' values represent the Latitude and Longitude values in 24-bit
"semicircle" 2-s compliment units. Latitude and Longitude are both encoded over a range of +/-
180 degrees. This provides a resolution of approximately 2.14577 x 10-5 degrees (approximately
2.38 meters at the equator). The data is presented most significant bit first.

For Latitude, North is considered Positive. The maximum Latitude value is +90.0 degrees. The
minimum Latitude value is -90.0 degrees.

For Longitude, East is considered Positive. The maximum Longitude value is +(180 minus
LSB) degrees. The minimum Longitude value is -180.0 degrees.

A target with no valid position has Latitude, Longitude, and NIC all set to zero.

Examples:
00.000 N or E degrees 0x00 00 00
00.000 + LSB N or E degrees 0x00 00 01
00.000 - LSB S or W degrees 0xFF FF FF
45.000 N or E degrees 0x20 00 00
45.000 S or W degrees 0xE0 00 00
90.000 E or N 0x40 00 00
-180.000 degrees 0x80 00 00
Max Longitude (+180 - LSB) 0x7F FF FF


Page 20 June 5, 2007

**3.5.1.4 ALTITUDE**

The Altitude field "ddd" contains the pressure altitude (referenced to 29.92 inches Hg), encoded
using 25-foot resolution, offset by 1,000 feet. The 0xFFF value represents that the pressure
altitude is invalid. The minimum altitude that can be represented is -1,000 feet. The maximum
valid altitude is +101,350 feet.

Examples:
-1,000 feet 0x000
0 feet 0x028
+1000 feet 0x050
+101,350 feet 0xFFE
Invalid or unavailable 0xFFF

MFD Recommendation: An invalid altitude should be depicted on the Display as the altitude
field being dashed-out. The target altitude should support display of the target altitude as either
absolute altitude, or altitude relative to the ownship.

**3.5.1.5 MISCELLANEOUS INDICATORS**

This 4-bit field "m" presents the following indicator bits that apply to the Traffic Report. See
Table 9. Bits 1 and 0 describe the type of data conveyed in the "tt" field. Bit 2 describes whether
the report is updated from an ADS-B message reception, or is extrapolated from a previous
report. Bit 3 gives the Air/Ground state of the traffic.

## TABLE 9-MISCELLANEOUS FIELD..................................................................................................

```
Bit 3 Bit 2 Bit 1 Bit 0 Meaning
```
- - 0 0 "tt" not valid
- - 0 1 "tt" = True Track Angle
- - 1 0 "tt" = Heading (Magnetic)
- - 1 1 "tt" = Heading (True)
- 0 - - Report is updated
- 1 - - Report is extrapolated
0 - - - On Ground
1 - - - Airborne

**3.5.1.6 INTEGRITY(NIC) AND ACCURACY (NACP)**

The Integrity and Accuracy of the traffic is reported using a 4-bit value for each field. See Table

10. At the transmitting source, NIC is encoded by the Containment Radius (typically HPL).
NACp is encoded using the Estimated Position Uncertainty (typically HFOM).


June 5, 2007 Page 21

## TABLE 10 - INTEGRITY AND ACCURACY.........................................................................................

```
Value
("i" or "a")
```
#### NIC

```
(HPL)
```
```
NACp
(HFOM)
0 Unknown Unknown
1 < 20.0 NM < 10.0 NM
2 < 8.0 NM < 4.0 NM
3 < 4.0 NM < 2.0 NM
4 < 2.0 NM < 1.0 NM
5 < 1.0 NM < 0.5 NM
6 < 0.6 NM < 0.3 NM
7 < 0.2 NM < 0.1 NM
8 < 0.1 NM < 0.05 NM
```
#### 9

```
HPL < 75 m and
VPL < 112 m
```
```
HFOM < 30 m and
VFOM < 45 m
```
#### 10

```
HPL < 25 m and
VPL < 37.5 m
```
```
HFOM < 10 m and
VFOM < 15 m
```
#### 11

```
HPL < 7.5 m and
VPL < 11 m
```
```
HFOM < 3 m and
VFOM < 4 m
12-15 Unused Unused
```
```
Note: See DO-282A Table 2-15 and Table 2-45 for the full definition of the NIC and NACp values.
```
MFD Recommendation: Targets with either a NIC or NACp value that is 4 or lower (HPL >=
1.0 NM, or HFOM >= 0.5 NM) should be depicted using an icon that denotes a degraded target.

**3.5.1.7 HORIZONTAL VELOCITY**

Horizontal velocity "hhh" is encoded as a 12-bit unsigned value, in units of 1 knot. The direction
of the velocity is given by the "tt" field (see §3.5.1.9). If the horizontal velocity is 4,094 knots
or greater, the value will hold at the value 0xFFE.

Special Values: The value 0xFFF is reserved to convey that no horizontal velocity information
is available.

**3.5.1.8 VERTICALVELOCITY**

Vertical velocity "vvv" is encoded as a 12-bit signed value, in units of 64 feet per minute (FPM).
The range that can be encoded is +/- 32,576 FPM. If the vertical velocity exceeds +/- 32,576
FPM the value will hold at the value that represents +/- 32,640 FPM.


Page 22 June 5, 2007

Special Values: The value 0x800 is reserved to convey that no vertical velocity information is
available. The values 0x1FF through 0x7FF and 0x801 through 0xE01 are not used.

Examples:
0 = 0 FPM
0x001 = 64 FPM climb
0xFFF = 64 FPM descend
0x1FD = 32,576 FPM climb
0x1FE = > 32,576 climb
0xE03 = 32,576 FPM descend
0xE02 = > 32.576 FPM descend
0x800 = no vertical rate available

**3.5.1.9 TRACK/HEADING**

The Track/Heading field "tt" provides an 8-bit angular weighted value. The resolution is in units
of 360/256 degrees (approximately 1.4 degrees).

```
Note: Typically, all airborne targets report True Track. Targets on the ground can
report either Track (if no heading sensor is present and the aircraft is in motion), or
Heading (if equipped with a heading sensor).
```
MFD Recommendation: The "tt" field provides the directionality of the traffic. When this field
is Not Valid (see §3.5.1.5) the traffic should be depicted using a non-directional icon. Typically
this would occur with a stationary aircraft that does not have a heading source.


June 5, 2007 Page 23

**3.5.1.10 EMITTERCATEGORY**

The "ee" field encodes the Emitter Category as a binary value within the range 0 to 39. Emitter
categories are defined as shown in Table 11.

## TABLE 11 - EMITTER CATEGORIES..................................................................................................

```
Value Meaning Value Meaning
0 No aircraft type information 20 Cluster Obstacle
1 Light (ICAO) < 15 500 lbs 21 Line Obstacle
2 Small - 15 500 to 75 000 lbs 22 (reserved)
3 Large - 75 000 to 300 000 lbs 23 (reserved)
4 High Vortex Large (e.g., aircraft such as B757) 24 (reserved)
5 Heavy (ICAO) - > 300 000 lbs 25 (reserved)
```
(^6) acceleration and high speed Highly Maneuverable > 5G 26 (reserved)
7 Rotorcraft 27 (reserved)
8 (Unassigned) 28 (reserved)
9 Glider/sailplane 29 (reserved)
10 Lighter than air 30 (reserved)
11 Parachutist/sky diver 31 (reserved)
12 Ultra light/hang glider/paraglider 32 (reserved)
13 (Unassigned) 33 (reserved)
14 Unmanned aerial vehicle 34 (reserved)
15 Space/transatmospheric vehicle 35 (reserved)
16 (Unassigned) 36 (reserved)
17 Surface vehicle — emergency vehicle 37 (reserved)
18 Surface vehicle — service vehicle 38 (reserved)
19 Point Obstacle (incballoons) ludes tethered 39 (reserved)
MFD Recommendation: The Display should determine the appropriate style of traffic symbol
for a target by using a combination of Address Type, Emitter Category, NIC value, Air/Ground
state, and Traffic Alert status.
Example: "ee" = 0x11 -> Surface Emergency Vehicle.
**3.5.1.11 CALLSIGN**
The Call Sign is conveyed using 8 ASCII characters. The valid character values are the codes
for the numbers '0' through '9', the letters 'A' through 'Z', and the Space character (0x20). Space


Page 24 June 5, 2007

is only used as a trailing pad character, or when no call sign character is available. With **SW
Mod C** and earlier, the dash ‘-‘ character represents a printable code for a character that is
unavailable. Starting with **SW Mod D** , the space character is used for unavailable characters, to
reduce display clutter.

MFD Recommendation: The Call Sign field can contain any of the following types of
information; an aircraft tail number (e.g. "N89TM"), an airline-style flight number (e.g.
"UAL123"), or a company-specified identifier (e.g. "LFS32Y"). The Display may present the
Call Sign to the flight crew to aid in visual acquisition. The Call Sign should not be relied on as a
unique target identifier.

**3.5.1.12 EMERGENCY/PRIORITY CODE**

The Emergency Priority Code is a 4-bit value "p" that provides status information about the
traffic. The values for "p" are given below:
p = 0 : no emergency
p = 1 : general emergency
p = 2 : medical emergency
p = 3 : minimum fuel
p = 4 : no communication
p = 5 : unlawful interference
p = 6 : downed aircraft
p = 7-15 : reserved

MFD Recommendation: Displaying the target Emergency/Priority Code may be useful in some
specialized applications (e.g. Search and Rescue).


June 5, 2007 Page 25

### 3.5.2. Traffic Report Example..............................................................................................

This section presents a fully worked-out example of a typical Traffic Report, for a target airborne
over Salem OR, stated in byte order including the Message ID.

Report Data:
No Traffic Alert
ICAO ADS-B Address (octal): 52642511 8
Latitude: 44.90708 (North)
Longitude: -122.99488 (West)
Altitude: 5,000 feet (pressure altitude)
Airborne with True Track
HPL = 20 meters, HFOM = 25 meters (NIC = 10, NACp = 9)
Horizontal velocity: 123 knots at 45 degrees (True Track)
Vertical velocity: 64 FPM climb
Emergency/Priority Code: none
Emitter Category: Light
Tail Number: N825V

## TABLE 12 - TRAFFIC REPORT EXAMPLE..........................................................................................

**Byte # - Field Value Byte # - Field Value**
1 - Message ID 0x14 15 - hh 0x07
2 - st 0x00 16 - hv 0xB0
3 - aa 0xAB 17 - vv 0x01
4 - aa 0x45 18 - tt 0x20
5 - aa 0x49 19 - ee 0x01
6 - ll 0x1F 20 - cc 0x4E
7 - ll 0xEF 21 - cc 0x38
8 - ll 0x15 22 - cc 0x32
9 - nn 0xA8 23 - cc 0x35
10 - nn 0x89 24 - cc 0x56
11 - nn 0x78 25 - cc 0x20
12 - dd 0x0F 26 - cc 0x20
13 - dm 0x09 27 - cc 0x20
14 - ia 0xA9 28 - px 0x00


Page 26 June 5, 2007

## 3.6. Pass-Through Reports

When the pass-through interface is in use, the GDL 90 will output the received ADS-B messages
as-is without further processing. Targets are selected for output based on proximity to the
ownship position, and the amount of data interface bandwidth available. No traffic alerting
service is provided when this interface is in use. No report extrapolation or coasting is
performed.

There are two Pass-Through report messages; one for the Basic UAT message (see Table 13),
and one for the Long UAT message (see Table 14).

See §3.3.1 for the format of the Time of Reception field.

## TABLE 13 - BASICUAT REPORT (OUTPUT) ....................................................................................

```
Byte # Name Size Value
1 Message ID 1 30 10 = Basic Report
```
```
2-4 Time of Reception 3
```
```
24-bit binary fraction
Resolution = 80 nsec
```
```
5-22 Basic Payload 18 (see text)
Total Length 22
```
The format of the 18 bytes of Basic Payload is specified in RTCA/DO-282, Section 2.2.

## TABLE 14 - LONGUAT REPORT (OUTPUT).....................................................................................

```
Byte # Name Size Value
```
```
1 Message ID 1 31 10 = Long Report
```
```
2-4 Time of Reception 3
```
```
24-bit binary fraction
Resolution = 80 nsec
```
```
5-38 Long Payload 34 (see text)
Total Length 38
```
The format of the 34 bytes of Long Payload is specified in RTCA/DO-282, Section 2.2.


June 5, 2007 Page 27

## 3.7. Height Above Terrain.....................................................................................................

The GDL 90 can use the Height Above Terrain information from other on-board equipment that
supports terrain awareness, in order to provide reduced CSA sensitivity at low altitudes. The
Display can provide the current Height Above Terrain to the GDL 90 using this message.
Alternatively, the GDL 90 can use an ARINC 429 format Radio Altitude (label 164) for this
purpose.

If Height Above Terrain from one of these sources is not provided to the GDL 90, CSA will not
be able to use the lower sensitivity levels, which can result in an increased occurrence of
nuisance traffic alerts.

## TABLE 15 - HEIGHTABOVE TERRAIN MESSAGE(INPUT) ................................................................

```
Byte # Name Size Value
1 Message ID 1 9 10 = HAT Message
```
```
2-3 Height Above Terrain 2
```
```
Height above terrain
Resolution: 1 foot
```
```
Total Length 3
```
Height Above Terrain is encoded as a 16-bit signed value, with a resolution of 1 foot. The data
is transmitted most significant byte first.

Example:
If Byte 2 is 0x01, and Byte 3 is 0x00, this represents a Height Above Terrain of 256 feet.

Special Value: The value 0x8000 indicates that the Height Above Terrain data is invalid.


Page 28 June 5, 2007

## 3.8. Ownship Geometric Altitude Message..........................................................................

**SW Mod C** : When configured for either the Traffic Alert or Pass-through interfaces, the GDL 90
will output an Ownship Geometric Altitude message once per second, when geometric altitude is
available. See Table 16 for the message format.

## TABLE 16 - OWNSHIP GEOALTITUDEMESSAGE(OUTPUT) ............................................................

```
Byte # Name Size Value
```
```
1 Message ID 1 11 10 = Ownship Geo Alt
```
```
2 - 3 Ownship Geo Altitude 2
```
```
“dd dd”
Signed altitude in 5 ft. resolution (see text)
```
```
4-5 Vertical Metrics 2
```
- Vertical Warning indicator
- Vertical Figure of Merit, in meters (see text)

```
Total Length 5
```
The Ownship Geometric Altitude message is output by the GDL 90 only when the ownship GPS
altitude is available.

The Geo Altitude field is a 16-bit signed integer that represents the geometric altitude (height
above WGS-84 ellipsoid), encoded using 5-foot resolution, as follows:

```
Geo Altitude (ft) = "dddd" * 5
```
Byte 2 is the most-significant byte.

Geo Altitude Examples:
-1,000 feet 0xFF38
0 feet 0x0000
+1000 feet 0x00C8

The Vertical Metrics field contains a 1-bit value for the Vertical Warning indicator, and a 15-bit
unsigned integer that represents the Vertical Figure of Merit in meters. Byte 4 is the most-
significant byte.

The most significant bit of Byte 4 is the Vertical Warning indication. The bit is SET whenever a
position alarm is present, or if fault detection is not available.

The remaining 15 bits represent the Vertical Figure of Merit in meters. Two of the values are
reserved to indicate special conditions:

```
Value 0x7FFF is reserved to indicate that VFOM is not available.
Value 0x7FFE is reserved to indicate that VFOM is available and is >= 32766 meters.
```

June 5, 2007 Page 29

Examples of Vertical Metrics values:
Vertical Warning and VFOM not available: 0xFFFF
No Vertical Warning, VFOM = 40,000 meters 0x7FFE
No Vertical Warning, VFOM = 10 meters 0x000A
Vertical Warning, VFOM = 50 meters 0x8032


Page 30 June 5, 2007

## 4. UPLINK PAYLOAD FORMAT ....................................................................................

This section defines the format of the Uplink Message payload.

```
Note: The following material is adopted from the SF21 East Coast project guidance document draft.
```
## 4.1. Uplink Message

The UAT Uplink message is a general-purpose mechanism for the uplink of data services. Each
Uplink message contains a 432-byte payload field. The payload is composed of an eight-byte
UAT-Specific Header, followed by 424 bytes of Application Data. The Application Data field is
further composed of one or more Information Frames (I-Frames). The overall composition of
the Uplink message is shown in Figure 3.

```
3 b its 4 b its
```
**...** fill as needed

```
Length Fra me Data
```
```
I-F ra me 1 I-F ra me 2 I-F ra me 3 I-F ra me N
```
```
Application Data
```
```
Frame Type
```
```
Length
```
```
UAT-Specific Header
```
```
8 bytes
```
```
432 bytes (message payload)
```
```
424 bytes
```
```
9 b its
```
```
Res.
```
```
Transmission order
```
## FIGURE3-COMPOSITION OF THE GROUND UPLINKMESSAGEPAYLOAD.......................................

### 4.1.1. UAT-Specific Header .................................................................................................

The UAT-Specific Header is an 8-byte field that contains information on the location of the
broadcasting ground station, the time slot used to send the present message, validity flags for
position, time, and application data, and other fields as described in Section 2.2.3.2.2 of
RTCA/DO-282.


June 5, 2007 Page 31

**4.1.2. Application Data**

The Application Data is a fixed-length field of 424 bytes. The Application Data consists of
Information Frames, and always consists of an integral number of bytes. Any remaining unused
portion of the field is zero-filled (i.e., all bits set to ZERO).

```
Note : When processed by the I-Frame parsing logic, the zero-fill portion will appear as a Frame
Length of zero bytes, or as an incomplete frame (if less than 2 bytes remain). Either condition
indicates that that the Application Data contains no additional I-Frames.
```
## 4.2. Information Frames........................................................................................................

Each Information Frame consists of ‘N’ bytes, comprising four fields formatted as shown in
Table 17.

```
Table 17 - I-Frame Structure
Byte
# Bit 7 Bit 6 Bit 5 Bit 4 Bit 3 Bit 2 Bit 1 Bit 0
1 Length
2 LSB Reserved Frame Type
3
```
**-
N**

```
Frame Data
```
_Note: Byte numbers in this table are relative to the beginning of the current Information Frame._

### 4.2.1. Length Field ...............................................................................................................

The Length field (Byte 1 bit 7 through Byte 2 bit 7) is a 9-bit field that contains the length of the
Frame Data field in bytes. Values range from 0 through 422 (decimal). The Length value is
always equal to ‘N-2’. If the Length value is zero, this indicates that there are no additional I-
Frames in this message.

### 4.2.2. Reserved Field

The Reserved field (Byte 2 bits 6..4) is a 3-bit field that is reserved for future use, and will be set
to ALL ZEROS.

### 4.2.3. Frame Type Field.......................................................................................................

The Frame Type field (Byte 2 bits 3..0) is a 4-bit field that contains the indication for the format
of the Frame Data field. The Frame Types are defined in Table 18.


Page 32 June 5, 2007

## TABLE 18 - FRAME TYPES...............................................................................................................

```
MSB Value
(binary)
LSB Frame Data Format
0000 FIS-B APDU
0001 - 1110 Reserved for future use
1111
Reserved for
Developmental use
```
When the Frame Type is the binary value “0 0 0 0”, the Frame Data contains FIS-B data
packaged as an Application Protocol Data Unit (APDU) as described in Section 3.6, and
Appendix D of RTCA/DO-267.

Fourteen reserved values remain for future use.

When the Frame Type is the binary value “1 1 1 1”, the Frame Data contains an Uplink message
whose content is intended for developmental or experimental use, and should be processed as
appropriate by those participating in those efforts.

### 4.2.4. Frame Data Field ......................................................................................................

The Frame Data field conveys the basic units of uplink application data. For FIS-B this data unit
is known as the Application Protocol Data Unit (APDU) as defined in §4.3.

## 4.3. FIS-B Product Encoding (APDUs)

Each APDU is comprised of an APDU Header followed by the APDU Payload.

### 4.3.1. APDU Header ............................................................................................................

The APDU header format is described in Appendix D of the RTCA/DO-267 (FIS-B MASPS)
with one variation as described below.

The UAT APDU header does not include the 16-bit FIS-B APDU ID field defined in the FIS-B
MASPS (i.e. as a fixed two byte field of 0xFF and 0xFE). Since UAT FIS-B APDUs are fully
identified by the Frame Type field (see §4.2.3), inclusion of these two APDU ID bytes in the
UAT APDU header is unnecessary, and they are omitted.

### 4.3.2. APDU Payload...........................................................................................................

The FAA Broadcast Services ground system presently encodes FIS-B data products for uplink
using only _independent_ APDUs as described in RTCA/DO-267. Each APDU stands alone in
that each individual APDU received results in some data that can be rendered on the cockpit
display; there is no dependence on the APDUs that precede or succeed it. In the event that future
FIS-B products require an APDU longer than 422 bytes, then the APDU segmentation scheme
described in RTCA/DO-267 may be used.


June 5, 2007 Page 33

APDUs will carry products that are registered in the FAA’s FIS-B product registry. This registry
is maintained by the Weather Processor and Sensors Group (ACB-630) at the FAA’s William J.
Hughes Technical Center. The registry can be accessed at [http://fpr.tc.faa.gov.](http://fpr.tc.faa.gov.)

## 4.4. FIS-B Products

### 4.4.1. Textual METAR and TAF Products ...........................................................................

The Textual METAR and TAF products use the format identified in the FIS-B product registry
by the name “Generic Textual Data Product - Type 2 (DLAC)” and the 11-bit Product ID of
“413 10 ”. Details on the encoding of the text records are found in the FAA’s FIS-B product
registry (http://fpr.tc.faa.gov).

### 4.4.2. NEXRAD Graphic Product ........................................................................................

The NEXRAD Graphic product is identified in the FIS-B product registry by the name “Global
Block Representation – NEXRAD, Type 4 – 8 Level” and the 11 bit Product ID of “63 10 ”.
Details on the encoding of the text records are found in the FAA’s FIS-B product registry
(http://fpr.tc.faa.gov).

## 4.5. Future Products

The FAA UAT base station deployment plan will accommodate additional Uplink products.
FAA will announce the availability of new products when they are ready for operational use.
New products will be described in the FIS-B product registry.


```
Page 34 June 5, 2007
```
## 5. FIS-B PRODUCT APDU DEFINITION .......................................................................

```
The following information is taken from the data submitted for inclusion in the FIS-B Product
Registry, and is provided as guidance until the registry is updated. In case of discrepancies
between this document and the FIS-B Product Registry, the Registry takes precedence.
As additional FIS-B products are made available by the ground stations, full specifications will
be disclosed through the FIS-B Product Registry. Updates to this document will not be required,
and since the GDL 90 acts as a pass-through device for FIS-B Products, no updates to GDL 90
application software will be necessary.
MFD Recommendation: Display vendors may wish to consult RTCA/DO-267A for guidance on
presentation of FIS-B products to the flight crew.
```
## 5.1. Type 4 NEXRAD Precipitation Image – Global Block Representation.....................

### 5.1.1. Definition ...................................................................................................................

```
This description provides the format for encoding NEXRAD graphic products using the Global
Block Representation format described in Section D.2.3.5 of RTCA DO-267A (FIS-B MASPS).
```
### 5.1.2. Assumptions ...............................................................................................................

```
The receiving system can assume that when this product is received from multiple ground
stations offering overlapping coverage, the areas of overlap will be assured to register and can be
simply merged on the cockpit display.
```
### 5.1.3. APDU Payload Format..............................................................................................

```
5.1.3.1 APDU HEADER
```
```
The format of the APDU header used for this product is shown in Table 19. It follows the
APDU Header Format as outlined in Appendix D of RTCA DO-267 with none of the optional
fields used for this product; specifically, no Product Descriptor options and no APDU
segmentation are used. The Product ID is "63" 10.
The last four zeros show the pad that is required to round out the APDU header to end on a byte
boundary. The time field encoded in the APDU header is the time of product creation.
```
## TABLE 19 - APDU HEADER - NEXRAD GRAPHICS.......................................................................

```
Å APDU Header (32 bits) Æ
```
APDU ID Af Gf PF Product ID (11 bits) Sf opt T (5 bits) Hours Minutes (6 bits)

```
(See Note 1) 0 0 0 0 0 0 0 0 1 1 1 1 1 1 0 0 0 0 0 0 0
Transmission order Æ
Note:
1) The FIS-B APDU-ID is not transmitted in the FAA UAT FIS-B network. The length of the UAT APDU
header is 32 bits, rather than 48 bits as defined in the FIS-B MASPS.
```

June 5, 2007 Page 35

```
2) While this product employs the minimal APDU header format shown above, avionics designed for
operation on the FAA’s network should not preclude the ability to parse APDUs with any of the
optional fields invoked. This will ensure any future products that may employ these optional fields can
be processed.
```
**5.1.3.2 PAYLOAD**

The Global Block Representation geo references individual “bins” of the NEXRAD image to
latitude and longitude rather than on a projection requiring a point of tangency. The encoded
intensity levels for the individual “bins” map into “dBz” reflectivity levels as shown in Table 20.

## TABLE 20 - INTENSITYENCODING OF NEXRAD COMPOSITE REFLECTIVITY PRODUCT.................

```
Intensity Encoded Value dBz Reflectivity Range Weather Condition
0 dBz < 5
1 5  dBz  20
2 20  dBz  30 VIP 1
3 30  dBz  40 VIP 2
4 40  dBz  45 VIP 3
5 45  dBz  50 VIP 4
6 50  dBz  55 VIP 5
7 55 dBz VIP 6
```
```
Note:
1) The color rendering on cockpit displays of the Intensity Encoded Values 2(two) through 7 (seven)
should follow the Color Philosophy for the associated Weather Condition as described in Section
3.8.2 (Table 3-2) of RTCA DO-267A (FIS-B MASPS).
2) The Intensity Encoded Values 0 (zero) and 1 (one) are considered Background and should be color
rendered accordingly.
```
The Global Block Representation itself is defined in detail in Section D.2.3.5 of RTCA/DO-
267A, and is not replicated here due to copyright considerations.


Page 36 June 5, 2007

### 5.1.4. FIS-B Graphical Example..........................................................................................

This section presents hexadecimal data for two sample 424-byte Application Data fields. These
fields convey a graphical NEXRAD image for an area of northern Oregon. The graphical image
contains a test pattern that depicts three colored elliptical areas that roughly resemble
precipitation cells, surrounded by a region that contains no precipitation.

The sample Application Data fields contain a total of 19 APDUs; nine of the APDUs contain
run-length encoded blocks, and 10 APDUs contain Empty Element blocks. Three APDUs make
up each ellipse (a top, middle, and bottom stripe).

Step-by-step decoding process:

The first two bytes (0x1300) are the I-Frame Length (Length = 38) and Frame Type (Type 0,
FIS-B APDU) for the first APDU.

The following 4 bytes (0x00 0xFC 0x00 0x00) are the APDU Header (Product ID=63 10 , Time =
00 hr 00 min). Note that the APDU Header Time for a NEXRAD Graphic product would
typically contain the time of product creation, but does not in this example.

The following three bytes (0x84 0xA5 0x70) carry the Block Reference Indicator, as shown in
RTCA/DO-267A, Appendix D.2.3.5.2.2, Figure 10. The Element Identifier is SET, indicating
that this APDU describes a run-length encoded block, and the Block Reference Number is
0x4A570 in the North hemisphere. This block occupies a region from 123º 12' to 122º 24' West
longitude, and from 45º 04' to 45º 08' North latitude.

Each of the remaining bytes of the APDU encode the value of each of the 128 bins that comprise
this block (as 4 rows of 32 bins each). In each byte, the upper 5 bits represent the number of
sequential bins (minus 1) that each have the intensity value given in the lower 3 bits. The next
byte in the example data (0x30) indicates that the first 7 bins have Intensity value 0. The
following byte (0x89) indicates that the next 18 bins have Intensity value 1. The following byte
(0x50) indicates that the next 11 bins (the last 7 of the first row, plus the first 4 of the following
row) have Intensity value 0.

Parsing the entire first APDU will yield the following Intensity values shown in Table 21 for this
block (blank cells represent Intensity = 0).

## TABLE 21 - SAMPLE BLOCK DECODING..........................................................................................

1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
1 1 1 2 2 2 2 3 3 3 3 3 3 3 3 3 3 3 2 2 2 1 1

1 1 1 2 2 3 3 3 3 3 5 5 5 5 5 5 5 5 5 3 3 3 3 2 2 1 1
1 1 2 2 3 3 3 3 4 4 5 5 5 5 6 7 6 5 5 5 5 4 3 3 3 3 2 2 1

The remaining 8 run-length encoded APDUs are processed in like manner.

The 10 APDUs that encode Empty Element blocks serve to map the entire rectangular region
from 124º 00' to 120º 00' West longitude, and from 44º 56' to 45º 32' North latitude (other than
the three precipitation ellipses) to the Intensity = 0 value. Outside of this region, the MFD
should show that no data is available.


June 5, 2007 Page 37

Sample Application Data Field 1:

130000FC000084A570308950111A53120930110A23451B0A0918090A1B0C1D0607061D041
B0A0108208000FC000084A3AE00090A1314150617061D04130A01080112131C0D06270615
140B0A01000112131C0D06270615140B0A010000090A1314150617061D04130A0108148000
FC000084A1EC00090A1B0C1D0607061D041B0A010808110A23451B0A091018111A531209
20308930130000FC000084AAB7308950111A53120930110A23451B0A0918090A1B0C1D060
7061D041B0A0108208000FC000084A8F500090A1314150617061D04130A01080112131C0D
06270615140B0A01000112131C0D06270615140B0A010000090A1314150617061D04130A01
08148000FC000084A73300090A1B0C1D0607061D041B0A010808110A23451B0A091018111
A53120920308930130000FC000084AFFD308950111A53120930110A23451B0A0918090A1B
0C1D0607061D041B0A010800000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000

Sample Application Data Field 2:

208000FC000084AE3B00090A1314150617061D04130A01080112131C0D06270615140B0A0
1000112131C0D06270615140B0A010000090A1314150617061D04130A0108148000FC00008
4AC7900090A1B0C1D0607061D041B0A010808110A23451B0A091018111A5312092030893
0040000FC000004B1BDF0040000FC000004AFFBD0040000FC000004AE39D0040000FC000
004AC77D0040000FC000004AAB5D0040000FC000004A8F3D0040000FC000004A731D004
0000FC000004A56FE0040000FC000004A3ADE0040000FC000004A1EBE0000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000


Page 38 June 5, 2007

## 5.2. Generic Textual Data Product – Type 2 (DLAC)

### 5.2.1. Definition ...................................................................................................................

This description is based on the Generic Text Data Product Type 2, except that the DLAC 6-bit
alphabet will be used. This Generic Text Data Product is represented as strings of characters in a
format that is independent of the type of text product itself. The advantage of the Generic Text
product is that new types of text records following this format can be introduced without
necessitating changes to the Display software.

### 5.2.2. APDU Payload Format..............................................................................................

**5.2.2.1 APDU HEADER**

The format of the APDU header used for this product is shown in Table 22. It follows the
APDU Header Format as outlined in Appendix D of RTCA DO-267 with none of the optional
fields used for this product; specifically, no Product Descriptor options and no APDU
segmentation are used. The Product ID is "413" 10.

The last four zeros show the pad that is required to round out the APDU header to end on a byte
boundary. For this product, the time field encoded in the APDU header has no meaning. Each
text record contains a time field that should be used to indicate product age.

## TABLE 22 - APDU HEADER -GENERIC TEXT.................................................................................

```
Å APDU Header (32 bits) Æ
APDU ID Product Descriptor (14 bits)^ Header Time (13 bits)
A
f
```
```
G
f
```
```
P
f
```
```
Product ID
(11 bits)
```
```
S
f
```
```
T
opt
```
```
Hours
(5 bits)
```
```
Minutes
(6 bits)
```
```
Pad
(4 bits)
```
```
(See Note 1) 0 0 0 0 0 1 1 0 0 1 1 1 0 1 0 0 0 0 0 0 0
Transmission order Æ
Note:
```
```
1) The FIS-B APDU-ID is not transmitted in the FAA UAT FIS-B network. The length of the UAT APDU
header is 32 bits, rather than 48 bits as defined in the FIS-B MASPS.
```
```
2) While this product employs the minimal APDU header format shown above, avionics designed for
operation on the FAA’s network should not preclude the ability to parse APDUs with any of the
optional fields invoked. This will ensure any future products that may employ these optional fields can
be processed
```
```
3) The Hours and Minutes fields in the APDU Header have no meaning for this product, as a Time field
is included in each text record.
```

June 5, 2007 Page 39

**5.2.2.2 PAYLOAD**

General Requirements

1. All Text is composed of the DLAC 6 bit character set encoded per Appendix K of RTCA DO-267A
    (FIS-B MASPS).
2. Within each character the most significant bit is transmitted first. The most significant bit of
    character n+1 follows immediately after the least significant bit of character n.
3. The APDU will be composed of one or more whole, concatenated text records.
4. One text record will not span more than one APDU payload.
5. The length of a text record will have a maximum size of 418 bytes.

```
Note: An artificial limit smaller than 418 bytes may be imposed to eliminate ongoing remarks in
the text message. The value would be chosen to meet two criteria:
1) the required information in the original report is faithfully preserved; and
2) the resulting size would allow several text messages to pack efficiently into each Ground Uplink
message payload.
```
### 5.2.3. METAR / TAF Composition .......................................................................................

Text records for METAR and TAF are composed as shown in the syntax below:

```
Record = <Type> <sp> <LocID> <sp> <Time> [SP|AM]<sp> <Text report> <RS><fill bits>
```
The syntax elements and rules for text record composition are shown in Table 23 below:

## TABLE 23 - METAR/TAF STRUCTURE...........................................................................................

```
Syntax
Element
```
```
Description Required/
Optional
<> Denotes a text string N/A
[] Denotes an optional field N/A
sp Denotes a single space character (100000 2 ) Required
RS Denotes the record separator character (011101 2 ) Required
Type One or more characters not containing the <sp> or <RS>. Limited to “METAR” and “TAF” initially Required
```
```
LocID
```
```
One or more characters that can not contain <sp> or <RS>, required.
Recommended but not limited to standard location Identifiers (i.e., ILN,
SDF)
```
```
Required
```
```
Time
```
```
One or more characters that can not contain <sp> or <RS>. Typically
represents UTC date/time group (i.e., 012155Z), and it is used to
convey the Product Age for the report.
```
```
Required
SP or
AM
```
```
SP denotes special METAR (SPECI) as a subset of METAR, or AM
denotes amendments (AMEND) as a subset of TAF. Optional
Text
report
```
```
One or more characters that cannot contain <RS>. This is the actual
text of the WMO report that may be displayed exactly as received
without additional formatting or interpretation.^1
```
```
Required
```
```
Fill
bits
```
```
0, 2, 4, or 6 bit positions set to ALL ZEROs as required to zero fill any
unused bits in the last byte of the record.
```
```
Required
for byte
alignment
```
(^1) METAR and TAF messages may contain the equals (‘=’) character to indicate a message delimiter, or the string
“NIL=” to indicate a report that is missing or delayed. The “NIL=” string may replace either the LocID or Time
fields. The display processor should be capable of gracefully handling these conditions. See also US National
Weather Service Instruction 10-813, Feb 7, 2005, "Terminal Aerodrome Forecasts.


Page 40 June 5, 2007

### 5.2.4. FIS-B Text Example ...................................................................................................

The following hexadecimal data represents a sample 424-byte Application Data field. This
sample message conveys textual TAF reports for several Oregon airports.

The sample Application Data field contains five APDUs. Each APDU conveys a single TAF
report.

Step-by-step decoding process:

The first two bytes (0x2180) are the I-Frame Length (Length = 67) and Frame Type (Type 0,
FIS-B APDU).

The following 4 bytes (0x06 0x74 0x41 0x90) are the APDU Header (Product ID=413, Time =
16 hr 25 min). Note that the APDU Header Time is unused for FIS-B Text messages, but is
included here for illustration.

The remaining 63 bytes contain packed 6-bit DLAC characters that make up the text records for
this report. Decoding the first 3 bytes (0x50 0x11 0xA0) yields the 4 DLAC values 20, 1, 6, and
32, which represent the letters 'T', 'A', 'F', <space>.

Continuing in this manner, the next 3 bytes represent the text "KSLE". The next 6 bytes
represent the text " 260900Z". Therefore, the first three text fields of the first APDU of this
Application Data Field are "TAF KSLE 260900Z". Since the text fields are always space-
delimited, the third field is the date/time group for this TAF.

The remainder of the APDUs contain similar TAF reports for "KPDX", "KEUG", "KAST", and
"KHIO". The body of the TAF text is identical for all 5 reports. The end of the Application
Data is zero-filled to the fixed length of 424-bytes.

Sample Application Data Field (424 bytes):

2180067441905011a02d3305832db0e70c1a04d832d71cf1d60c38c30d8b5204364cd806157c36c
2008b3b1cb079c146370d30c205920b0ccb5204364cd8130d4cb5c3d79d2180067441905011a02d
0118832db0e70c1a04d832d71cf1d60c38c30d8b5204364cd806157c36c2008b3b1cb079c146370
d30c205920b0ccb5204364cd8130d4cb5c3d79d2180067441905011a02c5547832db0e70c1a04d8
32d71cf1d60c38c30d8b5204364cd806157c36c2008b3b1cb079c146370d30c205920b0ccb52043
64cd8130d4cb5c3d79d2180067441905011a02c14d4832db0e70c1a04d832d71cf1d60c38c30d8b
5204364cd806157c36c2008b3b1cb079c146370d30c205920b0ccb5204364cd8130d4cb5c3d79d2
180067441905011a02c824f832db0e70c1a04d832d71cf1d60c38c30d8b5204364cd806157c36c2
008b3b1cb079c146370d30c205920b0ccb5204364cd8130d4cb5c3d79d00000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000


June 5, 2007 Page 41

## 6. CONTROL PANEL INTERFACE ................................................................................

The GDL 90 receives control messages over the Control Panel interface (on the DB15 - P1
connector), using pin 12 (input to GDL 90) and pin 5 (ground). The interface uses an ASCII-text
basis, with an ASCII-encoded hexadecimal checksum. The checksum is the algebraic sum of the
message byte values. Messages are delimited with a carriage return character.

## CAUTION

Equipment used to control the GDL 90 must be FAA-approved and certified under TSO-C154.

## 6.1. Physical Interface............................................................................................................

The Control Panel interface uses RS-232 signaling levels. The port is configured for the
following characteristics:

```
Baud Rate: 1200 or 9600 baud (configurable)
Start Bits: 1
Data length: 8 bits
Stop Bits: 1
Parity: None
Flow Control: None
```
## 6.2. Control Messages ............................................................................................................

The following table summarizes the Control Panel messages that the GDL 90 receives.

## TABLE 24 - CONTROLMESSAGES....................................................................................................

```
Msg ID Description Notes Ref
^CS Call Sign 1 min interval or on change 6.2.1
^MD Operation Mode Message 1 second interval (nominal) 6.2.2
^VC VFR Code 1 min interval 6.2.3
```

Page 42 June 5, 2007

### 6.2.1. Call Sign Message......................................................................................................

```
The call sign message provides for a user selectable call sign.
Rate: Every 1 minute or when a change occurs
Message Length: 15 bytes
```
**6.2.1.1 CALLSIGNFORMATSPECIFICATION**

## TABLE 25 - CALLSIGNMESSAGEFORMAT.....................................................................................

Byte Contents Description
1 ‘^’ ASCII ‘^’ (0x5E)
2 ‘C’ ASCII ‘C’ (0x43)
3 ‘S’ ASCII ‘S’ (0x53)
4 ‘ ‘ ASCII space (0x20)
5-12 dddddddd ASCII call sign (all 8 characters are mandatory, right pad with space)
13-14 dd Checksum of bytes 1 through 12. In hex ASCII i.e. “FA”
15 ‘\r’ ASCII carriage return (0x0D)

**6.2.1.2 CALLSIGNMESSAGEEXAMPLES**

```
^CS GARMIN 12 Call Sign is “GARMIN “ (includes two trailing spaces before checksum)
```

June 5, 2007 Page 43

### 6.2.2. Mode Message ...........................................................................................................

```
The mode message indicates the current operating mode. It includes the current mode, the Ident
status, current Squawk code setting, and emergency code.
```
```
Rate: 1 sec (nominal)
Message Length: 17 bytes
```
**6.2.2.1 MODEFORMAT SPECIFICATION**

## TABLE 26 - MODEMESSAGEFORMAT............................................................................................

```
Byte Contents Description
1 ‘^’ ASCII ‘^’ (0x5E)
2 ‘M’ ASCII ‘M’ (0x4D)
3 ‘D’ ASCII ‘D’ (0x44)
4 ‘ ‘ ASCII space (0x20)
5 m See Table 27 - Mode Field
6 ‘, ‘ ASCII comma (0x2C)
7 i See Table 28 - Ident Field
8 ‘,‘ ASCII comma (0x2C)
9-12 dddd ASCII Squawk code
13 e See Table 29 - Emergency Field
14 h Health bit in hex ASCII “1”
15-16 dd Checksum of bytes 1 through 14. In hex ASCII i.e. “FA”
17 ‘\r’ ASCII carriage return (0x0D)
```
The field values are discussed in the following tables.

## TABLE 27 - MODEFIELD.................................................................................................................

```
m Definition ASCII
O Standby Mode 0x4F
A Mode A 0x41
C Mode C 0x43
```
Standby Mode turns the GDL 90 transmitter off, so that no ADS-B messages are transmitted.
Mode A suppresses the transmission of pressure altitude in the ADS-B messages. Mode C is the
normal operating mode, which includes pressure altitude.

## TABLE 28 - IDENTFIELD.................................................................................................................

```
i Definition ASCII
I Ident Enabled 0x49
```
- Ident is Inactive 0x2D

When IDENT is enabled, this causes the GDL 90 to include the IDENT indication in the
transmitted ADS-B messages for the next 20 seconds.


Page 44 June 5, 2007

## TABLE 29 - EMERGENCY FIELD.......................................................................................................

```
e Definition ASCII
0 None 0x0
1 General 0x1
2 Medical 0x2
3 Fuel 0x3
4 Com 0x4
5 Hijack 0x5
6 Downed 0x6
```
Any active emergency code is included in the GDL 90’s transmitted ADS-B messages.

The Health indication is set to ‘1’ by the control panel to indicate that it is operating normally.

**6.2.2.2 MODEMESSAGEEXAMPLE**

```
^MD A,I,23540120 Mode A, Ident active, Squawk 2354, No Emergency, Healthy
```

June 5, 2007 Page 45

### 6.2.3. VFR Code Message....................................................................................................

```
The VFR Code message informs the GDL 90 of the squawk code that is used to indicate the VFR
operating condition. In the US NAS, this is the value “1200”.
```
**6.2.3.1 INTERFACESPECIFICATION**

```
Rate: 1 minute
Message Length 11 bytes
```
**6.2.3.2 VFR CODEFORMATSPECIFICATION**

## TABLE 30 - VFR CODE MESSAGEFORMAT.....................................................................................

Byte Contents Description
1 ‘^’ ASCII ‘^’ (0x5E)
2 ‘V’ ASCII ‘V’ (0x56)
3 ‘C’ ASCII ‘C’ (0x43)
4 ‘ ‘ ASCII space (0x20)
5-8 dddd ASCII VFR Code ASCII characters
9-10 dd Checksum of bytes 1 through 8. In hex ASCII i.e. “FA”
11 ‘\r’ ASCII carriage return (0x0D)

**6.2.3.3 VFR CODEMESSAGEEXAMPLES**
^VC 1200DA VFR code is 1200


Page 46 June 5, 2007




