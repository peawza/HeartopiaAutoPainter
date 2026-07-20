"""
DLL Injection Tester - Standalone Tool
═══════════════════════════════════════
Test for suspicious DLL injections that may interfere with HeartopiaAutoPainter

Author: Kiro AI Assistant
Version: 1.0
Date: 2026-07-19
"""

import os
import sys
import time
import psutil
from typing import List, Tuple, Dict

# ANSI color codes for Windows
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Enable ANSI colors on Windows
if os.name == 'nt':
    os.system('color')

# DLL patterns to detect
SUSPICIOUS_DLL_PATTERNS = {
    'HIGH_RISK': [
        'cheatengine',
        'frida',
        'easyhook',
        'minhook',
        'inject',
        'x64dbg',
        'x32dbg',
        'ollydbg',
        'windbg',
    ],
    'MEDIUM_RISK': [
        'discord',
        'obs',
        'reshade',
        'rtss',
        'overlay',
        'hook',
    ],
    'LOW_RISK': [
        'kernel32',
        'user32',
        'ntdll',
        'kernelbase',
    ]
}


def print_header():
    """Print fancy ASCII art header"""
    print("\n" + "═" * 70)
    print("║" + " " * 68 + "║")
    print("║" + f"{'🛡️  DLL INJECTION TESTER - STANDALONE VERSION 🛡️':^68}" + "║")
    print("║" + " " * 68 + "║")
    print("═" * 70)
    print()


def print_menu():
    """Print main menu"""
    print("🎯 " + Colors.BOLD + "MENU OPTIONS" + Colors.ENDC)
    print("═" * 70)
    print()
    print(f"{Colors.CYAN}1.{Colors.ENDC} Quick Scan")
    print(f"   → Scan current process (this program itself)")
    print()
    print(f"{Colors.CYAN}2.{Colors.ENDC} Target Scan {Colors.GREEN}⭐ RECOMMENDED{Colors.ENDC}")
    print(f"   → Scan HeartopiaAutoPainter / main.py")
    print()
    print(f"{Colors.CYAN}3.{Colors.ENDC} Show Common Injection Patterns")
    print(f"   → Learn what DLLs are commonly injected")
    print()
    print(f"{Colors.CYAN}4.{Colors.ENDC} Test Detection Logic")
    print(f"   → Test if pattern matching works correctly")
    print()
    print(f"{Colors.CYAN}5.{Colors.ENDC} Real-Time Monitor")
    print(f"   → Watch for DLL injection live (30 seconds)")
    print()
    print(f"{Colors.CYAN}6.{Colors.ENDC} Full Test Suite")
    print(f"   → Run all tests at once")
    print()
    print(f"{Colors.RED}0.{Colors.ENDC} Exit")
    print()
    print("═" * 70)


def get_process_dlls(process_name: str = None) -> Tuple[List[str], int]:
    """Get list of DLLs loaded in a process"""
    dlls = []
    pid = None
    
    try:
        if process_name:
            # Find process by name
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    pid = proc.info['pid']
                    process = psutil.Process(pid)
                    break
            else:
                return [], None
        else:
            # Current process
            process = psutil.Process()
            pid = process.pid
        
        # Get memory maps (DLLs)
        try:
            for mmap in process.memory_maps():
                if mmap.path:
                    dlls.append(mmap.path)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
            
    except Exception as e:
        print(f"{Colors.RED}Error accessing process: {e}{Colors.ENDC}")
        
    return dlls, pid


