#!/usr/bin/env python3
"""
Test Logitech Device (COM6) Connection
ทดสอบการเชื่อมต่อกับ Logitech device ที่ใช้เป็น HID emulator
"""

import serial
import time
import sys

def test_connection(port='COM6', baudrate=115200):
    """ทดสอบการเชื่อมต่อ"""
    
    print("=" * 70)
    print(f"🔌 Testing Connection to {port}")
    print("=" * 70)
    print()
    
    try:
        print(f"[1/6] Opening port {port} at {baudrate} baud...")
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=2.0,
            write_timeout=2.0
        )
        print(f"✅ Port opened successfully")
        print()
        
        # Give device time to initialize
        print(f"[2/6] Waiting 2 seconds for device initialization...")
        time.sleep(2.0)
        print(f"✅ Ready")
        print()
        
        # Check if there's any data waiting
        print(f"[3/6] Checking for startup messages...")
        if ser.in_waiting > 0:
            print(f"📬 {ser.in_waiting} bytes available")
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"   << {line}")
        else:
            print(f"⚠️  No startup messages")
        print()
        
        # Try sending ping
        print(f"[4/6] Sending PING command...")
        ser.write(b'P\n')
        ser.flush()
        print(f"   >> P")
        
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"   << {response}")
            
            if response == "PONG":
                print(f"✅ Device responded with PONG!")
            else:
                print(f"⚠️  Unexpected response: {response}")
        else:
            print(f"❌ No response to PING")
        print()
        
        # Try version command
        print(f"[5/6] Sending VERSION command...")
        ser.write(b'V\n')
        ser.flush()
        print(f"   >> V")
        
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"   << {response}")
            
            if response.startswith("VERSION:"):
                version = response.split(":", 1)[1]
                print(f"✅ Device version: {version}")
            else:
                print(f"⚠️  Unexpected response: {response}")
        else:
            print(f"❌ No response to VERSION")
        print()
        
        # Try mouse move test
        print(f"[6/6] Sending TEST mouse move command...")
        ser.write(b'M 10 10\n')
        ser.flush()
        print(f"   >> M 10 10")
        
        time.sleep(0.5)
        
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"   << {response}")
            
            if response == "OK":
                print(f"✅ Mouse move OK!")
            else:
                print(f"⚠️  Unexpected response: {response}")
        else:
            print(f"❌ No response to MOVE")
        print()
        
        # Close connection
        ser.close()
        print(f"✅ Connection closed")
        print()
        
        print("=" * 70)
        print("📊 Summary:")
        print("=" * 70)
        print("✅ Port can be opened")
        print("⚠️  Check responses above to see if device is compatible")
        print()
        print("💡 Compatible device should respond:")
        print("   P → PONG")
        print("   V → VERSION:x.x.x")
        print("   M x y → OK")
        print()
        
        return True
        
    except serial.SerialException as e:
        print(f"❌ Serial Error: {e}")
        print()
        print("💡 Possible causes:")
        print("   1. Port is already open by another program")
        print("   2. Port doesn't exist")
        print("   3. Permission denied")
        print("   4. Device is not ready")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_raw_hid():
    """ทดสอบว่า device นี้เป็น HID device หรือไม่"""
    
    print("\n" + "=" * 70)
    print("🎮 Checking if device is HID (Human Interface Device)")
    print("=" * 70)
    print()
    
    try:
        import hid
        
        print("Scanning HID devices...")
        devices = hid.enumerate()
        
        logitech_devices = [d for d in devices if d['vendor_id'] == 0x046D]
        
        if logitech_devices:
            print(f"✅ Found {len(logitech_devices)} Logitech HID device(s):")
            for dev in logitech_devices:
                print(f"   - {dev['product_string']}")
                print(f"     VID:PID = {dev['vendor_id']:04X}:{dev['product_id']:04X}")
                print(f"     Usage: {dev.get('usage_page', 'N/A')} / {dev.get('usage', 'N/A')}")
            print()
            print("💡 This is an HID device, not a serial device!")
            print("   Serial commands (P, V, M) won't work on HID devices.")
        else:
            print("⚠️  No Logitech HID devices found")
            
    except ImportError:
        print("⚠️  'hidapi' not installed. Install with:")
        print("   pip install hidapi")
        print()
        print("💡 Or check Device Manager to see if it's HID")


if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else 'COM6'
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    # Test serial connection
    test_connection(port, baudrate)
    
    # Test HID
    test_raw_hid()
    
    print("\n" + "=" * 70)
    print("🎯 Conclusion:")
    print("=" * 70)
    print()
    print("If device responded to P/V/M commands:")
    print("   ✅ Compatible! Update config.json and mouse_config.json")
    print()
    print("If device did NOT respond:")
    print("   ❌ This is likely a real Logitech mouse (HID), not Arduino")
    print("   💡 Either:")
    print("      1. Flash Arduino firmware to a real Arduino/ESP32")
    print("      2. Use PyAutoGUI instead (disable Hardware Mouse)")
    print("=" * 70)
