# ESP32-C3 OLED Workshop Project

## Project Overview

This project sub-folder is for preparing a workshop teaching people how to program ESP32 devices using AI assistance. The goal is to prepare ESP32-C3 boards with OTA (Over-The-Air) firmware that allows participants to flash their boards over WiFi, eliminating the need for data-capable USB cables.

### Workshop Challenge
Many participants may bring power-only USB-C cables that cannot transfer data. The solution is to pre-flash boards with firmware that:
1. Connects to WiFi networks:
   - **Workshop**: SSID: `cfb`, Password: `cfb_1958!`
2. Enables OTA firmware updates over WiFi
3. Displays the board's mDNS hostname and IP on the OLED screen (e.g., `esp32-384be46.local` and `192.168.1.123`)
4. Allows participants to flash new firmware using only WiFi (no data cable needed)

## Hardware Information

### Board Specifications
- **Product**: ESP32-C3 OLED Development Board with 0.42" OLED
- **Manufacturer**: ICGOICIC
- **Chip**: ESP32-C3FN4/FH4 (QFN32) revision v0.4
- **Architecture**: RISC-V 32-bit single-core @ 160MHz
- **Flash**: 4MB (XMC) embedded
- **RAM**: 400KB SRAM
- **WiFi**: 802.11 b/g/n (2.4GHz only) with ceramic antenna
- **Bluetooth**: BLE 5.0
- **Crystal**: 40MHz
- **USB**: USB-C connector with native USB-Serial/JTAG support
- **Size**: Ultra-compact form factor (~25mm x 15mm)
- **Packaging**: Individual plastic protective boxes
- **Board Marking**: ESP32-C3FH4_P4J1050

### Display Specifications
- **Type**: SSD1306-compatible OLED (actually SSD1306B variant)
- **Size**: 0.42 inch diagonal
- **Resolution**: 72 x 40 pixels (physical visible area)
- **Controller Resolution**: 128 x 64 (but only 72x40 visible)
- **Color**: White (monochrome)
- **Interface**: I2C
- **I2C Address**: 0x3C
- **I2C Pins**: SDA=GPIO5, SCL=GPIO6
- **Display Offset**: X=28-30, Y=0-24 (varies by library - see below)
- **I2C Speed**: Tested up to 1MHz (400kHz recommended)
- **Viewing**: Very small - may need reading glasses for close work
- **Lifespan**: OLED may burn out after 2-3 years of continuous use

### Critical Display Configuration

**For U8g2 Library (recommended for ESP-IDF/Arduino)**:screen shows squares
```c
// Use the EastRising 72x40 constructor
U8G2_SSD1306_72X40_ER_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE, /* clock=*/ 6, /* data=*/ 5);

// In setup:
u8g2.begin();
u8g2.setContrast(30);  // 0-255, adjust for brightness
u8g2.setBusClock(400000);  // 400kHz I2C speed
```

**Alternative with manual offset (if using 128x64 constructor)**:
```c
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE, 6, 5);
int width = 72;
int height = 40;
int xoffset = 28;  // = (128-72)/2
int yoffset = 24;  // = (64-40)/2
```

**For ESPHome**:
```yaml
i2c:
  sda: 5
  scl: 6

display:
  - platform: ssd1306_i2c
    model: "SSD1306 72x40"
    address: 0x3C
```

**Display Capacity**:
- Small font (6x8): ~12 characters per line, 5 lines max
- Large font (12x16): ~6 characters per line, 2-3 lines max
- Very tiny - best for status indicators, not detailed text

### GPIO Pinout

