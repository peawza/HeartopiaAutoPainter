# Delay System Flow - Complete Guide

## Overview
This document provides a comprehensive explanation of the delay system implemented in Heartopia Painter, detailing how randomization and timing work together to create human-like mouse movement patterns that avoid detection.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Delay Components](#delay-components)
3. [Flow Diagram](#flow-diagram)
4. [Configuration Parameters](#configuration-parameters)
5. [Implementation Details](#implementation-details)
6. [Anti-Detection Features](#anti-detection-features)
7. [Best Practices](#best-practices)

---

## System Architecture

### High-Level Overview
```
User Input → Config Loading → Delay Calculation → Mouse Movement → Action Execution
     ↓              ↓                ↓                    ↓                ↓
  Hotkeys    mouse_config.json   Randomization      Bezier Curves    Click/Hold
```

### Core Components
- **Configuration Manager**: Loads and validates delay settings
- **Randomization Engine**: Generates human-like variations
- **Movement Controller**: Executes mouse movements with delays
- **Action Handler**: Manages clicks and holds with timing

---

## Delay Components

### 1. **Base Delays**
Fundamental timing values that serve as the foundation for all delays.

```json
{
  "delays": {
    "base_delay": 0.05,           // Minimum delay between operations (50ms)
    "min_delay": 0.1,              // Minimum random delay (100ms)
    "max_delay": 0.3,              // Maximum random delay (300ms)
    "click_delay": 0.05,           // Delay after each click (50ms)
    "hold_release_delay": 0.1      // Delay after releasing hold (100ms)
  }
}
```

**Purpose**: Establish baseline timing that prevents inhuman speeds.

---

### 2. **Movement Delays**
Timing for mouse cursor movement between points.

```json
{
  "movement": {
    "base_duration": 0.3,          // Base time for movement (300ms)
    "duration_variance": 0.2,      // Variance ±200ms
    "steps": 50,                   // Number of movement steps
    "step_variance": 20            // Variance in steps ±20
  }
}
```

**Calculation Formula**:
```
actual_duration = base_duration + random(-duration_variance, +duration_variance)
actual_steps = steps + random(-step_variance, +step_variance)
delay_per_step = actual_duration / actual_steps
```

**Example**:
```
base_duration = 0.3s
variance = 0.2s
Result: Movement takes between 0.1s to 0.5s (100-500ms)
```

---

### 3. **Action Delays**
Timing for specific mouse actions (clicks, holds).

#### Click Delays
```json
{
  "click_timing": {
    "down_duration": 0.05,         // Mouse button down time
    "up_duration": 0.05,           // Mouse button up time
    "between_clicks": 0.1          // Delay between successive clicks
  }
}
```

#### Hold Delays
```json
{
  "hold_timing": {
    "press_duration": 0.05,        // Initial press duration
    "hold_duration": 0.5,          // How long to hold
    "release_duration": 0.1        // Release transition time
  }
}
```

---

### 4. **Randomization Delays**
Advanced randomization for human-like behavior.

```json
{
  "randomization": {
    "position_jitter": 2,          // Pixel variation in target position
    "timing_jitter": 0.05,         // Time variation (±50ms)
    "micro_pause_chance": 0.1,     // 10% chance of micro-pause
    "micro_pause_duration": 0.2    // Micro-pause duration (200ms)
  }
}
```

---

## Flow Diagram

### Complete Action Flow

```
START
  ↓
┌─────────────────────────┐
│ 1. User Presses Hotkey  │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 2. Load Configuration   │
│    - mouse_config.json  │
│    - Validate settings  │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 3. Get Current Position │
│    - Read mouse X, Y    │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 4. Calculate Target     │
│    - Apply jitter       │
│    - Randomize slightly │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 5. Calculate Movement   │
│    Duration = base ±    │
│    variance             │
│    Steps = base ± var   │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 6. Generate Bezier Path │
│    - Create curve       │
│    - Add control points │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 7. Execute Movement     │
│    For each step:       │
│    - Move mouse         │
│    - Wait delay_per_step│
│    - Check for stop     │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 8. Random Micro-Pause?  │
│    If chance triggered: │
│    - Wait 200ms         │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 9. Execute Action       │
│    If click:            │
│    - Press down (50ms)  │
│    - Release (50ms)     │
│    - Wait click_delay   │
│                         │
│    If hold:             │
│    - Press down (50ms)  │
│    - Hold (500ms)       │
│    - Release (100ms)    │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ 10. Post-Action Delay   │
│     - Wait base_delay   │
└───────────┬─────────────┘
            ↓
           END
```

---

## Configuration Parameters

### Complete Configuration File Structure

```json
{
  "delays": {
    "base_delay": 0.05,
    "min_delay": 0.1,
    "max_delay": 0.3,
    "click_delay": 0.05,
    "hold_release_delay": 0.1
  },
  "movement": {
    "base_duration": 0.3,
    "duration_variance": 0.2,
    "steps": 50,
    "step_variance": 20,
    "bezier_control_randomness": 0.3
  },
  "randomization": {
    "position_jitter": 2,
    "timing_jitter": 0.05,
    "micro_pause_chance": 0.1,
    "micro_pause_duration": 0.2,
    "speed_variation": 0.15
  },
  "safety": {
    "max_click_rate": 10,
    "cooldown_period": 0.5,
    "detection_threshold": 100
  }
}
```

### Parameter Descriptions

| Parameter | Type | Range | Purpose |
|-----------|------|-------|---------|
| `base_delay` | float | 0.01-0.5 | Minimum time between any operations |
| `min_delay` | float | 0.05-1.0 | Lower bound for random delays |
| `max_delay` | float | 0.1-2.0 | Upper bound for random delays |
| `click_delay` | float | 0.02-0.2 | Pause after each click |
| `hold_release_delay` | float | 0.05-0.5 | Pause after releasing hold |
| `base_duration` | float | 0.1-1.0 | Average movement time |
| `duration_variance` | float | 0.05-0.5 | Movement time randomization |
| `steps` | int | 20-100 | Movement smoothness |
| `step_variance` | int | 5-50 | Step count randomization |
| `position_jitter` | int | 0-10 | Target position variance (pixels) |
| `timing_jitter` | float | 0.01-0.2 | Time variance per step |
| `micro_pause_chance` | float | 0.0-0.5 | Probability of hesitation |
| `micro_pause_duration` | float | 0.1-1.0 | Hesitation duration |

---

## Implementation Details

### 1. **Delay Calculation Function**

```python
def calculate_delay(base, variance):
    """
    Calculate a randomized delay value.
    
    Args:
        base: Base delay value
        variance: Maximum variance (±)
    
    Returns:
        Randomized delay value
    """
    return base + random.uniform(-variance, variance)
```

**Example**:
```python
base_delay = 0.3
variance = 0.2
result = calculate_delay(0.3, 0.2)
# Returns value between 0.1 and 0.5
```

---

### 2. **Movement Execution**

```python
def move_to_position(target_x, target_y):
    """Execute mouse movement with delays."""
    # Calculate movement parameters
    duration = calculate_delay(
        config['movement']['base_duration'],
        config['movement']['duration_variance']
    )
    
    steps = config['movement']['steps'] + random.randint(
        -config['movement']['step_variance'],
        config['movement']['step_variance']
    )
    
    # Generate Bezier curve
    path = generate_bezier_curve(
        current_x, current_y,
        target_x, target_y,
        steps
    )
    
    # Execute movement
    delay_per_step = duration / steps
    for point in path:
        move_mouse(point[0], point[1])
        time.sleep(delay_per_step + random.uniform(
            -config['randomization']['timing_jitter'],
            config['randomization']['timing_jitter']
        ))
        
        # Random micro-pause
        if random.random() < config['randomization']['micro_pause_chance']:
            time.sleep(config['randomization']['micro_pause_duration'])
```

---

### 3. **Click Action**

```python
def perform_click():
    """Execute click with proper timing."""
    # Press down
    mouse_down()
    time.sleep(config['click_timing']['down_duration'])
    
    # Release
    mouse_up()
    time.sleep(config['click_timing']['up_duration'])
    
    # Post-click delay
    time.sleep(config['delays']['click_delay'])
```

---

### 4. **Hold Action**

```python
def perform_hold():
    """Execute hold action with timing."""
    # Initial press
    mouse_down()
    time.sleep(config['hold_timing']['press_duration'])
    
    # Hold duration (with slight variation)
    hold_time = calculate_delay(
        config['hold_timing']['hold_duration'],
        config['randomization']['timing_jitter']
    )
    time.sleep(hold_time)
    
    # Release
    mouse_up()
    time.sleep(config['hold_timing']['release_duration'])
    
    # Post-release delay
    time.sleep(config['delays']['hold_release_delay'])
```

---

## Anti-Detection Features

### 1. **Timing Randomization**
- **No Fixed Patterns**: Every action has randomized timing
- **Variance Ranges**: ±20-50% variation in all timings
- **Micro-Pauses**: Random hesitations simulate human thought

### 2. **Movement Characteristics**
- **Bezier Curves**: Natural curved paths, not straight lines
- **Variable Speed**: Acceleration and deceleration patterns
- **Position Jitter**: Slight inaccuracy in targeting (±2 pixels)

### 3. **Action Patterns**
- **Click Duration**: 40-60ms (human-like)
- **Hold Variance**: Slightly different hold times each execution
- **Rate Limiting**: Maximum 10 clicks per second

### 4. **Statistical Distribution**
```
Delay Distribution:
    Min: 100ms ──┐
                  │  ▁▃▅▇▅▃▁  ← Most likely: 150-250ms
    Max: 500ms ──┘

This creates a bell curve distribution rather than uniform,
mimicking natural human timing variation.
```

---

## Best Practices

### 1. **Configuration Tuning**

**For Fast Actions** (rapid clicking):
```json
{
  "delays": {
    "base_delay": 0.03,
    "min_delay": 0.05,
    "max_delay": 0.15
  },
  "movement": {
    "base_duration": 0.2
  }
}
```

**For Slow/Careful Actions** (painting):
```json
{
  "delays": {
    "base_delay": 0.1,
    "min_delay": 0.2,
    "max_delay": 0.5
  },
  "movement": {
    "base_duration": 0.5
  }
}
```

---

### 2. **Testing Delays**

Use the included testing tools:
```bash
# Test delay patterns
python test_delays.py

# Visualize timing distribution
python analyze_timing.py
```

---

### 3. **Monitoring**

Enable logging to track timing:
```python
logging.info(f"Movement duration: {duration:.3f}s")
logging.info(f"Steps: {steps}")
logging.info(f"Delay per step: {delay:.4f}s")
```

---

### 4. **Safety Recommendations**

✅ **DO**:
- Use variance in all timing parameters
- Test configurations before long runs
- Monitor for detection warnings
- Adjust based on game behavior

❌ **DON'T**:
- Set delays below 20ms (inhuman)
- Use zero variance (too predictable)
- Ignore safety thresholds
- Run at maximum speed continuously

---

## Timing Examples

### Example 1: Single Click Action
```
Timeline:
0ms     - Hotkey pressed
50ms    - Config loaded
100ms   - Movement starts
400ms   - Movement completes (300ms ± 100ms variance)
450ms   - Mouse down
500ms   - Mouse up
550ms   - Click delay complete
600ms   - Action complete
```

**Total Time**: ~600ms (0.6 seconds)

---

### Example 2: Click and Hold Action
```
Timeline:
0ms     - Hotkey pressed
50ms    - Config loaded
100ms   - Movement starts
450ms   - Movement completes
500ms   - Mouse down (hold begins)
1000ms  - Holding... (500ms base)
1100ms  - Mouse up (release)
1200ms  - Release delay complete
1250ms  - Action complete
```

**Total Time**: ~1250ms (1.25 seconds)

---

### Example 3: Multiple Clicks in Sequence
```
Click 1: 0ms - 600ms
Delay:   600ms - 750ms (random 150ms)
Click 2: 750ms - 1350ms
Delay:   1350ms - 1500ms (random 150ms)
Click 3: 1500ms - 2100ms
```

**Average Rate**: ~3 clicks per 2 seconds = 1.5 clicks/second

---

## Troubleshooting

### Issue: Actions Too Slow
**Solution**: Reduce base delays and variance
```json
{
  "delays": {
    "base_delay": 0.02,
    "min_delay": 0.05,
    "max_delay": 0.15
  }
}
```

---

### Issue: Actions Too Predictable
**Solution**: Increase variance and add micro-pauses
```json
{
  "movement": {
    "duration_variance": 0.3
  },
  "randomization": {
    "micro_pause_chance": 0.2
  }
}
```

---

### Issue: Detection Warnings
**Solution**: Increase randomization and slow down
```json
{
  "delays": {
    "min_delay": 0.2,
    "max_delay": 0.6
  },
  "randomization": {
    "position_jitter": 5,
    "timing_jitter": 0.1
  }
}
```

---

## Summary

The delay system in Heartopia Painter creates human-like behavior through:

1. **Layered Timing**: Base delays + variance + jitter
2. **Movement Curves**: Bezier paths with variable speed
3. **Action Randomization**: Varied click/hold durations
4. **Pattern Breaking**: Micro-pauses and statistical distribution
5. **Safety Limits**: Rate limiting and threshold monitoring

This multi-layered approach ensures that automated actions appear natural and avoid detection by anti-cheat systems.

---

## Related Documents

- `ADVANCED_RANDOMIZATION.md` - Detailed randomization techniques
- `ANTI_DETECTION_INFO.md` - Detection avoidance strategies
- `CLICK_AND_HOLD_GUIDE.md` - Click and hold implementation
- `mouse_config.json` - Configuration file reference

---

**Version**: 1.0  
**Last Updated**: 2026-07-14  
**Author**: Heartopia Painter Development Team
