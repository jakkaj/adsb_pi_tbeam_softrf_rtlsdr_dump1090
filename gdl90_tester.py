#!/usr/bin/env python3

import socket
import struct
import argparse
import time
from datetime import datetime, timezone
import sys
import select

# Attempt to import the CRC function from the existing module
try:
    from modules.gdl90 import calculate_crc, FLAG_BYTE, CONTROL_ESCAPE, ESCAPE_XOR
    from modules.gdl90 import MSG_ID_HEARTBEAT, MSG_ID_OWNSHIP_REPORT, MSG_ID_OWNSHIP_GEO_ALT, MSG_ID_TRAFFIC_REPORT
except ImportError:
    print("Error: Could not import from modules.gdl90.")
    print("Ensure this script is run from the project root directory and modules are accessible.")
    sys.exit(1)

# --- GDL90 Frame Parsing ---

def unstuff_data(stuffed_data):
    """Removes GDL90 byte stuffing."""
    unstuffed = bytearray()
    escape_next = False
    for byte in stuffed_data:
        if escape_next:
            unstuffed.append(byte ^ ESCAPE_XOR)
            escape_next = False
        elif byte == CONTROL_ESCAPE:
            escape_next = True
        else:
            unstuffed.append(byte)
    return bytes(unstuffed)

def parse_frame(raw_data):
    """
    Parses a raw byte sequence to find and validate a GDL90 frame.
    Returns the message payload (ID + Data) if valid, otherwise None.
    Also returns the number of bytes consumed from the raw_data buffer.
    """
    start_index = raw_data.find(FLAG_BYTE)
    if start_index == -1:
        return None, 0 # No start flag found, consume nothing

    end_index = raw_data.find(FLAG_BYTE, start_index + 1)
    if end_index == -1:
        # Found start but no end yet, need more data. Consume nothing for now.
        # Or, if buffer is very large, maybe discard up to start_index? For now, consume 0.
        return None, 0

    stuffed_payload_with_crc = raw_data[start_index + 1 : end_index]
    bytes_consumed = end_index + 1 # Consume up to and including the end flag

    if not stuffed_payload_with_crc:
        # print("Empty frame found") # Debug
        return None, bytes_consumed # Empty frame, consume it

    try:
        unstuffed_payload_with_crc = unstuff_data(stuffed_payload_with_crc)
    except Exception as e:
        print(f"Error unstuffing data: {e}")
        return None, bytes_consumed # Consume the bad frame

    if len(unstuffed_payload_with_crc) < 3: # Need at least ID + 2 CRC bytes
        # print(f"Frame too short after unstuffing: {len(unstuffed_payload_with_crc)} bytes") # Debug
        return None, bytes_consumed # Consume the bad frame

    message_payload = unstuffed_payload_with_crc[:-2]
    received_crc = unstuffed_payload_with_crc[-2:]

    try:
        calculated_crc = calculate_crc(message_payload)
    except Exception as e:
        print(f"Error calculating CRC: {e}")
        return None, bytes_consumed # Consume the bad frame

    if received_crc != calculated_crc:
        # print(f"CRC mismatch! Got: {received_crc.hex()}, Calc: {calculated_crc.hex()}, Payload: {message_payload.hex()}") # Debug
        return None, bytes_consumed # Consume the bad frame

    # If we reach here, the frame is valid
    return message_payload, bytes_consumed

# --- GDL90 Value Decoding ---

def decode_lat_lon(three_bytes):
    """Decodes GDL90 3-byte latitude or longitude into degrees."""
    if len(three_bytes) != 3:
        return None
    # Unpack as 3 bytes, big-endian, then handle 2's complement for 24 bits
    semicircles = (three_bytes[0] << 16) | (three_bytes[1] << 8) | three_bytes[2]
    # Check if the sign bit (bit 23) is set
    if semicircles & (1 << 23):
        # Perform 2's complement conversion for 24 bits
        semicircles -= (1 << 24)

    # Convert semicircles to degrees
    degrees = semicircles * (180.0 / (2**23))
    # Clamp to valid range just in case
    return max(-180.0, min(180.0, degrees))

