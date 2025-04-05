#!/usr/bin/env python3

import sys
import time
import serial
import serial.tools.list_ports
import re
from datetime import datetime

def list_serial_ports():
    """List all available serial ports."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
        return []
    
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i+1}. {port.device} - {port.description} ({port.hwid})")
    
    return [port.device for port in ports]

def test_port(port, baud_rate=9600, timeout=1, test_duration=5):
    """Test if there's activity on the given port."""
    print(f"\nTesting port {port} at {baud_rate} baud...")
    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        start_time = time.time()
        received_data = False
        data_samples = []
        
        while time.time() - start_time < test_duration:
            if ser.in_waiting:
                try:
                    data = ser.read(ser.in_waiting)
                    if data:
                        received_data = True
                        data_samples.append(data)
                        print(f"Received data: {data}")
                except Exception as e:
                    print(f"Error reading data: {e}")
            time.sleep(0.1)
            
        ser.close()
        
        if received_data:
            print(f"✅ Port {port} shows activity!")
            if data_samples:
                print(f"Sample data received: {data_samples[0][:20]}")
            return True
        else:
            print(f"❌ No data received on port {port}")
            return False
            
    except Exception as e:
        print(f"Error opening port {port}: {e}")
        return False

def find_baud_rate(port, timeout=1, test_duration=2):
    """Try multiple baud rates to determine the correct one for a port."""
    common_baud_rates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    print(f"\nAutomatically testing different baud rates for {port}...")
    
    successful_bauds = []
    
    for baud in common_baud_rates:
        print(f"\nTrying {baud} baud...")
        try:
            ser = serial.Serial(port, baud, timeout=timeout)
            start_time = time.time()
            received_data = False
            data_samples = []
            
            while time.time() - start_time < test_duration:
                if ser.in_waiting:
                    try:
                        data = ser.read(ser.in_waiting)
                        if data:
                            received_data = True
                            data_samples.append(data)
                            print(f"Received data at {baud} baud: {data}")
                    except Exception as e:
                        print(f"Error reading data: {e}")
                time.sleep(0.1)
                
            ser.close()
            
            if received_data:
                print(f"✅ Success! {baud} baud rate shows activity")
                successful_bauds.append((baud, data_samples[0][:20] if data_samples else b''))
            else:
                print(f"❌ No data received at {baud} baud")
                
        except Exception as e:
            print(f"Error testing baud {baud}: {e}")
    
    return successful_bauds

def parse_nmea(sentence):
    """Parse an NMEA sentence and return the message type and data."""
    if not sentence.startswith('$'):
        return None, None
    
    # Remove the checksum part if present
    checksum_pos = sentence.find('*')
    if checksum_pos != -1:
        sentence = sentence[:checksum_pos]
    
    # Split the sentence into its components
    parts = sentence.split(',')
    if len(parts) < 2:
        return None, None
    
    message_type = parts[0][1:]  # Remove the $ from the message type
    return message_type, parts[1:]

