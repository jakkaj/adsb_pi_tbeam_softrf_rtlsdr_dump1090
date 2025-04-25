# GDL90 Broadcaster Testing Plan

## Objective
Use the reference Python implementation in `sample/gdl90-sample/gdl90-master` to test and validate our GDL90 broadcaster, ensuring correct message encoding, framing, and transmission.

## Background
Our project implements a GDL90 broadcaster that sends aircraft position and traffic information over UDP. The GDL90 protocol is used in aviation for ADS-B data exchange. We want to ensure our implementation correctly encodes and transmits GDL90 messages according to the specification.

The sample code provides tools for:
- Receiving and decoding GDL90 messages (`gdl90_receiver.py`)
- Recording GDL90 messages to a file (`gdl90_recorder.py`)
- Sending recorded GDL90 data (`gdl90_sender.py`)

## Testing Phases

### Phase 1: Environment Setup

**Task 1.1: Configure Sample Code Environment**
- Create a Python virtual environment for the sample code
- Install required dependencies
- Verify the sample code can run

**Task 1.2: Configure Network Settings**
- Determine the network interface and port our broadcaster uses
- Configure the sample receiver to listen on the same interface/port
- Ensure firewall rules permit local UDP traffic

### Phase 2: Basic Reception Test

**Task 2.1: Start GDL90 Broadcaster**
- Run our GDL90 broadcaster with debugging enabled
- Use GPS spoofing option to generate predictable message content
- Monitor console output to verify transmission

**Task 2.2: Run Sample Receiver**
- Run the sample `gdl90_receiver.py` to listen for GDL90 messages
- Configure it to display received messages
- Verify messages are being received and decoded

```bash
# Example command to run the receiver
python3 sample/gdl90-sample/gdl90-master/gdl90_receiver.py --interface=lo --port=4000 --verbose
```

### Phase 3: Message Validation

**Task 3.1: Heartbeat Message Validation**
- Verify Heartbeat messages (ID 0x00) are received
- Confirm timestamp field is correctly encoded
- Check status flags match our broadcaster's settings

**Task 3.2: Ownship Report Validation**
- Verify Ownship Report messages (ID 0x0A) are received
- Confirm position data (lat/lon) matches our broadcaster's settings
- Validate altitude encoding

**Task 3.3: Traffic Report Validation**
- Generate traffic data for our broadcaster to transmit
- Verify Traffic Report messages (ID 0x14) are received
- Confirm all fields (position, altitude, callsign, etc.) are correctly encoded

### Phase 4: Automated Testing

**Task 4.1: Create Test Script**
- Develop a Python script that automates the testing process
- Script should:
  - Start our broadcaster
  - Run the sample receiver
  - Validate received messages
  - Generate a test report

**Task 4.2: Extended Testing**
- Run the automated test with various configurations
- Test edge cases:
  - Invalid position data
  - Extreme altitude values
  - Special characters in callsigns
  - Missing fields

### Phase 5: Performance Testing

**Task 5.1: Message Throughput Test**
- Simulate high traffic conditions with many aircraft
- Measure message throughput
- Check for any dropped or malformed messages

**Task 5.2: Long-Duration Test**
- Run the broadcaster and receiver for an extended period
- Monitor for any degradation in performance
- Validate continuous reception of all expected message types

## Success Criteria
- Sample receiver successfully decodes all message types from our broadcaster
- Message content matches expected values
- No CRC errors or malformed messages are detected
- Performance remains stable over extended operation

## Testing Checklist
- [x] **Phase 1: Environment Setup**
  - [x] Task 1.1: Configure Sample Code Environment
  - [x] Task 1.2: Configure Network Settings
- [ ] **Phase 2: Basic Reception Test**
  - [ ] Task 2.1: Start GDL90 Broadcaster
  - [ ] Task 2.2: Run Sample Receiver
- [ ] **Phase 3: Message Validation**
  - [ ] Task 3.1: Heartbeat Message Validation
  - [ ] Task 3.2: Ownship Report Validation
  - [ ] Task 3.3: Traffic Report Validation
