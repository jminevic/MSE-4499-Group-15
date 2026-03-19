#include <HX711.h> // HX711 Arduino Library by Bogdan Necula
#include <AS5600.h> // AS5600 by Rob Tillaart
#include <Wire.h>
#include "helper.h"
#include "waitForKey.h"

HX711 loadCell;

float calibration_factor = 15000;

/*
void setup() {
  Serial.begin(115200);
  Wire.begin(SDA, SCL);
}

void loop() {
  // put your main code here, to run repeatedly:
  uint16_t raw = encoder.readAngle();
  float angle = raw * 360 / 4096;
  Serial.print("Angle: ");
  Serial.print(angle);
  Serial.println(" degrees");

  delay(200);
}
*/

/*
void setup() {
  Serial.begin(9600);
  loadCell.begin(SDA, SCL);

  loadCell.set_scale(calibration_factor);
  loadCell.tare();
}

void loop() {
  float kgValue = loadCell.get_units() * -1;
  Serial.print("Weight: ");
  Serial.print(kgValue, 2);
  Serial.println(" kg");

  delay(500);
}
*/

void setup() {
  Serial.begin(9600);
  Wire.begin(encodeSDA, encodeSCL);
  loadCell.begin(loadSDA, loadSCL);
  loadCell.set_scale(calibration_factor);
  loadCell.tare();

  while (!Serial);

  Serial.println("Select user option:");
  Serial.println("1. New Patient");
  Serial.println("2. Existing Patient");


}

void loop() {

  char key = waitForKey();

  switch (key) {
    case '1':
      Serial.println("New Patient");
      break;
    case '2':
      Serial.println("Existing Patient");
      break;
    default:
      Serial.println(":(");
      break;
    }

  Serial.println("Select a testing option:");
  Serial.println("1. New Patient");
  Serial.println("2. Existing Patient");
}