def analyze_dlls(dlls: List[str]) -> Dict[str, List[str]]:
    """Analyze DLLs and categorize by risk level"""
    results = {
        'HIGH_RISK': [],
        'MEDIUM_RISK': [],
        'LOW_RISK': [],
        'CLEAN': []
    }
    
    for dll_path in dlls:
        dll_name = os.path.basename(dll_path).lower()
        categorized = False
        
        # Skip self (DLL_Injection_Tester.exe)
        if 'dll_injection_tester' in dll_name:
            continue
        
        # Check HIGH_RISK patterns
        for pattern in SUSPICIOUS_DLL_PATTERNS['HIGH_RISK']:
            if pattern in dll_name:
                results['HIGH_RISK'].append(dll_path)
                categorized = True
                break
        
        if not categorized:
            # Check MEDIUM_RISK patterns
            for pattern in SUSPICIOUS_DLL_PATTERNS['MEDIUM_RISK']:
                if pattern in dll_name:
                    results['MEDIUM_RISK'].append(dll_path)
                    categorized = True
                    break
        
        if not categorized:
            # Check LOW_RISK patterns (system DLLs)
            for pattern in SUSPICIOUS_DLL_PATTERNS['LOW_RISK']:
                if pattern in dll_name:
                    results['LOW_RISK'].append(dll_path)
                    categorized = True
                    break
        
        if not categorized:
            results['CLEAN'].append(dll_path)
    
    return results


def print_results(results: Dict[str, List[str]], pid: int = None):
    """Print analysis results with colors"""
    print("\n" + "═" * 70)
    print("📊 " + Colors.BOLD + "SCAN RESULTS" + Colors.ENDC)
    print("═" * 70)
    
    if pid:
        print(f"\n🔍 Process ID: {pid}")
    
    total_suspicious = len(results['HIGH_RISK']) + len(results['MEDIUM_RISK'])
    
    print(f"\n📈 Total DLLs Loaded: {sum(len(v) for v in results.values())}")
    print(f"⚠️  Suspicious DLLs: {Colors.RED if total_suspicious > 0 else Colors.GREEN}{total_suspicious}{Colors.ENDC}")
    print()
    
    # HIGH RISK
    if results['HIGH_RISK']:
        print(f"{Colors.RED}🔴 HIGH RISK ({len(results['HIGH_RISK'])} found):{Colors.ENDC}")
        for dll in results['HIGH_RISK']:
            print(f"   • {os.path.basename(dll)}")
            print(f"     {Colors.RED}{dll}{Colors.ENDC}")
        print()
    
    # MEDIUM RISK
    if results['MEDIUM_RISK']:
        print(f"{Colors.YELLOW}🟡 MEDIUM RISK ({len(results['MEDIUM_RISK'])} found):{Colors.ENDC}")
        for dll in results['MEDIUM_RISK']:
            print(f"   • {os.path.basename(dll)}")
            print(f"     {Colors.YELLOW}{dll}{Colors.ENDC}")
        print()
    
    # Summary
    print("═" * 70)
    if total_suspicious == 0:
        print(f"{Colors.GREEN}✅ CLEAN! No suspicious DLLs detected{Colors.ENDC}")
        print(f"{Colors.GREEN}Safe to use HeartopiaAutoPainter{Colors.ENDC}")
    elif total_suspicious <= 5:
        print(f"{Colors.YELLOW}⚠️  WARNING! {total_suspicious} suspicious DLL(s) detected{Colors.ENDC}")
        print(f"{Colors.YELLOW}Usually from: Discord, OBS, overlays{Colors.ENDC}")
        print(f"{Colors.YELLOW}Action: Close those programs and test again{Colors.ENDC}")
    else:
        print(f"{Colors.RED}🚨 ALERT! {total_suspicious} suspicious DLLs detected{Colors.ENDC}")
        print(f"{Colors.RED}Possible: Cheat engines, debuggers, hooks{Colors.ENDC}")
        print(f"{Colors.RED}Action: Close ALL suspicious programs immediately{Colors.ENDC}")
    print("═" * 70)


def quick_scan():
    """Option 1: Quick scan of current process"""
    print("\n🔍 " + Colors.BOLD + "QUICK SCAN - Current Process" + Colors.ENDC)
    print("═" * 70)
    print("\nScanning this program's loaded DLLs...")
    
    dlls, pid = get_process_dlls()
    if not dlls:
        print(f"{Colors.RED}Failed to retrieve DLL list{Colors.ENDC}")
        return
    
    results = analyze_dlls(dlls)
    print_results(results, pid)


