#include <Arduino.h>
#include "helper.h"
#include "waitForKey.h"
#include <HX711.h>

float proSupF() {

  const int testLength = 5000; // 5 seconds
  const float momentArm = 100; //change this value after measuring moment arm
  volatile float highestTorqueApp = 0; //inital
  volatile float highestForceApp = 0; // initial
  int start = 0;
  
  Serial.println("Hold the handle in the starting position, then press 's' to start. Once the test begins, apply maximum force for 5 seconds. The maximum value will be recorded.");

  char key = waitForKey();

  if (key == 's') {
    start = millis();
    while(millis() < start + testLength) {
      float kgValue = loadCell.get_units() * -1;
      Serial.print("Torque: ");
      Serial.print(kgValue * momentArm, 2);
      Serial.println(" kg-mm");

      if (kgValue > highestForceApp) {
        highestForceApp = kgValue;
      }
    }
    highestTorqueApp = highestForceApp * momentArm;
    return highestTorqueApp;
  } else {
    Serial.println("Not 's' fam");
    return 0;
  }
}