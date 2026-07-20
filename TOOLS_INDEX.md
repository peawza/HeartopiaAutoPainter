# 🛠️ Tools Directory - HeartopiaAutoPainter

## 📂 โครงสร้างเครื่องมือเสริม

โปรเจคนี้มีเครื่องมือเสริมหลายตัวที่ช่วยในการพัฒนาและทดสอบ

---

## 📋 รายการเครื่องมือ

### 🛡️ 1. DLL Injection Tester

**ตำแหน่ง**: `tools/dll_tester/`

**คำอธิบาย**: เครื่องมือตรวจสอบ DLL ที่น่าสงสัยซึ่งอาจรบกวนการทำงานของโปรแกรม

**ไฟล์สำคัญ**:
```
tools/dll_tester/
├── dll_injection_tester.py           - โปรแกรมหลัก (Python)
├── run_dll_tester.bat                - รัน script ง่ายๆ
├── build_dll_tester.bat              - Build เป็น EXE (แบบง่าย)
├── build_dll_tester_advanced.bat     - Build EXE (advanced)
├── DLL_TESTER_README.md              - คู่มือใช้งานฉบับเต็ม
├── BUILD_DLL_TESTER_GUIDE.md         - คู่มือ build
└── README.txt                        - Quick start guide
```

**วิธีใช้งาน**:
```bash
# แบบ Python
cd tools/dll_tester
python dll_injection_tester.py

# หรือใช้ batch file
run_dll_tester.bat

# Build เป็น EXE
build_dll_tester.bat
```

**ฟีเจอร์**:
- ✅ ตรวจสอบ DLL ที่น่าสงสัย (HIGH/MEDIUM/LOW risk)
- ✅ 6 โหมดการทดสอบ
- ✅ Real-time monitoring
- ✅ รองรับ Build เป็น standalone .exe

**เอกสาร**: [DLL_TESTER_README.md](tools/dll_tester/DLL_TESTER_README.md)

---

### 🔒 2. Anti-Detection Layer

**ตำแหน่ง**: `anti_detection.py` (root)

**คำอธิบาย**: ระบบป้องกันการตรวจจับที่ทำงานก่อนโปรแกรมหลัก

**ไฟล์สำคัญ**:
```
anti_detection.py                   - โมดูลหลัก
test_anti_detection_simple.py       - สคริปต์ทดสอบ
test_startup_detection.py           - ทดสอบ startup
ANTI_DETECTION_LAYER_SUMMARY.md     - เอกสารครบถ้วน (8,500+ บรรทัด)
```

**วิธีใช้งาน**:
```python
from anti_detection import init_stealth

# รันก่อน import อื่นๆ
init_stealth()

# จากนั้นรันโปรแกรมหลัก
from your_app import main
main()
```

**ฟีเจอร์**:
- ✅ 8 เทคนิคตรวจจับ (Debugger, VM, DLL, etc.)
- ✅ Process obfuscation
- ✅ Random delays
- ✅ Timing analysis prevention

**เอกสาร**: [ANTI_DETECTION_LAYER_SUMMARY.md](ANTI_DETECTION_LAYER_SUMMARY.md)

---

### 🔌 3. ESP32 / Arduino Tools

**ตำแหน่ง**: `esp32/`

**คำอธิบาย**: เครื่องมือสำหรับ Arduino/ESP32 Hardware Mouse

**ไฟล์สำคัญ**:
```
esp32/
├── Arduino_Mouse/
│   └── Arduino_Mouse.ino           - Firmware
├── upload.bat                      - อัพโหลด firmware
├── install_esp32.bat               - ติดตั้ง board
├── check_boards.bat                - ตรวจสอบ board
├── spoof_usb_leonardo.bat          - USB spoofing
└── README_SETUP.txt                - คู่มือติดตั้ง
```

**วิธีใช้งาน**:
```bash
# ติดตั้ง ESP32 board
cd esp32
install_esp32.bat

# อัพโหลด firmware
upload.bat

# ตรวจสอบ
check_boards.bat
```

**ฟีเจอร์**:
- ✅ Arduino Leonardo / ESP32-S3 support
- ✅ USB HID Mouse emulation
- ✅ Auto-detection COM port
- ✅ Microsecond precision

**เอกสาร**: [esp32/README_SETUP.txt](esp32/README_SETUP.txt), [ESP32_SETUP_COMPLETE.md](ESP32_SETUP_COMPLETE.md)

---

### 🏗️ 4. Build Tools

**ตำแหน่ง**: Root directory

**คำอธิบาย**: สคริปต์สำหรับ build โปรแกรมหลัก

**ไฟล์สำคัญ**:
```
build_stealth.bat                   - Build โปรแกรมหลัก
build_stealth.py                    - Build script (Python)
build_painter_tester.bat            - Build tester version
HeartopiaAutoPainter_stealth.spec   - PyInstaller config
BUILD_INSTRUCTIONS.md               - คู่มือ build
```

**วิธีใช้งาน**:
```bash
# Build โปรแกรมหลัก
build_stealth.bat

# ไฟล์จะอยู่ที่
dist/HeartopiaAutoPainter_stealth.exe
```

**เอกสาร**: [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

---

### 🧪 5. Testing Tools

**ตำแหน่ง**: `tests/`, root

**คำอธิบาย**: เครื่องมือทดสอบต่างๆ

**ไฟล์สำคัญ**:
```
test_anti_detection_simple.py       - ทดสอบ anti-detection
test_startup_detection.py           - ทดสอบ startup
test_connect.py                     - ทดสอบ connection
test_serial.py                      - ทดสอบ serial port
tests/                              - โฟลเดอร์ tests เพิ่มเติม
```

**วิธีใช้งาน**:
```bash
# ทดสอบ anti-detection
python test_anti_detection_simple.py

# ทดสอบ startup
python test_startup_detection.py

# ทดสอบ serial
python test_serial.py
```

---

## 📚 เอกสารทั้งหมด

### 📖 คู่มือหลัก
- [README.md](README.md) - คู่มือโปรเจคหลัก
- [QUICKSTART_ESP32.md](QUICKSTART_ESP32.md) - เริ่มต้นใช้ ESP32
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - วิธี build โปรแกรม

### 🔒 Anti-Detection
- [ANTI_DETECTION_LAYER_SUMMARY.md](ANTI_DETECTION_LAYER_SUMMARY.md) - เอกสารครบถ้วน
- [AUTO_CONNECT_FEATURE.md](AUTO_CONNECT_FEATURE.md) - Auto-connect feature

### 🛡️ DLL Tester
- [tools/dll_tester/DLL_TESTER_README.md](tools/dll_tester/DLL_TESTER_README.md) - คู่มือใช้งาน
- [tools/dll_tester/BUILD_DLL_TESTER_GUIDE.md](tools/dll_tester/BUILD_DLL_TESTER_GUIDE.md) - คู่มือ build

### 🔌 ESP32 / Hardware
- [ESP32_SETUP_COMPLETE.md](ESP32_SETUP_COMPLETE.md) - สถานะ setup
- [ESP32_INTEGRATION_TASKS.md](ESP32_INTEGRATION_TASKS.md) - Task list
- [COMPLETE_ARDUINO_MOUSE_SOLUTION.md](COMPLETE_ARDUINO_MOUSE_SOLUTION.md) - วิธีแก้ปัญหา

### ⚡ Enhanced Features
- [ADVANCED_RANDOMNESS_FEATURES.md](ADVANCED_RANDOMNESS_FEATURES.md) - Randomness v1.3
- [DELAY_SYSTEM_FLOW_COMPLETE.md](DELAY_SYSTEM_FLOW_COMPLETE.md) - Delay system
- [CHANGELOG_v1.2.0.md](CHANGELOG_v1.2.0.md) - Velocity profiles

### 📁 โครงสร้าง
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - โครงสร้างโปรเจค
- [PROJECT_STRUCTURE_NEW.md](PROJECT_STRUCTURE_NEW.md) - โครงสร้างใหม่

---

## 🎯 Quick Reference

### รันโปรแกรมหลัก
```bash
python main.py
```

### ทดสอบ Anti-Detection
```bash
python test_anti_detection_simple.py
```

### ทดสอบ DLL Injection
```bash
cd tools/dll_tester
python dll_injection_tester.py
```

### Build โปรแกรม
```bash
build_stealth.bat
```

### Build DLL Tester
```bash
cd tools/dll_tester
build_dll_tester.bat
```

---

## 📊 สถิติโปรเจค

```
📈 Total Code Lines:      8,500+
📚 Documentation Files:   20+
🛠️ Tools:                 5+
🧪 Test Files:            5+
🔒 Security Features:     8 detection techniques
⭐ Human-likeness Score:  9.5/10
```

---

## 🏆 Features Summary

### ✅ Core Systems
- 🔒 Anti-Detection Layer (8 techniques)
- 🎯 Enhanced Timing (Bell Curve)
- 🖱️ Hardware Mouse Support (Arduino/ESP32)
- 🌀 Bezier Curve Movement
- 🚀 6 Velocity Profiles
- 🎲 Advanced Randomness (v1.3)

### ✅ Tools
- 🛡️ DLL Injection Tester
- 🔌 ESP32 Firmware & Upload Scripts
- 🏗️ Build System (PyInstaller)
- 🧪 Testing Suite
- 📊 Statistical Analysis Tools

### ✅ Documentation
- 📖 14+ comprehensive docs (Thai + English)
- 🎓 Build guides
- 💡 Quick start guides
- 🔧 Troubleshooting guides

---

## 💡 Tips

1. **ก่อนใช้โปรแกรม**: รัน DLL Tester เพื่อตรวจสอบ DLL
2. **ก่อน Build**: อ่าน BUILD_INSTRUCTIONS.md
3. **หาก Error**: ตรวจสอบ Anti-Detection ทำงานหรือไม่
4. **Performance**: ใช้ Hardware Mouse เพื่อความแม่นยำสูงสุด

---

**Created**: 19 กรกฎาคม 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready

---

**Happy Coding! 🎨**