```
       ┌──── USB-C ────┐
    ───┤ GPIO0   GPIO20├───  TX (UART) - Available
    ───┤ GPIO1   GPIO21├───  RX (UART) - Available
    ───┤ GPIO2   3V3   ├───  3.3V Power Output
    ───┤ GPIO3   GND   ├───  Ground
    ───┤ GPIO4   GPIO10├───  Available
    ───┤ GPIO5   GPIO9 ├───  BOOT Button (active LOW)
    ───┤ GPIO6   GPIO8 ├───  Blue LED (active LOW)
    ───┤ GPIO7   GND   ├───  Ground
       └───────────────┘

Special Functions:
✓ GPIO5  - I2C SDA (OLED display)
✓ GPIO6  - I2C SCL (OLED display)
✓ GPIO8  - Built-in blue LED (active LOW)
✓ GPIO9  - BOOT/User button (active LOW)
✗ GPIO18 - USB D- (DO NOT USE - breaks USB!)
✗ GPIO19 - USB D+ (DO NOT USE - breaks USB!)
✓ GPIO20 - UART TX (available for sensors/peripherals)
✓ GPIO21 - UART RX (available for sensors/peripherals)

Available for Projects:
GPIO0, 1, 2, 3, 4, 7, 10, 20, 21
(GPIO5/6 shared with OLED via I2C - can add more I2C devices on same bus)

SPI Pins (if needed):
Can use GPIO9, 10, 20, 21 for SPI (tested and confirmed working)
```

### USB and Serial
- **USB Mode**: Native USB-Serial/JTAG (no external USB chip like CH340 needed)
- **Serial Output**: Via USB, not via GPIO pins
- **Debug**: Use `ESP_LOGI()` functions for serial debug messages
- **JTAG**: Built-in USB JTAG for debugging and programming
- **Windows Device**: Shows as "USB JTAG/serial debug unit" in Device Manager
- **VID:PID**: 0x303A:0x1001 (Espressif Systems)
- **Serial Number**: Matches MAC address (e.g., 38:44:BE:46:50:E4)
- **Baud Rate**: 115200 (default)

### Current Test Device
- **MAC Address**: 38:44:be:46:50:e4
- **Windows Port**: COM29
- **WSL1 Port**: /dev/ttyS29

### Known Hardware Issues (from user reviews)
- **WiFi Antenna**: Ceramic antenna has limited range - some users report poor reception
- **Display Mounting**: Screen attached with double-sided foam tape - may need re-soldering if loose
- **USB Connector**: On display side (not ideal for enclosures)
- **Heat**: Board can get warm during WiFi operation (~40-50°C)
- **No Native USB HID**: ESP32-C3 doesn't support USB HID/MIDI/MSC natively
- **Display Quirks**: Some units may need display reinitialization after power cycle

## ESP-IDF Installation

### Windows Installation (Recommended for this project)
ESP-IDF v5.5.3 is installed at: `C:\Espressif\frameworks\esp-idf-v5.5.3`

**Key Paths**:
- **Python**: `C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe` (Python 3.11.2)
- **OpenOCD**: `C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\bin\openocd.exe`
- **OpenOCD Scripts**: `C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts`
- **Git**: `C:\Espressif\tools\idf-git\2.44.0\cmd\git.exe` (git 2.44.0)
- **IDF Tools**: `C:\Espressif\tools\`

**Activating ESP-IDF Environment**:
```batch
call C:\Espressif\frameworks\esp-idf-v5.5.3\export.bat
```

After activation, you'll have access to:
- `idf.py` - ESP-IDF build tool
- `esptool.py` - Flash programming tool
- `openocd` - Debug and JTAG tool
- RISC-V toolchain for ESP32-C3

### WSL1 Installation (Not recommended for this project)
ESP-IDF v5.2 is installed at: `/home/cnd/esp/esp-idf`

**Activating ESP-IDF Environment**:
```bash
source /home/cnd/esp/esp-idf/export.sh
```

**Critical Limitation**: WSL1 has severe issues with:
- Serial port access (write timeouts with esptool.py)
- USB device access (OpenOCD cannot see JTAG interface)
- **Use Windows native tools instead**

## Working with OpenOCD and JTAG (Recommended Method)

### Why Use OpenOCD Instead of Serial?

OpenOCD via JTAG is **strongly preferred** over serial (esptool.py) because:
1. **Reliable Reset**: OpenOCD can reset the board without button presses
2. **Better Control**: Full debug capabilities including halt, resume, memory access
3. **No Serial Issues**: Avoids serial port timeout and communication errors
4. **Flash Probing**: Can properly detect and read flash memory
5. **Debugging**: Can set breakpoints, inspect memory, step through code
6. **Faster**: JTAG is faster than serial for large flash operations

### Important: OpenOCD Must Run from Windows

OpenOCD needs direct USB access to the JTAG interface. WSL1 cannot access USB devices directly, so **always run OpenOCD from Windows**, not from WSL.

### OpenOCD Commands

All commands should be run from the project directory. For brevity in examples below, the full OpenOCD path is shown as `openocd` - substitute with the full path or add to PATH.

#### Backup Factory Firmware (Complete Flash Dump)

```cmd
cd C:\Users\cnd\Downloads\cursor\esp32c3lcd

