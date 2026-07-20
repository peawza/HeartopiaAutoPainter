# Rest Breaks Feature Documentation

## Implementation Status: ✅ COMPLETE

## Overview
The Rest Breaks feature adds realistic human-like pauses during painting to simulate natural fatigue and rest patterns. This makes the painting behavior more natural and human-like.

**Implementation completed on:** 2026-07-20

All core features have been implemented and integrated:
- ✅ Long breaks (5-15 minutes)
- ✅ Short random pauses (1-10 seconds)
- ✅ Regular breaks (15-45 seconds)
- ✅ Interruptible sleep with status updates
- ✅ Integration into paint.py (both row and color modes)

## UI Features (Status Display)

### 1. Main Window Break Status Panel ✨ NEW!
ระบบจะแสดงสถานะการหยุดพักในหน้าต่างหลักของโปรแกรม (Main Window) พร้อมข้อมูลแบบเรียลไทม์:

**UI Components:**
- 📋 **Break Status Label** - แสดงสถานะปัจจุบัน (ใหญ่ ตัวหนา ตรงกลาง)
  - `⏸ ไม่มีการหยุดพัก` (สีเทา) - ไม่ได้หยุด
  - `💤 Long Break (หยุดพักยาว) 🎨` (สีชมพูเข้ม) - กำลังหยุดยาว
  - `⏸ Short Pause (หยุดพักสั้น) 🎨` (สีชมพูอ่อน) - กำลังหยุดสั้น
  - `✅ หยุดพักเสร็จสิ้น - กำลังวาดต่อ...` (สีเขียว) - เสร็จแล้ว
  - `❌ หยุดพักถูกยกเลิก` (สีแดง) - ถูกยกเลิก

- 📊 **Break Progress Bar** - แสดงความคืบหน้า 0-100%
  - แสดงเฉพาะเมื่อมีการหยุดพัก
  - อัพเดตแบบเรียลไทม์ตามสถานะจาก overlay

- ⏱ **Time Information Grid** - แสดงข้อมูลเวลา 3 บรรทัด:
  - `⏱ เวลาที่ผ่านไป:` - เวลาที่หยุดไปแล้ว (เช่น "3 นาที")
  - `⏳ เวลาที่เหลือ:` - เวลาที่เหลือก่อนกลับมาทำงาน (เช่น "7 นาที")
  - `🕐 กลับมาวาด:` - เวลาจริงที่จะกลับมา (เช่น "14:35:20")

**Auto-Update Features:**
- ✅ อัพเดตอัตโนมัติจากข้อความ status overlay
- ✅ Parse ข้อมูลจาก progress bar และข้อความ
- ✅ แสดงสีตามสถานะ (เทา/ชมพู/เขียว/แดง)
- ✅ ซ่อน progress bar เมื่อไม่ได้หยุด
- ✅ รีเซ็ตอัตโนมัติ 3 วินาทีหลังเสร็จ/ยกเลิก

**User Benefits:**
- 👀 ดูสถานะได้แม้ไม่โฟกัสหน้าต่างเกม
- 📱 เช็คเวลาที่เหลือได้สะดวก
- 🎯 รู้เวลาที่จะกลับมาแน่นอน
- 🔔 ไม่ต้องเฝ้าหน้าจอเกมตลอดเวลา

### 2. Real-time Break Status Overlay (In-Game)
ระบบจะแสดงสถานะการหยุดพักแบบเรียลไทม์ในหน้าต่างเกม (Status Overlay) โดยอัตโนมัติ โดยจะแสดง:

**สำหรับการหยุดพักแบบยาว (≥ 60 วินาที):**
- 🎨 ไอคอนและชื่อประเภทการหยุดพัก
- Progress bar แบบกราฟิก (█████░░░) พร้อมเปอร์เซ็นต์
- เวลาที่ผ่านไปแล้ว (เช่น "3 นาที 25 วินาที")
- เวลาที่เหลือ (เช่น "6 นาที 35 วินาที")
- เวลาจริงที่จะกลับมาทำงาน (เช่น "14:35:20")
- คำแนะนำการยกเลิก ("💡 กด ESC เพื่อยกเลิก")

**สำหรับการหยุดพักแบบสั้น (< 60 วินาที):**
- ข้อมูลแบบกระชับ (Compact format)
- Progress bar พร้อมเปอร์เซ็นต์
- เวลาที่เหลือและเวลาที่จะกลับมา

