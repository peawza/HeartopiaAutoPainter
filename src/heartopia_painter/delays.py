"""
Delay System - Human-like timing and randomization

This module implements a comprehensive delay system with multiple layers
of randomization to create natural, human-like mouse movement and action
timing patterns that avoid detection.

Key Features:
- Base delays with variance
- Movement duration randomization
- Position jitter
- Timing jitter
- Micro-pause injection
- Bezier curve generation for natural mouse paths
- Statistical distribution (bell curve, not uniform)
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import MouseConfig


Point = Tuple[int, int]


class VelocityProfile:
    """Velocity profiles for natural mouse movement patterns."""
    
    SLOW_START = "slow_start"           # Start slow, accelerate
    FAST_START = "fast_start"           # Start fast, decelerate
    CONSTANT = "constant"               # Constant speed (boring, use rarely)
    HESITANT = "hesitant"               # Pause/hesitate mid-movement
    SMOOTH = "smooth"                   # Smooth ease-in-out (most natural)
    OVERSHOOT = "overshoot"             # Overshoot target then correct
    
    @staticmethod
    def get_random_profile() -> str:
        """Get a random velocity profile with realistic distribution."""
        profiles = [
            (VelocityProfile.SMOOTH, 0.40),      # 40% - most common
            (VelocityProfile.SLOW_START, 0.25),  # 25% - careful start
            (VelocityProfile.FAST_START, 0.15),  # 15% - quick reaction
            (VelocityProfile.HESITANT, 0.10),    # 10% - uncertainty
            (VelocityProfile.OVERSHOOT, 0.07),   # 7%  - common mistake
            (VelocityProfile.CONSTANT, 0.03),    # 3%  - rare/robotic
        ]
        
        rand = random.random()
        cumulative = 0.0
        for profile, probability in profiles:
            cumulative += probability
            if rand <= cumulative:
                return profile
        return VelocityProfile.SMOOTH
    
    @staticmethod
    def apply_easing(t: float, profile: str) -> float:
        """
        Apply easing function to normalize time value (0.0 to 1.0).
        
        Args:
            t: Normalized time (0.0 to 1.0)
            profile: Velocity profile name
        
        Returns:
            Eased time value
        """
        if profile == VelocityProfile.SLOW_START:
            # Quadratic ease-in: slow start, faster end
            return t * t
        
        elif profile == VelocityProfile.FAST_START:
            # Quadratic ease-out: fast start, slower end
            return t * (2 - t)
        
        elif profile == VelocityProfile.SMOOTH:
            # Smoothstep: slow-fast-slow (most natural)
            return t * t * (3 - 2 * t)
        
        elif profile == VelocityProfile.HESITANT:
            # Pause in the middle
            if t < 0.3:
                # Normal speed to 30%
                return t * 0.8
            elif t < 0.5:
                # Slow down / pause
                return 0.24 + (t - 0.3) * 0.1
            else:
                # Resume and finish
                return 0.26 + (t - 0.5) * 1.48
        
        elif profile == VelocityProfile.OVERSHOOT:
            # Go past target then back (common human error)
            if t < 0.8:
                # Move 110% of the way
                return (t / 0.8) * 1.10
            else:
                # Correct back to 100%
                return 1.10 - (t - 0.8) * 0.5
        
        else:  # CONSTANT
            return t
    
    @staticmethod
    def apply_acceleration_curve(t: float, factor: float = 0.3) -> float:
        """
        Apply acceleration curve (ease-in-out with custom factor).
        
        This creates natural human-like acceleration:
        - Start slow (0-30%)
        - Speed up (30-70%)
        - Slow down (70-100%)
        
        Args:
            t: Normalized time (0.0 to 1.0)
            factor: Acceleration factor (0.0 = linear, 1.0 = max curve)
        
        Returns:
            Accelerated time value
        """
        # Smootherstep (more natural than smoothstep)
        # Formula: 6t^5 - 15t^4 + 10t^3
        smooth = t * t * t * (t * (t * 6 - 15) + 10)
        
        # Blend between linear and smooth based on factor
        return t + (smooth - t) * factor


@dataclass
class DelayConfig:
    """Configuration for all delay and randomization parameters."""
    
    # Base Delays (seconds)
    base_delay: float = 0.05
    min_delay: float = 0.1
    max_delay: float = 0.4  # Increased from 0.3
    click_delay: float = 0.05
    hold_release_delay: float = 0.1
    
    # Movement Delays
    base_duration: float = 0.3
    duration_variance: float = 0.25  # Increased from 0.2
    steps: int = 50
    step_variance: int = 30  # Increased from 20
    bezier_control_randomness: float = 0.4  # Increased from 0.3
    
    # Randomization
    position_jitter: int = 3  # Increased from 2 but still safe
    timing_jitter: float = 0.08  # Increased from 0.05
    micro_pause_chance: float = 0.25  # Increased from 0.1
    micro_pause_duration: float = 0.3  # Increased from 0.2
    speed_variation: float = 0.20  # Increased from 0.15
    
    # Double-Click Variation (NEW!)
    double_click_min: float = 0.08  # Minimum time between double clicks
    double_click_max: float = 0.15  # Maximum time between double clicks
    
    # Acceleration/Deceleration (NEW!)
    enable_acceleration: bool = True  # Enable smooth acceleration
    accel_factor: float = 0.3  # How much to accelerate (0-1)
    
    # Safety
    max_click_rate: int = 10
    cooldown_period: float = 0.5
    detection_threshold: int = 100


@dataclass
class ClickTiming:
    """Timing configuration for click actions."""
    down_duration: float = 0.05
    up_duration: float = 0.05
    between_clicks: float = 0.1


@dataclass
class HoldTiming:
    """Timing configuration for hold actions."""
    press_duration: float = 0.05
    hold_duration: float = 0.5
    release_duration: float = 0.1


class DelaySystem:
    """
    Main delay system class that provides human-like timing and randomization.
    
    This class handles:
    - Delay calculation with variance
    - Position jittering
    - Bezier curve generation for natural movement
    - Micro-pause injection
    - Statistical timing distribution
    - Dual-range delays (fast/slow variation)
    - Mistake simulation
    - Speed variation
    - Break timer
    - Fatigue simulation
    """
    
    def __init__(self, config: Optional[DelayConfig] = None, mouse_config: Optional["MouseConfig"] = None):
        """Initialize the delay system with the given configuration."""
        self.config = config or DelayConfig()
        self.mouse_config = mouse_config
        self._last_action_time: float = 0.0
        self._action_count: int = 0
        self._start_time: float = time.time()
        self._session_start_time: float = time.time()
        
        # Break timer state
        self._actions_since_break: int = 0
        self._next_break_at: int = 0
        if mouse_config and mouse_config.enable_breaks:
            self._next_break_at = random.randint(
                mouse_config.break_min_actions,
                mouse_config.break_max_actions
            )
    
    def calculate_dual_range_delay(self) -> float:
        """
        Calculate delay using dual-range distribution (fast or slow).
        
        Returns random delay from either:
        - Fast range: delay_min_ms to (delay_min_ms + 30ms)
        - Slow range: (delay_max_ms - 30ms) to delay_max_ms
        
        This creates more human-like variation than uniform distribution.
        
        Returns:
            Delay in seconds
        """
        if not self.mouse_config:
            return self.calculate_delay(self.config.base_delay, self.config.min_delay)
        
        min_ms = self.mouse_config.delay_min_ms
        max_ms = self.mouse_config.delay_max_ms
        
        # 50% chance for fast range, 50% for slow range
        if random.random() < 0.5:
            # Fast range: min to (min + 30)
            delay_ms = random.uniform(min_ms, min(min_ms + 30, max_ms))
        else:
            # Slow range: (max - 30) to max
            delay_ms = random.uniform(max(max_ms - 30, min_ms), max_ms)
        
        return delay_ms / 1000.0  # Convert to seconds
    
    def should_make_mistake(self) -> bool:
        """
        Determine if a mistake should occur (click wrong position first).
        
        Returns:
            True if should simulate a mistake (5% default)
        """
        if not self.mouse_config or not self.mouse_config.enable_mistakes:
            return False
        
        return random.random() < self.mouse_config.mistake_probability
    
    def generate_mistake_offset(self, click_randomness_px: int = 25) -> Tuple[int, int]:
        """
        Generate random offset for a mistake click.
        
        Args:
            click_randomness_px: Maximum offset in pixels
        
        Returns:
            (offset_x, offset_y) tuple for the mistake position
        """
        # Mistake should be further away than normal jitter
        offset_range = click_randomness_px * 2
        offset_x = random.randint(-offset_range, offset_range)
        offset_y = random.randint(-offset_range, offset_range)
        return (offset_x, offset_y)
    
    def get_speed_multiplier(self) -> float:
        """
        Get random speed multiplier for action timing.
        
        Returns:
            Multiplier between speed_variation_min and speed_variation_max
            (default: 0.75 to 1.25)
        """
        if not self.mouse_config or not self.mouse_config.enable_speed_variation:
            return 1.0
        
        return random.uniform(
            self.mouse_config.speed_variation_min,
            self.mouse_config.speed_variation_max
        )
    
    def should_take_break(self) -> bool:
        """
        Check if it's time for a break.
        
        Returns:
            True if should take a break now
        """
        if not self.mouse_config or not self.mouse_config.enable_breaks:
            return False
        
        self._actions_since_break += 1
        
        if self._actions_since_break >= self._next_break_at:
            # Reset counters and schedule next break
            self._actions_since_break = 0
            self._next_break_at = random.randint(
                self.mouse_config.break_min_actions,
                self.mouse_config.break_max_actions
            )
            return True
        
        return False
    
    def get_break_duration(self) -> float:
        """
        Get random break duration.
        
        Returns:
            Break duration in seconds (15-45s default)
        """
        if not self.mouse_config:
            return 20.0
        
        return random.uniform(
            self.mouse_config.break_min_duration_s,
            self.mouse_config.break_max_duration_s
        )
    
    def get_fatigue_multiplier(self) -> float:
        """
        Calculate fatigue slowdown multiplier based on action count.
        
        Returns:
            Multiplier >= 1.0 (slower as actions increase)
            Max: fatigue_max_multiplier (default 1.5 = 50% slower)
        """
        if not self.mouse_config or not self.mouse_config.enable_fatigue:
            return 1.0
        
        # Calculate slowdown: 0.8% per 100 actions
        slowdown = (self._action_count / 100.0) * self.mouse_config.fatigue_slowdown_per_100_actions
        multiplier = 1.0 + slowdown
        
        # Cap at max multiplier
        return min(multiplier, self.mouse_config.fatigue_max_multiplier)
    
    def check_session_time_limit(self) -> bool:
        """
        Check if session time limit has been exceeded.
        
        Returns:
            True if session should end (exceeded time limit)
        """
        if not self.mouse_config:
            return False
        
        elapsed_hours = (time.time() - self._session_start_time) / 3600.0
        return elapsed_hours >= self.mouse_config.session_time_limit_hours
    
    def increment_action_count(self) -> None:
        """Increment action counter (for fatigue and break tracking)."""
        self._action_count += 1
    
    def calculate_delay(self, base: float, variance: float) -> float:
        """
        Calculate a randomized delay value using bell curve distribution.
        
        Args:
            base: Base delay value
            variance: Maximum variance (±)
        
        Returns:
            Randomized delay value with bell curve distribution
        """
        # Use triangular distribution for a more natural bell curve
        # (closer to human timing than uniform distribution)
        return max(0.0, random.triangular(
            base - variance,
            base + variance,
            base  # mode (most likely value)
        ))
    
    def calculate_movement_duration(self) -> float:
        """
        Calculate randomized movement duration.
        
        Returns:
            Duration in seconds with variance applied
        """
        return self.calculate_delay(
            self.config.base_duration,
            self.config.duration_variance
        )
    
    def calculate_movement_steps(self) -> int:
        """
        Calculate randomized number of movement steps.
        
        Returns:
            Number of steps with variance applied
        """
        steps = self.config.steps + random.randint(
            -self.config.step_variance,
            self.config.step_variance
        )
        return max(10, steps)  # Ensure minimum steps for smoothness
    
    def apply_position_jitter(self, x: int, y: int) -> Tuple[int, int]:
        """
        Apply random jitter to target position for human-like inaccuracy.
        
        Args:
            x: Target x coordinate
            y: Target y coordinate
        
        Returns:
            Jittered (x, y) coordinates
        """
        if not getattr(self, "enable_position_jitter", False):
            return (int(x), int(y))

        jitter = self.config.position_jitter
        jx = random.randint(-jitter, jitter)
        jy = random.randint(-jitter, jitter)
        return (int(x + jx), int(y + jy))
    
    def should_micro_pause(self) -> bool:
        """
        Determine if a micro-pause should occur (simulates human hesitation).
        
        Returns:
            True if a micro-pause should happen
        """
        return random.random() < self.config.micro_pause_chance
    
    def get_micro_pause_duration(self) -> float:
        """
        Get a randomized micro-pause duration.
        
        Returns:
            Micro-pause duration in seconds
        """
        return self.calculate_delay(
            self.config.micro_pause_duration,
            self.config.micro_pause_duration * 0.3
        )
    
    def generate_bezier_curve(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        steps: int,
        velocity_profile: Optional[str] = None
    ) -> List[Point]:
        """
        Generate a Bezier curve path from start to end with natural control points
        and velocity profile.
        
        Args:
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            end_x: Ending x coordinate
            end_y: Ending y coordinate
            steps: Number of points in the curve
            velocity_profile: Optional velocity profile name (random if None)
        
        Returns:
            List of (x, y) points along the Bezier curve with velocity applied
        """
        # Generate control points with randomness for natural curves
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Add perpendicular offset for curve control points
        dx = end_x - start_x
        dy = end_y - start_y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance < 1:
            # Too short for a curve, return straight line
            return [(start_x, start_y), (end_x, end_y)]
        
        # Perpendicular direction
        perp_x = -dy / distance
        perp_y = dx / distance
        
        # Random offset along perpendicular (creates natural curve)
        offset_amount = distance * self.config.bezier_control_randomness * random.uniform(-1, 1)
        
        ctrl1_x = mid_x + perp_x * offset_amount * 0.5
        ctrl1_y = mid_y + perp_y * offset_amount * 0.5
        ctrl2_x = mid_x + perp_x * offset_amount
        ctrl2_y = mid_y + perp_y * offset_amount
        
        # Select velocity profile
        if velocity_profile is None:
            velocity_profile = VelocityProfile.get_random_profile()
        
        # Generate cubic Bezier curve points with velocity profile
        points: List[Point] = []
        for i in range(steps + 1):
            t_linear = i / steps
            
            # Apply velocity profile (easing)
            t = VelocityProfile.apply_easing(t_linear, velocity_profile)
            
            # Apply acceleration curve if enabled
            if self.config.enable_acceleration:
                t = VelocityProfile.apply_acceleration_curve(t, self.config.accel_factor)
            
            # Clamp t to [0, 1] (for overshoot correction)
            t = max(0.0, min(1.0, t))
            
            # Cubic Bezier formula
            u = 1 - t
            tt = t * t
            uu = u * u
            uuu = uu * u
            ttt = tt * t
            
            x = uuu * start_x
            x += 3 * uu * t * ctrl1_x
            x += 3 * u * tt * ctrl2_x
            x += ttt * end_x
            
            y = uuu * start_y
            y += 3 * uu * t * ctrl1_y
            y += 3 * u * tt * ctrl2_y
            y += ttt * end_y
            
            points.append((int(round(x)), int(round(y))))
        
        return points
    
    def get_step_delay(self, base_step_delay: float) -> float:
        """
        Calculate delay for a single movement step with jitter.
        
        Args:
            base_step_delay: Base delay per step
        
        Returns:
            Step delay with timing jitter applied
        """
        return max(0.0, base_step_delay + random.uniform(
            -self.config.timing_jitter,
            self.config.timing_jitter
        ))
    
    def enforce_rate_limit(self) -> None:
        """
        Enforce maximum click rate to prevent inhuman speeds.
        This implements safety throttling.
        """
        now = time.time()
        
        # Reset counter every second
        if now - self._start_time >= 1.0:
            self._action_count = 0
            self._start_time = now
        
        self._action_count += 1
        
        # If we're approaching the rate limit, add cooldown
        if self._action_count >= self.config.max_click_rate:
            time.sleep(self.config.cooldown_period)
            self._action_count = 0
            self._start_time = time.time()
    
    def interruptible_sleep(
        self,
        duration: float,
        should_stop: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Sleep for the given duration, but check for interruption frequently.
        
        Args:
            duration: Sleep duration in seconds
            should_stop: Optional callback to check if we should stop early
        
        Returns:
            True if sleep completed, False if interrupted
        """
        if duration <= 0:
            return True
        
        end_time = time.time() + duration
        
        while True:
            if should_stop and should_stop():
                return False
            
            now = time.time()
            if now >= end_time:
                return True
            
            # Sleep in small chunks (20ms) for responsiveness
            time.sleep(min(0.02, end_time - now))
    
    def get_random_delay(self) -> float:
        """
        Get a random delay between min_delay and max_delay.
        Uses bell curve distribution for natural timing.
        
        Returns:
            Random delay in seconds
        """
        mid = (self.config.min_delay + self.config.max_delay) / 2
        return max(
            self.config.min_delay,
            min(
                self.config.max_delay,
                random.triangular(
                    self.config.min_delay,
                    self.config.max_delay,
                    mid
                )
            )
        )
    
    def get_double_click_delay(self) -> float:
        """
        Get random delay for double-click (varies naturally).
        
        Human double-click timing varies between 80-150ms typically,
        not constant like bots.
        
        Returns:
            Double-click delay in seconds (0.08-0.15s)
        """
        return random.uniform(
            self.config.double_click_min,
            self.config.double_click_max
        )


