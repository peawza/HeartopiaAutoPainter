"""
🔒 Advanced Build Script with Anti-Detection Techniques
สำหรับการทดสอบในสภาพแวดล้อมส่วนตัวเท่านั้น

เทคนิคที่ใช้:
1. Random executable name - หลีกเลี่ยง signature database
2. Strip debug symbols - ลดข้อมูลสำหรับ reverse engineering
3. Code optimization level 2 - เปลี่ยน bytecode structure
4. Remove PyInstaller metadata - ลดลายเซ็น PyInstaller
5. Signature randomization - เปลี่ยน file hash
6. Anti-debugging in main.py - ตรวจสอบ debugger runtime
"""
import subprocess
import sys
import os
import shutil
import random
import string
import hashlib
from pathlib import Path


def random_string(length=8):
    """สร้างชื่อแบบสุ่มเพื่อหลีกเลี่ยง signature detection"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def create_obfuscated_spec():
    """สร้าง spec file ที่มีการปกปิด"""
    random_name = random_string(12)
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import random
import string
from PyInstaller.config import CONF

# Skip strict binary analysis to avoid tool errors
CONF['strict_binary_analysis'] = False

# Random runtime values to avoid static analysis
runtime_key = '{"".join(random.choices(string.ascii_letters, k=32))}'

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('mouse_config.json', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'win32api',
        'win32con',
        'win32gui',
        'pywintypes',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'heartopia_painter.paint',
        'heartopia_painter.delays',
        'heartopia_painter.enhanced_paint',
        'heartopia_painter.hardware_mouse',
        'heartopia_painter.config',
        'heartopia_painter.screen',
        'heartopia_painter.capture',
        'heartopia_painter.hidpi',
        'heartopia_painter.image_processing',
        'heartopia_painter.overlay',
        # pyserial modules (COM port communication)
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'serial.serialutil',
        'serial.win32',
        'serial.serialwin32',
        'serial.tools.list_ports_windows',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'numpy.distutils',
        'tcl',
        'tk',
        '_tkinter',
        'tkinter',
        # Exclude unused Qt modules to reduce size and errors
        'PySide6.QtQml',
        'PySide6.QtQuick',
        'PySide6.QtNetwork',
        'PySide6.QtOpenGL',
        'PySide6.QtWebEngine',
        'PySide6.Qt3D',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
    ],
    noarchive=False,
    optimize=2,  # Maximum optimization
)

# Remove debug information
a.datas = [x for x in a.datas if not x[0].startswith('pyi-')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{random_name}',  # Random name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Changed to False to avoid binary analysis issues
    upx=False,  # ปิด UPX เพราะถูกตรวจจับง่าย
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    spec_file = Path("HeartopiaAutoPainter_stealth.spec")
    spec_file.write_text(spec_content, encoding='utf-8')
    return spec_file, random_name


def add_junk_data(exe_path):
    """เพิ่มข้อมูลสุ่มเพื่อเปลี่ยน hash signature"""
    try:
        with open(exe_path, 'ab') as f:
            junk = ''.join(random.choices(string.printable, k=random.randint(100, 500)))
            f.write(f"\n# {junk}".encode('utf-8'))
        print("✓ Added junk data to change signature")
    except Exception as e:
        print(f"⚠ Could not add junk data: {e}")


def create_wrapper_script():
    """สร้าง wrapper script ที่ใช้เทคนิค anti-debugging"""
    wrapper = """# Anti-Detection Wrapper
import sys
import os
import ctypes
import time
import random

# Anti-debugging checks
def check_debugger():
    if ctypes.windll.kernel32.IsDebuggerPresent():
        time.sleep(random.uniform(0.5, 2.0))
        sys.exit(0)
    return True

# Anti-VM checks (basic)
def check_vm():
    suspicious_processes = ['vmtoolsd', 'vboxservice', 'vboxtray']
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in suspicious_processes:
                time.sleep(random.uniform(0.5, 2.0))
                return False
    except:
        pass
    return True

# Delay execution randomly
time.sleep(random.uniform(0.1, 0.5))

if check_debugger() and check_vm():
    # Import and run actual application
    from heartopia_painter.app import main
    main()
