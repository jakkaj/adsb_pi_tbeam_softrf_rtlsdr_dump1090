"""
GDL90 message creation functions.

This module provides functions for creating various types of GDL90 messages
(Heartbeat, Ownship Report, Traffic Report, etc.) in their complete form,
ready for transmission.
"""
import struct
from datetime import datetime, timezone

from .constants import (
    MSG_ID_HEARTBEAT,
    MSG_ID_OWNSHIP_REPORT,
    MSG_ID_OWNSHIP_GEO_ALT,
    MSG_ID_TRAFFIC_REPORT
)
from .encoders import (
    encode_lat_lon,
    encode_altitude_pressure,
    encode_altitude_geometric,
    encode_velocity,
    encode_vertical_velocity,
    encode_track_heading,
    encode_icao_address,
    encode_callsign
)
from .framing import frame_message


def create_heartbeat_message(gps_valid=False, maintenance_required=False, ident_active=False, utc_timing=True):
    """
    Creates a GDL90 Heartbeat message (ID 0x00). Version 1 GDL90.
    
    Args:
        gps_valid: Whether the GPS position is valid
        maintenance_required: Whether maintenance is required
        ident_active: Whether the IDENT state is active
        utc_timing: Whether UTC timing is used
        
    Returns:
        Complete framed GDL90 Heartbeat message
    """
    message_id = MSG_ID_HEARTBEAT

    # Status byte 1: Uplink status, Basic/FIS-B status (Assume minimal capability)
    # Bit 7: UAT Initialized (0)
    # Bit 6: RATCS (Reserved, 0)
    # Bit 5: ATC CDTI (Traffic Display) Available (1 = Yes) - Set based on if we send traffic
    # Bit 4: ATC Ground Station Uplink (0 = No)
    # Bit 3: FIS-B Uplink Available (0 = No)
    # Bit 2-0: Reserved (0)
    status_byte1 = 0b00100000  # Assume CDTI available

    # Status byte 2: GPS status
    # Bit 7: Reserved (0) - Will be set to bit 16 of timestamp below
    # Bit 6: GPS Position Valid (1=Valid, 0=Invalid)
    # Bit 5: Maintenance Required (1=Yes, 0=No)
    # Bit 4: IDENT state active (1=Yes, 0=No)
    # Bit 3: Reserved (set 1)
    # Bit 2: Reserved (set 1)
    # Bit 1: Reserved (set 1)
    # Bit 0: Reserved (set 1)
    status_byte2 = 0b00001111  # Base for reserved bits
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

    # Format message with 7 bytes: ID, Status1, Status2, TS1(LSB), TS2(MSB), UplinkCount, BasicLongCount
    # Note that we're packing the timestamp in little-endian format
    payload = struct.pack('>BBB',  # The message ID and status bytes are big-endian
                        message_id,
                        status_byte1,
                        status_byte2)
    
    payload += struct.pack('<BB',  # The timestamp is little-endian
                        ts_byte1,
                        ts_byte2)

    # Add message count fields (UplinkCount, Basic/LongCount) as required by GDL90 spec
    # Set both to zero for now
    payload += struct.pack('BB', 0, 0)

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
        
    Returns:
        Complete framed GDL90 Ownship Report message
    """
    message_id = MSG_ID_OWNSHIP_REPORT

    lat_bytes = encode_lat_lon(lat)
    lon_bytes = encode_lat_lon(lon)
    alt_bytes = encode_altitude_pressure(alt_press)

    # Handle invalid position/altitude according to spec
    if lat_bytes is None or lon_bytes is None:
        lat_bytes = b'\x00\x00\x00'
        lon_bytes = b'\x00\x00\x00'
        nic = 0  # NIC=0 indicates invalid position
        nac_p = 0  # NACp should also be 0 if NIC is 0
    if alt_bytes == bytes([0x0F, 0xFF]):  # Check for invalid altitude encoding
        alt_bytes = bytes([0x0F, 0xFF])  # Ensure it's set if input was None

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
                   
    Returns:
        Complete framed GDL90 Ownship Geometric Altitude message
    """
    message_id = MSG_ID_OWNSHIP_GEO_ALT
    alt_bytes = encode_altitude_geometric(alt_geo)

    # VPL encoding (Table 3-8 in DO-282B / GDL90 Spec)
    # We need to map meters to the code. Let's assume unknown for now.
    # TODO: Implement proper VPL mapping if available
    vpl_code = 0xFFFF  # Unknown or > 185m

    payload = bytearray([message_id])
    payload.extend(alt_bytes)
    payload.extend(struct.pack('>H', vpl_code))  # VPL is 2 bytes

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
        
    Returns:
        Complete framed GDL90 Traffic Report message
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
    
    # Altitude (12 bits, packed in 2 bytes)
    # First 4 bits of first byte are from altitude, last 4 bits are 0 (reserved)
    payload.append((alt_enc >> 8) & 0x0F)
    payload.append(alt_enc & 0xFF)
    
    # Navigation integrity/accuracy
    payload.append(nav_integrity_byte)
    
    # Horizontal velocity (12 bits, packed in 2 bytes)
    payload.append((h_vel >> 8) & 0x0F)
    payload.append(h_vel & 0xFF)
    
    # Vertical velocity (12 bits, packed in 2 bytes)
    payload.append((v_vel >> 8) & 0x0F)
    payload.append(v_vel & 0xFF)
    
    # Track/heading (8 bits)
    payload.append(track_enc)
    
    # Emitter category (8 bits)
    payload.append(emitter)
    
    # Callsign (8 bytes)
    payload.extend(callsign_bytes)
    
    # Code (4 bits) + Emergency/Priority Code (4 bits)
    # For now, set both to 0
    payload.append(((code & 0x0F) << 4) | 0x00)
    
    # Payload length = 1(ID) + 1(Status) + 3(ICAO) + 3(lat) + 3(lon) + 2(alt) + 1(NIC/NAC)
    #                  + 2(Horiz) + 2(Vert) + 1(Track) + 1(Emit) + 8(Callsign) + 1(Codes) = 29 bytes
    
    return frame_message(bytes(payload))