def decode_altitude_pressure(two_bytes):
    """Decodes GDL90 12-bit pressure altitude into feet."""
    if len(two_bytes) != 2: return None
    encoded_alt = ((two_bytes[0] & 0x0F) << 8) | two_bytes[1]
    if encoded_alt == 0xFFF: # 0xFFF represents invalid/unknown
        return None
    # Value = (Altitude_ft + 1000) / 25
    feet = (encoded_alt * 25.0) - 1000.0
    return feet

def decode_altitude_geometric(two_bytes):
    """Decodes GDL90 16-bit geometric altitude into feet."""
    if len(two_bytes) != 2: return None
    encoded_alt = struct.unpack('>H', two_bytes)[0]
    if encoded_alt == 0xFFFF: # Invalid/Unknown
        return None
    # Value = (Altitude_ft + 1000) / 5
    feet = (encoded_alt * 5.0) - 1000.0
    return feet

def decode_velocity(two_bytes):
    """Decodes GDL90 12-bit horizontal velocity into knots."""
    if len(two_bytes) != 2: return None
    encoded_vel = ((two_bytes[0] & 0x0F) << 8) | two_bytes[1]
    if encoded_vel == 0xFFF: # Invalid/Unknown
        return None
    return float(encoded_vel) # 1 knot increments

def decode_vertical_velocity(two_bytes):
    """Decodes GDL90 12-bit signed vertical velocity into feet per minute."""
    if len(two_bytes) != 2: return None
    encoded_vv = ((two_bytes[0] & 0x0F) << 8) | two_bytes[1]
    # Check for invalid value 0x800 (-2048) which means unknown/invalid
    if encoded_vv == 0x800:
        return None
    # Handle 12-bit two's complement
    if encoded_vv & (1 << 11): # Check sign bit
        encoded_vv -= (1 << 12)
    # Value = VV_fpm / 64
    fpm = encoded_vv * 64.0
    return fpm

def decode_track_heading(one_byte):
    """Decodes GDL90 8-bit track/heading into degrees."""
    if len(one_byte) != 1: return None
    encoded = one_byte[0]
    # Value = degrees * (256 / 360) -> degrees = Value * (360 / 256)
    degrees = encoded * (360.0 / 256.0)
    return degrees

def decode_icao_address(three_bytes):
    """Decodes GDL90 3-byte ICAO address into a hex string."""
    if len(three_bytes) != 3: return "Invalid"
    icao_int = (three_bytes[0] << 16) | (three_bytes[1] << 8) | three_bytes[2]
    return f"{icao_int:06X}"

def decode_callsign(eight_bytes):
    """Decodes GDL90 8-byte callsign."""
    if len(eight_bytes) != 8: return "Invalid"
    try:
        # Replace non-printable chars, strip trailing spaces
        cleaned = bytes(b if 32 <= b <= 126 else ord('?') for b in eight_bytes)
        return cleaned.decode('ascii').strip()
    except UnicodeDecodeError:
        return "DecodeErr"

# --- Message Decoding Functions ---

def decode_heartbeat(payload):
    # Heartbeat payload = ID(1) + Status1(1) + Status2(1) + TS_Low(2) = 5 bytes
    if len(payload) < 5: return None
    # Unpack ID, Status1, Status2 as big-endian bytes
    # Unpack Timestamp lower 16 bits as little-endian unsigned short
    msg_id, status1, status2 = struct.unpack('>BBB', payload[:3])
    ts_lower_16, = struct.unpack('<H', payload[3:5]) # Comma unpacks the single tuple element

    # Status Byte 1
    uat_init = bool(status1 & 0x80)
    ratcs = bool(status1 & 0x40) # Reserved
    cdti_avail = bool(status1 & 0x20)
    gnd_uplink = bool(status1 & 0x10)
    fisb_avail = bool(status1 & 0x08)

    # Status Byte 2
    # Bit 7 (MSB) contains bit 16 of the timestamp
    ts_bit16 = (status2 & 0x80) >> 7
    gps_valid = bool(status2 & 0x40)
    maint_req = bool(status2 & 0x20)
    ident_active = bool(status2 & 0x10)
    # reserved_bits = status2 & 0x0F # Not usually displayed

    # Timestamp: Reconstruct from lower 16 bits and the bit stored in Status2
    # Note: GDL90 spec v1.0 doesn't explicitly define timestamp type bit, assume UTC based on create_heartbeat_message
    utc_timestamp_field = (ts_bit16 << 16) | ts_lower_16
    seconds_since_midnight = utc_timestamp_field / 10.0 # GDL90 timestamp is 0.1s increments

    return {
        "Type": "Heartbeat",
        "UAT Initialized": uat_init,
        "CDTI Available": cdti_avail,
        "Ground Uplink": gnd_uplink,
        "FIS-B Available": fisb_avail,
        # "Timestamp Type": "GPS" if ts_type_gps else "UTC", # Bit 7 is used for timestamp, not type - Removed this line
        "GPS Valid": gps_valid,
        "Maintenance Req": maint_req,
        "IDENT Active": ident_active,
        # "Timestamp (sec*10)": utc_timestamp_field, # Raw value
        "Seconds Since Midnight": f"{seconds_since_midnight:.1f}",
    }

