import unittest
from unittest.mock import patch

from heartopia_painter.paint import (
    HARDWARE_STROKE_CHUNK_PAUSE_MAX_S,
    HARDWARE_STROKE_CHUNK_PAUSE_MIN_S,
    PainterOptions,
    _rapid_click_stroke,
    _split_hardware_stroke_chunks,
)
from tests.test_hardware_human_travel import make_controller


class SequenceRandInt:
    def __init__(self, values):
        self.values = iter(values)

    def __call__(self, low, high):
        self.test_bounds = (low, high)
        return next(self.values)


class HardwareStrokeChunkTests(unittest.TestCase):
    def test_split_ten_points_into_deterministic_3_2_4_1(self):
        points = [(index, 0) for index in range(10)]
        chooser = SequenceRandInt([3, 2, 4, 5])
        chunks = _split_hardware_stroke_chunks(points, randint=chooser)

        self.assertEqual([len(chunk) for chunk in chunks], [3, 2, 4, 1])
        self.assertEqual([point for chunk in chunks for point in chunk], points)
        self.assertEqual(chooser.test_bounds, (2, 5))

    def test_hardware_run_reports_progress_after_each_completed_chunk(self):
        points = [(index, 0) for index in range(10)]
        chunks = [points[:3], points[3:5], points[5:9], points[9:]]
        progress = []
        controller = make_controller()

        with patch("heartopia_painter.paint._split_hardware_stroke_chunks", return_value=chunks), patch(
            "heartopia_painter.enhanced_paint.enhanced_stroke", return_value=True
        ) as stroke, patch("heartopia_painter.paint.random.uniform", side_effect=[0.04, 0.08, 0.12]), patch(
            "heartopia_painter.paint._interruptible_sleep", return_value=True
        ) as pause:
            _rapid_click_stroke(
                points,
                PainterOptions(),
                on_point=progress.append,
                mouse_controller=controller,
            )

        self.assertEqual([call.args[0] for call in stroke.call_args_list], chunks)
        self.assertTrue(all(call.kwargs["post_delay"] is False for call in stroke.call_args_list))
        self.assertEqual(progress, list(range(10)))
        self.assertEqual([call.args[0] for call in pause.call_args_list], [0.04, 0.08, 0.12])

    def test_chunk_pauses_stay_in_human_range(self):
        self.assertEqual(HARDWARE_STROKE_CHUNK_PAUSE_MIN_S, 0.040)
        self.assertEqual(HARDWARE_STROKE_CHUNK_PAUSE_MAX_S, 0.120)

    def test_stop_during_pause_prevents_next_chunk(self):
        points = [(index, 0) for index in range(6)]
        chunks = [points[:3], points[3:]]
        controller = make_controller()

        with patch("heartopia_painter.paint._split_hardware_stroke_chunks", return_value=chunks), patch(
            "heartopia_painter.enhanced_paint.enhanced_stroke", return_value=True
        ) as stroke, patch("heartopia_painter.paint._interruptible_sleep", return_value=False):
            _rapid_click_stroke(points, PainterOptions(), mouse_controller=controller)

        self.assertEqual(stroke.call_count, 1)

    def test_real_chunk_orchestration_paints_all_ten_points(self):
        points = [(index, 0) for index in range(10)]
        controller = make_controller()

        with patch("heartopia_painter.paint.random.randint", side_effect=[3, 2, 4, 5]), patch(
            "heartopia_painter.paint.random.uniform", return_value=0.04
        ), patch("heartopia_painter.paint._interruptible_sleep", return_value=True), patch(
            "heartopia_painter.enhanced_paint.PYAUTOGUI_AVAILABLE", False
        ), patch("heartopia_painter.enhanced_paint.random.uniform", return_value=0.12), patch(
            "heartopia_painter.enhanced_paint.random.random", return_value=1.0
        ):
            _rapid_click_stroke(points, PainterOptions(), mouse_controller=controller)

        self.assertEqual([point for point in points if point not in controller.hardware_mouse.painted], [])
        self.assertEqual(
            sum(command[0] == "DOWN" for command in controller.hardware_mouse.commands),
            4,
        )
        self.assertFalse(controller.hardware_mouse.button_down)


if __name__ == "__main__":
    unittest.main()
