import struct
import math
from datetime import datetime, timezone

# GDL90 Constants
FLAG_BYTE = 0x7E
CONTROL_ESCAPE = 0x7D
ESCAPE_XOR = 0x20

# Message IDs
MSG_ID_HEARTBEAT = 0x00
MSG_ID_OWNSHIP_GEO_ALT = 0x0B # 11 - Ownship Geometric Altitude
MSG_ID_OWNSHIP_REPORT = 0x0A # 10 - Ownship Pressure Altitude Report
MSG_ID_TRAFFIC_REPORT = 0x14 # 20
# Add other message IDs as needed (e.g., 0x01 Status, 0x07 ID)

# --- CRC Calculation (Fletcher-16 variant used by GDL90) ---
# Note: CRC is calculated *before* byte stuffing on the raw message payload (ID + Data)

def calculate_crc(message_payload):
    """Calculates the GDL90 Fletcher-16 checksum."""
    c0, c1 = 0, 0
    for byte in message_payload:
        c0 = (c0 + byte) % 256
        c1 = (c1 + c0) % 256
    # The checksum itself is part of the stream, but not included in *its own* calculation
    return bytes([c0, c1])

# --- Byte Stuffing ---

def byte_stuff(raw_payload_with_crc):
    """Performs GDL90 byte stuffing on the message payload including CRC."""
    stuffed = bytearray()
    for byte in raw_payload_with_crc:
        if byte == FLAG_BYTE:
            stuffed.append(CONTROL_ESCAPE)
            stuffed.append(FLAG_BYTE ^ ESCAPE_XOR) # 0x5E
        elif byte == CONTROL_ESCAPE:
            stuffed.append(CONTROL_ESCAPE)
            stuffed.append(CONTROL_ESCAPE ^ ESCAPE_XOR) # 0x5D
        else:
            stuffed.append(byte)
    return bytes(stuffed)

# --- Message Framing ---

def frame_message(message_payload):
    """Adds CRC, performs byte stuffing, and adds framing flags."""
    crc = calculate_crc(message_payload)
    payload_with_crc = message_payload + crc
    stuffed_payload = byte_stuff(payload_with_crc)
    return bytes([FLAG_BYTE]) + stuffed_payload + bytes([FLAG_BYTE])

# --- Helper Functions ---

def encode_lat_lon(degrees):
    """Encodes latitude or longitude into GDL90 3-byte format (2's complement semicircles)."""
    if degrees is None or not (-180 <= degrees <= 180):
        # Return None and let the calling function handle invalid data (e.g., set NIC=0)
        return None

    # GDL90 uses 2's complement representation based on semicircles
    # Range is -180 to +180 degrees. Max value is 2^23 semicircles.
    semicircles = int(round(degrees * (2**23 / 180.0)))

    # Pack as 3 bytes, big-endian, handling negative numbers (2's complement)
    if semicircles < 0:
        semicircles += 2**24 # Convert to 2's complement representation for 24 bits

    b1 = (semicircles >> 16) & 0xFF
    b2 = (semicircles >> 8) & 0xFF
    b3 = semicircles & 0xFF
    return bytes([b1, b2, b3])

def encode_altitude_pressure(feet):
    """Encodes pressure altitude in feet into GDL90 12-bit format (in 2 bytes)."""
    if feet is None:
        # 0xFFF represents invalid/unknown altitude
        return bytes([0x0F, 0xFF]) # Upper 4 bits are part of the 12 bits

    # Altitude is encoded in 25 ft increments, offset by -1000 ft.
    # Value = (Altitude_ft + 1000) / 25
    # Range: -1000 ft to +101350 ft
    encoded_alt = int(round((feet + 1000.0) / 25.0))

    if encoded_alt < 0: encoded_alt = 0
    if encoded_alt > 0xFFE: encoded_alt = 0xFFF # Use invalid if out of range (0xFFF)

    # Pack into 2 bytes (12 bits used)
    # Value = bbbb bbbb bbbb (12 bits)
    # Byte 1 = 0000 bbbb (bits 11-8)
    # Byte 2 = bbbb bbbb (bits 7-0)
    b1 = (encoded_alt >> 8) & 0x0F
    b2 = encoded_alt & 0xFF
    return bytes([b1, b2])