def decode_ownship_report(payload):
    if len(payload) < 16: return None
    # ID(1) Lat(3) Lon(3) Alt(2) Misc(1) NavInt(1) GS(2) VV(2) Track(1) = 16 bytes
    lat = decode_lat_lon(payload[1:4])
    lon = decode_lat_lon(payload[4:7])
    alt_press = decode_altitude_pressure(payload[7:9])
    misc_byte = payload[9]
    nav_integrity_byte = payload[10]
    gs_knots = decode_velocity(payload[11:13])
    vv_fpm = decode_vertical_velocity(payload[13:15])
    track_deg = decode_track_heading(payload[15:16])

    misc_flags = (misc_byte >> 4) & 0x0F # e.g., 1=Airborne, 2=On Ground
    nic = (nav_integrity_byte >> 4) & 0x0F
    nac_p = nav_integrity_byte & 0x0F

    misc_map = {1: "Airborne", 2: "On Ground"}

    return {
        "Type": "Ownship Report",
        "Latitude": f"{lat:.5f}" if lat is not None else "Invalid",
        "Longitude": f"{lon:.5f}" if lon is not None else "Invalid",
        "Altitude (Press)": f"{alt_press:.0f} ft" if alt_press is not None else "Invalid",
        "Status": misc_map.get(misc_flags, f"Code {misc_flags}"),
        "NIC": nic,
        "NACp": nac_p,
        "Ground Speed": f"{gs_knots:.0f} kts" if gs_knots is not None else "Invalid",
        "Vertical Velocity": f"{vv_fpm:.0f} fpm" if vv_fpm is not None else "Invalid",
        "Track": f"{track_deg:.1f}°" if track_deg is not None else "Invalid",
    }

def decode_ownship_geo_altitude(payload):
     if len(payload) < 5: return None
     # ID(1) AltGeo(2) VPL(2) = 5 bytes
     alt_geo = decode_altitude_geometric(payload[1:3])
     vpl_code = struct.unpack('>H', payload[3:5])[0]

     # TODO: Decode VPL code to meters if needed
     vpl_display = f"Code {vpl_code}" if vpl_code != 0xFFFF else "Unknown (>185m)"

     return {
         "Type": "Ownship Geo Alt",
         "Altitude (Geo)": f"{alt_geo:.0f} ft" if alt_geo is not None else "Invalid",
         "VPL": vpl_display,
     }

