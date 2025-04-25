"""
GDL90 message framing functionality.

This module provides functions for byte stuffing and framing of GDL90 messages
according to the protocol specification.
"""
from .constants import FLAG_BYTE, CONTROL_ESCAPE, ESCAPE_XOR
from .crc import calculate_crc


def byte_stuff(raw_payload_with_crc):
    """
    Performs GDL90 byte stuffing on the message payload including CRC.
    
    Args:
        raw_payload_with_crc: The bytes to stuff (usually message + CRC)
        
    Returns:
        The byte-stuffed payload ready for framing
    """
    stuffed = bytearray()
    for byte in raw_payload_with_crc:
        if byte == FLAG_BYTE:
            stuffed.append(CONTROL_ESCAPE)
            stuffed.append(FLAG_BYTE ^ ESCAPE_XOR)  # 0x5E
        elif byte == CONTROL_ESCAPE:
            stuffed.append(CONTROL_ESCAPE)
            stuffed.append(CONTROL_ESCAPE ^ ESCAPE_XOR)  # 0x5D
        else:
            stuffed.append(byte)
    return bytes(stuffed)


def frame_message(message_payload):
    """
    Adds CRC, performs byte stuffing, and adds framing flags.
    
    This is the main function to use when preparing a GDL90 message for
    transmission.
    
    Args:
        message_payload: The raw message bytes (message ID + message data)
        
    Returns:
        A complete GDL90 frame ready for transmission
    """
    crc_bytes = calculate_crc(message_payload)  # Returns LSB, MSB
    payload_with_crc = message_payload + crc_bytes
    stuffed_payload = byte_stuff(payload_with_crc)
    return bytes([FLAG_BYTE]) + stuffed_payload + bytes([FLAG_BYTE])