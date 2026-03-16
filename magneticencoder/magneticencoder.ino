#include <AS5600.h>
#include <Wire.h>

#define SDA 35
#define SCL 36

AS5600 encoder;

float angle;
float lastAngle = 0;

int turns = 0;
float multiAngle = 0;

float maxAngle = 0;

bool recording = false;
bool trialComplete = false;

unsigned long lastMovementTime = 0;
const int stopTime = 1000;

float movementThreshold = 2;
float neutralThreshold = 10;

const int totalTrials = 3;
int trialCount = 0;

float trialResults[3];

void setup() {

  Serial.begin(115200);
  Wire.begin(SDA, SCL);

  Serial.println("---- Rotation Test ----");
  Serial.println("Return device to neutral to begin");
}

void loop() {

  uint16_t raw = encoder.readAngle();
  angle = raw * 360.0 / 4096.0;

  // detect wraparound
  if (lastAngle > 300 && angle < 60) turns++;
  if (lastAngle < 60 && angle > 300) turns--;

  multiAngle = turns * 360 + angle;

  float change = abs(multiAngle - lastAngle);
  lastAngle = multiAngle;

  // detect start of movement
  if (change > movementThreshold && !recording && !trialComplete) {

    recording = true;
    maxAngle = multiAngle;

    Serial.print("\nTrial ");
    Serial.print(trialCount + 1);
    Serial.println(" recording...");

    lastMovementTime = millis();
  }

  // while rotating
  if (recording) {

    if (abs(multiAngle) > abs(maxAngle)) {
      maxAngle = multiAngle;
    }

    if (change > movementThreshold) {
      lastMovementTime = millis();
    }

    // detect stop
    if (millis() - lastMovementTime > stopTime) {

      recording = false;
      trialComplete = true;

      Serial.print("Trial ");
      Serial.print(trialCount + 1);
      Serial.print(" max rotation: ");
      Serial.println(maxAngle);

      trialResults[trialCount] = maxAngle;
      trialCount++;

      Serial.println("Return to neutral position...");
    }
  }

  // detect neutral reset
  if (trialComplete && abs(multiAngle) < neutralThreshold) {

    Serial.println("Neutral detected.");

    trialComplete = false;
    turns = 0;

    if (trialCount < totalTrials) {

      Serial.print("Ready for trial ");
      Serial.println(trialCount + 1);

    } else {

      calculateResults();
      trialCount = 0;
    }
  }

  delay(20);
}

void calculateResults() {

  float sum = 0;
  float highest = trialResults[0];

  for (int i = 0; i < totalTrials; i++) {

    sum += trialResults[i];

    if (abs(trialResults[i]) > abs(highest)) {
      highest = trialResults[i];
    }
  }

  float average = sum / totalTrials;

  Serial.println("\n---- Test Results ----");

  for (int i = 0; i < totalTrials; i++) {

    Serial.print("Trial ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.println(trialResults[i]);
  }

  Serial.print("Average rotation: ");
  Serial.println(average);

  Serial.print("Highest rotation: ");
  Serial.println(highest);

  Serial.println("\nReturn to neutral to start new test");
}