# Debug Output Control Plan

## Objective
Standardize and control all debug and verbose output in the project. All debug output (e.g., "FLARM Raw ...", "Sample Traffic ...", etc.) must be:
- Emitted via the Python `logging` module (not `print`)
- Only shown if a CLI switch (e.g., `--debug` or `--verbose`) is set

## Phase 1: Audit and Planning

### Task 1.1: Identify All Debug/Verbose Output
- [ ] List all scripts/modules with debug or verbose print statements (e.g., "FLARM Raw", "Sample Traffic", etc.)
- [ ] Confirm which outputs are for debugging and which are user-facing

### Task 1.2: Define Logging and CLI Switch Standard
- [ ] Specify logging setup (format, default level, etc.)
- [x] Define CLI switch name and behavior (e.g., `--debug` sets logging to DEBUG)

#### Logging and CLI Switch Standard

- All debug and verbose output must use the Python `logging` module, not `print`.
- Standard log format: `%(asctime)s %(levelname)s: %(message)s`
- Default logging level: `WARNING` (or `INFO` for user-facing scripts).
- Add a CLI switch `--debug` (or `-d`) to each main script.
    - If `--debug` is set, logging level is `DEBUG`.
    - If not set, logging level remains at default.
- All debug output must use `logging.debug`. User-facing info should use `logging.info` or `logging.error` as appropriate.
- Example setup:
    ```python
    import logging
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s: %(message)s"
    )
    ```

## Phase 2: Implementation

### Task 2.1: Refactor Scripts to Use Logging
- [ ] Add logging setup to each script if not present
- [ ] Replace debug/verbose print statements with `logging.debug` or `logging.info`
- [ ] Ensure user-facing output (errors, critical info) uses `logging.error` or `logging.info` as appropriate

### Task 2.2: Add CLI Switch for Debug/Verbose Output
- [ ] Add CLI argument (e.g., `--debug` or `--verbose`) to each main script
- [ ] Set logging level based on CLI switch

### Task 2.3: Test Debug Output Control
- [ ] Run each script with and without the debug switch to verify output is correctly controlled

## Phase 3: Documentation and Cleanup

### Task 3.1: Update Documentation
- [ ] Document the new debug/verbose switch in README or script docstrings

### Task 3.2: Remove Obsolete Print Statements
- [ ] Remove any remaining print statements used for debugging

---

## Checklist

- [ ] Task 1.1: All debug/verbose print statements identified
- [x] Task 1.2: Logging and CLI switch standard defined
- [ ] Task 2.1: All scripts refactored to use logging
- [ ] Task 2.2: CLI switch added to all main scripts
- [ ] Task 2.3: Debug output control tested in all scripts
- [ ] Task 3.1: Documentation updated
- [ ] Task 3.2: Obsolete print statements removed

---

## Success Criteria

- All debug output is routed through the logging module.
- Debug output is only shown when the CLI switch is set.
- No stray print statements remain for debug output.
- Documentation clearly explains how to enable debug output.