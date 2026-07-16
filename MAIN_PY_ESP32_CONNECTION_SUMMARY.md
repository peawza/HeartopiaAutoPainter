# `main.py` และการเชื่อมต่อ ESP สำหรับ Hardware Click

เอกสารนี้สรุป call path ปัจจุบันของโปรแกรมเมื่อใช้โหมด **โปรแกรมขยับ cursor + ESP/Arduino คลิก** โดยไม่เปลี่ยน logic ของเมาส์ Logitech หรือ USB detection เดิม

## สรุปสั้น

`main.py` เป็น launcher ไม่ได้เปิด COM port เอง จุดที่เชื่อมต่อ ESP จริงคือ `HardwareMouse` ใน `src/heartopia_painter/hardware_mouse.py`

```text
main.py
  -> app.run(...)
  -> MainWindow สร้าง PainterOptions
  -> paint_grid()
  -> _create_mouse_controller()
  -> HardwareMouse.connect()
  -> ESP รับ D/U สำหรับคลิก
```

Logitech เป็นเมาส์ HID ที่ Windows ใช้งานอยู่แล้ว โปรแกรมจึงขยับ cursor ผ่าน PyAutoGUI/pynput ส่วน ESP รับเฉพาะคำสั่งกดและปล่อยปุ่มเมาส์

## วิธีเปิดใช้งาน

```powershell
python main.py --hardware-click --port COM6 --baudrate 115200
```

ตัวเลือกใน `main.py`:

| Argument | หน้าที่ |
|---|---|
| `--hardware-click` | เปิดโหมดให้ ESP เป็นผู้คลิก |
| `--port COM6` | ระบุ COM port ของ ESP แบบ session-only |
| `--baudrate 115200` | ความเร็ว serial; ค่าเริ่มต้นคือ `115200` |

ถ้าไม่ระบุ `--port` ระบบจะใช้ค่าตามลำดับนี้:

1. port จาก command line
2. `config.json` ที่ `hardware_mouse_port`
3. `mouse_config.json` ที่ `arduino_port`

## ขั้นตอนใน `main.py`

เมื่อไม่มี `--arduino-example`, `main()` จะเรียก `_run_gui()` และส่งค่าไปยัง `app.run()`:

```python
_run_gui(
    hardware_click=args.hardware_click,
    port=args.port,
    baudrate=args.baudrate,
)
```

จากนั้น `app.py` ส่งค่าเข้า `PainterOptions` เป็น:

```python
hardware_click_only=True
hardware_mouse_port="COM6"
hardware_mouse_baudrate=115200
```

ค่าเหล่านี้เป็น override เฉพาะ session และไม่เขียนทับ config เดิม

## จุดที่เชื่อมต่อ ESP จริง

ใน `paint.py` เมื่อ `hardware_click_only=True` ระบบจะสร้าง `HardwareMouseConfig` แล้วเรียก:

```python
hardware_click.connect()
```

`HardwareMouse.connect()` ทำงานดังนี้:

1. เปิด serial ด้วย port, baudrate และ timeout ที่กำหนด
2. รออุปกรณ์ reset หลังเปิด COM
3. อ่านและล้าง startup messages เช่น `READY` และ `VERSION`
4. ส่งคำสั่ง `V` เพื่ออ่าน firmware version ถ้ามี
5. ตั้งสถานะ `connected=True`
6. เริ่ม health monitor สำหรับ firmware ที่รองรับ ping

ใน startup preflight ของ `app.py` ถ้า `use_hardware_mouse` ใน config เปิดอยู่ ระบบจะเรียก `connect()`, `ping()` และ `get_status()` เพื่อตรวจสอบก่อนแสดง GUI ด้วย

> หมายเหตุ: เมื่อใช้ `--hardware-click` อย่างเดียว การเชื่อมต่อที่จำเป็นจริงจะเกิดตอนเริ่ม paint/erase ผ่าน `_create_mouse_controller()` หาก config เดิมไม่ได้เปิด `use_hardware_mouse` startup preflight อาจแสดงว่า Hardware Mouse disabled แต่การวาดจะยัง connect ด้วย port ที่ส่งผ่าน CLI ได้

## ขั้นตอนคลิก

เมื่อ cursor ถูกโปรแกรมขยับไปยังตำแหน่งเป้าหมายแล้ว:

```text
MouseController.press()
  -> HardwareMouse.press()
  -> ส่ง D\\n
MouseController.release()
  -> HardwareMouse.release()
  -> ส่ง U\\n
```

ESP ต้องตอบ `OK` หลังแต่ละคำสั่ง ถ้าเกิด exception ระหว่างช่วงกด ระบบใช้ `finally` เพื่อพยายามส่ง `U` ป้องกันปุ่มค้าง

ในโหมดนี้:

- ไม่ส่งคำสั่ง `M` หรือ `MS` ไปยัง ESP
- ไม่ใช้ ESP ขยับ cursor
- ปิด click-position randomness เพื่อรักษาพิกัดเดิม
- ตรวจว่า hardware click device ยัง `connected` ก่อนส่ง `D`
- ถ้า ESP หลุดหรือไม่ตอบ ระบบ raise error และหยุดการวาด
- ไม่มี fallback ไปคลิกด้วย software

## การตรวจสอบแบบ command line

ตรวจรายการ serial port:

```powershell
python main.py --arduino-example 1
```

ทดสอบการเชื่อมต่อและ `P -> PONG` โดยไม่เปิด GUI:

```powershell
python main.py --arduino-example 3 --port COM6
```

ทดสอบ `HardwareMouse` จริงและอ่าน status:

```powershell
python main.py --arduino-example 5 --port COM6
```

## Logitech กับ ESP แยกหน้าที่กันอย่างไร

| อุปกรณ์ | หน้าที่ในโหมด `--hardware-click` |
|---|---|
| Logitech/Windows HID | รับการเคลื่อน cursor จาก PyAutoGUI/pynput |
| ESP/Arduino serial HID | รับ `D` และ `U` เพื่อกด/ปล่อยคลิก |
| `main.py` | รับ arguments และส่ง runtime options ต่อไปยัง app |

ดังนั้น `main.py` ไม่ได้เปิด connection กับ Logitech ผ่าน COM และไม่มีการแก้ logic Logitech detection ในโหมดนี้

## ข้อจำกัดของ firmware

ไฟล์ `esp32/Arduino_Mouse/Arduino_Mouse.ino` ปัจจุบันใช้ `Mouse.h` และระบุ board หลักเป็น Arduino Leonardo/Pro Micro (ATmega32U4) หากใช้ ESP32 จริง ต้องเป็นรุ่นและ Arduino core ที่รองรับ native USB HID ตาม firmware ที่ติดตั้งอยู่

## ไฟล์อ้างอิงหลัก

- [`main.py`](main.py)
- [`app.py`](src/heartopia_painter/app.py)
- [`paint.py`](src/heartopia_painter/paint.py)
- [`enhanced_paint.py`](src/heartopia_painter/enhanced_paint.py)
- [`hardware_mouse.py`](src/heartopia_painter/hardware_mouse.py)
- [`Arduino_Mouse.ino`](esp32/Arduino_Mouse/Arduino_Mouse.ino)
