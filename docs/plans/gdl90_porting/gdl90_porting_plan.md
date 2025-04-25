# GDL90 Encoder Porting Plan

**Objective:** Replace the GDL90 encoding and message assembly logic in `modules/gdl90/` with the logic from `sample/gdl90-sample/gdl90-master/gdl90/encoder.py` and its dependencies, ensuring all tests pass.

## Phase 1: Preparation & Setup

*   **Task 1.1:** Create this plan document at `docs/plans/gdl90_porting/gdl90_porting_plan.md`.
    *   *Success Criteria:* Plan document exists at the specified path.
*   **Task 1.2:** Add this plan as a 'Plan' entity to the memory knowledge graph.
    *   *Success Criteria:* Plan entity created in memory graph with link to the plan file.
*   **Task 1.3:** (Optional but Recommended) Create a source control branch for this work.
    *   *Success Criteria:* A new branch (e.g., `feature/gdl90-porting`) is created.

## Phase 2: Port Encoder Logic to `modules/gdl90/encoders.py`

*   **Task 2.1:** Add helper functions (`_pack24bit`, `_makeLatitude`, `_makeLongitude`) from the target `sample/.../encoder.py` to `modules/gdl90/encoders.py`.
    *   *Success Criteria:* Helper functions are present and correctly implemented in `encoders.py`.
*   **Task 2.2:** Replace `encode_lat_lon` implementation with logic using the new helper functions, matching the target's calculation (integer truncation).
    *   *Success Criteria:* `encode_lat_lon` uses the new helpers and matches target logic.
*   **Task 2.3:** Replace `encode_altitude_pressure` implementation with the target's calculation and packing logic (extracted from `_msgType10and20`).
    *   *Success Criteria:* `encode_altitude_pressure` matches target logic.
*   **Task 2.4:** Replace `encode_altitude_geometric` implementation with the target's calculation and packing logic (extracted from `msgOwnshipGeometricAltitude`). Verify GDL90 spec regarding the 1000ft offset.
    *   *Success Criteria:* `encode_altitude_geometric` matches target logic and spec.
*   **Task 2.5:** Replace `encode_velocity` (horizontal) implementation with the target's calculation and packing logic (extracted from `_msgType10and20`).
    *   *Success Criteria:* `encode_velocity` matches target logic.
*   **Task 2.6:** Replace `encode_vertical_velocity` implementation with the target's calculation and packing logic (extracted from `_msgType10and20`).
    *   *Success Criteria:* `encode_vertical_velocity` matches target logic.
*   **Task 2.7:** Replace `encode_track_heading` implementation with the target's calculation logic (extracted from `_msgType10and20`).
    *   *Success Criteria:* `encode_track_heading` matches target logic.
*   **Task 2.8:** Update `encode_icao_address` implementation to use `_pack24bit`, ensuring it handles input appropriately (likely keep hex string input and convert internally).
    *   *Success Criteria:* `encode_icao_address` uses `_pack24bit` and handles input correctly.
*   **Task 2.9:** Update `encode_callsign` implementation to match the target's logic.
    *   *Success Criteria:* `encode_callsign` matches target logic.
*   **Task 2.10:** Update `tests/test_gdl90_encoders.py` to reflect the new encoding logic and expected outputs based on the target implementation.
    *   *Success Criteria:* All tests in `tests/test_gdl90_encoders.py` pass.

## Phase 3: Port Message Assembly Logic to `modules/gdl90/messages.py`

*   **Task 3.1:** Read the current contents of `modules/gdl90/messages.py` (if it exists and has relevant content).
    *   *Success Criteria:* Understanding of any existing message assembly logic.
*   **Task 3.2:** Implement functions in `modules/gdl90/messages.py` (e.g., `assemble_heartbeat`, `assemble_ownship_report`, `assemble_traffic_report`, `assemble_ownship_geom_alt`, etc.) that replicate the message payload assembly logic from the target `sample/.../encoder.py`'s `msg*` methods. These functions should use the updated encoders from `modules/gdl90/encoders.py`.
    *   *Success Criteria:* Functions exist in `messages.py` that correctly assemble the raw payloads for required GDL90 messages using the updated encoders.
