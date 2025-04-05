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
    def __init__(self, broadcast_ip, port, data_queue, stop_event):
        self.broadcast_address = (broadcast_ip, port)
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.sock = None
        self.last_heartbeat_time = 0
        # Add state for ownship data if needed for reports
        self.ownship_data = {}
        # Add state for traffic data (dictionary keyed by ICAO hex)
        self.traffic_data = {}
        print(f"Broadcaster: Initialized for {broadcast_ip}:{port}")

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

                    # Attempt to create and send a traffic report
                    # This is a simplified example, real implementation needs more logic
                    # We need valid lat/lon for traffic reports, which requires CPR decoding
                    lat = self.traffic_data[icao].get('latitude')
                    lon = self.traffic_data[icao].get('longitude')

                    # Only send if we have basic required fields (lat/lon might be missing initially)
                    if lat is not None and lon is not None and data.get('altitude') is not None:
                        traffic_msg = gdl90.create_traffic_report(
                            icao=icao,
                            lat=lat,
                            lon=lon,
                            alt_press=data.get('altitude'),
                            misc=0x01, # No Alert, ADS-B ICAO address type
                            nic=self.traffic_data[icao].get('nic', 8), # Placeholder NIC or from data if available
                            nac_p=self.traffic_data[icao].get('nac_p', 8), # Placeholder NACp or from data if available
                            horiz_vel=data.get('speed'),
                            vert_vel=data.get('vert_rate'),
                            track=data.get('heading'),
                            emitter_cat=self.traffic_data[icao].get('emitter_cat', 1), # Placeholder or from data
                            callsign=data.get('callsign')
                        )
                        if traffic_msg:
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
                            else:
                                # If essential fields are missing, skip this message
                                raise ValueError("Missing essential GPS fields (lat/lon/fix)")

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
                            self.ownship_data['last_gps_update'] = time.time()
                            # print(f"DEBUG: Updated ownship position: Lat={self.ownship_data['latitude']:.4f}, Lon={self.ownship_data['longitude']:.4f}, AltGeo={self.ownship_data['altitude_geo']}")
                        except (ValueError, IndexError) as e:
                            print(f"FLARM Client: Error parsing GPS data ({msg_type}): {e}")
                    # TODO: Add parsing for RMC (speed, track) and potentially others
                    pass
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

        while not self.stop_event.is_set():
            now = time.monotonic() # Use monotonic clock for intervals

            # Send Heartbeat periodically
            if now - self.last_heartbeat_time >= HEARTBEAT_INTERVAL:
                gps_valid_flag = self.ownship_data.get('gps_valid', False) # Default to False if no GPS data yet
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

            # Send Ownship Report periodically (e.g., every 1 second if data available)
            # Requires pressure altitude, which might not come from standard GPS NMEA
            # We might need a separate sensor or use geometric altitude if allowed/configured
            if now - last_ownship_report_time >= 1.0 and 'latitude' in self.ownship_data:
                 # Using Geometric Altitude for Pressure Altitude here - THIS IS INCORRECT for standard GDL90
                 # A proper implementation needs a pressure altitude source.
                 # For now, we'll send Geo Alt in the dedicated message instead.
                 # ownship_report_msg = gdl90.create_ownship_report(
                 #     lat=self.ownship_data.get('latitude'),
                 #     lon=self.ownship_data.get('longitude'),
                 #     alt_press=self.ownship_data.get('altitude_geo'), # WRONG - Needs Pressure Alt
                 #     misc=1, # Airborne
                 #     nic=self.ownship_data.get('nic', 8), # Placeholder
                 #     nac_p=self.ownship_data.get('nac_p', 8), # Placeholder
                 #     ground_speed=self.ownship_data.get('speed'), # Needs RMC
                 #     track=self.ownship_data.get('track'), # Needs RMC
                 #     vert_vel=self.ownship_data.get('vert_rate') # Needs calculation or specific sensor
                 # )
                 # if ownship_report_msg:
                 #     self.send_message(ownship_report_msg)
                 last_ownship_report_time = now # Update time even if not sent

            # Send Ownship Geo Altitude periodically if available (e.g., every 1 second)
            if now - last_ownship_geo_alt_time >= 1.0 and 'altitude_geo' in self.ownship_data:
                ownship_geo_msg = gdl90.create_ownship_geo_altitude(
                    alt_geo=self.ownship_data.get('altitude_geo'),
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
    broadcaster = Broadcaster(args.udp_broadcast_ip, args.udp_port, data_queue, stop_event)
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
