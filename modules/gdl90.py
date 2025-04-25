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

# --- CRC Calculation (CRC-16-CCITT as per GDL90 Spec) ---
# Note: CRC is calculated *before* byte stuffing on the raw message payload (ID + Data)

CRC16Table = (
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
)

def calculate_crc(data: bytes) -> bytes:
    """Calculates the GDL90 CRC-16-CCITT checksum."""
    mask16bit = 0xffff
    crc = 0
    for byte in data:
        # Python 3 bytes are already ints, no need for ord()
        m = (crc << 8) & mask16bit
        # Ensure byte is treated as an integer index
        crc = CRC16Table[(crc >> 8)] ^ m ^ byte
    
    # Return CRC bytes in LSB, MSB order as required by GDL90
    crc_bytes = bytearray()
    crc_bytes.append(crc & 0x00ff)       # LSB
    crc_bytes.append((crc & 0xff00) >> 8) # MSB
    return bytes(crc_bytes)

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
    crc_bytes = calculate_crc(message_payload) # Returns LSB, MSB
    payload_with_crc = message_payload + crc_bytes
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
    # Bit 7: Reserved (0) - Will be set to bit 16 of timestamp below
    # Bit 6: GPS Position Valid (1=Valid, 0=Invalid)
    # Bit 5: Maintenance Required (1=Yes, 0=No)
    # Bit 4: IDENT state active (1=Yes, 0=No)
    # Bit 3: Reserved (set 1)
    # Bit 2: Reserved (set 1)
    # Bit 1: Reserved (set 1)
    # Bit 0: Reserved (set 1)
    status_byte2 = 0b00001111 # Base for reserved bits
    if gps_valid:      status_byte2 |= 0b01000000
    if maintenance_required: status_byte2 |= 0b00100000
    if ident_active:   status_byte2 |= 0b00010000
    if not utc_timing: status_byte2 |= 0b00000000  # No effect, just for clarity

    # Timestamp: UTC seconds since midnight * 10, max 863999 (0xD2F1F), 21 bits
    now_utc = datetime.now(timezone.utc)
    seconds_since_midnight = (now_utc - now_utc.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    utc_timestamp_field = min(int(seconds_since_midnight * 10), 863999)
    
    # Move bit 16 of the timestamp into the MSB of status byte 2
    ts_bit16 = (utc_timestamp_field & 0x10000) >> 16
    status_byte2 = (status_byte2 & 0b01111111) | (ts_bit16 << 7)
    
    # Pack timestamp as little-endian for the lower 16 bits (GDL90 specification)
    ts_lower_16bits = utc_timestamp_field & 0xFFFF
    ts_byte1 = ts_lower_16bits & 0xFF           # LSB
    ts_byte2 = (ts_lower_16bits >> 8) & 0xFF    # MSB

    # Format message with 6 bytes: ID, Status1, Status2, TS1(LSB), TS2(MSB)
    # Note that we're packing the timestamp in little-endian format
    payload = struct.pack('>BBB',  # The message ID and status bytes are big-endian
                          message_id,
                          status_byte1,
                          status_byte2)
    
    payload += struct.pack('<BB',  # The timestamp is little-endian
                           ts_byte1, 
                           ts_byte2)

    # We don't include a message count field as it's not in our current implementation
    # The spec mentions it's optional

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
    payload.extend(track_byte)    # Use extend instead of append for bytes object
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


def create_traffic_report(icao, lat, lon, alt_press, misc, nic, nac_p, horiz_vel, vert_vel, track, emitter_cat, callsign, code=0):
    """
    Creates a GDL90 Traffic Report message (ID 0x14).

    Args:
        icao (str): 24-bit ICAO address (hex string, e.g., "AABBCC").
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        alt_press (int): Pressure altitude in feet MSL.
        misc (int): Miscellaneous indicators (0-15, see GDL90 spec).
        nic (int): Navigation Integrity Category (0-11).
        nac_p (int): Navigation Accuracy Category for Position (0-11).
        horiz_vel (int): Horizontal velocity (ground speed) in knots.
        vert_vel (int): Vertical velocity in feet/minute.
        track (int): True track/heading in degrees.
        emitter_cat (int): Emitter category (see GDL90 spec, e.g., 1=Light).
        callsign (str): Callsign (up to 8 chars).
        code (int): Reserved field (0-15), typically 0.
    """
    message_id = MSG_ID_TRAFFIC_REPORT

    # First byte is traffic alert status in upper 4 bits, address type in lower 4 bits
    status_byte = misc
    
    # Pack ICAO address as 3 bytes
    if isinstance(icao, str):
        try:
            icao_int = int(icao, 16)
            if not (0 <= icao_int <= 0xFFFFFF):
                icao_int = 0  # Use 0 for invalid
        except (ValueError, TypeError):
            icao_int = 0  # Use 0 for invalid
    else:
        icao_int = icao if isinstance(icao, int) and 0 <= icao <= 0xFFFFFF else 0
    
    # Encode latitude and longitude
    if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        lat_int = 0
        lon_int = 0
        nic = 0  # NIC=0 indicates invalid position
        nac_p = 0  # NACp should also be 0 if NIC is 0
    else:
        # Convert to semicircles per GDL90 spec
        lat_int = int(lat * (0x800000 / 180.0))
        if lat_int < 0:
            lat_int = (0x1000000 + lat_int) & 0xFFFFFF  # 2's complement for 24 bits
            
        lon_int = int(lon * (0x800000 / 180.0))
        if lon_int < 0:
            lon_int = (0x1000000 + lon_int) & 0xFFFFFF  # 2's complement for 24 bits
    
    # Process altitude
    if alt_press is None:
        alt_enc = 0xFFF  # Invalid/Unknown altitude
    else:
        # Altitude in 25ft increments offset by +1000ft
        alt_enc = int((alt_press + 1000) / 25.0)
        if alt_enc < 0:
            alt_enc = 0
        if alt_enc > 0xFFE:
            alt_enc = 0xFFE  # Max valid value (avoid using 0xFFF which is reserved for invalid)
    
    # Navigation integrity and accuracy
    nic_val = nic if nic is not None else 0
    nac_p_val = nac_p if nac_p is not None else 0
    nav_integrity_byte = ((nic_val & 0x0F) << 4) | (nac_p_val & 0x0F)
    
    # Process horizontal velocity
    if horiz_vel is None:
        h_vel = 0xFFF  # Invalid/Unknown
    elif horiz_vel < 0:
        h_vel = 0
    elif horiz_vel > 0xFFE:
        h_vel = 0xFFE  # Max valid value
    else:
        h_vel = int(round(horiz_vel))
    
    # Process vertical velocity
    if vert_vel is None:
        v_vel = 0x800  # Invalid/Unknown (-2048 in 12-bit 2's complement)
    else:
        # Convert to 64fpm increments
        v_vel = int(vert_vel / 64.0)
        
        # Clamp to valid range
        if v_vel > 2047:
            v_vel = 2047
        elif v_vel < -2047:
            v_vel = -2047  # Avoid -2048 which is the invalid marker
            
        # Convert to 12-bit 2's complement if negative
        if v_vel < 0:
            v_vel = (0x1000 + v_vel) & 0xFFF  # 12-bit 2's complement
    
    # Process track/heading
    if track is None or not (0 <= track < 360):
        track_enc = 0
    else:
        track_enc = int(track * (256.0 / 360.0)) & 0xFF
    
    # Process emitter category
    emitter = emitter_cat if emitter_cat is not None else 0
    emitter = emitter & 0xFF
    
    # Process callsign
    if not callsign:
        callsign_bytes = b'        '  # 8 spaces
    else:
        # Ensure ASCII, strip non-printable, pad/truncate to 8 chars
        cleaned = ''.join(c for c in callsign if 32 <= ord(c) <= 126)
        padded = cleaned.ljust(8)[:8]
        callsign_bytes = padded.encode('ascii')
    
    # Build the message payload
    payload = bytearray([message_id])
    
    # Status byte (alert status in upper 4 bits, address type in lower 4 bits)
    payload.append(status_byte & 0xFF)
    
    # ICAO address (3 bytes)
    payload.append((icao_int >> 16) & 0xFF)
    payload.append((icao_int >> 8) & 0xFF)
    payload.append(icao_int & 0xFF)
    
    # Latitude (3 bytes)
    payload.append((lat_int >> 16) & 0xFF)
    payload.append((lat_int >> 8) & 0xFF)
    payload.append(lat_int & 0xFF)
    
    # Longitude (3 bytes)
    payload.append((lon_int >> 16) & 0xFF)
    payload.append((lon_int >> 8) & 0xFF)
    payload.append(lon_int & 0xFF)
    
    # Altitude (2 bytes) - top 8 bits in first byte, low 4 bits combined with misc in second byte
    payload.append((alt_enc >> 4) & 0xFF)
    payload.append(((alt_enc & 0x0F) << 4) | (misc & 0x0F))
    
    # Navigation integrity/accuracy
    payload.append(nav_integrity_byte)
    
    # Velocities (3 bytes combined) - exact byte ordering from GDL90 spec
    payload.append((h_vel >> 4) & 0xFF)  # Top 8 bits of horizontal velocity
    payload.append(((h_vel & 0x0F) << 4) | ((v_vel >> 8) & 0x0F))  # Bottom 4 bits of h_vel + top 4 bits of v_vel
    payload.append(v_vel & 0xFF)  # Bottom 8 bits of vertical velocity
    
    # Track/heading (1 byte)
    payload.append(track_enc)
    
    # Emitter category (1 byte)
    payload.append(emitter)
    
    # Callsign (8 bytes)
    payload.extend(callsign_bytes)
    
    # Code field (1 byte) - code in top 4 bits, bottom 4 bits are spare
    payload.append((code & 0x0F) << 4)
    
    # Payload length = 1 + 1 + 3 + 3 + 3 + 2 + 1 + 3 + 1 + 1 + 8 + 1 = 28 bytes
    
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