def encode_altitude_geometric(feet):
    """Encodes geometric (GNSS) altitude in feet into GDL90 16-bit format (in 2 bytes)."""
    if feet is None:
        # Use 0xFFFF for invalid/unknown geometric altitude
        return b'\xFF\xFF'

    # Altitude is encoded in 5 ft increments, offset by -1000 ft.
    # Value = (Altitude_ft + 1000) / 5
    # Range: -1000 ft to +317675 ft (using 16 bits for calculation range)
    encoded_alt = int(round((feet + 1000.0) / 5.0))

    if encoded_alt < 0: encoded_alt = 0
    if encoded_alt > 0xFFFE: encoded_alt = 0xFFFF # Use invalid if out of range

    # Pack into 2 bytes (16 bits), big-endian unsigned short
    return struct.pack('>H', encoded_alt)

def encode_velocity(knots):
    """Encodes horizontal velocity in knots into GDL90 12-bit format (in 2 bytes)."""
    if knots is None or knots < 0:
        return b'\x0F\xFF' # Invalid/Unknown (0xFFF)

    # Velocity is encoded in 1 knot increments. Range 0 to 4094 knots.
    encoded_vel = int(round(knots))
    if encoded_vel > 4094: encoded_vel = 4095 # Use 0xFFF for >4094 kts

    # Pack into 2 bytes (12 bits used)
    b1 = (encoded_vel >> 8) & 0x0F
    b2 = encoded_vel & 0xFF
    return bytes([b1, b2])

def encode_vertical_velocity(fpm):
    """Encodes vertical velocity in feet per minute into GDL90 12-bit signed format (in 2 bytes)."""
    if fpm is None:
        # Use 0x800 (-2048) which represents invalid/unknown in the 12-bit signed range
        # 0x800 -> 1000 0000 0000
        # Byte 1 = 1000, Byte 2 = 0000
        return b'\x08\x00'

    # Vertical velocity is encoded in 64 fpm increments.
    # Value = VV_fpm / 64
    # Range: -32768 fpm to +32704 fpm maps to 12-bit signed range -2048 to +2047
    encoded_vv = int(round(fpm / 64.0))

    # Clamp to 12-bit signed range
    if encoded_vv > 2047: encoded_vv = 2047
    if encoded_vv < -2047: encoded_vv = -2047 # Note: -2048 is technically invalid per spec? Use -2047.

    # Convert to 12-bit two's complement if negative
    if encoded_vv < 0:
        encoded_vv += 2**12

    # Pack into 2 bytes (12 bits used)
    b1 = (encoded_vv >> 8) & 0x0F
    b2 = encoded_vv & 0xFF
    return bytes([b1, b2])

def encode_track_heading(degrees):
    """Encodes track or heading in degrees into GDL90 8-bit format."""
    if degrees is None or not (0 <= degrees < 360):
        # Use 0, but rely on validity flags elsewhere if possible
        return b'\x00'

    # Encoded as value = degrees * (256 / 360)
    encoded = int(round(degrees * 256.0 / 360.0)) & 0xFF
    return bytes([encoded])

def encode_icao_address(icao_hex):
    """Encodes a 24-bit ICAO address (hex string) into 3 bytes."""
    try:
        icao_int = int(icao_hex, 16)
        if not (0 <= icao_int <= 0xFFFFFF):
             raise ValueError("ICAO address out of range")
        # Pack as 3 bytes, big-endian
        return struct.pack('>I', icao_int)[1:] # Use 4 bytes then take last 3
    except (ValueError, TypeError):
        return b'\x00\x00\x00' # Invalid

def encode_callsign(callsign):
    """Encodes a callsign (up to 8 chars) into 8 bytes, space padded."""
    if not callsign:
        return b'        ' # 8 spaces
    # Ensure ASCII, strip non-printable, pad/truncate to 8 chars
    cleaned = ''.join(c for c in callsign if 32 <= ord(c) <= 126)
    padded = cleaned.ljust(8)[:8]
    return padded.encode('ascii')


# --- Message Creation Functions ---

