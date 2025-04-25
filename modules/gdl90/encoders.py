"""
GDL90 data encoding functions.

This module provides functions for encoding various data types (latitude, longitude,
altitude, velocity, etc.) into the specific binary formats required by the GDL90 protocol.
"""
import struct
import math

def _pack24bit(num):
    """
    Packs an unsigned 24-bit integer into a 3-byte big-endian bytearray.
    Raises ValueError if input is not a 24-bit unsigned value.
    """
    if ((num & 0xFFFFFF) != num) or num < 0:
        raise ValueError("input not a 24-bit unsigned value")
    return bytes([(num & 0xff0000) >> 16, (num & 0x00ff00) >> 8, num & 0xff])

def _makeLatitude(latitude):
    """
    Converts a signed float latitude to 2's complement, ready for 24-bit packing.
    """
    if latitude > 90.0: latitude = 90.0
    if latitude < -90.0: latitude = -90.0
    latitude = int(latitude * (0x800000 / 180.0))
    if latitude < 0:
        latitude = (0x1000000 + latitude) & 0xffffff  # 2s complement
    return latitude

def _makeLongitude(longitude):
    """
    Converts a signed float longitude to 2's complement, ready for 24-bit packing.
    """
    if longitude > 180.0: longitude = 180.0
    if longitude < -180.0: longitude = -180.0
    longitude = int(longitude * (0x800000 / 180.0))
    if longitude < 0:
        longitude = (0x1000000 + longitude) & 0xffffff  # 2s complement
    return longitude

def encode_lat_lon(degrees, is_latitude=False):
    """
    Encodes latitude or longitude into GDL90 3-byte format (2's complement semicircles).
    Uses sample implementation logic for clamping and 2's complement.

    Args:
        degrees: Latitude or longitude in degrees
        is_latitude: True if latitude, False if longitude

    Returns:
        3-byte encoding of the position or None if invalid
    """
    if degrees is None:
        return None
    if is_latitude:
        value = _makeLatitude(degrees)
    else:
        value = _makeLongitude(degrees)
    return _pack24bit(value)


def encode_altitude_pressure(feet):
    """
    Encodes pressure altitude in feet into GDL90 12-bit format (in 2 bytes).
    Uses sample implementation logic for clamping and packing.

    Args:
        feet: Altitude in feet MSL

    Returns:
        2-byte encoding of the pressure altitude
    """
    if feet is None:
        # 0xFFF represents invalid/unknown altitude
        return bytes([0x0F, 0xFF])

    # Altitude is encoded in 25 ft increments, offset by +1000 ft.
    # Value = (Altitude_ft + 1000) / 25
    altitude = int((feet + 1000) / 25.0)
    if altitude < 0:
        altitude = 0
    if altitude > 0xffe:
        altitude = 0xffe

    # altitude is bits 15-4, misc code is bits 3-0 (misc handled elsewhere)
    b1 = (altitude & 0x0ff0) >> 4  # top 8 bits of altitude
    b2 = (altitude & 0x0f) << 4    # bottom 4 bits of altitude, misc handled in message assembly
    return bytes([b1, b2])


def encode_altitude_geometric(feet):
    """
    Encodes geometric (GNSS) altitude in feet into GDL90 16-bit format (in 2 bytes).
    Uses sample implementation logic for clamping and packing.

    Args:
        feet: Geometric altitude in feet MSL

    Returns:
        2-byte encoding of the geometric altitude
    """
    if feet is None:
        return b'\xFF\xFF'
    # Altitude is encoded in 5 ft increments
    altitude = int(feet / 5)
    if altitude < 0:
        altitude = (0x10000 + altitude) & 0xffff  # 2s complement
    return struct.pack('>H', altitude)


def encode_velocity(knots):
    """
    Encodes horizontal velocity in knots into GDL90 12-bit format (in 2 bytes).
    Uses sample implementation logic for clamping and packing.

    Args:
        knots: Velocity in knots

    Returns:
        2-byte encoding of the velocity
    """
    if knots is None:
        return b'\xFF\xFF'
    hVelocity = int(knots)
    if hVelocity < 0:
        hVelocity = 0
    elif hVelocity > 0xffe:
        hVelocity = 0xffe
    b1 = (hVelocity & 0xff0) >> 4
    b2 = (hVelocity & 0xf) << 4
    return bytes([b1, b2])


def encode_vertical_velocity(fpm):
    """
    Encodes vertical velocity in feet per minute into GDL90 12-bit signed format (in 2 bytes).
    Uses sample implementation logic for clamping and packing.

    Args:
        fpm: Vertical velocity in feet per minute (positive up)

    Returns:
        2-byte encoding of the vertical velocity
    """
    if fpm is None:
        return b'\x08\x00'
    vVelocity = int(fpm / 64)
    if vVelocity > 32576:
        vVelocity = 0x1fe
    elif vVelocity < -32576:
        vVelocity = 0xe02
    else:
        vVelocity = int(fpm / 64)
        if vVelocity < 0:
            vVelocity = (0x1000000 + vVelocity) & 0xffffff  # 2s complement
    # Packing into 3 bytes in the sample, but for 2 bytes, use lower 12 bits
    b1 = (vVelocity & 0xff0) >> 4
    b2 = (vVelocity & 0xf) << 4
    return bytes([b1, b2])


def encode_track_heading(degrees):
    """
    Encodes track or heading in degrees into GDL90 8-bit format.
    Uses sample implementation logic.

    Args:
        degrees: Track or heading in degrees (0-359)

    Returns:
        1-byte encoding of the track/heading
    """
    if degrees is None:
        return b'\x00'
    encoded = int(degrees / (360. / 256)) & 0xFF
    return bytes([encoded])


def encode_icao_address(icao_hex):
    """
    Encodes a 24-bit ICAO address (hex string) into 3 bytes.
    Uses _pack24bit for packing.

    Args:
        icao_hex: ICAO address as a hex string (e.g., "AABBCC")

    Returns:
        3-byte encoding of the ICAO address
    """
    try:
        icao_int = int(icao_hex, 16)
        if not (0 <= icao_int <= 0xFFFFFF):
            raise ValueError("ICAO address out of range")
        return _pack24bit(icao_int)
    except (ValueError, TypeError):
        return b'\x00\x00\x00'


def encode_callsign(callsign):
    """
    Encodes a callsign (up to 8 chars) into 8 bytes, space padded.
    Uses sample implementation logic.

    Args:
        callsign: Aircraft callsign or flight number

    Returns:
        8-byte encoding of the callsign
    """
    if not callsign:
        return b'        '
    return bytes(str(callsign + " "*8)[:8], 'ascii')