openocd -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg -c "init; reset halt; adapter speed 1000; flash probe 0; flash read_bank 0 firmware_backup.bin 0 0x400000; resume; shutdown"
```

**Full path version**:
```cmd
C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\bin\openocd.exe -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg -c "init; reset halt; adapter speed 1000; flash probe 0; flash read_bank 0 firmware_backup.bin 0 0x400000; resume; shutdown"
```

**Key Points**:
- `flash probe 0` is **CRITICAL** before reading - this initializes the flash driver
- Without `flash probe 0`, the dump will be all zeros (0x00 bytes)
- Reading 4MB takes approximately 10 minutes at adapter speed 1000
- The backup file will be exactly 4194304 bytes (4MB)
- Progress shown: "PROF: Data transferred in XXX ms @ X.XX KB/s"

#### Reset the Board (No Button Press Required)

```cmd
openocd -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg -c "init; reset; resume; shutdown"
```

This is **much better** than serial reset which often fails or requires manual button presses.

#### Flash New Firmware via OpenOCD

```cmd
openocd -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg -c "init; reset halt; adapter speed 1000; flash probe 0; program_esp build/my_project.bin 0x0 verify; reset run; shutdown"
```

#### Interactive OpenOCD Session (for debugging)

```cmd
openocd -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg
```

Then connect with:
- **Telnet**: `telnet localhost 4444` for interactive commands
- **GDB**: `riscv32-esp-elf-gdb` on port 3333 for debugging

### OpenOCD Connection Details

When OpenOCD connects successfully, you'll see:
```
Info : esp_usb_jtag: serial (38:44:BE:46:50:E4)
Info : esp_usb_jtag: Device found. Base speed 40000KHz, div range 1 to 255
Info : clock speed 40000 kHz
Info : JTAG tap: esp32c3.tap0 tap/device found: 0x00005c25 (mfg: 0x612 (Espressif Systems), part: 0x0005, ver: 0x0)
Info : [esp32c3] Examined RISC-V core; found 1 harts
Info : [esp32c3] Examination succeed
```

## Using MCP Terminal Tool (Advanced)

The `user-mypc-terminal` MCP tool is available in Cursor IDE and provides advanced terminal capabilities. It's particularly useful for persistent sessions, complex operations, and monitoring serial output.

### Tool Unlock Token
All operations require: `"tool_unlock_token": "a8cd1903"`

### List Available Serial Ports

```json
{
  "operation": "list_ports",
  "tool_unlock_token": "a8cd1903"
}
```

### Open a Serial Session (for monitoring)

```json
{
  "operation": "open_session",
  "session_id": "esp32_serial",
  "endpoint": "COM29",
  "baud_rate": 115200,
  "set_dtr": false,
  "set_rts": false,
  "tool_unlock_token": "a8cd1903"
}
```

**Important**: `set_dtr` and `set_rts` are set to `false` to prevent unwanted resets on ESP32.

### Read Serial Data

```json
{
  "operation": "read_data",
  "session_id": "esp32_serial",
  "read_timeout": 2,
  "tool_unlock_token": "a8cd1903"
}
```

### Send Data to Serial

```json
{
  "operation": "send_data",
  "session_id": "esp32_serial",
  "data": "test command\r\n",
  "tool_unlock_token": "a8cd1903"
}
```

### Close Session

```json
{
  "operation": "close_session",
  "session_id": "esp32_serial",
  "tool_unlock_token": "a8cd1903"
}
```

## Quick Reference Commands

### Check Device Connection
```cmd
C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe -m esptool --port COM29 chip_id
```

Expected output:
```
Chip is ESP32-C3 (QFN32) (revision v0.4)
Features: WiFi, BLE, Embedded Flash 4MB (XMC)
Crystal is 40MHz
USB mode: USB-Serial/JTAG
MAC: 38:44:be:46:50:e4
```

### Erase Flash (via serial)
```cmd
C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe -m esptool --port COM29 erase_flash
```

### Flash Firmware via Serial (fallback method)
```cmd
C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe -m esptool --port COM29 write_flash 0x0 firmware.bin
```

**Note**: Serial flashing may not reset the board properly - use OpenOCD for reliable reset.

## Building ESP-IDF Projects

### Activate ESP-IDF Environment First

Before running any `idf.py` commands, activate the environment:
```cmd
call C:\Espressif\frameworks\esp-idf-v5.5.3\export.bat
```

You'll see:
```
Done! You can now compile ESP-IDF projects.
Go to the project directory and run:
  idf.py build
