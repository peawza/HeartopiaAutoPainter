# แก้ไข: Painter_Stealth.exe ขาด pyserial Module

## ปัญหา
เมื่อเปิด `Painter_Stealth.exe` จะแสดง error:
```
ไม่พบโมดูล pyserial
คำแนะนำ: pip install pyserial
```

## สาเหตุ
PyInstaller ไม่ได้ include `pyserial` และ sub-modules ทั้งหมดเข้าไปใน executable ทำให้โค้ดที่เรียกใช้ `import serial` หรือ `serial.tools.list_ports` ทำงานไม่ได้

## การแก้ไข

### 1. ติดตั้ง pyserial ใน venv (ถ้ายังไม่ได้ติดตั้ง)
```bash
.\.venv\Scripts\python.exe -m pip install pyserial
```

ผลลัพธ์:
```
Successfully installed pyserial-3.5
```

### 2. เพิ่ม pyserial modules ลง hiddenimports

**ไฟล์ที่แก้ไข:**
- `HeartopiaAutoPainter_stealth.spec`
- `build_stealth.py`

**เดิม:**
```python
hiddenimports=[
    ...
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
],
```

**ใหม่ (เพิ่ม Windows-specific modules):**
```python
hiddenimports=[
    ...
    # pyserial modules (COM port communication)
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    'serial.serialutil',
    'serial.win32',
    'serial.serialwin32',
    'serial.tools.list_ports_windows',
],
```

### 3. Build ใหม่
```bash
.\\.venv\Scripts\python.exe build_stealth.py
```

หรือ

```bash
build_stealth.bat
```

## pyserial Modules ที่ต้อง Include

| Module | วัตถุประสงค์ |
|--------|--------------|
| `serial` | Core pyserial module |
| `serial.tools` | Serial port tools package |
| `serial.tools.list_ports` | List available COM ports |
| `serial.serialutil` | Serial utilities and base classes |
| `serial.win32` | Windows-specific serial functions |
| `serial.serialwin32` | Windows serial port implementation |
| `serial.tools.list_ports_windows` | Windows COM port enumeration |

## การทดสอบ

### ทดสอบว่า pyserial ถูกติดตั้ง:
```bash
.\\.venv\Scripts\python.exe -c "import serial; print('pyserial version:', serial.__version__)"
```

ผลลัพธ์ที่คาดหวัง:
```
pyserial version: 3.5
```

### ทดสอบหลัง build:
1. Build โปรแกรมด้วย `build_stealth.bat` หรือ `build_stealth.py`
2. เปิด `dist\Painter_Stealth.exe`
3. ไปที่ tab "จังหวะ / ความน่าเชื่อถือ"
4. กดปุ่ม 🔄 (Refresh ports)
5. ตรวจสอบว่าไม่มี error popup เกี่ยวกับ pyserial

## ปัญหาที่เกี่ยวข้อง

### ถ้า build ยังแสดง error pyserial:
1. ตรวจสอบว่า venv ใช้ Python ที่ถูกต้อง
2. ลบ `build/` และ `dist/` แล้ว build ใหม่:
   ```bash
   rmdir /s /q build
   rmdir /s /q dist
   build_stealth.bat
   ```

### ถ้า COM ports ไม่แสดง:
- ตรวจสอบว่า Arduino/ESP32 เชื่อมต่ออยู่
- ตรวจสอบใน Device Manager ว่ามี COM port ไหนแสดงอยู่
- ลอง refresh ports อีกครั้ง

## ความสัมพันธ์กับการแก้ไขอื่น

การแก้ไขนี้ทำงานร่วมกับ:
- ✅ การโหลด config จาก `mouse_config.json` (แก้ไขแล้วใน `FIX_ENHANCED_TIMING_CONFIG_LOAD.md`)
- ✅ การบันทึก Arduino port ลง `mouse_config.json`
- ✅ Auto-detect Arduino ports (🔄 button)

---
**หมายเหตุ:** pyserial จำเป็นสำหรับ:
- การสแกนหา COM ports
- การเชื่อมต่อกับ Arduino/ESP32
- การส่งคำสั่ง mouse movement ผ่าน serial port
