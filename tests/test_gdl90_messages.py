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
        hb_msg = create_heartbeat_message(gps_valid=True, utc_timing=True)
        print(f"Heartbeat: {hb_msg.hex().upper()}")
        self.assertIsInstance(hb_msg, bytes)
        self.assertTrue(hb_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(hb_msg.endswith(bytes([FLAG_BYTE])))
        self.assertGreater(len(hb_msg), 2)  # Should be more than just flags
    
    def test_ownship_report(self):
        """Test creation of Ownship Report messages."""
        ownship_msg = create_ownship_report(
            lat=34.12345, lon=-118.54321, alt_press=10000, misc=1,  # Airborne
            nic=8, nac_p=8, ground_speed=120, track=90, vert_vel=500
        )
        print(f"Ownship Report: {ownship_msg.hex().upper()}")
        self.assertIsInstance(ownship_msg, bytes)
        self.assertTrue(ownship_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(ownship_msg.endswith(bytes([FLAG_BYTE])))
        self.assertGreater(len(ownship_msg), 2)
    
    def test_ownship_geo_altitude(self):
        """Test creation of Ownship Geometric Altitude messages."""
        ownship_geo_msg = create_ownship_geo_altitude(alt_geo=10250, vpl=0xFFFF)
        print(f"Ownship Geo Alt: {ownship_geo_msg.hex().upper()}")
        self.assertIsInstance(ownship_geo_msg, bytes)
        self.assertTrue(ownship_geo_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(ownship_geo_msg.endswith(bytes([FLAG_BYTE])))
        self.assertGreater(len(ownship_geo_msg), 2)
    
    def test_traffic_report(self):
        """Test creation of Traffic Report messages."""
        traffic_msg = create_traffic_report(
            icao="AABBCC", lat=34.12500, lon=-118.54000, alt_press=11000,
            misc=0x00,  # No Alert (0 << 4), ADS-B ICAO address type (0)
            nic=8, nac_p=8, horiz_vel=150, vert_vel=-200, track=270,
            emitter_cat=1,  # Light aircraft
            callsign="N12345"
        )
        print(f"Traffic Report: {traffic_msg.hex().upper()}")
        self.assertIsInstance(traffic_msg, bytes)
        self.assertTrue(traffic_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(traffic_msg.endswith(bytes([FLAG_BYTE])))
        self.assertGreater(len(traffic_msg), 2)
    
    def test_invalid_values(self):
        """Test message creation with invalid parameter values."""
        # Test with invalid altitude
        invalid_alt_msg = create_ownship_report(
            lat=34, lon=-118, alt_press=None, misc=1, nic=8, nac_p=8, 
            ground_speed=100, track=180, vert_vel=0
        )
        print(f"Ownship Invalid Alt: {invalid_alt_msg.hex().upper()}")
        self.assertIsInstance(invalid_alt_msg, bytes)
        self.assertTrue(invalid_alt_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(invalid_alt_msg.endswith(bytes([FLAG_BYTE])))
        
        # Test with invalid position
        invalid_pos_msg = create_ownship_report(
            lat=None, lon=None, alt_press=5000, misc=1, nic=8, nac_p=8, 
            ground_speed=100, track=180, vert_vel=0
        )
        print(f"Ownship Invalid Pos: {invalid_pos_msg.hex().upper()}")
        self.assertIsInstance(invalid_pos_msg, bytes)
        self.assertTrue(invalid_pos_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(invalid_pos_msg.endswith(bytes([FLAG_BYTE])))
        
        # Test with invalid vertical velocity
        invalid_vv_msg = create_traffic_report(
            "C0FFEE", 34, -118, 12000, 0x00, 8, 8, 200, None, 90, 1, "TEST"
        )
        print(f"Traffic Invalid VV: {invalid_vv_msg.hex().upper()}")
        self.assertIsInstance(invalid_vv_msg, bytes)
        self.assertTrue(invalid_vv_msg.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(invalid_vv_msg.endswith(bytes([FLAG_BYTE])))
    
    def test_longitude_encoding_fix(self):
        """Test longitude encoding specifically."""
        traffic_msg_lon_fix = create_traffic_report(
            icao="AABBCC", lat=34.12500, lon=-118.54000, alt_press=11000,
            misc=0x00, nic=8, nac_p=8, horiz_vel=150, vert_vel=-200, track=270,
            emitter_cat=1, callsign="N12345"
        )
        print(f"Traffic Report (Lon Fix): {traffic_msg_lon_fix.hex().upper()}")
        self.assertIsInstance(traffic_msg_lon_fix, bytes)
        self.assertTrue(traffic_msg_lon_fix.startswith(bytes([FLAG_BYTE])))
        self.assertTrue(traffic_msg_lon_fix.endswith(bytes([FLAG_BYTE])))


if __name__ == '__main__':
    unittest.main()