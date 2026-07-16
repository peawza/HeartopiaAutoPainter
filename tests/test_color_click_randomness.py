import sys
import unittest
from unittest.mock import call, patch

sys.path.insert(0, "src")

from heartopia_painter.config import AppConfig, MainColor, ShadeButton
from heartopia_painter.paint import (
    COLOR_CLICK_RANDOMNESS_PX,
    GLOBAL_BUTTON_RANDOMNESS_PX,
    PainterOptions,
    _randomize_color_click_pos,
    _randomize_global_button_pos,
    _select_shade,
    _last_color_click_positions,
)


class TestColorClickRandomness(unittest.TestCase):
    def setUp(self):
        _last_color_click_positions.clear()

    @patch("heartopia_painter.paint.random.randint")
    def test_randomized_position_supports_full_range(self, randint_mock):
        limit = COLOR_CLICK_RANDOMNESS_PX
        randint_mock.side_effect = [-limit, -limit, 0, 0, limit, limit]

        self.assertEqual(_randomize_color_click_pos((100, 200)), (100 - limit, 200 - limit))
        self.assertEqual(_randomize_color_click_pos((100, 200)), (100, 200))
        self.assertEqual(_randomize_color_click_pos((100, 200)), (100 + limit, 200 + limit))
        self.assertEqual(
            randint_mock.call_args_list,
            [call(-limit, limit), call(-limit, limit)] * 3,
        )

    @patch("heartopia_painter.paint.random.randint", return_value=0)
    def test_color_click_never_reuses_the_previous_point(self, randint_mock):
        first = _randomize_color_click_pos((1740, 302))
        second = _randomize_color_click_pos((1740, 302))

        self.assertEqual(first, (1740, 302))
        self.assertNotEqual(second, first)
        self.assertLessEqual(abs(second[0] - 1740), 10)
        self.assertLessEqual(abs(second[1] - 302), 10)
        self.assertEqual(randint_mock.call_count, 18)

    @patch("heartopia_painter.paint.random.randint")
    def test_global_button_randomness_supports_full_range(self, randint_mock):
        limit = GLOBAL_BUTTON_RANDOMNESS_PX
        randint_mock.side_effect = [-limit, -limit, 0, 0, limit, limit]

        self.assertEqual(_randomize_global_button_pos((100, 200)), (100 - limit, 200 - limit))
        self.assertEqual(_randomize_global_button_pos((100, 200)), (100, 200))
        self.assertEqual(_randomize_global_button_pos((100, 200)), (100 + limit, 200 + limit))
        self.assertEqual(
            randint_mock.call_args_list,
            [call(-limit, limit), call(-limit, limit)] * 3,
        )

    @patch("heartopia_painter.paint._tap")
    @patch("heartopia_painter.paint.random.randint")
    def test_select_shade_randomizes_main_and_each_shade_tap_only(self, randint_mock, tap_mock):
        randint_mock.side_effect = [-5, 5, 10, -10, 0, 0, -10, 10, 0, 0]
        options = PainterOptions()
        main = MainColor(name="main", pos=(100, 200), rgb=(1, 2, 3))
        shade = ShadeButton(name="shade", pos=(300, 400), rgb=(4, 5, 6))
        cfg = AppConfig(
            back_button_pos=(10, 20),
            shades_panel_button_pos=(30, 40),
            main_colors=[main],
        )

        result = _select_shade(
            cfg,
            options,
            main,
            shade,
            last_main=None,
            last_shade=None,
            in_shades_panel=False,
        )

        self.assertEqual(result, (main, shade, True))
        self.assertEqual(
            tap_mock.call_args_list,
            [
                call((5, 25), options, mouse_controller=None),
                call((110, 190), options, mouse_controller=None),
                call((30, 40), options, extra_delay_s=options.panel_open_delay_s, mouse_controller=None),
                call((290, 410), options, extra_delay_s=options.shade_select_delay_s, mouse_controller=None),
                call((300, 400), options, extra_delay_s=0.0, mouse_controller=None),
            ],
        )

    @patch("heartopia_painter.paint._tap")
    @patch("heartopia_painter.paint.random.randint")
    def test_select_shade_hardware_mode_uses_button_specific_bounds(self, randint_mock, tap_mock):
        randint_mock.side_effect = [-5, 5, 10, -10, 0, 0, -10, 10, 0, 0]
        options = PainterOptions(use_hardware_mouse=True)
        main = MainColor(name="main", pos=(100, 200), rgb=(1, 2, 3))
        shade = ShadeButton(name="shade", pos=(300, 400), rgb=(4, 5, 6))
        cfg = AppConfig(
            back_button_pos=(10, 20),
            shades_panel_button_pos=(30, 40),
            main_colors=[main],
        )

        result = _select_shade(
            cfg,
            options,
            main,
            shade,
            last_main=None,
            last_shade=None,
            in_shades_panel=False,
        )

        self.assertEqual(result, (main, shade, True))
        self.assertEqual(
            tap_mock.call_args_list,
            [
                call((5, 25), options, mouse_controller=None),
                call((110, 190), options, mouse_controller=None),
                call((30, 40), options, extra_delay_s=options.panel_open_delay_s, mouse_controller=None),
                call((290, 410), options, extra_delay_s=options.shade_select_delay_s, mouse_controller=None),
                call((300, 400), options, extra_delay_s=0.0, mouse_controller=None),
            ],
        )


if __name__ == "__main__":
    unittest.main()
