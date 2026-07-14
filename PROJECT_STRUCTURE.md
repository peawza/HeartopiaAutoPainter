# 📁 Project Structure

**Heartopia Auto Painter - Enhanced Features**  
โครงสร้างโปรเจกต์อย่างละเอียด

---

## 🗂️ Root Directory

```
HeartopiaAutoPainter/
├── 📄 README.md                        → คู่มือหลัก (Start Here!)
├── 📄 โปรดอ่าน.txt                      → คู่มือภาษาไทย
├── 📄 requirements.txt                 → Python dependencies
├── 📄 main.py                          → Entry point (เริ่มโปรแกรม)
│
├── 📂 src/                             → Source code
├── 📂 docs/                            → 📚 Documentation (14 ไฟล์)
├── 📂 esp32/                           → Arduino/ESP32 firmware
├── 📂 ตั้งค่า/                          → ตัวอย่างค่าแนะนำ
│
├── 🧪 test_delays.py                   → Unit tests (Delay System)
├── 🧪 test_paint_integration.py        → Integration tests
├── 📊 profile_paint_enhanced.py        → Performance profiling
├── 📊 analyze_timing.py                → Timing analysis
│
└── 🔧 build_*.bat/py                   → Build scripts
```

---

## 📂 src/ - Source Code

```
src/heartopia_painter/
├── __init__.py                         → Package init
│
├── 🎨 app.py                           → GUI Application (Main UI)
├── 🎨 paint.py                         → Core painting logic (MAIN)
├── 🎨 enhanced_paint.py                → Enhanced painting (MouseController)
│
├── ⏱️  delays.py                        → Delay System (Bell Curve)
├── 🖱️  hardware_mouse.py                → Hardware Mouse (Arduino/ESP32)
│
├── 📷 capture.py                       → Screen capture
├── 🖼️  image_processing.py             → Image processing
├── 🎯 screen.py                        → Screen detection
├── 🎭 overlay.py                       → Overlay display
│
├── ⚙️  config.py                        → Configuration management
└── 🖥️  hidpi.py                         → HiDPI support
```

### 📝 File Descriptions

#### Core Files (หัวใจของโปรแกรม)
- **app.py** (800+ lines) - GUI หลัก, event handlers, controls
- **paint.py** (1,500+ lines) - วาดภาพ, พร้อม Enhanced Features integration
- **enhanced_paint.py** (800+ lines) - MouseController, Bezier curves, enhanced strokes

#### Enhanced Features (ระบบใหม่)
- **delays.py** (1,000+ lines) - DelaySystem, Bell Curve, timing profiles
- **hardware_mouse.py** (600+ lines) - HardwareMouse, Arduino communication

#### Utilities (ฟังก์ชันช่วย)
- **capture.py** - จับภาพหน้าจอ
- **image_processing.py** - แปลงรูป, resize, quantize colors
- **screen.py** - ตรวจจับ monitor, resolution
- **overlay.py** - แสดง preview overlay
- **config.py** - บันทึก/โหลด configuration
- **hidpi.py** - รองรับ HiDPI/Retina displays

---

## 📚 docs/ - Documentation (จัดระเบียบแล้ว!)

```
docs/
├── 📄 README.md                        → Documentation Index (Start here!)
│
├── 📂 user-guides/                     → 👤 คู่มือผู้ใช้
│   ├── QUICKSTART_ENHANCED.md          → ⭐ เริ่มต้นใช้งาน 3 นาที
│   └── DELAY_QUICKSTART.md             → Delay System 5 นาที
│
├── 📂 technical/                       → 🔧 เอกสารเทคนิค
│   ├── DELAY_SYSTEM_README.md          → Delay System ฉบับเต็ม
│   ├── DELAY_SYSTEM_FLOW_COMPLETE.md   → Flow Diagrams
│   ├── ESP32_INTEGRATION_GUIDE.md      → Setup Arduino/ESP32
│   ├── TECHNICAL_DOCS.md               → เอกสารเทคนิคทั่วไป
│   └── สรุป_ระบบ_Delay_และ_ESP32.md    → สรุปภาษาไทย
│
└── 📂 development/                     → 💻 Developer Docs
    ├── FINAL_INTEGRATION_REPORT.md     → ✅ รายงานสรุปสุดท้าย
    ├── INTEGRATION_PLAN.md             → แผนการ integrate (95%)
    ├── INTEGRATION_ROADMAP.md          → Roadmap
    ├── IMPLEMENTATION_SUMMARY.md       → สรุปการ implement
    ├── COMPLETE_IMPLEMENTATION_REPORT.md → รายงาน 8,500+ บรรทัด
    └── FINAL_CHECKLIST.md              → Checklist
```