def create_default_delay_system() -> DelaySystem:
    """
    Create a delay system with default configuration.
    
    Returns:
        DelaySystem instance with default settings
    """
    return DelaySystem(DelayConfig())


def create_fast_delay_system() -> DelaySystem:
    """
    Create a delay system optimized for fast actions (rapid clicking).
    
    Returns:
        DelaySystem instance with fast timing settings
    """
    config = DelayConfig(
        base_delay=0.03,
        min_delay=0.05,
        max_delay=0.15,
        click_delay=0.03,
        base_duration=0.2,
        duration_variance=0.1,
        micro_pause_chance=0.05,
    )
    return DelaySystem(config)


def create_careful_delay_system() -> DelaySystem:
    """
    Create a delay system optimized for careful/slow actions (painting).
    
    Returns:
        DelaySystem instance with careful timing settings
    """
    config = DelayConfig(
        base_delay=0.1,
        min_delay=0.2,
        max_delay=0.5,
        click_delay=0.1,
        hold_release_delay=0.15,
        base_duration=0.5,
        duration_variance=0.3,
        micro_pause_chance=0.15,
        position_jitter=3,
    )
    return DelaySystem(config)


# Utility functions for common delay patterns

def create_click_timing(fast: bool = False) -> ClickTiming:
    """
    Create timing configuration for click actions.
    
    Args:
        fast: If True, use faster timing for rapid clicks
    
    Returns:
        ClickTiming instance
    """
    if fast:
        return ClickTiming(
            down_duration=0.03,
            up_duration=0.03,
            between_clicks=0.05
        )
    return ClickTiming()


