"""
Test Velocity Profiles - Visual demonstration of mouse movement patterns
"""

import time
from src.heartopia_painter.delays import DelaySystem, VelocityProfile

def test_velocity_profiles():
    """Test all velocity profiles and show movement characteristics."""
    
    print("=" * 60)
    print("Velocity Profile Testing")
    print("=" * 60)
    
    ds = DelaySystem()
    
    # Test coordinates
    start = (100, 100)
    end = (500, 300)
    steps = 50
    
    profiles = [
        (VelocityProfile.SMOOTH, "Natural smooth movement (most common)"),
        (VelocityProfile.SLOW_START, "Careful start, accelerate"),
        (VelocityProfile.FAST_START, "Quick reaction, decelerate"),
        (VelocityProfile.HESITANT, "Pause/hesitate mid-movement"),
        (VelocityProfile.OVERSHOOT, "Overshoot then correct"),
        (VelocityProfile.CONSTANT, "Constant speed (robotic)"),
    ]
    
    print("\nTesting each velocity profile:")
    print("-" * 60)
    
    for profile, description in profiles:
        print(f"\n{profile.upper()}")
        print(f"  Description: {description}")
        
        # Generate curve
        curve = ds.generate_bezier_curve(
            start[0], start[1],
            end[0], end[1],
            steps,
            velocity_profile=profile
        )
        
        # Analyze movement
        print(f"  Total points: {len(curve)}")
        print(f"  Start: {curve[0]}")
        print(f"  Quarter: {curve[len(curve)//4]}")
        print(f"  Half: {curve[len(curve)//2]}")
        print(f"  Three-quarter: {curve[3*len(curve)//4]}")
        print(f"  End: {curve[-1]}")
        
        # Calculate distances between consecutive points (speed analysis)
        distances = []
        for i in range(1, len(curve)):
            dx = curve[i][0] - curve[i-1][0]
            dy = curve[i][1] - curve[i-1][1]
            dist = (dx*dx + dy*dy) ** 0.5
            distances.append(dist)
        
        if distances:
            avg_dist = sum(distances) / len(distances)
            max_dist = max(distances)
            min_dist = min(distances)
            
            print(f"  Speed variation:")
            print(f"    Average: {avg_dist:.2f} px/step")
            print(f"    Max: {max_dist:.2f} px/step")
            print(f"    Min: {min_dist:.2f} px/step")
            print(f"    Ratio: {max_dist/min_dist if min_dist > 0 else 0:.2f}x")


def test_velocity_distribution():
    """Test the distribution of randomly selected velocity profiles."""
    
    print("\n" + "=" * 60)
    print("Velocity Profile Distribution Test (10,000 samples)")
    print("=" * 60)
    
    counts = {}
    samples = 10000
    
    for _ in range(samples):
        profile = VelocityProfile.get_random_profile()
        counts[profile] = counts.get(profile, 0) + 1
    
    print("\nDistribution:")
    for profile, count in sorted(counts.items(), key=lambda x: -x[1]):
        percentage = (count / samples) * 100
        bar = "█" * int(percentage / 2)
        expected = {
            VelocityProfile.SMOOTH: 40,
            VelocityProfile.SLOW_START: 25,
            VelocityProfile.FAST_START: 15,
            VelocityProfile.HESITANT: 10,
            VelocityProfile.OVERSHOOT: 7,
            VelocityProfile.CONSTANT: 3,
        }.get(profile, 0)
        
        print(f"  {profile:15} {count:5} ({percentage:5.2f}%)  Expected: {expected}%  {bar}")


def test_easing_functions():
    """Test easing functions mathematically."""
    
    print("\n" + "=" * 60)
    print("Easing Function Test")
    print("=" * 60)
    
    test_times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    profiles = [
        VelocityProfile.SLOW_START,
        VelocityProfile.FAST_START,
        VelocityProfile.SMOOTH,
        VelocityProfile.HESITANT,
        VelocityProfile.OVERSHOOT,
    ]
    
    for profile in profiles:
        print(f"\n{profile.upper()}:")
        print("  t     -> eased_t")
        print("  " + "-" * 20)
        for t in test_times:
            eased = VelocityProfile.apply_easing(t, profile)
            bar = "█" * int(eased * 20)
            print(f"  {t:.1f}  ->  {eased:.3f}  {bar}")


def visualize_curves_ascii():
    """Create ASCII visualization of different velocity profiles."""
    
    print("\n" + "=" * 60)
    print("ASCII Visualization (Time vs Position)")
    print("=" * 60)
    
    profiles = [
        VelocityProfile.SMOOTH,
        VelocityProfile.SLOW_START,
        VelocityProfile.FAST_START,
        VelocityProfile.HESITANT,
    ]
    
    width = 50
    height = 20
    
    for profile in profiles:
        print(f"\n{profile.upper()}:")
        
        # Create grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Draw axes
        for x in range(width):
            grid[height-1][x] = '-'
        for y in range(height):
            grid[y][0] = '|'
        grid[height-1][0] = '+'
        
        # Draw curve
        for x in range(1, width):
            t = x / (width - 1)
            eased = VelocityProfile.apply_easing(t, profile)
            y = int((1 - eased) * (height - 2))
            y = max(0, min(height-2, y))
            grid[y][x] = '●'
        
        # Print grid
        for row in grid:
            print('  ' + ''.join(row))


if __name__ == "__main__":
    test_velocity_profiles()
    test_velocity_distribution()
    test_easing_functions()
    visualize_curves_ascii()
    
    print("\n" + "=" * 60)
    print("✓ All tests complete!")
    print("=" * 60)
