#include <Adafruit_GFX.h>
#include <Adafruit_TFTLCD.h>
#include <Fonts/FreeSerifBold24pt7b.h> // Much larger artistic font for the current time
#include <Fonts/FreeSans12pt7b.h>      // Smaller font for the activity and alarm

#define LCD_CS A3 // Chip Select goes to Analog 3
#define LCD_CD A2 // Command/Data goes to Analog 2
#define LCD_WR A1 // LCD Write goes to Analog 1
#define LCD_RD A0 // LCD Read goes to Analog 0
#define LCD_RESET A4

Adafruit_TFTLCD tft(LCD_CS, LCD_CD, LCD_WR, LCD_RD, LCD_RESET);

String inputString = "";  // String to hold incoming data
bool stringComplete = false; // Whether the string is complete

void setup() {
  Serial.begin(9600);
  tft.begin(0x9341); // Initialize with your screen's driver ID
  tft.setRotation(1); // Adjust orientation if needed
  tft.fillScreen(0xFFFF); // Clear screen with white
}

void loop() {
  // Read incoming data from serial
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
      break;
    }
    inputString += inChar;
  }

  if (stringComplete) {
    updateDisplay(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void updateDisplay(String data) {
  tft.fillScreen(0xFFFF); // Clear screen

  int separator1 = data.indexOf('|');
  int separator2 = data.lastIndexOf('|');
  
  // Extract components
  String currentTime = data.substring(0, separator1);
  String activity = data.substring(separator1 + 1, separator2);
  String alarmTime = data.substring(separator2 + 1);

  // Display the current time with a much larger artistic font
  tft.setFont(&FreeSerifBold24pt7b);  // Larger font for the current time
  tft.setTextSize(1); // Font size is managed by the GFX font itself
  tft.setTextColor(0x0000); // Black text
  int16_t x1, y1;
  uint16_t w, h;
  tft.getTextBounds(currentTime, 0, 0, &x1, &y1, &w, &h); // Calculate text width/height
  tft.setCursor((tft.width() - w) / 2, 75); // Center horizontally, Y-position for line 1
  tft.print(currentTime);

  // Display the activity with a smaller font
  tft.setFont(&FreeSans12pt7b);
  tft.getTextBounds(activity, 0, 0, &x1, &y1, &w, &h);
  tft.setCursor((tft.width() - w) / 2, 140); // Center horizontally, Y-position for line 2
  tft.print(activity);

  // Display the alarm time with a smaller font, adjust position
  String alarmText = "Alarm: " + alarmTime;
  tft.getTextBounds(alarmText, 0, 0, &x1, &y1, &w, &h);
  tft.setCursor((tft.width() - w) / 2 - 6, 200); // Slightly left-adjusted for better centering
  if (alarmTime.length() > 0) {
    tft.print(alarmText);
  }
}
//