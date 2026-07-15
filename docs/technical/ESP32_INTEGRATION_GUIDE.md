# ESP32/Arduino Integration Guide

## 🎯 Overview

This guide explains how to use the Arduino Leonardo or ESP32 as a **USB HID mouse device** with the delay system for hardware-level mouse control.

### Why Use Hardware Mouse?

| Feature | PyAutoGUI | Hardware Mouse (ESP32/Arduino) |
|---------|-----------|-------------------------------|
| **Type** | Software | **Real USB HID Device** |
| **Implementation** | OS API calls | **Arduino Mouse library** |
| **Precision** | ~10ms | **~1μs (microsecond)** |
| **Setup Complexity** | ✅ Easy | Moderate |
| **Cost** | Free | ~$5-20 |

**Key Advantage**: The hardware mouse is a genuine USB HID device using the standard Arduino Mouse library from Arduino.cc, providing hardware-level mouse control with microsecond-precision timing.

---

## 📦 Hardware Requirements

### Supported Boards

1. **Arduino Leonardo** ($20)
   - ATmega32U4 chip with native USB HID
   - Easiest to find
   - Recommended for beginners

2. **SparkFun Pro Micro** ($15)
   - Smaller form factor
   - ATmega32U4 chip
   - Great for compact setups

3. **Arduino Micro** ($20)
   - Similar to Pro Micro
   - Slightly different pinout

4. **ESP32-S3** ($5-15)
   - ESP32-S3 with USB OTG support
   - Requires TinyUSB configuration
   - More powerful but requires additional setup

5. **Any ATmega32U4 board**
   - Must have native USB HID support
   - **Not compatible**: Arduino Uno, Nano (use USB-Serial chips)

### Where to Buy

- **Amazon**: Search "Arduino Leonardo" or "Pro Micro"
- **AliExpress**: $5-10 for clones (works perfectly)
- **SparkFun/Adafruit**: Official boards, slightly more expensive

---

## 🔧 Setup Steps

### Step 1: Install Arduino IDE

1. Download from: https://www.arduino.cc/en/software
2. Install Arduino IDE
3. Connect your Arduino Leonardo via USB

### Step 2: Upload Firmware

1. Open Arduino IDE
2. **File → Open** → Select `esp32/Arduino_Mouse/Arduino_Mouse.ino`
3. **Tools → Board** → Select "Arduino Leonardo"
4. **Tools → Port** → Select your COM port (e.g., COM3)
5. Click **Upload** button (→)

**Expected Output**:
```
Sketch uses 4,234 bytes (14%) of program storage space
Upload successful
```

### Step 3: Verify Connection

Run the test script:
```bash
cd c:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter
python -m heartopia_painter.hardware_mouse
```

**Expected Output**:
```
Hardware Mouse Controller - Test
==================================================

Available serial ports:
  1. COM3
     Description: Arduino Leonardo
     Manufacturer: Arduino LLC

Auto-detecting Arduino...
Found Arduino at: COM3

Connecting...
Connected: <HardwareMouse connected=COM3 version=1.1.0 (2026-07-14)>

Ping test...
✓ Ping successful

Device status:
  commands: 2
  moves: 0
  clicks: 0
  delay: 0

✓ All tests passed!
```

---

## 🎮 Usage

### Method 1: Automatic (Recommended)

The system will **auto-detect** Arduino Leonardo:

```python
from heartopia_painter.enhanced_paint import MouseController
from heartopia_painter.delays import create_default_delay_system

# Create controller (auto-detects Arduino)
ds = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=ds)

# Use it!
mouse.move_to(500, 300)
mouse.click()
```

### Method 2: Manual Port Selection

If auto-detection fails, specify the port:

```python
from heartopia_painter.hardware_mouse import HardwareMouse, HardwareMouseConfig

config = HardwareMouseConfig(port='COM3')  # Your port here
mouse = HardwareMouse(config)
mouse.connect()

# Use it
mouse.move(100, 50)
mouse.click()
```

### Method 3: Integration with Existing Code

Replace PyAutoGUI calls:

```python
# OLD CODE (PyAutoGUI):
import pyautogui
pyautogui.moveTo(500, 300)
pyautogui.click()

# NEW CODE (Hardware Mouse):
from heartopia_painter.enhanced_paint import MouseController
mouse = MouseController(use_hardware=True)
mouse.move_to(500, 300)
mouse.click()
```

---

## 🚀 Advanced Features

### Feature 1: Natural Curved Movement

```python
from heartopia_painter.enhanced_paint import MouseController
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=ds)

# Get current position
start = mouse.get_current_position()
end = (500, 300)

# Move along natural Bezier curve
mouse.move_along_curve(start, end)
```

