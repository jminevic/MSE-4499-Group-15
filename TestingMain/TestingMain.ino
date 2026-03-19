#include <HX711.h> // HX711 Arduino Library by Bogdan Necula
#include <AS5600.h> // AS5600 by Rob Tillaart
#include <Wire.h>
#include "helper.h"
#include "waitForKey.h"

HX711 loadCell;

float calibration_factor = 24440;
bool running = false;  // flag for infinite testing loop
float results[3]; // results[0], result[1], results[2]
char optionSelect;

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
      Serial.println("Select Direction and Hand:");
      Serial.println("1. Pronate Left");
      Serial.println("2. Supinate Left");
      Serial.println("3. Pronate Right");
      Serial.println("4. Supinate Right");

      optionSelect = waitForKey();

      for (int i=0; i < 3; i++) {
        Serial.println("Trial ");
        Serial.print(i);
        Serial.println(" of 3");
        results[i] = proSupROM();
      }
      if (optionSelect == 1) {
        // save data to left pronate ROM
      } else if (optionSelect == 2) {
        // save data to left supinate ROM
      } else if (optionSelect == 3) {
        // save data to right pronate ROM
      } else if (optionSelect == 4) {
        // save data to right supinate ROM
      } else {
        Serial.println("Invalid Option");
      }
      break;

    case '2': // pronation supination torque
      Serial.println("Pronation / Supination Torque Selected.");
      Serial.println("Select Direction and Hand:");
      Serial.println("1. Pronate Left");
      Serial.println("2. Supinate Left");
      Serial.println("3. Pronate Right");
      Serial.println("4. Supinate Right");

      optionSelect = waitForKey();

      for (int i=0; i < 3; i++) {
        Serial.println("Trial ");
        Serial.print(i);
        Serial.println(" of 3");
        results[i] = proSupF();
      }
      if (optionSelect == 1) {
        // save data to left pronate torque
      } else if (optionSelect == 2) {
        // save data to left supinate torque
      } else if (optionSelect == 3) {
        // save data to right pronate torque
      } else if (optionSelect == 4) {
        // save data to right supinate torque
      } else {
        Serial.println("Invalid Option");
      }
      break;

    case '3': // pinch strength
      Serial.println("Pinch Grip Strength Selected.");
      Serial.println("Select Pinch Grip Orientation and Hand");
      Serial.println("1. Tip-to-Tip, Left");
      Serial.println("2. Tip-to-Tip, Right");
      Serial.println("3. Lateral Pinch, Left");
      Serial.println("4. Lateral Pinch, Right");
      Serial.println("5. 3-Point Pinch, Left");
      Serial.println("6. 3-Point Pinch, Right");

      optionSelect = waitForKey();
      
      for (int i=0; i < 3; i++) {
        Serial.println("Trial ");
        Serial.print(i);
        Serial.println(" of 3");
        results[i] = pinchTest();
      }
      if (optionSelect == 1) {
        // save data to tip-to-tip, left
      } else if (optionSelect == 2) {
        // save data to tip-to-tip, right
      } else if (optionSelect == 3) {
        // save data to lateral, left
      } else if (optionSelect == 4) {
        // save data to lateral, right
      } else if (optionSelect == 5) {
        // save data to 3-point, left
      } else if (optionSelect == 6) {
        // save data to 3-point, right
      } else {
        Serial.println("Invalid Option");
      }
      break;

    case '4': // radial ulnar deviation
      Serial.println("Radial / Ulnar Deviation Selected.");
      Serial.println("Select Direction and Hand:");
      Serial.println("1. Radial, Left");
      Serial.println("2. Ulnar, Left");
      Serial.println("3. Radial, Right");
      Serial.println("4. Ulnar, Right");

      optionSelect = waitForKey();

      for (int i=0; i < 3; i++) {
        Serial.println("Trial ");
        Serial.print(i);
        Serial.println(" of 3");
        results[i] = radialUlnar();
      }
      if (optionSelect == 1) {
        // save data to left radial
      } else if (optionSelect == 2) {
        // save data to left ulnar
      } else if (optionSelect == 3) {
        // save data to right radial
      } else if (optionSelect == 4) {
        // save data to right ulnar
      } else {
        Serial.println("Invalid Option");
      }
      break;

    case '5': // wrist flexion and extension
      Serial.println("Wrist Flexion / Extension Selected.");
      Serial.println("Select Direction and Hand:");
      Serial.println("1. Flexion, Left");
      Serial.println("2. Extension, Left");
      Serial.println("3. Flexion, Right");
      Serial.println("4. Extension, Right");

      optionSelect = waitForKey();

      if (optionSelect == 1) {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtLeft();
        }
        // save data to left flexion
      } else if (optionSelect == 2) {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtLeft();
        }
        // save data to left extension
      } else if (optionSelect == 3) {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtRight();
        }
        // save data to right flexion
      } else if (optionSelect == 4) {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtRight();
        }
        // save data to right extension
      } else {
        Serial.println("Invalid Option");
      }
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