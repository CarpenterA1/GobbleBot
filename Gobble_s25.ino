// MOSFET gates for solenoids 1–3
const int NUM_SOL = 3;
const int gatePins[NUM_SOL] = {9, 10, 11};

// how long to hold each solenoid (ms)
const unsigned long PULSE_DURATION = 250;

bool    isOpen[NUM_SOL]        = {false, false, false};
unsigned long openStart[NUM_SOL] = {0, 0, 0};

void setup() {
  // 1) configure MOSFET gates as outputs, start LOW
  for (int i = 0; i < NUM_SOL; i++) {
    pinMode(gatePins[i], OUTPUT);
    digitalWrite(gatePins[i], LOW);
  }

  // 2) init debug on USB
  Serial.begin(115200);
  while (!Serial);

  // 3) init HC-06 on Serial1 @ 19200
  Serial1.begin(19200);
  Serial.println("HC-06 solenoid controller ready");
}

void loop() {
  // 1) check for incoming BT command
  if (Serial1.available()) {
    char c = Serial1.read();
    if (c >= '1' && c <= '3') {
      int idx = c - '1';  // '1'→0, '2'→1, '3'→2

      // start the pulse
      digitalWrite(gatePins[idx], HIGH);
      isOpen[idx] = true;
      openStart[idx] = millis();

      // ACK back over BT
      Serial1.print("SOL");
      Serial1.print(idx+1);
      Serial1.println("_ON");

      // also log to USB
      Serial.print("SOL");
      Serial.print(idx+1);
      Serial.println(" ON");
    }
  }

  // 2) handle time-outs to turn MOSFETs OFF
  unsigned long now = millis();
  for (int i = 0; i < NUM_SOL; i++) {
    if (isOpen[i] && (now - openStart[i] >= PULSE_DURATION)) {
      digitalWrite(gatePins[i], LOW);
      isOpen[i] = false;

      // ACK off
      Serial1.print("SOL");
      Serial1.print(i+1);
      Serial1.println("_OFF");

      Serial.print("SOL");
      Serial.print(i+1);
      Serial.println(" OFF");
    }
  }
}
