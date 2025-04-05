import pyModeS as pms
from pyModeS.extra.tcpclient import TcpClient
import time

class Dump1090Client(TcpClient):
    def __init__(self, host='127.0.0.1', port=30002, rawtype='raw'):
        # Call super init without rawtype, as it seems unsupported in this version
        # Call super init with host, port, and datatype ('raw' for port 30002)
        super().__init__(host, port, 'raw')
        print(f"Connecting to {host}:{port} ({rawtype} format)...")

    def handle_messages(self, messages):
        """
        Processes a list of received messages.

        Args:
            messages: A list of tuples, where each tuple contains
                      (hex_message_string, timestamp).
        """
        for msg, ts in messages:
            if not msg or len(msg) != 28: # Basic check for typical ADS-B message length
                continue

            # Check Downlink Format (DF) and CRC
            df = pms.df(msg)
            if df != 17: # Only process ADS-B messages (DF17)
                continue
            if pms.crc(msg) != 0: # Check CRC
                # print(f"CRC failed for message: {msg}") # Optional: Log CRC failures
                continue

            # Decode basic ADS-B info
            icao = pms.icao(msg)
            tc = pms.adsb.typecode(msg)

            print(f"[{ts:.2f}] ICAO: {icao}, TC: {tc:2d}", end="")

            # Decode specific info based on Type Code (TC)
            try:
                if 1 <= tc <= 4: # Identification and Category
                    callsign = pms.adsb.callsign(msg)
                    print(f", Callsign: {callsign.strip('_')}")
                elif 5 <= tc <= 8: # Surface Position
                    # Requires reference position for full decoding, just print TC for now
                    print(", Type: Surface Position")
                elif 9 <= tc <= 18: # Airborne Position (with Baro Altitude)
                    alt = pms.adsb.altitude(msg)
                    # Position decoding requires message pairs or reference, print altitude
                    print(f", Altitude: {alt} ft")
                elif tc == 19: # Airborne Velocity
                    vel = pms.adsb.velocity(msg) # Returns (speed, heading, vert_rate, speed_type)
                    print(f", Speed: {vel[0]} kts, Heading: {vel[1]:.1f} deg, VR: {vel[2]} fpm ({vel[3]})")
                elif 20 <= tc <= 22: # Airborne Position (with GNSS Height)
                    alt = pms.adsb.altitude(msg) # GNSS Height
                    print(f", GNSS Alt: {alt} ft")
                else:
                    print(", Type: Other/Unknown") # Handle other TCs if needed

            except Exception as e:
                print(f"\nError decoding TC {tc} for {icao}: {e}")


if __name__ == '__main__':
    try:
        client = Dump1090Client()
        client.run()
    except ConnectionRefusedError:
        print("Connection refused. Is dump1090 running and providing data on port 30002?")
    except KeyboardInterrupt:
        print("\nStopping client...")
    finally:
        # TcpClient usually handles cleanup, but added explicit stop just in case
        if 'client' in locals() and hasattr(client, 'stop'):
             client.stop()
        print("Client stopped.")