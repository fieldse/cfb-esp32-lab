# FireBeetle 2 ESP32-C6 — Reference Guide

A consolidated reference for the DFRobot FireBeetle 2 ESP32-C6 (DFR1075) board and MicroPython development.

---

## Sources

- DFRobot Wiki: https://wiki.dfrobot.com/dfr1075/
- MicroPython ESP32 Quick Reference: https://docs.micropython.org/en/latest/esp32/quickref.html
- MicroPython ESP32 Intro / Flashing: https://docs.micropython.org/en/latest/esp32/tutorial/intro.html
- MicroPython ESP32-C6 Firmware: https://micropython.org/download/ESP32_GENERIC_C6/
- MicroPython WLAN API: https://docs.micropython.org/en/latest/library/network.WLAN.html

---

## 1. Board Overview

The **DFRobot FireBeetle 2 ESP32-C6** (DFR1075) is a compact, low-power IoT development board built around the Espressif ESP32-C6 SoC. It targets smart home and IoT applications with multi-protocol wireless support.

**Key differentiators:**
- Wi-Fi 6 (802.11ax), BLE 5, Zigbee 3.0, Thread 1.3 — all on one chip
- Ultra-low deep sleep current (16–36 µA depending on board version)
- Built-in LiPo battery charging with optional solar panel support (MPPT)
- Dedicated 18-pin GDI display connector for plug-and-play LCD/OLED screens
- USB 2.0 CDC (no separate USB-UART chip — firmware must enable CDC-on-boot for Serial)

---

## 2. Technical Specifications

**Source:** https://wiki.dfrobot.com/dfr1075/#tech_specs

### Processor & Memory

| Parameter       | Value                                |
|-----------------|--------------------------------------|
| CPU             | RISC-V single-core                   |
| Clock speed     | 160 MHz                              |
| SRAM            | 512 KB                               |
| ROM             | 320 KB                               |
| Flash (external)| 4 MB                                 |
| RTC SRAM        | 16 KB                                |
| USB             | USB 2.0 CDC                          |

### Power

| Parameter            | Value                          |
|----------------------|--------------------------------|
| Operating voltage    | 3.3 V                          |
| Type-C input         | 5 V DC                         |
| VCC input            | 5 V DC or solar panel          |
| Max charge current   | 0.5 A                          |
| Deep sleep current   | 16 µA (v1.0) / 36 µA (v1.2)   |
| Operating temp       | -10 °C to 60 °C                |
| Dimensions           | 25.4 × 60 mm (1 × 2.36 in)    |

### Power Management ICs

| Component         | Role                                      |
|-------------------|-------------------------------------------|
| HM6245            | 3.3V LDO regulator (board v1.0)           |
| TPS62A02DRLR      | 3.3V DC-DC converter (board v1.1+)        |
| CN3165            | Solar MPPT power management / LiPo charge |

### Wireless Connectivity

| Protocol        | Standard / Details                                         |
|-----------------|------------------------------------------------------------|
| Wi-Fi           | 802.11 b/g/n/ax (Wi-Fi 6), 2.4 GHz, 20/40 MHz            |
| Bluetooth       | BLE 5, 125 Kbps–2 Mbps, mesh capable                      |
| IEEE 802.15.4   | 2.4 GHz, 250 Kbps — supports Zigbee 3.0 and Thread 1.3    |

### Interfaces & Peripherals

| Interface     | Quantity / Notes                        |
|---------------|-----------------------------------------|
| Digital I/O   | 19 pins                                 |
| PWM (LED)     | 6 channels                              |
| SPI           | 1                                       |
| UART          | 3 (including 1 low-power LP UART)       |
| I2C           | 2 (including 1 low-power LP I2C)        |
| I2S           | 1 (audio)                               |
| ADC           | 12-bit SAR, 7 channels                  |
| DMA           | 3 TX / 3 RX channels                    |
| IR            | 2 TX / 2 RX                             |

---

## 3. GPIO & Pin Reference

