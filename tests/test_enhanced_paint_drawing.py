"""
Comprehensive test suite for enhanced_paint.py drawing functions.

Tests cover:
- MouseController initialization (software and hardware)
- Position tracking and movement operations
- Click operations (press, release, click)
- Hardware position feedback loop
- enhanced_tap function
- enhanced_stroke function
- Error handling and cleanup
"""

from __future__ import annotations

import math
import time
from unittest.mock import MagicMock, Mock, patch, call

import pytest

from src.heartopia_painter.enhanced_paint import (
    HardwareMouseError,
    MouseController,
    enhanced_tap,
    enhanced_stroke,
    HARDWARE_FEEDBACK_MAX_ATTEMPTS,
    HARDWARE_FEEDBACK_TOLERANCE_PX,
    HARDWARE_FEEDBACK_MAX_DELTA,
)


# ============================================================================
# Fixtures and Helpers
# ============================================================================

@pytest.fixture
def mock_delay_system():
    """Create a mock delay system with default behavior."""
    delay_system = MagicMock()
    delay_system.apply_position_jitter.side_effect = lambda x, y: (x, y)
    delay_system.calculate_movement_duration.return_value = 0.1
    delay_system.calculate_movement_steps.return_value = 10
    delay_system.generate_bezier_curve.side_effect = (
        lambda sx, sy, ex, ey, steps, velocity_profile=None: [(sx, sy), (ex, ey)]
    )
    delay_system.get_step_delay.return_value = 0.01
    delay_system.should_micro_pause.return_value = False
    delay_system.interruptible_sleep.return_value = True
    delay_system.calculate_delay.return_value = 0.05
    return delay_system


@pytest.fixture
def mock_hardware_mouse():
    """Create a mock hardware mouse device."""
    hw_mouse = MagicMock()
    hw_mouse.connect.return_value = True
    hw_mouse.move.return_value = True
    hw_mouse.move_smooth.return_value = True
    hw_mouse.press.return_value = True
    hw_mouse.release.return_value = True
    hw_mouse.click.return_value = True
    hw_mouse.device_port = "COM3"
    hw_mouse.connected = True
    return hw_mouse


class FakeHardwareMouse:
    """Fake hardware mouse for testing with command recording."""
    
    def __init__(self, fail_on_move=None):
        self.commands = []
        self.moves = []
        self.smooth_moves = []
        self.connected = True
        self.device_port = "FAKE_PORT"
        self.fail_on_move = fail_on_move
    
    def connect(self):
        self.commands.append("CONNECT")
        return True
    
    def disconnect(self):
        self.commands.append("DISCONNECT")
    
    def move(self, dx, dy):
        self.moves.append((dx, dy))
        self.commands.append(f"M,{dx},{dy}")
        if self.fail_on_move is not None and len(self.moves) == self.fail_on_move:
            raise HardwareMouseError("movement failed")
        return True
    
    def move_smooth(self, dx, dy, steps):
        self.smooth_moves.append((dx, dy, steps))
        self.commands.append(f"MS,{dx},{dy},{steps}")
        if self.fail_on_move is not None and len(self.moves) + len(self.smooth_moves) == self.fail_on_move:
            raise HardwareMouseError("smooth movement failed")
        return True
    
    def press(self):
        self.commands.append("D")
        return True
    
    def release(self):
        self.commands.append("U")
        return True
    
    def click(self):
        self.commands.append("C")
        return True


# ============================================================================
# MouseController Tests - Initialization
# ============================================================================

