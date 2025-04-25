# GDL90 Testing Diagrams and Visual References

This document provides visual diagrams to complement the GDL90 broadcaster testing plan.

## Overall Testing Architecture

```mermaid
graph TB
    subgraph "Our Implementation"
        A[Main Application] --> B[Broadcaster Module]
        B -->|Creates| C[GDL90 Messages]
        C -->|Encoded by| D[modules/gdl90.py]
        D -->|Frames with| E[CRC-16-CCITT]
        E -->|Sent via| F[UDP Socket]
    end
    
    F -->|Port 4000| G[Network Interface]
    
    subgraph "Sample Code Test"
        G -->|Receives on Port 4000| H[gdl90_receiver.py]
        H -->|Passes to| I[decoder.py]
        I -->|Validates| J[Frame Structure]
        I -->|Checks| K[CRC-16-CCITT]
        I -->|Decodes| L[Message Content]
        L -->|Reports| M[Console Output]
    end
    
    M -->|Analyzed by| N[Test Script]
    N -->|Validates| O[Message Types]
    N -->|Validates| P[Message Content]
    N -->|Generates| Q[Test Report]
```

## Message Flow Sequence

```mermaid
sequenceDiagram
    participant App as Main Application
    participant Broadcaster as Broadcaster Module
    participant GDL90 as modules/gdl90.py
    participant Network as UDP Socket
    participant Receiver as Sample gdl90_receiver.py
    participant Decoder as Sample decoder.py
    participant Test as Test Script
    
    App->>Broadcaster: Start broadcaster
    activate Broadcaster
    
    loop Every 1 second
        Broadcaster->>GDL90: Request Heartbeat message
        GDL90->>GDL90: Create message payload
        GDL90->>GDL90: Calculate CRC-16-CCITT
        GDL90->>GDL90: Frame message
        GDL90-->>Broadcaster: Return framed message
        Broadcaster->>Network: Send UDP packet
        Network-->>Receiver: Receive UDP packet
        Receiver->>Decoder: Process bytes
        Decoder->>Decoder: Extract message
        Decoder->>Decoder: Validate CRC
        Decoder->>Decoder: Decode message fields
        Decoder-->>Receiver: Return decoded message
        Receiver-->>Test: Output message details
        Test->>Test: Validate message type
        Test->>Test: Validate message content
    end
    
    loop Every 1 second
        Broadcaster->>GDL90: Request Ownship Report
        GDL90->>GDL90: Create message payload
        GDL90->>GDL90: Calculate CRC-16-CCITT
        GDL90->>GDL90: Frame message
        GDL90-->>Broadcaster: Return framed message
        Broadcaster->>Network: Send UDP packet
        Network-->>Receiver: Receive UDP packet
        Receiver->>Decoder: Process bytes
        Decoder->>Decoder: Extract message
        Decoder->>Decoder: Validate CRC
        Decoder->>Decoder: Decode message fields
        Decoder-->>Receiver: Return decoded message
        Receiver-->>Test: Output message details
        Test->>Test: Validate message type
        Test->>Test: Validate message content
    end
    
    Broadcaster->>GDL90: Request other messages (Traffic, etc)
    GDL90-->>Broadcaster: Return framed messages
    Broadcaster->>Network: Send UDP packets
    Network-->>Receiver: Receive UDP packets
    
    Test->>Test: Compile message statistics
    Test->>Test: Generate test report
    
    deactivate Broadcaster
```

## Test Execution Workflow

```mermaid
graph TD
    A[Start] --> B[Configure Test Environment]
    B --> C[Start Our GDL90 Broadcaster]
    C --> D[Run Sample Receiver with Test Script]
    D --> E{Messages Received?}
    
    E -->|Yes| F[Record Message Stats]
    E -->|No| G[Troubleshoot]
    
    G --> H[Check Network Settings]
    H --> I[Verify Port Numbers]
    I --> J[Check Broadcaster Logs]
    J --> C
    
    F --> K{CRC Valid?}
    K -->|Yes| L[Validate Message Content]
    K -->|No| M[Fix CRC Implementation]
    M --> C
    
    L --> N{Content Correct?}
    N -->|Yes| O[Record Success]
    N -->|No| P[Fix Message Encoding]
    P --> C
    
    O --> Q[Generate Test Report]
    Q --> R[End]
```

## Message Structure Reference

Below is a reference diagram for the key GDL90 message types being tested:

### Heartbeat Message (ID: 0x00)

```
+----------------+----------------+----------------+----------------+----------------+
| Message ID     | Status Byte 1  | Status Byte 2  | Timestamp LSB  | Timestamp MSB  |
|    (0x00)      |                |                |                |                |
+----------------+----------------+----------------+----------------+----------------+
```

### Ownship Report (ID: 0x0A)

```
+------+------+------+------+------+------+------+------+------+------+------+------+------+------+------+------+
| ID   | Latitude (3 bytes)  | Longitude (3 bytes) | Altitude (2)| Misc | NIC/ | Velocity (2)| Vert Vel (2)| Track|
|(0x0A)|                     |                     |             |      | NAC  |             |             |      |
+------+------+------+------+------+------+------+------+------+------+------+------+------+------+------+------+
```

### Ownship Geo Altitude (ID: 0x0B)

```
+----------------+----------------+----------------+----------------+----------------+
| Message ID     | Geo Altitude   | Geo Altitude   | Vertical Prot  | Vertical Prot  |
|    (0x0B)      | (MSB)          | (LSB)          | Limit (MSB)    | Limit (LSB)    |
+----------------+----------------+----------------+----------------+----------------+
```

### Traffic Report (ID: 0x14)

```
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
| ID|St | ICAO Address (3)   | Latitude (3 bytes)  | Longitude (3 bytes) | Alt  | Misc| NIC/| Vel  | Vert | Track|
|(14)|   |                   |                     |                     | (2)  |     | NAC | (2)  | Vel(2)|      |
+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
|    Emitter     | Callsign (8 bytes - ASCII)                                                     | Code |
|    Category    |                                                                                 |      |
+----------------+----------------+----------------+----------------+----------------+-------------+------+
```

## Test Execution Instructions

### Step 1: Start the Broadcaster

```bash
# In terminal 1
cd /home/jak/adsb_pi_thing
python3 main.py --gdl90 --spoof-gps
```

### Step 2: Run the Sample Receiver

```bash
# In terminal 2
cd /home/jak/adsb_pi_thing
python3 sample/gdl90-sample/gdl90-master/gdl90_receiver.py --interface=lo --port=4000 --verbose
```

### Step 3: Analyze the Results

Watch the output from the sample receiver to ensure proper message decoding. Look for:

1. No CRC errors
2. Properly decoded lat/lon values matching our spoofed values
3. Proper altitude, track, and speed values
4. Correct timestamp values in heartbeat messages