**Note:** The board uses ESP32-C6 native GPIO numbering. Board silkscreen labels (D0–D13, A0–A6) map to GPIO numbers as described below. The full schematic PDF is available in the DFRobot wiki Downloads section.

### Known Pin Assignments

| Board Label | GPIO   | Notes                                      |
|-------------|--------|--------------------------------------------|
| D13 / LED   | GPIO15 | Onboard blue LED (active high)             |
| D9 / BOOT   | GPIO9  | BOOT button (also used for boot mode)      |
| —           | GPIO0  | Battery voltage ADC input                  |
| —           | GPIO1  | GDI LCD_CS (chip select)                   |
| D2          | GPIO8  | GDI LCD_DC (data/command)                  |
| D3          | GPIO14 | GDI LCD_RST (display reset)                |
| D7          | GPIO18 | GDI SD_CS (SD card chip select)            |
| D12         | GPIO6  | GDI TCS (touch chip select)                |

### SPI Pins (main SPI bus, shared with GDI connector)

| Function | GPIO |
|----------|------|
| SCK      | 23   |
| MOSI     | 22   |
| MISO     | 21   |

### I2C Pins (GDI connector I2C)

| Function | GPIO |
|----------|------|
| SDA      | 19   |
| SCL      | 20   |

### Power Pins

| Pin  | Function                        |
|------|---------------------------------|
| VIN  | 5V input (Type-C or VCC header) |
| 3V3  | 3.3V regulated output           |
| GND  | Ground                          |

### Entering Bootloader Mode (for flashing)

If the board does not enter bootloader automatically:
1. Press and hold **BOOT** (GPIO9)
2. Press and release **RST**
3. Release **BOOT**
4. Re-run the flash command

---

## 4. MicroPython Support for ESP32-C6

MicroPython officially supports the ESP32-C6 as of v1.24.0. The C6 uses a **RISC-V** core (not Xtensa), so use the dedicated `ESP32_GENERIC_C6` firmware — do not use the generic ESP32 firmware.

**Latest stable release:** v1.27.0 (2025-12-09)
**Firmware filename:** `ESP32_GENERIC_C6-20251209-v1.27.0.bin`
**Download:** https://micropython.org/download/ESP32_GENERIC_C6/

### ESP32-C6 vs Generic ESP32 differences in MicroPython

- Temperature: use `esp32.mcu_temperature()` (returns °C) — not `esp32.raw_temperature()`
- PWM: 6 channels (vs 16 on original ESP32)
- ADC: 7 channels, no DAC
- No capacitive touch pins
- REPL available over USB CDC or UART0

---

## 5. Flashing MicroPython

**Source:** https://micropython.org/download/ESP32_GENERIC_C6/

### Prerequisites

Install `esptool`:
```bash
pip install esptool
```

### Step 1 — Erase flash

```bash
esptool.py --port /dev/cu.usbmodem01 erase_flash
```

Replace `/dev/cu.usbmodem01` with your actual port:
- macOS: `/dev/cu.usbmodem*` or `/dev/cu.usbserial*`
- Linux: `/dev/ttyACM0` or `/dev/ttyUSB0`
- Windows: `COM4` (or similar)

### Step 2 — Flash firmware

```bash
esptool.py --port /dev/cu.usbmodem01 --baud 460800 write_flash 0 ESP32_GENERIC_C6-20251209-v1.27.0.bin
```

If flashing fails midway, remove `--baud 460800` to use the default (slower) speed:
```bash
esptool.py --port /dev/cu.usbmodem01 write_flash 0 ESP32_GENERIC_C6-20251209-v1.27.0.bin
```

### Step 3 — Access the REPL

Connect a serial terminal at **115200 baud** to access the MicroPython REPL:
```bash
# Using mpremote (recommended)
pip install mpremote
mpremote connect /dev/cu.usbmodem01

# Or using screen
screen /dev/cu.usbmodem01 115200
```

Press **Enter** to get the `>>>` prompt. Press **Ctrl+D** to soft-reset.

---

## 6. MicroPython Quick Reference

