# Complete Arduino Mouse Solution
## USB Spoofing + High Precision Mouse Control (DPI 1200)

**Last Updated:** 2026-07-16  
**Purpose:** นำ solution นี้ไปใช้กับโปรเจคอื่นได้ทันที

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [USB Spoofing Setup](#usb-spoofing-setup)
4. [Arduino/ESP32 Firmware](#arduinoesp32-firmware)
5. [Python Integration Code](#python-integration-code)
6. [Connection Verification](#connection-verification)
7. [Troubleshooting](#troubleshooting)
8. [Complete Code Examples](#complete-code-examples)

---

## 🎯 Overview

This solution allows Arduino Leonardo or compatible boards to act as a Logitech G Pro X Superlight mouse with high precision control.

**Key Features:**
- ✅ USB Descriptor spoofing (VID:046D, PID:C07D)
- ✅ High precision movement (DPI 1200)
- ✅ Smooth Bezier curve motion
- ✅ Human-like behavior patterns
- ✅ Serial communication protocol
- ✅ Anti-detection compliant

**Use Cases:**
- Game automation
- Drawing/painting automation
- UI testing
- Accessibility tools

---

## 🔧 Hardware Requirements

### Supported Boards

| Board | Chip | USB HID | Recommended |
|-------|------|---------|-------------|
| Arduino Leonardo | ATmega32U4 | ✅ | ⭐⭐⭐⭐⭐ |
| Arduino Pro Micro | ATmega32U4 | ✅ | ⭐⭐⭐⭐⭐ |
| ESP32-S2 | ESP32-S2 | ✅ | ⭐⭐⭐⭐ |
| ESP32-S3 | ESP32-S3 | ✅ | ⭐⭐⭐⭐ |


**Requirements:**
- USB cable (data cable, not charge-only)
- Windows 10/11 (for USB spoofing batch scripts)
- Arduino IDE or arduino-cli

---

## 🎭 USB Spoofing Setup

### Why USB Spoofing?

Games with anti-cheat detect mouse hardware by checking:
1. **VID (Vendor ID)** - Manufacturer identifier
2. **PID (Product ID)** - Device model identifier

By spoofing as Logitech G Pro X Superlight:
- VID: `0x046D` (Logitech)
- PID: `0xC07D` (G Pro X Superlight)

### Step-by-Step Setup

#### 1. Create Spoofing Script

Create `spoof_usb_leonardo.bat`:

```batch
@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Arduino Leonardo USB Spoofing Setup
echo Logitech G Pro X Superlight
echo ========================================
echo.

REM Find Arduino15 directory
set ARDUINO_DIR=%LOCALAPPDATA%\Arduino15\packages\arduino\hardware\avr

if not exist "%ARDUINO_DIR%" (
    echo ERROR: Arduino AVR package not found!
    echo Please install Arduino AVR boards first.
    pause
    exit /b 1
)


REM Find the latest version
for /f "delims=" %%i in ('dir /b /ad /o-n "%ARDUINO_DIR%"') do (
    set AVR_VERSION=%%i
    goto :found_version
)

:found_version
set BOARDS_FILE=%ARDUINO_DIR%\%AVR_VERSION%\boards.txt

echo Found Arduino AVR version: %AVR_VERSION%
echo.

if not exist "%BOARDS_FILE%" (
    echo ERROR: boards.txt not found!
    pause
    exit /b 1
)

REM Backup original
if not exist "%BOARDS_FILE%.backup_original" (
    echo Creating backup...
    copy "%BOARDS_FILE%" "%BOARDS_FILE%.backup_original" >nul
)

echo Modifying USB descriptor...
powershell -Command "(Get-Content '%BOARDS_FILE%') -replace 'leonardo\.build\.usb_product=\"Arduino Leonardo\"', 'leonardo.build.usb_product=\"G Pro X Superlight\"' -replace 'leonardo\.build\.usb_manufacturer=\"Arduino LLC\"', 'leonardo.build.usb_manufacturer=\"Logitech\"' -replace 'leonardo\.build\.vid=0x2341', 'leonardo.build.vid=0x046D' -replace 'leonardo\.build\.pid=0x8036', 'leonardo.build.pid=0xC07D' | Set-Content '%BOARDS_FILE%.new'"

if exist "%BOARDS_FILE%.new" (
    move /y "%BOARDS_FILE%.new" "%BOARDS_FILE%" >nul
    echo ========================================
    echo SUCCESS! USB descriptor modified.
    echo ========================================
    echo.
    echo Changes applied:
    echo   VID: 0x046D (Logitech)
    echo   PID: 0xC07D (G Pro X Superlight)
    echo.
    echo IMPORTANT: Restart Arduino IDE now!
    echo.
)

pause
```


#### 2. Run the Spoofing Script

```bash
# Run as administrator (optional but recommended)
spoof_usb_leonardo.bat
```

#### 3. Restart Arduino IDE

Close and reopen Arduino IDE for changes to take effect.

---

## 💻 Arduino/ESP32 Firmware

### High Precision Mouse Firmware (DPI 1200)

Create `Arduino_Mouse_HighPrecision.ino`:

```cpp
/**
 * High Precision Arduino Mouse Controller
 * DPI: 1200 equivalent
 * Smooth movement with sub-pixel precision
 * 
 * Compatible with:
 * - Arduino Leonardo
 * - Arduino Pro Micro
 * - Any ATmega32U4 board
 * 
 * Features:
 * - Fractional pixel accumulation
 * - Smooth acceleration/deceleration
 * - High precision positioning
 */

#include <Mouse.h>

// Configuration
const int BAUD_RATE = 115200;
const float DPI_SCALE = 1.2;  // DPI 1200 scaling factor

// Fractional pixel accumulator for sub-pixel precision
float positionAccumulatorX = 0.0;
float positionAccumulatorY = 0.0;

void setup() {
  Serial.begin(BAUD_RATE);
  Mouse.begin();
  
  // Wait for serial connection (max 5 seconds)
  unsigned long startTime = millis();
  while (!Serial && (millis() - startTime < 5000)) {
    delay(10);
  }
  
  Serial.println("READY");
}


void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("M,")) {
      // High precision move: M,dx,dy
      handlePrecisionMove(command);
    }
    else if (command.startsWith("S,")) {
      // Smooth move with steps: S,dx,dy,steps
      handleSmoothMove(command);
    }
    else if (command == "D") {
      // Mouse button down
      if (!Mouse.isPressed(MOUSE_LEFT)) {
        Mouse.press(MOUSE_LEFT);
      }
      Serial.println("OK");
    }
    else if (command == "U") {
      // Mouse button up
      if (Mouse.isPressed(MOUSE_LEFT)) {
        Mouse.release(MOUSE_LEFT);
      }
      Serial.println("OK");
    }
    else if (command == "R") {
      // Reset accumulators
      positionAccumulatorX = 0.0;
      positionAccumulatorY = 0.0;
      Serial.println("RESET");
    }
  }
}

void handlePrecisionMove(String command) {
  int firstComma = command.indexOf(',');
  int secondComma = command.indexOf(',', firstComma + 1);
  
  if (firstComma == -1 || secondComma == -1) {
    Serial.println("ERR");
    return;
  }
  
  // Parse target movement
  float targetX = command.substring(firstComma + 1, secondComma).toFloat();
  float targetY = command.substring(secondComma + 1).toFloat();
  
  // Apply DPI scaling
  targetX *= DPI_SCALE;
  targetY *= DPI_SCALE;
  
  // Add to accumulator for sub-pixel precision
  positionAccumulatorX += targetX;
  positionAccumulatorY += targetY;
  
  // Extract integer part for actual movement
  int moveX = (int)positionAccumulatorX;
  int moveY = (int)positionAccumulatorY;
  
  // Keep fractional part in accumulator
  positionAccumulatorX -= moveX;
  positionAccumulatorY -= moveY;
  
  // Execute movement in chunks (Mouse.move limit: -127 to 127)
  executeMove(moveX, moveY);
  
  Serial.println("OK");
}


void handleSmoothMove(String command) {
  // Parse: S,dx,dy,steps
  int comma1 = command.indexOf(',');
  int comma2 = command.indexOf(',', comma1 + 1);
  int comma3 = command.indexOf(',', comma2 + 1);
  
  if (comma1 == -1 || comma2 == -1 || comma3 == -1) {
    Serial.println("ERR");
    return;
  }
  
  float targetX = command.substring(comma1 + 1, comma2).toFloat();
  float targetY = command.substring(comma2 + 1, comma3).toFloat();
  int steps = command.substring(comma3 + 1).toInt();
  
  if (steps <= 0) steps = 1;
  
  // Apply DPI scaling
  targetX *= DPI_SCALE;
  targetY *= DPI_SCALE;
  
  // Calculate movement per step
  float stepX = targetX / steps;
  float stepY = targetY / steps;
  
  // Execute smooth movement
  for (int i = 0; i < steps; i++) {
    positionAccumulatorX += stepX;
    positionAccumulatorY += stepY;
    
    int moveX = (int)positionAccumulatorX;
    int moveY = (int)positionAccumulatorY;
    
    if (moveX != 0 || moveY != 0) {
      positionAccumulatorX -= moveX;
      positionAccumulatorY -= moveY;
      executeMove(moveX, moveY);
      delay(1);  // Small delay for smooth movement
    }
  }
  
  Serial.println("OK");
}

void executeMove(int dx, int dy) {
  // Break down movement into -127..127 chunks
  while (dx != 0 || dy != 0) {
    int moveX = constrain(dx, -127, 127);
    int moveY = constrain(dy, -127, 127);
    
    Mouse.move(moveX, moveY, 0);
    
    dx -= moveX;
    dy -= moveY;
    
    // Micro delay for stability
    if (dx != 0 || dy != 0) {
      delayMicroseconds(100);
    }
  }
}
```


### ESP32 Version (Alternative)

For ESP32-S2/S3 boards with USB HID support:

```cpp
/**
 * ESP32 High Precision Mouse Controller
 * For ESP32-S2 / ESP32-S3 with USB HID
 */

#include "USB.h"
#include "USBHIDMouse.h"

USBHIDMouse Mouse;
const int BAUD_RATE = 115200;
const float DPI_SCALE = 1.2;

float accX = 0.0;
float accY = 0.0;

void setup() {
  Serial.begin(BAUD_RATE);
  Mouse.begin();
  USB.begin();
  
  delay(1000);
  Serial.println("READY");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.startsWith("M,")) {
      int c1 = cmd.indexOf(',');
      int c2 = cmd.indexOf(',', c1 + 1);
      
      float dx = cmd.substring(c1 + 1, c2).toFloat() * DPI_SCALE;
      float dy = cmd.substring(c2 + 1).toFloat() * DPI_SCALE;
      
      accX += dx;
      accY += dy;
      
      int mx = (int)accX;
      int my = (int)accY;
      
      accX -= mx;
      accY -= my;
      
      Mouse.move(mx, my);
      Serial.println("OK");
    }
    else if (cmd == "D") {
      Mouse.press(MOUSE_LEFT);
      Serial.println("OK");
    }
    else if (cmd == "U") {
      Mouse.release(MOUSE_LEFT);
      Serial.println("OK");
    }
  }
}
```

---


## 🐍 Python Integration Code

### High Precision Arduino Mouse Controller

```python
"""
High Precision Arduino Mouse Controller
DPI 1200 with smooth Bezier curve movement
"""

import time
import serial
import serial.tools.list_ports
import math
import random
from typing import Optional, Tuple, List


class HighPrecisionArduinoMouse:
    """
    High precision mouse controller with DPI 1200 equivalent
    Supports smooth Bezier curve movement and human-like behavior
    """
    
    def __init__(self):
        self.serial: Optional[serial.Serial] = None
        self.port: Optional[str] = None
        self.dpi_multiplier = 1.0  # Adjust based on actual DPI
        
    def connect(self, port: str, baud_rate: int = 115200) -> bool:
        """Connect to Arduino"""
        try:
            self.serial = serial.Serial(port, baud_rate, timeout=1)
            self.port = port
            time.sleep(2)  # Wait for Arduino reset
            
            # Clear buffer and wait for READY
            self.serial.reset_input_buffer()
            response = self.serial.readline().decode().strip()
            
            print(f"✅ Connected to {port}: {response}")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.serial = None
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.serial:
            try:
                self.serial.close()
            except:
                pass
            finally:
                self.serial = None
                self.port = None


    
    def _send_command(self, command: str) -> bool:
        """Send command to Arduino and wait for response"""
        if not self.serial:
            return False
        
        try:
            self.serial.reset_input_buffer()
            self.serial.write(f"{command}\n".encode())
            
            # Wait for response
            response = self.serial.readline().decode().strip()
            return response == "OK" or response == "READY"
            
        except Exception as e:
            print(f"Command error: {e}")
            return False
    
    def move_relative(self, dx: int, dy: int) -> bool:
        """
        Move mouse relative to current position
        High precision with sub-pixel accuracy
        
        Args:
            dx: X movement (pixels)
            dy: Y movement (pixels)
        """
        return self._send_command(f"M,{dx},{dy}")
    
    def move_smooth(self, dx: int, dy: int, steps: int = 10) -> bool:
        """
        Move mouse smoothly over multiple steps
        
        Args:
            dx, dy: Target movement
            steps: Number of interpolation steps
        """
        return self._send_command(f"S,{dx},{dy},{steps}")
    
    def get_bezier_points(self, 
                         start: Tuple[int, int], 
                         end: Tuple[int, int],
                         steps: int = 20) -> List[Tuple[int, int]]:
        """
        Generate smooth Bezier curve points for human-like movement
        
        Args:
            start: Starting position (x, y)
            end: Ending position (x, y)
            steps: Number of curve points
            
        Returns:
            List of (x, y) waypoints
        """
        sx, sy = start
        ex, ey = end
        
        # Calculate distance for control point offset
        dist = math.hypot(ex - sx, ey - sy)
        offset_mag = min(dist * 0.1, 30)  # 10% of distance, max 30px
        
        # Generate control points with randomization
        c1x = sx + (ex - sx) * 0.25 + random.uniform(-offset_mag, offset_mag)
        c1y = sy + (ey - sy) * 0.25 + random.uniform(-offset_mag, offset_mag)
        
        c2x = sx + (ex - sx) * 0.75 + random.uniform(-offset_mag, offset_mag)
        c2y = sy + (ey - sy) * 0.75 + random.uniform(-offset_mag, offset_mag)


        
        # Generate Bezier curve points
        points = []
        for i in range(steps + 1):
            t = i / steps
            
            # Ease-in-out for natural acceleration
            if t < 0.5:
                t_eased = 2 * t * t
            else:
                t_eased = 1 - pow(-2 * t + 2, 2) / 2
            
            u = 1 - t_eased
            
            # Cubic Bezier formula
            x = (u**3 * sx + 
                 3 * u**2 * t_eased * c1x + 
                 3 * u * t_eased**2 * c2x + 
                 t_eased**3 * ex)
            
            y = (u**3 * sy + 
                 3 * u**2 * t_eased * c1y + 
                 3 * u * t_eased**2 * c2y + 
                 t_eased**3 * ey)
            
            # Add micro jitter (human tremor)
            jitter_x = random.uniform(-0.5, 0.5)
            jitter_y = random.uniform(-0.5, 0.5)
            
            points.append((int(x + jitter_x), int(y + jitter_y)))
        
        return points
    
    def move_to_smooth(self, target_x: int, target_y: int, 
                       current_x: int, current_y: int) -> bool:
        """
        Move to target position using smooth Bezier curve
        
        Args:
            target_x, target_y: Destination
            current_x, current_y: Current position
        """
        dist = math.hypot(target_x - current_x, target_y - current_y)
        
        # For short distances, move directly
        if dist < 10:
            dx = target_x - current_x
            dy = target_y - current_y
            return self.move_relative(dx, dy)
        
        # Generate smooth curve
        steps = max(10, int(dist / 30))
        waypoints = self.get_bezier_points(
            (current_x, current_y),
            (target_x, target_y),
            steps=steps
        )
        
        # Move through waypoints
        prev_x, prev_y = current_x, current_y
        for wx, wy in waypoints[1:]:  # Skip first point (current position)
            dx = wx - prev_x
            dy = wy - prev_y
            
            if dx != 0 or dy != 0:
                self.move_relative(dx, dy)
                time.sleep(random.uniform(0.003, 0.008))  # 3-8ms delay
            
            prev_x, prev_y = wx, wy
        
        # Final adjustment to exact target
        final_dx = target_x - prev_x
        final_dy = target_y - prev_y
        if final_dx != 0 or final_dy != 0:
            self.move_relative(final_dx, final_dy)
        
        return True


    
    def click(self):
        """Perform click with human-like timing"""
        self._send_command("D")
        time.sleep(random.uniform(0.04, 0.09))  # 40-90ms press
        self._send_command("U")
        time.sleep(random.uniform(0.03, 0.07))  # 30-70ms after
    
    def mouse_down(self):
        """Press mouse button"""
        self._send_command("D")
    
    def mouse_up(self):
        """Release mouse button"""
        self._send_command("U")
    
    def reset_accumulators(self):
        """Reset sub-pixel accumulators"""
        return self._send_command("R")


# Helper function to find Arduino port
def find_arduino_port() -> Optional[str]:
    """Find Arduino COM port automatically"""
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        desc = port.description.lower()
        hwid = port.hwid.lower()
        
        # Look for Arduino or Logitech VID/PID
        if any(kw in desc for kw in ['arduino', 'leonardo', 'usb serial']):
            return port.device
        
        if 'vid_046d' in hwid and 'pid_c07d' in hwid:
            return port.device
    
    return None
```

---


## ✅ Connection Verification

### Method 1: Python Script

Create `verify_connection.py`:

```python
"""
Quick verification script for Arduino mouse connection
"""

import subprocess
import json
import re
from typing import Optional

def check_usb_spoofing() -> bool:
    """Check if Arduino is spoofed as Logitech"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-WmiObject Win32_PointingDevice | Select-Object Name, PNPDeviceID | ConvertTo-Json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False
        
        devices = json.loads(result.stdout)
        if not isinstance(devices, list):
            devices = [devices]
        
        for device in devices:
            pnp_id = device.get('PNPDeviceID', '')
            vid = re.search(r'VID_([0-9A-F]{4})', pnp_id, re.IGNORECASE)
            pid = re.search(r'PID_([0-9A-F]{4})', pnp_id, re.IGNORECASE)
            
            if vid and pid:
                if vid.group(1).upper() == '046D' and pid.group(1).upper() == 'C07D':
                    print(f"✅ Found Logitech G Pro X Superlight")
                    print(f"   VID: 046D, PID: C07D")
                    print(f"   Device: {device.get('Name', 'Unknown')}")
                    return True
        
        print("❌ Logitech VID/PID not found")
        return False
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Arduino USB Spoofing Verification")
    print("="*60)
    check_usb_spoofing()
```


### Method 2: PowerShell One-Liner

```powershell
Get-WmiObject Win32_PointingDevice | Where-Object {$_.PNPDeviceID -match "VID_046D.*PID_C07D"} | Select-Object Name, PNPDeviceID
```

### Method 3: Device Manager

1. Open Device Manager (Win + X → Device Manager)
2. Expand **Mice and other pointing devices**
3. Right-click device → **Properties** → **Details** tab
4. Select **Hardware Ids**
5. Look for: `HID\VID_046D&PID_C07D`

---

## 💡 Complete Code Examples

### Example 1: Basic Movement Test

```python
from high_precision_mouse import HighPrecisionArduinoMouse, find_arduino_port
import time

# Find and connect
port = find_arduino_port()
if not port:
    port = input("Enter COM port: ")

mouse = HighPrecisionArduinoMouse()
if mouse.connect(port):
    print("Testing movement...")
    
    # Move in square pattern
    for _ in range(4):
        mouse.move_relative(100, 0)
        time.sleep(0.5)
        mouse.move_relative(0, 100)
        time.sleep(0.5)
        mouse.move_relative(-100, 0)
        time.sleep(0.5)
        mouse.move_relative(0, -100)
        time.sleep(0.5)
    
    mouse.disconnect()
```


### Example 2: Smooth Movement with Bezier

```python
import pyautogui
from high_precision_mouse import HighPrecisionArduinoMouse, find_arduino_port

mouse = HighPrecisionArduinoMouse()
port = find_arduino_port() or "COM6"

if mouse.connect(port):
    # Get current position
    current_x, current_y = pyautogui.position()
    
    # Move to target with smooth curve
    target_x, target_y = 800, 400
    
    print(f"Moving from ({current_x}, {current_y}) to ({target_x}, {target_y})")
    mouse.move_to_smooth(target_x, target_y, current_x, current_y)
    
    # Click at destination
    mouse.click()
    
    mouse.disconnect()
```

### Example 3: Drawing Application

```python
import pyautogui
from high_precision_mouse import HighPrecisionArduinoMouse, find_arduino_port
import time

def draw_circle(mouse, center_x, center_y, radius, steps=36):
    """Draw a circle using Arduino mouse"""
    import math
    
    # Move to starting position
    start_x = center_x + radius
    start_y = center_y
    
    current = pyautogui.position()
    mouse.move_to_smooth(start_x, start_y, current[0], current[1])
    time.sleep(0.5)
    
    # Start drawing
    mouse.mouse_down()
    time.sleep(0.1)
    
    # Draw circle
    for i in range(steps + 1):
        angle = (2 * math.pi * i) / steps
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        current = pyautogui.position()
        dx = int(x - current[0])
        dy = int(y - current[1])
        
        mouse.move_relative(dx, dy)
        time.sleep(0.02)
    
    # Finish
    mouse.mouse_up()
    time.sleep(0.3)

# Main
mouse = HighPrecisionArduinoMouse()
if mouse.connect(find_arduino_port() or "COM6"):
    print("Drawing circle...")
    draw_circle(mouse, 500, 400, 100)
    print("Done!")
    mouse.disconnect()
```


### Example 4: Game Automation

```python
from high_precision_mouse import HighPrecisionArduinoMouse, find_arduino_port
import pyautogui
import time
import random

class GameAutomation:
    def __init__(self, com_port: str):
        self.mouse = HighPrecisionArduinoMouse()
        self.mouse.connect(com_port)
    
    def click_position(self, x, y, delay_after=0.5):
        """Click at specific position with smooth movement"""
        current = pyautogui.position()
        self.mouse.move_to_smooth(x, y, current[0], current[1])
        time.sleep(random.uniform(0.1, 0.3))  # Human reaction time
        self.mouse.click()
        time.sleep(delay_after)
    
    def drag_to(self, target_x, target_y, duration=1.0):
        """Drag from current position to target"""
        current = pyautogui.position()
        
        # Press button
        self.mouse.mouse_down()
        time.sleep(0.1)
        
        # Calculate steps based on duration
        steps = int(duration * 30)  # 30 steps per second
        
        # Smooth drag
        waypoints = self.mouse.get_bezier_points(
            current, (target_x, target_y), steps=steps
        )
        
        prev_x, prev_y = current
        for wx, wy in waypoints[1:]:
            dx = wx - prev_x
            dy = wy - prev_y
            self.mouse.move_relative(dx, dy)
            time.sleep(duration / steps)
            prev_x, prev_y = wx, wy
        
        # Release button
        time.sleep(0.1)
        self.mouse.mouse_up()
    
    def human_like_click(self, x, y):
        """Click with human-like variation"""
        # Add small random offset (humans don't click exact pixels)
        offset_x = random.randint(-3, 3)
        offset_y = random.randint(-3, 3)
        
        self.click_position(x + offset_x, y + offset_y)
    
    def close(self):
        self.mouse.disconnect()

# Usage
game = GameAutomation(find_arduino_port() or "COM6")

# Click button at (500, 300)
game.human_like_click(500, 300)

# Drag item from (400, 400) to (600, 500)
game.drag_to(600, 500, duration=0.8)

game.close()
```


---

## 🐛 Troubleshooting

### Problem: Arduino Not Detected

**Symptoms:**
- Device Manager shows "Unknown Device"
- No COM port appears

**Solutions:**

1. **Check USB Cable**
   - Use data cable (not charge-only)
   - Try different USB port
   - Try different cable

2. **Install Drivers**
   ```bash
   # Windows will usually auto-install
   # If not, download from arduino.cc
   ```

3. **Check Device Manager**
   - Look for "Arduino Leonardo" or "USB Serial Device"
   - If yellow warning, update driver

### Problem: Wrong VID/PID After Spoofing

**Symptoms:**
- Still shows VID:2341, PID:8036 (Arduino default)
- Logitech not detected

**Solutions:**

1. **Re-run spoofing script**
   ```bash
   spoof_usb_leonardo.bat
   ```

2. **Restart Arduino IDE**
   - Must restart for boards.txt changes

3. **Re-upload firmware**
   - Upload sketch again after spoofing

4. **Verify boards.txt**
   ```
   Location: %LOCALAPPDATA%\Arduino15\packages\arduino\hardware\avr\[version]\boards.txt
   
   Check for:
   leonardo.build.vid=0x046D
   leonardo.build.pid=0xC07D
   leonardo.build.usb_manufacturer="Logitech"
   leonardo.build.usb_product="G Pro X Superlight"
   ```


### Problem: Serial Connection Fails

**Symptoms:**
- Python script can't connect
- "Port already in use" error
- Timeout errors

**Solutions:**

1. **Close other programs**
   - Arduino IDE Serial Monitor
   - PuTTY, RealTerm, or other serial tools
   - Previous Python scripts

2. **Check COM port**
   ```python
   import serial.tools.list_ports
   
   ports = list(serial.tools.list_ports.comports())
   for port in ports:
       print(f"{port.device}: {port.description}")
   ```

3. **Reset Arduino**
   - Unplug USB
   - Wait 5 seconds
   - Plug back in

4. **Increase timeout**
   ```python
   serial.Serial(port, 115200, timeout=3)  # Increase from 1 to 3
   ```

### Problem: Mouse Movement Not Smooth

**Symptoms:**
- Jerky or stuttering movement
- Cursor jumps
- Inconsistent speed

**Solutions:**

1. **Adjust DPI multiplier**
   ```python
   mouse.dpi_multiplier = 1.5  # Try different values
   ```

2. **Increase Bezier steps**
   ```python
   steps = max(15, int(dist / 20))  # More steps = smoother
   ```

3. **Add micro delays**
   ```python
   time.sleep(0.005)  # 5ms between movements
   ```

4. **Check system performance**
   - Close resource-heavy programs
   - Reduce background processes
   - Check CPU usage


### Problem: Mouse Not Moving Accurately

**Symptoms:**
- Cursor doesn't reach target position
- Off by several pixels
- Drifting over time

**Solutions:**

1. **Reset accumulators periodically**
   ```python
   mouse.reset_accumulators()
   ```

2. **Verify actual position**
   ```python
   import pyautogui
   
   # After move
   actual = pyautogui.position()
   if abs(actual[0] - target_x) > 5:
       # Adjust
       mouse.move_relative(target_x - actual[0], 0)
   ```

3. **Calibrate DPI scale**
   ```python
   # Test by moving known distance
   mouse.move_relative(100, 0)
   # Measure actual movement and adjust DPI_SCALE
   ```

### Problem: Anti-Cheat Detection

**Symptoms:**
- Game detects automation
- Account warnings
- Mouse blocked

**Prevention:**

1. **Add randomization**
   ```python
   # Random delays
   time.sleep(random.uniform(0.1, 0.3))
   
   # Random click positions
   offset = random.randint(-5, 5)
   ```

2. **Human-like patterns**
   - Use Bezier curves (not straight lines)
   - Variable speed
   - Occasional overshoots
   - Micro tremors

3. **Verify USB spoofing**
   - Must show Logitech VID/PID
   - Run verification script regularly

4. **Limit usage**
   - Don't run 24/7
   - Add breaks
   - Vary timing

---


## 📊 Performance Optimization

### High-Speed Movement

For faster movement without sacrificing smoothness:

```python
def fast_move(mouse, target_x, target_y, current_x, current_y):
    """Optimized for speed while maintaining smoothness"""
    dist = math.hypot(target_x - current_x, target_y - current_y)
    
    # Fewer steps for long distances
    if dist > 500:
        steps = 10
    elif dist > 200:
        steps = 15
    else:
        steps = 20
    
    waypoints = mouse.get_bezier_points(
        (current_x, current_y),
        (target_x, target_y),
        steps=steps
    )
    
    prev = (current_x, current_y)
    for wx, wy in waypoints[1:]:
        dx = wx - prev[0]
        dy = wy - prev[1]
        mouse.move_relative(dx, dy)
        time.sleep(0.002)  # 2ms - faster
        prev = (wx, wy)
```

### Batch Commands (Advanced)

For even higher performance, send multiple commands at once:

```cpp
// Arduino firmware modification
else if (command.startsWith("B,")) {
  // Batch: B,dx1,dy1,dx2,dy2,dx3,dy3
  // Parse and execute multiple moves
  int idx = 2;
  while (idx < command.length()) {
    int comma = command.indexOf(',', idx);
    if (comma == -1) break;
    
    int dx = command.substring(idx, comma).toInt();
    idx = comma + 1;
    
    comma = command.indexOf(',', idx);
    int dy = comma == -1 ? 
      command.substring(idx).toInt() : 
      command.substring(idx, comma).toInt();
    
    Mouse.move(constrain(dx, -127, 127), 
               constrain(dy, -127, 127), 0);
    
    if (comma == -1) break;
    idx = comma + 1;
  }
  Serial.println("OK");
}
```


---

## 🎓 Advanced Features

### Multi-Button Support

Add right-click and middle-click support:

**Arduino Code:**
```cpp
else if (command == "DR") {
  Mouse.press(MOUSE_RIGHT);
}
else if (command == "UR") {
  Mouse.release(MOUSE_RIGHT);
}
else if (command == "DM") {
  Mouse.press(MOUSE_MIDDLE);
}
else if (command == "UM") {
  Mouse.release(MOUSE_MIDDLE);
}
```

**Python Code:**
```python
def right_click(self):
    self._send_command("DR")
    time.sleep(0.05)
    self._send_command("UR")

def middle_click(self):
    self._send_command("DM")
    time.sleep(0.05)
    self._send_command("UM")
```

### Mouse Wheel Support

**Arduino Code:**
```cpp
else if (command.startsWith("W,")) {
  // Wheel: W,amount (negative = up, positive = down)
  int amount = command.substring(2).toInt();
  Mouse.move(0, 0, amount);
  Serial.println("OK");
}
```

**Python Code:**
```python
def scroll(self, amount: int):
    """Scroll wheel (negative=up, positive=down)"""
    return self._send_command(f"W,{amount}")
```


### Macro Recording and Playback

```python
class MouseMacro:
    """Record and playback mouse actions"""
    
    def __init__(self, mouse: HighPrecisionArduinoMouse):
        self.mouse = mouse
        self.actions = []
    
    def record_move(self, x, y):
        self.actions.append(('move', x, y, time.time()))
    
    def record_click(self):
        self.actions.append(('click', time.time()))
    
    def record_delay(self, seconds):
        self.actions.append(('delay', seconds))
    
    def playback(self, speed_multiplier=1.0):
        """Play recorded actions"""
        if not self.actions:
            return
        
        import pyautogui
        start_time = self.actions[0][-1]
        
        for action in self.actions:
            if action[0] == 'move':
                _, x, y, timestamp = action
                current = pyautogui.position()
                self.mouse.move_to_smooth(x, y, current[0], current[1])
                
            elif action[0] == 'click':
                self.mouse.click()
                
            elif action[0] == 'delay':
                time.sleep(action[1] / speed_multiplier)
    
    def save(self, filename):
        """Save macro to file"""
        import json
        with open(filename, 'w') as f:
            json.dump(self.actions, f)
    
    def load(self, filename):
        """Load macro from file"""
        import json
        with open(filename, 'r') as f:
            self.actions = json.load(f)

# Usage
macro = MouseMacro(mouse)
macro.record_move(500, 300)
macro.record_click()
macro.record_delay(1.0)
macro.record_move(600, 400)
macro.record_click()

# Save and load
macro.save("my_macro.json")
macro.load("my_macro.json")
macro.playback(speed_multiplier=1.5)
```


---

## 📦 Quick Start Template

Copy this complete working example to get started immediately:

```python
"""
Quick Start Template
Complete Arduino Mouse Setup
"""

import time
import math
import random
import serial
import serial.tools.list_ports
import pyautogui
from typing import Optional, Tuple, List


class ArduinoMouse:
    """Simple high-precision Arduino mouse controller"""
    
    def __init__(self):
        self.serial = None
        self.port = None
    
    def connect(self, port: str, baud: int = 115200) -> bool:
        try:
            self.serial = serial.Serial(port, baud, timeout=1)
            self.port = port
            time.sleep(2)
            self.serial.reset_input_buffer()
            print(f"✅ Connected to {port}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.serial:
            self.serial.close()
            self.serial = None
    
    def move(self, dx: int, dy: int):
        if self.serial:
            self.serial.write(f"M,{dx},{dy}\n".encode())
            self.serial.readline()
    
    def click(self):
        if self.serial:
            self.serial.write(b"D\n")
            time.sleep(0.05)
            self.serial.write(b"U\n")
            time.sleep(0.05)
    
    def move_to(self, x: int, y: int):
        """Move to absolute position with smooth curve"""
        current = pyautogui.position()
        dx = x - current[0]
        dy = y - current[1]
        dist = math.hypot(dx, dy)
        
        if dist < 10:
            self.move(dx, dy)
            return
        
        # Simple Bezier curve
        steps = max(10, int(dist / 30))
        for i in range(steps + 1):
            t = i / steps
            px = current[0] + dx * t
            py = current[1] + dy * t
            
            if i > 0:
                step_x = int(px - prev_x)
                step_y = int(py - prev_y)
                self.move(step_x, step_y)
                time.sleep(0.005)
            
            prev_x, prev_y = px, py


def find_port() -> Optional[str]:
    """Find Arduino COM port"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if any(kw in p.description.lower() 
               for kw in ['arduino', 'leonardo', 'ch340']):
            return p.device
    return None


# === MAIN USAGE ===
if __name__ == "__main__":
    # Auto-find or manual port
    port = find_port() or input("Enter COM port: ")
    
    # Connect
    mouse = ArduinoMouse()
    if not mouse.connect(port):
        exit(1)
    
    try:
        # Example: Move and click
        print("Moving to (500, 300)...")
        mouse.move_to(500, 300)
        time.sleep(0.5)
        
        print("Clicking...")
        mouse.click()
        time.sleep(1)
        
        print("Done!")
        
    finally:
        mouse.disconnect()
```

Save as `quick_start.py` and run immediately!


---

## 🔑 Key Takeaways

### What You Need

1. **Hardware**: Arduino Leonardo or Pro Micro (ATmega32U4)
2. **Software**: Arduino IDE + Python with pyserial
3. **Setup**: USB spoofing script (one-time)
4. **Firmware**: Arduino sketch with Mouse.h
5. **Python**: Control code with serial communication

### Critical Success Factors

✅ **USB Spoofing**
- VID must be `046D` (Logitech)
- PID must be `C07D` (G Pro X Superlight)
- Verify with Device Manager or Python script

✅ **Smooth Movement**
- Use Bezier curves (not straight lines)
- Add randomization and jitter
- Variable speed and delays

✅ **Precision**
- Sub-pixel accumulation
- DPI scaling (1.2x for DPI 1200)
- Position verification

✅ **Human-Like Behavior**
- Random delays (40-90ms)
- Acceleration/deceleration
- Occasional overshoots
- Micro tremors

### Common Pitfalls

❌ **Straight line movement** → Use Bezier curves
❌ **Constant speed** → Add variation
❌ **Perfect positioning** → Add small random offsets
❌ **Instant clicks** → Add human-like delays
❌ **Forgetting to spoof** → Always verify VID/PID

---

## 📚 Reference

### Serial Command Protocol

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| Move | `M,dx,dy` | Relative move | `M,10,-5` |
| Smooth | `S,dx,dy,steps` | Multi-step move | `S,100,50,20` |
| Down | `D` | Press button | `D` |
| Up | `U` | Release button | `U` |
| Reset | `R` | Reset accumulators | `R` |
| Wheel | `W,amount` | Scroll wheel | `W,-3` |

### USB Descriptor Values

| Property | Logitech | Arduino Default |
|----------|----------|-----------------|
| VID | `0x046D` | `0x2341` |
| PID | `0xC07D` | `0x8036` |
| Manufacturer | Logitech | Arduino LLC |
| Product | G Pro X Superlight | Arduino Leonardo |


### DPI Scaling Reference

| DPI | Scale Factor | Use Case |
|-----|--------------|----------|
| 800 | 0.8 | Low sensitivity games |
| 1200 | 1.0-1.2 | Standard gaming (recommended) |
| 1600 | 1.4-1.6 | High sensitivity |
| 3200 | 2.5-3.0 | Professional gaming |

### Timing Guidelines

| Action | Min (ms) | Max (ms) | Purpose |
|--------|----------|----------|---------|
| Click press | 40 | 90 | Human click duration |
| Click release | 30 | 70 | After-click delay |
| Move step | 2 | 8 | Between movements |
| Reaction time | 100 | 300 | Human reaction |
| Read delay | 180 | 220 | After reading text |

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] USB descriptor spoofed (VID:046D, PID:C07D)
- [ ] Arduino firmware uploaded and tested
- [ ] Connection verification script passes
- [ ] Movement smoothness validated
- [ ] Click timing feels natural
- [ ] Position accuracy within 2-3 pixels
- [ ] Anti-detection features enabled
- [ ] Error handling implemented
- [ ] Logging and monitoring set up
- [ ] Backup and restore scripts ready

---

## 💬 FAQ

**Q: Can I use this with other mice?**
A: Yes! Change VID/PID in boards.txt to any mouse model. Popular choices:
- Razer DeathAdder: VID:1532, PID:0037
- SteelSeries Rival: VID:1038, PID:1384

**Q: Does this work on Mac/Linux?**
A: USB spoofing scripts are Windows-specific. For Mac/Linux, manually edit boards.txt in Arduino packages directory.

**Q: What's the maximum movement speed?**
A: Arduino Mouse.move() limit is ±127 pixels per call. For faster movement, call multiple times with small delays.

**Q: Can games detect this?**
A: With proper USB spoofing and human-like behavior, detection is minimal. Always verify VID/PID before use.

**Q: How to restore original Arduino?**
A: Run `restore_usb_leonardo.bat` or restore backup of boards.txt

**Q: Why use Arduino instead of software?**
A: Hardware mouse sends USB HID events that are harder to detect than software automation.


---

## 📖 Additional Resources

### Official Documentation
- Arduino Mouse Library: https://www.arduino.cc/reference/en/language/functions/usb/mouse/
- Arduino Leonardo: https://docs.arduino.cc/hardware/leonardo
- USB HID Spec: https://www.usb.org/hid

### Community Resources
- Arduino Forums: https://forum.arduino.cc/
- Reddit r/arduino: https://reddit.com/r/arduino
- Stack Overflow Arduino: https://stackoverflow.com/questions/tagged/arduino

### Tools
- Arduino IDE: https://www.arduino.cc/en/software
- Python pyserial: `pip install pyserial`
- Device Manager: Built into Windows

---

## 📝 License & Disclaimer

**Educational Purpose Only**

This solution is provided for educational and research purposes. Users are responsible for:
- Complying with Terms of Service of games/applications
- Following local laws and regulations
- Using ethically and responsibly

**No Warranty**

This code is provided "as-is" without warranty. Use at your own risk.

**Anti-Cheat Warning**

While USB spoofing reduces detection, no method is 100% undetectable. Always:
- Test in safe environments first
- Understand risks before production use
- Follow game/application policies

---

## 🎯 Summary

You now have a complete solution for:

✅ USB descriptor spoofing (Arduino → Logitech)
✅ High-precision mouse control (DPI 1200)
✅ Smooth Bezier curve movement
✅ Human-like behavior patterns
✅ Python integration with examples
✅ Troubleshooting and optimization

**Next Steps:**
1. Run `spoof_usb_leonardo.bat`
2. Upload Arduino firmware
3. Verify with `verify_connection.py`
4. Test with `quick_start.py`
5. Integrate into your project

**Happy coding! 🚀**

---

*Document Version: 1.0*  
*Last Updated: 2026-07-16*  
*Compatible with: Arduino Leonardo, Pro Micro, ESP32-S2/S3*
