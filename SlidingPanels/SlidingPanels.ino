// AUTHORS: Maryam, Anthony, Austin, Jasmin
// this is a test

// pin constants

#define BUTTON                8
#define SWITCH_PANEL          6      // direction switch motor 1
#define SWITCH_DIRECTION      48      // direction switch motor 2

#define LEFT_MOTOR_A          35      // motor1 pin A
#define LEFT_MOTOR_B          36       // motor1 pin B
#define RIGHT_MOTOR_A         37       // motor2 pin A
#define RIGHT_MOTOR_B         38       // motor2 pin B

#define ENCODER_LEFT_A       15
#define ENCODER_LEFT_B       16
#define ENCODER_RIGHT_A      11
#define ENCODER_RIGHT_B      12

// device specification constants
const int pinionRadius = 1; // in cm
const int pinionPitch = 0.2; // in cm
const int panelLength = 20; // in cm

// PWM stuff (also constants)

const int cPWMRes = 8;                    // bit resolution for PWM
const int cMinPWM = 120;                  // PWM value for minimum speed that turns motor
const int cMaxPWM = pow(2, cPWMRes) - 1;  // PWM value for maximum speed (255 in this case)

//encoder software limits

const long LEFT_PANEL_MIN  = 0;      // fully retracted
const long LEFT_PANEL_MAX  = 5000;   // fully extended

const long RIGHT_PANEL_MIN = 0;      // fully retracted
const long RIGHT_PANEL_MAX = 5000;   // fully extended

// system variables

int position = 0;
int button = 0;        // push button (motor ON/OFF toggle)
bool motorsOn = false;
int lastButtonState = HIGH;
int iLeftMotorRunning = 0;
int iRightMotorRunning = 0;

// encoder variables
volatile long leftEncoderCount = 0;
volatile long rightEncoderCount = 0;

// encoder interrupt routines
void IRAM_ATTR leftEncoderISR()
{
  bool a = digitalRead(ENCODER_LEFT_A);
  bool b = digitalRead(ENCODER_LEFT_B);

  if (a == b)
    leftEncoderCount--;
  else
    leftEncoderCount++;
}

void IRAM_ATTR rightEncoderISR()
{
  bool a = digitalRead(ENCODER_RIGHT_A);
  bool b = digitalRead(ENCODER_RIGHT_B);

  if (a == b)
    rightEncoderCount--;
  else
    rightEncoderCount++;
}

// helper functions to read / clear encoders

long getLeftEncoderCount()
{
  noInterrupts();
  long count = leftEncoderCount;
  interrupts();
  return count;
}

long getRightEncoderCount()
{
  noInterrupts();
  long count = rightEncoderCount;
  interrupts();
  return count;
}

void clearLeftEncoder()
{
  noInterrupts();
  leftEncoderCount = 0;
  interrupts();
}

void clearRightEncoder()
{
  noInterrupts();
  rightEncoderCount = 0;
  interrupts();
}

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
  pinMode(ENCODER_LEFT_A, INPUT_PULLUP);
  pinMode(ENCODER_LEFT_B, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_A, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENCODER_LEFT_A), leftEncoderISR, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_RIGHT_A), rightEncoderISR, CHANGE);

  // zero encoders at setup (both panels need to be at fully "in" state at startup
  clearLeftEncoder();
  clearRightEncoder();

  stopAllMotors(); //duh

  // debuggery
  Serial.println("Sliding panel controller started.");
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

  // update + read encoders
  long leftPos = getLeftEncoderCount();
  long rightPos = getRightEncoderCount();

  // default state is not moving
  stopAllMotors();

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