*   **Task 3.3:** Create a new test file `tests/test_gdl90_messages.py`.
    *   *Success Criteria:* Test file exists.
*   **Task 3.4:** Add tests to `tests/test_gdl90_messages.py` to verify the raw payload output of the message assembly functions (before CRC/framing). Use known good examples from the spec or target implementation.
    *   *Success Criteria:* Comprehensive tests for message assembly functions are added.
*   **Task 3.5:** Ensure all tests in `tests/test_gdl90_messages.py` pass.
    *   *Success Criteria:* `make test` (or equivalent) shows passing tests for `test_gdl90_messages.py`.

## Phase 4: Integration Testing & Finalization

*   **Task 4.1:** Add integration tests (e.g., in `tests/test_gdl90_integration.py` or similar) that use `modules/gdl90/messages.py` to generate payloads and `modules/gdl90/framing.py` to create complete, framed messages. Verify the final byte output against known good full GDL90 frames.
    *   *Success Criteria:* Integration tests covering the full process from data input to framed message output exist and pass.
*   **Task 4.2:** Run all project tests (`make test` or equivalent command).
    *   *Success Criteria:* All project tests pass without errors.
*   **Task 4.3:** Update this plan document, marking all tasks as complete (`- [x]`).
    *   *Success Criteria:* All checklist items in the plan document are marked as complete.
*   **Task 4.4:** Update the status of the corresponding Plan entity in the memory graph to 'Completed'.
    *   *Success Criteria:* Memory graph entity reflects the completed status.
*   **Task 4.5:** Create `FileChange` entities in the memory graph for `modules/gdl90/encoders.py`, `modules/gdl90/messages.py`, `tests/test_gdl90_encoders.py`, and `tests/test_gdl90_messages.py`, linking them to this plan entity.
    *   *Success Criteria:* Memory graph accurately reflects the files changed as part of this plan.

## Overall Success Criteria

*   The GDL90 encoding and message assembly logic in `modules/gdl90/` accurately reflects the logic from the target `sample/gdl90-sample/gdl90-master/gdl90/` implementation.
*   All relevant unit tests (`test_gdl90_encoders.py`, `test_gdl90_messages.py`) pass.
*   Integration tests verifying complete framed messages pass.
*   The overall project test suite passes.
*   The plan document and memory graph are updated to reflect completion.

---

## Checklist

**Phase 1: Preparation & Setup**
- [ ] Task 1.1: Create plan document.
- [ ] Task 1.2: Add plan entity to memory.
- [ ] Task 1.3: Create source control branch.

**Phase 2: Port Encoder Logic**
- [ ] Task 2.1: Add helper functions to `encoders.py`.
- [ ] Task 2.2: Update `encode_lat_lon`.
- [ ] Task 2.3: Update `encode_altitude_pressure`.
- [ ] Task 2.4: Update `encode_altitude_geometric`.
- [ ] Task 2.5: Update `encode_velocity`.
- [ ] Task 2.6: Update `encode_vertical_velocity`.
- [ ] Task 2.7: Update `encode_track_heading`.
- [ ] Task 2.8: Update `encode_icao_address`.
- [ ] Task 2.9: Update `encode_callsign`.
- [ ] Task 2.10: Update and pass `tests/test_gdl90_encoders.py`.

**Phase 3: Port Message Assembly Logic**
- [ ] Task 3.1: Read `modules/gdl90/messages.py`.
- [ ] Task 3.2: Implement message assembly functions in `messages.py`.
- [ ] Task 3.3: Create `tests/test_gdl90_messages.py`.
- [ ] Task 3.4: Add tests for message assembly.
- [ ] Task 3.5: Pass tests in `tests/test_gdl90_messages.py`.

**Phase 4: Integration Testing & Finalization**
- [ ] Task 4.1: Add and pass integration tests for full frames.
- [ ] Task 4.2: Pass all project tests.
- [ ] Task 4.3: Update plan document checklist.
- [ ] Task 4.4: Update plan entity status in memory.
- [ ] Task 4.5: Create `FileChange` entities in memory.