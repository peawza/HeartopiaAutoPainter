╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║       🛡️  DLL INJECTION TESTER - STANDALONE VERSION 🛡️            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

📦 WHAT IS THIS?
═══════════════════════════════════════════════════════════════════

DLL_Injection_Tester.exe is a standalone tool to test for
suspicious DLL injections that may interfere with HeartopiaAutoPainter.

✅ No Python installation required (when using .exe)
✅ No dependencies needed
✅ Just run the file!

═══════════════════════════════════════════════════════════════════

📁 FILES IN THIS FOLDER
═══════════════════════════════════════════════════════════════════

dll_injection_tester.py           - Python source code (15 KB)
run_dll_tester.bat                - Quick run script
build_dll_tester.bat              - Build to EXE (simple)
build_dll_tester_advanced.bat     - Build to EXE (advanced options)
DLL_TESTER_README.md              - Full documentation (Thai)
BUILD_DLL_TESTER_GUIDE.md         - Build guide (Thai)
README.txt                        - This file

═══════════════════════════════════════════════════════════════════

🚀 QUICK START
═══════════════════════════════════════════════════════════════════

Method 1: Run Python Script
────────────────────────────────────────────────────────────────
Double-click: run_dll_tester.bat

OR

Open CMD/PowerShell:
  cd tools\dll_tester
  python dll_injection_tester.py


Method 2: Build EXE
────────────────────────────────────────────────────────────────
Double-click: build_dll_tester.bat

Then run:
  dist\DLL_Injection_Tester.exe


Method 3: Advanced Build
────────────────────────────────────────────────────────────────
Double-click: build_dll_tester_advanced.bat

Choose option 1-5:
  [1] Standard Build (~5-6 MB)      ⭐ Recommended
  [2] Silent Build (no console)
  [3] Debug Build (with logs)
  [4] Optimized Build (UPX, ~3-4 MB)
  [5] With Icon (.ico required)

═══════════════════════════════════════════════════════════════════

📊 HOW TO USE
═══════════════════════════════════════════════════════════════════

Step 1: Start HeartopiaAutoPainter
────────────────────────────────────────────────────────────────
  cd ..\..
  python main.py

Step 2: Run DLL Tester
────────────────────────────────────────────────────────────────
  cd tools\dll_tester
  run_dll_tester.bat

Step 3: Choose Option
────────────────────────────────────────────────────────────────
  Menu will show:
    [1] Quick Scan
    [2] Target Scan ⭐ RECOMMENDED
    [3] Show Patterns
    [4] Test Logic
    [5] Real-Time Monitor
    [6] Full Test Suite
    [0] Exit

  Select: 2 (Target Scan)

Step 4: Review Results
────────────────────────────────────────────────────────────────
  ✅ 0 suspicious DLLs    = CLEAN! Safe to use
  ⚠️ 1-5 suspicious DLLs  = Close Discord/OBS
  🚨 >5 suspicious DLLs   = Close ALL suspicious programs

═══════════════════════════════════════════════════════════════════

🔍 WHAT DLLs ARE DETECTED?
═══════════════════════════════════════════════════════════════════

HIGH RISK 🔴 (Always flagged)
────────────────────────────────────────────────────────────────
• cheatengine*.dll    - Cheat Engine
• frida*.dll          - Frida Framework
• easyhook*.dll       - EasyHook
• minhook*.dll        - MinHook
• inject*.dll         - Injection tools
• x64dbg.dll          - x64dbg Debugger
• x32dbg.dll          - x32dbg Debugger

MEDIUM RISK 🟡 (May be flagged)
────────────────────────────────────────────────────────────────
• discord*.dll        - Discord Overlay
• obs*.dll            - OBS Capture
• reshade*.dll        - ReShade Mod
• rtss*.dll           - RivaTuner Overlay

LOW RISK 🟢 (Usually OK)
────────────────────────────────────────────────────────────────
• kernel32.dll        - Windows System
• user32.dll          - Windows System
• ntdll.dll           - Windows System

═══════════════════════════════════════════════════════════════════

💡 TIPS
═══════════════════════════════════════════════════════════════════

✓ Run test BEFORE using HeartopiaAutoPainter
✓ Close Discord/OBS if warnings appear
✓ Run as Administrator for best results
✓ Test again after closing suspicious programs

═══════════════════════════════════════════════════════════════════

🔧 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

Problem: "HeartopiaAutoPainter is not running"
Solution: Start main.py first (from project root)

Problem: "Access Denied"
Solution: Right-click → Run as Administrator

Problem: Antivirus blocks
Solution: Add to exclusion list (false positive)

Problem: Python not found
Solution: Install Python or use compiled .exe

═══════════════════════════════════════════════════════════════════

📖 DOCUMENTATION
═══════════════════════════════════════════════════════════════════

Full Documentation:
  DLL_TESTER_README.md         - Complete user guide (Thai)
  BUILD_DLL_TESTER_GUIDE.md    - Build instructions (Thai)

═══════════════════════════════════════════════════════════════════

📞 SUPPORT
═══════════════════════════════════════════════════════════════════

For issues or questions:
• Read DLL_TESTER_README.md
• Check BUILD_DLL_TESTER_GUIDE.md
• Review test_dll_report.txt (after testing)

═══════════════════════════════════════════════════════════════════

Created by: Kiro AI Assistant
Date: 2026-07-19
Version: 1.0

Ready to use! 🛡️