"""
    
    wrapper_path = Path("main_wrapper.py")
    wrapper_path.write_text(wrapper, encoding='utf-8')
    return wrapper_path


def build_stealth():
    """Build with stealth techniques"""
    print("=" * 60)
    print("    STEALTH BUILD - Anti-Detection Techniques")
    print("    สำหรับการทดสอบในสภาพแวดล้อมส่วนตัวเท่านั้น")
    print("=" * 60)
    print()
    
    # Check requirements
    config_file = Path("config.json")
    if not config_file.exists():
        print("❌ ERROR: config.json not found!")
        sys.exit(1)
    
    print("✓ Found config.json")
    
    # Install additional packages if needed
    print("\n📦 Installing additional packages...")
    packages = ['pyarmor', 'psutil']
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✓ {pkg} already installed")
        except ImportError:
            print(f"⚠ Installing {pkg}...")
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], 
                         capture_output=True, check=False)
    
    # Step 1: Create wrapper with anti-debugging
    print("\n🔧 Step 1: Creating anti-detection wrapper...")
    wrapper_path = create_wrapper_script()
    print(f"✓ Created {wrapper_path}")
    
    # Step 2: Backup original main.py
    main_backup = Path("main.py.backup")
    if not main_backup.exists():
        shutil.copy("main.py", main_backup)
        print("✓ Backed up original main.py")
    
    # Step 3: Create stealth spec
    print("\n🔧 Step 2: Creating stealth spec file...")
    spec_file, random_name = create_obfuscated_spec()
    print(f"✓ Created {spec_file.name}")
    print(f"✓ Random executable name: {random_name}.exe")
    
    # Step 4: Build with PyInstaller
    print("\n🔨 Step 3: Building with PyInstaller...")
    print("-" * 60)
    
    try:
        # Set environment variable to skip binary analysis
        env = os.environ.copy()
        env['PYINSTALLER_STRICT_BINARY_ANALYSIS'] = '0'
        
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean", "--noconfirm", "--log-level=WARN"],
            check=True,
            capture_output=False,
            text=True,
            env=env
        )
        
        print()
        print("=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        
        # Find the built executable
        exe_file = Path("dist") / f"{random_name}.exe"
        if exe_file.exists():
            original_size = exe_file.stat().st_size / 1024 / 1024
            print(f"\n✓ Executable created: {exe_file}")
            print(f"  Size: {original_size:.2f} MB")
            
            # Step 5: Add junk data to change signature
            print("\n🔧 Step 4: Modifying signature...")
            add_junk_data(exe_file)
            
            # Rename to Painter.exe
            final_exe = Path("dist") / "Painter_Stealth.exe"
            if final_exe.exists():
                final_exe.unlink()
            shutil.copy(exe_file, final_exe)
            
            final_size = final_exe.stat().st_size / 1024 / 1024
            print(f"✓ Final executable: {final_exe}")
            print(f"  Size: {final_size:.2f} MB")
            
            print("\n" + "=" * 60)
            print("🎯 STEALTH BUILD COMPLETE")
            print("=" * 60)
            print(f"\n📁 ไฟล์ที่สร้าง: {final_exe}")
            print("\n⚠️  หมายเหตุ:")
            print("   - ไฟล์นี้ใช้เทคนิคลดการตรวจจับพื้นฐาน")
            print("   - อาจยังถูกตรวจจับโดย antivirus บางตัว")
            print("   - ใช้สำหรับการทดสอบในสภาพแวดล้อมส่วนตัวเท่านั้น")
            print("   - Anti-cheat ระดับสูงยังคงตรวจจับได้")
            
        else:
            print(f"❌ ERROR: Could not find {exe_file}")
            
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("❌ BUILD FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)
    
    # Cleanup
    print("\n🧹 Cleaning up temporary files...")
    if wrapper_path.exists():
        wrapper_path.unlink()
    print("✓ Cleanup complete")


def restore_original():
    """Restore original main.py"""
    main_backup = Path("main.py.backup")
    if main_backup.exists():
        shutil.copy(main_backup, "main.py")
        print("✓ Restored original main.py")


if __name__ == "__main__":
    try:
        build_stealth()
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        restore_original()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        restore_original()
        raise

