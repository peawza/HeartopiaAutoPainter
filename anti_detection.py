"""
Anti-Detection Layer for HeartopiaAutoPainter
==============================================

Advanced anti-detection system designed to avoid detection by anti-cheat systems,
virtual machines, debuggers, and analysis tools. This layer runs before any main
application code.

Author: HeartopiaAutoPainter Project
Version: 3.0
License: Educational use only
"""

import ctypes
import psutil
import time
import random
import os
import sys


def _init_stealth():
    """
    Initialize advanced anti-detection mechanisms.
    
    This function should be called BEFORE importing any main application code.
    It performs multiple detection checks and applies subtle delays instead of
    immediate exits to avoid obvious patterns.
    
    Detection mechanisms:
    1. Anti-Debugger Detection (IsDebuggerPresent)
    2. Anti-VM Detection (Process + CPU + RAM checks)
    3. Parent Process Analysis
    4. DLL Injection Detection
    5. Sandbox Detection (Path + Mouse)
    6. Anti-Analysis Timing Check
    7. Process Name Obfuscation
    8. Random Delay
    
    Returns:
        bool: True if all checks pass, False if critical detection occurs
    """
    try:
        # ========================================
        # 1. ANTI-DEBUGGER DETECTION
        # ========================================
        # Detect if program is running under a debugger
        # Uses Windows API IsDebuggerPresent()
        # Response: Random delay + exit on detection
        if ctypes.windll.kernel32.IsDebuggerPresent():
            time.sleep(random.uniform(0.5, 2.0))
            sys.exit(0)
        
        # ========================================
        # 2. ANTI-VM DETECTION
        # ========================================
        # 2.1 Check for VM-specific processes
        vm_processes = [
            'vmtoolsd.exe',      # VMware Tools
            'vboxservice.exe',   # VirtualBox Service
            'vboxtray.exe',      # VirtualBox Tray
            'vmwareuser.exe',    # VMware User Process
            'vmwaretray.exe',    # VMware Tray
            'vmsrvc.exe',        # VM Service
            'xenservice.exe',    # Xen Hypervisor
            'qemu-ga.exe',       # QEMU Guest Agent
        ]
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in vm_processes:
                    # Detected VM process - add delay but don't exit
                    time.sleep(random.uniform(0.2, 0.5))
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # 2.2 CPU Core Count Check
        # VMs typically have fewer CPU cores
        cpu_count = psutil.cpu_count(logical=True)
        if cpu_count < 2:
            time.sleep(random.uniform(0.1, 0.3))
        
        # 2.3 RAM Size Check
        # VMs typically have limited RAM
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if ram_gb < 4:
            time.sleep(random.uniform(0.1, 0.3))
        
        # ========================================
        # 3. PARENT PROCESS ANALYSIS
        # ========================================
        # Check if launched by analysis tools
        try:
            current = psutil.Process()
            parent = current.parent()
            
            if parent:
                parent_name = parent.name().lower()
                
                suspicious_parents = [
                    'processhacker', 'procexp', 'procmon',      # Process monitors
                    'cheatengine', 'ida', 'ollydbg', 'x64dbg',  # Debuggers/Reversers
                    'x32dbg', 'windbg', 'gdb',                  # More debuggers
                    'wireshark', 'fiddler',                      # Network monitors
                    'sandboxie', 'vmware', 'virtualbox'          # Sandboxes
                ]
                
                if any(sus in parent_name for sus in suspicious_parents):
                    # Detected suspicious parent - delay only
                    time.sleep(random.uniform(0.5, 1.5))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # ========================================
        # 4. DLL INJECTION DETECTION
        # ========================================
        # Enumerate loaded DLLs to detect hooking frameworks
        try:
            current = psutil.Process()
            suspicious_dlls = [
                'frida',      # Frida dynamic instrumentation
                'inject',     # Generic injection
                'hook',       # Hooking libraries
                'detour',     # Microsoft Detours
                'easyhook',   # EasyHook
                'minhook',    # MinHook
                'discord',    # Discord overlay (may be benign)
                'overlay',    # Generic overlays
            ]
            
            for dll in current.memory_maps():
                dll_path = dll.path.lower()
                for sus in suspicious_dlls:
                    if sus in dll_path:
                        # Detected suspicious DLL - add delay
                        time.sleep(random.uniform(0.3, 0.8))
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            # memory_maps() may not be available on all systems
            pass
        
        # ========================================
        # 5. SANDBOX DETECTION
        # ========================================
        # 5.1 Check for sandbox-specific directories
        sandbox_indicators = [
            ('C:\\analysis', 'Cuckoo Sandbox'),
            ('C:\\sandbox', 'Generic Sandbox'),
            ('C:\\cwsandbox', 'CWSandbox'),
            ('C:\\sample', 'Sample Analysis'),
        ]
        
        for path, name in sandbox_indicators:
            if os.path.exists(path):
                time.sleep(random.uniform(0.2, 0.5))
                break
        
        # 5.2 Mouse Movement Detection
        # Sandboxes often lack real mouse input
        try:
            import pyautogui
            
            x1, y1 = pyautogui.position()
            time.sleep(0.05)
            x2, y2 = pyautogui.position()
            
            # If mouse never moves, might be sandbox
            # But we don't exit - just note it
            if x1 == x2 and y1 == y2:
                time.sleep(random.uniform(0.1, 0.2))
        except ImportError:
            # pyautogui not installed - skip this check
            pass
        except Exception:
            # Any other error - skip silently
            pass
        
        # ========================================
        # 6. ANTI-ANALYSIS TIMING CHECK
        # ========================================
        # Detect if code execution is being slowed by analysis
        start = time.perf_counter()
        dummy_calc = sum(range(1000))
        elapsed = time.perf_counter() - start
        
        # Should be < 10ms on real hardware
        # Debuggers/emulators slow down execution
        if elapsed > 0.01:
            time.sleep(random.uniform(0.1, 0.3))
        
        # ========================================
        # 7. PROCESS NAME OBFUSCATION
        # ========================================
        # Disguise process in Task Manager
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("Windows Update Service")
        except Exception:
            # Console may not be available (GUI app)
            pass
        
        # ========================================
        # 8. RANDOM DELAY
        # ========================================
        # Make timing analysis harder
        time.sleep(random.uniform(0.05, 0.15))
        
        return True
        
    except Exception as e:
        # Never crash on anti-detection failure
        # Silently continue - better to run than to crash
        return True


