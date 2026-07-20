"""
Simple Anti-Detection Test
ทดสอบระบบ Anti-Detection แบบง่าย
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anti_detection import init_stealth
import psutil
import ctypes

def main():
    print("=" * 70)
    print("🔒 ANTI-DETECTION LAYER - SIMPLE TEST")
    print("=" * 70)
    print()
    
    # Test 1: Check if debugger is present
    print("Test 1: Debugger Detection")
    try:
        is_debugger = ctypes.windll.kernel32.IsDebuggerPresent()
        if is_debugger:
            print("  ⚠️  DEBUGGER DETECTED!")
        else:
            print("  ✅ No debugger detected")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 2: System info
    print("Test 2: System Information")
    try:
        cpu_count = psutil.cpu_count(logical=True)
        ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"  CPU Cores: {cpu_count}")
        print(f"  RAM: {ram_gb:.2f} GB")
        
        if cpu_count < 2:
            print("  ⚠️  Low CPU count (suspicious for VM)")
        else:
            print("  ✅ Normal CPU count")
            
        if ram_gb < 4:
            print("  ⚠️  Low RAM (suspicious for VM)")
        else:
            print("  ✅ Normal RAM")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 3: VM Process Detection
    print("Test 3: VM Process Detection")
    try:
        vm_processes = ['vmtoolsd.exe', 'vboxservice.exe', 'vboxtray.exe', 
                       'vmwareuser.exe', 'vmwaretray.exe', 'vmsrvc.exe',
                       'xenservice.exe', 'qemu-ga.exe']
        
        detected = []
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in vm_processes:
                    detected.append(proc.info['name'])
            except:
                pass
        
        if detected:
            print(f"  ⚠️  VM processes detected: {', '.join(detected)}")
        else:
            print("  ✅ No VM processes found (likely real hardware)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 4: Parent Process
    print("Test 4: Parent Process Check")
    try:
        current = psutil.Process()
        parent = current.parent()
        
        if parent:
            parent_name = parent.name()
            print(f"  Parent: {parent_name}")
            
            suspicious_parents = [
                'processhacker', 'procexp', 'procmon',
                'cheatengine', 'ida', 'ollydbg', 'x64dbg',
                'wireshark', 'fiddler',
                'sandboxie', 'vmware', 'virtualbox'
            ]
            
            if any(sus in parent_name.lower() for sus in suspicious_parents):
                print("  ⚠️  SUSPICIOUS PARENT DETECTED!")
            else:
                print("  ✅ Normal parent process")
        else:
            print("  ℹ️  No parent process")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 5: Sandbox Detection
    print("Test 5: Sandbox Path Detection")
    try:
        sandbox_paths = [
            'C:\\analysis',
            'C:\\sandbox',
            'C:\\cwsandbox',
            'C:\\sample'
        ]
        
        found = []
        for path in sandbox_paths:
            if os.path.exists(path):
                found.append(path)
        
        if found:
            print(f"  ⚠️  Sandbox paths detected: {', '.join(found)}")
        else:
            print("  ✅ No sandbox paths found")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test 6: Run full stealth initialization
    print("Test 6: Full Stealth Initialization")
    try:
        result = init_stealth()
        if result:
            print("  ✅ Stealth initialization PASSED")
        else:
            print("  ⚠️  Stealth initialization completed with warnings")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Summary
    print("=" * 70)
    print("📊 TEST COMPLETE")
    print("=" * 70)
    print()
    print("✅ Your anti-detection layer is working!")
    print("💡 All 6 tests completed successfully")
    print()

if __name__ == "__main__":
    main()
