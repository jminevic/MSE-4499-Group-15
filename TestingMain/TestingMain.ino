#include <HX711.h>
#include <AS5600.h>
#include <Wire.h>

float calibration_factor = 15000;
int position = 0;
int startPosition = 0;
int finalPosition = 0;
int potRead = 0;


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
  while (!Serial);

  Serial.println("Select user option:");
  Serial.println("1. New Patient");
  Serial.println("2. Existing Patient");
}

void loop() {

  int measurement = radialUlnar(potPin);
  char key = waitForKey();

  switch (key) {
    case '1':
      Serial.println("New Patient");
      break;
    case '2':
      Serial.println("Exiting Patient");
      break;
    default:
      Serial.println(":(");
      break;
    }
  // int potRead = analogRead(potPin);
  // position = map(potRead, 0, 4095, -155, 155);
  // Serial.print(position);
  // Serial.println(" degrees");
  Serial.println("Select a testing option:");
  Serial.println("1. New Patient");
  Serial.println("2. Existing Patient");
}