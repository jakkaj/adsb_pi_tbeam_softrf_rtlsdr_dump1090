# GDL90 Test Implementation Guide

This document contains implementation details for creating a test script that uses the sample GDL90 code to test our broadcaster.

## Test Script Implementation

To implement the GDL90 broadcaster test, create a Python script named `gdl90_test_receiver.py` with the following content:

```python
#!/usr/bin/env python3
"""
GDL90 Test Receiver

This script uses the sample GDL90 receiver code to test our broadcaster implementation.
It runs the sample receiver, captures the output, and validates the received messages.
"""

import subprocess
import time
import threading
import queue
import re
import sys
import os
import argparse
from datetime import datetime

# Queue for receiver output
receiver_output = queue.Queue()

def run_receiver(interface, port, verbose=True):
    """Start the sample GDL90 receiver"""
    # Path to the sample receiver relative to project root
    sample_path = "sample/gdl90-sample/gdl90-master/gdl90_receiver.py"
    
    # Build command
    cmd = [
        "python3", 
        sample_path,
        f"--interface={interface}",
        f"--port={port}"
    ]
    
    if verbose:
        cmd.append("--verbose")
    
    print(f"Starting receiver: {' '.join(cmd)}")
    
    # Run the receiver
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # Start thread to capture output
    output_thread = threading.Thread(target=capture_output, args=(proc,))
    output_thread.daemon = True
    output_thread.start()
    
    return proc, output_thread

def capture_output(proc):
    """Capture and process output from the sample receiver"""
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        line_str = line.decode('utf-8').strip()
        receiver_output.put(line_str)
        print(f"Receiver: {line_str}")

def process_messages(timeout=60, message_types=None):
    """
    Process and validate received messages
    
    Args:
        timeout: Time in seconds to listen for messages
        message_types: List of message types to track (e.g., ["MSG00", "MSG10", "MSG20"])
    
    Returns:
        Dict of message counts by type
    """
    if message_types is None:
        message_types = ["MSG00", "MSG10", "MSG0B", "MSG14"]
    
    start_time = time.time()
    message_counts = {msg_type: 0 for msg_type in message_types}
    
    # Translation for more readable output
    msg_names = {
        "MSG00": "Heartbeat",
        "MSG10": "Ownship Report",
        "MSG0B": "Ownship Geo Altitude",
        "MSG14": "Traffic Report"
    }
    
    print(f"\nListening for messages for {timeout} seconds...")
    print(f"Tracking message types: {', '.join(message_types)}")
    
    while time.time() - start_time < timeout:
        try:
            line = receiver_output.get(timeout=1)
            
            # Check for message types
            for msg_type in message_types:
                if msg_type in line:
                    message_counts[msg_type] += 1
                    readable_name = msg_names.get(msg_type, msg_type)
                    print(f"Detected {readable_name} message")
                    
                    # Parse and display key fields based on message type
                    if "timestamp" in line.lower():
                        timestamp_match = re.search(r'timestamp: (\d+)', line)
                        if timestamp_match:
                            timestamp = timestamp_match.group(1)
                            print(f"  - Timestamp: {timestamp}")
                    
                    if "position" in line.lower():
                        position_match = re.search(r'position: \(([-\d.]+), ([-\d.]+)\)', line)
                        if position_match:
                            lat, lon = position_match.group(1), position_match.group(2)
                            print(f"  - Position: ({lat}, {lon})")
                    
                    if "altitude" in line.lower():
                        alt_match = re.search(r'altitude: ([-\d.]+)', line)
                        if alt_match:
                            altitude = alt_match.group(1)
                            print(f"  - Altitude: {altitude} ft")
                    
        except queue.Empty:
            continue
    
    return message_counts

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description="GDL90 Broadcaster Test")
    parser.add_argument("--interface", default="lo", help="Network interface to listen on")
    parser.add_argument("--port", type=int, default=4000, help="UDP port to listen on")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    args = parser.parse_args()
    
    print("=== GDL90 Broadcaster Test ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration:")
    print(f"  - Interface: {args.interface}")
    print(f"  - Port: {args.port}")
    print(f"  - Duration: {args.duration} seconds")
    
    # Start the receiver
    receiver_proc, output_thread = run_receiver(args.interface, args.port)
    
    try:
        # Wait for receiver to initialize
        time.sleep(2)
        
        # Process messages
        message_counts = process_messages(timeout=args.duration)
        
        # Report results
        print("\n=== Test Results ===")
        for msg_type, count in message_counts.items():
            readable_name = {
                "MSG00": "Heartbeat",
                "MSG10": "Ownship Report",
                "MSG0B": "Ownship Geo Altitude",
                "MSG14": "Traffic Report"
            }.get(msg_type, msg_type)
            
            print(f"{readable_name} messages: {count}")
        
        # Overall status
        if message_counts["MSG00"] > 0 and message_counts["MSG10"] > 0:
            print("\nTEST PASSED: Required message types received")
        else:
            print("\nTEST FAILED: Missing required message types")
            
    finally:
        # Cleanup
        print("\nCleaning up...")
        receiver_proc.terminate()
        
        # Wait for process to terminate
        receiver_proc.wait(timeout=5)
        
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
```

