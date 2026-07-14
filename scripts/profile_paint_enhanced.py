"""
Performance profiling for Enhanced Features

Benchmarks:
- Paint operations with/without enhanced mode
- Memory usage comparison
- CPU usage analysis
- Timing distribution verification
"""

import time
import statistics
import sys
from typing import List, Dict, Tuple
import tracemalloc

sys.path.insert(0, 'src')

from heartopia_painter.delays import DelaySystem, create_default_delay_system
from heartopia_painter.enhanced_paint import MouseController


def benchmark_delay_system(samples: int = 1000) -> Dict[str, float]:
    """Benchmark delay system performance"""
    print(f"\n🔬 Benchmarking Delay System ({samples} samples)...")
    
    # Create delay systems for each profile
    profiles = {
        'fast': create_default_delay_system(profile='fast'),
        'default': create_default_delay_system(profile='default'),
        'careful': create_default_delay_system(profile='careful'),
    }
    
    results = {}
    
    for profile_name, ds in profiles.items():
        print(f"\n  Testing profile: {profile_name}")
        
        # Measure computation time (not actual delay)
        times = []
        for _ in range(samples):
            start = time.perf_counter()
            _ = ds.between_actions()  # Get delay value (don't actually wait)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"    Computation time: {avg_time:.4f}ms (min: {min_time:.4f}ms, max: {max_time:.4f}ms)")
        
        results[profile_name] = {
            'avg_ms': avg_time,
            'min_ms': min_time,
            'max_ms': max_time,
        }
    
    return results


def benchmark_mouse_controller_creation(iterations: int = 100) -> Dict[str, float]:
    """Benchmark MouseController creation time"""
    print(f"\n🔬 Benchmarking MouseController Creation ({iterations} iterations)...")
    
    results = {}
    
    # Test software mode
    print(f"\n  Testing Software Mouse mode...")
    times = []
    for _ in range(iterations):
        ds = create_default_delay_system()
        start = time.perf_counter()
        controller = MouseController(use_hardware=False, delay_system=ds)
        end = time.perf_counter()
        controller.close()
        times.append((end - start) * 1000)
    
    avg_time = statistics.mean(times)
    print(f"    Creation time: {avg_time:.4f}ms")
    results['software'] = avg_time
    
    # Test hardware mode (will fallback if no hardware)
    print(f"\n  Testing Hardware Mouse mode (may fallback to software)...")
    times = []
    for _ in range(iterations):
        ds = create_default_delay_system()
        start = time.perf_counter()
        controller = MouseController(use_hardware=True, delay_system=ds)
        end = time.perf_counter()
        controller.close()
        times.append((end - start) * 1000)
    
    avg_time = statistics.mean(times)
    print(f"    Creation time: {avg_time:.4f}ms")
    results['hardware'] = avg_time
    
    return results


def benchmark_memory_usage() -> Dict[str, float]:
    """Benchmark memory usage of enhanced features"""
    print(f"\n🔬 Benchmarking Memory Usage...")
    
    tracemalloc.start()
    
    # Baseline
    tracemalloc.reset_peak()
    baseline = tracemalloc.get_traced_memory()[0]
    print(f"\n  Baseline: {baseline / 1024:.2f} KB")
    
    # Create delay system
    tracemalloc.reset_peak()
    ds = create_default_delay_system()
    delay_mem = tracemalloc.get_traced_memory()[1] - baseline
    print(f"  DelaySystem: {delay_mem / 1024:.2f} KB")
    
    # Create mouse controller (software)
    tracemalloc.reset_peak()
    controller = MouseController(use_hardware=False, delay_system=ds)
    controller_mem = tracemalloc.get_traced_memory()[1] - baseline
    print(f"  MouseController (software): {controller_mem / 1024:.2f} KB")
    
    # Simulate 100 operations
    tracemalloc.reset_peak()
    for i in range(100):
        _ = ds.between_actions()
    ops_mem = tracemalloc.get_traced_memory()[1] - baseline
    print(f"  After 100 operations: {ops_mem / 1024:.2f} KB")
    
    controller.close()
    tracemalloc.stop()
    
    return {
        'baseline_kb': baseline / 1024,
        'delay_system_kb': delay_mem / 1024,
        'mouse_controller_kb': controller_mem / 1024,
        'after_100_ops_kb': ops_mem / 1024,
    }


def verify_timing_distribution(samples: int = 10000) -> Dict[str, float]:
    """Verify timing distribution matches expected bell curve"""
    print(f"\n🔬 Verifying Timing Distribution ({samples} samples)...")
    
    ds = create_default_delay_system(profile='default')
    
    delays = []
    for _ in range(samples):
        delays.append(ds.between_actions())
    
    avg = statistics.mean(delays)
    median = statistics.median(delays)
    stdev = statistics.stdev(delays)
    min_val = min(delays)
    max_val = max(delays)
    
    print(f"\n  Statistics:")
    print(f"    Mean:     {avg:.4f}s")
    print(f"    Median:   {median:.4f}s")
    print(f"    Std Dev:  {stdev:.4f}s")
    print(f"    Min:      {min_val:.4f}s")
    print(f"    Max:      {max_val:.4f}s")
    
    # Check if distribution is approximately normal
    # For normal distribution: mean ≈ median (within 10%)
    mean_median_diff = abs(avg - median) / avg * 100
    print(f"\n  Bell Curve Check:")
    print(f"    Mean-Median difference: {mean_median_diff:.2f}%")
    
    if mean_median_diff < 10:
        print(f"    ✅ Distribution appears normal (bell curve)")
    else:
        print(f"    ⚠️  Distribution may not be perfectly normal")
    
    return {
        'mean': avg,
        'median': median,
        'stdev': stdev,
        'min': min_val,
        'max': max_val,
        'mean_median_diff_pct': mean_median_diff,
    }


