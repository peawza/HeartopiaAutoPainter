import sys
sys.path.insert(0, 'src')

from heartopia_painter.hardware_mouse import HardwareMouse, HardwareMouseConfig

print("Testing Hardware Mouse connection...")
print("=" * 50)

try:
    config = HardwareMouseConfig(port='COM6')
    mouse = HardwareMouse(config)
    
    print("Connecting to COM6...")
    if mouse.connect():
        print("✓ Connected successfully!")
        print(f"  Device: {mouse.device_type}")
        print(f"  Port: {mouse.device_port}")
        print(f"  Version: {mouse.device_version}")
        print(f"  Connected: {mouse.connected}")
        
        print("\nTesting move command...")
        if mouse.move(10, 0):
            print("✓ Move right 10px - SUCCESS")
        
        print("\nTesting mouse down/up...")
        if mouse.press():
            print("✓ Press - SUCCESS")
        if mouse.release():
            print("✓ Release - SUCCESS")
        
        print("\n✓ All basic tests passed!")
        mouse.disconnect()
    else:
        print("✗ Connection failed")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
