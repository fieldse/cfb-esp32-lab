// Button press detector on GPIO9 (BOOT button)
// Prints "Button pressed!" to serial when pressed
#define BUTTON_PIN 9

bool lastButtonState = HIGH;
int pressCount = 0;

void setup()
{
  Serial.begin(115200);
  delay(1500); // wait for USB-CDC host connection
  Serial.println("Button sketch ready!");

  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop()
{
  bool currentButtonState = digitalRead(BUTTON_PIN);

  // Detect transition from HIGH (released) to LOW (pressed)
  if (lastButtonState == HIGH && currentButtonState == LOW)
  {
    pressCount++;
    Serial.print("Button pressed! Count: ");
    Serial.println(pressCount);
    delay(20); // simple debounce
  }

  lastButtonState = currentButtonState;
  delay(10); // debounce sampling rate
}
