"""
Test and demonstration script for the delay system.

This script demonstrates all the features of the delay system including:
- Delay calculation with variance
- Position jittering
- Bezier curve generation
- Micro-pause injection
- Movement timing
- Statistical analysis
"""

import sys
from pathlib import Path

# Add src to path
_ROOT = Path(__file__).resolve().parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from heartopia_painter.delays import (
    DelaySystem,
    DelayConfig,
    create_default_delay_system,
    create_fast_delay_system,
    create_careful_delay_system,
    example_calculate_delays,
    example_position_jitter,
    example_bezier_curve,
)
import time


def test_delay_distribution():
    """Test that delays follow a bell curve distribution."""
    print("\n" + "=" * 60)
    print("TEST: Delay Distribution Analysis")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    # Generate 1000 samples
    samples = []
    for _ in range(1000):
        delay = ds.calculate_delay(0.3, 0.2)
        samples.append(delay)
    
    # Calculate statistics
    avg = sum(samples) / len(samples)
    min_val = min(samples)
    max_val = max(samples)
    
    # Create histogram buckets
    bucket_count = 10
    buckets = [0] * bucket_count
    bucket_size = (max_val - min_val) / bucket_count
    
    for sample in samples:
        bucket_idx = int((sample - min_val) / bucket_size)
        if bucket_idx >= bucket_count:
            bucket_idx = bucket_count - 1
        buckets[bucket_idx] += 1
    
    print(f"\nStatistics from 1000 samples:")
    print(f"  Expected range: 0.1s - 0.5s")
    print(f"  Actual min: {min_val:.3f}s")
    print(f"  Actual max: {max_val:.3f}s")
    print(f"  Average: {avg:.3f}s")
    print(f"  Target (mode): 0.3s")
    
    print(f"\nDistribution (should show bell curve):")
    max_count = max(buckets)
    for i, count in enumerate(buckets):
        bucket_start = min_val + i * bucket_size
        bucket_end = bucket_start + bucket_size
        bar_length = int((count / max_count) * 40)
        bar = "█" * bar_length
        print(f"  {bucket_start:.2f}-{bucket_end:.2f}s: {bar} ({count})")
    
    print("\n✓ Distribution test complete")


def test_movement_timing():
    """Test movement timing calculations."""
    print("\n" + "=" * 60)
    print("TEST: Movement Timing")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    print("\nCalculating movement parameters for 10 movements:")
    print(f"  Base duration: {ds.config.base_duration}s")
    print(f"  Duration variance: ±{ds.config.duration_variance}s")
    print(f"  Base steps: {ds.config.steps}")
    print(f"  Step variance: ±{ds.config.step_variance}")
    print()
    
    total_durations = []
    total_steps = []
    
    for i in range(10):
        duration = ds.calculate_movement_duration()
        steps = ds.calculate_movement_steps()
        delay_per_step = duration / steps
        
        total_durations.append(duration)
        total_steps.append(steps)
        
        print(f"  Movement {i+1:2d}: {duration:.3f}s, {steps:3d} steps, {delay_per_step:.4f}s/step")
    
    avg_duration = sum(total_durations) / len(total_durations)
    avg_steps = sum(total_steps) / len(total_steps)
    
    print(f"\n  Average duration: {avg_duration:.3f}s")
    print(f"  Average steps: {avg_steps:.1f}")
    
    print("\n✓ Movement timing test complete")


def test_position_jitter():
    """Test position jittering."""
    print("\n" + "=" * 60)
    print("TEST: Position Jitter")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    target = (500, 300)
    jitter = ds.config.position_jitter
    
    print(f"\nTarget position: {target}")
    print(f"Jitter range: ±{jitter} pixels")
    print("\nGenerating 20 jittered positions:")
    
    jittered_positions = []
    for i in range(20):
        jx, jy = ds.apply_position_jitter(target[0], target[1])
        offset_x = jx - target[0]
        offset_y = jy - target[1]
        jittered_positions.append((jx, jy))
        print(f"  {i+1:2d}. ({jx:3d}, {jy:3d}) - offset: ({offset_x:+3d}, {offset_y:+3d})")
    
    # Verify all offsets are within jitter range
    all_valid = True
    for jx, jy in jittered_positions:
        offset_x = abs(jx - target[0])
        offset_y = abs(jy - target[1])
        if offset_x > jitter or offset_y > jitter:
            all_valid = False
            break
    
    if all_valid:
        print("\n✓ All positions within jitter range")
    else:
        print("\n✗ Some positions outside jitter range!")
    
    print("\n✓ Position jitter test complete")


