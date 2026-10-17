```cpp
// =============================================
// AirTouch: Five-LED Gesture Control
// Board: ESP32
// Communication: USB Serial
// Baud rate: 115200
// =============================================

const int leds[] = {13, 12, 14, 27, 26};
const int totalLEDs = 5;

String command = "";

void allLEDsOff() {
  for (int i = 0; i < totalLEDs; i++) {
    digitalWrite(leds[i], LOW);
  }
}

void allLEDsOn() {
  for (int i = 0; i < totalLEDs; i++) {
    digitalWrite(leds[i], HIGH);
  }
}

void handleCommand(String cmd) {
  cmd.trim();

  if (cmd == "ALL_ON") {
    allLEDsOn();
    Serial.println("ACK:ALL_ON");
  }
  else if (cmd == "ALL_OFF") {
    allLEDsOff();
    Serial.println("ACK:ALL_OFF");
  }
  else if (cmd.startsWith("LED")) {
    int number = cmd.substring(3).toInt();

    if (number >= 1 && number <= totalLEDs) {
      allLEDsOff();
      digitalWrite(leds[number - 1], HIGH);

      Serial.print("ACK:LED");
      Serial.println(number);
    }
    else {
      Serial.println("ERROR:INVALID_LED");
    }
  }
  else {
    Serial.println("ERROR:UNKNOWN_COMMAND");
  }
}

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < totalLEDs; i++) {
    pinMode(leds[i], OUTPUT);
  }

  allLEDsOff();

  Serial.println("AirTouch ESP32 Ready");
}

void loop() {
  while (Serial.available() > 0) {
    char incoming = Serial.read();

    if (incoming == '\n') {
      handleCommand(command);
      command = "";
    }
    else if (incoming != '\r') {
      if (command.length() < 32) {
        command += incoming;
      }
      else {
        command = "";
      }
    }
  }
}
```
