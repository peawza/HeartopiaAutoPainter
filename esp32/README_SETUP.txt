===========================================
Arduino Leonardo Setup Guide - USB Spoofing
===========================================

เลือกวิธีใดวิธีหนึ่ง: ESP32 (แนะนำ) หรือ Leonardo (ใช้ USB spoofing)

===========================================
วิธีที่ 1: ESP32-S3 / S2 (แนะนำ)
===========================================

ทำไมต้อง ESP32?
- รองรับ USB descriptor spoofing แบบ runtime
- ไม่ต้องแก้ไข boards.txt
- ใช้ USB.productName() ตั้งชื่อได้เลย

ขั้นตอน:
1. รัน install_esp32.bat
2. ตั้งค่า Arduino IDE:
   - Board: ESP32S3 Dev Module
   - USB Mode: USB-OTG (TinyUSB)
   - USB CDC On Boot: Disabled
3. Upload Arduino_Mouse.ino
4. เสร็จ! Windows จะเห็น "Logitech G Pro X Superlight"

===========================================
วิธีที่ 2: Arduino Leonardo (ต้อง spoof USB)
===========================================

ข้อจำกัด:
- ต้องแก้ไขไฟล์ boards.txt (ระบบไฟล์)
- ทุกครั้งที่ compile จะใช้ชื่อ Logitech (ไม่สามารถเปลี่ยนกลับได้ง่าย)

ขั้นตอนติดตั้ง:
------------------

1. รัน spoof_usb_leonardo.bat
   - จะแก้ไข boards.txt อัตโนมัติ
   - สำรองไฟล์เดิมไว้ที่ boards.txt.backup_original

2. Restart Arduino IDE (สำคัญมาก!)

3. ตั้งค่า Arduino IDE:
   - Board: Arduino Leonardo
   - Port: เลือก COM port ของ Leonardo

4. Upload Arduino_Mouse.ino

5. ตรวจสอบใน Device Manager:
   - ต้องเห็น "HID-compliant mouse" หรือ
   - "Logitech G Pro X Superlight" (ถ้า driver รู้จัก VID/PID)

6. ถ้าต้องการคืนค่าเดิม:
   - รัน restore_usb_leonardo.bat
   - Restart Arduino IDE

หมายเหตุ:
----------
- Leonardo ต้องมี ATmega32U4 (มี USB native)
- Arduino Uno / Nano ใช้ไม่ได้ (ไม่มี USB HID)
- Pro Micro (SparkFun) ใช้ได้ (เป็น ATmega32U4 เหมือนกัน)

===========================================
ปัญหาที่พบบ่อย
===========================================

Q: Compile error "USB.h: No such file or directory"
A: ใช้ ESP32 แต่ยังไม่ได้ติดตั้ง ESP32 core
   → รัน install_esp32.bat

Q: Leonardo upload แล้วแต่ไม่เห็นชื่อ Logitech
A: ลืม restart Arduino IDE หลังรัน spoof_usb_leonardo.bat
   → Restart IDE แล้ว upload ใหม่

Q: ต้องการเปลี่ยนกลับเป็น Arduino Leonardo ปกติ
A: รัน restore_usb_leonardo.bat แล้ว restart IDE

Q: Python ไม่เจอ serial port
A: ตรวจสอบ COM port ใน Device Manager
   → Leonardo จะขึ้น 2 ports (เลือกตัวที่ไม่ใช่ bootloader)
