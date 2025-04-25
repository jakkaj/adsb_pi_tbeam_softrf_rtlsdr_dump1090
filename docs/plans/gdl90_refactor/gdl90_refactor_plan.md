# Plan: Refactor GDL90 Module and Tests

**Goal:** Split the large `modules/gdl90.py` file into smaller, logically grouped modules within a new `modules/gdl90/` package. Extract embedded tests into a separate `tests/` directory structure, following Python unit testing best practices. Ensure all tests pass and are runnable via a new `make test` command.

**Proposed New Structure:**

```
.
├── Makefile
├── gdl90_broadcaster.py
├── gdl90_tester.py
├── modules/
│   ├── __init__.py
│   ├── adsb_client.py
│   ├── broadcaster.py
│   ├── flarm_client.py
│   └── gdl90/             <-- New Package
│       ├── __init__.py    <-- Makes it a package, potentially re-exports
│       ├── constants.py   <-- GDL90 constants (IDs, framing bytes)
│       ├── crc.py         <-- CRC calculation logic
│       ├── encoders.py    <-- encode_* helper functions
│       ├── framing.py     <-- byte_stuff, frame_message
│       └── messages.py    <-- create_*_message functions
├── tests/                 <-- New Directory
│   ├── __init__.py        <-- Makes it a package
│   ├── test_gdl90_crc.py
│   ├── test_gdl90_encoders.py
│   ├── test_gdl90_framing.py
│   └── test_gdl90_messages.py
├── docs/
│   └── plans/
│       └── gdl90_refactor/  <-- New directory for this plan
│           └── gdl90_refactor_plan.md <-- This plan document
... (other files)
```

**Mermaid Diagram (Structure):**

```mermaid
graph TD
    A[adsb_pi_thing] --> B(modules);
    A --> C(tests);
    A --> D(Makefile);
    A --> E(gdl90_broadcaster.py);
    A --> F(gdl90_tester.py);
    A --> G(docs);

    B --> H(gdl90);
    B --> I(adsb_client.py);
    B --> J(broadcaster.py);
    B --> K(flarm_client.py);

    H --> L(__init__.py);
    H --> M(constants.py);
    H --> N(crc.py);
    H --> O(encoders.py);
    H --> P(framing.py);
    H --> Q(messages.py);

    C --> R(__init__.py);
    C --> S(test_gdl90_crc.py);
    C --> T(test_gdl90_encoders.py);
    C --> U(test_gdl90_framing.py);
    C --> V(test_gdl90_messages.py);

    Q --> M;
    Q --> O;
    Q --> P;
    P --> N;
    P --> M;

    S --> N;
    T --> O;
    U --> P;
    V --> Q;

    E --> H;
    F --> H; % Assuming tester might use parts for decoding/constants later
```

**Phases and Tasks:**

**Phase 1: Setup New Structure**
*   **Task 1.1:** Create the new directory `modules/gdl90/`.
    *   *Success Criteria:* Directory `modules/gdl90/` exists.
*   **Task 1.2:** Create `modules/gdl90/__init__.py`.
    *   *Success Criteria:* File `modules/gdl90/__init__.py` exists.
*   **Task 1.3:** Create the new directory `tests/`.
    *   *Success Criteria:* Directory `tests/` exists.
*   **Task 1.4:** Create `tests/__init__.py`.
    *   *Success Criteria:* File `tests/__init__.py` exists.
*   **Task 1.5:** Create empty test files: `tests/test_gdl90_crc.py`, `tests/test_gdl90_encoders.py`, `tests/test_gdl90_framing.py`, `tests/test_gdl90_messages.py`.
    *   *Success Criteria:* All four test files exist in the `tests/` directory.

**Phase 2: Migrate Code**
*   **Task 2.1:** Move GDL90 constants from `modules/gdl90.py` to `modules/gdl90/constants.py`.
    *   *Success Criteria:* Constants are defined in `constants.py` and removed from the original file. Imports updated where necessary (initially just within the old `gdl90.py`).
*   **Task 2.2:** Move CRC logic (`CRC16Table`, `calculate_crc`) from `modules/gdl90.py` to `modules/gdl90/crc.py`. Update imports.
    *   *Success Criteria:* CRC logic is in `crc.py`, removed from original, imports updated.
*   **Task 2.3:** Move framing logic (`byte_stuff`, `frame_message`) from `modules/gdl90.py` to `modules/gdl90/framing.py`. Update imports (will need `constants` and `crc`).
    *   *Success Criteria:* Framing logic is in `framing.py`, removed from original, imports updated.
*   **Task 2.4:** Move `encode_*` helper functions from `modules/gdl90.py` to `modules/gdl90/encoders.py`. Update imports (may need `struct`).
    *   *Success Criteria:* Encoder functions are in `encoders.py`, removed from original, imports updated.
*   **Task 2.5:** Move `create_*_message` functions from `modules/gdl90.py` to `modules/gdl90/messages.py`. Update imports (will need `constants`, `encoders`, `framing`, `datetime`, `struct`).
    *   *Success Criteria:* Message creation functions are in `messages.py`, removed from original, imports updated.
*   **Task 2.6:** Update `modules/gdl90/__init__.py` to potentially re-export key functions/classes for easier access (e.g., `from .messages import create_heartbeat_message`). This simplifies imports for external users like `gdl90_broadcaster.py`.
    *   *Success Criteria:* `__init__.py` contains appropriate exports.
