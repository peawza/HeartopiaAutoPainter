#!/usr/bin/env python3
"""
ESP32 Setup Test Script - HeartopiaAutoPainter
ตรวจสอบความพร้อมของระบบ Hardware Mouse อัตโนมัติ
"""

import sys
import os
from pathlib import Path

# Color output for Windows
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ''

def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    """Print info message"""
    print(f"  {text}")

def test_imports():
    """Test 1: Check required Python packages"""
    print_header("Test 1: Python Packages")
    
    results = []
    
    # Essential packages
    packages = [
        ('serial', 'pyserial'),
        ('PySide6', 'PySide6'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy'),
    ]
    
    for module, package in packages:
        try:
            __import__(module)
            print_success(f"{package} installed")
            results.append(True)
        except ImportError:
            print_error(f"{package} NOT installed")
            print_info(f"Install: pip install {package}")
            results.append(False)
    
    return all(results)

def test_project_files():
    """Test 2: Check required project files exist"""
    print_header("Test 2: Project Files")
    
    base = Path(__file__).parent
    files = [
        'src/heartopia_painter/hardware_mouse.py',
        'src/heartopia_painter/enhanced_paint.py',
        'src/heartopia_painter/delays.py',
        'src/heartopia_painter/paint.py',
        'src/heartopia_painter/config.py',
        'esp32/Arduino_Mouse/Arduino_Mouse.ino',
        'mouse_config.json',
        'config.json',
    ]
    
    results = []
    for file in files:
        path = base / file
        if path.exists():
            print_success(f"{file}")
            results.append(True)
        else:
            print_error(f"{file} NOT FOUND")
            results.append(False)
    
    return all(results)

def test_arduino_ports():
    """Test 3: Check for Arduino/ESP32 devices"""
    print_header("Test 3: Arduino Detection")
    
    try:
        import serial.tools.list_ports
        
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print_error("No serial ports found")
            print_info("Make sure Arduino is plugged in via USB")
            return False
        
        print_success(f"Found {len(ports)} serial port(s):")
        
        arduino_found = False
        for port in ports:
            desc = port.description or "Unknown"
            mfg = port.manufacturer or "Unknown"
            
            # A spoofed Leonardo reports the Logitech VID/PID instead of Arduino's.
            is_logitech_spoof = port.vid == 0x046D and port.pid == 0xC07D
            is_arduino = is_logitech_spoof or any(keyword in desc.lower() for keyword in
                           ['arduino', 'leonardo', 'pro micro', 'atmega32u4', 'usb serial'])
            
            if is_arduino:
                print_success(f"  {port.device} - {desc}")
                print_info(f"    Manufacturer: {mfg}")
                print_info(f"    VID:PID = {port.vid:04X}:{port.pid:04X}")
                arduino_found = True
            else:
                print_info(f"  {port.device} - {desc}")
        
        if not arduino_found:
            print_warning("No Arduino device detected")
            print_info("If you plugged in Arduino, try:")
            print_info("  1. Different USB port")
            print_info("  2. Unplug and replug")
            print_info("  3. Check Device Manager (Windows)")
            return False
        
        return True
        
    except ImportError:
        print_error("pyserial not installed")
        print_info("Install: pip install pyserial")
        return False
    except Exception as e:
        print_error(f"Error checking ports: {e}")
        return False

def test_hardware_mouse_module():
    """Test 4: Test hardware_mouse module"""
    print_header("Test 4: Hardware Mouse Module")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from heartopia_painter.hardware_mouse import (
            HardwareMouse,
            HardwareMouseConfig,
            list_available_ports,
            find_arduino_port
        )
        
        print_success("hardware_mouse.py imports successfully")
        
        # Test port listing
        ports = list_available_ports()
        print_success(f"list_available_ports() works: {len(ports)} ports")
        
        # Test Arduino detection
        arduino_port = find_arduino_port()
        if arduino_port:
            print_success(f"Arduino detected at: {arduino_port}")
            return True
        else:
            print_warning("Arduino not detected")
            print_info("This is OK if Arduino is not plugged in yet")
            return True  # Still pass test
        
    except Exception as e:
        print_error(f"Module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hardware_connection():
    """Test 5: Try to connect to Arduino"""
    print_header("Test 5: Hardware Connection")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from heartopia_painter.hardware_mouse import HardwareMouse, find_arduino_port
        
        port = find_arduino_port()
        if not port:
            print_warning("Arduino not detected - skipping connection test")
            print_info("Plug in Arduino to enable this test")
            return True  # Not a failure, just skipped
        
        print_info(f"Attempting connection to {port}...")
        
        mouse = HardwareMouse()
        if mouse.connect(port):
            print_success(f"Connected successfully!")
            print_info(f"  Device: {mouse.device_port}")
            print_info(f"  Version: {mouse.device_version}")
            
            # Test ping
            if mouse.ping():
                print_success("Ping successful")
            
            # Test status
            status = mouse.get_status()
            if status:
                print_success(f"Status: {status}")
            
            # Cleanup
            mouse.disconnect()
            print_success("Disconnected cleanly")
            
            return True
        else:
            print_error("Connection failed")
            return False
            
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_files():
    """Test 6: Check configuration files"""
    print_header("Test 6: Configuration Files")
    
    base = Path(__file__).parent
    
    # Check mouse_config.json
    mouse_config = base / 'mouse_config.json'
    if mouse_config.exists():
        print_success("mouse_config.json exists")
        try:
            import json
            with open(mouse_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check essential keys
            keys = ['arduino_port', 'click_randomness_px', 'enable_fatigue', 
                   'enable_breaks', 'session_time_limit_hours']
            
            for key in keys:
                if key in config:
                    print_success(f"  {key}: {config[key]}")
                else:
                    print_warning(f"  {key}: missing (will use default)")
            
        except Exception as e:
            print_error(f"Failed to parse mouse_config.json: {e}")
            return False
    else:
        print_warning("mouse_config.json not found")
        print_info("Will use default settings")
    
    # Check config.json
    config_file = base / 'config.json'
    if config_file.exists():
        print_success("config.json exists")
    else:
        print_warning("config.json not found")
        print_info("Will be created on first run")
    
    return True

def test_enhanced_features():
    """Test 7: Check enhanced features availability"""
    print_header("Test 7: Enhanced Features")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        # Test delays module
        try:
            from heartopia_painter.delays import DelaySystem
            print_success("DelaySystem available")
        except ImportError as e:
            print_error(f"DelaySystem import failed: {e}")
            return False
        
        # Test MouseConfig from config module
        try:
            from heartopia_painter.config import MouseConfig, load_mouse_config
            print_success("MouseConfig available")
        except ImportError as e:
            print_error(f"MouseConfig import failed: {e}")
            return False
        
        # Test enhanced_paint module
        try:
            from heartopia_painter.enhanced_paint import MouseController, enhanced_tap
            print_success("Enhanced paint features available")
        except ImportError as e:
            print_error(f"Enhanced paint import failed: {e}")
            return False
        
        # Create a DelaySystem instance
        try:
            ds = DelaySystem()
            print_success("DelaySystem instantiates correctly")
            # Try to show some info if available
            try:
                print_info(f"  Profile: {getattr(ds, 'profile', 'default')}")
            except:
                pass
        except Exception as e:
            print_error(f"DelaySystem instantiation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Enhanced features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(results):
    """Print final summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"Tests run: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}{RESET}")
    
    print()
    
    if all(results):
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}{'✓ ALL TESTS PASSED':^60}{RESET}")
        print(f"{GREEN}{'='*60}{RESET}")
        print()
        print_success("Your system is ready to use Hardware Mouse!")
        print_info("Next steps:")
        print_info("  1. Upload firmware to Arduino (run: cd esp32 && upload.bat)")
        print_info("  2. Enable in app: 'เปิดใช้ Enhanced Timing'")
        print_info("  3. Enable: 'ใช้ Hardware Mouse'")
        print_info("  4. Enter COM port (e.g., COM3)")
        print_info("  5. Start painting!")
        return True
    else:
        print(f"{RED}{'='*60}{RESET}")
        print(f"{RED}{'✗ SOME TESTS FAILED':^60}{RESET}")
        print(f"{RED}{'='*60}{RESET}")
        print()
        print_error("Please fix the issues above before using Hardware Mouse")
        print_info("Check: QUICKSTART_ESP32.md for troubleshooting")
        return False

def main():
    """Run all tests"""
    print(f"{BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       ESP32 Hardware Mouse - Setup Test Script            ║")
    print("║              HeartopiaAutoPainter v1.0                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    
    tests = [
        ("Python Packages", test_imports),
        ("Project Files", test_project_files),
        ("Arduino Detection", test_arduino_ports),
        ("Hardware Mouse Module", test_hardware_mouse_module),
        ("Hardware Connection", test_hardware_connection),
        ("Configuration Files", test_config_files),
        ("Enhanced Features", test_enhanced_features),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
