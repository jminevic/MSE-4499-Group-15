#include <Arduino.h>
#include "helper.h"
#include "waitForKey.h"
#include <HX711.h>

float pinchTest() {

  float maxLoad = 0;
  float load = 0;
  int startTime = 0;

  Serial.println("Set your hand to the initial position for the desired pinch strength test, then press 's' to start.");

  char key = waitForKey();

  if (key == 's') {
    startTime = millis();
    maxLoad = 0;

    while (millis() < (startTime + 5000)) {
      load = loadCell.get_units() * -1;
      if (load > maxLoad) {
        maxLoad = load;
      }
    }
    return maxLoad;
  }
  else {
    Serial.println("Not 's' fam");
    return 0;
  }
}