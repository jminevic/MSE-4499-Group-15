#include "helper.h"

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

float flexExt() {
  Serial.println("Set the hand support to a comfortable start position, then press 's' to start. Once the movement is completed, press 'f' to finish.");

  char key = waitForKey();

  if (key == 's') {
    potRead = analogRead(potPin);
    startPosition = map(potRead, 0, 4095, -155, 155);
    Serial.println(startPosition);

    key = waitForKey();

    if (key == 'f') {
      potRead = analogRead(potPin);
      finalPosition = map(potRead, 0, 4095, -155, 155);
      Serial.println(finalPosition);

      int totalAngle = (finalPosition - startPosition);
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

