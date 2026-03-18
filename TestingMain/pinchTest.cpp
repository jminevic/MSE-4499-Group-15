#include "helper.h"
#include <HX711.h>

HX711 loadCell;

float calibration_factor = 15000;

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