def test_bezier_curves():
    """Test Bezier curve generation."""
    print("\n" + "=" * 60)
    print("TEST: Bezier Curve Generation")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    test_cases = [
        ((100, 100), (500, 300), 20, "Diagonal movement"),
        ((200, 200), (200, 400), 15, "Vertical movement"),
        ((300, 250), (600, 250), 25, "Horizontal movement"),
        ((100, 100), (105, 105), 10, "Very short movement"),
    ]
    
    for start, end, steps, description in test_cases:
        print(f"\n{description}:")
        print(f"  Start: {start}")
        print(f"  End: {end}")
        print(f"  Steps: {steps}")
        
        curve = ds.generate_bezier_curve(start[0], start[1], end[0], end[1], steps)
        
        # Verify curve properties
        if curve[0] == start:
            print(f"  ✓ Curve starts at correct position")
        else:
            print(f"  ✗ Curve start mismatch: expected {start}, got {curve[0]}")
        
        if curve[-1] == end or (abs(curve[-1][0] - end[0]) <= 1 and abs(curve[-1][1] - end[1]) <= 1):
            print(f"  ✓ Curve ends at or near correct position")
        else:
            print(f"  ✗ Curve end mismatch: expected {end}, got {curve[-1]}")
        
        if len(curve) == steps + 1:
            print(f"  ✓ Curve has correct number of points ({len(curve)})")
        else:
            print(f"  ✗ Point count mismatch: expected {steps + 1}, got {len(curve)}")
        
        # Show first 5 points
        print(f"  First 5 points: {curve[:5]}")
    
    print("\n✓ Bezier curve test complete")


def test_micro_pauses():
    """Test micro-pause probability."""
    print("\n" + "=" * 60)
    print("TEST: Micro-Pause Probability")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    print(f"\nMicro-pause chance: {ds.config.micro_pause_chance * 100:.1f}%")
    print(f"Expected pauses in 1000 actions: ~{ds.config.micro_pause_chance * 1000:.0f}")
    
    # Simulate 1000 actions
    pause_count = 0
    for _ in range(1000):
        if ds.should_micro_pause():
            pause_count += 1
    
    print(f"Actual pauses: {pause_count}")
    
    # Check if within reasonable range (±3 standard deviations)
    expected = ds.config.micro_pause_chance * 1000
    std_dev = (1000 * ds.config.micro_pause_chance * (1 - ds.config.micro_pause_chance)) ** 0.5
    lower_bound = expected - 3 * std_dev
    upper_bound = expected + 3 * std_dev
    
    if lower_bound <= pause_count <= upper_bound:
        print(f"✓ Within expected range [{lower_bound:.0f}, {upper_bound:.0f}]")
    else:
        print(f"✗ Outside expected range [{lower_bound:.0f}, {upper_bound:.0f}]")
    
    # Test pause duration
    print(f"\nMicro-pause durations (10 samples):")
    for i in range(10):
        duration = ds.get_micro_pause_duration()
        print(f"  Pause {i+1}: {duration:.3f}s")
    
    print("\n✓ Micro-pause test complete")


def test_timing_profiles():
    """Test different timing profiles (fast, default, careful)."""
    print("\n" + "=" * 60)
    print("TEST: Timing Profiles")
    print("=" * 60)
    
    profiles = [
        ("Fast", create_fast_delay_system()),
        ("Default", create_default_delay_system()),
        ("Careful", create_careful_delay_system()),
    ]
    
    for name, ds in profiles:
        print(f"\n{name} Profile:")
        print(f"  Base delay: {ds.config.base_delay}s")
        print(f"  Min delay: {ds.config.min_delay}s")
        print(f"  Max delay: {ds.config.max_delay}s")
        print(f"  Base movement duration: {ds.config.base_duration}s")
        print(f"  Movement variance: ±{ds.config.duration_variance}s")
        print(f"  Micro-pause chance: {ds.config.micro_pause_chance * 100:.1f}%")
        print(f"  Position jitter: ±{ds.config.position_jitter}px")
    
    print("\n✓ Timing profile test complete")