def benchmark_jitter_and_pauses(iterations: int = 1000) -> Dict[str, any]:
    """Benchmark position jitter and micro-pauses"""
    print(f"\n🔬 Benchmarking Jitter & Micro-Pauses ({iterations} iterations)...")
    
    ds = create_default_delay_system()
    controller = MouseController(use_hardware=False, delay_system=ds)
    
    # Count micro-pauses (should be ~10%)
    pause_count = 0
    for _ in range(iterations):
        # Simulate checking if should pause
        if ds.should_micro_pause():
            pause_count += 1
    
    pause_percentage = (pause_count / iterations) * 100
    
    print(f"\n  Micro-Pauses:")
    print(f"    Occurred: {pause_count}/{iterations}")
    print(f"    Percentage: {pause_percentage:.2f}%")
    print(f"    Expected: ~10%")
    
    if 8 <= pause_percentage <= 12:
        print(f"    ✅ Within expected range (8-12%)")
    else:
        print(f"    ⚠️  Outside expected range")
    
    # Test position jitter
    test_x, test_y = 500, 300
    jittered_positions = []
    
    for _ in range(iterations):
        jx, jy = controller._apply_jitter(test_x, test_y)
        jittered_positions.append((jx - test_x, jy - test_y))
    
    # Calculate jitter statistics
    x_deltas = [dx for dx, dy in jittered_positions]
    y_deltas = [dy for dx, dy in jittered_positions]
    
    avg_x_delta = statistics.mean([abs(dx) for dx in x_deltas])
    avg_y_delta = statistics.mean([abs(dy) for dy in y_deltas])
    max_x_delta = max([abs(dx) for dx in x_deltas])
    max_y_delta = max([abs(dy) for dy in y_deltas])
    
    print(f"\n  Position Jitter:")
    print(f"    Avg X delta: {avg_x_delta:.2f}px")
    print(f"    Avg Y delta: {avg_y_delta:.2f}px")
    print(f"    Max X delta: {max_x_delta:.0f}px")
    print(f"    Max Y delta: {max_y_delta:.0f}px")
    print(f"    Expected: ±2px")
    
    if max_x_delta <= 2 and max_y_delta <= 2:
        print(f"    ✅ Jitter within expected range")
    else:
        print(f"    ⚠️  Jitter exceeds expected range")
    
    controller.close()
    
    return {
        'pause_count': pause_count,
        'pause_percentage': pause_percentage,
        'avg_x_delta': avg_x_delta,
        'avg_y_delta': avg_y_delta,
        'max_x_delta': max_x_delta,
        'max_y_delta': max_y_delta,
    }


def print_summary(results: Dict):
    """Print comprehensive summary"""
    print("\n" + "="*70)
    print("📊 Performance Profiling Summary")
    print("="*70)
    
    print("\n🚀 Delay System Performance:")
    if 'delay_system' in results:
        for profile, data in results['delay_system'].items():
            print(f"  {profile.capitalize()}: {data['avg_ms']:.4f}ms avg computation time")
    
    print("\n🖱️ MouseController Creation:")
    if 'mouse_creation' in results:
        for mode, time_ms in results['mouse_creation'].items():
            print(f"  {mode.capitalize()}: {time_ms:.4f}ms")
    
    print("\n💾 Memory Usage:")
    if 'memory' in results:
        mem = results['memory']
        print(f"  Baseline: {mem['baseline_kb']:.2f} KB")
        print(f"  DelaySystem: {mem['delay_system_kb']:.2f} KB")
        print(f"  MouseController: {mem['mouse_controller_kb']:.2f} KB")
        print(f"  After 100 ops: {mem['after_100_ops_kb']:.2f} KB")
    
    print("\n📈 Timing Distribution:")
    if 'timing_dist' in results:
        dist = results['timing_dist']
        print(f"  Mean: {dist['mean']:.4f}s")
        print(f"  Std Dev: {dist['stdev']:.4f}s")
        print(f"  Bell Curve: {'✅ Normal' if dist['mean_median_diff_pct'] < 10 else '⚠️ Check'}")
    
    print("\n🎯 Jitter & Pauses:")
    if 'jitter_pauses' in results:
        jp = results['jitter_pauses']
        print(f"  Micro-pauses: {jp['pause_percentage']:.2f}% (target: 10%)")
        print(f"  Position jitter: ±{jp['max_x_delta']:.0f}px, ±{jp['max_y_delta']:.0f}px (target: ±2px)")
    
    print("\n" + "="*70)
    print("✅ Performance profiling complete!")
    print("="*70 + "\n")


def main():
    """Run all performance benchmarks"""
    print("="*70)
    print("🎨 Heartopia Enhanced Features - Performance Profiling")
    print("="*70)
    
    results = {}
    
    try:
        # Benchmark 1: Delay System
        results['delay_system'] = benchmark_delay_system(samples=1000)
        
        # Benchmark 2: MouseController Creation
        results['mouse_creation'] = benchmark_mouse_controller_creation(iterations=100)
        
        # Benchmark 3: Memory Usage
        results['memory'] = benchmark_memory_usage()
        
        # Benchmark 4: Timing Distribution
        results['timing_dist'] = verify_timing_distribution(samples=10000)
        
        # Benchmark 5: Jitter & Pauses
        results['jitter_pauses'] = benchmark_jitter_and_pauses(iterations=1000)
        
        # Print summary
        print_summary(results)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during profiling: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
