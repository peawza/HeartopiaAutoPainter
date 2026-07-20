# 🛡️ DLL Injection Tester - คู่มือการใช้งาน

## 📦 คืออะไร?

**DLL Injection Tester** เป็นเครื่องมือตรวจสอบ DLL ที่น่าสงสัยซึ่งอาจรบกวนการทำงานของ HeartopiaAutoPainter

### ✅ จุดเด่น:
- ไม่ต้องติดตั้ง Python (เมื่อ compile เป็น .exe)
- ไม่มี dependencies
- รันได้ทันที!

---

## 🚀 วิธีใช้งาน

### วิธีที่ 1: รัน Python Script (สำหรับ Developers)

```bash
python dll_injection_tester.py
```

หรือดับเบิลคลิก:
```
run_dll_tester.bat
```

### วิธีที่ 2: รัน EXE (สำหรับ End Users)

```bash
# Build EXE ก่อน (ครั้งแรก)
pyinstaller --onefile --name="DLL_Injection_Tester" --icon=NONE dll_injection_tester.py

# จากนั้นรัน
dist\DLL_Injection_Tester.exe
```

---

## 🎯 เมนูตัวเลือก

### 1. Quick Scan
- **คืออะไร**: สแกน process ปัจจุบัน (โปรแกรมนี้เอง)
- **ใช้เมื่อไหร่**: ต้องการเช็คระบบอย่างรวดเร็ว

### 2. Target Scan ⭐ **แนะนำ**
- **คืออะไร**: สแกน HeartopiaAutoPainter / main.py
- **ข้อกำหนด**: ต้องเปิด main.py ก่อน
- **ใช้เมื่อไหร่**: ก่อนใช้ Painter เพื่อตรวจสอบว่ามี DLL น่าสงสัยหรือไม่

```bash
# ขั้นตอน:
1. เปิดหน้าต่างใหม่: python main.py
2. เปิด DLL Tester: python dll_injection_tester.py
3. เลือก option 2
4. ดูผลลัพธ์
```

### 3. Show Common Injection Patterns
- **คืออะไร**: แสดง DLL patterns ที่มักถูก inject
- **ใช้เมื่อไหร่**: เรียนรู้ว่า DLL ไหนน่าสงสัย

### 4. Test Detection Logic
- **คืออะไร**: ทดสอบว่าระบบตรวจจับทำงานถูกต้อง
- **ใช้เมื่อไหร่**: สำหรับ developers ที่ต้องการ verify logic

### 5. Real-Time Monitor
- **คืออะไร**: ติดตาม DLL injection แบบ real-time (30 วินาที)
- **ใช้เมื่อไหร่**: ต้องการดูว่าโปรแกรมอะไร inject DLL

```bash
# ตัวอย่าง:
1. เลือก option 5
2. เปิด Discord ขณะที่กำลัง monitor
3. ดูว่า discord*.dll ถูกตรวจพบหรือไม่
```

### 6. Full Test Suite
- **คืออะไร**: รันทุก test รวมกัน
- **ใช้เมื่อไหร่**: ต้องการตรวจสอบครบถ้วนที่สุด

---

## 📊 เข้าใจผลลัพธ์

### ✅ Suspicious DLLs Found: 0
```
Status: CLEAN!
Action: ปลอดภัย ใช้ HeartopiaAutoPainter ได้เลย
```

### ⚠️ Suspicious DLLs Found: 1-5
```
Status: WARNING!
Cause: มักมาจาก Discord, OBS, overlays
Action: ปิดโปรแกรมเหล่านั้นแล้วทดสอบอีกครั้ง
```

### 🚨 Suspicious DLLs Found: >5
```
Status: ALERT!
Cause: อาจเป็น Cheat engines, debuggers, hooks
Action: ปิดโปรแกรมที่น่าสงสัยทั้งหมดทันที
```

---

## 🔍 DLL ที่ถูกตรวจจับ

### 🔴 HIGH RISK (จะถูกตรวจพบแน่นอน)

