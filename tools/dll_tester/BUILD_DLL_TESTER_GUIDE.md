# 🏗️ DLL Injection Tester - Build Guide

## 🚀 Quick Build (แนะนำ!)

### วิธีที่ 1: ดับเบิลคลิก (ง่ายที่สุด)
```
1. ดับเบิลคลิก: build_dll_tester.bat
2. รอ 1-3 นาที
3. เสร็จแล้ว! ไฟล์จะอยู่ที่ dist\DLL_Injection_Tester.exe
```

### วิธีที่ 2: PowerShell/CMD
```batch
cd c:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter
build_dll_tester.bat
```

---

## 🎨 Advanced Build Options

หากต้องการ options เพิ่มเติม:

```batch
build_dll_tester_advanced.bat
```

### ตัวเลือกที่มี:

| Option | คำอธิบาย | ขนาดไฟล์ | เหมาะสำหรับ |
|--------|----------|----------|-------------|
| **[1] Standard** | แบบปกติ มี console | ~5-6 MB | **แนะนำ!** |
| [2] Silent | ไม่มี console window | ~5-6 MB | GUI wrapper |
| [3] Debug | แสดง debug info | ~6-7 MB | Troubleshooting |
| [4] Optimized | บีบอัดด้วย UPX | ~3-4 MB | ขนาดเล็กกว่า |
| [5] With Icon | ใส่ไอคอน .ico | ~5-6 MB | สวยงาม |

---

## 📁 โครงสร้างไฟล์หลัง Build

```
HeartopiaAutoPainter/
├── dll_injection_tester.py       (ซอร์สโค้ด)
├── build_dll_tester.bat          (สคริปต์ build แบบง่าย)
├── build_dll_tester_advanced.bat (สคริปต์ build แบบ advanced)
├── build/                         (ไฟล์ชั่วคราว - ลบได้)
├── dist/
│   └── DLL_Injection_Tester.exe  ⭐ ไฟล์ EXE สำเร็จรูป!
└── DLL_Injection_Tester.spec     (ไฟล์ config - ลบได้)
```

---

## ✅ ขั้นตอนการ Build (รายละเอียด)

### [1/4] ติดตั้ง PyInstaller

Build script จะติดตั้งให้อัตโนมัติ แต่หากต้องการติดตั้งเอง:

```bash
pip install pyinstaller
```

### [2/4] ทำความสะอาด Build เก่า

Script จะลบไฟล์เก่าให้อัตโนมัติ:
- `dist\DLL_Injection_Tester.exe` (EXE เก่า)
- `build\DLL_Injection_Tester\` (โฟลเดอร์ build)
- `DLL_Injection_Tester.spec` (ไฟล์ config)

### [3/4] Build EXE

PyInstaller จะ:
1. วิเคราะห์ dependencies (psutil)
2. รวม Python interpreter
3. บรรจุทุกอย่างใน 1 ไฟล์ .exe
4. ใช้เวลา **1-3 นาที**

### [4/4] ตรวจสอบผลลัพธ์

หากสำเร็จ จะเห็น:
```
SUCCESS! EXE built successfully!
File location: dist\DLL_Injection_Tester.exe
```

---

## 🧪 ทดสอบ EXE

### ทดสอบบนเครื่องตัวเอง:

```batch
dist\DLL_Injection_Tester.exe
```

### ทดสอบบนเครื่องอื่น:

1. คัดลอก `dist\DLL_Injection_Tester.exe` ไปเครื่องอื่น
2. **ไม่ต้องติดตั้ง Python!**
3. ดับเบิลคลิกรันได้เลย

---

## ⚙️ Build Options อธิบาย

### Standard Build (แนะนำ)

```batch
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --clean ^
    --noconfirm ^
    dll_injection_tester.py
```

**Parameters:**
- `--onefile` - รวมทุกอย่างใน 1 ไฟล์
- `--console` - แสดง console window
- `--clean` - ลบไฟล์ cache เก่า
- `--noconfirm` - ไม่ถามยืนยัน (overwrite อัตโนมัติ)

### Silent Build (No Console)

```batch
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --noconsole ^
    dll_injection_tester.py
```

⚠️ **คำเตือน**: ไม่แนะนำ เพราะจะไม่เห็น output อะไรเลย!

### Optimized Build (UPX)

```batch
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --upx-dir=. ^
    dll_injection_tester.py
```

**ข้อดี**: ขนาดเล็กลง 30-40%
**ข้อเสีย**: ต้องติดตั้ง UPX ก่อน

**ดาวน์โหลด UPX**: https://github.com/upx/upx/releases

### With Icon

```batch
pyinstaller --onefile ^
    --name="DLL_Injection_Tester" ^
    --console ^
    --icon=icon.ico ^
    dll_injection_tester.py
