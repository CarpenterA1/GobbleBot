/* 
 * This example shows how to control MDDS30 in Serial Simplified mode with Arduino.
 * Set MDDS30 input mode to 0b11001100
 * Open Serial Monitor, set baudrate to 9600bps and "No line ending".
 * Send 0: Left motor stops
 *      1: Left motor rotates CW with half speed
 *      2: Left motor rotates CW with full speed
 *      3: Left motor rotates CCW with half speed
 *      4: Left motor rotates CCW with full speed
 *      5: Right motor stops
 *      6: Right motor rotates CW with half speed
 *      7: Right motor rotates CW with full speed
 *      8: Right motor rotates CCW with half speed
 *      9: Right motor rotates CCW with full speed
 * 
 * Note: This example also compatible with MDDS10 and MDDS60
 *
 * Hardware Connection:
 *   Arduino Uno    MDDS30
 *   GND ---------- GND
 *   4 ------------ IN1
 *
 * Related Products:
 * - SmartDriveDuo-30: http://www.cytron.com.my/P-MDDS60
 * - CT UNO: http://www.cytron.com.my/p-ct-uno
 * - DC Brush Motors: http://www.cytron.com.my/c-84-dc-motor
 * - LiPo Battery: http://www.cytron.com.my/c-87-power/c-97-lipo-rechargeable-battery-and-charger
 * - Male to Male Jumper: https://www.cytron.com.my/p-wr-jw-mm65
 *
 * URL: http://www.cytron.com.my
 */

#include <Cytron_SmartDriveDuo.h>

#define IN1 1 // Arduino pin 4 is connected to MDDS30 pin IN1.
#define BAUDRATE  9600
#define SPEED_FACTOR .75 // 0-1

Cytron_SmartDriveDuo smartDriveDuo30(SERIAL_SIMPLIFIED, IN1, BAUDRATE);

char inChar;
int speedLeft = 0, speedRight = 0;

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);

  digitalWrite(13, HIGH);
  delay(2000); // Delay for 2 seconds.
  digitalWrite(13, LOW);
}

void loop() {
  if (Serial.available()) {
    delay(100);
    inChar = (char)Serial.read();
    
    switch (inChar) {
      case '0': // Stop
        speedLeft = 0;
        speedRight = 0;
        break;
        
      case '1': // Forward
        speedLeft = 100;
        speedRight = 100;
        break;
        
      case '2': // Backward
        speedLeft = -100;
        speedRight = -100;
        break;
        
      case '3': // Turn left
        speedLeft = -50;
        speedRight = 50;
        break;
        
      case '4': // Turn right
        speedLeft = 50;
        speedRight = -50;
        break;
        
      case '5': // Left tread forward, right tread stop
        speedLeft = 100;
        speedRight = 0;
        break;
        
      case '6': // Left tread backward, right tread stop
        speedLeft = -100;
        speedRight = 0;
        break;
        
      case '7': // Right tread forward, left tread stop
        speedLeft = 0;
        speedRight = 100;
        break;
        
      case '8': // Right tread backward, left tread stop
        speedLeft = 0;
        speedRight = -100;
        break;
        
      case '9': // Diagonal forward left
        speedLeft = 75;
        speedRight = 100;
        break;
        
      case 'A': // Diagonal forward right
        speedLeft = 100;
        speedRight = 75;
        break;
        
      case 'B': // Diagonal backward left
        speedLeft = -75;
        speedRight = -100;
        break;
        
      case 'C': // Diagonal backward right
        speedLeft = -100;
        speedRight = -75;
        break;
    }
    
    // Multiply speeds by SPEED_FACTOR
    speedLeft *= SPEED_FACTOR;
    speedRight *= SPEED_FACTOR;

    smartDriveDuo30.control(speedLeft, speedRight);
  }
}