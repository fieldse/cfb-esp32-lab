# FireBeetle 2 ESP32-C6 Commands Cheatsheet

**Board:** DFRobot FireBeetle 2 ESP32-C6
**Port:** `/dev/cu.usbmodem1101`
**Arduino CLI:** `/opt/homebrew/bin/arduino-cli`

---

## Compile a Sketch

```bash
/opt/homebrew/bin/arduino-cli compile --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

**Note:** `:CDCOnBoot=cdc` is required for USB Serial debugging to work.

---

## Upload a Sketch

```bash
/opt/homebrew/bin/arduino-cli upload -p /dev/cu.usbmodem1101 --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

---

## Compile + Upload (One Command)

```bash
/opt/homebrew/bin/arduino-cli compile --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path> && \
/opt/homebrew/bin/arduino-cli upload -p /dev/cu.usbmodem1101 --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

---

## Monitor Serial Output

```bash
/opt/homebrew/bin/arduino-cli monitor -p /dev/cu.usbmodem1101 --config baudrate=115200
```

Press `Ctrl+C` to exit.

---

## List Available Ports

```bash
/opt/homebrew/bin/arduino-cli board list
```

---

## Install a Library

```bash
/opt/homebrew/bin/arduino-cli lib install "Library Name"
```

Example:
```bash
/opt/homebrew/bin/arduino-cli lib install "U8g2"
```

---

## Create an Alias (Optional)

Add this to your shell config (`.zshrc` or `.bashrc`) to shorten commands:

```bash
alias arduino-cli="/opt/homebrew/bin/arduino-cli"
```

Then use:
```bash
arduino-cli compile --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

---

## Quick Reference: Sketch Paths

- **hello_oled:** `/Users/matt/Documents/SecondBrain/Meetups/codingfrombeach/03-mar-2026/sketches/hello_oled`

---

## Debugging Tips

- **No serial output?** Make sure your sketch calls `Serial.begin(115200)` and `delay(1500)` at the start of `setup()`
- **Upload fails?** Unplug and replug the USB cable, then try again
- **Serial port not found?** Check `/dev/cu.usbmodem*` — the number may vary
