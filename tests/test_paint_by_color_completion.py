import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, "src")

from heartopia_painter.config import AppConfig, MainColor, ShadeButton
from heartopia_painter.paint import PainterOptions, paint_grid


class TestPaintByColorCompletion(unittest.TestCase):
    def _cfg(self) -> AppConfig:
        red = MainColor(
            name="red",
            pos=(10, 10),
            rgb=(255, 0, 0),
            shades=[ShadeButton(name="red-1", pos=(11, 11), rgb=(255, 0, 0))],
        )
        blue = MainColor(
            name="blue",
            pos=(20, 20),
            rgb=(0, 0, 255),
            shades=[ShadeButton(name="blue-1", pos=(21, 21), rgb=(0, 0, 255))],
        )
        return AppConfig(
            main_colors=[red, blue],
            shades_panel_button_pos=(100, 100),
            back_button_pos=(101, 101),
            paint_tool_button_pos=(102, 102),
            bucket_tool_button_pos=(103, 103),
            paint_mode="color",
            bucket_fill_enabled=True,
            bucket_fill_min_cells=2,
            bucket_fill_regions_enabled=False,
            verify_streaming_enabled=False,
            row_delay_s=0,
        )

    def test_bucket_fill_first_color_continues_to_remaining_colors(self):
        cfg = self._cfg()
        pixels = [(255, 0, 0), (255, 0, 0), (0, 0, 255)]
        progress = []
        selected = []

        def get_pixel(x, y):
            return pixels[x]

        def select_shade(**kwargs):
            selected.append((kwargs["main"].name, kwargs["shade"].name))
            return kwargs["main"], kwargs["shade"], True

        with patch("heartopia_painter.paint._create_mouse_controller", return_value=None), patch(
            "heartopia_painter.paint._tap"
        ), patch("heartopia_painter.paint._bucket_fill_canvas_with_shade"), patch(
            "heartopia_painter.paint._select_shade", side_effect=select_shade
        ), patch("heartopia_painter.paint._verify_and_repair_color_group"), patch(
            "heartopia_painter.paint.get_screen_pixel_rgb", return_value=(255, 0, 0)
        ):
            completed = paint_grid(
                cfg=cfg,
                canvas_rect=(0, 0, 30, 10),
                grid_w=3,
                grid_h=1,
                get_pixel=get_pixel,
                options=PainterOptions(row_delay_s=0),
                paint_mode="color",
                progress_cb=lambda x, y: progress.append((x, y)),
            )

        self.assertTrue(completed)
        self.assertEqual(progress[:2], [(0, 0), (1, 0)])
        self.assertEqual(set(progress), {(0, 0), (1, 0), (2, 0)})
        self.assertIn(("blue", "blue-1"), selected)

    def test_stop_after_bucket_fill_reports_incomplete(self):
        cfg = self._cfg()
        pixels = [(255, 0, 0), (255, 0, 0), (0, 0, 255)]
        progress = []
        selected = []

        def get_pixel(x, y):
            return pixels[x]

        def should_stop():
            return len(progress) >= 2

        def select_shade(**kwargs):
            selected.append((kwargs["main"].name, kwargs["shade"].name))
            return kwargs["main"], kwargs["shade"], True

        with patch("heartopia_painter.paint._create_mouse_controller", return_value=None), patch(
            "heartopia_painter.paint._tap"
        ), patch("heartopia_painter.paint._bucket_fill_canvas_with_shade"), patch(
            "heartopia_painter.paint._select_shade", side_effect=select_shade
        ), patch("heartopia_painter.paint._verify_and_repair_color_group"), patch(
            "heartopia_painter.paint.get_screen_pixel_rgb", return_value=(255, 0, 0)
        ):
            completed = paint_grid(
                cfg=cfg,
                canvas_rect=(0, 0, 30, 10),
                grid_w=3,
                grid_h=1,
                get_pixel=get_pixel,
                options=PainterOptions(row_delay_s=0),
                paint_mode="color",
                progress_cb=lambda x, y: progress.append((x, y)),
                should_stop=should_stop,
            )

        self.assertFalse(completed)
        self.assertEqual(set(progress), {(0, 0), (1, 0)})
        self.assertNotIn(("blue", "blue-1"), selected)


if __name__ == "__main__":
    unittest.main()