| DLL Pattern | โปรแกรม | ระดับอันตราย |
|-------------|---------|-------------|
| `cheatengine*.dll` | Cheat Engine | 🔴🔴🔴🔴🔴 |
| `frida*.dll` | Frida Framework | 🔴🔴🔴🔴🔴 |
| `easyhook*.dll` | EasyHook | 🔴🔴🔴🔴 |
| `minhook*.dll` | MinHook | 🔴🔴🔴🔴 |
| `inject*.dll` | Generic Injectors | 🔴🔴🔴🔴🔴 |
| `x64dbg.dll` | x64dbg Debugger | 🔴🔴🔴🔴 |
| `x32dbg.dll` | x32dbg Debugger | 🔴🔴🔴🔴 |

### 🟡 MEDIUM RISK (อาจถูกตรวจพบ)

| DLL Pattern | โปรแกรม | ระดับอันตราย |
|-------------|---------|-------------|
| `discord*.dll` | Discord Overlay | 🟡🟡 |
| `obs*.dll` | OBS Screen Capture | 🟡🟡 |
| `reshade*.dll` | ReShade Graphics Mod | 🟡🟡🟡 |
| `rtss*.dll` | RivaTuner Overlay | 🟡🟡 |

### 🟢 LOW RISK (ปกติจะไม่มีปัญหา)

| DLL Pattern | โปรแกรม | ระดับอันตราย |
|-------------|---------|-------------|
| `kernel32.dll` | Windows System | 🟢 |
| `user32.dll` | Windows System | 🟢 |
| `ntdll.dll` | Windows System | 🟢 |

---

## 💡 เคล็ดลับการใช้งาน

### ✓ DO (ควรทำ)
- ✅ รัน test ก่อนใช้ HeartopiaAutoPainter
- ✅ ถ้าเจอ warning ให้ปิด overlay programs
- ✅ รันด้วยสิทธิ์ Administrator เพื่อผลลัพธ์ที่ดีที่สุด
- ✅ ทดสอบอีกครั้งหลังปิดโปรแกรมที่น่าสงสัย

### ✗ DON'T (ไม่ควรทำ)
- ❌ ใช้ Painter ขณะที่มี Cheat Engine เปิดอยู่
- ❌ เพิกเฉยต่อ HIGH RISK warnings
- ❌ รันหลายๆ test พร้อมกัน (อาจทำให้สับสน)

---

## 🔧 แก้ปัญหา

### ❌ Problem: "HeartopiaAutoPainter is not running"

**สาเหตุ**: โปรแกรมยังไม่เปิด

**วิธีแก้**:
```bash
# Terminal 1: เปิด Painter
python main.py

# Terminal 2: เปิด DLL Tester
python dll_injection_tester.py
# เลือก option 2
```

---

### ❌ Problem: "Access Denied"

**สาเหตุ**: ไม่มีสิทธิ์ Administrator

**วิธีแก้**:
- คลิกขวา → Run as Administrator
- หรือเปิด PowerShell/CMD ด้วยสิทธิ์ Admin

---

### ❌ Problem: Antivirus blocks the program

**สาเหตุ**: False positive (เครื่องมือตรวจจับ DLL ถูกเข้าใจผิด)

**วิธีแก้**:
- เพิ่มเข้า exclusion list ของ Antivirus
- โปรแกรมนี้อ่าน process memory เท่านั้น ไม่ได้แก้ไขอะไร

---

## 🎓 ตัวอย่างการใช้งาน

### Scenario 1: ทดสอบก่อนใช้ Painter

```bash
┌─────────────────────────────────────────────┐
│ ขั้นตอน:                                    │
├─────────────────────────────────────────────┤
│ 1. ปิด Discord, OBS ทั้งหมด                │
│ 2. เปิด: python main.py                     │
│ 3. เปิด: python dll_injection_tester.py    │
│ 4. เลือก option 2 (Target Scan)            │
│ 5. รอผลลัพธ์                                │
│ 6. ถ้า 0 suspicious → ใช้ได้!               │
│ 7. ถ้ามี warning → ปิดโปรแกรมแล้วทดสอบใหม่  │
└─────────────────────────────────────────────┘
```