def create_hold_timing(long_hold: bool = False) -> HoldTiming:
    """
    Create timing configuration for hold actions.
    
    Args:
        long_hold: If True, use longer hold duration
    
    Returns:
        HoldTiming instance
    """
    if long_hold:
        return HoldTiming(
            press_duration=0.05,
            hold_duration=1.0,
            release_duration=0.15
        )
    return HoldTiming()


# Example usage functions (for testing)

def example_calculate_delays():
    """Example showing how delays are calculated with variance."""
    ds = create_default_delay_system()
    
    print("Example delay calculations:")
    print("-" * 50)
    
    for i in range(10):
        delay = ds.calculate_delay(0.3, 0.2)
        print(f"  Delay {i+1}: {delay:.3f}s (range: 0.1s - 0.5s)")
    
    print()
    print("Movement parameters:")
    for i in range(5):
        duration = ds.calculate_movement_duration()
        steps = ds.calculate_movement_steps()
        delay_per_step = duration / steps
        print(f"  Movement {i+1}: {duration:.3f}s, {steps} steps, {delay_per_step:.4f}s per step")


def example_position_jitter():
    """Example showing position jittering."""
    ds = create_default_delay_system()
    
    print("\nExample position jittering:")
    print("-" * 50)
    
    target = (500, 300)
    print(f"  Original target: {target}")
    
    for i in range(10):
        jittered = ds.apply_position_jitter(target[0], target[1])
        offset_x = jittered[0] - target[0]
        offset_y = jittered[1] - target[1]
        print(f"  Jittered {i+1}: {jittered} (offset: {offset_x:+d}, {offset_y:+d})")