```

### Create New Project from Example

```cmd
cd C:\Users\cnd\Downloads\cursor\esp32c3lcd
idf.py create-project-from-example "wifi/getting_started/station:my_project"
```

Or create blank project:
```cmd
idf.py create-project my_project
```

### Set Target to ESP32-C3

```cmd
cd my_project
idf.py set-target esp32c3
```

This configures CMake for ESP32-C3 architecture and toolchain.

### Configure Project (menuconfig)

```cmd
idf.py menuconfig
```

Key configuration areas:
- Component config → WiFi → Set SSID and password
- Component config → ESP32C3-Specific → USB settings
- Partition Table → Select partition scheme (for OTA: "Factory app, two OTA definitions")

### Build Project

```cmd
idf.py build
```

Output binary will be in: `build/my_project.bin`

### Flash via Serial

```cmd
idf.py -p COM29 flash
```

**Issue**: Serial flash does NOT reset the board reliably.

### Flash via OpenOCD (recommended)

```cmd
idf.py -p COM29 openocd flash
```

This uses OpenOCD for flashing and provides reliable reset.

### Monitor Serial Output

```cmd
idf.py -p COM29 monitor
```

Exit monitor with `Ctrl+]`

### Flash and Monitor (combined)

```cmd
idf.py -p COM29 flash monitor
```

### Clean Build

```cmd
idf.py fullclean
```

## Workshop Firmware Requirements

The pre-flashed OTA firmware must include:

### 1. Multi-Network WiFi Configuration

Support both networks with fallback:
```c
// Primary: Workshop network
#define WIFI_SSID_1 "cfb"
#define WIFI_PASS_1 "cfb_1958!"

// Secondary: Testing/home network
#define WIFI_SSID_2 "*"
#define WIFI_PASS_2 "*"
```

Try both networks on boot, connect to whichever is available.

### 2. OTA Support

- HTTP OTA server on port 80
- Web interface at `http://<ip>/` showing device info
- OTA upload page at `http://<ip>/ota`
- Partition scheme: "Factory app, two OTA definitions" for safe updates
- Rollback on failed update

### 3. mDNS/Bonjour Service

