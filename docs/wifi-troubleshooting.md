# MicroPython WiFi failures on FireBeetle 2 ESP32-C6

**The DFRobot FireBeetle 2 ESP32-C6 has a documented hardware power-regulation defect that causes persistent WiFi failures**, particularly after deep sleep cycles. Adding a **10 µF capacitor between 3.3V and GND** resolves the most severe board-specific issues. Beyond this hardware fix, WiFi authentication failures on ESP32-C6 boards running MicroPython stem from a predictable set of causes: WPA authentication mode thresholds, NVS flash corruption, regulatory channel mismatches, TX power self-interference, and timing bugs in the WiFi driver stack. This report consolidates findings from GitHub issues, Espressif errata, DFRobot forums, and MicroPython community discussions into a practical troubleshooting reference.

## The FireBeetle 2 C6 has a confirmed power regulation defect

Two board-specific bugs dominate FireBeetle 2 C6 WiFi complaints, and both trace to the same root cause: inadequate power delivery during WiFi RF initialization.

**Deep sleep + WiFi reboot loop.** After the first successful boot and WiFi connection, subsequent wakes from deep sleep fail to establish WiFi and trigger a software CPU reset (`rst:0xc (SW_CPU)`). Espressif's Arduino team classified this as a hardware issue specific to the DFRobot FireBeetle board (GitHub espressif/arduino-esp32 #9913, labeled "Type: 3rd party Boards"). RTC memory gets cleared during the unexpected reboot, resetting boot counters and breaking any persistent-state logic.

**`pll_cal exceeds 2ms!` permanent WiFi failure.** After days or weeks of operation, the board begins producing this PLL calibration error on wake from deep sleep. Once triggered, **WiFi will not connect again** — not through additional deep sleep cycles, `ESP.restart()`, or `abort()`. Only a physical press of the RST button recovers the device. This failure mode was confirmed on the DFRobot forum (topic 334203) by multiple users running the same board.

Both issues share a single fix: **solder a 10 µF ceramic capacitor between the 3.3V pin and GND**, as close to the ESP32-C6 module as possible. The WiFi transceiver draws current spikes of **300–500 mA** during RF calibration and TX bursts. The FireBeetle 2 C6's onboard voltage regulator and decoupling capacitors are insufficient to prevent voltage sags below the chip's minimum operating threshold (~2.44V), which corrupts PLL calibration and crashes the WiFi subsystem. For battery-powered deployments, users should also ensure the battery can deliver sustained peak currents; the FireBeetle series has documented failures when powered by weak batteries (DFRobot forum topic 16613).

## "Wrong password" errors usually aren't about the password

Authentication failures with correct credentials are among the most commonly reported ESP32 WiFi issues across all variants. The causes fall into a clear hierarchy of likelihood.

**WPA authentication mode threshold (most common cause).** Starting with ESP-IDF versions used in MicroPython ≥1.23.0, the default `authmode threshold` was raised to require WPA2 or WPA3. Routers still configured for WPA-only (WPA1) fail silently with status code **211** (`STAT_NO_AP_FOUND_IN_AUTHMODE_THRESHOLD`), which MicroPython does not map to any named constant — it simply appears as an unexplained numeric code. Users on MicroPython Discussion #16089 confirmed that switching their router from WPA to WPA2 immediately resolved the issue. WPA3-only networks also cause `AUTH_FAIL` (code 202) with error `wpa3: failed to parse SAE commit in state(2)!` — the solution is WPA2/WPA3 mixed mode on the router.

**NVS flash corruption.** ESP32 stores WiFi credentials in non-volatile storage. Corrupted NVS causes persistent password rejection even with correct credentials. Switching firmware frameworks (Arduino → MicroPython) without erasing flash leaves stale WiFi config that silently conflicts with new connection attempts. The fix is `esptool.py --chip esp32c6 erase_flash` before reflashing. This should be standard practice when changing firmware.

