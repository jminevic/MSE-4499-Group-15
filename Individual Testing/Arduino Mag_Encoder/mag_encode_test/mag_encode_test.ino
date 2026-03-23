#include <AS5600.h>
#include <Wire.h>

#define SDA 35
#define SCL 36
#define potPin 4

AS5600 encoder;
//HX711 loadCell;

float calibration_factor = 15000;
int position = 0;
int startPosition = 0;
int finalPosition = 0;
int potRead = 0;


void setup() {
  Serial.begin(115200);
  Wire.begin(SDA, SCL);
}

void loop() {
  // put your main code here, to run repeatedly:
  uint16_t raw = encoder.readAngle();
  float angle = (raw * 360 / 4096);
  Serial.print("Angle: ");
  Serial.print(angle);
  Serial.println(" degrees");

  delay(200);
}