def decode_traffic_report(payload):
    if len(payload) < 28: return None
    # ID(1) Status(1) ICAO(3) Lat(3) Lon(3) Alt(2) NavInt(1) GS(2) VV(2) Track(1) Emitter(1) Callsign(8) = 28 bytes
    status_byte = payload[1]
    icao = decode_icao_address(payload[2:5])
    lat = decode_lat_lon(payload[5:8])
    lon = decode_lat_lon(payload[8:11])
    alt_press = decode_altitude_pressure(payload[11:13])
    nav_integrity_byte = payload[13]
    gs_knots = decode_velocity(payload[14:16])
    vv_fpm = decode_vertical_velocity(payload[16:18])
    track_deg = decode_track_heading(payload[18:19])
    emitter_cat = payload[19]
    callsign = decode_callsign(payload[20:28])

    alert_status = (status_byte >> 4) & 0x0F
    addr_type = status_byte & 0x0F
    nic = (nav_integrity_byte >> 4) & 0x0F
    nac_p = nav_integrity_byte & 0x0F

    addr_type_map = {0: "ADS-B/ICAO", 1: "Self-assigned", 2: "TIS-B/Fine", 3: "TIS-B/Coarse", 4: "Surface", 5: "Reserved"}
    alert_status_map = {0: "No Alert", 1: "Traffic Alert"}
    # Basic emitter category mapping (refer to DO-282B / GDL90 spec for full list)
    emitter_map = {
        0: "No Info", 1: "Light", 2: "Small", 3: "Large", 4: "High Vortex", 5: "Heavy",
        6: "High Perf", 7: "Rotorcraft", 9: "Glider", 10: "Lighter-than-air",
        11: "Parachute", 12: "Ultralight", 14: "UAV", 15: "Space",
        17: "Surface/Emergency", 18: "Surface/Service", 19: "Point Obstacle",
        20: "Cluster Obstacle", 21: "Line Obstacle"
    }


    return {
        "Type": "Traffic Report",
        "ICAO": icao,
        "Callsign": callsign if callsign else "-",
        "Alert Status": alert_status_map.get(alert_status, f"Code {alert_status}"),
        "Address Type": addr_type_map.get(addr_type, f"Code {addr_type}"),
        "Latitude": f"{lat:.5f}" if lat is not None else "Invalid",
        "Longitude": f"{lon:.5f}" if lon is not None else "Invalid",
        "Altitude (Press)": f"{alt_press:.0f} ft" if alt_press is not None else "Invalid",
        "NIC": nic,
        "NACp": nac_p,
        "Ground Speed": f"{gs_knots:.0f} kts" if gs_knots is not None else "Invalid",
        "Vertical Velocity": f"{vv_fpm:.0f} fpm" if vv_fpm is not None else "Invalid",
        "Track": f"{track_deg:.1f}°" if track_deg is not None else "Invalid",
        "Emitter Cat": emitter_map.get(emitter_cat, f"Code {emitter_cat}"),
    }

DECODERS = {
    MSG_ID_HEARTBEAT: decode_heartbeat,
    MSG_ID_OWNSHIP_REPORT: decode_ownship_report,
    MSG_ID_OWNSHIP_GEO_ALT: decode_ownship_geo_altitude,
    MSG_ID_TRAFFIC_REPORT: decode_traffic_report,
}

MESSAGE_TYPE_NAMES = {
    MSG_ID_HEARTBEAT: "Heartbeat",
    MSG_ID_OWNSHIP_REPORT: "Ownship Report",
    MSG_ID_OWNSHIP_GEO_ALT: "Ownship Geo Alt",
    MSG_ID_TRAFFIC_REPORT: "Traffic Report",
}


# --- Main Listener Logic ---

