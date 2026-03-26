#include <Arduino.h>
#include "helper.h"
#include "waitForKey.h"

float radialUlnar(float handSize) {

  float startPosition = 0; //A2
  float finalPosition = 0; //A2
  int potRead = 0;
  const float c = 278.0; //mm
  float A;
  float a;
  float B;
  float bTwo;


  Serial.println("Set the hand support to a comfortable start position, then press 's' to start. Once the movement is completed, press 'f' to finish.");

  char key = waitForKey();

  if (key == 's') {
    potRead = analogRead(potPin);
    A = map(potRead, 0, 4095, -155, 155);
    a = sqrt((c * c) + (c * c) - 2 * c * c * cos(A * PI / 180));
    B = acos(a / (2 * c));
    bTwo = sqrt((a * a) + (handSize * handSize) - 2 * a * handSize * cos(B));
    startPosition = asin((a * sin(B)) / bTwo) * 180 / PI;
    Serial.println(startPosition);

    key = waitForKey();

    if (key == 'f') {
      potRead = analogRead(potPin);
      A = map(potRead, 0, 4095, -155, 155);
      a = sqrt((c * c) + (c * c) - 2 * c * c * cos(A * PI / 180));
      B = acos(a / (2 * c));
      bTwo = sqrt((a * a) + (handSize * handSize) - 2 * a * handSize * cos(B));
      finalPosition = asin((a * sin(B)) / bTwo) * 180 / PI;
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

