```
5 min. read · View original
```
# ForeFlight - GDL 90 Extended

# Specification

## ForeFlight's extension of the GDL 90 protocol

## provides more inflight connectivity for third-party

## devices.

## Connectivity

ForeFlight expects data sent using UDP to port 4000 on
the iOS device. Implementers are strongly advised to use
UDP unicast to avoid significant packet loss, as iOS appli-
cations such as ForeFlight cannot reliably receive UDP
broadcast messages, but perform much better with UDP
unicast. See ForeFlight Broadcast below to learn how to
discover ForeFlight's IP address to set as a UDP unicast
target.

iOS has an MTU of 1500 bytes. It is strongly recom-
mended to avoid fragmentation and to keep all packets
(including headers) smaller than 1500 bytes.

ForeFlight determines that a device is connected if data is
regularly received. Devices should regularly send either or
both of the Heartbeat or Ownship Report messages to en-
sure that the device is consistently reported as Connected.

## ForeFlight Broadcast


ForeFlight broadcasts a UDP message on port 63093 ev-
ery 5 seconds when ForeFlight is running in the fore-
ground. This message allows implementers to discover
ForeFlight's IP address, which can be used as the target of
UDP unicast messages. This is especially helpful when the
implementer and the iOS device are on a shared infra-
structure Wi-Fi network; otherwise, the implementer cannot
identify connected clients' IP addresses.

This broadcast will be a JSON message, with at least these
fields:

{

"App":"ForeFlight",

"GDL90":{

"port":

}

}

The GDL90 "port" field is currently 4000, but ForeFlight
reserves the right to change this port number in the future
as advanced configuration on networks where there are
collisions on port 4000.

Implementors in certified avionics (or otherwise difficult-
to-update software installations) are advised to consider
allowing ForeFlight's broadcast port (port 63093) to be


modified via advanced configuration as well, in case of
port collisions on certain networks.

## Messages

The ForeFlight GDL90 Extension protocol defines mes-
sages based on the GDL90 protocol. Section 2.2 of
the GDL90 specification describes the message structure
and Section 3 outlines a set of standard messages.
ForeFlight supports a subset of the standard messages
and also extends the protocol with a pair of custom mes-
sages containing device ID and AHRS information.

Heartbeat Message

See GDL90 specification §3.1 for complete details. Only
GPS validity bit is checked at this time.

```
Byte
# Name Size Value
1 Message ID 1 010 = Heartbeat
```
```
2
```
```
Status Byte 1
```
```
Bit 7: GPS Pos
Valid
```
```
1
```
```
1 = Position is available for
ADS-B Tx
```
```
Other bits are ignored
3 Status Byte 2 1 All bits ignored
4-5 Time Stamp 2 Ignored
6-7 Message Counts 2 Ignored
```
UAT Uplink

See GDL90 specification §3.3 for complete details.

```
Byte
# Name Size Value
1 Message ID 1 710 = Uplink Data
```

```
Byte
# Name Size Value
```
```
2-4 Time of
Reception
```
```
3
```
```
24-bit binary fraction
```
```
Resolution = 80 nsec
5-
436 Uplink Payload^432
```
```
UAT Uplink Packet. See §3.3.2 for
details
```
Ownship Report

See GDL90 specification §3.4 for complete details. The
position information in this message is used by ForeFlight
to determine current position.

```
Byte # Name Size Value
1 Message ID 1 1010 = Ownship Report
```
2-28 Ownship Report (^27) Defined in §3.5.
Notes:
Accuracy information is encoded by setting the NACp
value.
Altitude is defined as ownship pressure
altitude (referenced to 29.92 inches Hg). For unpressurized
aircraft a barometer in the cabin is close enough for prac-
tical purposes, but in pressurized aircraft, care must be
taken to set this field to 0xFFF (Invalid or Unavailable) if
the device does not have access to outside pressure.
Setting ownship pressure altitude incorrectly will result in
incorrect calculation of relative traffic altitude. 
Ownship Geometric Altitude
See GDL90 specification §3.8 for complete details. Note
that the altitude may be interpreted as either relative to


the WGS-84 ellipsoid as spec'ed, or to the WGS-84 geoid
(MSL). The ID message described below defines how this
altitude will be interpreted.

```
Byte
# Name Size Value
```
1 Message ID (^11110) = Ownship Geo Alt
2-
Ownship
Geo
Altitude
2
Signed altitude in 5ft resolution.
Byte 2 is the Most Significant
Byte
Altitude is interpreted as relative
to the WGS84 ellipsoid unless Bit
0 of the ID Message Capabilities
Mask is set, in which case it's
treated as MSL. 
4-5 VerticalMetrics 2
Vertical Warning Indicator (MSB
of Byte 4)
Vertical Figure of Merit (remain-
ing 15 bits).
0x7FFF indicates VFOM not
available
0x7EEE indicates VFOM is >
32766 meters
Byte 4 is the most significant
byte.
Traffic Report


See GDL90 specification §3.5 for complete details.

```
Byte # Name Size Value
1 Message ID 1 2010 = Traffic Report
2-28 Traffic Report 27 Defined in §3.5.
```
ID Message

For multibyte fields, the most significant byte should be
sent first (Big Endian).

```
Byte
# Name Size Value
1 ForeFlightMessage ID 1 0x
```
```
2
```
```
ForeFlight
Message
sub-ID
```
(^10)
3 Version 1 Must be 1
4-11 Device serialnumber 8 0xFFFFFFFFFFFFFFFF for
invalid
12-
19 Device name^8 8B UTF8 string.
20-
35
Device long
name^16
16B UTF8 string. Can be the same as Device
name. Used when there is sufficient space
for a longer string.
36-
39
Capabilities
mask
(^4) Bit 0 (LSB): Geometric altitude
datum used in the GDL
Ownship Geometric Altitudes
message
0: WGS-84 ellipsoid (as the
GDL90 spec states)
1: MSL
Bits 1,2 (LSB): Internet Policy -
how ForeFlight will access the


```
Byte
# Name Size Value
internet while connected to a
Wireless Device.
0: Unrestricted
1: Expensive (reduced band-
width usage)
2: Disallowed (will not at-
tempt to access the internet)
Bits 3-31: Reserved. Should be
all 0's.
```
AHRS Message

For multibyte fields, the most significant byte should be
sent first (Big Endian).
The AHRS message should be sent at 5Hz.

```
Byte
# Name Size Value
1 ForeFlightMessage ID 1 0x
```
```
2 AHRS Sub-
Message D
```
(^1) 0x
3-4 Roll (^2) Roll in units of 1/10 degree
0x7fff for invalid.
Positive values indicate right
wing down, negative values indi-
cate right wing up.
The message will be rejected if
roll is outside of the


```
Byte
# Name Size Value
range [-1800, 1800]
```
5-6 Pitch 2

```
Pitch in units of 1/10 degree
```
```
0x7fff for invalid.
```
```
Positive values indicate nose up,
negative values indicate nose
down.
```
```
The message will be rejected if
pitch is outside of the
range [-1800, 1800]
```
7-8 Heading 2

```
Most significant bit (bit 15)
0: True Heading
1: Magnetic Heading
```
```
Bits 14-0: Heading in units of
1/10 degree
```
```
Track should NOT be used here.
```
```
0xffff for invalid.
```
```
The message will be rejected if
heading is outside of the
range [-3600,3600]
```
9-10 IndicatedAirspeed 2

```
Value in Knots
```
```
0xffff for invalid.
```
11-12 True Airspeed 2

```
Value in Knots
```
```
0xffff for invalid.
```


