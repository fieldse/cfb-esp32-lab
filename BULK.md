# Bulk Flashing Guide

Flash 40x ESP32-C3 boards with the workshop OTA firmware. User plugs in each board; agent flashes it.

## Firmware files (all in `ota_base_fw/`)

| File | Flash address |
|------|--------------|
| `bootloader/bootloader.bin` | `0x0` |
| `partition_table/partition-table.bin` | `0x8000` |
| `ota_data_initial.bin` | `0xf000` |
| `workshop_firmware.bin` | `0x20000` |

## Prerequisites

Ensure `.claude/settings.json` has these entries in the `allow` list (exact format matters — no `:*` suffix):

```json
"Bash(ls /dev/cu.usbmodem*)",
"Bash(esptool*)"
```

## Per-board procedure

1. **Find port** — run `ls /dev/cu.usbmodem*` to confirm board is connected
2. **Enter bootloader mode** — tell user: *hold BOOT, press+release RST, release BOOT*
3. **Flash** — run the command below (replace PORT if needed):

```bash
esptool --port /dev/cu.usbmodem1101 --baud 460800 --chip esp32c3 write-flash \
  0x0     ota_base_fw/bootloader/bootloader.bin \
  0x8000  ota_base_fw/partition_table/partition-table.bin \
  0xf000  ota_base_fw/ota_data_initial.bin \
  0x20000 ota_base_fw/workshop_firmware.bin
```

4. **Verify** — esptool prints `Hash of data verified` for each file. Board reboots automatically.
5. **Confirm** — OLED shows IP address once connected to WiFi (`cfb` / `cfb_1958!`). Blue LED solid = connected.
6. Unplug, plug in next board, repeat from step 1.

## Notes

- `esptool` is already installed (`/usr/local/bin/esptool`)
- No erase needed — `write-flash` erases only the regions it writes
- If board doesn't connect: repeat BOOT+RST and retry immediately
- Port is usually `/dev/cu.usbmodem1101`; if multiple boards were recently connected, run `ls /dev/cu.usbmodem*` to confirm
- "NO WIFI" on OLED is fine during flashing — it just means the `cfb` network isn't in range
