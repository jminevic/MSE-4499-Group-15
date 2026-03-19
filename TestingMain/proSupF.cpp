#include <Arduino.h>
#include "helper.h"
#include "waitForKey.h"
#include <HX711.h>

float proSupF() {

  const int testLength = 5000; // 5 seconds 
  volatile float highestForceApp = 0; // initial
  int start = 0;
  
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