**Source:** https://docs.micropython.org/en/latest/esp32/quickref.html

### Board Control

```python
import machine, esp32

machine.freq()           # get current CPU frequency
machine.freq(160000000)  # set to 160 MHz (max for C6)

esp32.mcu_temperature()  # CPU temperature in Celsius (C6/C3/S2/S3)
```

### GPIO / Digital Pins

```python
from machine import Pin

# Output
led = Pin(15, Pin.OUT)
led.on()    # high
led.off()   # low
led.value(1)

# Input
btn = Pin(9, Pin.IN, Pin.PULL_UP)
print(btn.value())  # 0 or 1

# Interrupt
def callback(pin):
    print("triggered!", pin)

btn.irq(trigger=Pin.IRQ_FALLING, handler=callback)
```

**Drive strengths:** `DRIVE_0` (5 mA), `DRIVE_1` (10 mA), `DRIVE_2` (20 mA, default), `DRIVE_3` (40 mA)

```python
led = Pin(15, Pin.OUT, drive=Pin.DRIVE_2)
```

### PWM

```python
from machine import Pin, PWM

pwm = PWM(Pin(15), freq=1000, duty_u16=32768)  # 50% duty
pwm.freq(5000)            # change frequency
pwm.duty_u16(65535)       # 100% duty
pwm.duty_u16(0)           # 0% duty (off)
pwm.deinit()              # disable PWM
```

Frequency range: 1 Hz to 40 MHz. ESP32-C6 has **6 PWM channels**.

### ADC (Analog Read)

```python
from machine import ADC, Pin

adc = ADC(Pin(0))                    # GPIO0 = battery voltage pin
adc.atten(ADC.ATTN_11DB)            # full range: ~0–2.45V input
val = adc.read_u16()                 # 0–65535
voltage_uv = adc.read_uv()          # calibrated microvolts
```

Attenuation settings:
| Constant       | Input range     |
|----------------|-----------------|
| `ATTN_0DB`     | 100–950 mV      |
| `ATTN_2_5DB`   | 100–1250 mV     |
| `ATTN_6DB`     | 150–1750 mV     |
| `ATTN_11DB`    | 150–2450 mV     |

> Battery voltage monitoring: GPIO0 is wired to battery via a voltage divider. Read with ADC, then multiply by the divider ratio to get actual battery voltage.

### UART (Serial)

```python
from machine import UART

uart = UART(1, baudrate=9600, tx=10, rx=9)
uart.write('hello\n')
data = uart.read(64)      # read up to 64 bytes
uart.readline()
```

Default UART0 (REPL): tx=GPIO1, rx=GPIO3 — avoid reassigning these.

### I2C

**Hardware I2C (preferred — uses dedicated peripheral):**
```python
from machine import I2C, Pin

i2c = I2C(0, scl=Pin(20), sda=Pin(19), freq=400000)
devices = i2c.scan()        # returns list of I2C addresses
print([hex(d) for d in devices])

# Write to device
i2c.writeto(0x3C, b'\x00\xff')

# Read from device
data = i2c.readfrom(0x3C, 4)

# Write then read (register read pattern)
i2c.writeto(0x3C, b'\x00')          # send register address
data = i2c.readfrom(0x3C, 2)        # read 2 bytes
```

**Software I2C (any pins, slower):**
```python
from machine import SoftI2C, Pin

i2c = SoftI2C(scl=Pin(20), sda=Pin(19), freq=100000)
```

### SPI

**Hardware SPI:**
```python
from machine import SPI, Pin

spi = SPI(1, baudrate=10000000, polarity=0, phase=0,
          sck=Pin(23), mosi=Pin(22), miso=Pin(21))

cs = Pin(1, Pin.OUT)
cs.off()                         # assert CS (active low)
spi.write(b'\x01\x02\x03')
result = spi.read(4)
cs.on()                          # deassert CS
```

**Software SPI (any pins):**
```python
from machine import SoftSPI, Pin

spi = SoftSPI(baudrate=100000, polarity=0, phase=0,
              sck=Pin(23), mosi=Pin(22), miso=Pin(21))
```

