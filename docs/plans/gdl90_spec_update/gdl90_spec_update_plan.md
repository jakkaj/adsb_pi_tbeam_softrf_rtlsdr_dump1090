# GDL90 Specification Alignment Plan

**Objective:** Align the GDL90 implementation in `modules/gdl90/` with the correct specification, using the provided sample code in `sample/gdl90-sample/gdl90-master/` as the reference. The process involves updating the unit tests first to reflect the specification, observing the failures, and then fixing the implementation code.

**Reference Implementation:** `sample/gdl90-sample/gdl90-master/` (specifically `simulate_gdl90_unit.py`, `gdl90_receiver.py`, and the `gdl90.encoder` and `gdl90.decoder` modules they use).

**Key Issue Identified:** The `create_traffic_report` function in `modules/gdl90/messages.py` contains duplicated, manual encoding logic instead of using the shared encoder functions from `modules/gdl90/encoders.py`.

**Memory Graph Link:** `GDL90 Spec Alignment Plan`

---

## Phases and Tasks

**Phase 1: Information Gathering & Analysis (Completed)**
*   [`x`] Task 1.1: Search Memory Knowledge Graph
*   [`x`] Task 1.2: Read Sample Sender (`simulate_gdl90_unit.py`)
*   [`x`] Task 1.3: Read Sample Receiver (`gdl90_receiver.py`)
*   [`x`] Task 1.4: List Test Files (`tests/`)
*   [`x`] Task 1.5: Read Test Files (`tests/test_*.py`)
*   [`x`] Task 1.6: Read Current Implementation (`modules/gdl90/__init__.py`, `modules/gdl90/messages.py`)

**Phase 2: Update Unit Tests**
*   [` `] Task 2.1: Define Known-Good Message Payloads
    *   Use the reference `gdl90.encoder` or GDL90 specification to generate known-correct, fully framed byte sequences for Heartbeat, Ownship Report, Ownship Geometric Altitude, and Traffic Report messages.
    *   Include examples with various valid inputs and edge cases.
    *   *Success Criteria:* Documented, known-correct GDL90 message byte strings (hex format) are created.
*   [` `] Task 2.2: Update `tests/test_gdl90_messages.py`
    *   Modify existing tests to remove `print()` and add `assertEqual()` assertions comparing `create_*_message` output against known-good byte sequences from Task 2.1.
    *   Cover valid and invalid inputs.
    *   *Success Criteria:* `tests/test_gdl90_messages.py` contains assertions against known-correct byte sequences. Tests fail initially.
*   [` `] Task 2.3: (Optional) Enhance `tests/test_gdl90_encoders.py`
    *   Add assertions comparing individual encoder outputs against known-correct field byte sequences.
    *   *Success Criteria:* Encoder tests have specific value assertions where feasible.
*   [` `] Task 2.4: (Optional) Enhance `tests/test_gdl90_heartbeat.py`
    *   Modify `test_heartbeat_timestamp_encoding_decoding` to assert against a full known-good heartbeat byte sequence.
    *   *Success Criteria:* Heartbeat test compares against a full known-good message.

**Phase 3: Fix Implementation Code**
*   [` `] Task 3.1: Refactor `create_traffic_report` in `modules/gdl90/messages.py`
    *   Remove duplicated encoding logic.
    *   Replace with calls to shared functions from `modules/gdl90/encoders.py`.
    *   Align invalid input handling with encoders and spec.
    *   *Success Criteria:* `create_traffic_report` uses shared encoders; duplicated logic removed.
*   [` `] Task 3.2: Verify/Implement VPL in `create_ownship_geo_altitude`
    *   Consult spec/reference for correct VPL encoding.
    *   Update function to map input VPL (meters) to GDL90 code, replacing placeholder if needed.
    *   *Success Criteria:* VPL encoding matches the specification.
*   [` `] Task 3.3: Run Tests and Iterate
    *   Run updated unit tests (`make test`).
    *   Debug implementation and tests until all tests pass.
    *   *Success Criteria:* All unit tests in `tests/` pass successfully.

**Phase 4: Final Plan & Handoff (In Progress)**
*   [`x`] Task 4.1: Consolidate Plan
*   [`x`] Task 4.2: Add Plan to Memory Knowledge Graph
*   [`x`] Task 4.3: Present Plan for Approval
*   [`x`] Task 4.4: Write Plan File
*   [` `] Task 4.5: Request Mode Switch

---

## Mermaid Diagram

```mermaid
graph TD
    A[Start: Update GDL90] --> B{Phase 1: Info Gathering};
    B -- Done --> C{Phase 2: Update Tests};
    C --> C1[Task 2.1: Define Known Payloads];
    C --> C2[Task 2.2: Update Message Tests];
    C --> C3[Task 2.3: Enhance Encoder Tests];
    C --> C4[Task 2.4: Enhance Heartbeat Tests];
    C1 & C2 & C3 & C4 --> D{Phase 3: Fix Implementation};
    D --> D1[Task 3.1: Refactor Traffic Report];
    D --> D2[Task 3.2: Verify/Fix VPL];
    D --> D3[Task 3.3: Run Tests & Iterate];
    D1 & D2 & D3 --> E{Phase 4: Final Plan & Handoff};
    E --> E1[Task 4.1: Consolidate Plan (Done)];
    E --> E2[Task 4.2: Add Plan to Memory (Done)];
    E --> E3[Task 4.3: Present Plan (Done)];
    E --> E4[Task 4.4: Write Plan File (Current)];
    E --> E5[Task 4.5: Request Mode Switch];
    E4 & E5 --> F[End Planning];

    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#ccf,stroke:#333,stroke-width:2px
```

---

## Checklist

**Phase 1: Information Gathering & Analysis**
- [x] Task 1.1: Search Memory Knowledge Graph
- [x] Task 1.2: Read Sample Sender (`simulate_gdl90_unit.py`)
- [x] Task 1.3: Read Sample Receiver (`gdl90_receiver.py`)
- [x] Task 1.4: List Test Files (`tests/`)
- [x] Task 1.5: Read Test Files (`tests/test_*.py`)
- [x] Task 1.6: Read Current Implementation (`modules/gdl90/__init__.py`, `modules/gdl90/messages.py`)

**Phase 2: Update Unit Tests**
- [ ] Task 2.1: Define Known-Good Message Payloads
- [ ] Task 2.2: Update `tests/test_gdl90_messages.py`
- [ ] Task 2.3: (Optional) Enhance `tests/test_gdl90_encoders.py`
- [ ] Task 2.4: (Optional) Enhance `tests/test_gdl90_heartbeat.py`

**Phase 3: Fix Implementation Code**
- [ ] Task 3.1: Refactor `create_traffic_report` in `modules/gdl90/messages.py`
- [ ] Task 3.2: Verify/Implement VPL in `create_ownship_geo_altitude`
- [ ] Task 3.3: Run Tests and Iterate

**Phase 4: Final Plan & Handoff**
- [x] Task 4.1: Consolidate Plan
- [x] Task 4.2: Add Plan to Memory Knowledge Graph
- [x] Task 4.3: Present Plan for Approval
- [x] Task 4.4: Write Plan File
- [ ] Task 4.5: Request Mode Switch

---

## Overall Success Criteria
*   The GDL90 implementation in `modules/gdl90/` correctly encodes Heartbeat, Ownship Report, Ownship Geometric Altitude, and Traffic Report messages according to the GDL90 specification, matching the behavior of the reference implementation.
*   All unit tests in `tests/` pass, including tests that assert generated messages against known-correct byte sequences.
*   The duplicated encoding logic in `create_traffic_report` is removed and replaced with calls to shared encoder functions.