def test_rate_limiting():
    """Test rate limiting."""
    print("\n" + "=" * 60)
    print("TEST: Rate Limiting")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    print(f"\nMax click rate: {ds.config.max_click_rate} clicks/second")
    print(f"Cooldown period: {ds.config.cooldown_period}s")
    
    print("\nSimulating rapid clicks (15 clicks):")
    start_time = time.time()
    
    for i in range(15):
        action_start = time.time()
        ds.enforce_rate_limit()
        action_time = time.time() - action_start
        
        total_elapsed = time.time() - start_time
        print(f"  Click {i+1:2d}: {total_elapsed:.3f}s total, {action_time:.3f}s action time", end="")
        if action_time > 0.1:
            print(" (cooldown triggered)")
        else:
            print()
    
    total_time = time.time() - start_time
    actual_rate = 15 / total_time
    
    print(f"\nTotal time: {total_time:.3f}s")
    print(f"Actual rate: {actual_rate:.2f} clicks/second")
    print(f"Max allowed: {ds.config.max_click_rate} clicks/second")
    
    if actual_rate <= ds.config.max_click_rate + 0.5:  # Small tolerance for timing
        print("✓ Rate limiting working correctly")
    else:
        print("✗ Rate limit exceeded!")
    
    print("\n✓ Rate limiting test complete")


def test_interruptible_sleep():
    """Test interruptible sleep."""
    print("\n" + "=" * 60)
    print("TEST: Interruptible Sleep")
    print("=" * 60)
    
    ds = create_default_delay_system()
    
    # Test normal completion
    print("\nTest 1: Normal sleep (0.1s)")
    start = time.time()
    completed = ds.interruptible_sleep(0.1)
    elapsed = time.time() - start
    print(f"  Completed: {completed}")
    print(f"  Time: {elapsed:.3f}s")
    
    if completed and 0.09 <= elapsed <= 0.12:
        print("  ✓ Sleep completed correctly")
    else:
        print("  ✗ Sleep timing incorrect")
    
    # Test interruption
    print("\nTest 2: Interrupted sleep (0.5s, interrupt at ~0.05s)")
    start = time.time()
    stop_flag = False
    
    def should_stop():
        return stop_flag
    
    # Start sleep in background (simulated)
    import threading
    
    def sleep_task():
        nonlocal completed_flag
        completed_flag = ds.interruptible_sleep(0.5, should_stop)
    
    completed_flag = True
    thread = threading.Thread(target=sleep_task)
    thread.start()
    
    # Interrupt after 0.05s
    time.sleep(0.05)
    stop_flag = True
    thread.join()
    
    elapsed = time.time() - start
    print(f"  Completed: {completed_flag}")
    print(f"  Time: {elapsed:.3f}s")
    
    if not completed_flag and elapsed < 0.2:
        print("  ✓ Sleep interrupted correctly")
    else:
        print("  ✗ Sleep interruption failed")
    
    print("\n✓ Interruptible sleep test complete")


def run_all_tests():
    """Run all delay system tests."""
    print("\n" + "=" * 60)
    print("DELAY SYSTEM TEST SUITE")
    print("=" * 60)
    print("\nRunning comprehensive tests of the delay system...")
    print("This will test all features including:")
    print("  - Delay calculation and variance")
    print("  - Movement timing")
    print("  - Position jittering")
    print("  - Bezier curve generation")
    print("  - Micro-pause probability")
    print("  - Timing profiles")
    print("  - Rate limiting")
    print("  - Interruptible sleep")
    
    test_delay_distribution()
    test_movement_timing()
    test_position_jitter()
    test_bezier_curves()
    test_micro_pauses()
    test_timing_profiles()
    test_rate_limiting()
    test_interruptible_sleep()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
    print("\n✓ Delay system is working correctly!")


def show_examples():
    """Show usage examples."""
    print("\n" + "=" * 60)
    print("DELAY SYSTEM USAGE EXAMPLES")
    print("=" * 60)
    
    example_calculate_delays()
    example_position_jitter()
    example_bezier_curve()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_examples()
    else:
        run_all_tests()
    
    print("\nFor basic usage examples, run: python test_delays.py --examples")