def target_scan():
    """Option 2: Scan target process"""
    print("\n🎯 " + Colors.BOLD + "TARGET SCAN" + Colors.ENDC)
    print("═" * 70)
    
    # Try to find HeartopiaAutoPainter process
    targets = ['python', 'main.py', 'heartopia', 'painter']
    
    print("\n🔍 Searching for HeartopiaAutoPainter processes...")
    print()
    
    found_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        for target in targets:
            if target.lower() in proc.info['name'].lower():
                found_processes.append((proc.info['pid'], proc.info['name']))
                break
    
    if not found_processes:
        print(f"{Colors.RED}❌ No HeartopiaAutoPainter process found{Colors.ENDC}")
        print(f"\n💡 Make sure to start the application first:")
        print(f"   python main.py")
        return
    
    print(f"{Colors.GREEN}Found {len(found_processes)} process(es):{Colors.ENDC}")
    for pid, name in found_processes:
        print(f"   • PID {pid}: {name}")
    print()
    
    # Scan first found process
    target_pid = found_processes[0][0]
    target_name = found_processes[0][1]
    
    print(f"Scanning: {target_name} (PID {target_pid})...")
    
    try:
        process = psutil.Process(target_pid)
        dlls = []
        for mmap in process.memory_maps():
            if mmap.path:
                dlls.append(mmap.path)
    except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
        print(f"{Colors.RED}Access denied. Try running as Administrator.{Colors.ENDC}")
        return
    
    if not dlls:
        print(f"{Colors.RED}Failed to retrieve DLL list{Colors.ENDC}")
        return
    
    results = analyze_dlls(dlls)
    print_results(results, target_pid)


def show_patterns():
    """Option 3: Show common injection patterns"""
    print("\n📋 " + Colors.BOLD + "COMMON INJECTION PATTERNS" + Colors.ENDC)
    print("═" * 70)
    
    print(f"\n{Colors.RED}HIGH RISK 🔴 (Will be flagged){Colors.ENDC}")
    print("─" * 70)
    for pattern in SUSPICIOUS_DLL_PATTERNS['HIGH_RISK']:
        print(f"• {pattern}*.dll")
    
    print(f"\n{Colors.YELLOW}MEDIUM RISK 🟡 (May be flagged){Colors.ENDC}")
    print("─" * 70)
    for pattern in SUSPICIOUS_DLL_PATTERNS['MEDIUM_RISK']:
        print(f"• {pattern}*.dll")
    
    print(f"\n{Colors.GREEN}LOW RISK 🟢 (Usually ignored){Colors.ENDC}")
    print("─" * 70)
    for pattern in SUSPICIOUS_DLL_PATTERNS['LOW_RISK']:
        print(f"• {pattern}*.dll")
    
    print("\n" + "═" * 70)


