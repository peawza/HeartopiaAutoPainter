# แก้ไข: Enhanced Timing Tab โหลด Config จาก mouse_config.json

## ปัญหา
Tab "Enhanced Timing Hardware Mouse (ขั้นสูง)" ไม่ยอมโหลดค่าจาก `mouse_config.json` เมื่อเปิดโปรแกรม

## สาเหตุ
1. ฟังก์ชัน `_refresh_ui_from_config()` ไม่มีการโหลดค่าทั้งหมดจาก `mouse_config.json`
2. ฟังก์ชัน `_on_enhanced_timing_changed()` ยังไม่ถูกสร้าง แม้จะมี signal connections แล้ว
3. การโหลด config แยกกันระหว่าง `config.json` และ `mouse_config.json` ไม่สมบูรณ์

## การแก้ไข

### 1. ปรับปรุง `_refresh_ui_from_config()` (บรรทัด ~984-1013)
**เดิม:** โหลดเฉพาะ Fatigue, Breaks, Mistakes จาก `mouse_config.json`

**ใหม่:** โหลดค่าทั้งหมดจาก `mouse_config.json`:
- ✅ **Position Jitter** ← อ่านจาก `click_randomness_px` (ถ้า > 0 = เปิด)
- ✅ **Micro Pauses** ← อ่านจาก `enable_micro_pause`
- ✅ **Fatigue Simulation** ← อ่านจาก `enable_fatigue`
- ✅ **Random Breaks** ← อ่านจาก `enable_breaks`
- ✅ **Mistake Simulation** ← อ่านจาก `enable_mistakes`
- ✅ **Arduino Port** ← อ่านจาก `arduino_port`

### 2. เพิ่มฟังก์ชัน `_on_enhanced_timing_changed()` (หลังบรรทัด ~1090)
สร้างฟังก์ชันใหม่สำหรับบันทึกค่าเมื่อมีการเปลี่ยนแปลง:

```python
def _on_enhanced_timing_changed(self) -> None:
    """Save enhanced timing settings to both config.json and mouse_config.json."""
    # บันทึกลง config.json
    self._cfg.use_advanced_delays = bool(self.chk_enhanced_timing.isChecked())
    self._cfg.delay_profile = str(self.cbo_delay_profile.currentText()).lower()
    self._cfg.use_hardware_mouse = bool(self.chk_hardware_mouse.isChecked())
    self._cfg.enable_position_jitter = bool(self.chk_position_jitter.isChecked())
    self._cfg.enable_micro_pauses = bool(self.chk_micro_pauses.isChecked())
    self._save_cfg()
    
    # บันทึกลง mouse_config.json
    mouse_config = load_mouse_config()
    mouse_config.click_randomness_px = 3 if self.chk_position_jitter.isChecked() else 0
    mouse_config.enable_micro_pause = bool(self.chk_micro_pauses.isChecked())
    save_mouse_config(mouse_config)
```

## ผลลัพธ์
✅ เมื่อเปิดโปรแกรม: checkboxes ทั้งหมดใน Enhanced Timing tab จะโหลดค่าจาก `mouse_config.json` ถูกต้อง
✅ เมื่อแก้ไข checkboxes: จะบันทึกลง `mouse_config.json` ทันที
✅ Arduino port จะโหลดจาก `mouse_config.json` เมื่อเปิดโปรแกรม

## การทดสอบ
รัน test script:
```bash
.\.venv\Scripts\python.exe test_ui_config_load.py
```

ผลลัพธ์:
```
✅ All tests passed!
   - arduino_port: COM6
   - enable_micro_pause: True
   - enable_fatigue: True
   - enable_breaks: True
   - enable_mistakes: True
   - Position Jitter: True (from click_randomness_px = 3)
```

## ไฟล์ที่แก้ไข
1. `src/heartopia_painter/app.py` - เพิ่มการโหลดและบันทึก config
2. `test_ui_config_load.py` - สคริปต์ทดสอบ (ใหม่)

## วิธีใช้งาน
1. Build โปรแกรมใหม่:
   ```bash
   build_stealth.bat
   ```

2. เปิด `dist\Painter_Stealth.exe`

3. ไปที่ tab "จังหวะ / ความน่าเชื่อถือ"

4. ตรวจสอบว่า checkboxes ใน section "Enhanced Timing & Hardware Mouse (ขั้นสูง)" โหลดค่าถูกต้องจาก `mouse_config.json`

---
**หมายเหตุ:** การแก้ไขนี้ทำให้ UI synchronize กับ `mouse_config.json` อย่างสมบูรณ์ทั้ง 2 ทิศทาง (โหลดและบันทึก)
