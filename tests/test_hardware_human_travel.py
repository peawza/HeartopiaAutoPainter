import unittest
from unittest.mock import patch

from heartopia_painter.enhanced_paint import (
    HARDWARE_TRAVEL_MAX_DURATION_S,
    HARDWARE_TRAVEL_MIN_DURATION_S,
    MouseController,
    enhanced_stroke,
    enhanced_tap,
)


class RecordingDelay:
    def __init__(self):
        self.sleeps = []

    def interruptible_sleep(self, duration, should_stop=None):
        self.sleeps.append(float(duration))
        return not (should_stop and should_stop())

    def should_micro_pause(self):
        return False


class RecordingHardware:
    def __init__(self, fail_smooth=False):
        self.commands = []
        self.x = 0
        self.y = 0
        self.button_down = False
        self.painted = []
        self.fail_smooth = fail_smooth

    def move(self, dx, dy):
        self.commands.append(("MOVE", int(dx), int(dy), self.button_down))
        self.x += int(dx)
        self.y += int(dy)
        return True

    def move_smooth(self, dx, dy, steps):
        self.commands.append(("MOVE_SMOOTH", int(dx), int(dy), int(steps), self.button_down))
        if self.fail_smooth:
            return False
        start_x, start_y = self.x, self.y
        for index in range(1, int(steps) + 1):
            self.x = start_x + round(int(dx) * index / int(steps))
            self.y = start_y + round(int(dy) * index / int(steps))
            if self.button_down and (self.x, self.y) not in self.painted:
                self.painted.append((self.x, self.y))
        return True

    def press(self):
        self.commands.append(("DOWN",))
        self.button_down = True
        if (self.x, self.y) not in self.painted:
            self.painted.append((self.x, self.y))
        return True

    def release(self):
        self.commands.append(("UP",))
        self.button_down = False
        return True

    def set_min_delay(self, microseconds):
        self.commands.append(("SET_DELAY", int(microseconds)))
        return True


def make_controller(hardware=None):
    controller = MouseController.__new__(MouseController)
    controller.use_hardware = True
    controller.hardware_mouse = hardware or RecordingHardware()
    controller.hardware_click = None
    controller.use_hardware_click = False
    controller.delay_system = RecordingDelay()
    controller._current_x = 0
    controller._current_y = 0
    controller._button_pressed = False
    controller.hardware_position_feedback = False
    return controller


class HardwareHumanTravelTests(unittest.TestCase):
    def test_travel_is_curved_released_and_paced_at_600_dpi_profile(self):
        controller = make_controller()
        with patch("heartopia_painter.enhanced_paint.random.uniform", return_value=0.12), patch(
            "heartopia_painter.enhanced_paint.random.random", return_value=1.0
        ):
            controller.move_hardware_travel_curve((0, 0), (600, 0))

        moves = [command for command in controller.hardware_mouse.commands if command[0] == "MOVE"]
        self.assertGreater(len(moves), 10)
        self.assertEqual(controller.hardware_mouse.commands[0], ("UP",))
        self.assertTrue(all(command[3] is False for command in moves))

        y = 0
        visited_y = []
        for _, _, dy, _ in moves:
            y += dy
            visited_y.append(y)
        self.assertTrue(any(value != 0 for value in visited_y[:-1]))
        self.assertEqual((controller._current_x, controller._current_y), (600, 0))

        travel_duration = sum(controller.delay_system.sleeps)
        self.assertGreaterEqual(travel_duration, HARDWARE_TRAVEL_MIN_DURATION_S)
        self.assertLessEqual(travel_duration, HARDWARE_TRAVEL_MAX_DURATION_S)
        self.assertAlmostEqual(travel_duration, 1.0, places=6)

    def test_palette_tap_travels_with_button_up_before_click(self):
        controller = make_controller()
        with patch("heartopia_painter.enhanced_paint.random.uniform", return_value=0.12), patch(
            "heartopia_painter.enhanced_paint.random.random", return_value=1.0
        ), patch("heartopia_painter.enhanced_paint.time.sleep"):
            self.assertTrue(enhanced_tap(controller, (300, 200), hold_duration=0.04))

        names = [command[0] for command in controller.hardware_mouse.commands]
        self.assertEqual(names[0], "UP")
        self.assertIn("MOVE", names)
        self.assertLess(names.index("MOVE"), names.index("DOWN"))
        self.assertEqual(names[-1], "UP")
        self.assertTrue(
            all(command[3] is False for command in controller.hardware_mouse.commands if command[0] == "MOVE")
        )

    def test_stroke_travels_then_paints_every_pixel(self):
        controller = make_controller()
        points = [(100, 100), (104, 100), (108, 100), (112, 100)]
        with patch("heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", False), patch(
            "heartopia_painter.enhanced_paint.random.uniform", return_value=0.12
        ), patch("heartopia_painter.enhanced_paint.random.random", return_value=1.0):
            self.assertTrue(enhanced_stroke(points, controller))

        names = [command[0] for command in controller.hardware_mouse.commands]
        self.assertLess(names.index("UP"), names.index("DOWN"))
        self.assertEqual(names[-2:], ["UP", "SET_DELAY"])
        expected = [(x, 100) for x in range(100, 113)]
        self.assertEqual(controller.hardware_mouse.painted, expected)

    def test_stroke_error_still_releases_button(self):
        controller = make_controller(RecordingHardware(fail_smooth=True))
        with patch("heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", False):
            with self.assertRaises(Exception):
                enhanced_stroke([(0, 0), (4, 0)], controller)

        self.assertFalse(controller.hardware_mouse.button_down)
        self.assertIn(("UP",), controller.hardware_mouse.commands)


if __name__ == "__main__":
    unittest.main()