def parse_flarm_data(data):
    """Parse FLARM specific NMEA sentences."""
    if isinstance(data, bytes):
        try:
            # Try to decode as ASCII or UTF-8
            data_str = data.decode('ascii', errors='replace')
        except UnicodeDecodeError:
            data_str = data.decode('utf-8', errors='replace')
    else:
        data_str = data
        
    # Split into individual sentences
    sentences = data_str.strip().split('\r\n')
    parsed_data = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        message_type, fields = parse_nmea(sentence)
        
        if not message_type:
            continue
            
        # Parse known FLARM message types
        if message_type == 'PFLAA':  # FLARM traffic info
            if len(fields) >= 6:
                # PFLAA,<AlarmLevel>,<RelativeNorth>,<RelativeEast>,<RelativeVertical>,<IDType>,<ID>,<Track>,<TurnRate>,<GroundSpeed>,<ClimbRate>,<AcftType>
                parsed = {
                    'type': 'PFLAA',
                    'alarm_level': int(fields[0]) if fields[0] else None,
                    'relative_north': int(fields[1]) if fields[1] else None, 
                    'relative_east': int(fields[2]) if fields[2] else None,
                    'relative_vertical': int(fields[3]) if fields[3] else None,
                    'id_type': int(fields[4]) if fields[4] else None,
                    'id': fields[5] if len(fields) > 5 else None,
                    'track': int(fields[6]) if len(fields) > 6 and fields[6] else None,
                    'ground_speed': int(fields[8]) if len(fields) > 8 and fields[8] else None,
                    'climb_rate': int(fields[9]) if len(fields) > 9 and fields[9] else None,
                    'acft_type': fields[10] if len(fields) > 10 else None
                }
                parsed_data.append(parsed)
                
        elif message_type == 'PGRMZ':  # Garmin altitude
            if len(fields) >= 3:
                parsed = {
                    'type': 'PGRMZ',
                    'altitude': int(fields[0]) if fields[0] else None,
                    'unit': fields[1],
                    'mode': fields[2]
                }
                parsed_data.append(parsed)
                
        elif message_type == 'PFLAU':  # FLARM status
            if len(fields) >= 6:
                # PFLAU,<RX>,<TX>,<GPS>,<Power>,<AlarmLevel>,<RelativeBearing>,<AlarmType>,<RelativeVertical>,<RelativeDistance>
                parsed = {
                    'type': 'PFLAU',
                    'rx': int(fields[0]) if fields[0] else None,
                    'tx': int(fields[1]) if fields[1] else None,
                    'gps': int(fields[2]) if fields[2] else None,
                    'power': int(fields[3]) if fields[3] else None,
                    'alarm_level': int(fields[4]) if fields[4] else None,
                    'relative_bearing': int(fields[5]) if len(fields) > 5 and fields[5] else None,
                    'alarm_type': int(fields[6]) if len(fields) > 6 and fields[6] else None,
                }
                parsed_data.append(parsed)
                
        else:
            # Include any other NMEA sentences
            parsed = {
                'type': message_type,
                'raw': ','.join(fields)
            }
            parsed_data.append(parsed)
            
    return parsed_data

def monitor_flarm(port, baud_rate=38400, timeout=1, duration=None):
    """Monitor FLARM data on the given port."""
    print(f"\nMonitoring FLARM data on {port} at {baud_rate} baud...")
    print("Press Ctrl+C to stop\n")
    
    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        start_time = time.time()
        
        while True:
            if duration and time.time() - start_time > duration:
                break
                
            if ser.in_waiting:
                try:
                    data = ser.read(ser.in_waiting)
                    if data:
                        parsed = parse_flarm_data(data)
                        for item in parsed:
                            display_flarm_data(item)
                except Exception as e:
                    print(f"Error reading data: {e}")
            time.sleep(0.1)
            
        ser.close()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        if 'ser' in locals():
            ser.close()
    except Exception as e:
        print(f"Error monitoring port {port}: {e}")

