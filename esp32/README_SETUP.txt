===========================================
Arduino/ESP32 Hardware Mouse Setup Guide
===========================================

This guide explains how to set up an Arduino Leonardo or ESP32 board
as a USB HID mouse device for use with Heartopia Auto Painter.

===========================================
Supported Hardware
===========================================

Compatible Boards:
- Arduino Leonardo (ATmega32U4)
- SparkFun Pro Micro (ATmega32U4)
- Arduino Micro (ATmega32U4)
- ESP32-S3 with USB OTG support
- ESP32-S2 with USB OTG support

Requirements:
- Board must have native USB HID support
- NOT compatible with Arduino Uno/Nano (they use USB-to-Serial chips)

===========================================
Setup Instructions - Arduino Leonardo
===========================================

Step 1: Install Arduino IDE
----------------------------
1. Download Arduino IDE from: https://www.arduino.cc/en/software
2. Install the software
3. Connect your Arduino Leonardo via USB cable

Step 2: Upload Firmware
------------------------
1. Open Arduino IDE
2. File → Open → Navigate to: esp32/Arduino_Mouse/Arduino_Mouse.ino
3. Tools → Board → Select "Arduino Leonardo"
4. Tools → Port → Select your COM port (e.g., COM3, COM4)
   - Windows: Check Device Manager → Ports (COM & LPT)
   - Linux: Usually /dev/ttyACM0 or /dev/ttyUSB0
   - macOS: Usually /dev/cu.usbmodem*
5. Click Upload button (→)
6. Wait for "Upload successful" message

Step 3: Verify Connection
--------------------------
Run the diagnostic test:

    python -m heartopia_painter.hardware_mouse

Expected output:
    Available serial ports:
      1. COM3
         Description: Arduino Leonardo
         Manufacturer: Arduino LLC
    
    Auto-detecting Arduino...
    Found Arduino at: COM3
    
    Connecting...
    Connected: <HardwareMouse connected=COM3 version=1.1.0>
    Version: 1.1.0 (2026-07-14)
    
    ✓ All tests passed!

===========================================
Setup Instructions - ESP32-S3/S2
===========================================

Step 1: Install ESP32 Board Support
------------------------------------
Run the installation script:

    cd esp32
    install_esp32.bat    (Windows)
    ./install_esp32.sh   (Linux/macOS)

Or manually in Arduino IDE:
1. File → Preferences
2. Additional Board Manager URLs:
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
3. Tools → Board → Boards Manager
4. Search "esp32" and install "esp32 by Espressif Systems"

Step 2: Configure Arduino IDE
------------------------------
1. Tools → Board → ESP32 Arduino → ESP32S3 Dev Module
2. Tools → USB Mode → USB-OTG (TinyUSB)
3. Tools → USB CDC On Boot → Disabled
4. Tools → Port → Select your COM port

Step 3: Upload Firmware
------------------------
1. Open: esp32/Arduino_Mouse/Arduino_Mouse.ino
2. Click Upload button (→)
3. Wait for upload to complete

Step 4: Verify in Device Manager (Windows)
-------------------------------------------
1. Open Device Manager
2. Expand "Human Interface Devices"
3. Look for "USB Input Device" or "HID-compliant mouse"
4. Expand "Ports (COM & LPT)"
5. Note the COM port number

===========================================
Protocol Commands
===========================================

The firmware responds to these serial commands:

Command Format         Description              Response
-------------         -----------              --------
P                     Ping (health check)      PONG\nOK
V                     Get firmware version     VERSION:1.1.0 (2026-07-14)\nOK
S                     Get status               STATUS:commands=N,moves=N,...\nOK
M,dx,dy               Move by dx,dy pixels     OK
MS,dx,dy,steps        Smooth move in steps     OK
D                     Press left button        OK
U                     Release left button      OK
C                     Click (press+release)    OK
W,ms                  Wait milliseconds        OK
SETDELAY,us           Set min delay (μs)       OK

Example Communication:
    Send: P\n
    Receive: PONG\n
    Receive: OK\n
    
    Send: M,100,50\n
    Receive: OK\n
    
    Send: V\n
    Receive: VERSION:1.1.0 (2026-07-14)\n
    Receive: OK\n

===========================================
Troubleshooting
===========================================

Problem: Arduino not detected
------------------------------
Solutions:
1. Check USB cable supports data transfer (not charge-only)
2. Try a different USB port
3. Install/update Arduino Leonardo drivers
4. Press Reset button on Arduino twice quickly (bootloader mode)
5. Check Device Manager (Windows) for the COM port

Problem: Upload failed - "can't open device"
---------------------------------------------
Solutions:
1. Close all programs using the serial port:
   - Arduino IDE Serial Monitor
   - Python scripts
   - Other terminal programs
