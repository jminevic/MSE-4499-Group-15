#include <MSE2202_Lib.h>

// pin constants

#define BUTTON                27
#define SWITCH_PANEL          6      // direction switch motor 1
#define SWITCH_DIRECTION      7      // direction switch motor 2

#define LEFT_MOTOR_A          35       // motor1 pin A
#define LEFT_MOTOR_B          36       // motor1 pin B
#define RIGHT_MOTOR_A         37       // motor2 pin A
#define RIGHT_MOTOR_B         38       // motor2 pin B

#define ENCODER_LEFT_A       15
#define ENCODER_LEFT_B       16
#define ENCODER_RIGHT_A      11
#define ENCODER_RIGHT_B      12

// device specification constants
const int pinionRadius = 10 // in cm
const int pinionPitch = 0.5 // in cm
const int panelLength = 20 // in cm

// PWM stuff (also constants)

const int cPWMRes = 8;                    // bit resolution for PWM
const int cMinPWM = 150;                  // PWM value for minimum speed that turns motor
const int cMaxPWM = pow(2, cPWMRes) - 1;  // PWM value for maximum speed (255 in this case)
const float proportionalGain = 500;       // proportional gain constant - adjust as needed

//encoder software limits

const long LEFT_PANEL_MIN  = 0;      // fully retracted
const long LEFT_PANEL_MAX  = 1200;   // fully extended

const long RIGHT_PANEL_MIN = 0;      // fully retracted
const long RIGHT_PANEL_MAX = 1200;   // fully extended

// system variables

int position = 0;
int button = 0;        // push button (motor ON/OFF toggle)
bool motorsOn = false;
int lastButtonState = HIGH;
int iLeftMotorRunning = 0;
int iRightMotorRunning = 0;

// encoder object
Motion Actuate = Motion();                // Instance of Motion for motor control
Encoders LeftEncoder = Encoders();    // Instance of Encoders for left encoder data
Encoders RightEncoder = Encoders();   // Instance of Encoders for right encoder data

// helper function to stop motors, might separate into left and right
void stopAllMotors()
{
  analogWrite(LEFT_MOTOR_A, 0);
  analogWrite(LEFT_MOTOR_B, 0);
  analogWrite(RIGHT_MOTOR_A, 0);
  analogWrite(RIGHT_MOTOR_B, 0);
}

// helper function, move left motor
// if bool directionOut == true, move out
// if bool direction Out == false, move in
void driveLeftMotor(bool directionOut, int pwmValue)
{
  if (directionOut)
  {
    analogWrite(LEFT_MOTOR_A, pwmValue);
    analogWrite(LEFT_MOTOR_B, 0);
  }
  else
  {
    analogWrite(LEFT_MOTOR_A, 0);
    analogWrite(LEFT_MOTOR_B, pwmValue);
  }
}

// same as above, but for right motor
void driveRightMotor(bool directionOut, int pwmValue)
{
  if (directionOut)
  {
    analogWrite(RIGHT_MOTOR_A, pwmValue);
    analogWrite(RIGHT_MOTOR_B, 0);
  }
  else
  {
    analogWrite(RIGHT_MOTOR_A, 0);
    analogWrite(RIGHT_MOTOR_B, pwmValue);
  }
}

void setup() {
  Serial.begin(115200); //115200 baud is elite, is faster


  // motor pins
  pinMode(LEFT_MOTOR_A, OUTPUT);
  pinMode(LEFT_MOTOR_B, OUTPUT);
  pinMode(RIGHT_MOTOR_A, OUTPUT);
  pinMode(RIGHT_MOTOR_B, OUTPUT);

  // input pins
  pinMode(SWITCH_PANEL, INPUT_PULLUP);
  pinMode(SWITCH_DIRECTION, INPUT_PULLUP);
  pinMode(BUTTON, INPUT_PULLUP);

  // setup encoder objects
  LeftEncoder.Begin(ENCODER_LEFT_A, ENCODER_LEFT_B, &iLeftMotorRunning);
  RightEncoder.Begin(ENCODER_RIGHT_A, ENCODER_RIGHT_B, &iRightMotorRunning);

  // zero encoders at setup (both panels need to be at fully "in" state at startup
  LeftEncoder.clearEncoder();
  RightEncoder.clearEncoder();

  stopAllMotors(); //duh
}

void loop() {

  // read inputs
  int buttonState = digitalRead(BUTTON);
  int panelSelectState = digitalRead(SWITCH_PANEL);
  int directionState = digitalRead(SWITCH_DIRECTION);

  // low means button is pressed (pullup)
  bool buttonPressed = (buttonState == LOW);

  // switch panel high is left panel
  bool moveLeftPanel = (panelSelectState == HIGH);

  // switch direction high means move out
  bool moveOutward = (directionState == HIGH);

  // read encoders
  long leftPos = LeftEncoder.getEncoderRawCount();
  long rightPos = RightEncoder.getEncoderRawCount();

  // default state is not moving
  stopAllMotors();

  // Toggle motors ON/OFF
  if (buttonState == LOW && lastButtonState == HIGH) {
    motorsOn = !motorsOn;
    delay(200);
  }

  lastButtonState = buttonState;

  int toggleState1 = digitalRead(SWITCH_PANEL);
  int toggleState2 = digitalRead(SWITCH_DIRECTION);

  // logic to move panels executes when button pressed
  if (buttonPressed)
  {
    // left panel logic
    if (moveLeftPanel)
    {
      if (moveOutward)
      {
        // extend left panel only if below max limit
        if (leftPos < LEFT_PANEL_MAX)
        {
          driveLeftMotor(true, cMinPWM);
        }
        else
        {
          stopAllMotors();  // software stop at limit
        }
      }
      else
      {
        // retract left panel only if above min limit
        if (leftPos > LEFT_PANEL_MIN)
        {
          driveLeftMotor(false, cMinPWM);
        }
        else
        {
          stopAllMotors();  // software stop at limit
        }
      }
    }
    else
    {
      // right panel logic
      if (moveOutward)
      {
        // extend right panel only if below max limit
        if (rightPos < RIGHT_PANEL_MAX)
        {
          driveRightMotor(true, cMinPWM);
        }
        else
        {
          stopAllMotors();  // software stop at limit
        }
      }
      else
      {
        // retract right panel only if above min limit
        if (rightPos > RIGHT_PANEL_MIN)
        {
          driveRightMotor(false, cMinPWM);
        }
        else
        {
          stopAllMotors();  // software stop at limit
        }
      }
    }
  }

  // print statements for debugging (chat gave me these)
  Serial.print("Left encoder: ");
  Serial.print(leftPos);
  Serial.print(" | Right encoder: ");
  Serial.print(rightPos);
  Serial.print(" | Panel selected: ");
  Serial.print(moveLeftPanel ? "LEFT" : "RIGHT");
  Serial.print(" | Direction: ");
  Serial.print(moveOutward ? "OUT" : "IN");
  Serial.print(" | Button: ");
  Serial.println(buttonPressed ? "PRESSED" : "RELEASED");

  delay(20);
}