### การอัพเดตแบบเรียลไทม์
- อัพเดตทุก 1 วินาที สำหรับการหยุดพักแบบยาว
- อัพเดตทุก 0.5 วินาที สำหรับการหยุดพักแบบสั้น
- ใช้ภาษาไทยที่อ่านง่ายและเข้าใจได้ทันที

### การยกเลิกระหว่างหยุดพัก
- กด **ESC** ได้ตลอดเวลาระหว่างการหยุดพัก
- ระบบจะแสดงข้อความยืนยันการยกเลิก
- การวาดจะหยุดทันทีและกลับสู่สถานะ "Paused"

## Feature Types

### 1. Long Breaks (5-10 minutes)
Simulates a person getting tired and needing a substantial rest break.

**Configuration:**
```json
{
  "enable_long_breaks": true,
  "long_break_min_actions": 800,
  "long_break_max_actions": 1500,
  "long_break_min_duration_s": 300.0,
  "long_break_max_duration_s": 600.0
}
```

**Behavior:**
- Triggers after 800-1500 painting actions (randomly determined)
- Duration: 5-10 minutes (300-600 seconds)
- Status displays countdown: "💤 Long break (6 min)... 5m 32s remaining"
- Can be interrupted by pressing ESC (standard stop mechanism)

### 2. Short Random Pauses (1-10 seconds)
Simulates brief moments where a person pauses to think or rest their hand.

**Configuration:**
```json
{
  "enable_short_pauses": true,
  "short_pause_min_actions": 30,
  "short_pause_max_actions": 80,
  "short_pause_min_duration_s": 1.0,
  "short_pause_max_duration_s": 10.0
}
```

**Behavior:**
- Triggers after 30-80 painting actions (randomly determined)
- Duration: 1-10 seconds
- Status displays countdown: "⏸ Short pause... 7s remaining"
- Can be interrupted by pressing ESC

### 3. Regular Breaks (Original feature)
The existing break system continues to work alongside the new features.

**Configuration:**
```json
{
  "enable_breaks": true,
  "break_min_actions": 180,
  "break_max_actions": 450,
  "break_min_duration_s": 15.0,
  "break_max_duration_s": 45.0
}
```

## Implementation Details

### Break Priority
When checking for breaks, the system follows this priority:
1. Long breaks (checked first)
2. Short pauses (checked second)
3. Regular breaks (existing system)

This ensures that long breaks take precedence over short pauses.

### Break Points
Breaks are checked at strategic points during painting:

1. **Row-based painting mode**: After each row is completed
2. **Paint-by-color mode**: After each shade/color is completed

This ensures breaks happen at natural stopping points in the painting process.

### Action Counting
Actions are tracked independently for each break type:
- `_actions_since_long_break`: Counter for long breaks
- `_actions_since_short_pause`: Counter for short pauses
- `_actions_since_break`: Counter for regular breaks

Each counter increments with painting operations and resets after its respective break.

### Status Updates
During breaks, the status display shows:
- Break type (Long break, Short pause)
- Remaining time in appropriate units:
  - Minutes and seconds for breaks ≥ 60 seconds
  - Seconds only for breaks < 60 seconds
- Updates every 1 second for long breaks
- Updates every 0.5 seconds for short pauses

## Configuration File Location

Place configuration in one of these files:
- `configs/mouse_config.json` (recommended)
- `mouse_config.json` (project root)

## Usage Examples

### Example 1: Realistic Human-Like Painting
```json
{
  "enable_long_breaks": true,
  "long_break_min_actions": 1000,
  "long_break_max_actions": 1500,
  "long_break_min_duration_s": 300.0,
  "long_break_max_duration_s": 600.0,
  "enable_short_pauses": true,
  "short_pause_min_actions": 40,
  "short_pause_max_actions": 80,
  "short_pause_min_duration_s": 2.0,
  "short_pause_max_duration_s": 8.0
}
```

### Example 2: More Frequent Short Pauses
```json
{
  "enable_long_breaks": true,
  "long_break_min_actions": 800,
  "long_break_max_actions": 1200,
  "long_break_min_duration_s": 180.0,
  "long_break_max_duration_s": 420.0,
  "enable_short_pauses": true,
  "short_pause_min_actions": 20,
  "short_pause_max_actions": 50,
  "short_pause_min_duration_s": 1.0,
  "short_pause_max_duration_s": 5.0
}
```

### Example 3: Disable Breaks
```json
{
  "enable_long_breaks": false,
  "enable_short_pauses": false,
  "enable_breaks": false
}
```

## Testing the Feature

### Quick Test Configuration (For Verification)
For testing purposes, you can use very short durations and frequent triggers to quickly verify the feature works:

```json
{
  "enable_long_breaks": true,
  "long_break_min_actions": 10,
  "long_break_max_actions": 20,
  "long_break_min_duration_s": 5.0,
  "long_break_max_duration_s": 10.0,
  "enable_short_pauses": true,
  "short_pause_min_actions": 3,
  "short_pause_max_actions": 8,
  "short_pause_min_duration_s": 1.0,
  "short_pause_max_duration_s": 3.0
}
```

**Expected behavior:**
1. ✅ Long break triggers after ~10-20 paint actions, pauses for 5-10 seconds
2. ✅ Short pause triggers after ~3-8 paint actions, pauses for 1-3 seconds
3. ✅ Status overlay shows countdown: "💤 Long break... 7s remaining"
4. ✅ Can be interrupted by pressing ESC
5. ✅ After break completes, painting resumes automatically

### Testing Steps
1. Create/edit `mouse_config.json` with the quick test configuration above
2. Start painting with a small test image
3. Watch for break messages in the status overlay:
   - "💤 Long break (X min)..." for long breaks
   - "⏸ Short pause (Xs)..." for short pauses
4. Verify countdown updates every 1 second (long) or 0.5 second (short)
5. Test interruption by pressing ESC during a break
6. Verify painting resumes after break completes

### Production Configuration
After testing, use realistic values for actual use:

```json
{
  "enable_long_breaks": true,
  "long_break_min_actions": 10,
  "long_break_max_actions": 20,
  "long_break_min_duration_s": 5.0,
  "long_break_max_duration_s": 10.0,
  "enable_short_pauses": true,
  "short_pause_min_actions": 3,
  "short_pause_max_actions": 8,
  "short_pause_min_duration_s": 1.0,
  "short_pause_max_duration_s": 3.0
}
```

This will trigger breaks much more frequently with shorter durations for verification.

## Implementation Details (Completed)

### Modified Files

1. **src/heartopia_painter/config.py** ✅
   - Added break configuration parameters to `MouseConfig` dataclass:
     - `enable_long_breaks`, `long_break_min_actions`, `long_break_max_actions`
     - `long_break_min_duration_s`, `long_break_max_duration_s`
     - `enable_short_pauses`, `short_pause_min_actions`, `short_pause_max_actions`
     - `short_pause_min_duration_s`, `short_pause_max_duration_s`
   - Updated `from_json_dict()` to load all new parameters with proper type conversions

2. **src/heartopia_painter/delays.py** ✅
   - Added break tracking state variables in `DelaySystem.__init__()`:
     - `_actions_since_long_break`, `_next_long_break_at`
     - `_actions_since_short_pause`, `_next_short_pause_at`
   - Implemented all required methods:
     - `should_take_long_break()` - Checks if it's time for 5-15 minute break
     - `get_long_break_duration()` - Returns random long break duration
     - `should_take_short_pause()` - Checks if it's time for 1-10 second pause
     - `get_short_pause_duration()` - Returns random short pause duration
     - `reset_long_break_counter()` - Resets and schedules next long break
     - `reset_short_pause_counter()` - Resets and schedules next short pause
     - `interruptible_sleep_with_status()` - Sleep with countdown display and ESC interruption
       - Enhanced with detailed Thai status messages (lines 736-880)
       - Progress bars with percentage display
       - Time formatting (minutes, seconds, hours)
       - Resume time calculation (HH:MM:SS format)
   - All methods properly handle MouseConfig being None with safe defaults

3. **src/heartopia_painter/paint.py** ✅
   - Implemented `_check_and_handle_breaks()` helper function:
     - Checks both long breaks and short pauses (priority: long > short)
     - Handles status updates with countdown timers
     - Supports interruption via ESC/should_stop callback
     - Returns True to continue, False if interrupted
   - Integrated break checks into `paint_grid()` (row-based mode):
     - After each row is completed and verified
     - Before moving to next row
   - Integrated break checks into `_paint_grid_by_color()` (color mode):
     - After each shade/color group is completed and verified
     - Before moving to next color
   - Both modes properly handle interruption and cleanup