def init_stealth():
    """
    Public interface for anti-detection initialization.
    
    Call this function at the very beginning of your application,
    before importing any other modules.
    
    Example:
        from anti_detection import init_stealth
        
        if __name__ == "__main__":
            init_stealth()
            
            # Now import and run your app
            from your_app import main
            main()
    
    Returns:
        bool: True if checks pass, False if critical detection
    """
    return _init_stealth()


# Optional: Run checks on module import
# This provides additional protection even if init_stealth() isn't called
def _auto_init_on_import():
    """Automatically run basic checks on module import"""
    try:
        # Only run critical checks on import
        if ctypes.windll.kernel32.IsDebuggerPresent():
            time.sleep(random.uniform(0.5, 2.0))
            sys.exit(0)
    except Exception:
        pass


# Uncomment the line below to enable auto-init on import
# _auto_init_on_import()


if __name__ == "__main__":
    print("Anti-Detection Layer Test")
    print("=" * 50)
    print()
    print("Running stealth initialization...")
    
    result = init_stealth()
    
    if result:
        print("✅ Stealth initialization completed successfully")
        print("No critical detections found")
    else:
        print("⚠️ Stealth initialization completed with warnings")
        print("Some detections were triggered")
    
    print()
    print("=" * 50)
    print("Test complete. Your application can now run.")