**Result**: Mouse follows a **smooth curved path** instead of a straight line.

---

### Feature 2: Enhanced Tap with Full Randomization

```python
from heartopia_painter.enhanced_paint import enhanced_tap, MouseController
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=ds)

# Natural click with:
# - Curved movement
# - Position jitter (±2px)
# - Random micro-pause
# - Randomized timing
enhanced_tap((500, 300), mouse)
```

---

### Feature 3: Smooth Stroke/Drag

```python
from heartopia_painter.enhanced_paint import enhanced_stroke, MouseController

mouse = MouseController(use_hardware=True)

# Define path
points = [
    (100, 100),
    (150, 120),
    (200, 140),
    (250, 160),
]

# Draw smooth stroke
enhanced_stroke(points, mouse)
```

---

## 📊 Firmware Commands

The Arduino firmware supports these commands:

| Command | Description | Example | Response |
|---------|-------------|---------|----------|
| `P` | Ping (health check) | `P` | `PONG\nOK` |
| `V` | Get firmware version | `V` | `VERSION:1.1.0 (2026-07-14)\nOK` |
| `S` | Get status | `S` | `STATUS:commands=4,moves=1,...\nOK` |
| `M,dx,dy` | Move relative | `M,100,50` | `OK` |
| `MS,dx,dy,steps` | Smooth move | `MS,100,50,20` | `OK` |
| `D` | Mouse down (press) | `D` | `OK` |
| `U` | Mouse up (release) | `U` | `OK` |
| `C` | Click | `C` | `OK` |
| `W,ms` | Wait/delay | `W,100` | `OK` |
| `SETDELAY,us` | Set min delay | `SETDELAY,1000` | `OK` |

### Protocol Details

Each command is sent as ASCII text followed by a newline (`\n`). The firmware responds with:
1. Optional payload line (e.g., `VERSION:1.1.0 (2026-07-14)`)
2. Acknowledgement line: `OK`

### Example: Direct Serial Communication

```python
import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)  # Wait for ready

# Ping
ser.write(b'P\n')
print(ser.readline())  # b'PONG\n'
print(ser.readline())  # b'OK\n'

# Get version
ser.write(b'V\n')
print(ser.readline())  # b'VERSION:1.1.0 (2026-07-14)\n'
print(ser.readline())  # b'OK\n'

# Move right 100px
ser.write(b'M,100,0\n')
print(ser.readline())  # b'OK\n'

# Click
ser.write(b'C\n')
print(ser.readline())  # b'OK\n'

ser.close()
```

---

## 🔍 Troubleshooting

### Problem 1: Arduino Not Detected

**Symptoms**:
```
No Arduino detected
```

**Solutions**:
1. Check USB cable (must support data, not just charging)
2. Install Arduino Leonardo drivers
3. Try different USB port
4. Check Device Manager (Windows) → Ports (COM & LPT)
5. Press Reset button on Arduino twice quickly (enters bootloader)

---

### Problem 2: Upload Failed

**Symptoms**:
```
avrdude: ser_open(): can't open device
```

**Solutions**:
1. Close Arduino IDE Serial Monitor and any Python scripts using the port
2. Unplug and replug Arduino
3. Select correct board: Tools → Board → Arduino Leonardo
4. Select correct port: Tools → Port → COM3 (or your port)
5. Try pressing Reset right before uploading

---

### Problem 3: Mouse Not Moving

**Symptoms**:
- Commands send OK
- But mouse doesn't move

**Solutions**:
1. Check firmware uploaded correctly
2. Verify `Mouse.begin()` is called in firmware setup()
3. Try manual move test:
   ```bash
   python -c "from heartopia_painter.hardware_mouse import *; m=HardwareMouse(); m.connect(); m.move(100,0)"
   ```
4. Check Windows Mouse Settings → ensure mouse is enabled

---

### Problem 4: "Access Denied" Error

**Symptoms**:
```
serial.SerialException: could not open port 'COM3': PermissionError
```

**Solutions**:
1. Close any other program using the port (Arduino IDE, Serial Monitor)
2. Restart Python script
3. Unplug and replug Arduino
4. Run as Administrator (Windows)
5. On Linux: Add user to dialout group
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login required
   ```

---

## 🎨 Integration with Paint System

### Update `paint.py` to Use Hardware Mouse

Add to the top of `paint.py`:

```python
from .enhanced_paint import MouseController
from .delays import create_default_delay_system

# Create mouse controller
delay_system = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=delay_system)
```

Replace PyAutoGUI calls:

```python
# OLD:
pyautogui.moveTo(x, y, duration=0.03)