### 📖 Documentation Guide

**เริ่มต้น:**
1. อ่าน [docs/README.md](docs/README.md) - Documentation Index
2. อ่าน [docs/user-guides/QUICKSTART_ENHANCED.md](docs/user-guides/QUICKSTART_ENHANCED.md) - Quick Start

**ใช้ Hardware Mouse:**
- [docs/technical/ESP32_INTEGRATION_GUIDE.md](docs/technical/ESP32_INTEGRATION_GUIDE.md)

**เข้าใจเทคนิค:**
- [docs/technical/DELAY_SYSTEM_README.md](docs/technical/DELAY_SYSTEM_README.md)
- [docs/technical/DELAY_SYSTEM_FLOW_COMPLETE.md](docs/technical/DELAY_SYSTEM_FLOW_COMPLETE.md)

**Developer:**
- [docs/development/FINAL_INTEGRATION_REPORT.md](docs/development/FINAL_INTEGRATION_REPORT.md)
- [docs/development/INTEGRATION_PLAN.md](docs/development/INTEGRATION_PLAN.md)

---

## 🔌 esp32/ - Hardware Support

```
esp32/
├── 📂 Arduino_Mouse/                   → Arduino Sketch
│   └── Arduino_Mouse.ino               → Firmware (Leonardo/ESP32)
│
├── 📄 README_SETUP.txt                 → Setup instructions
├── 🔧 install_esp32.bat                → Install ESP32 boards
├── 🔧 upload.bat                       → Upload firmware
├── 🔧 spoof_usb_leonardo.bat           → Spoof USB VID/PID
├── 🔧 restore_usb_leonardo.bat         → Restore original
└── 🔧 check_boards.bat                 → Check installed boards
```

### 🖱️ Hardware Mouse Support

**รองรับ:**
- Arduino Leonardo
- Arduino Micro
- Pro Micro (SparkFun)
- ESP32 (experimental)

**คุณสมบัติ:**
- USB HID Mouse (hardware-level)
- Auto-detection (COM1-COM20)
- Microsecond precision
- Protocol version 1.1.0

---

## 🧪 Tests & Profiling

```
Tests & Analysis:
├── test_delays.py                      → Unit tests (Delay System)
│   └── 10,000 samples                  → Bell Curve verification
│
├── test_paint_integration.py           → Integration tests
│   └── 15+ test cases                  → paint.py integration
│
├── profile_paint_enhanced.py           → Performance profiling
│   └── 5 benchmarks                    → CPU, Memory, Timing
│
├── analyze_timing.py                   → Timing analysis
│   └── Distribution stats              → Mean, Std Dev, etc.
│
└── timing_report.txt                   → Timing report (output)
```

### 🧪 Running Tests

```bash
# Test Delay System
python test_delays.py

# Test paint.py Integration
python test_paint_integration.py

# Test Hardware Mouse (if Arduino connected)
python -m heartopia_painter.hardware_mouse

# Profile Performance
python profile_paint_enhanced.py

# Analyze Timing Distribution
python analyze_timing.py
```

---

## 🎨 ตั้งค่า/ - Configuration Examples

```
ตั้งค่า/
├── image-size.jpg                      → ตัวอย่างขนาดรูป
├── ค่าที่เหมาะสมที่สุดตอนนี้.png        → Recommended settings
├── ค่าวาดแม่นยำ วาดนาน เพี้ยนน้อยมาก.png → Careful mode
└── ค่าวาดไว-สีอาจเพี้ยน ถ้ารูปยาก.png   → Fast mode
```

---

## 🔧 Build Scripts

```
Build Tools:
├── build_painter_tester.bat            → Build tester
├── build_stealth.bat                   → Build with stealth
└── build_stealth.py                    → Build script (Python)
```

---

## 📊 Project Statistics

