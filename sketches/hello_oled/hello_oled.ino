#include <U8g2lib.h>
#include <Wire.h>

// OLED: 72x40, SDA=GPIO5, SCL=GPIO6
U8G2_SSD1306_72X40_ER_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE, 6, 5);

// Blue LED on GPIO8 (active LOW)
#define LED_PIN 8

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Wire.begin(5, 6);
  u8g2.begin();
  u8g2.setContrast(30);
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB10_tr);
  u8g2.drawStr(4, 20, "Hello!");
  u8g2.setFont(u8g2_font_6x10_tr);
  u8g2.drawStr(4, 36, "OTA works!");
  u8g2.sendBuffer();
}

void loop() {
  digitalWrite(LED_PIN, LOW);   // LED on
  delay(500);
  digitalWrite(LED_PIN, HIGH);  // LED off
  delay(500);
}
