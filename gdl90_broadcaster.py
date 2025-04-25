#!/usr/bin/env python3

import argparse
import sys
import time
import threading
import queue
import socket
import json
import serial.tools.list_ports

# Import the run functions from our modules
from modules import adsb_client
from modules import flarm_client
from modules import broadcaster
from modules import sample_traffic_generator
# gdl90 module is used by broadcaster, no direct import needed here usually

DEFAULT_DUMP1090_HOST = '127.0.0.1'
DEFAULT_DUMP1090_PORT = 30002
DEFAULT_SERIAL_BAUD = 38400 # Common FLARM baud rate
DEFAULT_UDP_PORT = 4000
DEFAULT_UDP_BROADCAST_IP = '255.255.255.255' # Standard broadcast address

def list_serial_ports():
    """List available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return []
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description} ({port.hwid})")
    return [port.device for port in ports]

def main():
    parser = argparse.ArgumentParser(description="GDL90 Broadcaster for ADS-B and FLARM data.")

    # ADS-B Source Arguments
    parser.add_argument('--dump1090-host', type=str, default=DEFAULT_DUMP1090_HOST,
                        help=f"Hostname or IP address for dump1090 raw feed (default: {DEFAULT_DUMP1090_HOST})")
    parser.add_argument('--dump1090-port', type=int, default=DEFAULT_DUMP1090_PORT,
                        help=f"Port number for dump1090 raw feed (default: {DEFAULT_DUMP1090_PORT})")

    # FLARM Source Arguments
    parser.add_argument('--serial-port', type=str, required=True,
                        help="Serial port device for FLARM input (e.g., /dev/ttyUSB0, COM3). Use --list-ports to see available ports.")
    parser.add_argument('--serial-baud', type=int, default=DEFAULT_SERIAL_BAUD,
                        help=f"Baud rate for the serial port (default: {DEFAULT_SERIAL_BAUD})")

    # Output Arguments
    parser.add_argument('--udp-port', type=int, default=DEFAULT_UDP_PORT,
                        help=f"UDP port for GDL90 broadcast (default: {DEFAULT_UDP_PORT})")
    parser.add_argument('--udp-broadcast-ip', default='255.255.255.255', help='UDP broadcast IP address (default: 255.255.255.255)')
    parser.add_argument('--interface', type=str, help='Network interface to bind to (e.g., eth0, wlan0)')

    # Add spoofing arguments
    spoof_group = parser.add_argument_group('GPS Spoofing Options')
    spoof_group.add_argument('--spoof-gps', action='store_true', help='Spoof GPS data (lat, lon, speed, track, validity) for testing.')
    spoof_group.add_argument('--location-file', type=str, help='Path to a JSON location configuration file for GPS spoofing.')
    
    # Sample Traffic Generation Options
    traffic_group = parser.add_argument_group('Sample Traffic Generation')
    traffic_group.add_argument('--generate-sample-traffic', action='store_true',
                             help='Generate sample aircraft traffic in an X pattern around ownship location')
    traffic_group.add_argument('--sample-traffic-distance', type=float, default=5.0,
                             help='Distance (in nautical miles) for sample traffic pattern (default: 5.0)')

    # Utility Arguments
    parser.add_argument('--list-ports', action='store_true',
                        help="List available serial ports and exit.")

    args = parser.parse_args()

    if args.list_ports:
        list_serial_ports()
        sys.exit(0)

    print("Starting GDL90 Broadcaster...")
    print(f"  ADS-B Source: {args.dump1090_host}:{args.dump1090_port}")
    print(f"  FLARM Source: {args.serial_port} @ {args.serial_baud} baud")
    print(f"  GDL90 Output: UDP Broadcast to {args.udp_broadcast_ip}:{args.udp_port}")
    
    if args.generate_sample_traffic:
        print(f"  Sample Traffic: Enabled (X pattern, {args.sample_traffic_distance} NM)")
    
    print("Press Ctrl+C to stop.")

    # --- Thread Setup ---
    data_queue = queue.Queue(maxsize=1000) # Limit queue size to prevent memory issues
    stop_event = threading.Event()

    threads = []

    # ADS-B Client Thread
    adsb_thread = threading.Thread(
        target=adsb_client.run_client,
        args=(args, data_queue, stop_event),
        name="ADS-B Client",
        daemon=True # Daemon threads exit when the main program exits
    )
    threads.append(adsb_thread)

    # FLARM Client Thread
    flarm_thread = threading.Thread(
        target=flarm_client.run_client,
        args=(args, data_queue, stop_event),
        name="FLARM Client",
        daemon=True
    )
    threads.append(flarm_thread)

    # Broadcaster Thread
    broadcast_thread = threading.Thread(
        target=broadcaster.run_broadcaster,
        args=(args, data_queue, stop_event),
        name="GDL90 Broadcaster",
        daemon=True
    )
    threads.append(broadcast_thread)
    
    # Sample Traffic Generator Thread (if enabled)
    if args.generate_sample_traffic:
        sample_traffic_thread = threading.Thread(
            target=sample_traffic_generator.run_generator,
            args=(args, data_queue, stop_event),
            name="Sample Traffic Generator",
            daemon=True
        )
        threads.append(sample_traffic_thread)

    # Start all threads
    print("\nStarting worker threads...")
    for thread in threads:
        thread.start()
        print(f"  Started {thread.name}")

    # --- Main Loop ---
    # Keep the main thread alive to handle signals (like Ctrl+C)
    # and potentially monitor thread health.

    try:
        while not stop_event.is_set():
            # Check if any thread has died unexpectedly
            all_alive = True
            for thread in threads:
                if not thread.is_alive():
                    print(f"!!! Thread {thread.name} has stopped unexpectedly. Initiating shutdown. !!!")
                    all_alive = False
                    break
            if not all_alive:
                stop_event.set() # Signal other threads to stop
                break

            time.sleep(1) # Check thread health every second

    except KeyboardInterrupt:
        print("\nCtrl+C detected. Stopping threads gracefully...")
        stop_event.set()
        # Wait for threads to finish
        for thread in threads:
            # Only join threads that were actually started and might still be running
            if thread.is_alive():
                print(f"  Waiting for {thread.name} to stop...")
                thread.join(timeout=5) # Give threads a chance to exit cleanly
                if thread.is_alive():
                    print(f"  Warning: {thread.name} did not stop within timeout.")
        print("Threads stopped.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        print("GDL90 Broadcaster stopped.")

if __name__ == "__main__":
    main()