*   **Task 2.7:** Update `gdl90_broadcaster.py` and `gdl90_tester.py` (and any other files identified) to import from the new `modules.gdl90` package structure (e.g., `from modules.gdl90 import create_heartbeat_message` or `from modules.gdl90.messages import create_heartbeat_message`).
    *   *Success Criteria:* All external usages of the old `gdl90.py` module now correctly import from the new package structure.
*   **Task 2.8:** Delete the original (now empty) `modules/gdl90.py` file.
    *   *Success Criteria:* `modules/gdl90.py` no longer exists.

**Phase 3: Migrate and Refine Tests**
*   **Task 3.1:** Move relevant test methods from `TestGDL90Encoding` in the old `modules/gdl90.py` to the appropriate new test files in `tests/`.
    *   `test_byte_stuffing` -> `tests/test_gdl90_framing.py` (needs adaptation for `framing.py` functions).
    *   Tests related to `calculate_crc` (if any implicitly exist within other tests) -> `tests/test_gdl90_crc.py`.
    *   Tests related to `encode_*` functions (e.g., `test_longitude_encoding_fix`, parts of `test_invalid_values`) -> `tests/test_gdl90_encoders.py`.
    *   Tests for full message creation (`test_heartbeat`, `test_ownship_report`, `test_ownship_geo_altitude`, `test_traffic_report`) -> `tests/test_gdl90_messages.py`.
    *   *Success Criteria:* All test logic from the original file is moved to the corresponding new test files. The `TestGDL90Encoding` class is removed from the original file before deletion.
*   **Task 3.2:** Update imports within the new test files to reflect the new `modules.gdl90` structure.
    *   *Success Criteria:* All test files use correct imports (e.g., `from modules.gdl90.crc import calculate_crc`).
*   **Task 3.3:** Ensure each test file uses standard `unittest` structure (import `unittest`, define `unittest.TestCase` subclasses).
    *   *Success Criteria:* Test files adhere to `unittest` conventions.
*   **Task 3.4:** Add a `test` target to the `Makefile` using `python3 -m unittest discover -s tests -p 'test_*.py'`.
    *   *Success Criteria:* `Makefile` contains a working `test` target.
*   **Task 3.5:** Run `make test` and fix any failing tests.
    *   *Success Criteria:* `make test` executes successfully and all tests pass.

**Phase 4: Memory Update**
*   **Task 4.1:** Update the memory graph to reflect the new file structure and relationships.
    *   Delete the old `modules/gdl90.py` entity.
    *   Create entities for the new files (`modules/gdl90/constants.py`, `crc.py`, etc., and the test files).
    *   Add observations about their purpose.
    *   Create relationships (e.g., `messages.py` uses `encoders.py`, `test_gdl90_crc.py` tests `crc.py`).
    *   Create a `Plan` entity for this refactoring effort.
    *   Create `FileChange` entities linked to this plan and the modified/created files.
    *   *Success Criteria:* Memory graph accurately represents the new code structure and the refactoring plan.

**Checklist:**

*   **Phase 1: Setup New Structure**
    *   `- [ ]` Task 1.1: Create `modules/gdl90/` directory.
    *   `- [ ]` Task 1.2: Create `modules/gdl90/__init__.py`.
    *   `- [ ]` Task 1.3: Create `tests/` directory.
    *   `- [ ]` Task 1.4: Create `tests/__init__.py`.
    *   `- [ ]` Task 1.5: Create empty test files.
*   **Phase 2: Migrate Code**
    *   `- [ ]` Task 2.1: Move constants to `constants.py`.
    *   `- [ ]` Task 2.2: Move CRC logic to `crc.py`.
    *   `- [ ]` Task 2.3: Move framing logic to `framing.py`.
    *   `- [ ]` Task 2.4: Move encoders to `encoders.py`.
    *   `- [ ]` Task 2.5: Move message creators to `messages.py`.
    *   `- [ ]` Task 2.6: Update `modules/gdl90/__init__.py` exports.
    *   `- [ ]` Task 2.7: Update external imports (`gdl90_broadcaster.py`, etc.).
    *   `- [ ]` Task 2.8: Delete old `modules/gdl90.py`.
*   **Phase 3: Migrate and Refine Tests**
    *   `- [ ]` Task 3.1: Move test methods to new files.
    *   `- [ ]` Task 3.2: Update test imports.
    *   `- [ ]` Task 3.3: Ensure standard `unittest` structure.
    *   `- [ ]` Task 3.4: Add `test` target to `Makefile`.
    *   `- [ ]` Task 3.5: Run `make test` and ensure all pass.
*   **Phase 4: Memory Update**
    *   `- [ ]` Task 4.1: Update memory graph entities and relations.

**Overall Success Criteria:**

*   The `modules/gdl90.py` file no longer exists.
*   Code is logically organized within the `modules/gdl90/` package.
*   All unit tests are located within the `tests/` directory structure.
*   The command `make test` successfully executes all unit tests, and all tests pass.
*   The `gdl90_broadcaster.py` and `gdl90_tester.py` scripts function correctly using the new module structure (verified by existing `make run*` targets if applicable, though explicit testing of those is outside the scope of *this specific* refactoring task).
*   The memory knowledge graph is updated to reflect the changes.