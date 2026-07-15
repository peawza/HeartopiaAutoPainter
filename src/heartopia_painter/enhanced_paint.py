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
        self.delay_system = delay_system or create_default_delay_system()
        
        # Initialize hardware mouse if requested
        if self.use_hardware:
            try:
                self.hardware_mouse = HardwareMouse(hardware_config)
                self.hardware_mouse.connect()
                print(f"✓ Hardware mouse connected: {self.hardware_mouse.device_port}")
            except Exception as e:
                if not fallback_to_software:
                    self.hardware_mouse = None
                    raise
                print(f"⚠ Hardware mouse failed, falling back to PyAutoGUI: {e}")
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
        # Apply position jitter
        jx, jy = self.delay_system.apply_position_jitter(x, y)
        
        if self.use_hardware and self.hardware_mouse:
            # Hardware mouse: calculate relative movement
            current_x, current_y = self.get_current_position()
            dx = jx - current_x
            dy = jy - current_y
            
            if duration and duration > 0:
                # Smooth movement with steps
                steps = self.delay_system.calculate_movement_steps()
                self.hardware_mouse.move_smooth(dx, dy, steps)
            else:
                # Instant movement
                self.hardware_mouse.move(dx, dy)
            
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
        # Calculate movement parameters
        duration = self.delay_system.calculate_movement_duration()
        steps = self.delay_system.calculate_movement_steps()
        
        # Apply jitter to end position
        end_x, end_y = self.delay_system.apply_position_jitter(end[0], end[1])
        
        # Generate Bezier curve with velocity profile
        curve = self.delay_system.generate_bezier_curve(
            start[0], start[1],
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
                self.hardware_mouse.move(dx, dy)
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
    
    def click(self, button: str = 'left') -> None:
        """
        Click mouse button.
        
        Args:
            button: Button to click ('left', 'right', 'middle')
        """
        self.press(button)
        time.sleep(_random_click_hold_s())
        self.release(button)
    
    def press(self, button: str = 'left') -> None:
        """
        Press and hold mouse button.
        
        Args:
            button: Button to press ('left', 'right', 'middle')
        """
        if self.use_hardware and self.hardware_mouse:
            self.hardware_mouse.press()
        else:
            pyautogui.mouseDown(button=button)
    
    def release(self, button: str = 'left') -> None:
        """
        Release mouse button.
        
        Args:
            button: Button to release ('left', 'right', 'middle')
        """
        if self.use_hardware and self.hardware_mouse:
            self.hardware_mouse.release()
        else:
            pyautogui.mouseUp(button=button)
    
    def disconnect(self) -> None:
        """Disconnect hardware mouse if connected."""
        if self.hardware_mouse:
            self.hardware_mouse.disconnect()

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
    
    # Click with a bounded human-like hold.
    mouse.press()
    time.sleep(max(CLICK_HOLD_MIN_S, min(CLICK_HOLD_MAX_S, float(hold_duration or _random_click_hold_s()))))
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
    
    # Move to first point
    current = mouse.get_current_position()
    mouse.move_along_curve(current, points[0], should_stop)
    
    if should_stop and should_stop():
        return False
    
    # Press mouse button
    mouse.press()
    
    # Small delay after press
    press_delay = _random_click_hold_s()
    if not mouse.delay_system.interruptible_sleep(press_delay, should_stop):
        mouse.release()
        return False
    
    # Move through points
    for i in range(1, len(points)):
        if should_stop and should_stop():
            mouse.release()
            return False
        
        mouse.move_along_curve(points[i-1], points[i], should_stop)
        
        # Small delay between points
        step_delay = mouse.delay_system.calculate_delay(0.01, 0.005)
        if not mouse.delay_system.interruptible_sleep(step_delay, should_stop):
            mouse.release()
            return False
    
    # Release mouse button
    mouse.release()
    
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
