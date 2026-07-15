/**
 * Arduino Leonardo / Pro Micro HID Mouse - Enhanced with Delay System Support
 * Works with: Arduino Leonardo, Pro Micro, or any ATmega32U4 board
 *
 * Board setting in Arduino IDE:
 *   - Board : "Arduino Leonardo" or "SparkFun Pro Micro"
 *   - Port  : Select your COM port
 *
 * This firmware implements a USB HID mouse using the standard Arduino Mouse library.
 * Serial commands are used for control, while HID reports are sent via USB.
 *
 * Enhanced Commands:
 *   M,dx,dy         - Move mouse by dx,dy pixels
 *   MS,dx,dy,steps  - Move mouse smoothly in steps (for Bezier curves)
 *   D               - Press left mouse button
 *   U               - Release left mouse button
 *   C               - Click (press + release)
 *   W,ms            - Wait/delay for ms milliseconds
 *   P               - Ping (health check)
 *   S               - Get status
 *   V               - Get version
 */

#include <Mouse.h>

// Version info
#define FW_VERSION "1.1.0"
#define FW_DATE "2026-07-14"

// Timing control
unsigned long lastMoveTime = 0;
unsigned long minDelayBetweenMoves = 0; // Configurable minimum delay (microseconds)

// Statistics
unsigned long totalCommands = 0;
unsigned long totalMoves = 0;
unsigned long totalClicks = 0;

void setup() {
  // Initialize Serial for receiving commands from Python
  Serial.begin(115200);
  
  // Initialize Mouse library
  Mouse.begin();
  
  // Wait for serial connection (max 5 seconds)
  unsigned long startTime = millis();
  while (!Serial && (millis() - startTime < 5000)) {
    delay(10);
  }
  
  // Send ready signal
  Serial.println("READY");
  Serial.print("VERSION:");
  Serial.println(FW_VERSION);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.length() == 0) {
      return; // Skip empty commands
    }
    
    totalCommands++;

    // Parse and execute command
    if (command.startsWith("M,")) {
      // Move: M,dx,dy
      handleMove(command);
    }
    else if (command.startsWith("MS,")) {
      // Smooth Move: MS,dx,dy,steps
      handleSmoothMove(command);
    }
    else if (command == "D") {
      // Mouse Down
      handleMouseDown();
    }
    else if (command == "U") {
      // Mouse Up
      handleMouseUp();
    }
    else if (command == "C") {
      // Click (Down + Up)
      handleClick();
    }
    else if (command.startsWith("W,")) {
      // Wait: W,milliseconds
      handleWait(command);
    }
    else if (command == "P") {
      // Ping (health check)
      Serial.println("PONG");
    }
    else if (command == "S") {
      // Status
      handleStatus();
    }
    else if (command == "V") {
      // Version
      handleVersion();
    }
    else if (command.startsWith("SETDELAY,")) {
      // Set minimum delay: SETDELAY,microseconds
      handleSetDelay(command);
    }
    else {
      // Unknown command
      Serial.print("ERROR:UNKNOWN:");
      Serial.println(command);
      return;
    }

    // Acknowledgment back to Python
    Serial.println("OK");
  }
}

void handleMove(String command) {
  // Move: M,dx,dy
  int firstComma  = command.indexOf(',');
  int secondComma = command.indexOf(',', firstComma + 1);

  if (firstComma != -1 && secondComma != -1) {
    int dx = command.substring(firstComma + 1, secondComma).toInt();
    int dy = command.substring(secondComma + 1).toInt();

    // Apply minimum delay if set
    if (minDelayBetweenMoves > 0) {
      unsigned long now = micros();
      unsigned long elapsed = now - lastMoveTime;
      if (elapsed < minDelayBetweenMoves) {
        delayMicroseconds(minDelayBetweenMoves - elapsed);
      }
      lastMoveTime = micros();
    }

    // Mouse.move() accepts -127..127 per call
    while (dx != 0 || dy != 0) {
      int moveX = constrain(dx, -127, 127);
      int moveY = constrain(dy, -127, 127);
      Mouse.move(moveX, moveY, 0);
      dx -= moveX;
      dy -= moveY;
      
      // Small delay between chunks for smoother movement
      if (dx != 0 || dy != 0) {
        delayMicroseconds(100);
      }
    }
    
    totalMoves++;
  }
}

