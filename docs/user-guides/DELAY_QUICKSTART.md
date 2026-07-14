# Delay System Quick Start Guide

## 🚀 5-Minute Quick Start

### 1. Import the Delay System
```python
from heartopia_painter.delays import create_default_delay_system
```

### 2. Create an Instance
```python
ds = create_default_delay_system()
```

### 3. Use It!

#### Replace Fixed Delays
```python
# OLD CODE:
time.sleep(0.3)

# NEW CODE:
delay = ds.calculate_delay(0.3, 0.2)
time.sleep(delay)
```

That's it! You now have human-like timing with bell curve distribution and ±0.2s variance.

## 📚 Common Use Cases

### Use Case 1: Randomize Any Delay
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()

# Get a random delay between 0.1s and 0.5s (bell curve, peak at 0.3s)
delay = ds.calculate_delay(base=0.3, variance=0.2)
time.sleep(delay)
```

**Result**: Every delay is different, clustering around 0.3s like human reaction times.

---

### Use Case 2: Add Position Inaccuracy
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()

# Target position
x, y = 500, 300

# Add ±2 pixel inaccuracy (like humans)
jx, jy = ds.apply_position_jitter(x, y)

# Use jittered position
pyautogui.moveTo(jx, jy)
```

**Result**: Clicks land ±2 pixels from target, simulating human inaccuracy.

---

### Use Case 3: Natural Mouse Movement
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()

# Current and target positions
start_x, start_y = 100, 100
end_x, end_y = 500, 300

# Generate a natural curved path
curve = ds.generate_bezier_curve(start_x, start_y, end_x, end_y, steps=50)

# Move along the curve
for point in curve:
    pyautogui.moveTo(point[0], point[1], duration=0)
    time.sleep(0.006)  # ~6ms per step
```

**Result**: Mouse follows a smooth curve instead of a straight line.

---

### Use Case 4: Random Hesitation (Micro-Pauses)
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()

# Before each action, 10% chance of a brief pause
if ds.should_micro_pause():
    pause_duration = ds.get_micro_pause_duration()
    time.sleep(pause_duration)  # ~0.2s pause

# Then do the action
pyautogui.click()
```

**Result**: Random hesitations simulate human thought/reaction time.

---

### Use Case 5: Complete Natural Click
```python
from heartopia_painter.delays import create_default_delay_system
import time

ds = create_default_delay_system()

def natural_click(x, y):
    """Click with full human-like behavior."""
    
    # 1. Apply position jitter
    jx, jy = ds.apply_position_jitter(x, y)
    
    # 2. Random pre-click pause (10% chance)
    if ds.should_micro_pause():
        time.sleep(ds.get_micro_pause_duration())
    
    # 3. Move with randomized timing
    duration = ds.calculate_movement_duration()
    pyautogui.moveTo(jx, jy, duration=duration)
    
    # 4. Click
    pyautogui.click()
    
    # 5. Random post-click delay
    delay = ds.calculate_delay(0.05, 0.02)
    time.sleep(delay)

# Use it:
natural_click(500, 300)
```

**Result**: Fully human-like click with curved movement, jitter, random pauses, and varied timing.

---

## 🎯 Pre-configured Profiles

### Fast Profile (Rapid Clicking)
```python
from heartopia_painter.delays import create_fast_delay_system

ds = create_fast_delay_system()
# - Shorter delays: 50-150ms
# - Less randomization
# - Fewer pauses: 5%
```

### Default Profile (Balanced)
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()
# - Medium delays: 100-300ms
# - Balanced randomization
# - Normal pauses: 10%
```

### Careful Profile (Slow/Precise)
```python
from heartopia_painter.delays import create_careful_delay_system

ds = create_careful_delay_system()
# - Longer delays: 200-500ms
# - More randomization
# - More pauses: 15%
```

---

## 🔧 Custom Configuration

### Create Your Own Profile
```python
from heartopia_painter.delays import DelaySystem, DelayConfig

# Define your timing
config = DelayConfig(
    base_delay=0.08,           # Base delay: 80ms
    min_delay=0.15,            # Min random: 150ms
    max_delay=0.4,             # Max random: 400ms
    base_duration=0.4,         # Movement time: 400ms
    duration_variance=0.25,    # Variance: ±250ms
    position_jitter=3,         # Jitter: ±3 pixels
    micro_pause_chance=0.15,   # Pause: 15% chance
)

# Create system with your config
ds = DelaySystem(config)
```

---

## 📊 Test Your Setup

### Quick Test
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()

# Generate 10 random delays
print("10 random delays:")
for i in range(10):
    delay = ds.calculate_delay(0.3, 0.2)
    print(f"  {i+1}. {delay:.3f}s")

# They should vary between 0.1-0.5s and cluster around 0.3s
```