- [ ] **Phase 4: Automated Testing**
  - [ ] Task 4.1: Create Test Script
  - [ ] Task 4.2: Extended Testing
- [ ] **Phase 5: Performance Testing**
  - [ ] Task 5.1: Message Throughput Test
  - [ ] Task 5.2: Long-Duration Test

## Test Script Implementation

Below is a starting template for the automated test script:

```python
#!/usr/bin/env python3

import subprocess
import time
import threading
import queue
import re
import sys
import os

# Queue for receiver output
receiver_output = queue.Queue()

def run_broadcaster(spoof_gps=True):
    """Start the GDL90 broadcaster with GPS spoofing enabled"""
    cmd = ["python3", "main.py", "--gdl90", "--spoof-gps"]
    print(f"Starting broadcaster: {' '.join(cmd)}")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def capture_receiver_output(proc):
    """Capture and process output from the sample receiver"""
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        line_str = line.decode('utf-8').strip()
        receiver_output.put(line_str)
        print(f"Receiver: {line_str}")

def run_receiver():
    """Start the sample GDL90 receiver"""
    receiver_cmd = [
        "python3", 
        "sample/gdl90-sample/gdl90-master/gdl90_receiver.py",
        "--interface=lo",  # Adjust based on your setup
        "--port=4000",     # Adjust to match broadcaster port
        "--verbose"
    ]
    print(f"Starting receiver: {' '.join(receiver_cmd)}")
    receiver_proc = subprocess.Popen(receiver_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # Start thread to capture output
    output_thread = threading.Thread(target=capture_receiver_output, args=(receiver_proc,))
    output_thread.daemon = True
    output_thread.start()
    
    return receiver_proc, output_thread

def validate_messages(timeout=30):
    """Validate received messages"""
    start_time = time.time()
    
    # Message type counters
    message_counts = {
        "Heartbeat": 0,
        "Ownship": 0,
        "Traffic": 0
    }
    
    while time.time() - start_time < timeout:
        try:
            line = receiver_output.get(timeout=1)
            
            # Check for message types
            if "MSG00" in line:  # Heartbeat
                message_counts["Heartbeat"] += 1
                print("Detected Heartbeat message")
                
            elif "MSG10" in line:  # Ownship
                message_counts["Ownship"] += 1
                print("Detected Ownship Report message")
                
            elif "MSG20" in line:  # Traffic
                message_counts["Traffic"] += 1
                print("Detected Traffic Report message")
                
        except queue.Empty:
            continue
    
    return message_counts

def main():
    """Main test function"""
    print("=== GDL90 Broadcaster Test ===")
    
    # Start the broadcaster
    broadcaster_proc = run_broadcaster()
    time.sleep(5)  # Allow time to initialize
    
    # Start the receiver
    receiver_proc, output_thread = run_receiver()
    
    try:
        # Validate messages for 30 seconds
        print("\nValidating messages for 30 seconds...")
        message_counts = validate_messages(timeout=30)
        
        # Report results
        print("\n=== Test Results ===")
        print(f"Heartbeat messages: {message_counts['Heartbeat']}")
        print(f"Ownship Report messages: {message_counts['Ownship']}")
        print(f"Traffic Report messages: {message_counts['Traffic']}")
        
        if message_counts['Heartbeat'] > 0 and message_counts['Ownship'] > 0:
            print("TEST PASSED: Required message types received")
        else:
            print("TEST FAILED: Missing required message types")
            
    finally:
        # Cleanup
        print("\nCleaning up...")
        receiver_proc.terminate()
        broadcaster_proc.terminate()
        
        # Wait for processes to terminate
        receiver_proc.wait(timeout=5)
        broadcaster_proc.wait(timeout=5)
        
        print("Test completed")

if __name__ == "__main__":
    main()
```

This script will need to be adjusted based on your specific project structure and requirements.