#!/usr/bin/env python3

import unittest
from datetime import datetime, timezone
import struct
import time

# Import from modules
from modules.gdl90 import create_heartbeat_message, frame_message, calculate_crc, FLAG_BYTE, CONTROL_ESCAPE, ESCAPE_XOR

# Import from gdl90_tester
from gdl90_tester import parse_frame, decode_heartbeat, unstuff_data

class TestGDL90HeartbeatEncodingDecoding(unittest.TestCase):
    
    def test_heartbeat_timestamp_encoding_decoding(self):
        """Test that heartbeat messages correctly encode and decode timestamps."""
        
        # Create a heartbeat message with known values
        hb_msg = create_heartbeat_message(gps_valid=True, ident_active=True)
        
        # Parse the frame to get the payload
        payload, _ = parse_frame(hb_msg)
        self.assertIsNotNone(payload, "Failed to parse the frame")
        self.assertEqual(payload[0], 0x00, "First byte should be message ID 0x00")
        
        # Decode the message
        decoded = decode_heartbeat(payload)
        self.assertIsNotNone(decoded, "Failed to decode the heartbeat message")
        
        # Check general field decoding
        self.assertEqual(decoded["GPS Valid"], True)
        self.assertEqual(decoded["IDENT Active"], True)
        
        # Check timestamp encoding/decoding specifically
        # Since we don't know the exact time when create_heartbeat_message was called,
        # we'll verify that the Seconds Since Midnight is a reasonable value
        seconds_str = decoded["Seconds Since Midnight"]
        seconds = float(seconds_str)
        
        # Seconds since midnight should be between 0 and 86400
        self.assertGreaterEqual(seconds, 0)
        self.assertLessEqual(seconds, 86400)
        
        print(f"Decoded heartbeat timestamp: {seconds} seconds since midnight")
    
    def test_heartbeat_with_known_timestamp(self):
        """Test heartbeat encoding/decoding with a manually constructed timestamp."""
        
        # Create a heartbeat with a specific timestamp for testing
        test_timestamp = 12345.6  # 12345.6 seconds since midnight
        ts_field = int(test_timestamp * 10)  # Convert to 0.1s units
        
        # Manually create a heartbeat message with this timestamp
        message_id = 0x00
        status_byte1 = 0b00100000  # CDTI available
        status_byte2 = 0b01110000  # GPS valid, IDENT active, reserved bits
        
        # Set bit 16 of timestamp in status_byte2 if needed
        ts_bit16 = (ts_field & 0x10000) >> 16
        status_byte2 = (status_byte2 & 0b01111111) | (ts_bit16 << 7)
        
        # Pack timestamp as little-endian for the lower 16 bits
        ts_lower_16bits = ts_field & 0xFFFF
        ts_byte1 = ts_lower_16bits & 0xFF           # LSB
        ts_byte2 = (ts_lower_16bits >> 8) & 0xFF    # MSB
        
        # Create the payload
        test_payload = bytearray()
        test_payload.extend(struct.pack('>BBB', message_id, status_byte1, status_byte2))
        test_payload.extend(struct.pack('<BB', ts_byte1, ts_byte2))
        
        # Add CRC, byte stuffing, and framing
        test_message = frame_message(bytes(test_payload))
        
        # Parse and decode
        test_payload, _ = parse_frame(test_message)
        self.assertIsNotNone(test_payload, "Failed to parse the test frame")
        
        test_decoded = decode_heartbeat(test_payload)
        self.assertIsNotNone(test_decoded, "Failed to decode the test heartbeat message")
        
        # Check timestamp decoding
        decoded_seconds = float(test_decoded["Seconds Since Midnight"])
        self.assertAlmostEqual(decoded_seconds, test_timestamp, delta=0.1)
        
        print(f"Expected timestamp: {test_timestamp}, Decoded timestamp: {decoded_seconds}")

if __name__ == "__main__":
    unittest.main()