def example_bezier_curve():
    """Example showing Bezier curve generation with velocity profiles."""
    ds = create_default_delay_system()
    
    print("\nExample Bezier curve generation with velocity profiles:")
    print("-" * 50)
    
    start = (100, 100)
    end = (500, 300)
    steps = 20
    
    print(f"  Start: {start}")
    print(f"  End: {end}")
    print(f"  Steps: {steps}")
    print()
    
    # Test different velocity profiles
    profiles = [
        VelocityProfile.SMOOTH,
        VelocityProfile.SLOW_START,
        VelocityProfile.FAST_START,
        VelocityProfile.HESITANT,
        VelocityProfile.OVERSHOOT,
    ]
    
    for profile in profiles:
        print(f"  Profile: {profile}")
        curve = ds.generate_bezier_curve(start[0], start[1], end[0], end[1], steps, velocity_profile=profile)
        
        # Show first, middle, and last points
        print(f"    First: {curve[0]}")
        print(f"    Middle: {curve[len(curve)//2]}")
        print(f"    Last: {curve[-1]}")
        print()


def example_velocity_distribution():
    """Example showing velocity profile distribution."""
    print("\nExample velocity profile distribution (1000 samples):")
    print("-" * 50)
    
    counts = {}
    samples = 1000
    
    for _ in range(samples):
        profile = VelocityProfile.get_random_profile()
        counts[profile] = counts.get(profile, 0) + 1
    
    print()
    for profile, count in sorted(counts.items(), key=lambda x: -x[1]):
        percentage = (count / samples) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {profile:15} {count:4} ({percentage:5.1f}%)  {bar}")
    print()


