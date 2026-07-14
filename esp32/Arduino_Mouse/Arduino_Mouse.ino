/**
 * Arduino Leonardo / Pro Micro HID Mouse
 * Works with: Arduino Leonardo, Pro Micro, or any ATmega32U4 board
 *
 * Board setting in Arduino IDE:
 *   - Board : "Arduino Leonardo" or "SparkFun Pro Micro"
 *   - Port  : Select your COM port
 *
 * NOTE: USB Product Name spoofing requires modifying boards.txt
 * See README_SETUP.txt for instructions
 */

#include <Mouse.h>

void setup() {
  // Initialize Serial for receiving commands from Python (hardware_mouse.py)
  Serial.begin(115200);
  
  // Initialize Mouse library
  Mouse.begin();
  
  // Wait for serial connection (max 5 seconds)
  unsigned long startTime = millis();
  while (!Serial && (millis() - startTime < 5000)) {
    delay(10);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("M,")) {
      // Move: M,dx,dy
      int firstComma  = command.indexOf(',');
      int secondComma = command.indexOf(',', firstComma + 1);

      if (firstComma != -1 && secondComma != -1) {
        int dx = command.substring(firstComma + 1, secondComma).toInt();
        int dy = command.substring(secondComma + 1).toInt();

        // Mouse.move() accepts -127..127 per call
        while (dx != 0 || dy != 0) {
          int moveX = constrain(dx, -127, 127);
          int moveY = constrain(dy, -127, 127);
          Mouse.move(moveX, moveY, 0);
          dx -= moveX;
          dy -= moveY;
        }
      }
    }
    else if (command == "D") {
      if (!Mouse.isPressed(MOUSE_LEFT)) {
        Mouse.press(MOUSE_LEFT);
      }
    }
    else if (command == "U") {
      if (Mouse.isPressed(MOUSE_LEFT)) {
        Mouse.release(MOUSE_LEFT);
      }
    }

    // Acknowledgment back to Python
    Serial.println("OK");
  }
}
