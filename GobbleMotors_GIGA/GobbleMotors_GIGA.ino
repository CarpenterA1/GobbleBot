// Define motor control constants
const byte MOTOR_LEFT = 0x00;
const byte MOTOR_RIGHT = 0x80;
const byte DIRECTION_CW = 0x00;
const byte DIRECTION_CCW = 0x40;
const byte SPEED_STOP = 0x00;
const byte SPEED_FULL = 0x3F;

// Function to control the motor
void controlMotor(byte motor, byte direction, byte speed) {
  byte dataByte = motor | direction | speed;
  Serial1.write(dataByte);
}

// Function to move treads forward
void moveForward() {
  controlMotor(MOTOR_LEFT, DIRECTION_CW, SPEED_FULL);
  controlMotor(MOTOR_RIGHT, DIRECTION_CW, SPEED_FULL);
}

// Function to move treads backward
void moveBackward() {
  controlMotor(MOTOR_LEFT, DIRECTION_CCW, SPEED_FULL);
  controlMotor(MOTOR_RIGHT, DIRECTION_CCW, SPEED_FULL);
}

// Function to turn treads left
void turnLeft() {
  controlMotor(MOTOR_LEFT, DIRECTION_CCW, SPEED_FULL);
  controlMotor(MOTOR_RIGHT, DIRECTION_CW, SPEED_FULL);
}

// Function to turn treads right
void turnRight() {
  controlMotor(MOTOR_LEFT, DIRECTION_CW, SPEED_FULL);
  controlMotor(MOTOR_RIGHT, DIRECTION_CCW, SPEED_FULL);
}

// Function to stop treads
void stopTreads() {
  controlMotor(MOTOR_LEFT, DIRECTION_CW, SPEED_STOP);
  controlMotor(MOTOR_RIGHT, DIRECTION_CW, SPEED_STOP);
}

void setup() {
  // Initialize Serial1 at 9600 baud rate for UART communication
  Serial1.begin(9600);
}

void loop() {
  // Move treads forward for 2 seconds
  moveForward();
  delay(2000);

  // Stop treads for 1 second
  stopTreads();
  delay(1000);

  // Move treads backward for 2 seconds
  moveBackward();
  delay(2000);

  // Stop treads for 1 second
  stopTreads();
  delay(1000);

  // Turn treads left for 2 seconds
  turnLeft();
  delay(2000);

  // Stop treads for 1 second
  stopTreads();
  delay(1000);

  // Turn treads right for 2 seconds
  turnRight();
  delay(2000);

  // Stop treads for 1 second
  stopTreads();
  delay(1000);
}
