# HeartopiaAutoPainter - โครงสร้างโปรเจค (ปรับปรุงแล้ว)

## 📁 โครงสร้างหลัก

```
HeartopiaAutoPainter/
├── 📂 src/                    # ซอร์สโค้ดหลัก
│   └── heartopia_painter/
│
├── 📂 configs/                # ไฟล์ Configuration
│   ├── config.json           # การตั้งค่าหลัก
│   └── mouse_config.json     # การตั้งค่าเมาส์
│
├── 📂 tests/                  # ไฟล์ทดสอบทั้งหมด
│   ├── test_*.py             # Python test files (11 files)
│   ├── test_*.bat            # Batch test files
│   └── timing_report.txt     # รายงานผลการวิเคราะห์เวลา
│
├── 📂 scripts/                # สคริปต์ช่วยเหลือต่างๆ
│   ├── build_*.bat           # Build scripts
│   ├── build_stealth.py      # Build script หลัก
│   ├── setup_build.bat       # Setup script
│   ├── analyze_timing.py     # วิเคราะห์เวลา
│   ├── check_*.py/bat        # เช็คพอร์ตและการเชื่อมต่อ
│   ├── find_missing_mouse_ctrl.py
│   ├── profile_paint_enhanced.py
│   └── simple_test_com6.py
│
├── 📂 build_specs/            # PyInstaller spec files
│   ├── HeartopiaAutoPainter_stealth.spec
│   ├── painter_stealth.spec
│   ├── painter_stealth_fixed.spec
│   └── simple_build.spec
│
├── 📂 esp32/                  # ESP32 Hardware Integration
│   ├── Arduino_Mouse/        # Arduino firmware
│   ├── *.bat                 # Setup & upload scripts
│   └── README_SETUP.txt
│
├── 📂 docs/                   # เอกสารภาษาอังกฤษ
│   ├── development/          # รายงานการพัฒนา
│   ├── technical/            # เอกสารเทคนิค
│   └── user-guides/          # คู่มือผู้ใช้
│
├── 📂 docs_th/                # เอกสารภาษาไทย
│   ├── ตั้งค่า/              # โฟลเดอร์การตั้งค่า
│   ├── สรุป_Auto-Connect.txt
│   ├── สรุป_ESP32.txt
│   └── โปรดอ่าน.txt
│
├── 📂 build/                  # Build output
├── 📂 dist/                   # Distribution files
│
├── 📄 main.py                 # Entry point หลัก
├── 📄 main.py.backup          # Backup
├── 📄 requirements.txt        # Python dependencies
│
└── 📄 Documentation Files (Root)
    ├── README.md
    ├── BUILD_INSTRUCTIONS.md
    ├── CHANGELOG_v1.2.0.md
    ├── QUICKSTART_ESP32.md
    ├── PROJECT_STRUCTURE.md
    ├── ADVANCED_RANDOMNESS_FEATURES.md
    ├── AUTO_CONNECT_FEATURE.md
    ├── RANDOMNESS_UPGRADE_GUIDE.md
    ├── ESP32_*.md (3 files)
    └── FIX_*.md (2 files)
```

## 📊 สรุปการจัดกลุ่มไฟล์

### ✅ ย้ายเรียบร้อยแล้ว

| โฟลเดอร์ | จำนวนไฟล์ | รายละเอียด |
|---------|----------|-----------|
| **configs/** | 2 | config.json, mouse_config.json |
| **tests/** | 12 | ไฟล์ทดสอบ Python และ Batch + timing report |
| **scripts/** | 12 | Build scripts, analysis, check utilities |
| **build_specs/** | 4 | PyInstaller .spec files |
| **docs_th/** | 3 files + 1 folder | เอกสารภาษาไทยทั้งหมด |

### 📌 ไฟล์ที่ยังอยู่ Root (ควรอยู่ที่นี่)

- `main.py` - Entry point ของโปรแกรม (ต้องอยู่ root)
- `main.py.backup` - Backup file
- `requirements.txt` - Python dependencies (ต้องอยู่ root)
- `.gitignore` - Git configuration
- เอกสาร Markdown ต่างๆ (README, CHANGELOG, etc.)

### 🎯 ประโยชน์ของการจัดระเบียบใหม่

1. **แยกประเภทชัดเจน** - ไฟล์แต่ละประเภทอยู่ในโฟลเดอร์เฉพาะ
2. **หาไฟล์ง่าย** - ไม่ต้องค้นหาในไฟล์เยอะๆ ที่ root
3. **จัดการได้ดีขึ้น** - Config, tests, scripts แยกกันชัดเจน
4. **Build ง่ายขึ้น** - Build specs อยู่ในที่เดียว
5. **เอกสารเป็นระเบียบ** - แยกภาษาไทย/อังกฤษ และประเภทเอกสาร

## 🔧 การใช้งานหลังจากจัดระเบียบ

### เรียกใช้โปรแกรม
```bash
python main.py
```

### Build
```bash
scripts\build_stealth.bat
```

### Run Tests
```bash
python tests\test_paint_integration.py
```

### Config Files
- หาการตั้งค่าได้ที่ `configs\config.json`
- การตั้งค่าเมาส์ที่ `configs\mouse_config.json`

## 📝 หมายเหตุ

- โครงสร้างเดิมยังคงอยู่ใน `PROJECT_STRUCTURE.md`
- ไฟล์ทั้งหมดถูกย้ายโดยไม่มีการลบหรือแก้ไข
- สามารถย้อนกลับได้ง่ายหากต้องการ