class TestMouseControllerInitialization:
    """Tests for MouseController initialization."""
    
    def test_software_mouse_initialization(self, mock_delay_system):
        """Test PyAutoGUI (software) mouse initialization."""
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            controller = MouseController(
                use_hardware=False,
                delay_system=mock_delay_system,
                fallback_to_software=False
            )
            
            assert controller.use_hardware is False
            assert controller.hardware_mouse is None
            assert controller.delay_system == mock_delay_system
    
    def test_hardware_mouse_initialization_success(self, mock_delay_system, mock_hardware_mouse):
        """Test hardware mouse initialization when connection succeeds."""
        with patch("src.heartopia_painter.enhanced_paint.HARDWARE_MOUSE_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.HardwareMouse", return_value=mock_hardware_mouse):
                controller = MouseController(
                    use_hardware=True,
                    delay_system=mock_delay_system,
                    fallback_to_software=False
                )
                
                assert controller.use_hardware is True
                assert controller.hardware_mouse == mock_hardware_mouse
                mock_hardware_mouse.connect.assert_called_once()
    
    def test_hardware_mouse_initialization_failure_with_fallback(self, mock_delay_system):
        """Test hardware mouse initialization failure with software fallback."""
        mock_hw = MagicMock()
        mock_hw.connect.side_effect = Exception("Connection failed")
        
        with patch("src.heartopia_painter.enhanced_paint.HARDWARE_MOUSE_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
                with patch("src.heartopia_painter.enhanced_paint.HardwareMouse", return_value=mock_hw):
                    controller = MouseController(
                        use_hardware=True,
                        delay_system=mock_delay_system,
                        fallback_to_software=True
                    )
                    
                    # Should fall back to software
                    assert controller.use_hardware is False
                    assert controller.hardware_mouse is None
    
    def test_hardware_mouse_initialization_failure_no_fallback(self, mock_delay_system):
        """Test hardware mouse initialization failure without fallback."""
        mock_hw = MagicMock()
        mock_hw.connect.side_effect = Exception("Connection failed")
        
        with patch("src.heartopia_painter.enhanced_paint.HARDWARE_MOUSE_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.HardwareMouse", return_value=mock_hw):
                with pytest.raises(Exception, match="Connection failed"):
                    MouseController(
                        use_hardware=True,
                        delay_system=mock_delay_system,
                        fallback_to_software=False
                    )
    
    def test_no_pyautogui_no_hardware_raises_error(self, mock_delay_system):
        """Test that initialization fails when neither hardware nor PyAutoGUI is available."""
        with patch("src.heartopia_painter.enhanced_paint.HARDWARE_MOUSE_AVAILABLE", False):
            with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", False):
                with pytest.raises(RuntimeError, match="Neither hardware mouse nor PyAutoGUI"):
                    MouseController(
                        use_hardware=False,
                        delay_system=mock_delay_system
                    )


# ============================================================================
# MouseController Tests - Position Tracking
# ============================================================================

class TestMouseControllerPosition:
    """Tests for position tracking."""
    
    def test_get_position_software_mouse(self, mock_delay_system):
        """Test get_current_position with software mouse."""
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", return_value=(100, 200)):
                controller = MouseController(
                    use_hardware=False,
                    delay_system=mock_delay_system,
                    fallback_to_software=False
                )
                
                pos = controller.get_current_position()
                assert pos == (100, 200)
    
    def test_get_position_hardware_mouse_tracks_position(self, mock_delay_system):
        """Test get_current_position with hardware mouse tracks internal position."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 50
        controller._current_y = 75
        controller.hardware_position_feedback = False
        
        pos = controller.get_current_position()
        assert pos == (50, 75)
    
    def test_get_position_hardware_initializes_with_pyautogui(self, mock_delay_system):
        """Test get_current_position initializes from PyAutoGUI if available."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = None
        controller._current_y = None
        controller.hardware_position_feedback = False
        
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", return_value=(150, 250)):
                pos = controller.get_current_position()
                assert pos == (150, 250)
                assert controller._current_x == 150
                assert controller._current_y == 250


# ============================================================================
# MouseController Tests - Movement Operations
# ============================================================================

class TestMouseControllerMovement:
    """Tests for mouse movement operations."""
    
    def test_move_to_software_mouse(self, mock_delay_system):
        """Test move_to with software mouse."""
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.moveTo") as mock_move:
                controller = MouseController(
                    use_hardware=False,
                    delay_system=mock_delay_system,
                    fallback_to_software=False
                )
                
                controller.move_to(100, 200, duration=0.5)
                mock_move.assert_called_once_with(100, 200, duration=0.5)
    
    def test_move_to_hardware_mouse_calculates_relative(self, mock_delay_system):
        """Test move_to with hardware mouse calculates relative movement."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 50
        controller._current_y = 75
        controller.hardware_position_feedback = False
        
        controller.move_to(150, 175)
        
        # Should move by delta (100, 100) from current position
        assert fake_hw.moves == [(100, 100)]
        assert controller._current_x == 150
        assert controller._current_y == 175
    
    def test_move_to_hardware_with_duration_uses_smooth(self, mock_delay_system):
        """Test move_to with duration uses smooth movement."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 0
        controller._current_y = 0
        controller.hardware_position_feedback = False
        
        controller.move_to(100, 50, duration=0.5)
        
        # Should use move_smooth
        assert len(fake_hw.smooth_moves) == 1
        assert fake_hw.smooth_moves[0][0:2] == (100, 50)
    
    def test_move_along_curve_software(self, mock_delay_system):
        """Test move_along_curve with software mouse."""
        mock_delay_system.generate_bezier_curve.return_value = [
            (0, 0), (25, 25), (50, 50), (75, 75), (100, 100)
        ]
        
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.moveTo") as mock_move:
                with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", return_value=(0, 0)):
                    controller = MouseController(
                        use_hardware=False,
                        delay_system=mock_delay_system,
                        fallback_to_software=False
                    )
                    
                    controller.move_along_curve((0, 0), (100, 100))
                    
                    # Should move to each point in the curve
                    assert mock_move.call_count == 5
    
    def test_move_along_curve_hardware(self, mock_delay_system):
        """Test move_along_curve with hardware mouse."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 0
        controller._current_y = 0
        controller.hardware_position_feedback = False
        
        controller.move_along_curve((0, 0), (100, 100))
        
        # Should use move_smooth for hardware
        assert len(fake_hw.smooth_moves) >= 1
    
    def test_move_hardware_stroke_segment(self, mock_delay_system):
        """Test move_hardware_stroke_segment with short distance."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 0
        controller._current_y = 0
        controller.hardware_position_feedback = False
        
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", return_value=(0, 0)):
                controller.move_hardware_stroke_segment((50, 50))
        
        # Should send smooth move commands
        assert len(fake_hw.smooth_moves) >= 1
    
    def test_move_hardware_stroke_segment_long_distance_splits(self, mock_delay_system):
        """Test move_hardware_stroke_segment splits long segments."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 0
        controller._current_y = 0
        controller.hardware_position_feedback = False
        
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", return_value=(0, 0)):
                # Move >100 pixels should split into segments
                controller.move_hardware_stroke_segment((250, 0))
        
        # Should split into multiple segments
        assert len(fake_hw.smooth_moves) > 1


# ============================================================================
# MouseController Tests - Click Operations
# ============================================================================

class TestMouseControllerClicks:
    """Tests for mouse click operations."""
    
    def test_press_software_mouse(self, mock_delay_system):
        """Test press with software mouse."""
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.mouseDown") as mock_down:
                controller = MouseController(
                    use_hardware=False,
                    delay_system=mock_delay_system,
                    fallback_to_software=False
                )
                
                controller.press('left')
                mock_down.assert_called_once_with(button='left')
    
    def test_release_software_mouse(self, mock_delay_system):
        """Test release with software mouse."""
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.mouseUp") as mock_up:
                controller = MouseController(
                    use_hardware=False,
                    delay_system=mock_delay_system,
                    fallback_to_software=False
                )
                
                controller.release('left')
                mock_up.assert_called_once_with(button='left')
    
    def test_click_software_mouse(self, mock_delay_system):
        """Test click with software mouse."""
        with patch("src.heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", True):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.mouseDown") as mock_down:
                with patch("src.heartopia_painter.enhanced_paint.pyautogui.mouseUp") as mock_up:
                    with patch("src.heartopia_painter.enhanced_paint.time.sleep"):
                        controller = MouseController(
                            use_hardware=False,
                            delay_system=mock_delay_system,
                            fallback_to_software=False
                        )
                        
                        controller.click('left')
                        mock_down.assert_called_once_with(button='left')
                        mock_up.assert_called_once_with(button='left')
    
    def test_press_hardware_mouse(self, mock_delay_system):
        """Test press with hardware mouse."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        
        controller.press()
        assert "D" in fake_hw.commands
    
    def test_release_hardware_mouse(self, mock_delay_system):
        """Test release with hardware mouse."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        
        controller.release()
        assert "U" in fake_hw.commands
    
    def test_click_releases_on_error(self, mock_delay_system):
        """Test click releases button even on error."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        
        with patch("src.heartopia_painter.enhanced_paint.time.sleep", side_effect=RuntimeError("test error")):
            with pytest.raises(RuntimeError, match="test error"):
                controller.click()
        
        # Should still release
        assert "D" in fake_hw.commands
        assert "U" in fake_hw.commands


# ============================================================================
# MouseController Tests - Hardware Feedback Loop
# ============================================================================

class TestHardwareFeedbackLoop:
    """Tests for hardware position feedback loop."""
    
    def test_feedback_loop_converges_to_target(self, mock_delay_system):
        """Test feedback loop successfully reaches target."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 0
        controller._current_y = 0
        controller.hardware_position_feedback = True
        
        # Simulate position converging to target
        positions = [(0, 0), (50, 50), (90, 90), (100, 100)]
        
        with patch("src.heartopia_painter.enhanced_paint.time.sleep"):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", side_effect=positions):
                controller._move_hardware_to_target(100, 100)
        
        # Should reach target
        assert controller._current_x == 100
        assert controller._current_y == 100
        assert len(fake_hw.moves) > 0
    
    def test_feedback_loop_respects_max_delta(self, mock_delay_system):
        """Test feedback loop respects HARDWARE_FEEDBACK_MAX_DELTA."""
        fake_hw = FakeHardwareMouse()
        controller = MouseController.__new__(MouseController)
        controller.use_hardware = True
        controller.hardware_mouse = fake_hw
        controller.hardware_click = None
        controller.use_hardware_click = False
        controller.delay_system = mock_delay_system
        controller._current_x = 0
        controller._current_y = 0
        controller.hardware_position_feedback = True
        
        # Start far from target
        positions = [(0, 0), (12, 12), (24, 24), (36, 36), (48, 48), (60, 60)]
        
        with patch("src.heartopia_painter.enhanced_paint.time.sleep"):
            with patch("src.heartopia_painter.enhanced_paint.pyautogui.position", side_effect=positions):