### Lines of Code
```
Source Code:              8,000+ lines
  - paint.py              1,500 lines
  - delays.py             1,000 lines
  - enhanced_paint.py     800 lines
  - hardware_mouse.py     600 lines
  - app.py                800 lines
  - Others                3,300 lines

Tests:                    2,000+ lines
  - test_delays.py        400 lines
  - test_paint_integration.py  800 lines
  - profile_paint_enhanced.py  800 lines

Documentation:            15,000+ lines
  - User guides           2,000 lines
  - Technical docs        8,000 lines
  - Developer docs        5,000 lines

TOTAL:                    25,000+ lines!
```

### File Count
```
Total Files:              50+ files
  - Python files:         20 files
  - Documentation:        14 files
  - Arduino/ESP32:        7 files
  - Config/Build:         9 files
```

---

## 🎯 Key Features by File

### Enhanced Timing (Anti-Detection)
- **delays.py** - Bell Curve randomization
- **enhanced_paint.py** - Bezier curves, jitter, pauses
- **paint.py** - Integration with all features

### Hardware Mouse
- **hardware_mouse.py** - Arduino communication
- **esp32/Arduino_Mouse.ino** - Arduino firmware
- **paint.py** - Hardware mouse integration

### GUI & Configuration
- **app.py** - Enhanced Features controls
- **config.py** - Save/load settings
- **paint.py** - Apply settings to painting

---

## 🚀 Development Workflow

### 1. Setup Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Application
```bash
python main.py
```

### 3. Run Tests
```bash
python test_delays.py
python test_paint_integration.py
```

### 4. Profile Performance
```bash
python profile_paint_enhanced.py
```

### 5. Build (Optional)
```bash
build_painter_tester.bat
```

---

## 📝 Configuration Files

```
Configuration:
├── config.json                         → User settings (auto-generated)
└── requirements.txt                    → Python dependencies

Dependencies:
  - pyautogui
  - pynput
  - pillow
  - customtkinter
  - pyserial (for hardware mouse)
  - numpy (for Bezier curves)
```

---

## 🎓 Learning Path

### 👤 For Users
1. Read [README.md](README.md)
2. Read [docs/user-guides/QUICKSTART_ENHANCED.md](docs/user-guides/QUICKSTART_ENHANCED.md)
3. Run `python main.py`
4. Enable "Enhanced Timing" in GUI
5. Paint!

### 🔧 For Hardware Setup
1. Read [docs/technical/ESP32_INTEGRATION_GUIDE.md](docs/technical/ESP32_INTEGRATION_GUIDE.md)
2. Buy Arduino Leonardo
3. Upload firmware: `esp32/Arduino_Mouse.ino`
4. Test: `python -m heartopia_painter.hardware_mouse`
5. Use in GUI!

### 💻 For Developers
1. Read [docs/development/FINAL_INTEGRATION_REPORT.md](docs/development/FINAL_INTEGRATION_REPORT.md)
2. Read [docs/technical/DELAY_SYSTEM_README.md](docs/technical/DELAY_SYSTEM_README.md)
3. Read [docs/development/INTEGRATION_PLAN.md](docs/development/INTEGRATION_PLAN.md)
4. Study source code in `src/heartopia_painter/`
5. Run tests: `python test_paint_integration.py`
6. Contribute!

---

## 🔒 Security & Anti-Detection

### Implementation Files
- **delays.py** - Human-like timing patterns
- **enhanced_paint.py** - Natural movement (Bezier, jitter)
- **hardware_mouse.py** - Hardware-level authentication

### Testing Files
- **test_delays.py** - Verify bell curve
- **profile_paint_enhanced.py** - Performance verification
- **analyze_timing.py** - Distribution analysis

---

## 📞 Support & Resources

### Documentation
- **Main:** [README.md](README.md)
- **Thai:** [โปรดอ่าน.txt](โปรดอ่าน.txt)
- **Index:** [docs/README.md](docs/README.md)

### Community
- GitHub Issues - Report bugs
- Pull Requests - Contribute
- Discussions - Ask questions

---

**Version:** 2.0  
**Last Updated:** 14 กรกฎาคม 2026  
**Status:** ✅ Complete & Organized

**Happy Coding!** 💻✨
