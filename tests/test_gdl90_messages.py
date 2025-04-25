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
        # - Status byte 1: 0b00100000 = 0x20 (CDTI Available) - Assuming traffic display capability
        # - Status byte 2: Based on inputs (gps_valid=T, maint=F, ident=T, utc=T)
        #   Bit 6 (GPS Valid) = 1
        #   Bit 5 (Maint Req) = 0
        #   Bit 4 (IDENT) = 1
        #   Bit 0 (UTC Timing) = 1 (This bit seems to be missing from the spec table but implied by utc_timing flag?)
        #   Expected base = 0b01010001 = 0x51 (Ignoring bit 7 for now)
        self.assertEqual(hb_msg[1], 0x00)  # Message ID
        self.assertEqual(hb_msg[2], 0x20)  # Status byte 1

        # Status byte 2 has bit 7 set by timestamp bit 16. Check lower 7 bits.
        # Expected lower 7 bits = 0b1010000 = 0x50 (GPS Valid + IDENT Active)
        # Note: The original test expected 0x50, which matches GPS Valid + IDENT Active.
        # The utc_timing flag doesn't seem to map directly to Status Byte 2 in the spec table.
        # Let's stick to the spec table interpretation for now.
        expected_status2_base = 0b01010000 # GPS Valid (bit 6) + IDENT Active (bit 4)
        self.assertEqual(hb_msg[3] & 0x7F, expected_status2_base) # Status byte 2 (lower 7 bits)
    
    def test_ownship_report_with_known_values(self):
        """Test creation of Ownship Report messages with known values."""
        # Using downtown Brisbane coordinates
        brisbane_lat = -27.47
        brisbane_lon = 153.02
        ownship_msg = create_ownship_report(
            lat=brisbane_lat,
            lon=brisbane_lon,
            alt_press=3300, # Keeping other values for simplicity
            misc=9,
            nic=8,
            nac_p=8,
            ground_speed=545,
            track=258.75,
            vert_vel=1408
        )
        
        # Expected bytes based on GDL90 Spec calculations for Brisbane:
        # Lat: -27.47 -> 0xEC4C04 (2's comp)
        # Lon: 153.02 -> 0x6D1187
        # Alt: 3300 ft -> 0x0A 0xC0
        # Misc: 9 -> 0x09
        # NIC/NACp: 8/8 -> 0x88
        # GS: 545 kts -> 0x221 -> Bytes: 0x22 0x10
        # VV: 1408 fpm -> 1408/64 = 22 = 0x16 -> Bytes: 0x01 0x60
        # Track: 258.75 deg -> 258.75 * 256/360 = 183 = 0xB7
        # Payload: 0A 157B7B BA2142 0AC0 09 88 2210 0160 B7
        # CRC (0A157B7BBA21420AC0098822100160B7) = 0x8C3D -> LSB first: 3D 8C
        # Framed: 7E 0A 15 7B 7B BA 21 42 0A C0 09 88 22 10 01 60 B7 3D 8C 7E

        # Check the message structure
        self.assertIsInstance(ownship_msg, bytes)
        self.assertTrue(ownship_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(ownship_msg.endswith(bytes([FLAG_BYTE])))
        
        # Check message ID and key fields
        self.assertEqual(ownship_msg[1], 0x0A)  # Message ID for Ownship Report
        
        # Check latitude encoding (3 bytes)
        # Expected: 0xEC, 0x77, 0x3D for -27.47
        self.assertEqual(ownship_msg[2:5], bytes([0xEC, 0x77, 0x3D]))

        # Check longitude encoding (3 bytes after latitude)
        # Expected: 0x6C, 0xD0, 0x71 for 153.02
        self.assertEqual(ownship_msg[5:8], bytes([0x6C, 0xD0, 0x71]))

        # Check altitude encoding (2 bytes)
        # Expected: 0x0A, 0xC0 for 3300 ft
        self.assertEqual(ownship_msg[8:10], bytes([0x0A, 0xC0]))

        # Check misc byte and nav integrity
        # Expected: 0x09 for misc=9, 0x88 for nic=8, nac_p=8
        self.assertEqual(ownship_msg[10], 0x09)  # Misc byte
        self.assertEqual(ownship_msg[11], 0x88)  # Nav integrity byte

        # Check ground speed (2 bytes)
        # Expected: 0x22, 0x10 for 545 knots
        self.assertEqual(ownship_msg[12:14], bytes([0x22, 0x10]))

        # Check vertical velocity (2 bytes)
        # Expected: 0x01, 0x60 for 1408 fpm
        self.assertEqual(ownship_msg[14:16], bytes([0x01, 0x60]))

        # Check track (1 byte)
        # Expected: 0xB8 for 258.75 degrees (int(round((258.75/360)*256)) = 184)
        self.assertEqual(ownship_msg[16], 0xB8)  # Track byte
    
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
        # Using downtown Brisbane coordinates
        brisbane_lat = -27.47
        brisbane_lon = 153.02
        traffic_msg = create_traffic_report(
            icao="E1F24F", # Keeping other values
            lat=brisbane_lat,
            lon=brisbane_lon,
            alt_press=4900,
            misc=0,
            nic=8,
            nac_p=8,
            horiz_vel=310,
            vert_vel=0,
            track=195.46875,
            emitter_cat=1,  # Light aircraft
            callsign="BNDT0"
        )
        
        # Expected bytes based on GDL90 Spec calculations for Brisbane:
        # Status: 0 -> 0x00
        # ICAO: E1F24F -> 0xE1 0xF2 0x4F
        # Lat: -27.47 -> 0xEC4C04 (2's comp)
        # Lon: 153.02 -> 0x6D1187
        # Alt: 4900 ft -> 0x0E 0xC0
        # NIC/NACp: 8/8 -> 0x88
        # Horiz Vel: 310 kts -> 0x136 -> Bytes: 0x13 0x60
        # Vert Vel: 0 fpm -> 0/64 = 0 = 0x000 -> Bytes: 0x00 0x00
        # Track: 195.46875 deg -> 195.46875 * 256/360 = 138 = 0x8A
        # Emitter Cat: 1 -> 0x01
        # Callsign: "BNDT0   " -> 0x42 0x4E 0x44 0x54 0x30 0x20 0x20 0x20
        # Code/Emergency: 0/0 -> 0x00
        # Payload: 14 00 E1F24F 15B4AF B9B235 0EC0 88 1360 0000 8A 01 424E445430202020 00
        # CRC (1400E1F24F15B4AFB9B2350EC088136000008A01424E44543020202000) = 0xA541 -> LSB first: 41 A5
        # Framed: 7E 14 00 E1 F2 4F 15 B4 AF B9 B2 35 0E C0 88 13 60 00 00 8A 01 42 4E 44 54 30 20 20 20 00 41 A5 7E

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
        # Expected: 0xEC, 0x77, 0x3D for -27.47
        self.assertEqual(traffic_msg[6:9], bytes([0xEC, 0x77, 0x3D]))

        # Check longitude encoding (3 bytes)
        # Expected: 0x6C, 0xD0, 0x71 for 153.02
        self.assertEqual(traffic_msg[9:12], bytes([0x6C, 0xD0, 0x71]))

        # Check altitude encoding (2 bytes)
        # Expected: 0x0E, 0xC0 for 4900 ft
        self.assertEqual(traffic_msg[12:14], bytes([0x0E, 0xC0]))

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
        # Expected: 0x8B for 195.46875 degrees (int(round((195.46875/360)*256)) = 139)
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