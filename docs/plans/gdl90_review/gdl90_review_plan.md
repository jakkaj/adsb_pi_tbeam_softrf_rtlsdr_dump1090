# Plan: GDL90 Encoding and Transmission Review

**Objective:** Review the existing GDL90 implementation in `modules/gdl90.py` and `modules/broadcaster.py` against the reference implementation in `sample/gdl90-sample/gdl90-master` and the GDL90 specification principles. Correct identified discrepancies, particularly in CRC calculation and message field encoding, to ensure compliance and proper transmission.

**Phases:**

**Phase 1: Correct Core GDL90 Encoding**
*   **Task 1.1: Replace Fletcher-16 CRC with CRC-16-CCITT.**
    *   **Action:** Adapt the CRC-16-CCITT implementation (lookup table and `crcCompute` function) from `sample/gdl90-sample/gdl90-master/gdl90/fcs.py` into `modules/gdl90.py`. Replace calls to the old `calculate_crc` with calls to the new CRC function. Ensure the CRC bytes are appended in the correct order (LSB, then MSB).
    *   **Success Criteria:** The `frame_message` function in `modules/gdl90.py` correctly calculates and appends the CRC-16-CCITT checksum for various test payloads.
    *   **Status:** - [ ]
*   **Task 1.2: Correct Heartbeat Timestamp Encoding.**
    *   **Action:** Modify the `create_heartbeat_message` function in `modules/gdl90.py` to encode the timestamp as per the sample/spec: pack the lower 16 bits as little-endian, and place the 17th bit (if applicable) into the MSB of Status Byte 2. Adjust the packing logic accordingly.
    *   **Success Criteria:** The generated Heartbeat message bytes match the expected format for the timestamp field based on the sample/spec.
    *   **Status:** - [ ]
*   **Task 1.3: Verify Other Field Encodings.**
    *   **Action:** Review the encoding functions (`encode_lat_lon`, `encode_altitude_pressure`, `encode_velocity`, etc.) in `modules/gdl90.py`. Compare their output byte sequences for sample inputs against the logic in the sample's `encoder.py` and `messages.py` (specifically the parsing logic which reveals expected formats). Pay attention to scaling factors, offsets, signed/unsigned representation, and byte order. Make minor corrections if discrepancies are found. This task covers general fields used across multiple messages.
    *   **Success Criteria:** Encoding functions produce byte sequences consistent with the GDL90 specification principles and the sample implementation for standard message types (Ownship, Geo Alt).
    *   **Status:** - [ ]
*   **Task 1.4: Explicitly Verify Traffic Report Encoding.**
    *   **Action:** Specifically review the `create_traffic_report` function in `modules/gdl90.py`. Compare the packing and encoding of each field (Status/Type, Address, Lat/Lon, Altitude, Misc, NIC/NACp, HVelocity/VVelocity, Track, EmitterCat, Callsign, Code) against the sample's `_msgType10and20` encoding logic and the parsing logic in `messages.py`. Ensure correct bit allocation, scaling, and handling of special values (e.g., invalid velocity).
    *   **Success Criteria:** The `create_traffic_report` function correctly encodes all fields according to the GDL90 specification and consistent with the sample implementation.
    *   **Status:** - [ ]

**Phase 2: Testing and Validation**
*   **Task 2.1: Enhance Encoding Test Cases.**
    *   **Action:** Add or modify test cases within the `if __name__ == '__main__':` block of `modules/gdl90.py`. These tests should generate messages with known inputs and assert that the resulting framed hex output matches pre-calculated known-good GDL90 frames (potentially derived by running the sample encoder or using spec examples). Include tests covering the corrected CRC, timestamp, and specific Traffic Report fields.
    *   **Success Criteria:** All test cases in `modules/gdl90.py` pass, validating the encoding logic against known-good outputs.
    *   **Status:** - [ ]
*   **Task 2.2: Validate Broadcast Output.**
    *   **Action:** Run the main application (`adsb_pi_thing`) with the corrected code. Use a GDL90 receiver tool (e.g., `netcat -ul <port>`, Wireshark with GDL90 dissector, or potentially the sample's `gdl90_receiver.py`) to capture the UDP broadcast packets on the configured port (e.g., 4000). Verify that the received packets are well-formed GDL90 messages and that the data fields (position, altitude, traffic) appear reasonable.
    *   **Success Criteria:** Broadcast UDP packets are valid GDL90 frames, decodable by standard tools, and contain plausible data based on the input sources or spoofing settings.
    *   **Status:** - [ ]

**Phase 3: Memory Graph Update**
*   **Task 3.1: Create/Update SourceFile Entities.**
    *   **Action:** Use the `memory` MCP tool to ensure `SourceFile` entities exist for `modules/gdl90.py` and `modules/broadcaster.py`. Add observations about their primary purpose (GDL90 encoding/framing, GDL90 broadcasting/state management).
    *   **Success Criteria:** `SourceFile` entities for the relevant files exist in the memory graph with accurate descriptions.
    *   **Status:** - [ ]
*   **Task 3.2: Add Observations about Corrections.**
    *   **Action:** Add observations to the `modules/gdl90.py` entity detailing the correction of the CRC algorithm (Fletcher-16 to CRC-16-CCITT), the Heartbeat timestamp encoding, and any specific Traffic Report field corrections.
    *   **Success Criteria:** Observations reflecting the specific encoding corrections are added to the `modules/gdl90.py` entity.
    *   **Status:** - [ ]
*   **Task 3.3: Create Plan Entity.**
    *   **Action:** Create a `Plan` entity in the memory graph named `gdl90_review_plan` with observations describing its objective.
    *   **Success Criteria:** A `Plan` entity for this task exists in the memory graph.
    *   **Status:** - [ ]
*   **Task 3.4: Create and Link FileChange Entities.**
    *   **Action:** For the changes made in Phase 1 (Tasks 1.1, 1.2, 1.3, 1.4), create `FileChange` entities (e.g., `Correct GDL90 CRC`, `Fix Heartbeat Timestamp`, `Verify Traffic Report Fields`). Link these changes to the `gdl90_review_plan` entity and the `modules/gdl90.py` `SourceFile` entity using appropriate relations (`implements`, `modifies`, `partOf`).
    *   **Success Criteria:** `FileChange` entities representing the core corrections are created and correctly linked in the memory graph.
    *   **Status:** - [ ]

**Overall Success Criteria:**
*   The GDL90 output from `modules/broadcaster.py` uses the correct CRC-16-CCITT checksum.
*   The Heartbeat message timestamp is encoded according to the GDL90 standard.
*   Other standard GDL90 message fields, including those in the Traffic Report, are encoded correctly.
*   The broadcast output is verifiable using standard GDL90 decoding tools.
*   The memory graph is updated to reflect the plan and the changes made.

**Checklist:**
- [x] Task 1.1: Replace Fletcher-16 CRC with CRC-16-CCITT.
- [x] Task 1.2: Correct Heartbeat Timestamp Encoding.
- [x] Task 1.3: Verify Other Field Encodings.
- [x] Task 1.4: Explicitly Verify Traffic Report Encoding.
- [ ] Task 2.1: Enhance Encoding Test Cases.
- [ ] Task 2.2: Validate Broadcast Output.
- [ ] Task 3.1: Create/Update SourceFile Entities.
- [ ] Task 3.2: Add Observations about Corrections.
- [ ] Task 3.3: Create Plan Entity.
- [ ] Task 3.4: Create and Link FileChange Entities.