**Regulatory domain channel mismatch.** MicroPython defaults to country code "01" (world safe mode), which limits scanning to **channels 1–11 only**. Routers on channels 12 or 13 — common in Europe and Asia — are invisible. MicroPython historically lacked a Python-level API for `esp_wifi_set_country()` (GitHub Issue #7179). In newer versions, `network.country("DE")` or the appropriate country code may be available; otherwise, a custom firmware build is required.

**Reason code confusion in ESP-IDF** compounds the diagnostic difficulty. Wrong passwords return `WIFI_REASON_AUTH_EXPIRE` (2), `WIFI_REASON_NO_AP_FOUND` (201), or even reason code 0 — instead of the expected `WIFI_REASON_AUTH_FAIL` (202). This is a documented long-standing ESP-IDF issue (espressif/esp-idf #3246) that makes programmatic error handling unreliable.

Special characters in passwords (`@`, `&`, `$`, `#`) have been reported to cause connection failures on ESP32 boards (GitHub copercini/esp32-iot-examples #11). SSID encoding matters too — hyphens in SSIDs have caused failures (espressif/arduino-esp32 #7488), and the byte-exact SSID comparison means invisible characters or encoding differences silently break connections.

## GPIO conflicts, antenna issues, and TX power self-interference

**ADC2 pins on the original ESP32** cannot perform analog reads while WiFi is active — the WiFi driver uses the ADC2 peripheral internally. The ESP32-C6 has a simpler ADC architecture (ADC1 on GPIO 0–6) and **largely avoids this conflict**. However, strapping pins on the C6 (GPIO4, GPIO5, GPIO8, GPIO9, GPIO15) must not be pulled at reset, and GPIO12/13 are reserved for native USB.

**TX power self-interference is a critical issue on small boards.** ESP32-C3 "Super Mini" boards — which share the RISC-V architecture and similar RF design with the C6 — are notorious for WiFi failures caused by RF energy from the transmitter disturbing the MCU itself. The community-discovered fix is reducing TX power: `wlan.config(txpower=5)`. At maximum TX power (20 dBm), the current draw peaks at ~150 mA on the RF path alone; on boards with poor antenna isolation or inadequate ground planes, this creates feedback that corrupts the WiFi handshake. Some users have even placed aluminum foil between the chip antenna and the ESP chip as a physical shield.

**Antenna design varies dramatically across boards.** The FireBeetle 2 C6 uses a PCB trace antenna with no external antenna option. Users report detecting only **3–5 networks** where laptops see 15+ (ESP32 forum topic 43316). Antenna orientation matters: the PCB antenna should not be flush against metal surfaces or enclosed in metal cases. For production deployments, boards with u.FL connectors and external antennas are strongly preferred.

**Power supply requirements are non-negotiable for stable WiFi.** The minimum recommendation is a 5V supply rated for **1A or more**, even though average draw is much less — the RF calibration burst at boot is especially demanding. For direct 3.3V supplies, the regulator must handle **500 mA sustained, 700+ mA peak**. Capacitor recommendations from the community: 10 µF ceramic minimum, **100–470 µF low-ESR electrolytic** recommended, placed as close to the ESP32 module's power pins as possible.

## MicroPython firmware maturity and ESP-IDF driver bugs on ESP32-C6

ESP32-C6 support in MicroPython reached general availability with **v1.24.0 (October 2024)**, using ESP-IDF v5.2.2. The current stable release is **v1.27.0 (December 2025)** on ESP-IDF v5.5.1. The C6 is no longer experimental, but it remains a newer target than the original ESP32, and edge-case WiFi bugs persist.

**WDT reset crash (Issue #16137).** In MicroPython v1.24.0, a simple `wlan.active(True); wlan.connect()` sequence could trigger a Watchdog Timer reset loop on ESP32-C6, crashing the device with `Guru Meditation Error: Core 0 panic'd (Interrupt wdt timeout on CPU0)`. This was fixed in subsequent releases — users should run **v1.25.0 or later** at minimum.

**`OSError: Wifi Internal Error` (Discussion #10524).** This persistent issue affects ESP32-C3 and C6 boards. The WiFi subsystem enters an error state that prevents connection. The proven workaround sequence is:

- Toggle the interface: `wlan.active(False); time.sleep(1); wlan.active(True)`
- Disable power management: `wlan.config(pm=wlan.PM_NONE)`
- Reduce TX power: `wlan.config(txpower=5)`
- Free memory before WiFi: `gc.collect()`
- Set country code: `network.country("CN")` or appropriate

**ESP-IDF deep sleep WiFi crash (IDFGH-12626).** At the IDF level, ESP32-C6 resets when starting WiFi after waking from deep sleep — the device connects normally after the reset, but the initial post-deep-sleep WiFi init crashes. This was found on ESP-IDF v5.2 and is separate from the FireBeetle-specific power issue.

**WiFi 6 features are invisible to MicroPython.** The ESP32-C6 supports 2.4 GHz 802.11ax (WiFi 6) with OFDMA and TWT, but MicroPython's `network.WLAN` API exposes none of these features. WiFi 6 negotiation happens automatically at the driver level. The C6 supports only **20 MHz bandwidth** in 802.11ax mode; if the router forces HT40, the chip silently falls back to 802.11bgn. The TWT teardown bug (ESP-IDF #13344) — where tearing down a Target Wake Time agreement causes intermittent TCP connection timeouts — remains open and affects MQTT and similar protocols.

The DFRobot wiki notes that MicroPython firmware for the FireBeetle 2 C6 was originally provided by a community member (HonestQiao), not the official MicroPython project. Users should prefer the **official `ESP32_GENERIC_C6` builds** from micropython.org for better support and bug fixes.

## A reliable connection pattern and systematic troubleshooting checklist

Based on the collective community experience, the following MicroPython code pattern maximizes WiFi reliability on ESP32-C6 boards:

```python
import network, time, gc, machine

def connect_wifi(ssid, password, max_retries=5):
    gc.collect()
    wlan = network.WLAN(network.STA_IF)
    network.WLAN(network.AP_IF).active(False)  # Disable AP interface
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    wlan.config(pm=wlan.PM_NONE)       # Disable power management
    wlan.config(reconnects=0)          # Manual retry control
    # wlan.config(txpower=5)           # Uncomment if board has RF issues

    for attempt in range(max_retries):
        if wlan.isconnected():
            return wlan.ifconfig()
        try:
            wlan.connect(ssid, password)
        except OSError:
            wlan.active(False); time.sleep(1); wlan.active(True); continue
        for _ in range(20):
            if wlan.isconnected():
                return wlan.ifconfig()
            time.sleep(0.5)
        wlan.disconnect(); time.sleep(2)
    machine.reset()
```

Key elements: toggling `active(False/True)` before first connection clears stale WiFi state; `PM_NONE` disables radio power cycling that causes dropped connections; `reconnects=0` prevents infinite retry loops; `gc.collect()` ensures sufficient heap; and `machine.reset()` as final fallback.

For systematic troubleshooting, work through the following in order:

- **Hardware first**: Add 10 µF capacitor (3.3V to GND) on FireBeetle boards. Use a quality USB cable and 1A+ power supply. Check antenna orientation.
- **Firmware**: Flash the latest official `ESP32_GENERIC_C6` build (v1.27.0+) with `erase_flash` first. Never skip the erase step when changing firmware.
- **Router configuration**: Confirm 2.4 GHz band is enabled, WPA2 (not WPA1 or WPA3-only) mode, fixed channel 1/6/11 at 20 MHz width, channels 1–11 if country code cannot be set.
- **MicroPython config**: Disable power management, reduce TX power to 5–8.5 dBm, set country code, toggle active state before connecting, implement retry logic with timeouts.
- **Debug output**: Enable with `import esp; esp.osdebug(0)` to see IDF-level WiFi driver logs on UART0, which reveal the actual disconnect reason codes.

## Conclusion

The FireBeetle 2 C6's WiFi problems are predominantly a **board-level power regulation defect** compounded by ESP32-C6's relative immaturity in the MicroPython ecosystem. The 10 µF capacitor fix addresses the most severe board-specific failures. Authentication errors on ESP32-C6 boards almost always trace to WPA mode thresholds, NVS corruption, or channel visibility — not actual password problems. MicroPython's C6 support has matured significantly from the crash-prone v1.24.0 to the stable v1.27.0, but users must still work around the WiFi driver's power management quirks and the C6's sensitivity to TX power self-interference. The combination of `PM_NONE`, reduced TX power, interface toggling, and proper retry logic transforms an unreliable connection into a dependable one. For production use, the official `ESP32_GENERIC_C6` firmware with a full flash erase is non-negotiable — community firmware and stale NVS data are the hidden source of many "impossible" WiFi failures.