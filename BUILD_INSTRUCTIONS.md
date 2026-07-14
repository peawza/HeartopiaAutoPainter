# 🔨 วิธีการ Build โปรแกรมเป็น EXE

## ขั้นตอนการ Build

### 1. ติดตั้ง Python
- ดาวน์โหลด Python 3.10 หรือสูงกว่าจาก [python.org](https://www.python.org/downloads/)
- ตรวจสอบว่า Python อยู่ใน PATH แล้ว (ทดสอบด้วยคำสั่ง `python --version`)

### 2. Setup สภาพแวดล้อม
รันไฟล์ `setup_build.bat` เพื่อติดตั้ง dependencies ทั้งหมด:
```batch
setup_build.bat
```

ไฟล์นี้จะทำดังนี้:
- สร้าง virtual environment (.venv)
- ติดตั้ง packages จาก requirements.txt
- ติดตั้ง PyInstaller สำหรับการ build
- ติดตั้ง packages เพิ่มเติมสำหรับ stealth build

### 3. Build โปรแกรม
หลังจาก setup เสร็จแล้ว รันไฟล์:
```batch
build_stealth.bat
```

ไฟล์ exe จะถูกสร้างที่: `dist\Painter_Stealth.exe`

## 📋 ไฟล์ที่จำเป็น

### ไฟล์หลัก
- ✅ `config.json` - ไฟล์ config (สร้างแล้ว)
- ✅ `main.py` - โปรแกรมหลัก
- ✅ `requirements.txt` - Python packages
- ✅ `build_stealth.py` - Build script
- ✅ `src/` - โฟลเดอร์ source code

### Build Scripts
- `setup_build.bat` - สำหรับ setup environment
- `build_stealth.bat` - สำหรับ build exe
- `build_stealth.py` - Python script สำหรับ build ด้วยเทคนิค anti-detection

## 🛠️ เทคนิค Anti-Detection ที่ใช้

`build_stealth.py` ใช้เทคนิคต่อไปนี้:
1. **Random executable name** - หลีกเลี่ยง signature database
2. **Strip debug symbols** - ลดข้อมูลสำหรับ reverse engineering
3. **Code optimization level 2** - เปลี่ยน bytecode structure
4. **Remove PyInstaller metadata** - ลดลายเซ็น PyInstaller
5. **Signature randomization** - เปลี่ยน file hash
6. **Anti-debugging wrapper** - ตรวจสอบ debugger runtime
7. **Anti-VM checks** - ตรวจสอบ virtual machine

## ⚠️ หมายเหตุสำคัญ

1. **เทคนิคเหล่านี้เป็นพื้นฐาน** - อาจยังถูกตรวจจับโดย:
   - Antivirus ที่ทันสมัย
   - Anti-cheat ระดับ kernel
   - Behavioral analysis systems

2. **การใช้งาน** - ควรใช้เฉพาะ:
   - ในสภาพแวดล้อมส่วนตัว
   - สำหรับการทดสอบ
   - ไม่แนะนำให้ใช้กับเกมออนไลน์ที่มี anti-cheat

3. **ความเสี่ยง**:
   - อาจถูกแบนจากเกม
   - อาจถูก antivirus flag
   - ใช้ความเสี่ยงของคุณเอง

## 🔍 การแก้ปัญหา

### ปัญหา: Virtual environment ไม่ถูกสร้าง
```batch
python -m venv .venv
```

### ปัญหา: PyInstaller ไม่ทำงาน
```batch
pip install --upgrade pyinstaller
```

### ปัญหา: Build error เกี่ยวกับ dependencies
```batch
pip install --upgrade -r requirements.txt
pip install pywin32 psutil pyarmor
```

### ปัญหา: config.json ไม่พบ
ไฟล์ config.json ถูกสร้างไว้แล้ว หากหายไป ให้รัน setup_build.bat อีกครั้ง

## 📦 Build Output

หลังจาก build สำเร็จ คุณจะได้:
- `dist\Painter_Stealth.exe` - ไฟล์ exe หลัก
- ขนาดประมาณ 50-100 MB (ขึ้นอยู่กับ dependencies)

## 🚀 การทดสอบ

1. รัน exe โดยตรง:
```batch
dist\Painter_Stealth.exe
```

2. หรือใช้ tester:
```batch
build_painter_tester.bat
```

## 📞 ต้องการความช่วยเหลือ?

หากมีปัญหา:
1. ตรวจสอบว่าไฟล์ทั้งหมดครบถ้วน
2. รัน setup_build.bat ใหม่
3. ตรวจสอบ error message ใน console
4. ลองรันโปรแกรมด้วย Python ก่อน: `python main.py`
