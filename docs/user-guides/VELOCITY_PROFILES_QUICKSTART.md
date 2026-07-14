# คู่มือใช้งาน Velocity Profiles

## ภาษาไทย

### Velocity Profiles คืออะไร?

Velocity Profiles เป็นระบบที่ทำให้เมาส์เคลื่อนที่แบบมนุษย์จริงๆ ไม่ใช่เคลื่อนที่ด้วยความเร็วคงที่แบบ bot

**ตัวอย่าง:**
- คนจริง: เริ่มช้า → เร็วขึ้น → ช้าลงตอนท้าย ✅
- Bot: ความเร็วคงที่ตลอดทาง ❌

### มีรูปแบบอะไรบ้าง?

1. **SMOOTH (40%)** - เคลื่อนที่นุ่มนวล เป็นธรรมชาติที่สุด
2. **SLOW_START (25%)** - เริ่มช้า ระมัดระวัง
3. **FAST_START (15%)** - เริ่มเร็ว แล้วช้าลง
4. **HESITANT (10%)** - ลังเลกลางทาง (เหมือนกำลังคิด)
5. **OVERSHOOT (7%)** - เคลื่อนเกินไป แล้วแก้ไข (ข้อผิดพลาด)
6. **CONSTANT (3%)** - ความเร็วคงที่ (ใช้น้อยเพราะดู robotic)

### การเปิดใช้งาน

ระบบจะเปิดใช้งานอัตโนมัติเมื่อคุณเปิด **Hardware Mouse** หรือ **Advanced Delays**

**ใน config.json:**
```json
{
  "use_advanced_delays": true,
  "use_hardware_mouse": true
}
```

### การทำงาน

1. ✅ **อัตโนมัติ** - ระบบจะสุ่ม profile ให้เอง (แนะนำ)
2. 📊 **กระจายตัวตามความเป็นจริง** - SMOOTH 40%, SLOW_START 25%, etc.
3. 🎯 **ไม่ซ้ำกัน** - ทุกครั้งที่เคลื่อนที่จะได้ pattern ต่างกัน

### ทดสอบระบบ

```bash
python test_velocity_profiles.py
```

คุณจะเห็น:
- การกระจายตัวของแต่ละ profile
- ความเร็วในแต่ละช่วง
- การแสดงผลแบบ ASCII

### ข้อดี

- ✅ **ตรวจจับยาก** - รูปแบบไม่ซ้ำกัน
- ✅ **เหมือนคนจริง** - มีข้อผิดพลาด มีความลังเล
- ✅ **ไม่ต้องตั้งค่า** - ทำงานอัตโนมัติ
- ✅ **Performance ดี** - ไม่กระทบความเร็ว

### คำถามที่พบบ่อย

**Q: ต้องตั้งค่าอะไรไหม?**
A: ไม่ต้อง ระบบจะทำงานอัตโนมัติ

**Q: จะเปลี่ยน profile เองได้ไหม?**
A: ได้ แต่ไม่แนะนำ ควรให้ระบบสุ่มเอง

**Q: ทำให้ช้าลงไหม?**
A: ไม่ เป็นการคำนวณทางคณิตศาสตร์ที่เร็วมาก

**Q: เหมาะกับเกมทุกเกมไหม?**
A: ใช่ เหมาะกับเกมที่มี anti-cheat detection

---

## English

### What is Velocity Profiles?

Velocity Profiles makes mouse movement human-like, not constant speed like bots.

**Example:**
- Human: Start slow → Speed up → Slow down at end ✅
- Bot: Constant speed throughout ❌

### Available Profiles

1. **SMOOTH (40%)** - Most natural, smooth movement
2. **SLOW_START (25%)** - Careful start, accelerate
3. **FAST_START (15%)** - Quick start, decelerate
4. **HESITANT (10%)** - Pause mid-movement (thinking)
5. **OVERSHOOT (7%)** - Overshoot then correct (mistake)
6. **CONSTANT (3%)** - Constant speed (robotic, rare)

### Activation

Automatically enabled when you enable **Hardware Mouse** or **Advanced Delays**.

**In config.json:**
```json
{
  "use_advanced_delays": true,
  "use_hardware_mouse": true
}
```

### How It Works

1. ✅ **Automatic** - System randomly selects profiles (recommended)
2. 📊 **Realistic distribution** - SMOOTH 40%, SLOW_START 25%, etc.
3. 🎯 **Never repeats** - Every movement has different pattern

### Test System

```bash
python test_velocity_profiles.py
```

You'll see:
- Profile distribution
- Speed variation per profile
- ASCII visualization

### Benefits

- ✅ **Hard to detect** - Non-repeating patterns
- ✅ **Human-like** - Has mistakes, hesitation
- ✅ **Zero configuration** - Works automatically
- ✅ **Good performance** - No speed impact

### FAQ

**Q: Do I need to configure anything?**
A: No, it works automatically.

**Q: Can I choose profile manually?**
A: Yes, but not recommended. Let system randomize.

**Q: Does it slow down painting?**
A: No, it's fast mathematical calculation.

**Q: Works with all games?**
A: Yes, especially games with anti-cheat detection.

---

## การอัปเดต / Updates

**Version 1.0** (Current)
- ✅ 6 velocity profiles implemented
- ✅ Automatic random selection
- ✅ Realistic distribution
- ✅ Integrated with Hardware Mouse
- ✅ Integrated with Bezier curves

**Planned Features**
- 🔄 User-customizable profile probabilities
- 🔄 Per-action profile selection (click vs drag)
- 🔄 Profile learning from user's real movements
