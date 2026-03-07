#!/bin/bash
# Convenience script for compiling, uploading sketches, and connecting to serial TTY
# with the arduino-cli toolkit

ARDUINO=/opt/homebrew/bin/arduino-cli
FQBN="esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc"
PORT="/dev/cu.usbmodem1101"
SKETCHES_DIR="$(dirname "$0")/sketches"

usage() {
  echo "Usage: $0 [--compile <sketch>] [--upload <sketch>] [--monitor]"
  echo ""
  echo "  --compile <sketch>   Compile a sketch (e.g. hello_oled)"
  echo "  --upload <sketch>    Compile and upload a sketch"
  echo "  --monitor            Open serial monitor at 115200 baud"
  echo ""
  echo "Available sketches:"
  for d in "$SKETCHES_DIR"/*/; do echo "  $(basename "$d")"; done
}

compile() {
  local sketch="$SKETCHES_DIR/$1"
  if [ ! -d "$sketch" ]; then
    echo "[error] sketch '$1' not found in $SKETCHES_DIR"
    exit 1
  fi
  echo "[+] Compiling $1..."
  "$ARDUINO" compile --fqbn "$FQBN" "$sketch"
  if [ $? -eq 0 ]; then echo "[+] compile OK"; else echo "[-] compilation failed"; fi
}

upload() {
  local sketch="$SKETCHES_DIR/$1"
  if [ ! -d "$sketch" ]; then
    echo "[error] sketch '$1' not found in $SKETCHES_DIR"
    exit 1
  fi
  echo "[+] Compiling $1..."
  "$ARDUINO" compile --fqbn "$FQBN" "$sketch" || exit 1
  echo "[+] Uploading $1..."
  "$ARDUINO" upload -p "$PORT" --fqbn "$FQBN" "$sketch"
  if [ $? -eq 0 ]; then echo "[+] upload OK"; else echo "[-] upload failed"; fi
}

monitor() {
  echo "[+] Opening serial monitor on $PORT (Ctrl+C to exit)..."
  "$ARDUINO" monitor -p "$PORT" --config baudrate=115200
  echo "[+] serial connection closed"
}

case "$1" in
  --compile) shift; compile "$1" ;;
  --upload)  shift; upload "$1" ;;
  --monitor) monitor ;;
  *) usage ;;
esac