- Hostname format: `esp32-<last-6-mac-digits>.local` (e.g., `esp32-4650e4.local`)
- Advertise HTTP service: `_http._tcp`
- Advertise OTA service: `_arduino._tcp` or `_esp32._tcp`

### 4. OLED Display Content

Display should show (scrolling or multi-screen):
- **Screen 1**: mDNS hostname (large text)
- **Screen 2**: IP address
- **Screen 3**: WiFi SSID and signal strength
- **Screen 4**: "Ready for OTA" status

Example display code:
```c
oled_clear();
oled_draw_string_2x(0, 0, "esp32-");
oled_draw_string_2x(0, 16, "4650e4");
oled_draw_string_1x(0, 32, "192.168.1.123");
oled_update_display();
```

### 5. Serial Output on Boot

Print to serial for post-it note labeling:
```
========================================
ESP32-C3 OTA Workshop Board
========================================
MAC: 38:44:be:46:50:e4
mDNS: esp32-4650e4.local
IP: 192.168.1.123
WiFi: cfb (Signal: 75%)
OTA: http://192.168.1.123/ota
========================================
```

### 6. LED Indicator

- Blink LED (GPIO8) to show activity
- Solid on: WiFi connected
- Fast blink: Connecting to WiFi
- Slow blink: OTA in progress
- Off: Error state

## Development Workflow

### Method 1: Using OpenOCD (Recommended)

1. **Edit code** in your project
2. **Build**: `idf.py build`
3. **Flash via OpenOCD**: 
   ```cmd
   openocd -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg -c "init; reset halt; adapter speed 1000; flash probe 0; program_esp build/my_project.bin 0x0 verify; reset run; shutdown"
   ```
4. **Monitor serial**: Use MCP terminal tool or `idf.py -p COM29 monitor`
5. **Test and repeat**

### Method 2: Using OTA (After initial flash)

1. **Edit code** in your project
2. **Build**: `idf.py build`
3. **Upload via web browser**:
   - Open `http://esp32-4650e4.local/ota` (or use IP)
   - Select `build/my_project.bin`
   - Click "Update"
   - Wait 30-60 seconds for reboot
4. **Monitor serial** or check web interface
5. **Test and repeat**

### Method 3: Using idf.py with OpenOCD

```cmd
idf.py -p COM29 openocd flash monitor
```

This combines building, flashing via OpenOCD, and monitoring in one command.

## Display Programming Guide

### Using U8g2 Library (from existing project)

The `esp32c3_ota` folder contains working example code. Key functions:

```c
// Initialize display
void oled_init(void);

// Clear display buffer
void oled_clear(void);

// Draw small text (6x8 font)
void oled_draw_string_1x(int x, int y, const char *str);

// Draw large text (12x16 font)
void oled_draw_string_2x(int x, int y, const char *str);

// Draw progress bar
void oled_draw_bar(int x, int y, int width, int height, int percent);

// Update display (send buffer to screen)
void oled_update_display(void);
```

### Example Display Layouts

**Simple Status**:
```c
oled_clear();
oled_draw_string_2x(0, 10, "READY");
oled_update_display();
```

**WiFi Info**:
```c
oled_clear();
oled_draw_string_1x(0, 0, "WiFi: cfb");
oled_draw_string_2x(0, 12, "75%");
oled_draw_string_1x(0, 32, "192.168.1.5");
oled_update_display();
```

**Multi-Line Status**:
```c
oled_clear();
oled_draw_string_1x(0, 0, "Line 1");
oled_draw_string_1x(0, 10, "Line 2");
oled_draw_string_1x(0, 20, "Line 3");
oled_draw_string_1x(0, 30, "Line 4");
oled_update_display();
```

See `esp32c3_ota/DISPLAY_EXAMPLES.md` for more examples.

## Troubleshooting

