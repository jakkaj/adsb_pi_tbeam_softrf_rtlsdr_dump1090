import pyModeS as pms
from pyModeS.extra.tcpclient import TcpClient
import time
import queue
import threading
from datetime import datetime

class AdsbClient(TcpClient):
    """
    Connects to a dump1090 source (like port 30002) and decodes ADS-B messages.
    Puts decoded aircraft data into a queue.
    """
    def __init__(self, host, port, data_queue, stop_event):
        # Reverting to 'raw' datatype for port 30002, will handle framing manually
        super().__init__(host, port, datatype='raw')
        self.data_queue = data_queue
        self.stop_event = stop_event
        self._thread = None
        # Add state for CPR decoding, keyed by ICAO
        self.cpr_data = {}
        print(f"ADS-B Client: Connecting to {host}:{port}...")

    def handle_messages(self, messages):
        """
        Processes raw messages, decodes ADS-B, and puts relevant data into the queue.
        """
        # --- Add print statement to see raw messages received by the handler ---
        for msg, ts in messages:
            print(f"ADS-B Raw Handled: '{msg}' (len={len(msg)}) @ {ts}")
        # --- End of added print statement ---

        for raw_msg, ts in messages:
            if self.stop_event.is_set():
                print("ADS-B Client: Stop event received, stopping message handling.")
                # Signal the client to stop receiving more data
                if hasattr(self, 'stop'): # Check if stop method exists
                    self.stop()
                return # Exit the handler loop

            # Manually strip '*' and ';' framing for raw mode
            msg = raw_msg
            if isinstance(msg, str) and msg.startswith('*') and msg.endswith(';'):
                msg = msg[1:-1]
            elif isinstance(msg, bytes) and msg.startswith(b'*') and msg.endswith(b';'):
                # If pyModeS gives bytes, decode and strip
                try:
                    msg = msg.decode('ascii')[1:-1]
                except UnicodeDecodeError:
                    print(f"ADS-B Decode Error: Could not decode '{raw_msg}' as ASCII")
                    continue

            # Now perform checks on the potentially stripped message 'msg'
            if not msg or len(msg) != 28: # Check for standard 28-char hex length
                # Optionally print skipped messages if debugging framing issues
                # print(f"ADS-B Skipping msg (len {len(msg)}): '{msg}' from raw '{raw_msg}'")
                continue

            df = pms.df(msg)
            if df != 17: # Only process ADS-B messages (DF17)
                continue

            if pms.crc(msg) != 0: # Check CRC
                # Add print statement here to see if CRC is failing
                print(f"ADS-B CRC Failed: {msg}")
                continue

            # If we reach here, it's a DF17 message with a valid CRC.
            icao = pms.icao(msg)
            tc = pms.adsb.typecode(msg)

            aircraft_data = {'source': 'adsb', 'icao': icao, 'timestamp': datetime.fromtimestamp(ts)} # Use message timestamp

            try:
                if 1 <= tc <= 4: # Identification and Category
                    callsign = pms.adsb.callsign(msg)
                    if callsign:
                        aircraft_data['callsign'] = callsign.strip('_')
                elif 9 <= tc <= 18: # Airborne Position (with Baro Altitude)
                    print(f"DEBUG: Processing TC {tc} for {icao}") # Added Debug
                    alt = pms.adsb.altitude(msg)
                    if alt is not None:
                        aircraft_data['altitude'] = alt # Altitude in feet
                        print(f"DEBUG: Decoded Altitude: {alt} for {icao}") # Added Debug
                    # Decode NIC and NACp if available
                    # NIC/NACp cannot be reliably decoded from TC 9-18 using standard pyModeS functions.
                    # Broadcaster will use default (0) if not updated by other message types (e.g., TC28-31).
                    aircraft_data['nic'] = None # Set to None explicitly
                    aircraft_data['nac_p'] = None # Set to None explicitly
                    aircraft_data['nic'] = None # Set to None directly
                    aircraft_data['nac_p'] = None # Set to None directly

                    # --- CPR Decoding Logic ---
                    # Ensure ICAO entry exists in cpr_data
                    if icao not in self.cpr_data:
                        self.cpr_data[icao] = {'odd': None, 'even': None}

                    # Determine frame type and store message/timestamp
                    oe_flag = pms.adsb.oe_flag(msg)
                    frame_type = 'even' if oe_flag == 0 else 'odd'
                    self.cpr_data[icao][frame_type] = {'ts': ts, 'msg': msg}
                    print(f"DEBUG: Stored {frame_type} frame for {icao} at {ts}") # Added Debug

                    # Check if we have a recent pair
                    odd_frame = self.cpr_data[icao]['odd']
                    even_frame = self.cpr_data[icao]['even']

                    if odd_frame and even_frame:
                        t_odd = odd_frame['ts']
                        t_even = even_frame['ts']
                        msg_odd = odd_frame['msg']
                        msg_even = even_frame['msg']

                        print(f"DEBUG: Found pair for {icao}. Odd: {t_odd}, Even: {t_even}") # Added Debug
                        # Check if the pair is recent enough (e.g., within 10 seconds)
                        if abs(t_odd - t_even) < 10.0:
                            # Attempt to decode position
                            print(f"DEBUG: Attempting position decode for {icao}") # Added Debug
                            position = pms.adsb.position(msg_even, msg_odd, t_even, t_odd)
                            if position:
                                aircraft_data['latitude'] = position[0]
                                aircraft_data['longitude'] = position[1]
                                print(f"DEBUG: Position Decoded: {position} for {icao}") # Added Debug
                                # Optional: Clear the used frames to prevent re-computation
                                # self.cpr_data[icao] = {'odd': None, 'even': None}

                elif tc == 19: # Airborne Velocity
                    vel = pms.adsb.velocity(msg) # (speed, heading, vert_rate, speed_type)
                    if vel and vel[0] is not None:
                        aircraft_data['speed'] = vel[0] # knots
                        aircraft_data['heading'] = vel[1] # degrees
                        aircraft_data['vert_rate'] = vel[2] # fpm
                        aircraft_data['speed_type'] = vel[3]
                # Add other typecodes if needed for GDL90 (e.g., Surface Position 5-8, GNSS Alt 20-22)

                # Only process and print/queue if we have more than just basic info
                if len(aircraft_data) > 3:
                    # Print the decoded data to the console for visibility
                    timestamp_str = aircraft_data['timestamp'].strftime("%H:%M:%S.%f")[:-3]
                    print(f"ADS-B Decoded [{timestamp_str}]: {aircraft_data}")
                    try:
                        self.data_queue.put(aircraft_data, block=False)
                    except queue.Full:
                        # Handle queue full scenario if necessary, e.g., log a warning
                        # print("Warning: ADS-B data queue is full. Discarding message.")
                        # print("Warning: ADS-B data queue is full. Discarding message.")
                        pass

            except Exception as e:
                # Print specific errors during decoding
                print(f"ADS-B Client: ERROR decoding TC {tc} for {icao}: {e}")
                import traceback
                traceback.print_exc() # Print full traceback for debugging
                pass # Continue processing other messages

    def run(self):
        """Calls the parent TcpClient's run method to handle socket operations."""
        print("ADS-B Client: Starting run loop.")
        try:
            # Call the parent class's run method which handles socket connection and data reading
            # The parent's run method should handle the stop_event internally or through exceptions.
            super().run()
        except ConnectionRefusedError:
            # This might be caught by the parent, but added here for clarity if needed.
            print(f"ADS-B Client: Connection refused to {self.host}:{self.port}")
        except OSError as e:
             print(f"ADS-B Client: Socket error during run: {e}")
        except Exception as e:
            # Catch any other unexpected errors during the parent's run execution
            print(f"ADS-B Client: Unexpected error in run method: {e}")
        finally:
            # This block executes whether the try block succeeded or failed.
            print("ADS-B Client: Run loop finished.")
            # Ensure stop is called to clean up resources if the parent's run exits.
            if hasattr(self, 'stop'):
                self.stop()

    def start_thread(self):
        """Starts the client in a separate thread."""
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True)
            self._thread.start()
            print("ADS-B Client: Thread started.")
        else:
            print("ADS-B Client: Thread already running.")

    def stop(self):
        """Safely stop the client and close the socket if it exists."""
        print("ADS-B Client: Stopping...")
        self.stop_event.set() # Signal threads using this event
        if self.socket:
            try:
                self.socket.close()
                print("ADS-B Client: Socket closed.")
            except Exception as e:
                print(f"ADS-B Client: Error closing socket: {e}")
        else:
            print("ADS-B Client: No socket to close.")
        # Call the superclass stop if necessary, though it might be redundant now
        # super().stop() # Be cautious if the superclass method has side effects