### Scenario 2: ตรวจสอบว่า Discord inject อะไรบ้าง

```bash
┌─────────────────────────────────────────────┐
│ ขั้นตอน:                                    │
├─────────────────────────────────────────────┤
│ 1. ปิด Discord                              │
│ 2. เปิด: python main.py                     │
│ 3. รัน DLL Tester → option 2               │
│ 4. บันทึกผลลัพธ์ (baseline: ควรเป็น 0)      │
│ 5. เปิด Discord (พร้อม overlay)            │
│ 6. รัน DLL Tester → option 2 อีกครั้ง      │
│ 7. เปรียบเทียบผล (ควรเห็น discord*.dll)    │
│ 8. ตัดสินใจ: ปิด Discord หรือยอมรับความเสี่ยง│
└─────────────────────────────────────────────┘
```

### Scenario 3: Real-Time Monitoring

```bash
┌─────────────────────────────────────────────┐
│ ขั้นตอน:                                    │
├─────────────────────────────────────────────┤
│ 1. เปิด: python main.py                     │
│ 2. เปิด DLL Tester → option 5              │
│ 3. ขณะที่กำลัง monitor (30 วินาที):        │
│    - ลองเปิด Discord                        │
│    - ลองเปิด OBS                            │
│    - ลองเปิด Browser + Extensions          │
│ 4. สังเกตว่า DLL ไหนถูก inject             │
│ 5. ดูรายงานสรุปหลัง 30 วินาที              │
└─────────────────────────────────────────────┘
```

---

## 📁 ข้อมูลไฟล์

```yaml
Filename: dll_injection_tester.py
Size: ~15 KB (source code)
Type: Python script
Requirements:
  - Python 3.7+
  - psutil library (pip install psutil)

Compiled EXE:
  Filename: DLL_Injection_Tester.exe
  Size: ~5-6 MB
  Requirements: Windows 10/11 (64-bit)
  Python: NOT required (bundled)
```

---

## ⚠️ ข้อควรระวัง

### 1. เครื่องมือนี้ใช้สำหรับทดสอบเท่านั้น
- ✅ อ่าน process memory maps
- ✅ วิเคราะห์ DLL patterns
- ❌ ไม่ inject DLL
- ❌ ไม่แก้ไข process
- ❌ ไม่ส่งข้อมูลไปที่ใด

### 2. False Positives
- Discord overlay = MEDIUM RISK (ไม่อันตรายจริง แต่ตรวจพบได้)
- OBS hook = MEDIUM RISK (ปกติใช้บันทึกวิดีโอ)
- ReshadeIt = MEDIUM RISK (mod graphics)

### 3. ความปลอดภัย
- โปรแกรมนี้ปลอดภัย 100%
- ไม่มีการเชื่อมต่อ internet
- ไม่เก็บข้อมูลส่วนตัว
- Open source (ดูโค้ดได้)

---

## 🏗️ สร้าง Standalone EXE

```bash
# ติดตั้ง PyInstaller
pip install pyinstaller

# Build EXE (แบบง่าย)
pyinstaller --onefile dll_injection_tester.py

# Build EXE (แบบมี icon + ชื่อสวย)
pyinstaller --onefile ^
  --name="DLL_Injection_Tester" ^
  --icon=NONE ^
  --noconsole ^
  dll_injection_tester.py

# ไฟล์ .exe จะอยู่ที่
dist\DLL_Injection_Tester.exe
```

---

## 📞 ติดต่อ / รายงานปัญหา

- **GitHub Issues**: สร้าง issue ที่ repository
- **Documentation**: อ่านเพิ่มเติมใน `ANTI_DETECTION_LAYER_SUMMARY.md`

---

## 📜 License

```
Educational use only
สร้างโดย: Kiro AI Assistant
วันที่: 19 กรกฎาคม 2026
เวอร์ชัน: 1.0
```

---

## 🎉 พร้อมใช้งาน!

**โปรแกรมพร้อมแล้ว! เริ่มทดสอบได้เลย:**

```bash
python dll_injection_tester.py
```

หรือ

```bash
run_dll_tester.bat
```

**Happy Testing! 🛡️**
