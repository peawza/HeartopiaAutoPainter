# Velocity Profiles System

## ภาพรวม

ระบบ Velocity Profiles เป็นฟีเจอร์ที่เพิ่มความเหมือนมนุษย์ให้กับการเคลื่อนที่เมาส์ โดยเลียนแบบรูปแบบความเร็วที่แตกต่างกันตามธรรมชาติ ไม่ใช่การเคลื่อนที่ด้วยความเร็วคงที่แบบ bot

## Velocity Profiles ที่มี

### 1. **SMOOTH** (40% - พบบ่อยที่สุด)
- **รูปแบบ:** เริ่มช้า → เร็วขึ้นกลางทาง → ช้าลงตอนท้าย
- **Easing:** Smoothstep (cubic)
- **เหมาะสำหรับ:** การเคลื่อนที่ปกติทั่วไป
- **ลักษณะ:** เป็นธรรมชาติที่สุด เหมือนคนเคลื่อนมือปกติ

```
Speed:  slow ━━━━ FAST ━━━━ slow
Position: Start ════════════ End
```

### 2. **SLOW_START** (25% - พบบ่อยรองลงมา)
- **รูปแบบ:** เริ่มช้ามาก → เร็วขึ้นเรื่อยๆ
- **Easing:** Quadratic ease-in
- **เหมาะสำหรับ:** การเคลื่อนที่อย่างระมัดระวัง
- **ลักษณะ:** เหมือนคนกำลังตั้งเป้า ค่อยๆ เคลื่อนที่

```
Speed:  slow slow ━━ FAST FAST
Position: Start ════════════ End
```

### 3. **FAST_START** (15%)
- **รูปแบบ:** เริ่มเร็ว → ช้าลงเรื่อยๆ
- **Easing:** Quadratic ease-out
- **เหมาะสำหรับ:** ปฏิกิริยารวดเร็ว แล้วควบคุมความแม่นยำ
- **ลักษณะ:** เหมือนคนทำอย่างรวดเร็ว แล้วระมัดระวังตอนท้าย

```
Speed:  FAST FAST ━━ slow slow
Position: Start ════════════ End
```

### 4. **HESITANT** (10%)
- **รูปแบบ:** เริ่มปกติ → หยุด/ลังเลกลางทาง → เดินหน้าต่อ
- **Easing:** Custom (pause at 30-50%)
- **เหมาะสำหรับ:** จำลองความไม่แน่ใจ หรือกำลังคิด
- **ลักษณะ:** เหมือนคนกำลังลังเลหรือคิดกลางทาง

```
Speed:  normal ━━ PAUSE ━━ fast
Position: Start ════════════ End
```

### 5. **OVERSHOOT** (7%)
- **รูปแบบ:** ไปเกินเป้า 110% → ถอยกลับมา 100%
- **Easing:** Custom (overshoot then correct)
- **เหมาะสำหรับ:** จำลองข้อผิดพลาดที่คนมักทำ
- **ลักษณะ:** เหมือนคนเคลื่อนเมาส์เกินไป แล้วปรับกลับมา

```
Position: Start ══════════╗══ End
                         110% ↑
                         (overshoot)
```

### 6. **CONSTANT** (3% - หายาก)
- **รูปแบบ:** ความเร็วคงที่ตลอดทาง
- **Easing:** Linear (ไม่มี easing)
- **เหมาะสำหรับ:** ใช้น้อยมาก เพราะดู robotic
- **ลักษณะ:** คงที่ ไม่เป็นธรรมชาติ

```
Speed:  ━━━━━━━━━━━━━━━━━━━━
Position: Start ════════════ End
```

## การทำงาน

### 1. Random Selection
ระบบจะสุ่มเลือก velocity profile ตามความน่าจะเป็นที่กำหนด:

```python
profile = VelocityProfile.get_random_profile()
```

### 2. Bezier Curve Generation
สร้าง Bezier curve พร้อมใช้ velocity profile:

```python
curve = delay_system.generate_bezier_curve(
    start_x, start_y,
    end_x, end_y,
    steps=50,
    velocity_profile=profile  # หรือ None สำหรับ random
)
```

### 3. Movement Execution
เคลื่อนที่ตามเส้นโค้งที่สร้าง:

```python
mouse_controller.move_along_curve(
    start=(100, 100),
    end=(500, 300),
    velocity_profile="smooth"  # หรือ None
)
```

## ตัวอย่างโค้ด

### ตัวอย่างที่ 1: Basic Usage

```python
from src.heartopia_painter.delays import DelaySystem, VelocityProfile

ds = DelaySystem()

# Random profile
curve = ds.generate_bezier_curve(100, 100, 500, 300, 50)

# Specific profile
curve = ds.generate_bezier_curve(
    100, 100, 500, 300, 50,
    velocity_profile=VelocityProfile.SMOOTH
)
```

### ตัวอย่างที่ 2: With MouseController

```python
from src.heartopia_painter.enhanced_paint import MouseController

mouse = MouseController(use_hardware=False)

# Random velocity (recommended)
mouse.move_along_curve((100, 100), (500, 300))

# Specific velocity
mouse.move_along_curve(
    (100, 100), (500, 300),
    velocity_profile=VelocityProfile.HESITANT
)
```

### ตัวอย่างที่ 3: Test Distribution

