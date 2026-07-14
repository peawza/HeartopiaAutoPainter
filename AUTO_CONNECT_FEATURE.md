# 🔌 Auto-Connect Hardware Mouse Feature

## 📋 ภาพรวม

ฟีเจอร์ **Auto-Connect** จะทำการ**ตรวจสอบและเชื่อมต่อ Hardware Mouse อัตโนมัติ**เมื่อเปิดโปรแกรม

---

## ✨ การทำงาน

### 1. เมื่อเปิดโปรแกรม (`python main.py`)

โปรแกรมจะทำตามลำดับ:

1. โหลด config.json
2. ตรวจสอบว่า `use_hardware_mouse` เปิดอยู่หรือไม่
3. ถ้าเปิด → **Auto-detect Arduino/ESP32**
4. พยายามเชื่อมต่อ
5. แสดงผลลัพธ์ใน Console
6. **แสดง Popup แจ้งเตือน** ใน UI

---

## 🎨 Popup แจ้งเตือน

### ✅ เชื่อมต่อสำเร็จ

```
╔════════════════════════════════════════╗
║      🎮 Hardware Mouse                 ║
╠════════════════════════════════════════╣
║ ✅ เชื่อมต่อ Hardware Mouse สำเร็จ!    ║
║                                        ║
║ พอร์ต: COM3                            ║
║ เวอร์ชัน: 1.1.0 (2026-07-14)          ║
║ สถานะ: commands=0, moves=0, clicks=0  ║
║                                        ║
║ 🎨 พร้อมวาดด้วยความปลอดภัยสูงสุด!    ║
╚════════════════════════════════════════╝
```

### ⚠️ ไม่พบ Arduino

```
╔════════════════════════════════════════╗
║      ⚠️ Hardware Mouse                 ║
╠════════════════════════════════════════╣
║ ❌ ไม่พบ Arduino/ESP32                 ║
║                                        ║
║ กรุณาตรวจสอบ:                          ║
║   1. เสียบ Arduino เข้า USB แล้ว       ║
║   2. ติดตั้ง Driver แล้ว              ║
║   3. เช็ค Device Manager (Windows)     ║
║                                        ║
║ หรือตั้งค่าพอร์ตใน mouse_config.json   ║
╚════════════════════════════════════════╝
```

### ⚠️ เชื่อมต่อผิดพลาด

```
╔════════════════════════════════════════╗
║      ⚠️ Hardware Mouse                 ║
╠════════════════════════════════════════╣
║ ⚠️ เชื่อมต่อ COM3 ไม่สำเร็จ            ║
║                                        ║
║ [Error details]                        ║
║                                        ║
║ จะใช้ PyAutoGUI แทน                    ║
╚════════════════════════════════════════╝
```

---

## 📝 Console Output

### เมื่อ Hardware Mouse ปิดอยู่

```
[INFO] Hardware Mouse: Disabled
```

### เมื่อเปิดและหา Arduino ไม่เจอ

```
[INFO] Hardware Mouse: Enabled - Testing connection...
[INFO] Auto-detecting Arduino/ESP32...
[WARNING] Arduino/ESP32 not detected
[INFO] Please check:
  1. Arduino is plugged in via USB
  2. Drivers are installed
  3. Check Device Manager for COM port
[INFO] You can manually set port in mouse_config.json
```

### เมื่อเชื่อมต่อสำเร็จ

```
[INFO] Hardware Mouse: Enabled - Testing connection...
[INFO] Connecting to COM3...
[SUCCESS] ✓ Hardware Mouse connected!
[INFO] Port: COM3
[INFO] Version: 1.1.0
[SUCCESS] ✓ Ping successful
[INFO] Device stats: {'commands': 0, 'moves': 0, 'clicks': 0, 'delay': 0}
[INFO] Connection test complete - ready to use!
```

---

## ⚙️ การตั้งค่า

### config.json

```json
{
  "use_hardware_mouse": true,
  "hardware_mouse_port": null,
  "hardware_mouse_auto_detect": true
}
```

| ตัวแปร | ค่า | คำอธิบาย |
|--------|-----|---------|
| `use_hardware_mouse` | `true` / `false` | เปิด/ปิด Hardware Mouse |
| `hardware_mouse_port` | `"COM3"` / `null` | ระบุพอร์ต หรือ `null` เพื่อ auto-detect |
| `hardware_mouse_auto_detect` | `true` / `false` | เปิด/ปิด auto-detection |

### mouse_config.json

```json
{
  "arduino_port": "COM3"
}
```

ถ้าตั้งค่า `arduino_port` ใน mouse_config.json จะใช้พอร์ตนี้ก่อน

---

## 🔄 ลำดับการหาพอร์ต

1. ตรวจสอบ `config.json` → `hardware_mouse_port`
2. ถ้าไม่มี → ตรวจสอบ `mouse_config.json` → `arduino_port`
3. ถ้ายังไม่มี → **Auto-detect** (หา Arduino/Leonardo/ESP32)