def display_flarm_data(data):
    """Display parsed FLARM data in a readable format."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    if data['type'] == 'PFLAA':
        # Colorize alarm levels
        alarm_colors = {0: "", 1: "\033[33m", 2: "\033[31m", 3: "\033[31;1m"}
        alarm_level = data['alarm_level'] if data['alarm_level'] is not None else 0
        alarm_color = alarm_colors.get(alarm_level, "")
        reset_color = "\033[0m" if alarm_color else ""
        
        # Calculate distance
        distance = None
        if data['relative_north'] is not None and data['relative_east'] is not None:
            import math
            distance = math.sqrt(data['relative_north']**2 + data['relative_east']**2)
            distance_str = f"{distance:.0f}m"
        else:
            distance_str = "?"
        
        # Format direction 
        direction = None
        if data['relative_north'] is not None and data['relative_east'] is not None:
            direction = (90 - (math.degrees(math.atan2(data['relative_north'], data['relative_east'])) % 360)) % 360
            direction_str = f"{direction:.0f}°"
        else:
            direction_str = "?"
            
        print(f"{timestamp} {alarm_color}TRAFFIC: ID:{data['id']} Dist:{distance_str} Dir:{direction_str}", end="")
        
        if data['relative_vertical'] is not None:
            vs = data['relative_vertical']
            if vs > 0:
                print(f" +{vs}m", end="")
            elif vs < 0:
                print(f" {vs}m", end="")
                
        if data['ground_speed'] is not None:
            print(f" {data['ground_speed']}kt", end="")
            
        if data['climb_rate'] is not None:
            cr = data['climb_rate']/10 if data['climb_rate'] is not None else 0
            if cr > 0:
                print(f" +{cr:.1f}m/s", end="")
            elif cr < 0:
                print(f" {cr:.1f}m/s", end="")
                
        if data['acft_type'] is not None:
            print(f" Type:{data['acft_type']}", end="")
            
        print(f"{reset_color}")
    
    elif data['type'] == 'PFLAU':
        gps_status = ["No signal", "Weak signal", "3D fix", "3D fix + diff", "Unknown", "Unknown", "Unknown", "Unknown", "WAAS"]
        gps = data['gps'] if data['gps'] is not None and data['gps'] < len(gps_status) else 0
        print(f"{timestamp} STATUS: RX:{data['rx']} GPS:{gps_status[gps]} {'TX:ON' if data['tx']==1 else 'TX:OFF'}")
    
    elif data['type'] == 'PGRMZ':
        if data['altitude'] is not None:
            print(f"{timestamp} ALTITUDE: {data['altitude']} {data['unit']}")
    
    else:
        # Print other messages as raw data
        print(f"{timestamp} {data['type']}: {data['raw'] if 'raw' in data else str(data)}")

def main():
    ports = list_serial_ports()
    
    if args.port:
        if args.port not in ports and not args.force:
            print(f"Warning: {args.port} is not in the list of available ports.")
            confirm = input("Continue anyway? (y/n): ")
            if confirm.lower() != 'y':
                sys.exit(1)
        
        if args.monitor_flarm:
            monitor_flarm(args.port, args.baud, duration=args.time if args.time > 0 else None)
        elif args.find_baud:
            successful_bauds = find_baud_rate(args.port, test_duration=args.time)
            if successful_bauds:
                print("\n== Results ==")
                print(f"Port {args.port} responded at these baud rates:")
                for baud, sample in successful_bauds:
                    print(f"- {baud} baud (sample: {sample})")
                print(f"\nRecommended baud rate: {successful_bauds[0][0]}")
            else:
                print(f"\nNo successful baud rate found for {args.port}")
                print("Try increasing the test duration with -t option")
        else:
            test_port(args.port, args.baud, test_duration=args.time)
    else:
        if not ports:
            sys.exit(1)
            
        print("\nScanning ports for activity...")
        
        active_ports = []
        for port in ports:
            if test_port(port, args.baud, test_duration=args.time):
                active_ports.append(port)
        
        if active_ports:
            print("\n== Results ==")
            print(f"Active ports detected: {', '.join(active_ports)}")
        else:
            print("\nNo active ports detected. Try:")
            print("1. Ensure your device is connected and powered on")
            print("2. Try different baud rates using the -b option")
            print("3. Increase the test duration using the -t option")
            print("4. Use --port and --find-baud to auto-detect the correct baud rate")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan serial ports for device activity")
    parser.add_argument("-b", "--baud", type=int, default=9600, 
                        help="Baud rate to test (default: 9600)")
    parser.add_argument("-t", "--time", type=int, default=5,
                        help="Test duration in seconds for each port (default: 5)")
    parser.add_argument("-p", "--port", type=str,
                        help="Specify a particular port to test")
    parser.add_argument("--find-baud", action="store_true",
                        help="Automatically try multiple baud rates on the specified port")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force operation even if port is not listed as available")
    parser.add_argument("--monitor-flarm", action="store_true",
                        help="Monitor and parse FLARM NMEA data")
    args = parser.parse_args()
    
    main()

# Example usage:
# python3 serialscanner.py -p /dev/ttyAMA4 --monitor-flarm -b 38400