### I2S (Audio)

```python
from machine import I2S, Pin

i2s = I2S(0,
          sck=Pin(23), ws=Pin(22), sd=Pin(21),
          mode=I2S.TX,
          bits=16,
          format=I2S.STEREO,
          rate=44100,
          ibuf=20000)
i2s.write(buf)    # write audio buffer
i2s.deinit()
```

### Timers

```python
from machine import Timer

# One-shot timer
t = Timer(1)
t.init(mode=Timer.ONE_SHOT, period=2000, callback=lambda t: print("done"))

# Periodic timer
t.init(mode=Timer.PERIODIC, period=500, callback=lambda t: print("tick"))

t.deinit()  # stop timer
```

> Timer 0 is reserved internally. Use Timer(1) or higher.

### Real-Time Clock (RTC)

```python
from machine import RTC

rtc = RTC()
rtc.datetime((2025, 3, 6, 0, 12, 0, 0, 0))  # set: (year, month, day, weekday, hour, min, sec, ms)
print(rtc.datetime())                         # read current time
```

### Deep Sleep & Wakeup

```python
import machine, esp32
from machine import Pin

# Wake after a timed interval (10 seconds)
machine.deepsleep(10000)

# Check why we woke up
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("woke from deep sleep")

# Wake on pin (e.g. button press)
esp32.wake_on_ext0(pin=Pin(9), level=esp32.WAKEUP_ALL_LOW)
machine.deepsleep()
```

### Watchdog Timer

```python
from machine import WDT

wdt = WDT(timeout=5000)  # 5 second timeout
# Must call wdt.feed() regularly or the board resets
wdt.feed()
```

### NeoPixel / WS2812

```python
from machine import Pin
from neopixel import NeoPixel

np = NeoPixel(Pin(4), 8)   # 8 pixels on GPIO4
np[0] = (255, 0, 0)        # red
np[1] = (0, 255, 0)        # green
np.write()
```

### OneWire / DS18B20 Temperature Sensor

```python
import onewire, ds18x20
from machine import Pin

ow = onewire.OneWire(Pin(4))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
ds.convert_temp()
import time; time.sleep_ms(750)
print(ds.read_temp(roms[0]))
```

### DHT Sensors

```python
import dht
from machine import Pin

d = dht.DHT22(Pin(4))   # or dht.DHT11
d.measure()
print(d.temperature())  # Celsius
print(d.humidity())     # percent
```

---

## 7. WiFi Networking

**Source:** https://docs.micropython.org/en/latest/library/network.WLAN.html

### Connect to a WiFi Network (Station Mode)

```python
import network, time

wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
wlan.connect('your-ssid', 'your-password')

# Wait for connection
while not wlan.isconnected():
    time.sleep(0.5)

print("Connected:", wlan.ifconfig())
# Returns: (IP, netmask, gateway, DNS)
```

### Useful helper function

```python
def connect_wifi(ssid, password, timeout=15):
    import network, time
    wlan = network.WLAN(network.WLAN.IF_STA)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                raise OSError("WiFi timeout")
            time.sleep(0.5)
    ip, mask, gw, dns = wlan.ifconfig()
    print(f"Connected — IP: {ip}")
    return wlan
```

### Workshop WiFi credentials

```python
SSID = 'cfb'
PASSWORD = 'cfb_1958!'
```

### Scan for Networks

```python
import network

wlan = network.WLAN(network.WLAN.IF_STA)
wlan.active(True)
nets = wlan.scan()
# Returns list of: (ssid, bssid, channel, RSSI, security, hidden)
for net in nets:
    print(net[0].decode(), "  RSSI:", net[3])
```

### Access Point Mode

```python
import network

ap = network.WLAN(network.WLAN.IF_AP)
ap.active(True)
ap.config(ssid='FireBeetle-AP', password='12345678', channel=6)
print("AP IP:", ap.ifconfig()[0])
```

### Check Connection Status

