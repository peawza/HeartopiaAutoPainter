"""
Enhanced Paint Module - Integration with Delay System and Hardware Mouse

This module provides enhanced painting functions that integrate:
- Delay system for human-like timing
- Hardware mouse support (ESP32/Arduino)
- Bezier curve movement
- Position jittering
- Micro-pauses
- Natural randomization

This is a drop-in enhancement for the existing paint.py module.
"""

from __future__ import annotations

import time
import random
import math
from typing import Callable, Optional, Tuple, List

# Import delay system
from .delays import DelaySystem, DelayConfig, VelocityProfile, create_default_delay_system

# Import hardware mouse (optional)
try:
    from .hardware_mouse import HardwareMouse, HardwareMouseConfig, HardwareMouseError
    HARDWARE_MOUSE_AVAILABLE = True
except ImportError:
    HARDWARE_MOUSE_AVAILABLE = False
    HardwareMouse = None
    HardwareMouseConfig = None
    HardwareMouseError = Exception

# Import PyAutoGUI as fallback
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None


Point = Tuple[int, int]
CLICK_DELAY_MIN_S = 0.250
CLICK_DELAY_MAX_S = 0.350
CLICK_HOLD_MIN_S = 0.030
CLICK_HOLD_MAX_S = 0.050
HARDWARE_SMOOTH_PIXELS_PER_STEP = 30
HARDWARE_SMOOTH_MAX_STEPS = 24
HARDWARE_STROKE_STEP_DELAY_S = 0.002
HARDWARE_STROKE_PIXELS_PER_STEP = 1
HARDWARE_STROKE_MAX_STEPS = 100
# Windows can coalesce the firmware's default 500us HID reports into visible
# jumps.  Pace them at 8ms during a held stroke so each canvas pixel has time
# to be observed by the game.
HARDWARE_STROKE_MIN_REPORT_INTERVAL_US = 8_000
# COM6 can amplify larger relative reports; small corrections prevent a
# feedback loop from repeatedly overshooting the same target.
HARDWARE_FEEDBACK_MAX_DELTA = 12
HARDWARE_FEEDBACK_MAX_ATTEMPTS = 160
# Fail closed for painting: do not report a target as reached until the OS
# cursor is on that exact pixel.  A device that cannot converge raises before
# the caller can click or continue a stroke.
HARDWARE_FEEDBACK_TOLERANCE_PX = 0
HARDWARE_FEEDBACK_SETTLE_S = 0.005


def _random_click_hold_s() -> float:
    return random.uniform(CLICK_HOLD_MIN_S, CLICK_HOLD_MAX_S)


def _random_click_delay_s(extra_delay: float = 0.0) -> float:
    return random.uniform(CLICK_DELAY_MIN_S, CLICK_DELAY_MAX_S) + max(0.0, float(extra_delay))


