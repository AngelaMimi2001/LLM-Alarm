#include <Adafruit_DotStar.h>
#include <SPI.h>

// LED strip configuration
#define DATA_PIN    2       // Data pin for LED strip
#define CLOCK_PIN   3       // Clock pin for LED strip
#define NUM_LEDS    20      // Number of LEDs in the strip

Adafruit_DotStar strip(NUM_LEDS, DATA_PIN, CLOCK_PIN, DOTSTAR_BGR);

void setup() {
  Serial.begin(9600);       // Start serial communication
  strip.begin();            // Initialize the LED strip
  strip.show();             // Turn off all LEDs initially
  Serial.println("Arduino is ready!"); // Debug message
}

void loop() {
  // Check if there is data available on the serial port
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Read the incoming command
    input.trim();  // Remove any leading/trailing spaces or newlines

    if (input == "LED:ON") {
      turnOnLEDs();  // Call function to turn on LEDs
    } else if (input == "LED:OFF") {
      turnOffLEDs(); // Call function to turn off LEDs
    }
  }
}

void turnOnLEDs() {
  // Set all LEDs to a bright color (e.g., white)
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 255, 255, 255);  // Full brightness white
  }
  strip.show();  // Update the LED strip
}

void turnOffLEDs() {
  // Turn off all LEDs
  strip.clear();  // Clear all LED colors
  strip.show();   // Update the LED strip
}
