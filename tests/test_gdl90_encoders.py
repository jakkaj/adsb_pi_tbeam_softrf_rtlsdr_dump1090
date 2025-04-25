"""
Tests for the GDL90 data encoding functions.
"""
import unittest
from modules.gdl90.encoders import (
    encode_lat_lon,
    encode_altitude_pressure,
    encode_altitude_geometric,
    encode_velocity,
    encode_vertical_velocity,
    encode_track_heading,
    encode_icao_address,
    encode_callsign
)


class TestGDL90Encoders(unittest.TestCase):
    """Test cases for GDL90 data type encoders."""
    
    def test_latitude_longitude_encoding(self):
        """Test encoding of latitude and longitude values."""
        # Test valid values
        lat_encoded = encode_lat_lon(34.12345, is_latitude=True)
        self.assertIsNotNone(lat_encoded)
        self.assertEqual(len(lat_encoded), 3)
        
        lon_encoded = encode_lat_lon(-118.54321, is_latitude=False)
        self.assertIsNotNone(lon_encoded)
        self.assertEqual(len(lon_encoded), 3)
        
        # Test boundary values
        max_lat = encode_lat_lon(90.0, is_latitude=True)
        self.assertIsNotNone(max_lat)
        
        min_lat = encode_lat_lon(-90.0, is_latitude=True)
        self.assertIsNotNone(min_lat)
        
        max_lon = encode_lat_lon(180.0, is_latitude=False)
        self.assertIsNotNone(max_lon)
        
        min_lon = encode_lat_lon(-180.0, is_latitude=False)
        self.assertIsNotNone(min_lon)
        
        # Test invalid values
        invalid_lat = encode_lat_lon(91.0, is_latitude=True)  # Out of range
        self.assertIsInstance(invalid_lat, bytes)
        self.assertEqual(len(invalid_lat), 3)
        
        invalid_lon = encode_lat_lon(-181.0, is_latitude=False)  # Out of range
        self.assertIsInstance(invalid_lon, bytes)
        self.assertEqual(len(invalid_lon), 3)
        
        # Only None values should return None
        none_value = encode_lat_lon(None, is_latitude=True)
        self.assertIsNone(none_value)
        
        invalid_none = encode_lat_lon(None, is_latitude=False)  # None value
        self.assertIsNone(invalid_none)
    
    def test_altitude_encoding(self):
        """Test encoding of pressure and geometric altitude values."""
        # Test pressure altitude encoding
        alt_press = encode_altitude_pressure(10000)
        self.assertIsNotNone(alt_press)
        self.assertEqual(len(alt_press), 2)
        
        # Test geometric altitude encoding
        alt_geo = encode_altitude_geometric(10250)
        self.assertIsNotNone(alt_geo)
        self.assertEqual(len(alt_geo), 2)
        
        # Test invalid values
        invalid_press = encode_altitude_pressure(None)
        self.assertEqual(invalid_press, bytes([0x0F, 0xFF]))  # Should return invalid marker
        
        invalid_geo = encode_altitude_geometric(None)
        self.assertEqual(invalid_geo, b'\xFF\xFF')  # Should return invalid marker
    
    def test_velocity_encoding(self):
        """Test encoding of horizontal and vertical velocity values."""
        # Test horizontal velocity
        horiz_vel = encode_velocity(120)
        self.assertIsNotNone(horiz_vel)
        self.assertEqual(len(horiz_vel), 2)
        
        # Test vertical velocity (positive)
        vert_vel_up = encode_vertical_velocity(500)
        self.assertIsNotNone(vert_vel_up)
        self.assertEqual(len(vert_vel_up), 2)
        
        # Test vertical velocity (negative)
        vert_vel_down = encode_vertical_velocity(-500)
        self.assertIsNotNone(vert_vel_down)
        self.assertEqual(len(vert_vel_down), 2)
        
        # Test invalid values
        invalid_horiz = encode_velocity(None)
        self.assertEqual(invalid_horiz, b'\xFF\xFF')  # Should return invalid marker (sample logic)
        
        invalid_vert = encode_vertical_velocity(None)
        self.assertEqual(invalid_vert, b'\x08\x00')  # Should return invalid marker
    
    def test_misc_encodings(self):
        """Test encoding of track/heading, ICAO address, and callsign."""
        # Test track/heading
        track = encode_track_heading(90)
        self.assertIsNotNone(track)
        self.assertEqual(len(track), 1)
        
        # Test ICAO address
        icao = encode_icao_address("AABBCC")
        self.assertIsNotNone(icao)
        self.assertEqual(len(icao), 3)
        
        # Test callsign
        callsign = encode_callsign("N12345")
        self.assertIsNotNone(callsign)
        self.assertEqual(len(callsign), 8)
        
        # Test invalid values
        invalid_track = encode_track_heading(None)
        self.assertEqual(invalid_track, b'\x00')  # Should return 0
        
        invalid_icao = encode_icao_address(None)
        self.assertEqual(invalid_icao, b'\x00\x00\x00')  # Should return all zeros
        
        invalid_callsign = encode_callsign(None)
        self.assertEqual(invalid_callsign, b'        ')  # Should return 8 spaces


if __name__ == '__main__':
    unittest.main()