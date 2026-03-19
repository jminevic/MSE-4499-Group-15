#include "helper.h"
#include "waitForKey.h"

int startPosition = 0;
int finalPosition = 0;
int potRead = 0;

float flexExt() {
  Serial.println("Set the hand support to a comfortable start position, then press 's' to start. Once the movement is completed, press 'f' to finish.");

  char key = waitForKey();

  if (key == 's') {
    potRead = analogRead(flexExtLeftPot);
    startPosition = map(potRead, 0, 4095, -155, 155);
    Serial.println(startPosition);

    key = waitForKey();

    if (key == 'f') {
      potRead = analogRead(flexExtLeftPot);
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