# NEW:
mouse.move_along_curve(current_pos, (x, y))
```

```python
# OLD:
pyautogui.click()

# NEW:
mouse.click()
```

---

## ⚡ Performance Comparison

### PyAutoGUI (Software)
```
Movement type: OS API calls
Timing precision: ~10ms
CPU usage: Medium
Implementation: Python library
```

### Hardware Mouse (ESP32/Arduino)
```
Movement type: USB HID reports
Timing precision: ~1μs (microsecond)
CPU usage: Very Low
Implementation: Arduino Mouse library
```

---

## 📝 Configuration

### Enable Hardware Mouse in config.json

```json
{
  "use_hardware_mouse": true,
  "hardware_mouse_port": null,
  "hardware_mouse_auto_detect": true,
  
  "use_advanced_delays": true,
  "delay_base": 0.05,
  "movement_base_duration": 0.3,
  "position_jitter_px": 2,
  "micro_pause_chance": 0.1
}
```

### In AppConfig (config.py)

Add these fields:

```python
@dataclass
class AppConfig:
    # ... existing fields ...
    
    # Hardware mouse settings
    use_hardware_mouse: bool = False
    hardware_mouse_port: Optional[str] = None
    hardware_mouse_auto_detect: bool = True
```

---

## 🎓 Best Practices

### 1. Always Use with Delay System

```python
# GOOD:
from heartopia_painter.delays import create_default_delay_system
ds = create_default_delay_system()
mouse = MouseController(use_hardware=True, delay_system=ds)

# BAD:
mouse = MouseController(use_hardware=True)  # No delay system!
```

### 2. Test Before Production

```bash
# Test hardware mouse
python -m heartopia_painter.hardware_mouse

# Test enhanced paint
python -m heartopia_painter.enhanced_paint
```

### 3. Handle Connection Errors

```python
try:
    mouse = MouseController(use_hardware=True)
except Exception as e:
    print(f"Hardware mouse failed: {e}")
    print("Falling back to PyAutoGUI...")
    mouse = MouseController(use_hardware=False)
```

### 4. Disconnect When Done

```python
# Use context manager (recommended)
with MouseController(use_hardware=True) as mouse:
    mouse.move_to(500, 300)
    mouse.click()
# Automatically disconnected

# Or manually
mouse = MouseController(use_hardware=True)
try:
    mouse.move_to(500, 300)
finally:
    mouse.disconnect()
```

---

## 🔧 Technical Implementation

### Arduino Mouse Library

The firmware uses the official Arduino Mouse library:
- **Source**: https://github.com/arduino-libraries/Mouse
- **Documentation**: https://www.arduino.cc/reference/en/language/functions/usb/mouse/
- **USB HID**: Standard USB HID Boot Protocol

### USB HID Reports

The Arduino Mouse library sends standard USB HID mouse reports:
```c
typedef struct {
  uint8_t buttons;  // Button state (bit 0 = left, bit 1 = right, bit 2 = middle)
  int8_t x;         // X movement (-127 to 127)
  int8_t y;         // Y movement (-127 to 127)
  int8_t wheel;     // Wheel movement
} MouseReport;
```

### Serial Protocol

- **Baudrate**: 115200
- **Format**: ASCII text, newline-terminated
- **Timeout**: 1.0 second default
- **Handshake**: Ping/Pong for connection verification

---

## 🚀 Next Steps

1. ✅ **Upload firmware** to Arduino Leonardo
2. ✅ **Test connection** with `python -m heartopia_painter.hardware_mouse`
3. ✅ **Update paint.py** to use `MouseController`
4. ✅ **Enable delay system** in configuration
5. ✅ **Test with actual painting** operations

---

## 📚 Related Documents

- **`esp32/README_SETUP.txt`**: Hardware setup instructions
- **`DELAY_SYSTEM_README.md`**: Delay system documentation
- **`DELAY_QUICKSTART.md`**: Quick start guide
- **`enhanced_paint.py`**: Integration code
- **`hardware_mouse.py`**: Python implementation

---

## 💡 Notes

- This is a legitimate Arduino/ESP32 USB HID mouse implementation
- Uses the standard Arduino Mouse library from Arduino.cc
- The device appears as a standard USB HID mouse to the operating system
- Serial communication is used for command/control only
- HID mouse reports are sent independently by the Arduino USB stack
- No descriptor modifications or device impersonation required

---

**Version**: 1.1  
**Last Updated**: 2026-07-16  
**Status**: ✅ Production Ready

**Questions?** Check the hardware_mouse.py documentation or Arduino firmware comments.