4. **src/heartopia_painter/app.py** ✅ **NEW!**
   - Added **Break Status UI Section** in main window after paint_group:
     - `lbl_break_status` - Large, bold status label (14pt font)
     - `break_progress` - QProgressBar for visual progress
     - `lbl_break_elapsed` - Elapsed time display
     - `lbl_break_remaining` - Remaining time display
     - `lbl_break_resume_time` - Resume time display (HH:MM:SS)
     - `break_info_widgets` - List for easy reset
   - Implemented `_update_break_status_ui(msg)` method:
     - Parses status messages from `_on_worker_status()`
     - Extracts break type, progress, times using regex
     - Updates all UI widgets accordingly
     - Handles completion/cancellation states
     - Auto-resets after 3 seconds
   - Implemented `_reset_break_status_ui()` method:
     - Resets all labels to idle state
     - Hides progress bar
     - Sets idle text and color
   - Modified `_on_worker_status(msg)` to call `_update_break_status_ui(msg)`
   - **Result**: User can see break status in main window without looking at game!


## Compatibility

- Compatible with all existing features (fatigue, micro-pauses, mistakes, etc.)
- Works with both hardware mouse (ESP32/Arduino) and software mouse
- Works in both painting modes (row-based and paint-by-color)
- Can be enabled/disabled independently per break type

## Performance Impact

- Minimal performance impact when breaks are not active
- Break checks are lightweight (simple counter comparisons)
- Status updates during breaks use efficient sleep with interruption support

## Known Limitations

- Breaks can only be interrupted via ESC key (stop mechanism)
- Break timings are approximate (±1 second)
- Status overlay must be enabled to see break countdown messages

## Technical Notes

### Break Priority System
The implementation uses a priority-based system to prevent conflicts:
1. **Long breaks checked first** - highest priority (simulates getting tired)
2. **Short pauses checked second** - medium priority (brief thinking/rest)
3. **Regular breaks** - lowest priority (original break system)

This ensures that when multiple break conditions are met simultaneously, the most significant break (long break) takes precedence.

### Action Counters
Each break type maintains independent counters:
- `_actions_since_long_break` - Increments on every `should_take_long_break()` call
- `_actions_since_short_pause` - Increments on every `should_take_short_pause()` call  
- `_actions_since_break` - Increments on every `should_take_break()` call

Counters reset after their respective break is taken, and a new random threshold is set for the next break.

### Integration Points
Breaks are checked at strategic painting waypoints:
- **Row mode**: After each row is painted and verified (in `paint_grid()`)
- **Color mode**: After each shade group is painted and verified (in `_paint_grid_by_color()`)

This ensures:
- Breaks happen at natural stopping points (not mid-stroke)
- Painting state remains consistent
- Verification completes before breaking
- UI state is clean (shades panel closed, etc.)

### Interruption Handling
The `interruptible_sleep_with_status()` method:
- Sleeps in 0.1 second chunks for responsiveness
- Checks `should_stop` callback every 100ms
- Updates status message at appropriate intervals (1s for long, 0.5s for short)
- Returns `False` if interrupted, `True` if completed
- Displays remaining time in human-readable format (minutes+seconds or just seconds)

### Status Message Format
สำหรับการหยุดพักแบบยาว (Long breaks ≥ 60 วินาที):
```
💤 Long break 🎨
[████████████░░░░░░░░] 60%
⏱ ผ่านไป: 6 นาที | เหลือ: 4 นาที
🕐 กลับมาวาด: 14:35:20
💡 กด ESC เพื่อยกเลิก
```

สำหรับการหยุดพักแบบสั้น (Short pauses < 60 วินาที):
```
⏸ Short pause [██████░░░░░░░░░░░░░░] 30%
⏱ เหลือ: 7 วินาที | กลับมา: 14:30:45
```

ข้อมูลที่แสดง:
- **Progress bar** - แถบความคืบหน้า (█ = เสร็จแล้ว, ░ = เหลืออยู่)
- **เปอร์เซ็นต์** - แสดงความคืบหน้า 0-100%
- **เวลาที่ผ่านไป** - เวลาที่หยุดพักไปแล้ว (นาที/ชั่วโมง)
- **เวลาที่เหลือ** - เวลาที่เหลือก่อนกลับมาทำงาน
- **เวลาที่จะกลับมาทำงาน** - เวลาจริง (HH:MM:SS) ที่จะกลับมาวาดต่อ

สถานะพิเศษ:
- `✅ Long break เสร็จสิ้น - กำลังกลับมาวาดต่อ...` - เมื่อหยุดพักเสร็จสิ้น
- `❌ Long break ถูกยกเลิก` - เมื่อกด ESC ระหว่างหยุดพัก

## Future Enhancements

Possible improvements for future versions:
- Configurable break messages
- Break history/statistics
- Adaptive break timing based on painting complexity
- User notification sounds at break start/end
- Resume countdown before painting continues
