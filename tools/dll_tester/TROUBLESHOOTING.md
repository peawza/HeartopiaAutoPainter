# 🔧 Troubleshooting - DLL Injection Tester Build Issues

## ปัญหาที่พบบ่อย

---

### ❌ Problem 1: "Script file 'dll_injection_tester.py' does not exist"

**สาเหตุ**: Build script ไม่ได้เปลี่ยน directory ไปที่โฟลเดอร์ที่มีไฟล์

**วิธีแก้** (แก้ไขแล้ว v1.1):
```batch
# ตรวจสอบว่าไฟล์ build_dll_tester.bat มีบรรทัดนี้
cd /d "%~dp0"
```

**วิธีรันที่ถูกต้อง**:

#### ✅ วิธีที่ 1: รันจาก PowerShell/CMD
```powershell
# เปลี่ยนไปโฟลเดอร์ก่อน
cd c:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter\tools\dll_tester

# จากนั้นรัน
.\build_dll_tester.bat
```

#### ✅ วิธีที่ 2: รัน Full Path
```powershell
c:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter\tools\dll_tester\build_dll_tester.bat
```

#### ✅ วิธีที่ 3: ดับเบิลคลิกใน Explorer
```
1. เปิด File Explorer
2. ไปที่ tools\dll_tester\
3. ดับเบิลคลิก build_dll_tester.bat
```

#### ❌ วิธีที่ไม่ถูกต้อง:
```powershell
# รันจาก root โดยตรง (ผิด!)
PS C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter> build_dll_tester.bat

# แก้: ใส่ .\ ด้านหน้า หรือใช้ full path
PS C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter> .\tools\dll_tester\build_dll_tester.bat
```

---

### ❌ Problem 2: PyInstaller ติดตั้งแล้วแต่ยังหาไม่เจอ

**สาเหตุ**: PATH ไม่ถูกตั้งค่า

**วิธีแก้**:
```bash
# ตรวจสอบ PyInstaller
python -m PyInstaller --version

# ถ้าไม่ work ให้ติดตั้งใหม่
pip uninstall pyinstaller
pip install pyinstaller

# ตรวจสอบอีกครั้ง
pyinstaller --version
```

---

### ❌ Problem 3: Build ใช้เวลานาน (>5 นาที)

**สาเหตุ**: PyInstaller กำลังวิเคราะห์ dependencies

**วิธีแก้**: รอให้เสร็จ หรือใช้ cache

```bash
# Build แบบปกติ (ครั้งแรกช้า)
pyinstaller --onefile dll_injection_tester.py

# Build ครั้งต่อไปจะเร็วขึ้น (ใช้ cache)
pyinstaller --onefile --clean dll_injection_tester.py
```

**Tip**: ครั้งแรก 2-3 นาที, ครั้งต่อไป ~30 วินาที

---

### ❌ Problem 4: "ERROR: pip is not recognized"

**สาเหตุ**: Python ไม่อยู่ใน PATH

**วิธีแก้**:
```bash
# ใช้ python -m pip แทน
python -m pip install pyinstaller

# หรือเพิ่ม Python เข้า PATH
# Windows: Environment Variables → Path → Add Python Scripts folder
# เช่น: C:\Python310\Scripts
```

---

### ❌ Problem 5: Build สำเร็จแต่ EXE รันไม่ได้

**สาเหตุ**: ขาด dependencies

**วิธีแก้**:
```bash
# ติดตั้ง dependencies ทั้งหมด
pip install psutil

# จากนั้น build ใหม่
pyinstaller --onefile --clean dll_injection_tester.py
```

**ตรวจสอบ dependencies**:
```bash
# ดู imports ในไฟล์
python -c "import ast; print([node.module for node in ast.walk(ast.parse(open('dll_injection_tester.py').read())) if isinstance(node, ast.Import)])"
```

---

### ❌ Problem 6: Antivirus ลบไฟล์ EXE ทันที

**สาเหตุ**: False positive (PyInstaller มักถูก flag)

**วิธีแก้**:
```
1. เพิ่ม dist\ folder เข้า exclusion list
2. หรือปิด Antivirus ชั่วคราว (ขณะ build)
3. Scan ไฟล์ใน VirusTotal เพื่อยืนยัน

Windows Defender:
  Settings → Update & Security → Windows Security
  → Virus & threat protection → Manage settings
  → Exclusions → Add folder: C:\...\tools\dll_tester\dist
```

---

### ❌ Problem 7: EXE ใหญ่เกินไป (>10 MB)

**สาเหตุ**: Bundle libraries ที่ไม่จำเป็น

**วิธีแก้ 1: ใช้ UPX Compression**
```bash
# ดาวน์โหลด UPX: https://github.com/upx/upx/releases
# วาง upx.exe ในโฟลเดอร์ project

pyinstaller --onefile --upx-dir=. dll_injection_tester.py
```

