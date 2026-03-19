#include <HX711.h> // HX711 Arduino Library by Bogdan Necula
#include <AS5600.h> // AS5600 by Rob Tillaart
#include <Wire.h>
#include "helper.h"
#include "waitForKey.h"

HX711 loadCell;

float calibration_factor = 15000;
bool running = false;  // flag for infinite testing loop
int results[3]; // results[0], result[1], results[2]

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

  running = true;     // ensure flag is set to true after patient selected

  while(running) {

    Serial.println("Select Which Test to Perform. Press x to exit.");
    Serial.println("1. Pronation / Supination Range of Motion");
    Serial.println("2. Pronation / Supintation Torque");
    Serial.println("3. Pinch Grip Test");
    Serial.println("4. Radial / Ulnar Deviation");
    Serial.println("5. Wrist Flexion / Extension");

    char testKey = waitForKey();

    switch (testKey) {
    case '1': // pronation supination ROM
      Serial.println("Pronation / Supination Range of Motion Selected.");
      Serial.println("Select Option");
      Serial.println("1. Pronate Left");
      Serial.println("2. Supinate Left");
      Serial.println("3. Pronate Right");
      Serial.println("4. Supinate Right");

      char optionSelect = waitForKey();

      for (int i=0; 2; i++) {
        Serial.println("Trial " + i + " of 3.");
        results[i] = proSupROM();
      }

      if (optionSelect == 1) {
        // save data to left pronate
      } else if (optionSelect == 2) {
        // save data to left supinate
      } else if (optionSelect == 2) {
        // save data to right pronate
      } else if (optionSelect == 2) {
        // save data to right supinate
      } else {
        "Invalid Selection"
      }

      break;
    case '2': // pronation supination torque
      Serial.println("Existing Patient");
      break;
    case '3': // pinch strength
      Serial.println("New Patient");
      break;
    case '4': // radial ulnar deviation
      Serial.println("Existing Patient");
      break;
    case '5': // wrist flexion and extension
      Serial.println("New Patient");
      break;
    case 'x': // exit testing, select new patient
      Serial.println("Exiting Test...");
      running = false;
      break;
    default:
      Serial.println("Invalid Input");
      break;
    }
  }

  Serial.println("Select a testing option:");
  Serial.println("1. New Patient");
  Serial.println("2. Existing Patient");
}