def test_detection_logic():
    """Option 4: Test detection logic"""
    print("\n🧪 " + Colors.BOLD + "TEST DETECTION LOGIC" + Colors.ENDC)
    print("═" * 70)
    
    test_cases = [
        ("cheatengine-x86_64.dll", "HIGH_RISK"),
        ("frida-agent.dll", "HIGH_RISK"),
        ("discord_overlay.dll", "MEDIUM_RISK"),
        ("obs_hook.dll", "MEDIUM_RISK"),
        ("kernel32.dll", "LOW_RISK"),
        ("user32.dll", "LOW_RISK"),
        ("myapp.dll", "CLEAN"),
    ]
    
    print("\n🔬 Testing pattern matching...")
    print()
    
    passed = 0
    failed = 0
    
    for dll_name, expected_category in test_cases:
        results = analyze_dlls([dll_name])
        
        # Find which category it ended up in
        actual_category = None
        for category, dlls in results.items():
            if dll_name in dlls:
                actual_category = category
                break
        
        if actual_category == expected_category:
            print(f"{Colors.GREEN}✅{Colors.ENDC} {dll_name:30} → {expected_category}")
            passed += 1
        else:
            print(f"{Colors.RED}❌{Colors.ENDC} {dll_name:30} → Expected: {expected_category}, Got: {actual_category}")
            failed += 1
    
    print("\n" + "═" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print(f"{Colors.GREEN}✅ All tests passed! Detection logic is working correctly.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}⚠️  Some tests failed. Detection logic may need adjustment.{Colors.ENDC}")
    
    print("═" * 70)


def realtime_monitor():
    """Option 5: Real-time monitoring"""
    print("\n⏱️  " + Colors.BOLD + "REAL-TIME MONITOR (30 seconds)" + Colors.ENDC)
    print("═" * 70)
    print("\n💡 Try opening Discord, OBS, or other overlay programs during monitoring")
    print()
    
    duration = 30
    interval = 2
    
    baseline = None
    
    print(f"Starting monitoring for {duration} seconds...")
    print()
    
    for i in range(0, duration, interval):
        time.sleep(interval)
        
        # Scan current process
        dlls, pid = get_process_dlls()
        if not dlls:
            continue
        
        results = analyze_dlls(dlls)
        suspicious_count = len(results['HIGH_RISK']) + len(results['MEDIUM_RISK'])
        
        if baseline is None:
            baseline = suspicious_count
        
        # Show progress
        elapsed = i + interval
        remaining = duration - elapsed
        
        if suspicious_count > baseline:
            print(f"[{elapsed:2d}s] {Colors.RED}⚠️  NEW INJECTION DETECTED! Count: {suspicious_count} (+{suspicious_count - baseline}){Colors.ENDC}")
        else:
            print(f"[{elapsed:2d}s] {Colors.GREEN}✓{Colors.ENDC} Suspicious DLLs: {suspicious_count}")
    
    print("\n✅ Monitoring complete!")
    print()
    
    # Final scan
    dlls, pid = get_process_dlls()
    results = analyze_dlls(dlls)
    print_results(results, pid)


def full_test_suite():
    """Option 6: Run all tests"""
    print("\n🏃 " + Colors.BOLD + "FULL TEST SUITE" + Colors.ENDC)
    print("═" * 70)
    
    print("\n[1/4] Running Quick Scan...")
    quick_scan()
    
    input("\nPress Enter to continue to Target Scan...")
    print("\n[2/4] Running Target Scan...")
    target_scan()
    
    input("\nPress Enter to continue to Pattern Display...")
    print("\n[3/4] Showing Injection Patterns...")
    show_patterns()
    
    input("\nPress Enter to continue to Detection Logic Test...")
    print("\n[4/4] Testing Detection Logic...")
    test_detection_logic()
    
    print("\n" + "═" * 70)
    print(f"{Colors.GREEN}✅ Full test suite completed!{Colors.ENDC}")
    print("═" * 70)


def main():
    """Main program loop"""
    print_header()
    
    print("📦 " + Colors.BOLD + "WHAT IS THIS?" + Colors.ENDC)
    print("═" * 70)
    print("DLL_Injection_Tester is a tool to test for suspicious DLL")
    print("injections that may interfere with HeartopiaAutoPainter.")
    print()
    print("✅ No Python installation required (when compiled to .exe)")
    print("✅ No dependencies needed")
    print("✅ Just run the program!")
    print("═" * 70)
    print()
    
    while True:
        print_menu()
        
        try:
            choice = input(f"{Colors.CYAN}Enter your choice (0-6): {Colors.ENDC}").strip()
            
            if choice == '0':
                print(f"\n{Colors.GREEN}👋 Goodbye! Stay safe!{Colors.ENDC}\n")
                break
            elif choice == '1':
                quick_scan()
            elif choice == '2':
                target_scan()
            elif choice == '3':
                show_patterns()
            elif choice == '4':
                test_detection_logic()
            elif choice == '5':
                realtime_monitor()
            elif choice == '6':
                full_test_suite()
            else:
                print(f"\n{Colors.RED}❌ Invalid choice. Please enter 0-6.{Colors.ENDC}\n")
            
            if choice in ['1', '2', '4', '5', '6']:
                input(f"\n{Colors.CYAN}Press Enter to return to menu...{Colors.ENDC}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}⚠️  Interrupted by user{Colors.ENDC}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
