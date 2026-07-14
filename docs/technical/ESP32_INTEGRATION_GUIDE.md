# ESP32/Arduino Integration Guide

## 🎯 Overview

This guide explains how to use the Arduino Leonardo or ESP32 as a **real HID mouse device** with the delay system for undetectable automation.

### Why Use Hardware Mouse?

| Feature | PyAutoGUI | Hardware Mouse (ESP32/Arduino) |
|---------|-----------|-------------------------------|
| **Detection Risk** | Medium-High | **Very Low** |
| **OS Detection** | Software automation | **Real HID device** |
| **Anti-cheat Bypass** | ❌ Can be detected | ✅ **Undetectable** |
| **Setup Complexity** | ✅ Easy | Moderate |
| **Cost** | Free | ~$5-20 |

**Key Advantage**: The hardware mouse appears as a **genuine USB HID device** to the operating system, making it virtually impossible to detect as automation.

---

## 📦 Hardware Requirements

### Supported Boards

1. **Arduino Leonardo** ($20)
   - ATmega32U4 chip with native USB
   - Easiest to find
   - Recommended for beginners

2. **SparkFun Pro Micro** ($15)
   - Smaller form factor
   - ATmega32U4 chip
   - Great for compact setups

3. **Arduino Micro** ($20)
   - Similar to Pro Micro
   - Slightly different pinout

4. **Any ATmega32U4 board**
   - Must have native USB support
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

| Command | Description | Example |
|---------|-------------|---------|
| `M,dx,dy` | Move relative | `M,100,50` |
| `MS,dx,dy,steps` | Smooth move | `MS,100,50,20` |
| `D` | Mouse down (press) | `D` |
| `U` | Mouse up (release) | `U` |
| `C` | Click | `C` |
| `W,ms` | Wait/delay | `W,100` |
| `P` | Ping (health check) | `P` → `PONG` |
| `S` | Get status | `S` → `STATUS:...` |
| `V` | Get version | `V` → `VERSION:1.1.0` |
| `SETDELAY,us` | Set min delay | `SETDELAY,1000` |

### Example: Direct Serial Communication

```python
import serial

ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)  # Wait for ready

# Move right 100px
ser.write(b'M,100,0\n')
response = ser.readline()  # "OK"

# Click
ser.write(b'C\n')
response = ser.readline()  # "OK"

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
1. Close Arduino IDE and Python scripts using the port
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
2. Verify `Mouse.begin()` is called in firmware
3. Try manual move: `python -c "from heartopia_painter.hardware_mouse import *; mouse = HardwareMouse(); mouse.connect(); mouse.move(100, 0)"`
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
Movement detection: ✗ Detectable
Timing precision: ~10ms
CPU usage: Medium
Anti-cheat bypass: ❌ Often detected
```

### Hardware Mouse (ESP32/Arduino)
```
Movement detection: ✅ Undetectable (real HID)
Timing precision: ~1μs (microsecond)
CPU usage: Very Low
Anti-cheat bypass: ✅ Virtually undetectable
```

---

## 🔒 Security & Detection Avoidance

### Why Hardware Mouse is Safer

1. **Real HID Device**: Appears as genuine USB mouse to OS
2. **Kernel-Level**: Operates at hardware level, not software
3. **No Process Injection**: No suspicious processes or hooks
4. **No Memory Patterns**: No detectable automation signatures
5. **Hardware Timing**: Precise timing matches real mouse hardware

### Combined with Delay System

When you combine hardware mouse + delay system:

- ✅ **Hardware-level authenticity** (real HID device)
- ✅ **Human-like timing** (bell curve delays)
- ✅ **Natural movement** (Bezier curves)
- ✅ **Position inaccuracy** (±2px jitter)
- ✅ **Random hesitation** (micro-pauses)

**Result**: Virtually impossible to distinguish from a real human!

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

## 🚀 Next Steps

1. ✅ **Upload firmware** to Arduino Leonardo
2. ✅ **Test connection** with `python -m heartopia_painter.hardware_mouse`
3. ✅ **Update paint.py** to use `MouseController`
4. ✅ **Enable delay system** in configuration
5. ✅ **Test with actual painting** operations

---

## 📚 Related Documents

- **`DELAY_SYSTEM_README.md`**: Delay system documentation
- **`DELAY_QUICKSTART.md`**: Quick start guide
- **`esp32/README_SETUP.txt`**: ESP32 setup instructions
- **`enhanced_paint.py`**: Integration code

---

## 💡 Pro Tips

1. **USB Spoofing**: Modify `boards.txt` to make Arduino appear as a brand-name mouse (Logitech, etc.)
2. **Multiple Devices**: Use multiple Arduinos for mouse + keyboard automation
3. **Physical Button**: Add a physical button to Arduino to pause/resume
4. **LED Indicator**: Add LED to show when automation is active
5. **Wireless**: Use Arduino with Bluetooth for wireless mouse

---

**Version**: 1.0  
**Last Updated**: 2026-07-14  
**Status**: ✅ Production Ready

**Questions?** Check the hardware_mouse.py documentation or Arduino firmware comments.