---

## 🎯 Use Cases

### กรณีที่ 1: ใช้ Hardware Mouse

1. เสียบ Arduino เข้า USB
2. เปิด `config.json`
3. ตั้งค่า `"use_hardware_mouse": true`
4. รัน `python main.py`
5. **Popup จะแสดงว่าเชื่อมต่อสำเร็จ** ✅

### กรณีที่ 2: ไม่มี Arduino

1. เปิด `config.json`
2. ตั้งค่า `"use_hardware_mouse": true`
3. รัน `python main.py` (ไม่มี Arduino เสียบ)
4. **Popup จะแจ้งว่าไม่พบ Arduino** ⚠️
5. โปรแกรมใช้ PyAutoGUI แทน

### กรณีที่ 3: ปิด Hardware Mouse

1. เปิด `config.json`
2. ตั้งค่า `"use_hardware_mouse": false`
3. รัน `python main.py`
4. **ไม่มี Popup** (ใช้ PyAutoGUI ตั้งแต่ต้น)

---

## 🛠️ Troubleshooting

### Popup ไม่แสดง

**สาเหตุ**: `use_hardware_mouse: false`

**แก้ไข**:
```json
{
  "use_hardware_mouse": true
}
```

### หา Arduino ไม่เจอ

**สาเหตุ**: 
- Arduino ไม่ได้เสียบ
- Driver ไม่ได้ติดตั้ง
- Port ผิด

**แก้ไข**:
1. เช็ค Device Manager (Windows)
2. หาพอร์ต COM (เช่น COM3, COM4)
3. ตั้งค่าใน `mouse_config.json`:
   ```json
   {
     "arduino_port": "COM3"
   }
   ```

### เชื่อมต่อล้มเหลว

**สาเหตุ**:
- Firmware ยังไม่ได้อัพโหลด
- พอร์ตถูกใช้โดยโปรแกรมอื่น
- Arduino เสียหาย

**แก้ไข**:
1. อัพโหลด firmware: `cd esp32 && upload.bat`
2. ปิดโปรแกรมที่ใช้พอร์ต COM (Arduino IDE, Serial Monitor)
3. ถอดแล้วเสียบ Arduino ใหม่

---

## 💻 Technical Details

### Function Flow

```python
main.py
  └─> app.run()
       ├─> QtWidgets.QApplication([])
       ├─> _test_hardware_mouse_connection()  # ← ฟังก์ชันใหม่
       │    ├─> load_config()
       │    ├─> check use_hardware_mouse
       │    ├─> find_arduino_port()
       │    ├─> HardwareMouse().connect()
       │    └─> return result dict
       ├─> MainWindow()
       ├─> w.show()
       └─> QTimer.singleShot(500, show_popup)  # ← แสดง Popup
```

### Result Dictionary

```python
{
    'success': bool,      # True if connected successfully
    'enabled': bool,      # True if hardware mouse is enabled in config
    'port': str | None,   # COM port (e.g., "COM3")
    'version': str | None, # Firmware version (e.g., "1.1.0")
    'message': str | None  # Message to display in popup
}
```

---

## 🎉 ผลลัพธ์

### ✅ ข้อดี

1. **ไม่ต้องกังวล**: รู้ทันทีว่าเชื่อมต่อสำเร็จหรือไม่
2. **ประหยัดเวลา**: ไม่ต้องเช็คเอง
3. **ใช้งานง่าย**: เสียบ Arduino → เปิดโปรแกรม → เสร็จ!
4. **Fallback**: ถ้าเชื่อมต่อไม่ได้ ใช้ PyAutoGUI แทนอัตโนมัติ

### 📊 User Experience

```
เสียบ Arduino
    ↓
เปิดโปรแกรม (python main.py)
    ↓
[หน้าจอโหลด 0.5 วินาที]
    ↓
✅ Popup: "เชื่อมต่อสำเร็จ!"
    ↓
กด OK
    ↓
เริ่มใช้งานได้ทันที!
```

---

## 📚 เอกสารที่เกี่ยวข้อง

- `QUICKSTART_ESP32.md` - คู่มือเริ่มต้น
- `ESP32_INTEGRATION_TASKS.md` - Task plan
- `mouse_config.json` - Configuration file
- `src/heartopia_painter/app.py` - Source code

---

## 🔮 Future Improvements

- [ ] เพิ่มปุ่ม "Reconnect" ใน Popup
- [ ] แสดงรายชื่อพอร์ตที่พบทั้งหมด
- [ ] บันทึก log การเชื่อมต่อ
- [ ] Status indicator ใน UI (สีเขียว = connected)

---

**เวอร์ชัน**: 1.0  
**วันที่**: 15 กรกฎาคม 2026  
**ผู้พัฒนา**: Beer-Studio  

**Status**: ✅ Production Ready
