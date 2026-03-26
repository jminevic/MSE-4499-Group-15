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
float handSize = 0.0;

long activeSessionId = -1;   // sent from Python host
bool sessionReady = false;

void setup() {
  Serial.begin(9600);
  Wire.begin(encodeSDA, encodeSCL);
  loadCell.begin(loadSDA, loadSCL);
  loadCell.set_scale(calibration_factor);
  loadCell.tare();

  while (!Serial);

  //Serial.println("Select user option:");
  //Serial.println("1. New Patient");
  //Serial.println("2. Existing Patient");

  Serial.println("Ready to begin testing.");
  Serial.println("Waiting for host to send SESSION,<session_id>");
}

void loop() {

  //char key = waitForKey();

  //switch (key) {
  //  case '1':
  //    Serial.println("New Patient");
  //    break;
  //  case '2':
  //    Serial.println("Existing Patient");
  //    break;
  //  default:
  //    Serial.println(":(");
  //    break;
  //  }

  handleHostCommands();

  if (!sessionReady) {
    delay(200);
    return;
  }

    Serial.println("Select Which Test to Perform. Press x to exit.");
    Serial.println("1. Pronation / Supination Range of Motion");
    Serial.println("2. Pronation / Supintation Torque");
    Serial.println("3. Pinch Test");
    Serial.println("4. Radial / Ulnar Deviation");
    Serial.println("5. Wrist Flexion / Extension");

    char testKey = waitForKey();

    switch (testKey) {
    case '1':
      handleProSupROM();
      break;

    case '2':
      handleProSupTorque();
      break;

    case '3':
      handlePinchTest();
      break;

<<<<<<< Updated upstream
    case '4': // radial ulnar deviation
      Serial.println("Radial / Ulnar Deviation Selected.");
      Serial.println("Select Direction and Hand:");
      Serial.println("1. Radial, Left");
      Serial.println("2. Ulnar, Left");
      Serial.println("3. Radial, Right");
      Serial.println("4. Ulnar, Right");

      optionSelect = waitForKey();

      Serial.println("Enter hand size (mm):");
      while (Serial.available() == 0) {
      }
      handSize = Serial.parseFloat();

      for (int i=0; i < 3; i++) {
        Serial.println("Trial ");
        Serial.print(i);
        Serial.println(" of 3");
        results[i] = radialUlnar(handSize);
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

      if (optionSelect == '1') {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtLeft();
        }
        // save data to left flexion
      } else if (optionSelect == '2') {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtLeft();
        }
        // save data to left extension
      } else if (optionSelect == '3') {
        for (int i=0; i < 3; i++) {
          Serial.println("Trial ");
          Serial.print(i);
          Serial.println(" of 3");
          results[i] = flexExtRight();
        }
        // save data to right flexion
      } else if (optionSelect == '4') {
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
=======
    case '4':
      handleRadialUlnar();
      break;

    case '5':
      handleFlexExt();
>>>>>>> Stashed changes
      break;

    case 'x':
      Serial.println("Exiting Test Mode...");
      sessionReady = false;
      activeSessionId = -1;
      Serial.println("Waiting for host to send SESSION,<session_id>");
      break;

    default:
      Serial.println("Invalid Input");
      break;
  }

  //Serial.println("Select a testing option:");
  //Serial.println("1. New Patient");
  //Serial.println("2. Existing Patient");
}

void handleHostCommands() {
  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();

  if (line.startsWith("SESSION,")) {
    String idStr = line.substring(8);
    activeSessionId = idStr.toInt();
    if (activeSessionId > 0) {
      sessionReady = true;
      Serial.print("SESSION_SET,");
      Serial.println(activeSessionId);
    }
  } else if (line == "CLEAR_SESSION") {
    sessionReady = false;
    activeSessionId = -1;
    Serial.println("SESSION_CLEARED");
  }
}

float average3(float a, float b, float c) {
  return (a + b + c) / 3.0;
}

void runThreeTrials(float (*testFunc)()) {
  for (int i = 0; i < 3; i++) {
    Serial.print("Trial ");
    Serial.print(i + 1);
    Serial.println(" of 3");
    results[i] = testFunc();
  }
}

void emitResult(const char* testName, const char* measurementName, const char* hand) {
  float avg = average3(results[0], results[1], results[2]);

  Serial.print("{\"type\":\"result\"");
  Serial.print(",\"session_id\":");
  Serial.print(activeSessionId);
  Serial.print(",\"test_name\":\"");
  Serial.print(testName);
  Serial.print("\"");
  Serial.print(",\"measurement_name\":\"");
  Serial.print(measurementName);
  Serial.print("\"");
  Serial.print(",\"hand\":\"");
  Serial.print(hand);
  Serial.print("\"");
  Serial.print(",\"trial1\":");
  Serial.print(results[0], 3);
  Serial.print(",\"trial2\":");
  Serial.print(results[1], 3);
  Serial.print(",\"trial3\":");
  Serial.print(results[2], 3);
  Serial.print(",\"average\":");
  Serial.print(avg, 3);
  Serial.println("}");
}