def main():
    parser = argparse.ArgumentParser(description="GDL90 Message Listener and Decoder")
    parser.add_argument('--port', type=int, default=4000,
                        help="UDP port to listen on (default: 4000)")
    parser.add_argument('--bind-address', type=str, default='0.0.0.0',
                        help="Address to bind the UDP socket (default: 0.0.0.0)")
    parser.add_argument('--filter', type=str, nargs='*',
                        help="Only show specific message types by name (e.g., heartbeat traffic)")
    parser.add_argument('--raw', action='store_true',
                        help="Show raw hexadecimal payload for each message")
    parser.add_argument('--stats', action='store_true',
                        help="Show message statistics periodically")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="Increase output verbosity (show CRC errors, unknown IDs, etc.)")
    args = parser.parse_args()

    # Normalize filter names to lower case for comparison
    filter_types = [f.lower() for f in args.filter] if args.filter else None

    print(f"Listening for GDL90 messages on UDP {args.bind_address}:{args.port}...")
    if filter_types:
        print(f"Filtering for message types: {', '.join(args.filter)}")

    sock = None
    buffer = b""
    msg_counts = {}
    last_stats_time = time.monotonic()
    total_msgs = 0
    total_bytes = 0
    crc_errors = 0
    unknown_msgs = 0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Enable broadcasting reception if needed, though binding to 0.0.0.0 usually suffices
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # May require root
        sock.bind((args.bind_address, args.port))
        sock.setblocking(False) # Use non-blocking socket with select
        print("Socket bound successfully. Press Ctrl+C to stop.")

        while True:
            # Use select for non-blocking read with timeout
            ready_to_read, _, _ = select.select([sock], [], [], 0.1) # 100ms timeout

            if ready_to_read:
                try:
                    data, addr = sock.recvfrom(4096) # Read up to 4096 bytes
                    # print(f"Received {len(data)} bytes from {addr}") # Debug raw receive
                    total_bytes += len(data)
                    buffer += data
                except socket.error as e:
                    print(f"Socket error receiving data: {e}")
                    time.sleep(1) # Avoid busy-loop on error
                    continue
                except Exception as e:
                    print(f"Unexpected error receiving data: {e}")
                    time.sleep(1)
                    continue

            # Process the buffer to find frames
            while True:
                original_buffer_len = len(buffer)
                payload, consumed = parse_frame(buffer)

                if consumed > 0:
                    # Frame processed (valid or invalid), remove consumed bytes
                    buffer = buffer[consumed:]
                elif len(buffer) > 4096: # Prevent buffer growing indefinitely if no flags found
                     print("Buffer overflow without finding frame flags, clearing buffer.")
                     buffer = b""
                     break # Exit inner loop, wait for more data
                else:
                    # No complete frame found or no start flag, need more data
                    break # Exit inner loop, wait for more data

                if payload:
                    total_msgs += 1
                    message_id = payload[0]
                    msg_counts[message_id] = msg_counts.get(message_id, 0) + 1

                    decoder = DECODERS.get(message_id)
                    msg_type_name = MESSAGE_TYPE_NAMES.get(message_id, f"ID 0x{message_id:02X}")

                    # Apply filtering
                    should_display = True
                    if filter_types and msg_type_name.lower().replace(" ", "") not in filter_types:
                         should_display = False

                    if should_display:
                        if decoder:
                            decoded_msg = decoder(payload)
                            if decoded_msg:
                                timestamp_str = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                                print(f"--- {timestamp_str} | {msg_type_name} (ID: 0x{message_id:02X}) ---")
                                for key, value in decoded_msg.items():
                                    if key != "Type": # Don't print type again
                                        print(f"  {key}: {value}")
                                if args.raw:
                                    print(f"  Raw Payload: {payload.hex().upper()}")
                                print("-" * (len(timestamp_str) + len(msg_type_name) + 15)) # Match header length
                            else:
                                if args.verbose:
                                    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}] Failed to decode {msg_type_name}, Payload: {payload.hex()}")
                        else:
                            unknown_msgs += 1
                            if args.verbose:
                                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}] Unknown message ID: 0x{message_id:02X}, Payload: {payload.hex()}")
                elif consumed > 0: # Frame was consumed but invalid (CRC error, short, etc.)
                    crc_errors += 1
                    if args.verbose:
                         # CRC errors are common if data stream is noisy or frames overlap
                         # Only print if verbose to avoid flooding console
                         print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]}] Invalid frame detected (CRC/Format Error)")


            # Print stats periodically
            now = time.monotonic()
            if args.stats and (now - last_stats_time >= 10.0): # Print every 10 seconds
                print("\n--- Statistics (last 10s) ---")
                print(f"Total Bytes Received: {total_bytes}")
                print(f"Total Valid Messages: {total_msgs}")
                print(f"CRC/Format Errors: {crc_errors}")
                print(f"Unknown Message IDs: {unknown_msgs}")
                print("Message Counts by ID:")
                for msg_id, count in sorted(msg_counts.items()):
                    name = MESSAGE_TYPE_NAMES.get(msg_id, f"ID 0x{msg_id:02X}")
                    print(f"  {name}: {count}")
                print("-----------------------------\n")
                # Reset counters for next interval if desired, or keep cumulative
                last_stats_time = now


    except KeyboardInterrupt:
        print("\nStopping listener...")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if sock:
            sock.close()
            print("Socket closed.")
        print("GDL90 Tester stopped.")

if __name__ == "__main__":
    main()