class MouseController:
    """
    Unified mouse controller supporting both PyAutoGUI and hardware mouse.
    
    This class provides a consistent interface for mouse operations,
    automatically using hardware mouse if available, falling back to
    PyAutoGUI otherwise.
    """
    
    def __init__(
        self,
        use_hardware: bool = False,
        hardware_config: Optional[HardwareMouseConfig] = None,
        delay_system: Optional[DelaySystem] = None,
        fallback_to_software: bool = True,
        hardware_click: Optional[HardwareMouse] = None,
    ):
        """
        Initialize mouse controller.
        
        Args:
            use_hardware: If True, use hardware mouse (ESP32/Arduino)
            hardware_config: Hardware mouse configuration
            delay_system: Delay system for human-like timing
        """
        self.use_hardware = use_hardware and HARDWARE_MOUSE_AVAILABLE
        self.hardware_mouse: Optional[HardwareMouse] = None
        self.hardware_click = hardware_click
        self.use_hardware_click = hardware_click is not None
        self.delay_system = delay_system or create_default_delay_system()
        
        # Initialize hardware mouse if requested
        if self.use_hardware:
            try:
                self.hardware_mouse = HardwareMouse(hardware_config)
                self.hardware_mouse.connect()
                print(f"Hardware mouse connected: {self.hardware_mouse.device_port}")
            except Exception as e:
                if not fallback_to_software:
                    self.hardware_mouse = None
                    raise
                print(f"Hardware mouse failed, falling back to PyAutoGUI: {e}")
                self.use_hardware = False
                self.hardware_mouse = None
        
        # Verify PyAutoGUI is available if not using hardware
        if not self.use_hardware and not PYAUTOGUI_AVAILABLE:
            raise RuntimeError(
                "Neither hardware mouse nor PyAutoGUI is available. "
                "Install PyAutoGUI or connect an Arduino Leonardo."
            )
        
        # Current position (for hardware mouse, which needs relative moves)
        self._current_x: Optional[int] = None
        self._current_y: Optional[int] = None
        # A relative HID report is affected by the host's pointer settings.
        # When PyAutoGUI can read the real cursor position, close that loop so
        # the tracked target cannot silently drift away from the OS cursor.
        self.hardware_position_feedback = self.use_hardware and PYAUTOGUI_AVAILABLE

    def _move_hardware_to_target(
        self,
        target_x: int,
        target_y: int,
        should_stop: Optional[Callable[[], bool]] = None,
    ) -> None:
        """Reach an absolute target using bounded relative HID corrections.

        Hardware HID movement is relative and Windows can apply scaling or
        acceleration.  Read the OS cursor after each small command rather
        than assuming a requested delta equals the observed pixel delta.
        """
        if not self.hardware_mouse:
            raise HardwareMouseError("Hardware mouse is not connected")

        for _ in range(HARDWARE_FEEDBACK_MAX_ATTEMPTS):
            if should_stop and should_stop():
                return

            current_x, current_y = pyautogui.position()
            dx = int(target_x) - int(current_x)
            dy = int(target_y) - int(current_y)
            if max(abs(dx), abs(dy)) <= HARDWARE_FEEDBACK_TOLERANCE_PX:
                self._current_x = int(current_x)
                self._current_y = int(current_y)
                return

            command_dx = max(-HARDWARE_FEEDBACK_MAX_DELTA, min(HARDWARE_FEEDBACK_MAX_DELTA, dx))
            command_dy = max(-HARDWARE_FEEDBACK_MAX_DELTA, min(HARDWARE_FEEDBACK_MAX_DELTA, dy))
            if not self.hardware_mouse.move(command_dx, command_dy):
                raise HardwareMouseError("Hardware mouse rejected feedback movement")
            time.sleep(HARDWARE_FEEDBACK_SETTLE_S)

        current_x, current_y = pyautogui.position()
        self._current_x = int(current_x)
        self._current_y = int(current_y)
        raise HardwareMouseError(
            "Hardware mouse did not reach target "
            f"({target_x}, {target_y}); cursor is at ({current_x}, {current_y})"
        )
    
    def get_current_position(self) -> Point:
        """Get current mouse position."""
        if self.use_hardware:
            # For hardware mouse, we track position ourselves
            if self._current_x is None or self._current_y is None:
                # Initialize with PyAutoGUI if available
                if PYAUTOGUI_AVAILABLE:
                    x, y = pyautogui.position()
                    self._current_x = x
                    self._current_y = y
                else:
                    self._current_x = 0
                    self._current_y = 0
            return (self._current_x, self._current_y)
        else:
            return pyautogui.position()
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """
        Move mouse to absolute position.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            duration: Movement duration (seconds), or None for instant
        """
        # Hardware movement must remain exact: the device only accepts relative
        # deltas, so even a small target jitter can accumulate into a large drift.
        if self.use_hardware:
            jx, jy = int(x), int(y)
        else:
            jx, jy = self.delay_system.apply_position_jitter(x, y)
        
        if self.use_hardware and self.hardware_mouse:
            if getattr(self, "hardware_position_feedback", False):
                self._move_hardware_to_target(jx, jy)
                return

            # Hardware mouse: calculate relative movement
            current_x, current_y = self.get_current_position()
            dx = jx - current_x
            dy = jy - current_y
            
            if duration and duration > 0:
                # Smooth movement with steps
                steps = self.delay_system.calculate_movement_steps()
                moved = self.hardware_mouse.move_smooth(dx, dy, steps)
            else:
                # Instant movement
                moved = self.hardware_mouse.move(dx, dy)

            if not moved:
                raise HardwareMouseError("Hardware mouse rejected absolute movement")
            
            # Update tracked position
            self._current_x = jx
            self._current_y = jy
        else:
            # PyAutoGUI
            if duration and duration > 0:
                pyautogui.moveTo(jx, jy, duration=duration)
            else:
                pyautogui.moveTo(jx, jy)
    
    def move_along_curve(
        self,
        start: Point,
        end: Point,
        should_stop: Optional[Callable[[], bool]] = None,
        velocity_profile: Optional[str] = None
    ) -> None:
        """
        Move mouse along a Bezier curve from start to end with velocity profile.
        
        Args:
            start: Starting position (x, y)
            end: Ending position (x, y)
            should_stop: Optional callback to check if we should stop
            velocity_profile: Optional velocity profile (random if None)
        """
        # The firmware can interpolate one relative movement with MS. Sending
        # every Python curve point as a separate M command causes serial
        # round-trips and visible stutter, especially for short canvas-cell
        # moves. Use a bounded, stable DPI-1200-style hardware profile instead.
        if self.use_hardware and self.hardware_mouse:
            if should_stop and should_stop():
                return

            if getattr(self, "hardware_position_feedback", False):
                self._move_hardware_to_target(int(end[0]), int(end[1]), should_stop)
                return

            current_x, current_y = self.get_current_position()
            target_x, target_y = int(end[0]), int(end[1])
            dx = target_x - current_x
            dy = target_y - current_y
            if dx != 0 or dy != 0:
                distance = math.hypot(dx, dy)
                smooth_steps = max(
                    1,
                    min(
                        HARDWARE_SMOOTH_MAX_STEPS,
                        int(math.ceil(distance / HARDWARE_SMOOTH_PIXELS_PER_STEP)),
                    ),
                )
                if not self.hardware_mouse.move_smooth(dx, dy, steps=smooth_steps):
                    raise HardwareMouseError("Hardware mouse rejected smooth movement")

            self._current_x = target_x
            self._current_y = target_y
            return

        # Calculate movement parameters for the software path.
        duration = self.delay_system.calculate_movement_duration()
        steps = self.delay_system.calculate_movement_steps()
        
        # Use the tracked hardware position as the source of truth. The caller's
        # start value can be stale after a previous relative movement.
        movement_start = self.get_current_position() if self.use_hardware else start

        # Hardware movement must finish at the requested absolute target.
        if self.use_hardware:
            end_x, end_y = int(end[0]), int(end[1])
        else:
            end_x, end_y = self.delay_system.apply_position_jitter(end[0], end[1])
        
        # Generate Bezier curve with velocity profile
        curve = self.delay_system.generate_bezier_curve(
            movement_start[0], movement_start[1],
            end_x, end_y,
            steps,
            velocity_profile=velocity_profile
        )
        
        # Move along curve
        delay_per_step = duration / steps
        
        for i, point in enumerate(curve):
            if should_stop and should_stop():
                break
            
            # Move to point
            if self.use_hardware and self.hardware_mouse:
                current_x, current_y = self.get_current_position()
                dx = point[0] - current_x
                dy = point[1] - current_y
                if (dx != 0 or dy != 0) and not self.hardware_mouse.move(dx, dy):
                    raise HardwareMouseError("Hardware mouse rejected curve movement")
                # Update only after the relative command succeeds so the next
                # segment is calculated from the real latest target.
                self._current_x = point[0]
                self._current_y = point[1]
            else:
                pyautogui.moveTo(point[0], point[1], duration=0)
            
            # Delay with jitter
            step_delay = self.delay_system.get_step_delay(delay_per_step)
            
            # Random micro-pause
            if self.delay_system.should_micro_pause():
                pause_duration = self.delay_system.get_micro_pause_duration()
                if not self.delay_system.interruptible_sleep(pause_duration, should_stop):
                    break
            
            # Regular step delay
            if not self.delay_system.interruptible_sleep(step_delay, should_stop):
                break

    def move_hardware_stroke_segment(self, target: Point) -> None:
        """Draw one continuous hardware stroke segment without feedback pauses.

        The ESP32 performs all of the interpolated HID reports for ``MS`` in
        one command.  Keeping the button down while it does so avoids the
        host-side move/measure/correct loop that creates visible gaps.
        """
        if not self.use_hardware or not self.hardware_mouse:
            self.move_to(*target)
            return

        if PYAUTOGUI_AVAILABLE:
            current_x, current_y = pyautogui.position()
        else:
            current_x, current_y = self.get_current_position()
        dx = int(target[0]) - int(current_x)
        dy = int(target[1]) - int(current_y)
        if dx == 0 and dy == 0:
            return

        # The firmware limits MS to 100 substeps.  Split long segments so
        # every HID substep remains roughly one pixel instead of turning a
        # 400px line into 100 visibly separated 4px jumps.  The button stays
        # held across the whole sequence.
        segments = max(1, int(math.ceil(max(abs(dx), abs(dy)) / HARDWARE_STROKE_MAX_STEPS)))
        sent_x = sent_y = 0
        for index in range(1, segments + 1):
            next_x = round(dx * index / segments)
            next_y = round(dy * index / segments)
            segment_dx = next_x - sent_x
            segment_dy = next_y - sent_y
            sent_x, sent_y = next_x, next_y
            distance = math.hypot(segment_dx, segment_dy)
            steps = max(1, int(math.ceil(distance / HARDWARE_STROKE_PIXELS_PER_STEP)))
            if not self.hardware_mouse.move_smooth(segment_dx, segment_dy, steps=steps):
                raise HardwareMouseError("Hardware mouse rejected smooth stroke movement")

        # Keep a best-effort position for callers without an OS position API.
        self._current_x = int(target[0])
        self._current_y = int(target[1])

    def finish_hardware_stroke(self, target: Point) -> None:
        """Apply any final exact correction while the stroke button is held."""
        if self.use_hardware and getattr(self, "hardware_position_feedback", False):
            self._move_hardware_to_target(int(target[0]), int(target[1]))
    
    def click(self, button: str = 'left') -> None:
        """
        Click mouse button.
        
        Args:
            button: Button to click ('left', 'right', 'middle')
        """
        pressed = False
        try:
            self.press(button)
            pressed = True
            time.sleep(_random_click_hold_s())
        finally:
            if pressed:
                self.release(button)
    
    def press(self, button: str = 'left') -> None:
        """
        Press and hold mouse button.
        
        Args:
            button: Button to press ('left', 'right', 'middle')
        """
        if self.use_hardware_click and self.hardware_click:
            if getattr(self.hardware_click, "connected", True) is False:
                raise HardwareMouseError("Hardware click device is disconnected")
            self.hardware_click.press()
        elif self.use_hardware and self.hardware_mouse:
            self.hardware_mouse.press()
        else:
            pyautogui.mouseDown(button=button)
    
    def release(self, button: str = 'left') -> None:
        """
        Release mouse button.
        
        Args:
            button: Button to release ('left', 'right', 'middle')
        """
        if self.use_hardware_click and self.hardware_click:
            self.hardware_click.release()
        elif self.use_hardware and self.hardware_mouse:
            self.hardware_mouse.release()
        else:
            pyautogui.mouseUp(button=button)
    
    def disconnect(self) -> None:
        """Disconnect hardware mouse if connected."""
        if self.hardware_mouse:
            self.hardware_mouse.disconnect()
        if self.hardware_click and self.hardware_click is not self.hardware_mouse:
            self.hardware_click.disconnect()

    def close(self) -> None:
        """Close the controller and its hardware connection."""
        self.disconnect()


