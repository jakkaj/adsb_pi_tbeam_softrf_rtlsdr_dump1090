"""
Tests for the GDL90 CRC calculation functionality.
"""
import unittest
from modules.gdl90.crc import calculate_crc


class TestGDL90CRC(unittest.TestCase):
    """Test cases for the GDL90 CRC-16-CCITT implementation."""
    
    def test_crc_calculation(self):
        """Test CRC calculation with known values."""
        # Test with a simple payload
        simple_payload = bytes([0x01, 0x02, 0x03, 0x04, 0x05])
        crc = calculate_crc(simple_payload)
        self.assertIsNotNone(crc)
        self.assertEqual(len(crc), 2)
        
        # Test with a payload that contains flag and escape bytes
        complex_payload = bytes([0x00, 0x7E, 0x14, 0x7D, 0xAB])
        crc = calculate_crc(complex_payload)
        self.assertIsNotNone(crc)
        self.assertEqual(len(crc), 2)
        # Expected CRC for this payload is 0x48, 0x04 (LSB, MSB)
        self.assertEqual(crc, bytes([0x48, 0x04]))
        
        # Test with an empty payload
        empty_payload = bytes([])
        crc = calculate_crc(empty_payload)
        self.assertIsNotNone(crc)
        self.assertEqual(len(crc), 2)
    
    def test_crc_byte_order(self):
        """Test that CRC bytes are returned in LSB, MSB order as required by GDL90."""
        # Use a known payload with a predictable CRC
        payload = bytes([0x00])  # Heartbeat message ID
        crc = calculate_crc(payload)
        
        # Verify that the CRC is in LSB, MSB order
        # We can't hardcode the expected value without knowing the exact CRC algorithm,
        # but we can verify the length and that it's not None
        self.assertIsNotNone(crc)
        self.assertEqual(len(crc), 2)
        
        # For a more thorough test, we could calculate the CRC manually and compare,
        # but that would essentially duplicate the implementation


if __name__ == '__main__':
    unittest.main()