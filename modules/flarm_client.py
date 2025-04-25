import serial
import time
import queue
import threading
from datetime import datetime, timezone
import logging

def parse_nmea(sentence):
    """Basic NMEA sentence parsing."""
    if not sentence or not sentence.startswith('$'):
        return None, None

    # Remove checksum if present
    checksum_pos = sentence.find('*')
    if checksum_pos != -1:
        # TODO: Optionally validate checksum here
        sentence = sentence[:checksum_pos]

    parts = sentence.split(',')
    if len(parts) < 1:
        return None, None

    message_type = parts[0][1:] # Remove '$'
    return message_type, parts[1:]

def run_client(args, data_queue, stop_event):
    """
    Connects to the specified serial port, reads NMEA data (expecting FLARM),
    logs raw NMEA to console, and puts structured data into the queue.
    This function will be the target for the FLARM thread.
    """
    serial_port = args.serial_port
    baud_rate = args.serial_baud
    buffer = ""

    logging.info(f"FLARM Client: Attempting to connect to {serial_port} at {baud_rate} baud...")

    while not stop_event.is_set():
        ser = None
        try:
            ser = serial.Serial(serial_port, baud_rate, timeout=1) # 1-second timeout
            logging.info(f"FLARM Client: Successfully connected to {serial_port}")

            while not stop_event.is_set():
                try:
                    if ser.in_waiting > 0:
                        # Read available data, decode assuming ASCII/UTF-8 compatibility
                        try:
                            data_bytes = ser.read(ser.in_waiting)
                            data_str = data_bytes.decode('ascii', errors='replace')
                        except UnicodeDecodeError:
                             data_str = data_bytes.decode('utf-8', errors='replace') # Fallback

                        buffer += data_str

                        # Process complete lines from the buffer
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip() # Remove leading/trailing whitespace and \r

                            if line.startswith('$'):
                                # Log raw NMEA sentence to console
                                timestamp_str = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                                logging.debug(f"FLARM Raw [{timestamp_str}]: {line}")

                                # Parse the NMEA sentence
                                msg_type, fields = parse_nmea(line)

                                if msg_type:
                                    flarm_data = {
                                        'source': 'flarm',
                                        'raw_nmea': line,
                                        'msg_type': msg_type,
                                        'fields': fields,
                                        'timestamp': datetime.now(timezone.utc)
                                    }
                                    try:
                                        data_queue.put(flarm_data, block=False)
                                    except queue.Full:
                                        # logging.warning("FLARM data queue is full. Discarding message.")
                                        pass
                    else:
                        # No data waiting, sleep briefly to prevent busy-waiting
                        time.sleep(0.05)

                except serial.SerialException as e:
                    logging.error(f"FLARM Client: Serial error on {serial_port}: {e}")
                    # Assume disconnection, break inner loop to reconnect
                    break
                except OSError as e:
                    logging.error(f"FLARM Client: OS error reading from {serial_port}: {e}")
                    break # Assume disconnection
                except Exception as e:
                    logging.error(f"FLARM Client: Unexpected error reading/processing data: {e}")
                    # Log error but try to continue reading
                    time.sleep(0.1)

            # End of inner loop (either stopped or serial error)
            if ser and ser.is_open:
                ser.close()
                logging.info(f"FLARM Client: Closed connection to {serial_port}")

        except serial.SerialException as e:
            logging.error(f"FLARM Client: Failed to open {serial_port}: {e}")
        except Exception as e:
            logging.error(f"FLARM Client: Error setting up serial connection: {e}")

        # If we're here due to an error and not stopped, wait before retrying
        if not stop_event.is_set():
            logging.info("FLARM Client: Retrying connection in 10 seconds...")
            time.sleep(10)

    # Clean up if loop exited because stop_event was set
    if ser and ser.is_open:
        ser.close()
        logging.info(f"FLARM Client: Closed connection to {serial_port} on exit.")

    logging.info("FLARM Client Thread: Exiting.")


# Example usage (for testing the module directly)
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="FLARM Client Module")
    parser.add_argument('--serial-port', type=str, default='/dev/ttyS0', help='Serial port to connect to')
    parser.add_argument('--serial-baud', type=int, default=38400, help='Baud rate for serial port')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s: %(message)s"
    )

    test_queue = queue.Queue()
    test_stop_event = threading.Event()

    logging.info(f"Attempting to read from {args.serial_port} at {args.serial_baud} baud.")
    logging.info("Connect a FLARM device or NMEA source to test.")
    logging.info("Press Ctrl+C to stop.")

    # Start the client in a thread
    client_thread = threading.Thread(target=run_client, args=(args, test_queue, test_stop_event))
    client_thread.start()

    # Monitor the queue
    try:
        while True:
            try:
                data = test_queue.get(timeout=1)
                logging.info(f"Received in Queue: {data}")
            except queue.Empty:
                pass
            if not client_thread.is_alive():
                logging.error("Client thread terminated unexpectedly.")
                break
            time.sleep(0.1) # Prevent busy loop in main thread
    except KeyboardInterrupt:
        logging.info("Stopping test...")
    finally:
        test_stop_event.set()
        client_thread.join(timeout=5) # Wait for thread to finish
        logging.info("Test finished.")