```python
# ทดสอบการกระจายตัว
counts = {}
for _ in range(1000):
    profile = VelocityProfile.get_random_profile()
    counts[profile] = counts.get(profile, 0) + 1

for profile, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{profile}: {count/10:.1f}%")
```

## สถิติการทดสอบ

### Distribution (10,000 samples)
```
smooth       39.92%  ████████████████████ (Expected: 40%)
slow_start   24.92%  ████████████         (Expected: 25%)
fast_start   15.23%  ███████              (Expected: 15%)
hesitant      9.96%  ████                 (Expected: 10%)
overshoot     7.07%  ███                  (Expected: 7%)
constant      2.90%  █                    (Expected: 3%)
```

### Speed Variation Analysis

| Profile    | Avg Speed | Max Speed | Min Speed | Ratio |
|-----------|-----------|-----------|-----------|-------|
| SMOOTH    | 9.03 px/step | 12.21 | 1.00 | 12.2x |
| SLOW_START| 9.41 px/step | 28.60 | 0.00 | ∞ |
| FAST_START| 9.17 px/step | 25.96 | 0.00 | ∞ |
| HESITANT  | 9.40 px/step | 22.00 | 0.00 | ∞ |
| OVERSHOOT | 9.20 px/step | 19.10 | 0.00 | ∞ |
| CONSTANT  | 9.21 px/step | 14.04 | 5.83 | 2.4x |

## ข้อดีของระบบ

### 1. ความหลากหลาย
- 6 รูปแบบที่แตกต่างกัน
- สุ่มเลือกตามความน่าจะเป็นที่เหมือนธรรมชาติ
- ไม่มีรูปแบบซ้ำซากที่คาดเดาได้

### 2. ความเป็นธรรมชาติ
- เลียนแบบพฤติกรรมมนุษย์จริง
- มีข้อผิดพลาด (overshoot, hesitation)
- ความเร็วไม่คงที่

### 3. ยากต่อการตรวจจับ
- Pattern ที่ไม่ซ้ำกัน
- Timing ที่สุ่มจริง
- จำลองข้อผิดพลาดของมนุษย์

### 4. Performance
- คำนวณเร็ว (mathematical easing)
- ไม่กระทบ frame rate
- Lightweight implementation

## การปรับแต่ง

### ปรับความน่าจะเป็น

แก้ไขใน `VelocityProfile.get_random_profile()`:

```python
profiles = [
    (VelocityProfile.SMOOTH, 0.50),      # เพิ่มเป็น 50%
    (VelocityProfile.SLOW_START, 0.20),  # ลดเหลือ 20%
    (VelocityProfile.FAST_START, 0.10),  # ลดเหลือ 10%
    (VelocityProfile.HESITANT, 0.10),
    (VelocityProfile.OVERSHOOT, 0.07),
    (VelocityProfile.CONSTANT, 0.03),
]
```

### เพิ่ม Profile ใหม่

```python
class VelocityProfile:
    # ... existing profiles ...
    ZIGZAG = "zigzag"  # เพิ่มรูปแบบใหม่
    
    @staticmethod
    def apply_easing(t: float, profile: str) -> float:
        # ... existing code ...
        elif profile == VelocityProfile.ZIGZAG:
            # ไปมาแบบ zigzag
            return t + 0.1 * math.sin(t * math.pi * 4)
```

## Best Practices

### 1. ใช้ Random Profile
```python
# ✅ Good - ใช้ random (แนะนำ)
curve = ds.generate_bezier_curve(x1, y1, x2, y2, 50)

# ⚠️ Less natural - กำหนด profile เอง
curve = ds.generate_bezier_curve(x1, y1, x2, y2, 50, "smooth")
```

### 2. เพิ่ม Randomness อื่นๆ ด้วย
```python
# ใช้ร่วมกับ features อื่นๆ
- Position jitter (±25px)
- Timing variance
- Micro-pauses
- Mistake simulation
```

### 3. ทดสอบ Distribution
```python
# ตรวจสอบว่า distribution ถูกต้อง
python test_velocity_profiles.py
```

## การทดสอบ

### รัน Test Suite
```bash
python test_velocity_profiles.py
```

### Test แต่ละ Profile
```python
from src.heartopia_painter.delays import DelaySystem, VelocityProfile

ds = DelaySystem()
profiles = [
    VelocityProfile.SMOOTH,
    VelocityProfile.SLOW_START,
    VelocityProfile.FAST_START,
]

for profile in profiles:
    curve = ds.generate_bezier_curve(0, 0, 100, 100, 50, profile)
    print(f"{profile}: {len(curve)} points")
```

## สรุป

Velocity Profiles เป็นระบบที่:
- ✅ เพิ่มความเหมือนมนุษย์อย่างมีนัยสำคัญ
- ✅ ใช้งานง่าย (auto random)
- ✅ Performance ดี
- ✅ ยากต่อการตรวจจับ
- ✅ Configurable และ extensible

**คะแนน:** หลังเพิ่มระบบนี้ **9.0/10** (เพิ่มจาก 8.5/10)

## อ้างอิง

- [Easing Functions Cheat Sheet](https://easings.net/)
- [Human Mouse Movement Patterns](https://dl.acm.org/doi/10.1145/1296843.1296852)
- Bezier Curve Mathematics