2. Unplug and replug the Arduino
3. Select correct board in Tools → Board
4. Select correct port in Tools → Port
5. Try pressing Reset right before clicking Upload

Problem: Python can't find the device
--------------------------------------
Solutions:
1. Verify COM port in Device Manager
2. Check that firmware uploaded successfully
3. Try unplugging and replugging the Arduino
4. Run diagnostic: python -m heartopia_painter.hardware_mouse
5. Manually specify port in config:
   {
     "hardware_mouse_port": "COM3"
   }

Problem: Mouse doesn't move
----------------------------
Solutions:
1. Verify firmware uploaded correctly
2. Check Serial Monitor for error messages
3. Ensure Mouse.begin() is called in setup()
4. Test with simple command:
   python -c "from heartopia_painter.hardware_mouse import *; m=HardwareMouse(); m.connect(); m.move(100,0)"

Problem: "Access Denied" or "Permission Error"
-----------------------------------------------
Solutions:
1. Close Arduino IDE and Serial Monitor
2. Close any Python scripts using the port
3. Unplug and replug the device
4. On Linux: Add user to dialout group:
   sudo usermod -a -G dialout $USER
   (logout and login required)
5. On Windows: Run as Administrator (if needed)

Problem: ESP32 upload fails
----------------------------
Solutions:
1. Hold BOOT button while connecting USB
2. Press BOOT + RESET, release RESET, then release BOOT
3. Check USB cable (must support data)
4. Try lower upload speed: Tools → Upload Speed → 115200

===========================================
Using with Heartopia Auto Painter
===========================================

Method 1: Auto-detection (Recommended)
---------------------------------------
The software will automatically detect your Arduino/ESP32:

1. Start Heartopia Auto Painter
2. Enable "Use Hardware Mouse ESP32/Arduino" checkbox
3. Leave port field empty for auto-detection
4. Click Start Painting

Method 2: Manual Port Selection
--------------------------------
If auto-detection doesn't work:

1. Check COM port in Device Manager
2. Enable "Use Hardware Mouse ESP32/Arduino"
3. Enter port (e.g., "COM3") in the port field
4. Click Start Painting

Method 3: Configuration File
-----------------------------
Edit config.json:

{
  "use_hardware_mouse": true,
  "hardware_mouse_port": "COM3",
  "hardware_mouse_auto_detect": true
}

===========================================
Best Practices
===========================================

1. Always test connection before painting:
   python -m heartopia_painter.hardware_mouse

2. Use with Enhanced Timing for natural movement:
   - Enable "Use Enhanced Timing"
   - Enable "Position Jitter"
   - Enable "Micro Pauses"

3. Handle disconnection gracefully:
   - Software will fallback to PyAutoGUI if hardware fails
   - Health monitoring detects disconnections automatically

4. Don't unplug during operation:
   - Can cause painting to fail mid-operation
   - Let painting complete first

5. Update firmware for bug fixes:
   - Check Arduino_Mouse.ino for version number
   - Re-upload if newer version available

===========================================
Hardware Specifications
===========================================

Arduino Leonardo:
- Microcontroller: ATmega32U4
- Clock Speed: 16 MHz
- USB: Native USB HID support
- Serial Baudrate: 115200
- Latency: ~1-10 ms
- Price: ~$20-30

ESP32-S3:
- Microcontroller: ESP32-S3
- Clock Speed: 240 MHz
- USB: USB OTG with TinyUSB
- Serial Baudrate: 115200
- Latency: ~1-5 ms
- Price: ~$5-15

===========================================
Additional Resources
===========================================

Documentation:
- Technical Guide: docs/technical/ESP32_INTEGRATION_GUIDE.md
- Quick Start: docs/user-guides/QUICKSTART_ENHANCED.md
- Delay System: docs/technical/DELAY_SYSTEM_README.md

Firmware:
- Source: esp32/Arduino_Mouse/Arduino_Mouse.ino
- Version: 1.1.0 (2026-07-14)

Python Module:
- Source: src/heartopia_painter/hardware_mouse.py
- Test: python -m heartopia_painter.hardware_mouse

===========================================
Notes
===========================================

- This is a legitimate Arduino/ESP32 HID device implementation
- The device appears as a standard USB HID mouse to the operating system
- No USB descriptor spoofing or device impersonation is required
- The firmware uses the standard Arduino Mouse library
- Serial communication is used for command/control only
- HID mouse reports are sent independently by the USB stack

For support or questions, refer to the project documentation
or open an issue on the project repository.

Version: 1.1.0
Last Updated: 2026-07-16
