"""
Tests for the GDL90 message creation functionality.
"""
import unittest
from modules.gdl90.messages import (
    create_heartbeat_message,
    create_ownship_report,
    create_ownship_geo_altitude,
    create_traffic_report
)
from modules.gdl90.constants import FLAG_BYTE


class TestGDL90Messages(unittest.TestCase):
    """Test cases for GDL90 message creation functions."""
    
    def test_heartbeat_message(self):
        """Test creation of Heartbeat messages."""
        # Test with specific parameters for consistent output
        hb_msg = create_heartbeat_message(
            gps_valid=True,
            maintenance_required=False,
            ident_active=True,
            utc_timing=True
        )
        
        # The timestamp will vary, so we can't check the exact bytes
        # But we can check the structure and first few bytes
        self.assertIsInstance(hb_msg, bytes)
        self.assertTrue(hb_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(hb_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check message ID and status bytes
        # After the start flag (0x7E), we should have:
        # - Message ID: 0x00
        # - Status byte 1: 0x20 (CDTI available)
        # - Status byte 2: 0x50 (GPS valid + IDENT active + reserved bits)
        self.assertEqual(hb_msg[1], 0x00)  # Message ID
        self.assertEqual(hb_msg[2], 0x20)  # Status byte 1
        
        # Status byte 2 might have bit 7 set depending on timestamp
        # So we check bits 0-6 only (0x50 = 0b01010000)
        self.assertEqual(hb_msg[3] & 0x7F, 0x50)  # Status byte 2 (lower 7 bits)
    
    def test_ownship_report_with_known_values(self):
        """Test creation of Ownship Report messages with known values."""
        # Using values from the reference implementation test
        ownship_msg = create_ownship_report(
            lat=30.209548473358154,
            lon=-98.25480937957764,
            alt_press=3300,
            misc=9,  # Airborne with specific flags
            nic=8,
            nac_p=8,
            ground_speed=545,
            track=258.75,
            vert_vel=1408
        )
        
        # Expected bytes based on reference implementation
        # 0x7e,0x0a,0x00,0x00,0x00,0x00,0x15,0x7b,0x7b,0xba,0x21,0x42,0x0a,0xc9,0x88,0x22,0x10,0x16,0xb8,0x01,0x4e,0x31,0x32,0x33,0x34,0x35,0x20,0x20,0x00,0x3d,0x8c,0x7e
        # Note: The callsign part will differ as we're not setting it in our test
        
        # Check the message structure
        self.assertIsInstance(ownship_msg, bytes)
        self.assertTrue(ownship_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(ownship_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check message ID and key fields
        self.assertEqual(ownship_msg[1], 0x0A)  # Message ID for Ownship Report
        
        # Check latitude encoding (3 bytes after message ID)
        # Expected: 0x15, 0x7b, 0x7b for 30.209548473358154
        self.assertEqual(ownship_msg[2:5], bytes([0x15, 0x7b, 0x7b]))
        
        # Check longitude encoding (3 bytes after latitude)
        # Expected: 0xba, 0x21, 0x42 for -98.25480937957764
        self.assertEqual(ownship_msg[5:8], bytes([0xba, 0x21, 0x42]))
        
        # Check altitude encoding (2 bytes)
        # Expected: 0x0a, 0xc9 for 3300 ft
        self.assertEqual(ownship_msg[8:10], bytes([0x0a, 0xc9]))
        
        # Check misc byte and nav integrity
        # Expected: 0x90 for misc=9, 0x88 for nic=8, nac_p=8
        self.assertEqual(ownship_msg[10], 0x90)  # Misc byte
        self.assertEqual(ownship_msg[11], 0x88)  # Nav integrity byte
        
        # Check ground speed (2 bytes)
        # Expected: 0x22, 0x10 for 545 knots
        self.assertEqual(ownship_msg[12:14], bytes([0x22, 0x10]))
        
        # Check vertical velocity (2 bytes)
        # Expected: 0x16, 0xb8 for 1408 fpm
        self.assertEqual(ownship_msg[14:16], bytes([0x16, 0xb8]))
        
        # Check track (1 byte)
        # Expected: 0x01 for 258.75 degrees (approximately)
        self.assertEqual(ownship_msg[16], 0x01)  # Track byte
    
    def test_ownship_geo_altitude(self):
        """Test creation of Ownship Geometric Altitude messages."""
        # Test with specific values
        ownship_geo_msg = create_ownship_geo_altitude(alt_geo=10250, vpl=0xFFFF)
        
        # Check the message structure
        self.assertIsInstance(ownship_geo_msg, bytes)
        self.assertTrue(ownship_geo_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(ownship_geo_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check message ID
        self.assertEqual(ownship_geo_msg[1], 0x0B)  # Message ID for Ownship Geo Alt
        
        # Check altitude encoding (2 bytes)
        # For 10250 ft: (10250 + 1000) / 5 = 2250 = 0x08CA
        self.assertEqual(ownship_geo_msg[2:4], bytes([0x08, 0xCA]))
        
        # Check VPL encoding (2 bytes)
        # Expected: 0xFF, 0xFF for unknown/invalid VPL
        self.assertEqual(ownship_geo_msg[4:6], bytes([0xFF, 0xFF]))
    
    def test_traffic_report_with_known_values(self):
        """Test creation of Traffic Report messages with known values."""
        # Using values from the reference implementation test
        traffic_msg = create_traffic_report(
            icao="E1F24F",
            lat=30.52377462387085,
            lon=-98.53493928909302,
            alt_press=4900,
            misc=0,  # No alert, ADS-B ICAO address
            nic=8,
            nac_p=8,
            horiz_vel=310,
            vert_vel=0,
            track=195.46875,
            emitter_cat=1,  # Light aircraft
            callsign="BNDT0"
        )
        
        # Expected bytes based on reference implementation
        # 0x7e,0x14,0x0,0xe1,0xf2,0x4f,0x15,0xb4,0xaf,0xb9,0xee,0x43,0xe,0xc9,0x88,0x13,0x60,0x0,0x8b,0x1,0x42,0x4e,0x44,0x54,0x30,0x20,0x20,0x20,0x0,0x41,0xa5,0x7e
        
        # Check the message structure
        self.assertIsInstance(traffic_msg, bytes)
        self.assertTrue(traffic_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(traffic_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check message ID and key fields
        self.assertEqual(traffic_msg[1], 0x14)  # Message ID for Traffic Report
        
        # Check status byte
        self.assertEqual(traffic_msg[2], 0x00)  # Status byte (no alert, ADS-B ICAO)
        
        # Check ICAO address (3 bytes)
        # Expected: 0xE1, 0xF2, 0x4F for "E1F24F"
        self.assertEqual(traffic_msg[3:6], bytes([0xE1, 0xF2, 0x4F]))
        
        # Check latitude encoding (3 bytes)
        # Expected: 0x15, 0xB4, 0xAF for 30.52377462387085
        self.assertEqual(traffic_msg[6:9], bytes([0x15, 0xB4, 0xAF]))
        
        # Check longitude encoding (3 bytes)
        # Expected: 0xB9, 0xEE, 0x43 for -98.53493928909302
        self.assertEqual(traffic_msg[9:12], bytes([0xB9, 0xEE, 0x43]))
        
        # Check altitude encoding (2 bytes)
        # Expected: 0x0E, 0xC9 for 4900 ft
        self.assertEqual(traffic_msg[12:14], bytes([0x0E, 0xC9]))
        
        # Check nav integrity
        # Expected: 0x88 for nic=8, nac_p=8
        self.assertEqual(traffic_msg[14], 0x88)  # Nav integrity byte
        
        # Check horizontal velocity (2 bytes)
        # Expected: 0x13, 0x60 for 310 knots
        self.assertEqual(traffic_msg[15:17], bytes([0x13, 0x60]))
        
        # Check vertical velocity (2 bytes)
        # Expected: 0x00, 0x00 for 0 fpm
        self.assertEqual(traffic_msg[17:19], bytes([0x00, 0x00]))
        
        # Check track (1 byte)
        # Expected: 0x8B for 195.46875 degrees
        self.assertEqual(traffic_msg[19], 0x8B)  # Track byte
        
        # Check emitter category
        self.assertEqual(traffic_msg[20], 0x01)  # Emitter category (Light)
        
        # Check callsign (8 bytes)
        # Expected: "BNDT0   " (padded with spaces)
        self.assertEqual(traffic_msg[21:29], b'BNDT0   ')
    
    def test_invalid_values(self):
        """Test message creation with invalid parameter values."""
        # Test with invalid altitude
        invalid_alt_msg = create_ownship_report(
            lat=34, lon=-118, alt_press=None, misc=1, nic=8, nac_p=8, 
            ground_speed=100, track=180, vert_vel=0
        )
        
        self.assertIsInstance(invalid_alt_msg, bytes)
        self.assertTrue(invalid_alt_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(invalid_alt_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check that altitude bytes indicate invalid altitude (0x0F, 0xFF)
        self.assertEqual(invalid_alt_msg[8:10], bytes([0x0F, 0xFF]))
        
        # Test with invalid position
        invalid_pos_msg = create_ownship_report(
            lat=None, lon=None, alt_press=5000, misc=1, nic=8, nac_p=8, 
            ground_speed=100, track=180, vert_vel=0
        )
        
        self.assertIsInstance(invalid_pos_msg, bytes)
        self.assertTrue(invalid_pos_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(invalid_pos_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check that position bytes are zeros for invalid position
        self.assertEqual(invalid_pos_msg[2:5], bytes([0x00, 0x00, 0x00]))  # Latitude
        self.assertEqual(invalid_pos_msg[5:8], bytes([0x00, 0x00, 0x00]))  # Longitude
        
        # Test with invalid vertical velocity
        invalid_vv_msg = create_traffic_report(
            "C0FFEE", 34, -118, 12000, 0x00, 8, 8, 200, None, 90, 1, "TEST"
        )
        
        self.assertIsInstance(invalid_vv_msg, bytes)
        self.assertTrue(invalid_vv_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(invalid_vv_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check that vertical velocity bytes indicate invalid (0x08, 0x00)
        self.assertEqual(invalid_vv_msg[17:19], bytes([0x08, 0x00]))


if __name__ == '__main__':
    unittest.main()