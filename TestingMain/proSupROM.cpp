#include "helper.h"
#include <AS5600.h>

AS5600 encoder;

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
  Serial.println("Hold the handle in the starting position, then press 's' to start. Once the maximum rotation is complete, press 'f' to finish.");

  char key = waitForKey();

  if (key == 's') {
    uint16_t startRaw = encoder.readAngle();
    float startAngle = startRaw * 360 / 4096;
    Serial.print("Starting angle: ");
    Serial.print(startAngle);
    Serial.println(" degrees");

    key = waitForKey();

    if (key == 'f') {
      uint16_t finalRaw = encoder.readAngle();
      float finalAngle = finalRaw * 360 / 4096;
      Serial.print("Final angle: ");
      Serial.print(finalAngle);
      Serial.println(" degrees");

      int totalAngle = (finalAngle - startAngle);
      Serial.print("Total angle: ");
      Serial.print(totalAngle);
      Serial.println(" degrees");

      return totalAngle;
    }
    else {
      Serial.println("Not 'f' fam");
      return 0;
    }
  }
  else {
    Serial.println("Not 's' fam");
    return 0;
  }
}