## Usage Instructions

1. Make sure the Python environment is set up with required dependencies:

```bash
# From the project root directory
cd sample/gdl90-sample/gdl90-master
pip install -r requirements.txt
```

2. Run your GDL90 broadcaster (in a separate terminal):

```bash
# Start your broadcaster (command depends on your implementation)
python3 main.py --gdl90 --spoof-gps
```

3. Run the test script:

```bash
# From the project root directory
python3 docs/plans/gdl90_testing/gdl90_test_receiver.py --interface=lo --port=4000 --duration=60
```

## Command Line Options

- `--interface`: Network interface to listen on (default: "lo" for loopback)
- `--port`: UDP port to listen on (default: 4000)
- `--duration`: Test duration in seconds (default: 60)

## Expected Output

If the test is successful, you should see output similar to:

```
=== GDL90 Broadcaster Test ===
Started at: 2025-04-25 14:30:00
Configuration:
  - Interface: lo
  - Port: 4000
  - Duration: 60 seconds
Starting receiver: python3 sample/gdl90-sample/gdl90-master/gdl90_receiver.py --interface=lo --port=4000 --verbose

Listening for messages for 60 seconds...
Tracking message types: MSG00, MSG10, MSG0B, MSG14
Receiver: Listening on interface lo at address 127.0.0.1 on port 4000
Detected Heartbeat message
  - Timestamp: 521345
Detected Ownship Report message
  - Position: (-27.4698, 153.0251)
  - Altitude: 1000 ft
Detected Ownship Geo Altitude message
  - Altitude: 1500 ft
...

=== Test Results ===
Heartbeat messages: 60
Ownship Report messages: 60
Ownship Geo Altitude messages: 60
Traffic Report messages: 0

TEST PASSED: Required message types received

Cleaning up...
Test completed at: 2025-04-25 14:31:00
```

## Troubleshooting

1. **No messages received**: 
   - Ensure the broadcaster and receiver are using the same network interface and port
   - Check if the broadcaster is actually sending messages (check its logs)
   - Verify network permissions (firewall settings)

2. **CRC errors**: 
   - This indicates an issue with message framing or CRC calculation
   - Review the CRC implementation in the broadcaster code
   - Compare with the sample code's CRC calculation

3. **Message fields incorrect**:
   - Check the field encoding in each message type
   - Verify scaling factors and byte order match the GDL90 specification
   - Ensure proper byte stuffing is applied

## Next Steps

- Extend the test script to perform more detailed validation of message contents
- Create automated tests for all key message types
- Integrate with CI/CD pipeline for continuous validation