```python
wlan.isconnected()           # True if has IP
wlan.status()                # detailed status code
wlan.status('rssi')          # signal strength (station mode)
wlan.ifconfig()              # (IP, netmask, gateway, DNS)
```

Status codes: `STAT_IDLE`, `STAT_CONNECTING`, `STAT_WRONG_PASSWORD`, `STAT_NO_AP_FOUND`, `STAT_CONNECT_FAIL`, `STAT_GOT_IP`

---

## 8. GDI Display Interface

The board has an **18-pin FPC (flat flex) connector** for plug-and-play display modules. DFRobot GDI-compatible displays connect directly without wiring.

| GDI Signal  | GPIO | Notes                              |
|-------------|------|------------------------------------|
| LCD_BL      | 15   | Backlight (PWM controllable)       |
| LCD_DC      | 8    | Data/Command select                |
| LCD_RST     | 14   | Display reset (active low)         |
| LCD_CS      | 1    | SPI chip select                    |
| SD_CS       | 18   | SD card chip select                |
| TCS         | 6    | Touch controller chip select       |
| SPI_SCK     | 23   | SPI clock                          |
| SPI_MOSI    | 22   | SPI data out                       |
| SPI_MISO    | 21   | SPI data in                        |
| I2C_SDA     | 19   | I2C data                           |
| I2C_SCL     | 20   | I2C clock                          |

Compatible display sizes: 1.54" to 3.5" (240×240 to 480×320 resolution).

---

## 9. Battery & Power Tips

- **Battery monitoring:** GPIO0 is connected to battery voltage via a voltage divider. Read with ADC and apply the divider ratio to get actual battery voltage.
- **Solar charging:** Connect a solar panel to the VCC header — the CN3165 chip handles MPPT charging automatically.
- **Charge indicator:** A small LED on the board shows charging status.
- **Deep sleep:** Call `machine.deepsleep(ms)` to reduce consumption to ~16–36 µA. Board resets on wake — check `machine.reset_cause()` to detect this.

---

## 10. Serial Debugging Notes

The ESP32-C6 uses **USB CDC** for the serial console — there is no separate USB-UART chip.

- In **Arduino / arduino-cli**: append `:CDCOnBoot=cdc` to the FQBN:
  `esp32:esp32:dfrobot_firebeetle2_esp32c6:CDCOnBoot=cdc`
- In **MicroPython**: USB CDC is active by default after flashing.
- REPL baud rate: **115200**
- Always call `Serial.begin(115200)` + `delay(1500)` at the start of `setup()` to let the CDC connection stabilise (Arduino).

---

## 11. Supported Frameworks

| Framework      | Notes                                              |
|----------------|----------------------------------------------------|
| Arduino IDE    | Install Espressif ESP32 board package; use DFRobot FQBN |
| MicroPython    | Use `ESP32_GENERIC_C6` firmware (RISC-V build)     |
| PlatformIO     | Espressif32 platform, `dfrobot_firebeetle2_esp32c6` board |
| ESP-IDF        | Native Espressif framework (most capable, most complex) |

---

## 12. Useful Links

| Resource | URL |
|----------|-----|
| DFRobot Wiki (DFR1075) | https://wiki.dfrobot.com/dfr1075/ |
| MicroPython ESP32-C6 Firmware | https://micropython.org/download/ESP32_GENERIC_C6/ |
| MicroPython ESP32 Quick Reference | https://docs.micropython.org/en/latest/esp32/quickref.html |
| MicroPython ESP32 Intro & Flashing | https://docs.micropython.org/en/latest/esp32/tutorial/intro.html |
| MicroPython machine module | https://docs.micropython.org/en/latest/library/machine.html |
| MicroPython network.WLAN | https://docs.micropython.org/en/latest/library/network.WLAN.html |
| Espressif ESP32-C6 Datasheet | https://www.espressif.com/sites/default/files/documentation/esp32-c6_datasheet_en.pdf |
| esptool documentation | https://docs.espressif.com/projects/esptool/en/latest/ |
