# Plan to Enable ADS-B Traffic Display in gdl90_tester.py

## Problem

The `gdl90_broadcaster.py` script detects ADS-B messages, but the corresponding traffic is not displayed in the `gdl90_tester.py`.

## Root Cause Analysis

1.  **`gdl90_tester.py`:** Listens correctly on UDP port 4000 and can decode GDL90 Traffic Reports (Message ID 20). It is not filtering messages by default when run via the Makefile.
2.  **`modules/broadcaster.py`:** Receives decoded data from a queue. It attempts to create GDL90 Traffic Reports but only proceeds if the incoming data dictionary contains non-null values for `latitude`, `longitude`, *and* `altitude`.
3.  **`modules/adsb_client.py`:** Connects to dump1090 (port 30002), receives raw ADS-B messages (DF17), and decodes some information using `pyModeS`.
    *   It correctly decodes `altitude`.
    *   It **fails** to decode `latitude` and `longitude` because it lacks the necessary Compact Position Reporting (CPR) decoding logic, which requires processing pairs of odd/even position messages.
    *   As a result, the data placed onto the queue is incomplete (missing `latitude` and `longitude`).
4.  **Conclusion:** The broadcaster doesn't receive complete position data from the ADS-B client, so it never generates the GDL90 Traffic Reports needed by the tester.

## Solution

Modify `modules/adsb_client.py` to correctly implement CPR decoding for ADS-B position messages.

## Detailed Implementation Steps for `modules/adsb_client.py`

1.  **Add State Management:**
    *   In the `AdsbClient.__init__` method, add a dictionary to store CPR state: `self.cpr_data = {}`.
    *   This dictionary will be keyed by aircraft ICAO hex strings.
    *   Each value will be another dictionary storing the last seen odd and even CPR message details: `{'odd': {'ts': timestamp, 'msg': raw_hex_msg}, 'even': {'ts': timestamp, 'msg': raw_hex_msg}}`.

2.  **Process CPR Messages (within `handle_messages`):**
    *   When a DF17 message with Type Code (TC) 9-18 (Airborne Position) is received and passes CRC check:
        *   Extract the ICAO address.
        *   Determine the CPR frame type (odd/even) using `pms.adsb.oe_flag(msg)`.
        *   Get the current timestamp (`ts` from the message tuple).
        *   Update the `self.cpr_data[icao]` entry for the corresponding frame type ('odd' or 'even') with the current timestamp and the raw message hex string (`msg`). Create the ICAO entry if it doesn't exist.

3.  **Attempt Position Calculation:**
    *   After updating the state for the current message, check if *both* 'odd' and 'even' entries exist for this ICAO in `self.cpr_data[icao]`.
    *   If both exist, retrieve the timestamps (`t_odd`, `t_even`) and messages (`msg_odd`, `msg_even`).
    *   Check if the time difference between the odd and even messages is within an acceptable window (e.g., `abs(t_odd - t_even) < 10.0` seconds).
    *   If a valid, recent pair is found:
        *   Calculate the absolute position using `pyModeS.adsb.position(msg_even, msg_odd, t_even, t_odd)`. This function returns `(latitude, longitude)`.
        *   If the calculated position is not None:
            *   Add `latitude` and `longitude` keys to the `aircraft_data` dictionary being prepared for the queue.
            *   Optionally, clear the `self.cpr_data[icao]['odd']` and `self.cpr_data[icao]['even']` entries to prevent recalculating with the same pair until new messages arrive.

4.  **Cleanup:**
    *   Remove the old, incorrect calls to `pms.adsb.position_with_ref(msg, 0, 0)` (lines 83-84 in the original code).
    *   Remove any temporary CPR-related keys added to `aircraft_data` if they are no longer needed (e.g., `cpr_lat_odd`, `raw_msg`, etc., unless `raw_msg` is needed elsewhere).

5.  **Queue Data:**
    *   Ensure the `aircraft_data` dictionary, now potentially containing `latitude`, `longitude`, and `altitude`, is put onto the `data_queue` (lines 102-108).

6.  **Verification (Conceptual):**
    *   Confirm that `modules/broadcaster.py` (lines 102-115) correctly uses the keys `latitude`, `longitude`, and `altitude` when calling `gdl90.create_traffic_report`. (This seems correct already).

## Expected Outcome

After implementing these changes, `adsb_client.py` will provide complete position and altitude data to `broadcaster.py`. The broadcaster will then successfully generate GDL90 Traffic Reports, which will be received and displayed by `gdl90_tester.py`.