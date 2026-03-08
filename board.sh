#!/bin/bash

# MicroPython convenience script for the FireBeetle 2 ESP32-C6
# Handles flashing firmware, uploading scripts, and REPL access

# ============================================================================
# Configuration Constants
# ============================================================================

VENV_BIN="./venv/bin"
RSHELL="$VENV_BIN/rshell"
ESPTOOL="$VENV_BIN/esptool.py"
MPREMOTE="$VENV_BIN/mpremote"
PORT="/dev/cu.usbmodem1101"
CHIP="esp32c6"
BAUD="460800"
FIRMWARE_DIR="./firmware"

# Check if venv exists and source it
if [ ! -d "./venv" ]; then
  echo "[-] virtualenv not found at ./venv"
  echo "[!] Create it with: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# Activate venv
source ./venv/bin/activate

# ============================================================================
# Helper Functions
# ============================================================================

# Print usage information
function usage() {
  echo "MicroPython board tools for FireBeetle 2 ESP32-C6"
  echo ""
  echo "Usage: $0 [command] [options]"
  echo ""
  echo "Commands:"
  echo "  test               Test board connectivity and get chip info"
  echo "  flash              Flash MicroPython firmware to board"
  echo "  upload <file>      Upload a Python script to board (e.g., main.py)"
  echo "  repl               Open interactive MicroPython REPL"
  echo "  serial             Watch serial output (no interaction)"
  echo "  upload-env         Upload .env to board (required for WiFi scripts)"
  echo "  reset              Reset the board"
  echo ""
  echo "Examples:"
  echo "  $0 test"
  echo "  $0 flash"
  echo "  $0 upload scripts/main.py"
  echo "  $0 repl"
  echo "  $0 reset"
}

# ============================================================================
# Commands
# ============================================================================

# Flash MicroPython firmware onto the board
# Erases existing flash and writes new MicroPython binary
function flash() {
  echo "[+] Looking for MicroPython firmware in $FIRMWARE_DIR..."

  FIRMWARE=$(ls -t "$FIRMWARE_DIR"/ESP32_GENERIC_C6*.bin 2>/dev/null | head -1)

  if [ -z "$FIRMWARE" ]; then
    echo "[-] No ESP32_GENERIC_C6 firmware found in $FIRMWARE_DIR"
    echo "[!] Download from: https://micropython.org/download/ESP32_GENERIC_C6/"
    return 1
  fi

  echo "[+] Found: $(basename "$FIRMWARE")"
  echo "[+] Erasing flash..."
  "$ESPTOOL" --chip "$CHIP" -p "$PORT" erase_flash || return 1

  echo "[+] Flashing MicroPython..."
  "$ESPTOOL" --chip "$CHIP" -p "$PORT" --baud "$BAUD" write_flash -z 0x0 "$FIRMWARE" || return 1

  echo "[+] Flash complete!"
  echo "[!] Board will reboot. Wait a moment, then run: $0 repl"
}

# Upload a Python script to the board
# Defaults to uploading as main.py (runs automatically on boot)
# Args: $1 = local filename (e.g., scripts/hello_count.py)
#       --name <name>  optional destination filename (default: main.py)
function upload() {
  local file="$1"
  local dest="main.py"
  shift

  # Parse optional --name flag
  while [[ "$#" -gt 0 ]]; do
    case "$1" in
      --name) dest="$2"; shift 2 ;;
      *) echo "[-] Unknown option: $1"; return 1 ;;
    esac
  done

  if [ -z "$file" ]; then
    echo "[-] Usage: $0 upload <filename> [--name <dest>]"
    echo "Example: $0 upload scripts/hello_count.py"
    echo "Example: $0 upload scripts/button_press.py --name button_press.py"
    return 1
  fi

  if [ ! -f "$file" ]; then
    echo "[-] File not found: $file"
    return 1
  fi

  echo "[+] Uploading $file to board as $dest..."

  (echo "cp $file /pyboard/$dest"; sleep 0.5; echo "exit") | "$RSHELL" -p "$PORT"

  if [ $? -eq 0 ]; then
    echo "[+] Upload complete!"
    reset
  else
    echo "[-] Upload failed"
    return 1
  fi
}

# Open interactive MicroPython REPL
# Access the Python prompt for live testing and debugging
function repl() {
  echo "[+] Opening MicroPython REPL (Ctrl+X to exit)"
  echo ""
  "$RSHELL" -p "$PORT"
  echo ""
  echo "[+] REPL closed"
}

# Monitor serial output without interaction
# Useful for watching a script run
function connect_serial() {
  echo "[+] Monitoring serial output (Ctrl+C to exit)..."
  echo ""
  # Use rshell's built-in serial monitoring or fall back to arduino-cli
  /opt/homebrew/bin/arduino-cli monitor -p "$PORT" --config baudrate=115200
}

# Test board connectivity and get chip information
# Non-destructive check to verify board is connected and responding
function test() {
  echo "[+] Testing board connectivity on $PORT..."
  echo ""

  # Check if port exists
  if [ ! -e "$PORT" ]; then
    echo "[-] Port $PORT not found"
    echo "[!] Check connection or try: ls /dev/cu.usbmodem*"
    return 1
  fi

  echo "[+] Port exists"

  # Get chip ID and info with esptool
  echo "[+] Reading chip info..."
  "$ESPTOOL" --chip "$CHIP" -p "$PORT" chip_id

  if [ $? -eq 0 ]; then
    echo ""
    echo "[+] Board is connected and responding!"
    return 0
  else
    echo ""
    echo "[-] Failed to read chip info"
    return 1
  fi
}

# Upload the .env file to the board's filesystem
# Required for scripts that read WiFi credentials or other config
function upload_env() {
  local env_file=".env"

  if [ ! -f "$env_file" ]; then
    echo "[-] No .env file found in current directory"
    return 1
  fi

  echo "[+] Uploading .env to board..."
  (echo "cp $env_file /pyboard/.env"; sleep 0.5; echo "exit") | "$RSHELL" -p "$PORT"

  if [ $? -eq 0 ]; then
    echo "[+] .env uploaded"
  else
    echo "[-] Failed to upload .env"
    return 1
  fi
}

# Reset the board via MicroPython
# Equivalent to unplugging and replugging the board
function reset() {
  echo "[+] Resetting board..."
  "$MPREMOTE" connect "$PORT" reset + disconnect
  echo "[+] Board reset"
}

# ============================================================================
# Main
# ============================================================================

case "$1" in
  test)     test ;;
  flash)    flash ;;
  upload)   shift; upload "$@" ;;
  repl)     repl ;;
  serial)   connect_serial ;;
  upload-env) upload_env ;;
  reset)    reset ;;
  *)        usage ;;
esac