def enhanced_tap(
    mouse: MouseController,
    pos: Point,
    hold_duration: Optional[float] = None,
    extra_delay: float = 0.0,
    should_stop: Optional[Callable[[], bool]] = None
) -> bool:
    """
    Enhanced tap with natural movement and timing.
    
    Args:
        pos: Target position (x, y)
        mouse: Mouse controller
        should_stop: Optional callback to check if we should stop
    
    Returns:
        True if completed, False if stopped
    """
    # Get current position
    current = mouse.get_current_position()
    
    # Move with Bezier curve
    mouse.move_along_curve(current, pos, should_stop)
    
    if should_stop and should_stop():
        return False
    
    # Random micro-pause before click
    if mouse.delay_system.should_micro_pause():
        pause = mouse.delay_system.get_micro_pause_duration()
        if not mouse.delay_system.interruptible_sleep(pause, should_stop):
            return False
    
    # Click with a bounded human-like hold. Always release after a
    # successful press, including when the hold or serial operation fails.
    pressed = False
    try:
        mouse.press()
        pressed = True
        time.sleep(max(CLICK_HOLD_MIN_S, min(CLICK_HOLD_MAX_S, float(hold_duration or _random_click_hold_s()))))
    finally:
        if pressed:
            mouse.release()
    
    # Post-click delay with randomization
    delay = _random_click_delay_s(extra_delay)
    
    return mouse.delay_system.interruptible_sleep(delay, should_stop)


