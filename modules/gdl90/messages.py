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
    # Bit 3-0: Reserved (set to match reference implementation)
    status_byte2 = 0b00000000  # Base value
    if gps_valid:      status_byte2 |= 0b01000000
    if maintenance_required: status_byte2 |= 0b00100000
    if ident_active:   status_byte2 |= 0b00010000
    
    # Set reserved bits to match reference implementation
    status_byte2 |= 0b00000000  # All reserved bits set to 0

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


def create_ownship_report(lat, lon, alt_press, misc, nic, nac_p, ground_speed, track, vert_vel, emitter_cat=1, callsign="", code=0):
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
        emitter_cat (int): Emitter category (see GDL90 spec, e.g., 1=Light, default=1).
        callsign (str): Callsign (up to 8 chars, default="").
        code (int): Reserved field (0-15, typically 0, default=0).
        
    Returns:
        Complete framed GDL90 Ownship Report message
    """
    message_id = MSG_ID_OWNSHIP_REPORT

    lat_bytes = encode_lat_lon(lat, is_latitude=True)
    lon_bytes = encode_lat_lon(lon, is_latitude=False)
    
    # Encode altitude using the corrected encoder (no misc)
    alt_bytes = encode_altitude_pressure(alt_press)

    # Handle invalid position/altitude according to spec
    if lat_bytes is None or lon_bytes is None:
        lat_bytes = b'\x00\x00\x00'
        lon_bytes = b'\x00\x00\x00'
        nic = 0  # NIC=0 indicates invalid position
        nac_p = 0  # NACp should also be 0 if NIC is 0

    # Combine NIC and NACp into one byte: (NIC << 4) | NACp
    nav_integrity_byte = ((nic & 0x0F) << 4) | (nac_p & 0x0F)

    gs_bytes = encode_velocity(ground_speed)
    track_byte = encode_track_heading(track)
    vv_bytes = encode_vertical_velocity(vert_vel)
    
    # Encode callsign (8 bytes)
    callsign_bytes = encode_callsign(callsign)

    # Assemble the payload according to GDL90 Ownship Report spec (Table 6 & Figure 2)
    # Total length must be 28 bytes including the Message ID.
    payload = bytearray([message_id])         # Byte 1: Message ID (len=1)

    # Byte 2: Status byte (Alert Status upper 4 bits=0, Address Type lower 4 bits=0 for Ownship)
    payload.append(0x00)                      # Byte 2: Status (len=2)

    # Bytes 3-5: Participant Address (ICAO). Use 0 for Ownship.
    payload.append(0)                         # Byte 3: ICAO MSB (len=3)
    payload.append(0)                         # Byte 4: ICAO middle (len=4)
    payload.append(0)                         # Byte 5: ICAO LSB (len=5)

    # Bytes 6-11: Position data
    payload.extend(lat_bytes)                 # Bytes 6-8: Latitude (len=8)
    payload.extend(lon_bytes)                 # Bytes 9-11: Longitude (len=11)

    # Bytes 12-13: Altitude (12 bits) + Misc (4 bits)
    # Need the raw 12-bit encoded altitude value before applying offset
    encoded_alt_12bit = 0xFFF # Default to invalid
    if alt_press is not None:
        # Reverse the formula: Value = (Altitude_ft + 1000) / 25
        encoded_alt_12bit = round((alt_press + 1000) / 25)
        if not (0 <= encoded_alt_12bit <= 0xFFE): # Check valid range (0xFFF is invalid)
            encoded_alt_12bit = 0xFFF

    # Pack Altitude (upper 8 bits) into Byte 12
    payload.append((encoded_alt_12bit >> 4) & 0xFF) # Byte 12 (len=12)
    # Pack Altitude (lower 4 bits) + Misc (lower 4 bits) into Byte 13
    byte13 = ((encoded_alt_12bit & 0x0F) << 4) | (misc & 0x0F)
    payload.append(byte13)                    # Byte 13 (len=13)

    # Byte 14: Navigation/accuracy info
    payload.append(nav_integrity_byte)        # Byte 14: NIC/NACp (len=14)

    # Bytes 15-19: Velocity information
    payload.extend(gs_bytes)                  # Bytes 15-16: Ground Speed (len=16)
    payload.extend(vv_bytes)                  # Bytes 17-18: Vertical Velocity (len=18)
    payload.extend(track_byte)                # Byte 19: Track/Heading (len=19)

    # Byte 20: Emitter Category
    payload.append(emitter_cat & 0xFF)        # Byte 20: Emitter Category (len=20)

    # Bytes 21-28: Callsign (8 bytes)
    payload.extend(callsign_bytes)            # Bytes 21-28: Callsign (len=28)

    # Note: The Emergency/Priority code ('code' arg) is not explicitly placed
    # as a separate byte in the 28-byte structure according to Figure 2.
    # It might be implicitly part of the 'misc' field or other status bits
    # depending on the exact interpretation, but we adhere to the 28-byte total.

    # Ensure the final payload is exactly 28 bytes before framing
    if len(payload) != 28:
       # This check ensures our manual packing logic is correct.
       raise ValueError(f"Internal Error: Ownship report payload length is {len(payload)}, expected 28")

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


def create_traffic_report(icao, lat, lon, alt_press, misc_flags, nic, nac_p, horiz_vel, vert_vel, track, emitter_cat, callsign, address_type=0, alert_status=0, code=0):
    """
    Creates a GDL90 Traffic Report message (ID 0x14).

    Args:
        icao (str): 24-bit ICAO address (hex string, e.g., "AABBCC").
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        alt_press (int): Pressure altitude in feet MSL.
        misc_flags (int): Miscellaneous indicators (Airborne status bit 3, Track Type bits 1-0 - see GDL90 spec Table 9).
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
    """
    Creates a GDL90 Traffic Report message (ID 0x14).

    Args:
        icao (str): 24-bit ICAO address (hex string, e.g., "AABBCC").
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        alt_press (int): Pressure altitude in feet MSL.
        misc_flags (int): Miscellaneous indicators (Airborne status bit 3, Track Type bits 1-0 - see GDL90 spec Table 9).
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
    # Status byte (Byte 2): Alert Status (bits 7-4), Address Type (bits 3-0)
    status_byte = ((alert_status & 0x0F) << 4) | (address_type & 0x0F)
    
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
    
    # Use shared encoder functions for lat/lon
    lat_bytes = encode_lat_lon(lat, is_latitude=True)
    lon_bytes = encode_lat_lon(lon, is_latitude=False)
    
    # Handle invalid position according to spec
    if lat_bytes is None or lon_bytes is None:
        lat_bytes = b'\x00\x00\x00'
        lon_bytes = b'\x00\x00\x00'
        nic = 0  # NIC=0 indicates invalid position
        nac_p = 0  # NACp should also be 0 if NIC is 0
    
    # Navigation integrity and accuracy
    nic_val = nic if nic is not None else 0
    nac_p_val = nac_p if nac_p is not None else 0
    nav_integrity_byte = ((nic_val & 0x0F) << 4) | (nac_p_val & 0x0F)
    
    # We'll use the shared encoder functions for these values
    # The actual encoding will happen when we build the payload
    
    # Use shared encoder functions for emitter category and callsign
    callsign_bytes = encode_callsign(callsign)
    
    # --- Debug: Print input values ---
    print(f"\nDEBUG create_traffic_report - Input values:")
    print(f"  icao: {icao}, lat: {lat:.4f}, lon: {lon:.4f}")
    print(f"  alt_press: {alt_press}, misc_flags: {misc_flags}, nic: {nic}, nac_p: {nac_p}")
    print(f"  horiz_vel: {horiz_vel}, vert_vel: {vert_vel}, track: {track}")
    print(f"  emitter_cat: {emitter_cat}, callsign: {callsign}")
    # --- End Debug ---

    # Build the message payload
    payload = bytearray([message_id])

    # Status byte (alert status in upper 4 bits, address type in lower 4 bits)
    payload.append(status_byte & 0xFF)
    
    # ICAO address (3 bytes)
    payload.append((icao_int >> 16) & 0xFF)
    payload.append((icao_int >> 8) & 0xFF)
    payload.append(icao_int & 0xFF)
    
    # Add latitude and longitude bytes
    payload.extend(lat_bytes)
    payload.extend(lon_bytes)
    
    # --- Assemble Bytes 12-19 according to GDL90 Figure 2 ---

    # Bytes 12-13: Altitude (12 bits) + Misc (4 bits)
    # Get the pre-encoded 2 bytes for altitude
    alt_encoded_bytes = encode_altitude_pressure(alt_press)
    # Byte 12 is the first byte from the encoder (Alt bits 11-4)
    payload.append(alt_encoded_bytes[0])
    # Byte 13 combines the lower nibble of the second altitude byte (Alt bits 3-0)
    # with the misc field (lower 4 bits)
    # Byte 13: Altitude bits 3-0 (upper nibble), Misc flags (lower nibble)
    # Ensure only relevant misc_flags (Airborne, Track Type) are used here.
    byte13 = (alt_encoded_bytes[1] & 0xF0) | (misc_flags & 0x0F)
    payload.append(byte13)

    # Byte 14: Navigation integrity/accuracy
    payload.append(nav_integrity_byte)

    # Bytes 15-16: Horizontal Velocity (12 bits) + VV Sign (1 bit)
    # Get the pre-encoded 2 bytes for horizontal velocity
    hv_encoded_bytes = encode_velocity(horiz_vel)
    vv_sign_bit = 1 if (vert_vel is not None and vert_vel < 0) else 0
    # Byte 15 is the first byte from the encoder (HV bits 11-4)
    payload.append(hv_encoded_bytes[0])
    # Byte 16 combines the lower nibble of the second HV byte (HV bits 3-0)
    # with the VV sign bit (shifted into bit 3)
    byte16 = (hv_encoded_bytes[1] & 0xF0) | (vv_sign_bit << 3) # Reserved bits 2-0 are 0
    payload.append(byte16)

    # Bytes 17-18: Vertical Velocity (11 bits magnitude) + Track Type (1 bit)
    # Calculate the 11-bit magnitude for VV
    encoded_vv_11bit_mag = 0x7FF # Default invalid
    if vert_vel is not None:
        # Value = abs(VV_fpm / 64), max 2047 (0x7FF)
        encoded_vv_11bit_mag = round(abs(vert_vel) / 64.0)
        if encoded_vv_11bit_mag > 2047: encoded_vv_11bit_mag = 2047
    # Track type bit in byte 18
    # 0 = True track angle (to match misc_flags=0x01)
    # 1 = Magnetic heading
    track_type_bit = 0 # Explicitly use 0 for True Track Angle
    # Byte 17 contains VV magnitude bits 10-3
    byte17 = (encoded_vv_11bit_mag >> 3) & 0xFF
    # Byte 18 combines VV magnitude bits 2-0 (shifted left 5)
    # with the track type bit (shifted left 4)
    byte18 = ((encoded_vv_11bit_mag & 0x07) << 5) | (track_type_bit << 4) # Reserved bits 3-0 are 0
    payload.append(byte17)
    payload.append(byte18)

    # Byte 19: Track/Heading (8 bits)
    track_byte = encode_track_heading(track)
    payload.extend(track_byte)

    # Emitter category (8 bits)
    payload.append(emitter_cat & 0xFF)  # Byte 20
    
    # Callsign (8 bytes)
    payload.extend(callsign_bytes)
    
    # Code (4 bits) + Emergency/Priority Code (4 bits)
    # For now, set both to 0
    payload.append(((code & 0x0F) << 4) | 0x00)
    
    # Payload length = 1(ID) + 1(Status) + 3(ICAO) + 3(lat) + 3(lon) + 2(alt) + 1(NIC/NAC)
    #                  + 2(Horiz) + 2(Vert) + 1(Track) + 1(Emit) + 8(Callsign) + 1(Codes) = 29 bytes
    
    return frame_message(bytes(payload))