if __name__ == "__main__":
    # Run examples when module is executed directly
    print("Delay System Examples")
    print("=" * 50)
    print()
    
    example_calculate_delays()
    example_position_jitter()
    example_bezier_curve()
    example_velocity_distribution()
    
    print("\n" + "=" * 50)
    print("Delay system examples complete!")


def example_acceleration_curve():
    """Example showing acceleration curve effect."""
    print("\nExample acceleration curve (Smootherstep):")
    print("-" * 50)
    
    test_times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    print("\nWith acceleration (factor=0.3):")
    print("  t     -> linear  -> accelerated")
    print("  " + "-" * 40)
    for t in test_times:
        accel = VelocityProfile.apply_acceleration_curve(t, 0.3)
        bar_lin = "░" * int(t * 20)
        bar_acc = "█" * int(accel * 20)
        print(f"  {t:.1f}  ->  {t:.3f}  ->  {accel:.3f}  {bar_lin}{bar_acc}")
    
    print("\nWithout acceleration (factor=0.0, linear):")
    print("  t     -> accelerated")
    print("  " + "-" * 40)
    for t in test_times:
        accel = VelocityProfile.apply_acceleration_curve(t, 0.0)
        bar = "█" * int(accel * 20)
        print(f"  {t:.1f}  ->  {accel:.3f}  {bar}")


def example_double_click_timing():
    """Example showing double-click timing variation."""
    print("\nExample double-click timing variation:")
    print("-" * 50)
    
    ds = create_default_delay_system()
    
    print("\n10 double-click samples:")
    delays = []
    for i in range(10):
        delay = ds.get_double_click_delay()
        delays.append(delay)
        bar = "█" * int((delay - 0.08) / 0.07 * 30)
        print(f"  {i+1:2}. {delay:.3f}s  {bar}")
    
    avg = sum(delays) / len(delays)
    min_d = min(delays)
    max_d = max(delays)
    
    print(f"\nStatistics:")
    print(f"  Average: {avg:.3f}s")
    print(f"  Min:     {min_d:.3f}s")
    print(f"  Max:     {max_d:.3f}s")
    print(f"  Range:   {max_d - min_d:.3f}s")
    print()
