# Makefile for GDL90 Broadcaster

# Default Python interpreter
PYTHON = python3

# Default serial port (can be overridden)
SERIAL_PORT ?= /dev/ttyAMA4
SERIAL_BAUD ?= 38400

# Default Dump1090 connection details (can be overridden)
DUMP1090_HOST ?= 127.0.0.1
DUMP1090_PORT ?= 30002

# Default UDP output details (can be overridden)
UDP_PORT ?= 4000
UDP_BROADCAST_IP ?= 255.255.255.255

# Main script
SCRIPT = gdl90_broadcaster.py

# Phony targets (not actual files)
.PHONY: help run run-spoof run-spoof-location run-spoof-location-brisbane run-tester run-receiver list-ports install-deps clean test

help:
	@echo "Makefile for GDL90 Broadcaster"
	@echo ""
	@echo "Usage:"
	@echo "  make install-deps         Install required Python packages with pip (pyserial, pyModeS)"
	@echo "  make install-system-deps  Install required packages system-wide (for Debian/Ubuntu)"
	@echo "  make list-ports           List available serial ports"
	@echo "  make run            Run the broadcaster with default settings (Serial: ${SERIAL_PORT})"
	@echo "  make run-spoof      Run the broadcaster with GPS spoofing enabled (for testing)"
	@echo "  make run-spoof-location LOCATION=surfers_paradise  Run with location-specific GPS spoofing"
	@echo "  make run PORT=/dev/ttyUSB0  Run with a specific serial port"
	@echo "  make run-tester     Run the GDL90 message tester/decoder (listens on UDP ${UDP_PORT})"
	@echo "  make run-receiver   Run the GDL90 receiver to listen for messages (on UDP ${UDP_PORT})"
	@echo "  make test           Run unit tests for the GDL90 modules"
	@echo "  make clean          Remove temporary Python files"
	@echo ""
	@echo "Default Settings (can be overridden):"
	@echo "  SERIAL_PORT      = ${SERIAL_PORT}"
	@echo "  SERIAL_BAUD      = ${SERIAL_BAUD}"
	@echo "  DUMP1090_HOST    = ${DUMP1090_HOST}"
	@echo "  DUMP1090_PORT    = ${DUMP1090_PORT}"
	@echo "  UDP_PORT         = ${UDP_PORT}"
	@echo "  UDP_BROADCAST_IP = ${UDP_BROADCAST_IP}"
	@echo ""

install-deps:
	@echo "Installing dependencies..."
	$(PYTHON) -m pip install pyserial pyModeS

install-system-deps:
	@echo "Installing system dependencies using apt..."
	sudo apt-get update
	sudo apt-get install -y python3-serial python3-pip
	@echo "Note: pyModeS isn't available as a system package, installing with pip..."
	sudo pip3 install pyModeS --break-system-packages

list-ports:
	@echo "Listing available serial ports..."
	$(PYTHON) $(SCRIPT) --list-ports

run:
	@echo "Starting GDL90 Broadcaster..."
	@echo "  Serial Port: ${SERIAL_PORT}"
	@echo "  Baud Rate:   ${SERIAL_BAUD}"
	@echo "  Dump1090:    ${DUMP1090_HOST}:${DUMP1090_PORT}"
	@echo "  UDP Output:  ${UDP_BROADCAST_IP}:${UDP_PORT}"
	$(PYTHON) $(SCRIPT) \
		--serial-port ${SERIAL_PORT} \
		--serial-baud ${SERIAL_BAUD} \
		--dump1090-host ${DUMP1090_HOST} \
		--dump1090-port ${DUMP1090_PORT} \
		--udp-port ${UDP_PORT} \
		--udp-broadcast-ip ${UDP_BROADCAST_IP}

run-spoof:
	@echo "Starting GDL90 Broadcaster with GPS spoofing..."
	@echo "  Serial Port: ${SERIAL_PORT}"
	@echo "  Baud Rate:   ${SERIAL_BAUD}"
	@echo "  Dump1090:    ${DUMP1090_HOST}:${DUMP1090_PORT}"
	@echo "  UDP Output:  ${UDP_BROADCAST_IP}:${UDP_PORT}"
	@echo "  Interface:   eth0 (Note: requires sudo for interface binding)"
	$(PYTHON) $(SCRIPT) \
		--serial-port ${SERIAL_PORT} \
		--serial-baud ${SERIAL_BAUD} \
		--dump1090-host ${DUMP1090_HOST} \
		--dump1090-port ${DUMP1090_PORT} \
		--udp-port ${UDP_PORT} \
		--udp-broadcast-ip ${UDP_BROADCAST_IP} \
		  eth0 \
		--spoof-gps

# Default location if not specified
LOCATION ?= brisbane

run-spoof-location:
	@echo "Starting GDL90 Broadcaster with GPS location spoofing..."
	@echo "  Serial Port: ${SERIAL_PORT}"
	@echo "  Baud Rate:   ${SERIAL_BAUD}"
	@echo "  Dump1090:    ${DUMP1090_HOST}:${DUMP1090_PORT}"
	@echo "  UDP Output:  ${UDP_BROADCAST_IP}:${UDP_PORT}"
	@echo "  Interface:   eth0 (Note: requires sudo for interface binding)"
	@echo "  Location:    ${LOCATION}"
	$(PYTHON) $(SCRIPT) \
		--serial-port ${SERIAL_PORT} \
		--serial-baud ${SERIAL_BAUD} \
		--dump1090-host ${DUMP1090_HOST} \
		--dump1090-port ${DUMP1090_PORT} \
		--udp-port ${UDP_PORT} \
		--udp-broadcast-ip ${UDP_BROADCAST_IP} \
		--interface eth0 \
		--location-file locations/${LOCATION}.json

# Specific location targets for convenience
run-spoof-location-file:
	@$(MAKE) run-spoof-location LOCATION=gold_coast_airport

run-tester:
	@echo "Starting GDL90 Tester (listening on UDP port ${UDP_PORT})..."
	$(PYTHON) gdl90_tester.py --port ${UDP_PORT} --bind-address 0.0.0.0

run-receiver:
	@echo "Starting GDL90 Receiver (listening on UDP port ${UDP_PORT})..."
	$(PYTHON) sample/gdl90-sample/gdl90-master/gdl90_receiver.py --port ${UDP_PORT} --interface eth0 --bcast --verbose

clean:
	@echo "Cleaning up..."
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

1090:
	~/github/dump1090/dump1090 --net --interactive

test:
	@echo "Running GDL90 unit tests..."
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

vscode:
	docker run -it --init -p 8000:3000 -v "$(pwd):/home/workspace" gitpod/openvscode-server
