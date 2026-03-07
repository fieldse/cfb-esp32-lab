# Button press detector on GPIO9 (BOOT button)
# Prints button count to serial when pressed

from machine import Pin
import time

BUTTON_PIN = 9

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

press_count = 0
last_state = 1  # HIGH (released)

print("Button sketch ready!")

while True:
    current_state = button.value()

    # Detect transition from HIGH (released) to LOW (pressed)
    if last_state == 1 and current_state == 0:
        press_count += 1
        print(f"Button pressed! Count: {press_count}")
        time.sleep_ms(20)  # simple debounce

    last_state = current_state
    time.sleep_ms(10)  # debounce sampling rate
