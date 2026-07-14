# 🚀 คู่มือเริ่มต้นใช้งาน ESP32 - ฉบับภาษาไทย

## ⚡ เริ่มต้นใน 3 ขั้นตอน (15 นาที)

---

## 📦 สิ่งที่ต้องเตรียม

### อุปกรณ์ (เลือก 1 อย่าง):
- ✅ **Arduino Leonardo** (~300 บาท) - ง่าย, หาง่าย
- ✅ **ESP32-S3** (~150 บาท) - **แนะนำ!** ถูกกว่า, ดีกว่า
- ✅ **SparkFun Pro Micro** (~400 บาท) - ขนาดเล็ก

### ซื้อได้ที่:
- 🛒 **Lazada/Shopee**: ค้นหา "Arduino Leonardo" หรือ "ESP32-S3"
- 🛒 **AliExpress**: ราคา 100-200 บาท (ส่ง 2-4 สัปดาห์)
- 🛒 **ร้านอิเล็กทรอนิกส์ใกล้บ้าน**

---

## ⚙️ ขั้นตอนที่ 1: ติดตั้ง Arduino

### 1.1 ดาวน์โหลด Arduino IDE

ไปที่: https://www.arduino.cc/en/software

- กด **Windows** → ดาวน์โหลด
- ติดตั้งตามปกติ (กด Next ไปเรื่อยๆ)

### 1.2 เสียบ Arduino เข้าคอมพิวเตอร์

- ใช้สาย USB (ต้องเป็นสาย **ข้อมูล** ไม่ใช่สายชาร์จอย่างเดียว)
- Windows จะติดตั้ง Driver อัตโนมัติ

### 1.3 หาหมายเลขพอร์ต COM

**วิธีที่ 1: ใช้ Device Manager**
1. กดปุ่ม Windows + X
2. เลือก **"Device Manager"**
3. เปิด **"Ports (COM & LPT)"**
4. หา **"Arduino Leonardo"** หรือ **"USB Serial Device"**
5. จดหมายเลข เช่น **COM3**, **COM4**

**วิธีที่ 2: ใช้คำสั่ง**
```cmd
cd C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter
python -m serial.tools.list_ports
```

---

## 📤 ขั้นตอนที่ 2: อัพโหลดโค้ด

### 2.1 เปิด Arduino IDE

### 2.2 ตั้งค่า Board
- **Tools** → **Board** → เลือก:
  - Arduino Leonardo (ถ้าใช้ Leonardo)
  - ESP32S3 Dev Module (ถ้าใช้ ESP32-S3)

### 2.3 เลือกพอร์ต
- **Tools** → **Port** → เลือก **COM3** (หรือพอร์ทที่คุณหาเจอ)

### 2.4 เปิดไฟล์
- **File** → **Open**
- ไปที่: `C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter\esp32\Arduino_Mouse\Arduino_Mouse.ino`

### 2.5 อัพโหลด
- กดปุ่ม **→** (Upload) มุมซ้ายบน
- รอ 10-30 วินาที
- ควรเห็น: **"Done uploading"**

**ถ้าอัพโหลดไม่ได้:**
- กดปุ่ม **Reset** บน Arduino 2 ครั้งเร็วๆ (เข้าโหมด Bootloader)
- ลองเปลี่ยนพอร์ต USB
- ปิด Arduino IDE Serial Monitor

---

## ✅ ขั้นตอนที่ 3: ทดสอบการทำงาน

### 3.1 รันคำสั่งทดสอบ

เปิด Command Prompt:
```cmd
cd C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter
python -m heartopia_painter.hardware_mouse
```

### 3.2 ผลลัพธ์ที่ต้องเห็น:

```
Hardware Mouse Controller - Test
==================================================

Available serial ports:
  1. COM3
     Description: Arduino Leonardo
     Manufacturer: Arduino LLC

Auto-detecting Arduino...
Found Arduino at: COM3

Connecting...
Connected: <HardwareMouse connected=COM3 version=1.1.0>

✓ All tests passed!
```

**ถ้าเห็นข้อความนี้ = สำเร็จแล้ว!** 🎉

---

## 🎨 ขั้นตอนที่ 4: เปิดใช้ในโปรแกรม

### 4.1 เปิดแอป Painter

```cmd
cd C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter
python main.py
```

หรือดับเบิลคลิก: `dist\Painter_Stealth.exe`

### 4.2 ไปที่แท็บ "จังหวะ / ความน่าเชื่อถือ"

### 4.3 เปิดใช้ฟีเจอร์:

#### ส่วนที่ 1: Enhanced Timing
- ☑ **เปิดใช้ Enhanced Timing**
- โปรไฟล์: **Default** (แนะนำ)

#### ส่วนที่ 2: Hardware Mouse
- ☑ **ใช้ Hardware Mouse (ESP32/Arduino)**
- พอร์ต: **COM3** (ใส่พอร์ทที่คุณหาเจอ)