# --- Function to be called by the main script ---

def run_client(args, data_queue, stop_event):
    """
    Creates and runs the AdsbClient instance.
    This function will be the target for the ADS-B thread.
    """
    while not stop_event.is_set():
        client = None
        try:
            client = AdsbClient(args.dump1090_host, args.dump1090_port, data_queue, stop_event)
            # The base TcpClient's run() method likely contains the main loop.
            # We need to ensure it respects the stop_event.
            # Let's try running the client's internal loop directly if possible,
            # or wrap the call to run() in our own loop that checks the stop event.
            # The modified run() method above attempts to handle this.
            client.run() # This will block until stop_event is set or connection fails

        except ConnectionRefusedError:
            print(f"ADS-B Main: Connection refused to {args.dump1090_host}:{args.dump1090_port}. Retrying in 10 seconds...")
        except OSError as e:
             print(f"ADS-B Main: OS Error connecting to dump1090: {e}. Retrying in 10 seconds...")
        except Exception as e:
            print(f"ADS-B Main: Error running client: {e}")
            # Avoid rapid restarts on persistent errors
            print("ADS-B Main: Unexpected error. Retrying in 10 seconds...")

        finally:
            # Ensure client was successfully initialized before trying to stop it
            if client and hasattr(client, 'stop'):
                client.stop() # Ensure cleanup if the loop exits unexpectedly

        if not stop_event.is_set():
            time.sleep(10) # Wait before retrying connection

    print("ADS-B Client Thread: Exiting.")

# Example usage (for testing the module directly)
if __name__ == '__main__':
    print("Testing ADS-B Client Module...")
    # Mock args for testing
    class Args:
        dump1090_host = '127.0.0.1'
        dump1090_port = 30002

    test_queue = queue.Queue()
    test_stop_event = threading.Event()

    # Start the client in a thread
    client_thread = threading.Thread(target=run_client, args=(Args(), test_queue, test_stop_event))
    client_thread.start()

    # Simulate running for a while and then stopping
    try:
        start_time = time.time()
        while time.time() - start_time < 15: # Run for 15 seconds
            try:
                data = test_queue.get(timeout=1)
                print(f"Received data: {data}")
            except queue.Empty:
                pass
            if not client_thread.is_alive():
                 print("Client thread terminated unexpectedly.")
                 break
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        test_stop_event.set()
        client_thread.join(timeout=5) # Wait for thread to finish
        print("Test finished.")