### OpenOCD Can't Find Device
- **Check Device Manager**: Look for "USB JTAG/serial debug unit" under "Universal Serial Bus devices"
- **Try different USB port**: Some USB hubs don't work well with JTAG
- **Check USB cable**: Must be data-capable (not power-only)
- **Restart the board**: Unplug and replug USB
- **Close other programs**: Ensure no other program is using the JTAG interface
- **Driver issue**: Windows should auto-install WinUSB driver, but may need manual installation

### Flash Dump Returns All Zeros
- **Must use** `flash probe 0` before `flash read_bank`
- Without flash probe, OpenOCD doesn't initialize the flash driver
- The command sequence MUST be: `init; reset halt; flash probe 0; flash read_bank ...`

### Serial Port Timeout in WSL
- WSL1 has known issues with serial ports (write timeout errors)
- **Solution**: Use Windows native tools instead
- COM ports in WSL map to /dev/ttySN where N is the COM number
- esptool.py in WSL will fail with "Write timeout" error

### Board Won't Reset After Flash
- **Don't use serial reset** - it's unreliable
- **Use OpenOCD reset**: `openocd -f board/esp32c3-builtin.cfg -c "init; reset; resume; shutdown"`
- Takes 2-3 seconds and always works

### Display Shows Nothing
- **Check I2C pins**: GPIO5 (SDA), GPIO6 (SCL)
- **Verify I2C address**: Should be 0x3C
- **Check display offset**: Use U8G2_SSD1306_72X40_ER_F_HW_I2C constructor
- **Power cycle**: Unplug and replug USB
- **Re-solder**: Display may have poor connection (foam tape issue)
- **Call oled_update_display()**: Must be called after drawing

### Display Shows Garbage or Offset
- **Wrong constructor**: Use `U8G2_SSD1306_72X40_ER_F_HW_I2C`, not generic 128x64
- **Wrong offset**: If using 128x64 constructor, set xoffset=28-30, yoffset=0-24
- **Wrong pins**: Must be SCL=6, SDA=5 (not 5, 6 order)

### WiFi Won't Connect
- **Check SSID/password**: Must be exact (case-sensitive)
- **2.4GHz only**: ESP32-C3 doesn't support 5GHz WiFi
- **Weak signal**: Ceramic antenna has limited range (try moving closer to AP)
- **Check serial output**: Look for WiFi connection messages
- **Security**: Supports WPA2/WPA3, not WEP

### OTA Upload Fails
- **Check network**: Device and computer must be on same network
- **Try IP instead of mDNS**: Some networks block mDNS
- **Check file**: Must be the `.bin` file from `build/` folder
- **Wait longer**: OTA takes 30-60 seconds
- **Check partition**: Must have OTA partition scheme configured
- **Fall back to serial/OpenOCD**: If OTA is broken, reflash via JTAG

## Building the Workshop OTA Firmware

### Step 1: Create Project from Example

```cmd
call C:\Espressif\frameworks\esp-idf-v5.5.3\export.bat
cd C:\Users\cnd\Downloads\cursor\esp32c3lcd
idf.py create-project-from-example "system/ota/native_ota_example:workshop_ota"
cd workshop_ota
idf.py set-target esp32c3
```

### Step 2: Configure for OTA

```cmd
idf.py menuconfig
```

Navigate to:
1. **Partition Table** → Select "Factory app, two OTA definitions"
2. **Component config** → **ESP HTTPS OTA** → Enable
3. **Component config** → **WiFi** → Configure as needed

### Step 3: Add Display Support

Add U8g2 library to project:
1. Add as component in `components/` folder
2. Or use ESP-IDF component manager: `idf.py add-dependency "u8g2"`

### Step 4: Modify main.c

Add WiFi credentials, OTA server, mDNS, and display code. See `esp32c3_ota/main/main.c` for working example.

### Step 5: Build and Flash

