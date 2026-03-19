#include "helper.h"
#include <HX711.h>

HX711 loadCell;

const int testLength = 5000; // 5 seconds
volatile float highestForceApp = 0; // initial
int start = 0;

char waitForKey() {
  while (true) {
    if (Serial.available() > 0) {
      char key = Serial.read();
      if (key == '\n' || key == '\r') {
        continue;
      }
      while (Serial.available() > 0) {
          Serial.read();
      }
      return key;
    }
  }
}

float proSupROM() {
  Serial.println("Hold the handle in the starting position, then press 's' to start. Once the test begins, apply maximum force for 5 seconds. The maximum value will be recorded.");

  char key = waitForKey();

  if (key == 's') {
    start = millis();
    while(millis() < start + testLength) {
      float kgValue = loadCell.get_units() * -1;
      Serial.print("Weight: ");
      Serial.print(kgValue, 2);
      Serial.println(" kg");

      if (kgValue > highestForceApp) {
        highestForceApp = kgValue;
      }
    }
    return highestForceApp;
  } else {
    Serial.println("Not 's' fam");
    return 0;
  }
}