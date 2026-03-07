# FireBeetle 2 ESP32-C6 Commands Cheatsheet

**Board:** DFRobot FireBeetle 2 ESP32-C6
**Port:** `/dev/cu.usbmodem1101`
**Arduino CLI:** `/opt/homebrew/bin/arduino-cli`

---

## Device Commands

### Monitor Serial Output

```bash
/opt/homebrew/bin/arduino-cli monitor -p /dev/cu.usbmodem1101 --config baudrate=115200
```

Press `Ctrl+C` to exit.

### List Available Ports

```bash
/opt/homebrew/bin/arduino-cli board list
```

### Check which device is connected

```bash
ls /dev/cu.*
```

The board should appear as `/dev/cu.usbmodem*` (number may vary).

---

## Arduino-cli

### Compile a Sketch

```bash
/opt/homebrew/bin/arduino-cli compile --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

**Note:** `:CDCOnBoot=cdc` is required for USB Serial debugging to work.

### Upload a Sketch

```bash
/opt/homebrew/bin/arduino-cli upload -p /dev/cu.usbmodem1101 --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

### Compile + Upload (One Command)

```bash
/opt/homebrew/bin/arduino-cli compile --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path> && \
/opt/homebrew/bin/arduino-cli upload -p /dev/cu.usbmodem1101 --fqbn esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc <sketch_path>
```

### Install a Library

```bash
/opt/homebrew/bin/arduino-cli lib install "Library Name"
```

Example:
```bash
/opt/homebrew/bin/arduino-cli lib install "U8g2"
```

### Using the board.sh Script

Instead of typing long commands, use the provided helper script:

```bash
# Compile only
./board.sh --compile hello_oled

# Compile + upload
./board.sh --upload button_press

# Serial monitor
./board.sh --monitor
```

### Debugging Tips for Arduino

- **No serial output?** Make sure your sketch calls `Serial.begin(115200)` and `delay(1500)` at the start of `setup()`
- **Upload fails?** Unplug and replug the USB cable, then try again
- **Serial port not found?** Check `/dev/cu.usbmodem*` — the number may vary

---

## MicroPython

MicroPython is an alternative to Arduino for programming the ESP32-C6. It uses Python instead of C/C++ and offers faster iteration through an interactive REPL.

### Download MicroPython Firmware

The ESP32-C6 uses RISC-V architecture, so you **must** use the `ESP32_GENERIC_C6` firmware, not the generic ESP32 firmware.

Download from: https://micropython.org/download/ESP32_GENERIC_C6/

### Flash MicroPython onto the Board

First, install `esptool`:

```bash
pip install esptool
```

Then erase the existing firmware and flash MicroPython:

```bash
esptool.py --chip esp32c6 -p /dev/cu.usbmodem1101 erase_flash

esptool.py --chip esp32c6 -p /dev/cu.usbmodem1101 --baud 460800 write_flash -z 0x0 ~/Downloads/ESP32_GENERIC_C6-xxx.bin
```

(Replace `xxx` with the version number of the file you downloaded)

### Access the MicroPython REPL

Once flashed, open a serial terminal at 115200 baud:

```bash
/opt/homebrew/bin/arduino-cli monitor -p /dev/cu.usbmodem1101 --config baudrate=115200
```

Press Enter a few times — you should see the `>>>` prompt. You can now type Python commands directly!

Example:
```python
>>> from machine import Pin
>>> led = Pin(15, Pin.OUT)
>>> led.on()   # turn LED on
>>> led.off()  # turn LED off
```

### Create a MicroPython Script

Create a file called `main.py` on the board's filesystem. The simplest way:

1. Open the REPL
2. Create the file with `open()`:

```python
>>> code = """
... from machine import Pin
... led = Pin(15, Pin.OUT)
... while True:
...     led.on()
...     print("LED on")
...     led.off()
...     print("LED off")
... """
>>> with open("main.py", "w") as f:
...     f.write(code)
>>>
```

Or use an editor like [Thonny](https://thonny.org/) for a better experience.

### Upload a Script to MicroPython

Use `rshell` (remote shell):

```bash
pip install rshell
```

Then:
```bash
rshell -p /dev/cu.usbmodem1101
```

Inside rshell:
```
> cp main.py /pyboard/
> repl
```

### Reboot the Board

In the REPL:
```python
>>> import machine
>>> machine.reset()
```

The board will restart and run `main.py` automatically.

### Common MicroPython Snippets

**Blink LED:**
```python
from machine import Pin
import time

led = Pin(15, Pin.OUT)

while True:
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)
```

**Read Button:**
```python
from machine import Pin

button = Pin(9, Pin.IN, Pin.PULL_UP)

while True:
    if not button.value():  # button pressed (active LOW)
        print("Button pressed!")
        time.sleep(0.2)  # debounce
```

**WiFi Connection:**
```python
from network import WLAN, STA_IF
import time

wlan = WLAN(STA_IF)
wlan.active(True)
wlan.connect("cfb", "cfb_1958!")

while not wlan.isconnected():
    time.sleep(0.1)

print("Connected!")
print(wlan.ifconfig())
```

### Switching Back to Arduino

If you want to go back to Arduino after using MicroPython, simply upload an Arduino sketch using `arduino-cli upload`. It will overwrite the MicroPython firmware.

### More Resources

- MicroPython Quick Reference: https://docs.micropython.org/en/latest/esp32/quickref.html
- MicroPython REPL Tutorial: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html
- Thonny IDE (easier than REPL): https://thonny.org/