def enhanced_stroke(
    points: List[Point],
    mouse: MouseController,
    substeps_per_cell: int = 6,
    should_stop: Optional[Callable[[], bool]] = None
) -> bool:
    """
    Enhanced stroke (drag) operation with natural timing.
    
    Args:
        points: List of points to visit (x, y)
        mouse: Mouse controller
        should_stop: Optional callback to check if we should stop
    
    Returns:
        True if completed, False if stopped
    """
    if not points:
        return True
    
    # Feedback is useful before pressing: begin every stroke at its exact
    # canvas pixel.  It is deliberately not used for every point while held.
    if mouse.use_hardware:
        mouse.move_to(*points[0])
    else:
        current = mouse.get_current_position()
        mouse.move_along_curve(current, points[0], should_stop)
    
    if should_stop and should_stop():
        return False
    
    pressed = False
    completed = False
    stroke_delay_active = False
    try:
        if mouse.use_hardware and mouse.hardware_mouse:
            set_min_delay = getattr(mouse.hardware_mouse, "set_min_delay", None)
            if callable(set_min_delay):
                if not set_min_delay(HARDWARE_STROKE_MIN_REPORT_INTERVAL_US):
                    raise HardwareMouseError("Hardware mouse rejected stroke pacing")
                stroke_delay_active = True

        # Press mouse button
        mouse.press()
        pressed = True

        # Small delay after press
        press_delay = _random_click_hold_s()
        if not mouse.delay_system.interruptible_sleep(press_delay, should_stop):
            return False

        # Move through points
        for i in range(1, len(points)):
            if should_stop and should_stop():
                return False

            if mouse.use_hardware:
                mouse.move_hardware_stroke_segment(points[i])
            else:
                mouse.move_along_curve(points[i-1], points[i], should_stop)

            # Hardware firmware already spaces MS substeps. Keep the delay
            # stable between canvas points instead of adding random jitter.
            if mouse.use_hardware:
                step_delay = HARDWARE_STROKE_STEP_DELAY_S
            else:
                step_delay = mouse.delay_system.calculate_delay(0.01, 0.005)
            if not mouse.delay_system.interruptible_sleep(step_delay, should_stop):
                return False

        if mouse.use_hardware:
            # Correct only once at the end, without lifting the button, so a
            # scaled HID report cannot leave a white final canvas pixel.
            mouse.finish_hardware_stroke(points[-1])

        completed = True
    finally:
        if pressed:
            mouse.release()
        if stroke_delay_active:
            try:
                mouse.hardware_mouse.set_min_delay(0)
            except Exception:
                # Releasing the held button is the safety-critical cleanup;
                # a disconnected device cannot receive the optional reset.
                pass

    if not completed:
        return False
    
    # Post-stroke delay
    release_delay = _random_click_delay_s()
    
    return mouse.delay_system.interruptible_sleep(release_delay, should_stop)


