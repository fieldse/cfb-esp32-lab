import time

count = 0
print("Hello from MicroPython!")

while True:
    count += 1
    print(f"count: {count}")
    time.sleep(1)
