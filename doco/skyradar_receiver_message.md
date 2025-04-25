```
Format of the SkyRadar receiver message ID 101
```
This document describes format for the message ID 101 for the receiver firmware version 10 and above.

**Offset Size Description Possible Values**

**0**^1 Message ID^101
**1** 1 Firmware version 21
**2** 1 Debug data 00

**3** 1 GPS fix quality ASCII character: ‘0’ – no
fix; ‘1’ – regular fix; ‘2’ –
DGPS (WAAS)

**4** 3 Total number of
transmitted messages
since power up. LSB
first.

**7** 1 GPS time in hours
**8** 1 GPS time minutes

**9** 2 Debug data
**11** 1 Hardware version Starting with firmware
version 42, this
additional byte reports
revision of the
hardware
**12** 2 GPS HDOP Firmware version 45
and above: GPS HDOP
in meters multiplied by
10 , LSB first. Will have
value 5000 when not
available

**14** 2 Reserved data Firmware version 45
and above

**16** 4 Receiver hardware ID Firmware version 45
and above

**20**^1 Hardware status^ Firmware version 45
and above: top bit
(0x80) when set
indicates that receiver
uses external antenna
instead of built-in.
Currently only valid for
hardware version 6