def create_heartbeat_message(gps_valid=False, maintenance_required=False, ident_active=False, utc_timing=True):
    """
    Creates a GDL90 Heartbeat message (ID 0x00). Version 1 GDL90.
    """
    message_id = MSG_ID_HEARTBEAT

    # Status byte 1: Uplink status, Basic/FIS-B status (Assume minimal capability)
    # Bit 7: UAT Initialized (0)
    # Bit 6: RATCS (Reserved, 0)
    # Bit 5: ATC CDTI (Traffic Display) Available (1 = Yes) - Set based on if we send traffic
    # Bit 4: ATC Ground Station Uplink (0 = No)
    # Bit 3: FIS-B Uplink Available (0 = No)
    # Bit 2-0: Reserved (0)
    status_byte1 = 0b00100000 # Assume CDTI available

    # Status byte 2: GPS status
    # Bit 7: Timestamp type (0=UTC, 1=GPS time)
    # Bit 6: GPS Position Valid (1=Valid, 0=Invalid)
    # Bit 5: Maintenance Required (1=Yes, 0=No)
    # Bit 4: IDENT state active (1=Yes, 0=No)
    # Bit 3: Reserved (set 1)
    # Bit 2: Reserved (set 1)
    # Bit 1: Reserved (set 1)
    # Bit 0: Reserved (set 1)
    status_byte2 = 0b00001111 # Base for reserved bits
    if not utc_timing: status_byte2 |= 0b10000000
    if gps_valid:      status_byte2 |= 0b01000000
    if maintenance_required: status_byte2 |= 0b00100000
    if ident_active:   status_byte2 |= 0b00010000

    # Timestamp: UTC seconds since midnight * 10, max 863999 (0xD2F1F), 21 bits
    now_utc = datetime.now(timezone.utc)
    seconds_since_midnight = (now_utc - now_utc.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    utc_timestamp_field = min(int(seconds_since_midnight * 10), 863999) & 0x1FFFFF

    ts_byte1 = (utc_timestamp_field >> 16) & 0xFF
    ts_byte2 = (utc_timestamp_field >> 8) & 0xFF
    ts_byte3 = utc_timestamp_field & 0xFF

    # Correct format string for 6 bytes: ID, Status1, Status2, TS1, TS2, TS3
    payload = struct.pack('>BBBBBB',
                          message_id,
                          status_byte1,
                          status_byte2,
                          ts_byte1, ts_byte2, ts_byte3)

    return frame_message(payload)


def create_ownship_report(lat, lon, alt_press, misc, nic, nac_p, ground_speed, track, vert_vel):
    """
    Creates a GDL90 Ownship Report message (ID 0x0A).
    Requires ownship pressure altitude, position, velocity etc.

    Args:
        lat (float): Latitude in degrees (-90 to 90)
        lon (float): Longitude in degrees (-180 to 180)
        alt_press (int): Pressure altitude in feet MSL.
        misc (int): Miscellaneous indicators (see GDL90 spec, e.g., 1 for Airborne)
        nic (int): Navigation Integrity Category (0-11)
        nac_p (int): Navigation Accuracy Category for Position (0-11)
        ground_speed (int): Ground speed in knots.
        track (int): True track in degrees (0-359).
        vert_vel (int): Vertical velocity in feet/minute (positive up).
    """
    message_id = MSG_ID_OWNSHIP_REPORT

    lat_bytes = encode_lat_lon(lat)
    lon_bytes = encode_lat_lon(lon)
    alt_bytes = encode_altitude_pressure(alt_press)

    # Handle invalid position/altitude according to spec
    if lat_bytes is None or lon_bytes is None:
        lat_bytes = b'\x00\x00\x00'
        lon_bytes = b'\x00\x00\x00'
        nic = 0 # NIC=0 indicates invalid position
        nac_p = 0 # NACp should also be 0 if NIC is 0
    if alt_bytes == bytes([0x0F, 0xFF]): # Check for invalid altitude encoding
        alt_bytes = bytes([0x0F, 0xFF]) # Ensure it's set if input was None

    # Combine NIC and NACp into one byte: (NIC << 4) | NACp
    nav_integrity_byte = ((nic & 0x0F) << 4) | (nac_p & 0x0F)

    gs_bytes = encode_velocity(ground_speed)
    track_byte = encode_track_heading(track)
    vv_bytes = encode_vertical_velocity(vert_vel)

    # Misc byte: Upper nibble = Misc flags (e.g., 0x10 for Airborne, 0x20 for On Ground)
    #            Lower nibble = Reserved (0)
    misc_byte = (misc & 0x0F) << 4

    payload = bytearray([message_id])
    payload.extend(lat_bytes)
    payload.extend(lon_bytes)
    payload.extend(alt_bytes)
    payload.append(misc_byte)
    payload.append(nav_integrity_byte)
    payload.extend(gs_bytes)
    payload.extend(vv_bytes)
    payload.append(track_byte)
    # Payload length = 1 + 3 + 3 + 2 + 1 + 1 + 2 + 2 + 1 = 16 bytes

    return frame_message(bytes(payload))

def create_ownship_geo_altitude(alt_geo, vpl):
    """
    Creates a GDL90 Ownship Geometric Altitude message (ID 0x0B).

    Args:
        alt_geo (int): Geometric (GNSS) altitude in feet MSL.
        vpl (int): Vertical Protection Limit (meters). Use 65535 if unknown.
                   GDL90 uses specific codes (see spec). 0xFFFF -> > 185m or unknown.
    """
    message_id = MSG_ID_OWNSHIP_GEO_ALT
    alt_bytes = encode_altitude_geometric(alt_geo)

    # VPL encoding (Table 3-8 in DO-282B / GDL90 Spec)
    # We need to map meters to the code. Let's assume unknown for now.
    # TODO: Implement proper VPL mapping if available
    vpl_code = 0xFFFF # Unknown or > 185m

    payload = bytearray([message_id])
    payload.extend(alt_bytes)
    payload.extend(struct.pack('>H', vpl_code)) # VPL is 2 bytes

    return frame_message(bytes(payload))


def create_traffic_report(icao, lat, lon, alt_press, misc, nic, nac_p, horiz_vel, vert_vel, track, emitter_cat, callsign):
    """
    Creates a GDL90 Traffic Report message (ID 0x14).

    Args:
        icao (str): 24-bit ICAO address (hex string, e.g., "AABBCC").
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        alt_press (int): Pressure altitude in feet MSL.
        misc (int): Traffic alert status (0=No alert, 1=Alert) + Address Type (0=ADS-B/ICAO, 1=Self-assigned, 2=TIS-B/Fine, 3=TIS-B/Coarse, 4=Surface, 5=Reserved)
                      Byte format: SSSS AAAA (S=Status, A=Addr Type)
        nic (int): Navigation Integrity Category (0-11).
        nac_p (int): Navigation Accuracy Category for Position (0-11).
        horiz_vel (int): Horizontal velocity (ground speed) in knots.
        vert_vel (int): Vertical velocity in feet/minute.
        track (int): True track/heading in degrees.
        emitter_cat (int): Emitter category (see GDL90 spec, e.g., 1=Light).
        callsign (str): Callsign (up to 8 chars).
    """
    message_id = MSG_ID_TRAFFIC_REPORT

    icao_bytes = encode_icao_address(icao)
    lat_bytes = encode_lat_lon(lat)
    # Corrected the function call for longitude
    lon_bytes = encode_lat_lon(lon)
    alt_bytes = encode_altitude_pressure(alt_press)

    # Handle invalid position/altitude
    if lat_bytes is None or lon_bytes is None:
        lat_bytes = b'\x00\x00\x00'
        lon_bytes = b'\x00\x00\x00'
        nic = 0
        nac_p = 0
    if alt_bytes == bytes([0x0F, 0xFF]):
        alt_bytes = bytes([0x0F, 0xFF]) # Ensure invalid marker is used

    # Combine NIC and NACp into one byte: (NIC << 4) | NACp
    nav_integrity_byte = ((nic & 0x0F) << 4) | (nac_p & 0x0F)

    vel_bytes = encode_velocity(horiz_vel)
    vv_bytes = encode_vertical_velocity(vert_vel)
    track_byte = encode_track_heading(track)
    callsign_bytes = encode_callsign(callsign)

    # Misc byte: Upper nibble = Alert Status (0=No, 1=Alert), Lower nibble = Address Type
    misc_byte = (misc & 0xFF)

    payload = bytearray([message_id])
    payload.append(misc_byte)
    payload.extend(icao_bytes)
    payload.extend(lat_bytes)
    payload.extend(lon_bytes)
    payload.extend(alt_bytes)
    payload.append(nav_integrity_byte)
    payload.extend(vel_bytes)
    payload.extend(vv_bytes)
    payload.append(track_byte)
    payload.append(emitter_cat & 0xFF)
    payload.extend(callsign_bytes)
    # Payload length = 1 + 1 + 3 + 3 + 3 + 2 + 1 + 2 + 2 + 1 + 1 + 8 = 28 bytes

    return frame_message(bytes(payload))


# --- Test Functions ---
if __name__ == '__main__':
    print("Testing GDL90 Module...")

    # Test Heartbeat
    hb_msg = create_heartbeat_message(gps_valid=True, utc_timing=True)
    print(f"Heartbeat: {hb_msg.hex().upper()}")

    # Test Ownship Report (Example Data)
    ownship_msg = create_ownship_report(
        lat=34.12345, lon=-118.54321, alt_press=10000, misc=1, # Airborne
        nic=8, nac_p=8, ground_speed=120, track=90, vert_vel=500
    )
    if ownship_msg:
        print(f"Ownship Report: {ownship_msg.hex().upper()}")

    # Test Ownship Geo Altitude
    ownship_geo_msg = create_ownship_geo_altitude(alt_geo=10250, vpl=0xFFFF)
    if ownship_geo_msg:
        print(f"Ownship Geo Alt: {ownship_geo_msg.hex().upper()}")

    # Test Traffic Report (Example Data)
    traffic_msg = create_traffic_report(
        icao="AABBCC", lat=34.12500, lon=-118.54000, alt_press=11000,
        misc=0x00, # No Alert (0 << 4), ADS-B ICAO address type (0)
        nic=8, nac_p=8, horiz_vel=150, vert_vel=-200, track=270,
        emitter_cat=1, # Light aircraft
        callsign="N12345"
    )
    if traffic_msg:
        print(f"Traffic Report: {traffic_msg.hex().upper()}")

    # Test byte stuffing edge cases
    payload_needs_stuffing = bytes([0x00, 0x7E, 0x14, 0x7D, 0xAB])
    framed_stuffed = frame_message(payload_needs_stuffing)
    print(f"Original Payload: {payload_needs_stuffing.hex().upper()}")
    # Expected CRC: C0=99 (0x63), C1=99+20+125+171 = 415 -> 159 (0x9F) -> CRC = 63 9F
    # Payload + CRC: 00 7E 14 7D AB 63 9F
    # Stuffed: 7E 00 7D 5E 14 7D 5D AB 63 9F 7E
    print(f"Framed & Stuffed: {framed_stuffed.hex().upper()}")

    # Test invalid values
    invalid_alt_msg = create_ownship_report(lat=34, lon=-118, alt_press=None, misc=1, nic=8, nac_p=8, ground_speed=100, track=180, vert_vel=0)
    print(f"Ownship Invalid Alt: {invalid_alt_msg.hex().upper()}")
    invalid_pos_msg = create_ownship_report(lat=None, lon=None, alt_press=5000, misc=1, nic=8, nac_p=8, ground_speed=100, track=180, vert_vel=0)
    print(f"Ownship Invalid Pos: {invalid_pos_msg.hex().upper()}")
    invalid_vv_msg = create_traffic_report("C0FFEE", 34, -118, 12000, 0x00, 8, 8, 200, None, 90, 1, "TEST")
    print(f"Traffic Invalid VV: {invalid_vv_msg.hex().upper()}")

    # Test longitude encoding fix
    traffic_msg_lon_fix = create_traffic_report(
        icao="AABBCC", lat=34.12500, lon=-118.54000, alt_press=11000,
        misc=0x00, nic=8, nac_p=8, horiz_vel=150, vert_vel=-200, track=270,
        emitter_cat=1, callsign="N12345"
    )
    if traffic_msg_lon_fix:
        print(f"Traffic Report (Lon Fix): {traffic_msg_lon_fix.hex().upper()}")