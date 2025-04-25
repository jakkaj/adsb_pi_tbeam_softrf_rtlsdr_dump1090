#!/usr/bin/env python3
"""
Sample Traffic Generator Module for ADSB System

This module generates simulated aircraft traffic in an X pattern around
the user's current GPS location, injecting data into the main processing
pipeline while still allowing real traffic to be displayed.
"""

import time
import math
import random
import queue
import threading
import os
import json
from datetime import datetime, timezone

# Constants for position calculations
EARTH_RADIUS_NM = 3440.065  # Earth radius in nautical miles
NM_TO_DEGREE_LAT = 1/60.0   # 1 nautical mile = 1/60 degree of latitude
DEFAULT_PATTERN_SIZE = 5.0  # Default distance (in NM) from center to edge of pattern


def run_generator(args, data_queue, stop_event):
    """
    Main function to run the sample traffic generator.
    This function will be the target for the sample traffic generator thread.
    """
    generator = SampleTrafficGenerator(args, data_queue, stop_event)
    generator.run()
    print("Sample Traffic Generator Thread: Exiting.")


class SampleTrafficGenerator:
    """
    Generates simulated aircraft traffic in an X pattern around the user's
    current GPS location, sending data to the shared queue.
    """
    
    def __init__(self, args, data_queue, stop_event):
        """
        Initialize the sample traffic generator.
        
        Args:
            args: Command-line arguments from main script
            data_queue: Shared queue for aircraft data
            stop_event: Threading event to signal stopping
        """
        self.args = args
        self.data_queue = data_queue
        self.stop_event = stop_event
        
        # Will store the most recent ownship data
        self.ownship_data = {
            'latitude': None,
            'longitude': None,
            'altitude_geo': None
        }
        
        # Pattern size in nautical miles
        self.pattern_size = getattr(args, 'sample_traffic_distance', DEFAULT_PATTERN_SIZE)
        
        # Initialize aircraft
        self.aircraft = self._initialize_aircraft()
        
        print(f"Sample Traffic Generator: Initialized with {len(self.aircraft)} aircraft")
        print(f"Sample Traffic Generator: Pattern size = {self.pattern_size} NM")
    
    def _initialize_aircraft(self):
        """
        Initialize the 4 aircraft for the X pattern with random altitudes.
        
        Returns:
            List of aircraft configuration dictionaries
        """
        return [
            {
                "id": "SIM1",
                "icao": "C0FFEE",  # Custom ICAO address for simulated traffic
                "callsign": "XPAT1",  # Short for X-PATTERN-1
                "direction": "NW-SE",
                "heading": 135,  # SE heading in degrees
                "track": 135,    # SE track in degrees
                "speed": random.uniform(120, 250),  # knots
                "altitude": random.uniform(3000, 10000),  # feet
                "vert_rate": 0,  # feet per minute
                "lat": None,  # Will be calculated based on ownship
                "lon": None,  # Will be calculated based on ownship
                "position_offset": 0.0,  # Initial position offset (0.0 to 1.0)
                "last_update": time.time()
            },
            {
                "id": "SIM2",
                "icao": "C0FFEF",
                "callsign": "XPAT2",
                "direction": "SE-NW",
                "heading": 315,  # NW heading in degrees
                "track": 315,    # NW track in degrees
                "speed": random.uniform(120, 250),
                "altitude": random.uniform(3000, 10000),
                "vert_rate": 0,
                "lat": None,
                "lon": None,
                "position_offset": 0.0,
                "last_update": time.time()
            },
            {
                "id": "SIM3",
                "icao": "C0FFF0",
                "callsign": "XPAT3",
                "direction": "NE-SW",
                "heading": 225,  # SW heading in degrees
                "track": 225,    # SW track in degrees
                "speed": random.uniform(120, 250),
                "altitude": random.uniform(3000, 10000),
                "vert_rate": 0,
                "lat": None,
                "lon": None,
                "position_offset": 0.0,
                "last_update": time.time()
            },
            {
                "id": "SIM4",
                "icao": "C0FFF1",
                "callsign": "XPAT4",
                "direction": "SW-NE",
                "heading": 45,  # NE heading in degrees
                "track": 45,     # NE track in degrees
                "speed": random.uniform(120, 250),
                "altitude": random.uniform(3000, 10000),
                "vert_rate": 0,
                "lat": None,
                "lon": None,
                "position_offset": 0.0,
                "last_update": time.time()
            }
        ]
    
    def run(self):
        """Main loop to generate and update traffic"""
        print("Sample Traffic Generator: Starting run loop")
        
        # Initial delay to let other threads start
        time.sleep(2)
        
        while not self.stop_event.is_set():
            # Update ownship data from broadcaster state
            self._update_ownship_data()
            
            # Only proceed if we have valid ownship data
            if self.ownship_data['latitude'] is not None and self.ownship_data['longitude'] is not None:
                # Update aircraft positions
                self._update_aircraft_positions()
                
                # Send aircraft data to queue
                self._send_aircraft_data()
            else:
                print("Sample Traffic Generator: Waiting for valid ownship position")
            
            # Sleep to control update rate
            time.sleep(1.0)
    
    def _update_ownship_data(self):
        """
        Update ownship data from the same sources used by the broadcaster:
        - Location file if specified
        - Default spoofed values if GPS spoofing is enabled
        """
        # Get location data from the same sources as the broadcaster
        location_file = getattr(self.args, 'location_file', None)
        spoof_gps_enabled = getattr(self.args, 'spoof_gps', False)
        
        # If we have a location file, load it
        if location_file and os.path.exists(location_file):
            try:
                with open(location_file, 'r') as f:
                    location_data = json.load(f)
                    
                self.ownship_data['latitude'] = location_data.get('latitude')
                self.ownship_data['longitude'] = location_data.get('longitude')
                self.ownship_data['altitude_geo'] = location_data.get('altitude_geo')
                
                if not hasattr(self, 'location_loaded'):
                    print(f"Sample Traffic Generator: Using location from {location_file}")
                    print(f"  Location: {location_data.get('name', 'Unknown')}: {location_data.get('description', 'No description')}")
                    self.location_loaded = True
                    
            except Exception as e:
                print(f"Sample Traffic Generator: Error loading location file {location_file}: {e}")
                print("Falling back to default spoofed values")
                self._use_default_location()
        
        elif spoof_gps_enabled:
            # Use default hardcoded values
            self._use_default_location()
            
            if not hasattr(self, 'location_loaded'):
                print("Sample Traffic Generator: Using default spoofed location (Brisbane)")
                self.location_loaded = True
        else:
            print("Sample Traffic Generator: Warning - No location source available.")
            print("Sample Traffic Generator: Using default location (Brisbane) for test traffic.")
            self._use_default_location()
    
    def _use_default_location(self):
        """Use default hardcoded location values (Brisbane)"""
        self.ownship_data['latitude'] = -27.4698  # Brisbane
        self.ownship_data['longitude'] = 153.0251
        self.ownship_data['altitude_geo'] = 1500
    
    def _calculate_position(self, direction, offset):
        """
        Calculate a position along one of the X pattern arms.
        
        Args:
            direction: Direction string ('NW-SE', 'SE-NW', 'NE-SW', 'SW-NE')
            offset: Position offset along the arm (0.0 to 1.0)
            
        Returns:
            Tuple of (latitude, longitude)
        """
        if self.ownship_data['latitude'] is None or self.ownship_data['longitude'] is None:
            print(f"Sample Traffic Generator: Unable to calculate position - ownship position unknown")
            return None, None
        
        # Center position
        center_lat = self.ownship_data['latitude']
        center_lon = self.ownship_data['longitude']
        
        # Convert offset to -0.5 to 0.5 range centered on ownship
        centered_offset = offset - 0.5
        
        # Scale by pattern size
        scaled_offset = centered_offset * self.pattern_size
        
        # Calculate deltas based on direction
        if direction == 'NW-SE':
            # Northwest to Southeast: -lat, +lon
            delta_lat = -scaled_offset * NM_TO_DEGREE_LAT
            delta_lon = scaled_offset * NM_TO_DEGREE_LAT / math.cos(math.radians(center_lat))
        elif direction == 'SE-NW':
            # Southeast to Northwest: +lat, -lon
            delta_lat = scaled_offset * NM_TO_DEGREE_LAT
            delta_lon = -scaled_offset * NM_TO_DEGREE_LAT / math.cos(math.radians(center_lat))
        elif direction == 'NE-SW':
            # Northeast to Southwest: -lat, -lon
            delta_lat = -scaled_offset * NM_TO_DEGREE_LAT
            delta_lon = -scaled_offset * NM_TO_DEGREE_LAT / math.cos(math.radians(center_lat))
        elif direction == 'SW-NE':
            # Southwest to Northeast: +lat, +lon
            delta_lat = scaled_offset * NM_TO_DEGREE_LAT
            delta_lon = scaled_offset * NM_TO_DEGREE_LAT / math.cos(math.radians(center_lat))
        else:
            return None, None
        
        # Calculate new position
        new_lat = center_lat + delta_lat
        new_lon = center_lon + delta_lon
        
        return new_lat, new_lon
    
    def _update_aircraft_positions(self):
        """
        Update each aircraft's position based on pattern direction and elapsed time.
        """
        current_time = time.time()
        print(f"Sample Traffic Generator: Updating positions with center at lat={self.ownship_data['latitude']}, lon={self.ownship_data['longitude']}")
        
        for aircraft in self.aircraft:
            # Calculate time elapsed since last update
            elapsed_time = current_time - aircraft['last_update']
            aircraft['last_update'] = current_time
            
            # Calculate distance traveled in NM
            distance = (aircraft['speed'] * elapsed_time) / 3600.0  # Convert knots to NM/s
            
            # Update position offset (full pattern is traversed in approximately 2 minutes)
            # Speed is adjusted based on pattern size
            speed_factor = 0.01 * (5.0 / self.pattern_size)  # Slower for larger patterns
            aircraft['position_offset'] += speed_factor * elapsed_time
            
            # Reset offset if it exceeds 1.0
            while aircraft['position_offset'] > 1.0:
                aircraft['position_offset'] -= 1.0
            
            # Calculate new position along the arm
            aircraft['lat'], aircraft['lon'] = self._calculate_position(
                aircraft['direction'],
                aircraft['position_offset']
            )
            
            # Debug output
            if aircraft['lat'] is not None and aircraft['lon'] is not None:
                print(f"Sample Traffic: {aircraft['id']} at lat={aircraft['lat']:.6f}, lon={aircraft['lon']:.6f}, alt={aircraft['altitude']:.1f}")
            else:
                print(f"Sample Traffic: {aircraft['id']} position calculation failed")
    
    def _send_aircraft_data(self):
        """
        Format and send aircraft data to the shared queue.
        """
        traffic_count = 0
        for aircraft in self.aircraft:
            # Skip aircraft without calculated positions
            if aircraft['lat'] is None or aircraft['lon'] is None:
                print(f"Sample Traffic: Skipping {aircraft['id']} - invalid position")
                continue
            
            # Format data for queue, matching adsb_client structure + adding defaults
            data = {
                'source': 'sample_traffic',
                'icao': aircraft['icao'],
                'callsign': aircraft['callsign'],
                'latitude': aircraft['lat'],
                'longitude': aircraft['lon'],
                'altitude': aircraft['altitude'], # Assuming pressure altitude
                'heading': aircraft['heading'],
                'track': aircraft['track'],       # Explicitly include track data
                'speed': aircraft['speed'],
                'vert_rate': aircraft['vert_rate'],
                'timestamp': datetime.now(timezone.utc),
                'nic': 8,  # Default NIC for simulation
                'nac_p': 8, # Default NACp for simulation
                'emitter_cat': 1, # Default Emitter Category (Light Aircraft)
                'airborne_status': True # Assume airborne for simulation
            }
            
            # Add to queue
            try:
                self.data_queue.put(data, block=False)
                traffic_count += 1
            except queue.Full:
                print(f"Sample Traffic: Queue full, unable to send {aircraft['id']}")
                # Skip if queue is full
                pass
        
        if traffic_count > 0:
            print(f"Sample Traffic: Sent {traffic_count} aircraft to queue")
        else:
            print("Sample Traffic: WARNING - No aircraft data sent to queue")


# For testing the module directly
if __name__ == '__main__':
    print("Testing Sample Traffic Generator Module...")
    
    # Mock args for testing
    class Args:
        spoof_gps = True
        sample_traffic_distance = 5.0
    
    test_queue = queue.Queue()
    test_stop_event = threading.Event()
    
    # Start the generator in a thread
    generator_thread = threading.Thread(
        target=run_generator, 
        args=(Args(), test_queue, test_stop_event),
        daemon=True
    )
    generator_thread.start()
    
    # Simulate running for a while and then stopping
    try:
        print("Generator running for 30 seconds...")
        start_time = time.time()
        while time.time() - start_time < 30:
            try:
                data = test_queue.get(timeout=1)
                print(f"Received traffic data: {data['icao']} at {data['latitude']:.4f}, {data['longitude']:.4f}, alt={data['altitude']}")
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        test_stop_event.set()
        generator_thread.join(timeout=2)
        print("Test finished.")