void handleSmoothMove(String command) {
  // Smooth Move: MS,dx,dy,steps
  // This breaks a large move into smaller steps for smoother movement
  int firstComma  = command.indexOf(',');
  int secondComma = command.indexOf(',', firstComma + 1);
  int thirdComma  = command.indexOf(',', secondComma + 1);

  if (firstComma != -1 && secondComma != -1 && thirdComma != -1) {
    int dx = command.substring(firstComma + 1, secondComma).toInt();
    int dy = command.substring(secondComma + 1, thirdComma).toInt();
    int steps = command.substring(thirdComma + 1).toInt();
    
    if (steps <= 0) steps = 1;
    if (steps > 100) steps = 100; // Limit max steps

    // Calculate step size
    float stepX = (float)dx / steps;
    float stepY = (float)dy / steps;
    
    float accX = 0.0;
    float accY = 0.0;

    for (int i = 0; i < steps; i++) {
      accX += stepX;
      accY += stepY;
      
      int moveX = (int)accX;
      int moveY = (int)accY;
      
      if (moveX != 0 || moveY != 0) {
        // Apply minimum delay if set
        if (minDelayBetweenMoves > 0) {
          unsigned long now = micros();
          unsigned long elapsed = now - lastMoveTime;
          if (elapsed < minDelayBetweenMoves) {
            delayMicroseconds(minDelayBetweenMoves - elapsed);
          }
          lastMoveTime = micros();
        }
        
        // Move in chunks of max 127 pixels
        int remainX = moveX;
        int remainY = moveY;
        while (remainX != 0 || remainY != 0) {
          int chunkX = constrain(remainX, -127, 127);
          int chunkY = constrain(remainY, -127, 127);
          Mouse.move(chunkX, chunkY, 0);
          remainX -= chunkX;
          remainY -= chunkY;
          
          if (remainX != 0 || remainY != 0) {
            delayMicroseconds(100);
          }
        }
        
        accX -= moveX;
        accY -= moveY;
        totalMoves++;
      }
      
      // Small delay between steps for smooth animation
      if (i < steps - 1) {
        delayMicroseconds(500);
      }
    }
  }
}

void handleMouseDown() {
  if (!Mouse.isPressed(MOUSE_LEFT)) {
    Mouse.press(MOUSE_LEFT);
  }
}

void handleMouseUp() {
  if (Mouse.isPressed(MOUSE_LEFT)) {
    Mouse.release(MOUSE_LEFT);
  }
}

void handleClick() {
  // Full click: down + delay + up
  if (!Mouse.isPressed(MOUSE_LEFT)) {
    Mouse.press(MOUSE_LEFT);
  }
  delay(50); // 50ms hold (human-like)
  if (Mouse.isPressed(MOUSE_LEFT)) {
    Mouse.release(MOUSE_LEFT);
  }
  totalClicks++;
}

void handleWait(String command) {
  // Wait: W,milliseconds
  int commaPos = command.indexOf(',');
  if (commaPos != -1) {
    int ms = command.substring(commaPos + 1).toInt();
    if (ms > 0 && ms <= 10000) { // Max 10 seconds
      delay(ms);
    }
  }
}

void handleStatus() {
  Serial.print("STATUS:");
  Serial.print("commands=");
  Serial.print(totalCommands);
  Serial.print(",moves=");
  Serial.print(totalMoves);
  Serial.print(",clicks=");
  Serial.print(totalClicks);
  Serial.print(",delay=");
  Serial.print(minDelayBetweenMoves);
  Serial.println("us");
}

void handleVersion() {
  Serial.print("VERSION:");
  Serial.print(FW_VERSION);
  Serial.print(" (");
  Serial.print(FW_DATE);
  Serial.println(")");
}

void handleSetDelay(String command) {
  // Set minimum delay: SETDELAY,microseconds
  int commaPos = command.indexOf(',');
  if (commaPos != -1) {
    unsigned long delay_us = command.substring(commaPos + 1).toInt();
    if (delay_us <= 100000) { // Max 100ms
      minDelayBetweenMoves = delay_us;
    }
  }
}