# Example usage and testing
if __name__ == "__main__":
    print("Enhanced Paint Module - Test")
    print("=" * 60)
    
    # Create delay system
    from .delays import create_default_delay_system
    ds = create_default_delay_system()
    
    print("\n1. Testing with PyAutoGUI (software mouse)...")
    mouse_soft = MouseController(use_hardware=False, delay_system=ds)
    print(f"   Current position: {mouse_soft.get_current_position()}")
    
    if HARDWARE_MOUSE_AVAILABLE:
        print("\n2. Testing with Hardware Mouse...")
        try:
            mouse_hw = MouseController(use_hardware=True, delay_system=ds)
            print(f"   Hardware mouse: {mouse_hw.hardware_mouse}")
            
            # Test movement
            print("\n   Testing natural movement...")
            current = mouse_hw.get_current_position()
            target = (current[0] + 100, current[1] + 50)
            
            print(f"   Moving from {current} to {target}...")
            mouse_hw.move_along_curve(current, target)
            
            print("   ✓ Movement complete")
            
            # Test click
            print("\n   Testing click...")
            enhanced_tap(target, mouse_hw)
            print("   ✓ Click complete")
            
            # Cleanup
            mouse_hw.disconnect()
            print("\n   ✓ Hardware mouse test complete")
            
        except Exception as e:
            print(f"\n   ⚠ Hardware mouse test failed: {e}")
    else:
        print("\n2. Hardware mouse not available (install required modules)")
    
    print("\n" + "=" * 60)
    print("Enhanced paint module ready!")