void handleProSupROM() {
  Serial.println("Pronation / Supination Range of Motion Selected.");
  Serial.println("1. Pronate Left");
  Serial.println("2. Supinate Left");
  Serial.println("3. Pronate Right");
  Serial.println("4. Supinate Right");

  optionSelect = waitForKey();
  runThreeTrials(proSupROM);

  if (optionSelect == '1') {
    emitResult("Pronation/Supination ROM", "Pronation Angle", "L");
  } else if (optionSelect == '2') {
    emitResult("Pronation/Supination ROM", "Supination Angle", "L");
  } else if (optionSelect == '3') {
    emitResult("Pronation/Supination ROM", "Pronation Angle", "R");
  } else if (optionSelect == '4') {
    emitResult("Pronation/Supination ROM", "Supination Angle", "R");
  } else {
    Serial.println("Invalid Option");
  }
}

void handleProSupTorque() {
  Serial.println("Pronation / Supination Torque Selected.");
  Serial.println("1. Pronate Left");
  Serial.println("2. Supinate Left");
  Serial.println("3. Pronate Right");
  Serial.println("4. Supinate Right");

  optionSelect = waitForKey();
  runThreeTrials(proSupF);

  if (optionSelect == '1') {
    emitResult("Pronation/Supination Torque", "Pronation Torque", "L");
  } else if (optionSelect == '2') {
    emitResult("Pronation/Supination Torque", "Supination Torque", "L");
  } else if (optionSelect == '3') {
    emitResult("Pronation/Supination Torque", "Pronation Torque", "R");
  } else if (optionSelect == '4') {
    emitResult("Pronation/Supination Torque", "Supination Torque", "R");
  } else {
    Serial.println("Invalid Option");
  }
}

void handlePinchTest() {
  Serial.println("Pinch Test Selected.");
  Serial.println("1. Two-Point Pinch, Left");
  Serial.println("2. Two-Point Pinch, Right");
  Serial.println("3. Lateral Pinch, Left");
  Serial.println("4. Lateral Pinch, Right");
  Serial.println("5. Three-Point Pinch, Left");
  Serial.println("6. Three-Point Pinch, Right");

  optionSelect = waitForKey();
  runThreeTrials(pinchTest);

  if (optionSelect == '1') {
    emitResult("Pinch Test", "Two-Point Pinch Force", "L");
  } else if (optionSelect == '2') {
    emitResult("Pinch Test", "Two-Point Pinch Force", "R");
  } else if (optionSelect == '3') {
    emitResult("Pinch Test", "Lateral Pinch Force", "L");
  } else if (optionSelect == '4') {
    emitResult("Pinch Test", "Lateral Pinch Force", "R");
  } else if (optionSelect == '5') {
    emitResult("Pinch Test", "Three-Point Pinch Force", "L");
  } else if (optionSelect == '6') {
    emitResult("Pinch Test", "Three-Point Pinch Force", "R");
  } else {
    Serial.println("Invalid Option");
  }
}

void handleRadialUlnar() {
  Serial.println("Radial / Ulnar Deviation Selected.");
  Serial.println("1. Radial, Left");
  Serial.println("2. Ulnar, Left");
  Serial.println("3. Radial, Right");
  Serial.println("4. Ulnar, Right");

  optionSelect = waitForKey();
  runThreeTrials(radialUlnar);

  if (optionSelect == '1') {
    emitResult("Radial/Ulnar Deviation ROM", "Radial Deviation Angle", "L");
  } else if (optionSelect == '2') {
    emitResult("Radial/Ulnar Deviation ROM", "Ulnar Deviation Angle", "L");
  } else if (optionSelect == '3') {
    emitResult("Radial/Ulnar Deviation ROM", "Radial Deviation Angle", "R");
  } else if (optionSelect == '4') {
    emitResult("Radial/Ulnar Deviation ROM", "Ulnar Deviation Angle", "R");
  } else {
    Serial.println("Invalid Option");
  }
}

void handleFlexExt() {
  Serial.println("Wrist Flexion / Extension Selected.");
  Serial.println("1. Flexion, Left");
  Serial.println("2. Extension, Left");
  Serial.println("3. Flexion, Right");
  Serial.println("4. Extension, Right");

  optionSelect = waitForKey();

  if (optionSelect == '1') {
    runThreeTrials(flexExtLeft);
    emitResult("Wrist Flexion/Extension ROM", "Wrist Flexion Angle", "L");
  } else if (optionSelect == '2') {
    runThreeTrials(flexExtLeft);
    emitResult("Wrist Flexion/Extension ROM", "Wrist Extension Angle", "L");
  } else if (optionSelect == '3') {
    runThreeTrials(flexExtRight);
    emitResult("Wrist Flexion/Extension ROM", "Wrist Flexion Angle", "R");
  } else if (optionSelect == '4') {
    runThreeTrials(flexExtRight);
    emitResult("Wrist Flexion/Extension ROM", "Wrist Extension Angle", "R");
  } else {
    Serial.println("Invalid Option");
  }
}
