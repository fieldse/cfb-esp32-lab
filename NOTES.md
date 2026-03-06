# Notes

Hardware:
- DFRobot FireBeetle 2 ESP32-C6

hardware FQBN:
- esp32:esp32:dfrobot_firebeetle2_esp32c6


## How to


### Compile the sketch:

```
/opt/homebrew/bin/arduino-cli compile -b esp32:esp32:dfrobot_firebeetle2_esp32c6
```

### Upload to the board
```
/opt/homebrew/bin/arduino-cli upload -b esp32:esp32:dfrobot_firebeetle2_esp32c6 -p /dev/cu.usbmodem1101
```

