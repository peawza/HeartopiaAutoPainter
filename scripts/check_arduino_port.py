#!/usr/bin/env python3
"""
Arduino/ESP32 Port Checker
ตรวจสอบและแสดงข้อมูลพอร์ต COM ทั้งหมด
"""

import serial.tools.list_ports

# Known Arduino/ESP32 VID:PID pairs
ARDUINO_VENDORS = {
    '2341': 'Arduino',
    '1A86': 'CH340 (cheap Arduino clone)',
    '10C4': 'CP210x (ESP32)',
    '0403': 'FTDI (Arduino compatible)',
    '067B': 'Prolific (Arduino compatible)',
}

def check_ports():
    """สแกนและแสดงข้อมูลพอร์ตทั้งหมด"""
    
    print("=" * 70)
    print("🔍 Arduino/ESP32 Port Checker")
    print("=" * 70)
    print()
    
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ ไม่พบ COM port ใดๆ")
        return
    
    print(f"พบทั้งหมด {len(ports)} พอร์ต:\n")
    
    arduino_found = False
    
    for i, port in enumerate(ports, 1):
        print(f"[{i}] {port.device}")
        print(f"    📝 Description: {port.description}")
        print(f"    🔌 HWID: {port.hwid}")
        
        # Extract VID:PID
        vid_pid = None
        if 'VID:PID=' in port.hwid:
            vid_pid_str = port.hwid.split('VID:PID=')[1].split()[0]
            vid_pid = vid_pid_str.upper()
            vid = vid_pid.split(':')[0]
            
            # Check if it's Arduino
            if vid in ARDUINO_VENDORS:
                vendor_name = ARDUINO_VENDORS[vid]
                print(f"    ⭐ นี่คือ {vendor_name}!")
                arduino_found = True
            else:
                print(f"    ⚠️  VID:PID = {vid_pid} (ไม่ใช่ Arduino)")
        
        # Check description for Arduino keywords
        desc_lower = port.description.lower()
        arduino_keywords = ['arduino', 'leonardo', 'pro micro', 'atmega', 'esp32', 'ch340']
        
        for keyword in arduino_keywords:
            if keyword in desc_lower:
                if not arduino_found:
                    print(f"    💡 พบคำว่า '{keyword}' ในชื่อ - อาจเป็น Arduino")
                break
        
        print()
    
    print("=" * 70)
    
    if arduino_found:
        print("✅ พบ Arduino/ESP32 แล้ว! ใช้พอร์ตที่มี ⭐")
    else:
        print("❌ ไม่พบ Arduino/ESP32")
        print()
        print("💡 แนะนำ:")
        print("   1. ตรวจสอบว่าเสียบ Arduino เข้า USB แล้ว")
        print("   2. ตรวจสอบว่าติดตั้ง Driver แล้ว (CH340/CP210x)")
        print("   3. เช็คใน Device Manager (devmgmt.msc)")
        print("   4. ลอง upload firmware ใหม่")
        print()
        print("📁 Firmware location:")
        print("   esp32/Arduino_Mouse/Arduino_Mouse.ino")
    
    print("=" * 70)


def test_connection(port_name):
    """ทดสอบการเชื่อมต่อกับ Arduino"""
    
    print(f"\n🔌 ทดสอบการเชื่อมต่อกับ {port_name}...")
    print("-" * 70)
    
    try:
        from src.heartopia_painter.hardware_mouse import HardwareMouse
        
        mouse = HardwareMouse()
        
        if mouse.connect(port_name):
            print(f"✅ เชื่อมต่อสำเร็จ!")
            print(f"   Port: {mouse.device_port}")
            print(f"   Version: {mouse.device_version}")
            
            # Test ping
            if mouse.ping():
                print(f"✅ Ping สำเร็จ")
            else:
                print(f"⚠️  Ping ล้มเหลว (แต่เชื่อมต่อได้)")
            
            # Test status
            status = mouse.get_status()
            if status:
                print(f"📊 Status:")
                for key, val in status.items():
                    print(f"   - {key}: {val}")
            
            mouse.disconnect()
            print(f"✅ Disconnect สำเร็จ")
            
            return True
        else:
            print(f"❌ เชื่อมต่อล้มเหลว")
            print(f"💡 พอร์ตนี้อาจไม่ใช่ Arduino หรือยังไม่ได้ upload firmware")
            return False
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False


if __name__ == "__main__":
    # Show all ports
    check_ports()
    
    # Test specific port if provided
    import sys
    if len(sys.argv) > 1:
        port_to_test = sys.argv[1]
        test_connection(port_to_test)
    else:
        print("\n💡 ต้องการทดสอบพอร์ต? รัน:")
        print("   python check_arduino_port.py COM6")
