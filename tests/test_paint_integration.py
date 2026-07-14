"""
Unit tests for paint.py integration with Enhanced Features

Tests:
- Software mode (use_enhanced_timing=True, use_hardware_mouse=False)
- Hardware mode (use_enhanced_timing=True, use_hardware_mouse=True)
- Backward compatibility (use_enhanced_timing=False)
- Fallback mechanisms
"""

import unittest
from unittest.mock import MagicMock, patch, ANY
from dataclasses import dataclass
from typing import Optional

# Mock the imports before importing paint module
import sys
sys.path.insert(0, 'src')

# Import paint module components
from heartopia_painter.paint import (
    PainterOptions,
    _create_mouse_controller,
    _tap,
    _stroke,
    _rapid_click_stroke,
)


class TestEnhancedIntegration(unittest.TestCase):
    """Test Enhanced Features integration with paint.py"""

    def setUp(self):
        """Set up test fixtures"""
        self.default_opts = PainterOptions(
            use_enhanced_timing=False,
            use_hardware_mouse=False,
            hardware_mouse_port=None,
            delay_profile="default",
            enable_position_jitter=True,
            enable_micro_pauses=True,
        )

    def test_create_mouse_controller_disabled(self):
        """Test _create_mouse_controller when enhanced timing is disabled"""
        opts = self.default_opts
        opts.use_enhanced_timing = False
        
        result = _create_mouse_controller(opts)
        
        self.assertIsNone(result, "Should return None when enhanced timing disabled")

    @patch('heartopia_painter.paint.DelaySystem')
    @patch('heartopia_painter.paint.MouseController')
    def test_create_mouse_controller_software_mode(self, mock_mouse_ctrl, mock_delay_sys):
        """Test _create_mouse_controller in software mode"""
        opts = self.default_opts
        opts.use_enhanced_timing = True
        opts.use_hardware_mouse = False
        
        # Mock DelaySystem creation
        mock_delay_instance = MagicMock()
        mock_delay_sys.return_value = mock_delay_instance
        
        # Mock MouseController creation
        mock_controller_instance = MagicMock()
        mock_mouse_ctrl.return_value = mock_controller_instance
        
        result = _create_mouse_controller(opts)
        
        # Should create delay system
        mock_delay_sys.assert_called_once()
        
        # Should create MouseController with use_hardware=False
        mock_mouse_ctrl.assert_called_once_with(
            use_hardware=False,
            hardware_port=None,
            delay_system=mock_delay_instance
        )
        
        self.assertEqual(result, mock_controller_instance)

    @patch('heartopia_painter.paint.DelaySystem')
    @patch('heartopia_painter.paint.MouseController')
    def test_create_mouse_controller_hardware_mode(self, mock_mouse_ctrl, mock_delay_sys):
        """Test _create_mouse_controller in hardware mode"""
        opts = self.default_opts
        opts.use_enhanced_timing = True
        opts.use_hardware_mouse = True
        opts.hardware_mouse_port = "COM3"
        
        # Mock DelaySystem creation
        mock_delay_instance = MagicMock()
        mock_delay_sys.return_value = mock_delay_instance
        
        # Mock MouseController creation (hardware mode)
        mock_controller_instance = MagicMock()
        mock_mouse_ctrl.return_value = mock_controller_instance
        
        result = _create_mouse_controller(opts)
        
        # Should create MouseController with use_hardware=True
        mock_mouse_ctrl.assert_called_once_with(
            use_hardware=True,
            hardware_port="COM3",
            delay_system=mock_delay_instance
        )
        
        self.assertEqual(result, mock_controller_instance)

    @patch('heartopia_painter.paint.DelaySystem')
    @patch('heartopia_painter.paint.MouseController')
    def test_create_mouse_controller_fallback_on_error(self, mock_mouse_ctrl, mock_delay_sys):
        """Test _create_mouse_controller falls back to None on import error"""
        opts = self.default_opts
        opts.use_enhanced_timing = True
        
        # Simulate import error
        mock_delay_sys.side_effect = ImportError("Module not found")
        
        result = _create_mouse_controller(opts)
        
        # Should return None and not crash
        self.assertIsNone(result, "Should return None on import error")

    @patch('heartopia_painter.paint.pyautogui')
    def test_tap_without_mouse_controller(self, mock_pyautogui):
        """Test _tap() without mouse controller (backward compatible)"""
        x, y = 100, 200
        
        _tap(x, y, mouse_controller=None)
        
        # Should use PyAutoGUI
        mock_pyautogui.click.assert_called_once_with(x, y)

    @patch('heartopia_painter.paint.pyautogui')
    def test_tap_with_mouse_controller(self, mock_pyautogui):
        """Test _tap() with mouse controller (enhanced mode)"""
        x, y = 100, 200
        
        # Mock MouseController
        mock_controller = MagicMock()
        mock_controller.enhanced_tap = MagicMock()
        
        _tap(x, y, mouse_controller=mock_controller)
        
        # Should use enhanced_tap
        mock_controller.enhanced_tap.assert_called_once_with(x, y)
        
        # Should NOT use PyAutoGUI
        mock_pyautogui.click.assert_not_called()

    @patch('heartopia_painter.paint.pyautogui')
    def test_tap_with_mouse_controller_fallback(self, mock_pyautogui):
        """Test _tap() fallback when enhanced_tap fails"""
        x, y = 100, 200
        
        # Mock MouseController that fails
        mock_controller = MagicMock()
        mock_controller.enhanced_tap.side_effect = Exception("Hardware failure")
        
        _tap(x, y, mouse_controller=mock_controller)
        
        # Should try enhanced_tap
        mock_controller.enhanced_tap.assert_called_once_with(x, y)
        
        # Should fallback to PyAutoGUI
        mock_pyautogui.click.assert_called_once_with(x, y)

    @patch('heartopia_painter.paint.pynput')
    @patch('heartopia_painter.paint.pyautogui')
    def test_stroke_without_mouse_controller(self, mock_pyautogui, mock_pynput):
        """Test _stroke() without mouse controller (backward compatible)"""
        start = (100, 100)
        end = (200, 200)
        
        # Mock pynput mouse
        mock_mouse = MagicMock()
        mock_pynput.mouse.Controller.return_value = mock_mouse
        mock_pynput.mouse.Button.left = "LEFT"
        
        _stroke(start, end, mouse_controller=None)
        
        # Should try pynput first
        mock_mouse.press.assert_called()
        mock_mouse.release.assert_called()

    @patch('heartopia_painter.paint.pyautogui')
    def test_stroke_with_mouse_controller(self, mock_pyautogui):
        """Test _stroke() with mouse controller (enhanced mode)"""
        start = (100, 100)
        end = (200, 200)
        
        # Mock MouseController
        mock_controller = MagicMock()
        mock_controller.enhanced_stroke = MagicMock()
        
        _stroke(start, end, mouse_controller=mock_controller)
        
        # Should use enhanced_stroke
        mock_controller.enhanced_stroke.assert_called_once_with(start, end)

    @patch('heartopia_painter.paint._tap')
    def test_rapid_click_stroke_without_mouse_controller(self, mock_tap):
        """Test _rapid_click_stroke() without mouse controller"""
        points = [(100, 100), (150, 150), (200, 200)]
        
        _rapid_click_stroke(points, mouse_controller=None)
        
        # Should call _tap for each point
        self.assertEqual(mock_tap.call_count, len(points))
        
        # Each call should have mouse_controller=None
        for i, point in enumerate(points):
            mock_tap.assert_any_call(point[0], point[1], mouse_controller=None)

    @patch('heartopia_painter.paint._tap')
    def test_rapid_click_stroke_with_mouse_controller(self, mock_tap):
        """Test _rapid_click_stroke() with mouse controller"""
        points = [(100, 100), (150, 150), (200, 200)]
        
        # Mock MouseController
        mock_controller = MagicMock()
        
        _rapid_click_stroke(points, mouse_controller=mock_controller)
        
        # Should call _tap for each point
        self.assertEqual(mock_tap.call_count, len(points))
        
        # Each call should pass mouse_controller
        for i, point in enumerate(points):
            mock_tap.assert_any_call(point[0], point[1], mouse_controller=mock_controller)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing code"""

    def test_painter_options_default_values(self):
        """Test PainterOptions has correct default values"""
        opts = PainterOptions()
        
        # Enhanced features should be OFF by default
        self.assertFalse(opts.use_enhanced_timing, "Enhanced timing should be disabled by default")
        self.assertFalse(opts.use_hardware_mouse, "Hardware mouse should be disabled by default")
        self.assertIsNone(opts.hardware_mouse_port, "Hardware port should be None by default")
        self.assertEqual(opts.delay_profile, "default", "Delay profile should be 'default'")
        self.assertTrue(opts.enable_position_jitter, "Position jitter should be enabled by default")
        self.assertTrue(opts.enable_micro_pauses, "Micro pauses should be enabled by default")

    def test_painter_options_all_fields_exist(self):
        """Test PainterOptions has all required fields"""
        opts = PainterOptions()
        
        # Check all enhanced fields exist
        self.assertTrue(hasattr(opts, 'use_enhanced_timing'))
        self.assertTrue(hasattr(opts, 'use_hardware_mouse'))
        self.assertTrue(hasattr(opts, 'hardware_mouse_port'))
        self.assertTrue(hasattr(opts, 'delay_profile'))
        self.assertTrue(hasattr(opts, 'enable_position_jitter'))
        self.assertTrue(hasattr(opts, 'enable_micro_pauses'))


class TestDelayProfiles(unittest.TestCase):
    """Test different delay profiles"""

    @patch('heartopia_painter.paint.DelaySystem')
    @patch('heartopia_painter.paint.MouseController')
    def test_fast_profile(self, mock_mouse_ctrl, mock_delay_sys):
        """Test fast delay profile"""
        opts = PainterOptions(
            use_enhanced_timing=True,
            delay_profile="fast"
        )
        
        mock_delay_instance = MagicMock()
        mock_delay_sys.return_value = mock_delay_instance
        
        result = _create_mouse_controller(opts)
        
        self.assertIsNotNone(result, "Should create controller with fast profile")

    @patch('heartopia_painter.paint.DelaySystem')
    @patch('heartopia_painter.paint.MouseController')
    def test_careful_profile(self, mock_mouse_ctrl, mock_delay_sys):
        """Test careful delay profile"""
        opts = PainterOptions(
            use_enhanced_timing=True,
            delay_profile="careful"
        )
        
        mock_delay_instance = MagicMock()
        mock_delay_sys.return_value = mock_delay_instance
        
        result = _create_mouse_controller(opts)
        
        self.assertIsNotNone(result, "Should create controller with careful profile")


def run_tests():
    """Run all tests and print results"""
    print("\n" + "="*70)
    print("🧪 Running Enhanced Features Integration Tests")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestDelayProfiles))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
