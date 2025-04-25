"""
Constants for GDL90 protocol implementation.

This module defines constants for the GDL90 protocol, including flag bytes,
message IDs, and other standard values.
"""

# GDL90 Frame Delimiters and Byte Stuffing
FLAG_BYTE = 0x7E
CONTROL_ESCAPE = 0x7D
ESCAPE_XOR = 0x20

# Message IDs
MSG_ID_HEARTBEAT = 0x00
MSG_ID_OWNSHIP_GEO_ALT = 0x0B  # 11 - Ownship Geometric Altitude
MSG_ID_OWNSHIP_REPORT = 0x0A   # 10 - Ownship Pressure Altitude Report
MSG_ID_TRAFFIC_REPORT = 0x14   # 20
# Add other message IDs as needed (e.g., 0x01 Status, 0x07 ID)