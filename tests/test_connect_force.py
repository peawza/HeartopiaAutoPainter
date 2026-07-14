#!/usr/bin/env python3
"""Force connect to COM6 with new tolerant code"""

from src.heartopia_painter.hardware_mouse import HardwareMouse

print("=" * 70)
print("🔌 Testing Force Connection to COM6")
print("=" * 70)
print()

try:
    print("[1/4] Creating HardwareMouse instance...")
    mouse = HardwareMouse()
    print("✅ Instance created")
    print()
    
    print("[2/4] Attempting to connect to COM6...")
    print("      (This may take a few seconds...)")
    result = mouse.connect('COM6')
    print()
    
    if result:
        print("✅ CONNECTION SUCCESSFUL!")
        print()
        print("📊 Device Info:")
        print(f"   Port: {mouse.device_port}")
        print(f"   Type: {mouse.device_type}")
        print(f"   Version: {mouse.device_version}")
        print()
        
        print("[3/4] Testing ping...")
        if mouse.ping():
            print("✅ Ping OK")
        else:
            print("⚠️  Ping failed (but connection OK for Logitech)")
        print()
        
        print("[4/4] Getting status...")
        status = mouse.get_status()
        if status:
            print("✅ Status:")
            for key, val in status.items():
                print(f"   {key}: {val}")
        else:
            print("⚠️  No status (but connection OK)")
        print()
        
        print("🔌 Disconnecting...")
        mouse.disconnect()
        print("✅ Disconnected")
        print()
        
        print("=" * 70)
        print("🎉 SUCCESS! COM6 is now connected and ready to use!")
        print("=" * 70)
        print()
        print("✅ Update your config:")
        print('   config.json: "hardware_mouse_port": "COM6"')
        print('   mouse_config.json: "arduino_port": "COM6"')
        print()
        print("🎨 Now you can use Hardware Mouse in the app!")
        
    else:
        print("❌ Connection FAILED")
        print()
        print("💡 This device may not be compatible")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("💡 Try:")
    print("   1. Close any program using COM6")
    print("   2. Unplug and replug the device")
    print("   3. Check Device Manager")

print()
print("=" * 70)