#### ส่วนที่ 3: ฟีเจอร์ความสมจริง (แนะนำเปิดทั้งหมด)
- ☑ **Position Jitter** (ความสุ่มตำแหน่ง ±25px)
- ☑ **Micro Pauses** (หยุดสั้นๆ บางครั้ง)
- ☑ **Fatigue Simulation** (เหนื่อยตามเวลา)
- ☑ **Random Breaks** (พักสุ่ม 2-8 วินาที)
- ⬜ **Mistake Simulation** (คลิกพลาดบางครั้ง - ไม่แนะนำถ้าต้องการความเร็ว)

### 4.4 กดปุ่ม "วาดตอนนี้"

---

## 🎯 โปรไฟล์แนะนำ

### 🏃 Fast (เร็ว - เสี่ยงปานกลาง)
```
- Base Delay: 0.03s
- Click Duration: 0.03s
- Movement: 0.2s
- เหมาะสำหรับ: ทดสอบ, วาดรวดเร็ว
- ระดับความปลอดภัย: ⚠️ ปานกลาง
```

### ✅ Default (มาตรฐาน - แนะนำ!)
```
- Base Delay: 0.05s
- Click Duration: 0.05s
- Movement: 0.3s
- เหมาะสำหรับ: ใช้งานปกติ
- ระดับความปลอดภัย: ✅ สูง
```

### 🛡️ Careful (ระมัดระวัง - ปลอดภัยสุด)
```
- Base Delay: 0.10s
- Click Duration: 0.08s
- Movement: 0.5s
- เหมาะสำหรับ: เกมที่เข้มงวดมาก
- ระดับความปลอดภัย: ✅✅ สูงสุด
```

---

## 🔧 แก้ปัญหาที่พบบ่อย

### ❌ หา Arduino ไม่เจอ

**วิธีแก้:**
1. เช็คสาย USB (ต้องเป็นสายข้อมูล)
2. ลองพอร์ต USB อื่น
3. ถอดแล้วเสียบใหม่
4. รีบูตคอมพิวเตอร์
5. ติดตั้ง Arduino Leonardo Driver จาก arduino.cc

**คำสั่งตรวจสอบ:**
```cmd
python -m serial.tools.list_ports
```

---

### ❌ อัพโหลดล้มเหลว

**ข้อผิดพลาด:**
```
avrdude: ser_open(): can't open device
```

**วิธีแก้:**
1. ปิด Arduino IDE Serial Monitor
2. ปิดโปรแกรมที่ใช้พอร์ต COM
3. กดปุ่ม **Reset** บน Arduino 2 ครั้งเร็วๆ
4. ลอง Upload ใหม่ทันที (ภายใน 8 วินาที)

---

### ❌ เมาส์ไม่เคลื่อนที่

**ตรวจสอบ:**
1. ไฟ LED บน Arduino ติดหรือไม่?
2. Device Manager เห็น "Arduino Leonardo" หรือไม่?
3. Upload สำเร็จหรือไม่?

**วิธีแก้:**
```cmd
# ทดสอบการเคลื่อนที่
python -c "from heartopia_painter.hardware_mouse import HardwareMouse; import time; m = HardwareMouse(); m.connect(); m.move(100, 0); time.sleep(1); m.move(-100, 0)"
```

---

### ❌ "Permission Denied" หรือ "Access Denied"

**สาเหตุ:** มีโปรแกรมอื่นใช้พอร์ต COM อยู่

**วิธีแก้:**
1. ปิด Arduino IDE
2. ปิด Serial Monitor ทั้งหมด
3. ปิดโปรแกรม Python อื่นๆ
4. ลองใหม่

---

## 📊 เปรียบเทียบความปลอดภัย

| โหมด | ความเร็ว | ความปลอดภัย | เหมาะกับ |
|------|---------|------------|---------|
| **PyAutoGUI อย่างเดียว** | ⚡⚡⚡ 100% | ⚠️ ต่ำ | ทดสอบเท่านั้น |
| **+ Delay System** | ⚡⚡ 80% | ⚠️ ปานกลาง | เกมทั่วไป |
| **+ Hardware Mouse** | ⚡⚡ 85% | ✅ สูง | เกมปลอดภัย |
| **+ ทุกฟีเจอร์** | ⚡ 70% | ✅✅ สูงสุด | **แนะนำ!** |

---

## ⚙️ ตั้งค่าขั้นสูง (mouse_config.json)

สำหรับผู้ใช้ขั้นสูง สามารถแก้ไขไฟล์:
```
C:\Users\gamwi\Desktop\Code_Dev\HeartopiaAutoPainter\mouse_config.json
```

### ตัวอย่างการตั้งค่า:

```json
{
  "arduino_port": "COM3",
  "click_randomness_px": 25,
  
  "enable_fatigue": true,
  "fatigue_slowdown_per_100_actions": 0.02,
  
  "enable_breaks": true,
  "break_probability_per_100_actions": 0.15,
  "break_min_actions": 50,
  "break_max_actions": 200,
  "break_duration_seconds_min": 2.0,
  "break_duration_seconds_max": 8.0,
  
  "enable_mistakes": false,
  "mistake_probability": 0.01,
  
  "session_time_limit_hours": 3.0,
  "dpi_calibration": 1.0
}
```