### Run Full Test Suite
```bash
python test_delays.py
```

### Run Timing Analysis
```bash
python analyze_timing.py
```

---

## ⚡ Performance Tips

1. **Create Once, Use Many Times**: Don't create a new DelaySystem for every action
   ```python
   # GOOD:
   ds = create_default_delay_system()
   for _ in range(100):
       delay = ds.calculate_delay(0.3, 0.2)
   
   # BAD:
   for _ in range(100):
       ds = create_default_delay_system()
       delay = ds.calculate_delay(0.3, 0.2)
   ```

2. **Reuse Bezier Curves**: Cache curves for repeated movements
   ```python
   # Generate once
   curve = ds.generate_bezier_curve(0, 0, 100, 100, 50)
   
   # Use many times
   for _ in range(10):
       for point in curve:
           pyautogui.moveTo(point[0], point[1], duration=0)
   ```

3. **Overhead is Minimal**: <2ms per action, negligible vs actual delays

---

## 🎓 Best Practices

### ✅ DO:
- Use variance on all delays (never fixed)
- Enable micro-pauses (10-15% chance)
- Use Bezier curves for movements >50px
- Apply position jitter to all clicks
- Choose appropriate profile for your task

### ❌ DON'T:
- Use zero variance (too predictable)
- Disable randomization completely
- Exceed max click rate (10/second default)
- Use straight-line movements
- Forget to test your configuration

---

## 🐛 Troubleshooting

### Problem: Actions Too Slow
**Solution**: Reduce delays
```python
config = DelayConfig(
    base_delay=0.02,    # Reduce from 0.05
    min_delay=0.05,     # Reduce from 0.1
    max_delay=0.15,     # Reduce from 0.3
)
```

### Problem: Actions Too Predictable
**Solution**: Increase variance
```python
config = DelayConfig(
    duration_variance=0.3,      # Increase from 0.2
    micro_pause_chance=0.2,     # Increase from 0.1
    position_jitter=4,          # Increase from 2
)
```

### Problem: Detection Warnings
**Solution**: Slow down and add more randomization
```python
config = DelayConfig(
    min_delay=0.2,              # Increase from 0.1
    max_delay=0.6,              # Increase from 0.3
    micro_pause_chance=0.2,     # Increase from 0.1
)
```

---

## 📖 Learn More

- **Full Documentation**: See `DELAY_SYSTEM_README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Original Spec**: See `DELAY_SYSTEM_FLOW_COMPLETE.md`
- **Test Suite**: Run `python test_delays.py`
- **Timing Analysis**: Run `python analyze_timing.py`

---

## 💡 Example: Integrate into Existing Code

### Before (Fixed Timing)
```python
def paint_pixel(x, y):
    pyautogui.moveTo(x, y, duration=0.03)
    time.sleep(0.06)
    pyautogui.click()
    time.sleep(0.05)
```

### After (Human-Like Timing)
```python
from heartopia_painter.delays import create_default_delay_system

ds = create_default_delay_system()

def paint_pixel(x, y):
    # Add jitter
    jx, jy = ds.apply_position_jitter(x, y)
    
    # Random movement time
    duration = ds.calculate_movement_duration()
    pyautogui.moveTo(jx, jy, duration=duration)
    
    # Random pre-click pause (10% chance)
    if ds.should_micro_pause():
        time.sleep(ds.get_micro_pause_duration())
    
    # Click
    pyautogui.click()
    
    # Random post-click delay
    delay = ds.calculate_delay(0.05, 0.02)
    time.sleep(delay)
```

**Improvements**:
- ✅ Position varies ±2px (human inaccuracy)
- ✅ Movement time varies 0.1-0.5s (bell curve)
- ✅ 10% chance of hesitation pause
- ✅ Post-click delay varies 0.03-0.07s
- ✅ All patterns use statistical distribution

---

## 🎉 You're Ready!

You now know how to:
- ✅ Create a delay system
- ✅ Randomize any delay
- ✅ Add position jitter
- ✅ Generate natural movement paths
- ✅ Add random pauses
- ✅ Choose the right profile
- ✅ Troubleshoot issues

**Next Step**: Integrate into your paint operations!

```python
from heartopia_painter.delays import create_default_delay_system

# Create once
ds = create_default_delay_system()

# Use everywhere
delay = ds.calculate_delay(0.3, 0.2)
jx, jy = ds.apply_position_jitter(x, y)
curve = ds.generate_bezier_curve(x1, y1, x2, y2, 50)
if ds.should_micro_pause():
    time.sleep(ds.get_micro_pause_duration())
```

---

**Questions?** Check the full documentation in `DELAY_SYSTEM_README.md`

**Version**: 1.0 | **Status**: ✅ Production Ready