```

**ข้อกำหนด**: ต้องมีไฟล์ `icon.ico` ในโฟลเดอร์โปรเจค

---

## 🔧 แก้ปัญหา

### ❌ Problem: "pyinstaller is not recognized"

**สาเหตุ**: PyInstaller ไม่ได้ติดตั้ง

**วิธีแก้**:
```bash
pip install pyinstaller
```

---

### ❌ Problem: "Failed to execute script"

**สาเหตุ**: ขาด dependencies

**วิธีแก้**:
```bash
pip install psutil
```

จากนั้น build ใหม่

---

### ❌ Problem: Antivirus blocks the EXE

**สาเหตุ**: False positive (PyInstaller มักถูก flag)

**วิธีแก้**:
1. เพิ่ม `dist\` folder เข้า exclusion list
2. หรือปิด Antivirus ชั่วคราวขณะ build

---

### ❌ Problem: EXE ใหญ่เกินไป (>10 MB)

**สาเหตุ**: รวม libraries ที่ไม่จำเป็น

**วิธีแก้**:
1. ใช้ UPX compression:
   ```bash
   build_dll_tester_advanced.bat
   # เลือก option 4
   ```

2. หรือ exclude libraries ที่ไม่ใช้:
   ```bash
   pyinstaller --onefile ^
       --exclude-module=matplotlib ^
       --exclude-module=numpy ^
       dll_injection_tester.py
   ```

---

### ❌ Problem: "ImportError: No module named 'psutil'"

**สาเหตุ**: psutil ไม่ถูก bundle เข้า EXE

**วิธีแก้**:
1. ติดตั้ง psutil:
   ```bash
   pip install psutil
   ```

2. Build ใหม่ (PyInstaller จะตรวจพบอัตโนมัติ)

---

## 📊 เปรียบเทียบ Build Methods

| Method | ขนาดไฟล์ | เวลา Build | ความยาก | แนะนำ |
|--------|----------|-----------|---------|-------|
| **Standard** | ~5-6 MB | 1-2 นาที | ง่าย | ⭐⭐⭐⭐⭐ |
| Silent | ~5-6 MB | 1-2 นาที | ง่าย | ⭐ |
| Debug | ~6-7 MB | 2-3 นาที | ปานกลาง | ⭐⭐⭐ |
| Optimized | ~3-4 MB | 2-4 นาที | ยาก | ⭐⭐⭐⭐ |
| With Icon | ~5-6 MB | 1-2 นาที | ง่าย | ⭐⭐⭐⭐ |

---

## 🎯 คำแนะนำสำหรับ Distribution

### สำหรับผู้ใช้ทั่วไป:
```
แจกจ่าย:
  dist\DLL_Injection_Tester.exe
  DLL_TESTER_README.md (คู่มือ)
```

### สำหรับ Developers:
```
แจกจ่าย:
  dll_injection_tester.py (ซอร์สโค้ด)
  build_dll_tester.bat (build script)
  requirements.txt
```

---

## 📦 Create Distribution Package

สร้าง .zip สำหรับแจกจ่าย:

```batch
@echo off
mkdir "DLL_Tester_Package"
copy "dist\DLL_Injection_Tester.exe" "DLL_Tester_Package\"
copy "DLL_TESTER_README.md" "DLL_Tester_Package\"
copy "BUILD_DLL_TESTER_GUIDE.md" "DLL_Tester_Package\"

echo Creating ZIP file...
powershell Compress-Archive -Path "DLL_Tester_Package\*" -DestinationPath "DLL_Tester_v1.0.zip" -Force

echo Package created: DLL_Tester_v1.0.zip
pause
```

---

## ✅ Checklist ก่อนแจกจ่าย

- [ ] Build EXE สำเร็จ
- [ ] ทดสอบ EXE บนเครื่องตัวเอง
- [ ] ทดสอบ EXE บนเครื่องอื่น (ไม่มี Python)
- [ ] ตรวจสอบขนาดไฟล์ (~5-6 MB)
- [ ] สแกน Antivirus (ตรวจสอบ false positive)
- [ ] รวมคู่มือ README
- [ ] สร้าง .zip package
- [ ] เขียน CHANGELOG

---

## 🏆 Build แล้ว อะไรต่อ?

### 1. ทดสอบให้ครบถ้วน
```batch
# รัน EXE
dist\DLL_Injection_Tester.exe

# ลองทุก option (1-6)
# ตรวจสอบว่าทำงานถูกต้อง
```

### 2. สร้างเอกสาร
- คู่มือการใช้งาน (มีแล้ว: DLL_TESTER_README.md)
- Release notes
- Known issues

### 3. แจกจ่าย
- GitHub Releases
- Google Drive / Dropbox
- แจกในชุมชน

---

## 🎓 Advanced: Custom Build

หากต้องการควบคุมมากขึ้น สร้างไฟล์ `.spec`:

```python
# DLL_Injection_Tester.spec
a = Analysis(
    ['dll_injection_tester.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DLL_Injection_Tester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

จากนั้น:
```bash
pyinstaller DLL_Injection_Tester.spec
```

---

## 📞 ติดต่อ / รายงานปัญหา

- **GitHub Issues**: สร้าง issue
- **Documentation**: อ่านเพิ่มที่ DLL_TESTER_README.md

---

**Created by**: Kiro AI Assistant  
**Date**: 19 กรกฎาคม 2026  
**Version**: 1.0

---

## 🎉 พร้อม Build แล้ว!

```batch
build_dll_tester.bat
```

**Happy Building! 🏗️** 🚀
