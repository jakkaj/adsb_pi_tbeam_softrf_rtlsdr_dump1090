"""
Tests for the GDL90 framing functionality.
"""
import unittest
from modules.gdl90.framing import byte_stuff, frame_message
from modules.gdl90.constants import FLAG_BYTE


class TestGDL90Framing(unittest.TestCase):
    """Test cases for GDL90 byte stuffing and message framing."""
    
    def test_byte_stuffing(self):
        """Test the byte stuffing functionality."""
        payload_needs_stuffing = bytes([0x00, 0x7E, 0x14, 0x7D, 0xAB])
        framed_stuffed = frame_message(payload_needs_stuffing)
        print(f"Original Payload: {payload_needs_stuffing.hex().upper()}")
        print(f"Framed & Stuffed: {framed_stuffed.hex().upper()}")
        # Expected CRC calculated based on payload 00 7E 14 7D AB -> 48 04 (CRC-16-CCITT/Kermit)
        # Expected Framed/Stuffed: 7E 00 7D 5E 14 7D 5D AB 48 04 7E
        expected_hex = "7E007D5E147D5DAB48047E"  # Corrected expected value
        self.assertEqual(framed_stuffed.hex().upper(), expected_hex)
    
    def test_message_framing(self):
        """Test the complete message framing process."""
        # Test with a simple payload that doesn't need stuffing
        simple_payload = bytes([0x01, 0x02, 0x03, 0x04, 0x05])
        framed_message = frame_message(simple_payload)
        
        # Check that the message is properly framed
        self.assertTrue(framed_message.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(framed_message.endswith(bytes([FLAG_BYTE])))
        self.assertGreater(len(framed_message), 2)  # Should be more than just flags


if __name__ == '__main__':
    unittest.main()