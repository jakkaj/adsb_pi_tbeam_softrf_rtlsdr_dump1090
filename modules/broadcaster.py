import socket
import time
import queue
import threading
from datetime import datetime, timezone
from . import gdl90 # Use relative import within the package

# Constants
HEARTBEAT_INTERVAL = 1.0  # Send heartbeat every 1 second
DEFAULT_GPS_VALID = True # Assume GPS is valid for now for heartbeat

class Broadcaster:
    def __init__(self, args, data_queue, stop_event):
        self.args = args # Store the args
        self.broadcast_address = (args.udp_broadcast_ip, args.udp_port)
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.sock = None
        self.last_heartbeat_time = 0
        # Add state for ownship data if needed for reports
        self.ownship_data = {}
        # Add state for traffic data (dictionary keyed by ICAO hex)
        self.traffic_data = {}
        print(f"Broadcaster: Initialized for {self.broadcast_address[0]}:{self.broadcast_address[1]}")

    def setup_socket(self):
        """Creates and configures the UDP broadcast socket."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            # Allow reusing the address (important for quick restarts)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Enable broadcasting mode
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # Set a timeout so the receive/send calls don't block indefinitely
            self.sock.settimeout(0.5)
            print(f"Broadcaster: UDP Socket created for {self.broadcast_address}")
            return True
        except socket.error as e:
            print(f"Broadcaster: Error creating socket: {e}")
            self.sock = None
            return False
        except Exception as e:
            print(f"Broadcaster: Unexpected error setting up socket: {e}")
            self.sock = None
            return False

    def send_message(self, message_bytes):
        """Sends a GDL90 message over the UDP socket."""
        if not self.sock:
            # print("Broadcaster: Socket not available, cannot send message.")
            return False
        if not message_bytes:
            # print("Broadcaster: Attempted to send empty message.")
            return False

        try:
            self.sock.sendto(message_bytes, self.broadcast_address)
            # print(f"DEBUG: Sent {len(message_bytes)} bytes to {self.broadcast_address}") # Optional debug
            return True
        except socket.error as e:
            print(f"Broadcaster: Socket error sending message: {e}")
            # Consider closing/reopening socket on certain errors
            self.close_socket()
            return False
        except Exception as e:
            print(f"Broadcaster: Unexpected error sending message: {e}")
            return False

    def close_socket(self):
        """Closes the UDP socket."""
        if self.sock:
            print("Broadcaster: Closing UDP socket.")
            self.sock.close()
            self.sock = None

    def process_data_queue(self):
        """Processes messages from the input data queue."""
        try:
            data = self.data_queue.get_nowait() # Non-blocking get
            # print(f"DEBUG: Processing data: {data}") # Optional debug

            if data.get('source') == 'adsb':
                # --- ADS-B Processing ---
                # TODO: Implement proper ADS-B to GDL90 Traffic Report conversion
                # This requires maintaining state for aircraft (position, velocity, etc.)
                # and potentially handling CPR decoding if not done in adsb_client.
                icao = data.get('icao')
                if icao:
                    # Update traffic data store
                    if icao not in self.traffic_data:
                        self.traffic_data[icao] = {'last_seen': time.time()}
                    self.traffic_data[icao].update(data)
                    self.traffic_data[icao]['last_seen'] = time.time()

                    # After updating state, check if we have enough stored data to send a report
                    stored_lat = self.traffic_data[icao].get('latitude')
                    stored_lon = self.traffic_data[icao].get('longitude')
                    # Check stored altitude as well, as it might come from a different message than lat/lon
                    stored_alt = self.traffic_data[icao].get('altitude')

                    if stored_lat is not None and stored_lon is not None and stored_alt is not None:
                        # We have the essentials, create the report using the latest stored data
                        traffic_msg = gdl90.create_traffic_report(
                            icao=icao,
                            lat=stored_lat,
                            lon=stored_lon,
                            alt_press=stored_alt,
                            misc=0x00, # No Alert (0<<4), ADS-B ICAO address type (0)
                            nic=self.traffic_data[icao].get('nic', 0), # Default to 0 (Unknown) if not available
                            nac_p=self.traffic_data[icao].get('nac_p', 0), # Default to 0 (Unknown) if not available
                            horiz_vel=self.traffic_data[icao].get('speed'),
                            vert_vel=self.traffic_data[icao].get('vert_rate'),
                            track=self.traffic_data[icao].get('heading'),
                            emitter_cat=self.traffic_data[icao].get('emitter_cat', 0), # Default to 0 (No Info) if not available
                            callsign=self.traffic_data[icao].get('callsign')
                        )
                        if traffic_msg:
                            # Consider adding rate limiting here if needed, but send for now
                            self.send_message(traffic_msg)

            elif data.get('source') == 'flarm':
                # --- FLARM Processing ---
                # The raw NMEA is already printed by flarm_client
                # We might want to convert specific FLARM messages (e.g., PFLAA)
                # to GDL90 Traffic Reports if they represent other aircraft.
                msg_type = data.get('msg_type')
                fields = data.get('fields', [])

                if msg_type == 'PFLAA' and len(fields) >= 6:
                    # Example: Convert PFLAA to GDL90 Traffic Report
                    # Note: PFLAA provides relative positions, GDL90 needs absolute.
                    # This requires knowing ownship position. For now, we skip conversion.
                    # print(f"DEBUG: Received FLARM PFLAA: {fields}")
                    pass
                elif msg_type in ['GPGGA', 'GPRMC', 'GNGGA', 'GNRMC']:
                    # TODO: Extract ownship position/velocity from GPS sentences
                    # Update self.ownship_data
                    # Example for GPGGA:
                    # GNGGA/GPGGA: Need index 9 for altitude, index 6 for fix quality
                    if msg_type.endswith('GGA') and len(fields) >= 10:
                        try:
                            lat_nmea_str = fields[1]
                            lat_dir = fields[2]
                            lon_nmea_str = fields[3]
                            lon_dir = fields[4]
                            fix_quality_str = fields[6]
                            alt_geo_str = fields[9] # Altitude MSL is index 9

                            # Check if essential fields are non-empty before conversion
                            if lat_nmea_str and lon_nmea_str and fix_quality_str:
                                lat_nmea = float(lat_nmea_str)
                                lon_nmea = float(lon_nmea_str)
                                fix_quality = int(fix_quality_str)
                                alt_geo = float(alt_geo_str) if alt_geo_str else None # Altitude can be empty

                                # Convert NMEA format (DDDMM.MMMM) to decimal degrees
                                lat_deg = int(lat_nmea / 100)
                                lat_min = lat_nmea - (lat_deg * 100)
                                self.ownship_data['latitude'] = lat_deg + (lat_min / 60.0)
                                if lat_dir == 'S': self.ownship_data['latitude'] *= -1

                                lon_deg = int(lon_nmea / 100)
                                lon_min = lon_nmea - (lon_deg * 100)
                                self.ownship_data['longitude'] = lon_deg + (lon_min / 60.0)
                                if lon_dir == 'W': self.ownship_data['longitude'] *= -1

                                self.ownship_data['altitude_geo'] = alt_geo * 3.28084 if alt_geo is not None else None # Meters to feet
                                self.ownship_data['gps_valid'] = fix_quality > 0
                            else:
                                # If essential fields are missing, default to Gold Coast and mark GPS as invalid
                                print(f"FLARM Client: Missing essential GPS fields ({msg_type}). Defaulting to Gold Coast.")
                                self.ownship_data['latitude'] = -28.016667
                                self.ownship_data['longitude'] = 153.400000
                                self.ownship_data['altitude_geo'] = None # Altitude is unknown if position is defaulted
                                self.ownship_data['gps_valid'] = False
                                # raise ValueError("Missing essential GPS fields (lat/lon/fix)") # Removed error raising

                            self.ownship_data['last_gps_update'] = time.time()
                            # print(f"DEBUG: Updated ownship position: Lat={self.ownship_data['latitude']:.4f}, Lon={self.ownship_data['longitude']:.4f}, AltGeo={self.ownship_data['altitude_geo']}")
                        except (ValueError, IndexError) as e:
                            print(f"FLARM Client: Error parsing GPS data ({msg_type}): {e}")
                    # GNRMC/GPRMC: Need index 1 (status), 6 (speed), 7 (track)
                    elif msg_type.endswith('RMC') and len(fields) >= 8:
                        try:
                            status = fields[1]
                            if status == 'A': # 'A' = Active/Valid, 'V' = Void
                                speed_knots_str = fields[6]
                                track_deg_str = fields[7]
                                if speed_knots_str:
                                    self.ownship_data['speed'] = float(speed_knots_str)
                                if track_deg_str:
                                    self.ownship_data['track'] = float(track_deg_str)
                                # print(f"DEBUG: Updated ownship speed/track: Speed={self.ownship_data.get('speed'):.1f}, Track={self.ownship_data.get('track'):.1f}")
                            else:
                                # If RMC is void, invalidate speed/track? Or just don't update?
                                # Let's just not update for now.
                                pass
                        except (ValueError, IndexError) as e:
                            print(f"FLARM Client: Error parsing GPS data ({msg_type}): {e}")
                    # PGRMZ: Need index 0 (altitude), 1 (unit)
                    elif msg_type == 'PGRMZ' and len(fields) >= 2:
                        try:
                            alt_str = fields[0]
                            unit = fields[1]
                            if alt_str and unit.upper() == 'F': # Check for non-empty string and feet unit
                                self.ownship_data['altitude_press'] = int(alt_str)
                                # print(f"DEBUG: Updated ownship pressure altitude: AltPress={self.ownship_data['altitude_press']}")
                            elif alt_str and unit.upper() == 'M': # Handle meters if needed
                                self.ownship_data['altitude_press'] = int(float(alt_str) * 3.28084)
                                # print(f"DEBUG: Updated ownship pressure altitude (from meters): AltPress={self.ownship_data['altitude_press']}")
                        except (ValueError, IndexError) as e:
                            print(f"FLARM Client: Error parsing Pressure Altitude data ({msg_type}): {e}")
                    # Handle other relevant FLARM messages (PFLAU, etc.) if needed

            self.data_queue.task_done() # Signal that the item is processed

        except queue.Empty:
            # Queue is empty, nothing to do
            pass
        except Exception as e:
            print(f"Broadcaster: Error processing data queue item: {e}")
            # Ensure task_done is called even if there's an error processing
            try:
                self.data_queue.task_done()
            except ValueError: # task_done called too many times
                pass


    def run(self):
        """Main loop for the broadcaster thread."""
        print("Broadcaster: Starting run loop.")
        if not self.setup_socket():
            print("Broadcaster: Failed to setup socket. Thread exiting.")
            return

        last_ownship_report_time = 0
        last_ownship_geo_alt_time = 0
        # Access the spoof_gps flag from the args passed during initialization
        spoof_gps_enabled = getattr(self.args, 'spoof_gps', False)
        if spoof_gps_enabled:
            print("*** Broadcaster: GPS Spoofing Enabled ***")

        while not self.stop_event.is_set():
            now = time.monotonic() # Use monotonic clock for intervals

            # Send Heartbeat periodically
            if now - self.last_heartbeat_time >= HEARTBEAT_INTERVAL:
                # If spoofing, force GPS valid for heartbeat
                gps_valid_flag = True if spoof_gps_enabled else self.ownship_data.get('gps_valid', False)
                # Print debugging info for the heartbeat
                if spoof_gps_enabled:
                    print(f"DEBUG: Sending heartbeat with GPS Valid = {gps_valid_flag}")
                heartbeat_msg = gdl90.create_heartbeat_message(gps_valid=gps_valid_flag)
                if not self.send_message(heartbeat_msg):
                    print("Broadcaster: Heartbeat send failed. Attempting to reset socket...")
                    self.close_socket()
                    if not self.setup_socket():
                        print("Broadcaster: Failed to reset socket. Waiting before retry...")
                        time.sleep(5)
                        continue
                self.last_heartbeat_time = now

            # Process items from the queue
            self.process_data_queue()

            # --- Apply Spoofing if Enabled ---
            if spoof_gps_enabled:
                self.ownship_data['latitude'] = -27.4698 # Brisbane Lat
                self.ownship_data['longitude'] = 153.0251 # Brisbane Lon
                self.ownship_data['altitude_geo'] = 1500 # Spoofed Geo Alt (feet)
                self.ownship_data['speed'] = 120 # Spoofed Speed (knots)
                self.ownship_data['track'] = 90 # Spoofed Track (degrees)
                self.ownship_data['vert_rate'] = 500 # Spoofed Vertical Rate (fpm) - climbing
                self.ownship_data['gps_valid'] = True
                self.ownship_data['altitude_press'] = 1000 # Spoof pressure altitude as well
                # We don't spoof 'altitude_press' - let it come from PGRMZ if available

            # Send Ownship Report periodically (e.g., every 1 second if data available)
            # Condition now relies on spoofed data or real data including pressure alt
            if now - last_ownship_report_time >= 1.0 and 'latitude' in self.ownship_data and 'altitude_press' in self.ownship_data:
                 ownship_report_msg = gdl90.create_ownship_report(
                     lat=self.ownship_data.get('latitude'),
                     lon=self.ownship_data.get('longitude'),
                     alt_press=self.ownship_data.get('altitude_press'), # Use parsed pressure altitude (NOT spoofed)
                     misc=1, # Airborne (TODO: Make this dynamic based on ground speed?)
                     nic=self.ownship_data.get('nic', 8 if self.ownship_data.get('gps_valid') else 0), # Use 8 if valid/spoofed, 0 if not
                     nac_p=self.ownship_data.get('nac_p', 8 if self.ownship_data.get('gps_valid') else 0), # Use 8 if valid/spoofed, 0 if not
                     ground_speed=self.ownship_data.get('speed'), # Use parsed or spoofed speed
                     track=self.ownship_data.get('track'), # Use parsed or spoofed track
                     vert_vel=self.ownship_data.get('vert_rate') # Still missing a source for this
                 )
                 if ownship_report_msg:
                     self.send_message(ownship_report_msg)
                 last_ownship_report_time = now # Update time

            # Send Ownship Geo Altitude periodically if available (e.g., every 1 second)
            # Condition now relies on spoofed data or real data
            if now - last_ownship_geo_alt_time >= 1.0 and 'altitude_geo' in self.ownship_data:
                # Debug the altitude data being sent
                if spoof_gps_enabled:
                    print(f"DEBUG: Sending ownship geo altitude = {self.ownship_data.get('altitude_geo')} feet")
                
                # Ensure altitude_geo is not None by using explicit check
                # This will ensure we don't send None to the encoder
                geo_alt = self.ownship_data.get('altitude_geo')
                if geo_alt is not None:
                    ownship_geo_msg = gdl90.create_ownship_geo_altitude(
                        alt_geo=geo_alt, # Use parsed or spoofed geo alt
                        vpl=self.ownship_data.get('vpl', 0xFFFF) # Vertical Protection Limit (Placeholder)
                    )
                    if ownship_geo_msg:
                        self.send_message(ownship_geo_msg)
                last_ownship_geo_alt_time = now

            # TODO: Implement traffic aging/removal from self.traffic_data
            # items_to_remove = []
            # for icao, data in self.traffic_data.items():
            #     if now - data.get('last_seen', 0) > 60: # Remove if not seen for 60 seconds
            #         items_to_remove.append(icao)
            # for icao in items_to_remove:
            #     del self.traffic_data[icao]
            #     print(f"Broadcaster: Removed stale traffic {icao}")


            # Small sleep to prevent high CPU usage if queue is empty
            # Adjust sleep time based on desired responsiveness vs CPU load
            time.sleep(0.02) # 50Hz loop approx

        self.close_socket()
        print("Broadcaster: Run loop finished.")


# --- Function to be called by the main script ---

def run_broadcaster(args, data_queue, stop_event):
    """
    Creates and runs the Broadcaster instance.
    This function will be the target for the broadcaster thread.
    """
    broadcaster = Broadcaster(args, data_queue, stop_event)
    broadcaster.run() # This method contains the main loop
    print("Broadcaster Thread: Exiting.")

# Example usage (for testing the module directly)
if __name__ == '__main__':
    print("Testing Broadcaster Module...")
    # Mock args for testing
    class Args:
        udp_broadcast_ip = '127.0.0.1' # Broadcast to loopback for testing
        udp_port = 4000

    test_queue = queue.Queue()
    test_stop_event = threading.Event()

    # Add some dummy data to the queue
    test_queue.put({'source': 'adsb', 'icao': 'AABBCC', 'altitude': 15000, 'latitude': 34.0, 'longitude': -118.0, 'speed': 150, 'heading': 90, 'vert_rate': 500, 'timestamp': datetime.now(timezone.utc)})
    test_queue.put({'source': 'flarm', 'raw_nmea': '$GPGGA,123519.00,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47', 'msg_type': 'GPGGA', 'fields': ['123519.00','4807.038','N','01131.000','E','1','08','0.9','545.4','M','46.9','M','',''], 'timestamp': datetime.now(timezone.utc)})
    test_queue.put({'source': 'flarm', 'raw_nmea': '$PFLAA,0,100,200,50,1,FLR12345,90,,100,,3', 'msg_type': 'PFLAA', 'fields': ['0','100','200','50','1','FLR12345','90','','100','','3'], 'timestamp': datetime.now(timezone.utc)})


    # Start the broadcaster in a thread
    broadcaster_thread = threading.Thread(target=run_broadcaster, args=(Args(), test_queue, test_stop_event), daemon=True)
    broadcaster_thread.start()

    # Let it run for a few seconds
    print("Broadcaster running for 10 seconds... Check for UDP packets on 127.0.0.1:4000")
    print("You can use tools like 'netcat' or 'wireshark' to listen: nc -ul 4000")
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        test_stop_event.set()
        broadcaster_thread.join(timeout=2)
        print("Test finished.")