```cmd
idf.py build
openocd -s C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts -f board/esp32c3-builtin.cfg -c "init; reset halt; adapter speed 1000; flash probe 0; program_esp build/workshop_ota.bin 0x0 verify; reset run; shutdown"
```

### Step 6: Test OTA

1. Note the IP address from serial output
2. Open browser to `http://<ip>/ota`
3. Make a small change to code
4. Build: `idf.py build`
5. Upload `build/workshop_ota.bin` via web interface
6. Verify board reboots with new code

## File Structure

```
esp32c3lcd/
├── README.md                          # This file - complete documentation
├── firmware_backup.bin                # Factory firmware backup (4MB)
├── links.md                           # AliExpress reviews and user feedback
├── pinouts.png                        # Board pinout diagram
├── openocd_dump_flash.cfg            # OpenOCD config for flash dump
├── openocd_connect.cfg               # OpenOCD config for testing
├── esp32c3_ota/                      # Working OTA example project
│   ├── main/
│   │   ├── main.c                    # Source code with WiFi, OTA, display
│   │   └── CMakeLists.txt
│   ├── build/
│   │   └── esp32c3_ota.bin          # Compiled firmware
│   ├── QUICK_START.md               # Quick start guide
│   ├── INDEX.md                     # Documentation index
│   └── README.md                    # Hardware reference
└── workshop_ota/                     # New workshop firmware (to be created)
    └── [project files]
```

## Resources and Documentation

### Official Documentation
- **ESP-IDF Programming Guide**: https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/
- **ESP32-C3 Datasheet**: https://www.espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
- **ESP32-C3 Technical Reference**: https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf

### Community Resources
- **Kevin's Blog**: https://emalliab.wordpress.com/2025/02/12/esp32-c3-0-42-oled/
  - Detailed hardware analysis and pinout verification
- **Arduino Tutorial**: https://projecthub.arduino.cc/Dziubym/sp32-c3-tiny-oled-tutorial-pinout-setup-first-programs-84634a
  - Arduino IDE examples and U8g2 usage
- **U8g2 Library**: https://github.com/olikraus/u8g2
  - Graphics library for monochrome displays

### Key Learnings from User Reviews
1. **Use U8g2 library** - Adafruit library doesn't work well
2. **Correct constructor**: `U8G2_SSD1306_72X40_ER_F_HW_I2C` (EastRising variant)
3. **I2C pins**: GPIO5=SDA, GPIO6=SCL (confirmed by multiple users)
4. **LED pin**: GPIO8 (active LOW)
5. **Boot button**: GPIO9 (active LOW)
6. **SPI available**: Can use GPIO9, 10, 20, 21 for SPI peripherals
7. **Display offset**: Built into ER constructor, no manual offset needed
8. **Works with ESPHome**: Many users successfully using ESPHome firmware

## AI Assistant Notes

When working with this project as an AI assistant:

### Critical Information
- **Always use OpenOCD via JTAG** for flashing and reset operations
- **Use the MCP `user-mypc-terminal` tool** for serial monitoring
- **Run OpenOCD from Windows**, not WSL (USB access required)
- **Remember `flash probe 0`** before any flash read/write operations
- **Terminal MCP unlock token**: `a8cd1903`

### Tool Paths
- **OpenOCD**: `C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\bin\openocd.exe`
- **OpenOCD Scripts**: `C:\Espressif\tools\openocd-esp32\v0.12.0-esp32-20251215\openocd-esp32\share\openocd\scripts`
- **Python**: `C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe`
- **ESP-IDF**: `C:\Espressif\frameworks\esp-idf-v5.5.3\`

### Workflow for Coding Tasks

1. **Activate ESP-IDF**: `call C:\Espressif\frameworks\esp-idf-v5.5.3\export.bat`
2. **Edit code**: Modify source files
3. **Build**: `idf.py build`
4. **Flash via OpenOCD**: Use full command with `flash probe 0` and `program_esp`
5. **Reset**: `openocd ... -c "init; reset; resume; shutdown"`
6. **Monitor**: Use MCP terminal tool to read serial output
7. **Test**: Verify functionality
8. **Iterate**: Repeat from step 2

### Testing OTA Functionality

1. **Initial flash via OpenOCD**: Flash OTA-enabled firmware
2. **Note IP address**: Read from serial output
3. **Test web interface**: Open `http://<ip>/` in browser
4. **Make code change**: Edit and rebuild
5. **Upload via OTA**: Use web interface at `http://<ip>/ota`
6. **Verify reboot**: Check serial output for new firmware
7. **Confirm functionality**: Test that changes work

