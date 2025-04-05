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
.PHONY: help run list-ports install-deps clean

help:
	@echo "Makefile for GDL90 Broadcaster"
	@echo ""
	@echo "Usage:"
	@echo "  make install-deps   Install required Python packages (pyserial, pyModeS)"
	@echo "  make list-ports     List available serial ports"
	@echo "  make run            Run the broadcaster with default settings (Serial: ${SERIAL_PORT})"
	@echo "  make run PORT=/dev/ttyUSB0  Run with a specific serial port"
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

clean:
	@echo "Cleaning up..."
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +