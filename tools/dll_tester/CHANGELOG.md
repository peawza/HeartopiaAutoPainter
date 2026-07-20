# Changelog - DLL Injection Tester

## Version 1.1 (2026-07-19)

### 🐛 Bug Fixes
- **Fixed**: Self-detection issue - โปรแกรมไม่ตรวจจับตัวเองอีกต่อไป
- **Fixed**: Working directory issue - เพิ่ม `cd /d "%~dp0"` ใน batch files
- **Fixed**: Build script ไม่หาไฟล์ `.py` เจอ

### ✨ Improvements
- **Added**: `TROUBLESHOOTING.md` - คู่มือแก้ปัญหาครบถ้วน
- **Added**: `test_build.bat` - ทดสอบ build environment
- **Added**: `CHANGELOG.md` - ไฟล์นี้
- **Improved**: Error messages ใน build scripts
- **Improved**: Working directory display

### 📝 Changes
```python
# Before (v1.0):
for dll_path in dlls:
    dll_name = os.path.basename(dll_path).lower()
    # Check patterns...

# After (v1.1):
for dll_path in dlls:
    dll_name = os.path.basename(dll_path).lower()
    
    # Skip self (DLL_Injection_Tester.exe)
    if 'dll_injection_tester' in dll_name:
        continue  ← เพิ่มบรรทัดนี้!
    
    # Check patterns...
```

---

## Version 1.0 (2026-07-19)

### 🎉 Initial Release

#### ✅ Features
- 6 ตัวเลือกการทดสอบ:
  1. Quick Scan
  2. Target Scan
  3. Show Patterns
  4. Test Logic
  5. Real-Time Monitor
  6. Full Test Suite

- 3 ระดับความเสี่ยง:
  - 🔴 HIGH RISK (cheatengine, frida, etc.)
  - 🟡 MEDIUM RISK (discord, obs, etc.)
  - 🟢 LOW RISK (kernel32, user32, etc.)

#### 📦 Build System
- `build_dll_tester.bat` - Simple build
- `build_dll_tester_advanced.bat` - Advanced options
- `run_dll_tester.bat` - Quick run script

#### 📚 Documentation
- `DLL_TESTER_README.md` - Full user guide
- `BUILD_DLL_TESTER_GUIDE.md` - Build instructions
- `README.txt` - Quick start

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| **1.1** | 2026-07-19 | ✅ Current | Fixed self-detection bug |
| **1.0** | 2026-07-19 | ✅ Stable | Initial release |

---

## Upgrade Guide

### จาก v1.0 → v1.1

**ไฟล์ที่เปลี่ยน:**
```
dll_injection_tester.py      ← Updated analyze_dlls()
build_dll_tester.bat         ← Added cd /d "%~dp0"
build_dll_tester_advanced.bat ← Added cd /d "%~dp0"
run_dll_tester.bat           ← Added cd /d "%~dp0"
```

**วิธีอัปเดต:**
1. ดาวน์โหลดไฟล์ใหม่
2. Copy ทับไฟล์เก่า
3. Build EXE ใหม่ (ถ้าใช้ .exe)

---

## Known Issues

### v1.1
- ✅ ไม่มี known issues

### v1.0
- ❌ **Fixed in v1.1**: ตรวจจับตัวเอง (false positive)
- ❌ **Fixed in v1.1**: Build script หาไฟล์ไม่เจอ

---

## Roadmap

### v1.2 (Planned)
- [ ] เพิ่ม export ผลลัพธ์เป็น JSON
- [ ] เพิ่ม whitelist/blacklist custom patterns
- [ ] เพิ่ม GUI mode (tkinter)
- [ ] เพิ่ม automatic report generation

### v2.0 (Future)
- [ ] Process injection detection
- [ ] Registry monitoring
- [ ] Network traffic analysis
- [ ] Multi-language support

---

**Maintained by**: Kiro AI Assistant  
**License**: Educational use only  
**Repository**: HeartopiaAutoPainter/tools/dll_tester