**วิธีแก้ 2: Exclude modules**
```bash
pyinstaller --onefile ^
    --exclude-module=matplotlib ^
    --exclude-module=numpy ^
    --exclude-module=pandas ^
    dll_injection_tester.py
```

---

### ❌ Problem 8: "The term 'build_dll_tester.bat' is not recognized"

**สาเหตุ**: PowerShell ไม่รัน batch files จาก current directory โดยตรง

**วิธีแก้**:
```powershell
# แทนที่จะพิมพ์:
build_dll_tester.bat

# ใช้:
.\build_dll_tester.bat

# หรือ full path:
c:\path\to\build_dll_tester.bat
```

**เหตุผล**: PowerShell security policy ไม่ load commands จาก current location

---

## 🧪 การทดสอบ Build Environment

### Test 1: ตรวจสอบ Python
```bash
python --version
# ต้องได้: Python 3.7+
```

### Test 2: ตรวจสอบ pip
```bash
pip --version
# หรือ
python -m pip --version
```

### Test 3: ตรวจสอบ PyInstaller
```bash
pyinstaller --version
# ต้องได้: 5.0+ หรือ 6.0+
```

### Test 4: ตรวจสอบ psutil
```bash
python -c "import psutil; print(psutil.__version__)"
# ต้องได้: 5.x+
```

### Test 5: ตรวจสอบไฟล์
```bash
cd tools\dll_tester
dir *.py
# ต้องเห็น: dll_injection_tester.py
```

---

## 🔍 Debug Build Process

### เปิด Verbose Mode
```bash
pyinstaller --onefile --log-level=DEBUG dll_injection_tester.py
```

### ดู Build Log
```bash
# ไฟล์ log จะอยู่ที่
build\DLL_Injection_Tester\warn-DLL_Injection_Tester.txt
```

### Test แบบ Manual
```bash
# 1. Test Python script ก่อน
python dll_injection_tester.py

# 2. ถ้า OK แล้ว build
pyinstaller --onefile dll_injection_tester.py

# 3. Test EXE
dist\DLL_Injection_Tester.exe
```

---

## 📋 Quick Reference

### Build Commands
```bash
# Simple build
pyinstaller --onefile dll_injection_tester.py

# Build with console
pyinstaller --onefile --console dll_injection_tester.py

# Build without console (silent)
pyinstaller --onefile --noconsole dll_injection_tester.py

# Build with icon
pyinstaller --onefile --icon=icon.ico dll_injection_tester.py

# Build optimized (UPX)
pyinstaller --onefile --upx-dir=. dll_injection_tester.py

# Clean build
pyinstaller --onefile --clean dll_injection_tester.py
```

---

## ✅ ขั้นตอนแก้ปัญหาทั่วไป

```
┌─────────────────────────────────────────────┐
│ Step 1: ตรวจสอบ Environment                 │
├─────────────────────────────────────────────┤
│ ✓ Python installed?                         │
│ ✓ pip working?                              │
│ ✓ PyInstaller installed?                    │
│ ✓ psutil installed?                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Step 2: ตรวจสอบไฟล์                          │
├─────────────────────────────────────────────┤
│ ✓ dll_injection_tester.py exists?          │
│ ✓ In correct directory?                     │
│ ✓ No syntax errors?                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Step 3: Clean Build                         │
├─────────────────────────────────────────────┤
│ 1. Delete build/ folder                     │
│ 2. Delete dist/ folder                      │
│ 3. Delete *.spec file                       │
│ 4. Build again                              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Step 4: Test                                │
├─────────────────────────────────────────────┤
│ 1. Test Python script first                 │
│ 2. Build to EXE                             │
│ 3. Test EXE on same machine                 │
│ 4. Test EXE on different machine            │
└─────────────────────────────────────────────┘
```

---

## 💡 Best Practices

### ✅ DO
- ตรวจสอบ environment ก่อน build
- Clean build เมื่อเจอปัญหา
- Test Python script ก่อน build EXE
- เพิ่ม dist/ folder เข้า antivirus exclusion
- Build จาก directory ที่มีไฟล์

### ❌ DON'T
- อย่า build จาก directory อื่น
- อย่าลบ .spec file ก่อนเข้าใจมัน
- อย่าใช้ --noconsole ถ้ายังไม่แน่ใจ
- อย่า force push changes ที่ยัง build ไม่ผ่าน

---

## 📞 ยังแก้ไม่ได้?

1. อ่านคู่มือ: BUILD_DLL_TESTER_GUIDE.md
2. ตรวจสอบ: test_build.bat
3. รัน debug: pyinstaller --log-level=DEBUG ...

**Created**: 19 กรกฎาคม 2026  
**Updated**: 19 กรกฎาคม 2026  
**Version**: 1.1
