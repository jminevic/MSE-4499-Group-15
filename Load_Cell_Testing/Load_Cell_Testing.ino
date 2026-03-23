#include <HX711.h>

#include <AS5600.h>
#include <Wire.h>

#define SDA 36
#define SCL 37
#define potPin 4

AS5600 encoder;
HX711 loadCell;
float calibration_factor = -24440;
int position = 0;
int startPosition = 0;
int finalPosition = 0;
int potRead = 0;

void setup() {
  Serial.begin(9600);
  loadCell.begin(SDA, SCL);

  loadCell.set_scale(calibration_factor);
  loadCell.tare();
}

void loop() {
  float kgValue = loadCell.get_units();
  Serial.print("Weight: ");
  Serial.print(kgValue, 2);
  Serial.println(" kg");

  delay(500);
}