### Using MCP Terminal Tool

The terminal tool is superior to standard serial monitors:
- **Persistent sessions**: Survives across multiple operations
- **Background reading**: Captures all output automatically
- **Pattern matching**: Wait for specific strings
- **Control sequences**: Send complex command sequences
- **No blocking**: Non-blocking I/O

Example workflow:
```json
// Open session
{"operation": "open_session", "session_id": "esp32", "endpoint": "COM29", "baud_rate": 115200, "set_dtr": false, "set_rts": false, "tool_unlock_token": "a8cd1903"}

// Read output
{"operation": "read_data", "session_id": "esp32", "read_timeout": 2, "tool_unlock_token": "a8cd1903"}

// Wait for specific pattern
{"operation": "wait_for_pattern", "session_id": "esp32", "pattern": "WiFi connected", "read_timeout": 30, "tool_unlock_token": "a8cd1903"}

// Close when done
{"operation": "close_session", "session_id": "esp32", "tool_unlock_token": "a8cd1903"}
```

## Next Steps

### Immediate Tasks
1. ✅ Document hardware and tools (this file)
2. ✅ Backup factory firmware
3. ⏳ Create OTA firmware with dual WiFi support
4. ⏳ Add OLED display code for hostname/IP
5. ⏳ Test OTA functionality
6. ⏳ Flash all workshop boards
7. ⏳ Test mDNS on CfB network
8. ⏳ Prepare troubleshooting guide for participants

### Workshop Preparation
1. **Pre-flash all boards** with OTA firmware
2. **Label each board** with mDNS hostname on post-it note
3. **Test on CfB network** to verify mDNS and OTA work
4. **Prepare backup boards** with known-good data cables
5. **Create participant guide** with simple instructions
6. **Test from participant perspective** using only WiFi

### Future Enhancements
- Add MQTT support for IoT projects
- Implement sleep mode for battery operation
- Add sensor examples (temperature, humidity, etc.)
- Create web-based IDE for in-browser coding
- Add BLE examples for wireless communication

## Common Pitfalls to Avoid

1. **Don't forget `flash probe 0`** - flash operations will fail silently
2. **Don't use WSL for OpenOCD** - USB devices not accessible
3. **Don't use GPIO18/19** - these are USB pins and will break connectivity
4. **Don't expect long WiFi range** - ceramic antenna is limited
5. **Don't use wrong display constructor** - must be 72x40 ER variant
6. **Don't forget to call `oled_update_display()`** - changes won't appear
7. **Don't rely on serial reset** - use OpenOCD reset instead
8. **Don't flash without backup** - always backup factory firmware first

## Success Indicators

You'll know everything is working when:
- ✅ OpenOCD connects and shows "Examination succeed"
- ✅ Flash backup is 4194304 bytes and contains non-zero data
- ✅ Serial output shows WiFi connection and IP address
- ✅ OLED displays hostname and IP
- ✅ Web interface accessible at device IP
- ✅ OTA upload works and device reboots with new firmware
- ✅ mDNS hostname resolves (e.g., `ping esp32-4650e4.local`)
- ✅ LED blinks to indicate status

---

**Last Updated**: March 3, 2026  
**Status**: Ready for workshop firmware development  
**Factory Firmware**: Backed up successfully via OpenOCD JTAG