### ความหมายแต่ละค่า:

| ตัวแปร | ค่าแนะนำ | คำอธิบาย |
|--------|---------|---------|
| `arduino_port` | "COM3" | พอร์ต Arduino |
| `click_randomness_px` | 25 | ความสุ่มคลิก ±25 พิกเซล |
| `enable_fatigue` | true | เหนื่อยตามเวลา |
| `fatigue_slowdown_per_100_actions` | 0.02 | ช้าลง 2% ทุก 100 คลิก |
| `enable_breaks` | true | พักสุ่ม |
| `break_probability_per_100_actions` | 0.15 | โอกาสพัก 15% ทุก 100 คลิก |
| `break_duration_seconds_min` | 2.0 | พักอย่างน้อย 2 วินาที |
| `break_duration_seconds_max` | 8.0 | พักไม่เกิน 8 วินาที |
| `enable_mistakes` | false | จำลองการคลิกผิด |
| `session_time_limit_hours` | 3.0 | จำกัดเวลา 3 ชั่วโมง |

---

## 🎮 เคล็ดลับการใช้งาน

### ✅ ควรทำ:
1. ใช้โปรไฟล์ "Default" หรือ "Careful"
2. เปิดทุกฟีเจอร์ (ยกเว้น Mistakes)
3. ตั้งเวลาจำกัด 2-3 ชั่วโมง
4. พักทุก 3 ชั่วโมง (หรือเมื่อระบบสั่งหยุด)
5. ตรวจสอบ Arduino ก่อนใช้งานทุกครั้ง

### ❌ ไม่ควรทำ:
1. ใช้โปรไฟล์ "Fast" นานๆ
2. ปิดฟีเจอร์ความสมจริง
3. วาดนานเกิน 4 ชั่วโมงติดต่อกัน
4. ปล่อยทิ้งไว้ตลอดคืน
5. ใช้หลายบัญชีพร้อมกันบนเครื่องเดียว

---

## 📞 ต้องการความช่วยเหลือ?

### เอกสารเพิ่มเติม:
- `ESP32_INTEGRATION_GUIDE.md` - คู่มือครบถ้วน (ภาษาอังกฤษ)
- `DELAY_SYSTEM_README.md` - ระบบ Delay ละเอียด
- `esp32/README_SETUP.txt` - การติดตั้ง ESP32

### คำสั่งที่มีประโยชน์:

**ทดสอบ Arduino:**
```cmd
python -m heartopia_painter.hardware_mouse
```

**ดูพอร์ตทั้งหมด:**
```cmd
python -m serial.tools.list_ports
```

**รันโปรแกรม:**
```cmd
python main.py
```

**Build EXE:**
```cmd
build_stealth.bat
```

---

## ✅ เช็คลิสต์ความพร้อม

ก่อนเริ่มวาด ให้แน่ใจว่า:

- [ ] ซื้อ Arduino Leonardo / ESP32 แล้ว
- [ ] ติดตั้ง Arduino IDE แล้ว
- [ ] อัพโหลดโค้ดสำเร็จ (เห็น "Done uploading")
- [ ] ทดสอบผ่าน (`python -m heartopia_painter.hardware_mouse`)
- [ ] หาพอร์ต COM แล้ว (เช่น COM3)
- [ ] เปิดใช้ Enhanced Timing ในแอป
- [ ] เปิดใช้ Hardware Mouse
- [ ] ใส่พอร์ตในช่อง "พอร์ต:"
- [ ] เลือกโปรไฟล์ Default
- [ ] ติ๊กถูกฟีเจอร์ทั้งหมด (Position Jitter, Micro Pauses, Fatigue, Breaks)
- [ ] ทดสอบวาดสำเร็จแล้ว

**ถ้าติ๊กถูกทุกข้อ = พร้อมใช้งานแล้ว!** 🚀

---

## 🎉 ยินดีด้วย!

คุณพร้อมใช้งาน **Hardware Mouse** แล้ว!

### ข้อดีที่ได้รับ:
- ✅ ตรวจจับไม่ได้เกือบแน่นอน
- ✅ เคลื่อนที่เป็นธรรมชาติเหมือนคน
- ✅ จังหวะเหมือนมนุษย์จริงๆ
- ✅ ปลอดภัยจากระบบ Anti-cheat

### เริ่มวาดได้เลย! 🎨

---

**เวอร์ชัน**: 1.0  
**อัปเดตล่าสุด**: 15 กรกฎาคม 2026  
**ผู้พัฒนา**: Beer-Studio  
**สถานะ**: ✅ พร้อมใช้งาน

**มีปัญหา?** ดูที่: `docs/technical/ESP32_INTEGRATION_GUIDE.md`
