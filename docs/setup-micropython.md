# MicroPython: Zero to Script Uploaded

- [x] **Install esptool.py and rshell**
```bash
pip3 install esptool rshell
```

## Install prerequisites
- [x] **Download MicroPython firmware**
  - Go to: https://micropython.org/download/ESP32_GENERIC_C6/
  - Download the latest `.bin` file (e.g., `ESP32_GENERIC_C6-20240xxx.bin`)
  - Save to `~/Downloads/`

- [x] **Connect board via USB cable**
  - Plug in the USB data cable
  - Verify it shows up: `ls /dev/cu.usbmodem*`


## Flash firmware
- [x] **Erase existing firmware**
  ```bash
  ~/Library/Python/3.9/bin/esptool.py --chip esp32c6 -p /dev/cu.usbmodem1101 erase_flash
  ```

- [x] **Flash MicroPython**
  ```bash
  ~/Library/Python/3.9/bin/esptool.py --chip esp32c6 -p /dev/cu.usbmodem1101 --baud 460800 write_flash -z 0x0 ~/Downloads/ESP32_GENERIC_C6-*.bin
  ```


## Connect to REPL
- [x] **Open REPL to verify it works**
  ```bash
  rshell -p /dev/cu.usbmodem1101
  > repl
  ```
  - You should see `>>>` prompt
  - Try: `print("Hello from MicroPython!")`
  - Exit REPL with `Ctrl+X`, then `exit` rshell


## Scripts
- [ ] **Create a test script locally**
  - Create file `main.py` with your code (e.g., blink LED)

- [ ] **Upload script to board using rshell**
  ```bash
  rshell -p /dev/cu.usbmodem1101
  > cp main.py /pyboard/
  > exit
  ```

## Test persistence
- [ ] **Reboot board and verify script runs**
  - Unplug/replug USB, or in REPL: `import machine; machine.reset()`
  - Monitor serial to see output: `/opt/homebrew/bin/arduino-cli monitor -p /dev/cu.usbmodem1101 --config baudrate=115200`

**Done!** Script is now running on the board.
