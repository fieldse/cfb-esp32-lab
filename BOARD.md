# BOARD DETAILS

**Board:** DFRobot FireBeetle 2 ESP32-C6 (DFR1075)

[Board documentation](https://wiki.dfrobot.com/dfr1075/)

---

## Chip

| Item | Detail |
|------|--------|
| Chip | ESP32-C6FH4 (QFN32), revision v0.2 |
| Architecture | 32-bit RISC-V, single core, 160 MHz |
| Flash | 8 MB (supports up to 16 MB) |
| RAM | 512 KB |
| Crystal | 40 MHz |
| Wi-Fi | Wi-Fi 6, 2.4 GHz 802.11 b/g/n |
| Bluetooth | BLE 5.0, 802.15.4 (Zigbee/Thread) |
| USB | USB-Serial/JTAG (native, no separate UART chip) |

---

## Onboard LED

| Item | Detail |
|------|--------|
| Type | Blue indicator LED |
| GPIO | GPIO15 |
| Logic | Active **HIGH** (HIGH = on, LOW = off) |
| Notes | Connected to the blue LED on the board |

---

## Onboard Button

| Item | Detail |
|------|--------|
| Type | BOOT button (programmable as general GPIO) |
| GPIO | GPIO9 |
| Logic | Active **LOW** (pulled up internally, LOW when pressed) |
| Pull-up | Internal pull-up enabled |

---

## GDI Display Connector (18-pin)

The FireBeetle 2 comes with a dedicated connector for plug-and-play LCD/OLED displays.

| Pin | Signal | GPIO | Notes |
|-----|--------|------|-------|
| 1 | GND | — | Ground |
| 2 | 5V | — | 5V power (regulated to 3.3V for display) |
| 3 | SDA | GPIO5 | I²C data line |
| 4 | SCL | GPIO6 | I²C clock line |
| 5 | D/C | GPIO8 | Data/Command for SPI mode |
| 6 | CS | GPIO7 | Chip Select for SPI mode |
| 7 | CLK | GPIO4 | SPI clock |
| 8 | MOSI | GPIO3 | SPI data out |
| 9 | MISO | GPIO2 | SPI data in |
| 10-18 | (reserved/power) | — | Additional signals for specific displays |

**Common display modes:**
- **I²C:** Uses GPIO5 (SDA) and GPIO6 (SCL) — simplest for small OLEDs
- **SPI:** Uses GPIO7 (CS), GPIO8 (D/C), GPIO4 (CLK), GPIO3 (MOSI), GPIO2 (MISO)

---

## General-Purpose GPIO

| GPIO | Function | Notes |
|------|----------|-------|
| GPIO0–GPIO4 | General I/O + ADC | Can be used for analog input or digital I/O |
| GPIO5, GPIO6 | Reserved for GDI display I²C | Avoid using for other purposes if display is connected |
| GPIO7 | General I/O | Also GDI CS if using SPI displays |
| GPIO8 | General I/O | Also GDI D/C if using SPI displays |
| GPIO9 | BOOT button | Can be programmed as general GPIO |
| GPIO15 | Onboard blue LED | Can be programmed but used for status LED by default |

---

## Power

| Feature | Detail |
|---------|--------|
| Input voltage | 5V (USB) or 3.7V–4.2V (Li-Po battery) |
| USB power | Yes (USB-C) |
| Battery connector | JST 2.0 |
| Charge management | On-board charging circuit |
| Charging LED | Shows charging status |
| Voltage regulator | LDO to 3.3V |

---

## Key Programming Notes

### Arduino CLI
- **FQBN:** `esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc`
- **Board:** DFRobot FireBeetle 2 ESP32-C6
- **Port:** `/dev/cu.usbmodem1101` (may vary; use `arduino-cli board list` to find)
- **Serial:** Use `:CDCOnBoot=cdc` to enable USB serial debugging
- **Baud rate:** 115200

### MicroPython
- **Firmware:** Download `ESP32_GENERIC_C6` (RISC-V, not Xtensa)
- **Do NOT use:** Generic ESP32 firmware — the C6 has a different architecture
- **REPL access:** Use `rshell -p /dev/cu.usbmodem1101` then `repl`

### GPIO Constraints
- **LED (GPIO15):** Active HIGH — `digitalWrite(15, HIGH)` turns on the LED
- **Button (GPIO9):** Active LOW — reads as LOW when pressed (internal pull-up)
- **Display I²C (GPIO5/6):** Reserved if using GDI connector
- **ADC:** GPIO0–GPIO4 support ADC input; use `analogRead()` or MicroPython's `ADC` class

### USB Connection
- **No separate UART chip** — USB-CDC runs natively over USB
- Ensure sketches call `Serial.begin(115200)` + `delay(1500)` at startup
- Append `:CDCOnBoot=cdc` to FQBN in Arduino for reliable serial
- MicroPython: USB CDC is active by default after flashing

---

## Useful References

- [DFRobot Wiki (DFR1075)](https://wiki.dfrobot.com/dfr1075/)
- [ESP32-C6 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf)
- [MicroPython ESP32-C6 Firmware](https://micropython.org/download/ESP32_GENERIC_C6/)
- [Arduino ESP32 Core](https://github.com/espressif/arduino-esp32)
