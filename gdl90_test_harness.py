#!/usr/bin/env python3
"""
GDL90 Test Harness: Run broadcaster (with sample traffic) and receiver together for integration testing.

Usage:
    python3 gdl90_test_harness.py [--location surfers_paradise] [--port 4000] [--interface eth0] [--distance 5.0] [--verbose]
"""

import argparse
import subprocess
import threading
import signal
import sys
import os

def stream_output(proc, prefix, color):
    try:
        for line in iter(proc.stdout.readline, b''):
            if not line:
                break
            sys.stdout.write(f"{color}{prefix}{line.decode(errors='replace')}\033[0m")
            sys.stdout.flush()
    except Exception as e:
        sys.stderr.write(f"\033[91m[HARNESS ERROR] {prefix} output error: {e}\033[0m\n")

def run_process(cmd, prefix, color):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1
    )
    t = threading.Thread(target=stream_output, args=(proc, prefix, color), daemon=True)
    t.start()
    return proc, t

def main():
    parser = argparse.ArgumentParser(description="Run GDL90 broadcaster and receiver together for integration testing.")
    parser.add_argument('--location', default='surfers_paradise', help='Location JSON file (without .json)')
    parser.add_argument('--port', type=int, default=4000, help='UDP port for communication')
    parser.add_argument('--interface', default='eth0', help='Network interface for receiver')
    parser.add_argument('--distance', type=float, default=5.0, help='Sample traffic pattern distance (NM)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    # Colors
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'

    # Broadcaster command
    broadcaster_cmd = [
        "python3", "gdl90_broadcaster.py",
        "--location-file", f"locations/{args.location}.json",
        "--generate-sample-traffic",
        "--sample-traffic-distance", str(args.distance),
        "--udp-port", str(args.port),
        "--udp-broadcast-ip", "255.255.255.255",
        "--serial-port", "/dev/null"
    ]
    if args.verbose:
        broadcaster_cmd.append("--verbose")

    # Receiver command
    receiver_cmd = [
        "python3", "sample/gdl90-sample/gdl90-master/gdl90_receiver.py",
        "--port", str(args.port),
        "--interface", args.interface,
        "--bcast",
        "--verbose"
    ]

    print(f"{BLUE}[HARNESS] Starting broadcaster: {' '.join(broadcaster_cmd)}\033[0m")
    print(f"{GREEN}[HARNESS] Starting receiver: {' '.join(receiver_cmd)}\033[0m")

    broadcaster_proc, broadcaster_thread = run_process(broadcaster_cmd, "[BROADCASTER] ", BLUE)
    receiver_proc, receiver_thread = run_process(receiver_cmd, "[RECEIVER]   ", GREEN)

    def terminate_all(signum, frame):
        print(f"\n{RED}[HARNESS] Terminating processes...\033[0m")
        broadcaster_proc.terminate()
        receiver_proc.terminate()
        try:
            broadcaster_proc.wait(timeout=5)
        except Exception:
            broadcaster_proc.kill()
        try:
            receiver_proc.wait(timeout=5)
        except Exception:
            receiver_proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, terminate_all)
    signal.signal(signal.SIGTERM, terminate_all)

    try:
        while True:
            if broadcaster_proc.poll() is not None:
                print(f"{RED}[HARNESS] Broadcaster exited with code {broadcaster_proc.returncode}\033[0m")
                break
            if receiver_proc.poll() is not None:
                print(f"{RED}[HARNESS] Receiver exited with code {receiver_proc.returncode}\033[0m")
                break
            threading.Event().wait(0.2)
    finally:
        terminate_all(None, None)

if __name__ == "__main__":
    main()