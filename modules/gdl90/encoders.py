"""
GDL90 data encoding functions.

This module provides functions for encoding various data types (latitude, longitude,
altitude, velocity, etc.) into the specific binary formats required by the GDL90 protocol.
"""
import struct
import math


def encode_lat_lon(degrees):
    """
    Encodes latitude or longitude into GDL90 3-byte format (2's complement semicircles).
    
    Args:
        degrees: Latitude or longitude in degrees (-180 to 180)
        
    Returns:
        3-byte encoding of the position or None if invalid
    """
    # Only return None for None input
    if degrees is None:
        return None
    
    # For all other values, clamp to valid range and encode
    # This ensures consistent behavior with the rest of the codebase
    clamped_degrees = max(-180.0, min(180.0, degrees))
    
    # GDL90 uses 2's complement representation based on semicircles
    # Range is -180 to +180 degrees. Max value is 2^23 semicircles.
    semicircles = int(round(clamped_degrees * (2**23 / 180.0)))

    # Pack as 3 bytes, big-endian, handling negative numbers (2's complement)
    if semicircles < 0:
        semicircles += 2**24  # Convert to 2's complement representation for 24 bits

    b1 = (semicircles >> 16) & 0xFF
    b2 = (semicircles >> 8) & 0xFF
    b3 = semicircles & 0xFF
    return bytes([b1, b2, b3])


def encode_altitude_pressure(feet, misc=0):
    """
    Encodes pressure altitude in feet into GDL90 12-bit format (in 2 bytes).
    
    Args:
        feet: Altitude in feet MSL
        misc: Miscellaneous indicators (0-15) to include in lower 4 bits of second byte
        
    Returns:
        2-byte encoding of the pressure altitude
    """
    if feet is None:
        # 0xFFF represents invalid/unknown altitude
        # For invalid altitude, we don't include misc bits to match reference implementation
        return bytes([0x0F, 0xFF])  # Upper 4 bits are part of the 12 bits

    # Altitude is encoded in 25 ft increments, offset by -1000 ft.
    # Value = (Altitude_ft + 1000) / 25
    # Range: -1000 ft to +101350 ft
    encoded_alt = int(round((feet + 1000.0) / 25.0))

    if encoded_alt < 0:
        encoded_alt = 0
    if encoded_alt > 0xFFE:
        encoded_alt = 0xFFE  # Use 0xFFE for max valid value (avoid 0xFFF which is invalid)

    # Pack into 2 bytes according to GDL90 spec
    # First byte: bits 11-4 of altitude (top 8 bits)
    # Second byte: bits 3-0 of altitude (bottom 4 bits) in upper nibble, misc in lower nibble
    b1 = (encoded_alt & 0xFF0) >> 4  # Top 8 bits (bits 11-4)
    b2 = ((encoded_alt & 0x00F) << 4) | (misc & 0x0F)  # Bottom 4 bits + misc
    
    # For debugging
    # print(f"Altitude: {feet} ft -> Encoded: {encoded_alt} -> Bytes: {b1:02X} {b2:02X}")
    
    return bytes([b1, b2])


def encode_altitude_geometric(feet):
    """
    Encodes geometric (GNSS) altitude in feet into GDL90 16-bit format (in 2 bytes).
    
    Args:
        feet: Geometric altitude in feet MSL
        
    Returns:
        2-byte encoding of the geometric altitude
    """
    if feet is None:
        # Use 0xFFFF for invalid/unknown geometric altitude
        return b'\xFF\xFF'

    # Altitude is encoded in 5 ft increments, offset by -1000 ft.
    # Value = (Altitude_ft + 1000) / 5
    # Range: -1000 ft to +317675 ft (using 16 bits for calculation range)
    encoded_alt = int(round((feet + 1000.0) / 5.0))

    if encoded_alt < 0:
        encoded_alt = 0
    if encoded_alt > 0xFFFE:
        encoded_alt = 0xFFFF  # Use invalid if out of range

    # Pack into 2 bytes (16 bits), big-endian unsigned short
    return struct.pack('>H', encoded_alt)


def encode_velocity(knots):
    """
    Encodes horizontal velocity in knots into GDL90 12-bit format (in 2 bytes).
    
    Args:
        knots: Velocity in knots
        
    Returns:
        2-byte encoding of the velocity
    """
    if knots is None or knots < 0:
        return b'\x0F\xFF'  # Invalid/Unknown (0xFFF)

    # Velocity is encoded in 1 knot increments. Range 0 to 4094 knots.
    encoded_vel = int(round(knots))
    if encoded_vel > 4094:
        encoded_vel = 4095  # Use 0xFFF for >4094 kts

    # Pack into 2 bytes (12 bits used)
    b1 = (encoded_vel >> 8) & 0x0F
    b2 = encoded_vel & 0xFF
    return bytes([b1, b2])


def encode_vertical_velocity(fpm):
    """
    Encodes vertical velocity in feet per minute into GDL90 12-bit signed format (in 2 bytes).
    
    Args:
        fpm: Vertical velocity in feet per minute (positive up)
        
    Returns:
        2-byte encoding of the vertical velocity
    """
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
    if encoded_vv > 2047:
        encoded_vv = 2047
    if encoded_vv < -2047:
        encoded_vv = -2047  # Note: -2048 is technically invalid per spec? Use -2047.

    # Convert to 12-bit two's complement if negative
    if encoded_vv < 0:
        encoded_vv += 2**12

    # Pack into 2 bytes (12 bits used)
    b1 = (encoded_vv >> 8) & 0x0F
    b2 = encoded_vv & 0xFF
    return bytes([b1, b2])


def encode_track_heading(degrees):
    """
    Encodes track or heading in degrees into GDL90 8-bit format.
    
    Args:
        degrees: Track or heading in degrees (0-359)
        
    Returns:
        1-byte encoding of the track/heading
    """
    if degrees is None or not (0 <= degrees < 360):
        # Use 0, but rely on validity flags elsewhere if possible
        return b'\x00'

    # Encoded as value = degrees * (256 / 360)
    encoded = int(round(degrees * 256.0 / 360.0)) & 0xFF
    return bytes([encoded])


def encode_icao_address(icao_hex):
    """
    Encodes a 24-bit ICAO address (hex string) into 3 bytes.
    
    Args:
        icao_hex: ICAO address as a hex string (e.g., "AABBCC")
        
    Returns:
        3-byte encoding of the ICAO address
    """
    try:
        icao_int = int(icao_hex, 16)
        if not (0 <= icao_int <= 0xFFFFFF):
            raise ValueError("ICAO address out of range")
        # Pack as 3 bytes, big-endian
        return struct.pack('>I', icao_int)[1:]  # Use 4 bytes then take last 3
    except (ValueError, TypeError):
        return b'\x00\x00\x00'  # Invalid


def encode_callsign(callsign):
    """
    Encodes a callsign (up to 8 chars) into 8 bytes, space padded.
    
    Args:
        callsign: Aircraft callsign or flight number
        
    Returns:
        8-byte encoding of the callsign
    """
    if not callsign:
        return b'        '  # 8 spaces
    # Ensure ASCII, strip non-printable, pad/truncate to 8 chars
    cleaned = ''.join(c for c in callsign if 32 <= ord(c) <= 126)
    padded = cleaned.ljust(8)[:8]
    return padded.encode('ascii')