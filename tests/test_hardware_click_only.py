from __future__ import annotations

from unittest.mock import MagicMock, patch

import main
import pytest

from src.heartopia_painter.enhanced_paint import (
    HardwareMouseError,
    MouseController,
    enhanced_stroke,
    enhanced_tap,
)
from src.heartopia_painter.paint import PainterOptions, _click_target, _create_mouse_controller


class FakeHardwareClick:
    def __init__(self):
        self.commands = []
        self.connected = True

    def press(self):
        self.commands.append("D")

    def release(self):
        self.commands.append("U")

    def disconnect(self):
        self.commands.append("DISCONNECT")


class FakeHardwareMove(FakeHardwareClick):
    def __init__(self, fail_on_move=None):
        super().__init__()
        self.moves = []
        self.fail_on_move = fail_on_move

    def move(self, dx, dy):
        self.moves.append((dx, dy))
        if self.fail_on_move is not None and len(self.moves) == self.fail_on_move:
            raise RuntimeError("movement failed")
        return True


def make_hardware_controller(device):
    controller = MouseController.__new__(MouseController)
    controller.use_hardware = True
    controller.hardware_mouse = device
    controller.hardware_click = None
    controller.use_hardware_click = False
    controller.delay_system = MagicMock()
    controller.delay_system.apply_position_jitter.side_effect = lambda x, y: (x, y)
    controller.delay_system.calculate_movement_duration.return_value = 0.0
    controller.delay_system.calculate_movement_steps.return_value = 1
    controller.delay_system.generate_bezier_curve.side_effect = (
        lambda sx, sy, ex, ey, steps, velocity_profile=None: [(sx, sy), (ex, ey)]
    )
    controller.delay_system.get_step_delay.return_value = 0.0
    controller.delay_system.should_micro_pause.return_value = False
    controller.delay_system.interruptible_sleep.return_value = True
    controller._current_x = 0
    controller._current_y = 0
    return controller


def test_hardware_click_only_moves_with_software_and_sends_only_press_release():
    click_device = FakeHardwareClick()
    delay_system = MagicMock()
    delay_system.apply_position_jitter.return_value = (100, 200)

    controller = MouseController(
        use_hardware=False,
        hardware_click=click_device,
        delay_system=delay_system,
        fallback_to_software=False,
    )

    with patch("src.heartopia_painter.enhanced_paint.pyautogui.moveTo") as move_to:
        controller.move_to(100, 200)
        controller.press()
        controller.release()

    move_to.assert_called_once_with(100, 200)
    assert click_device.commands == ["D", "U"]


def test_hardware_click_releases_after_click_error():
    click_device = FakeHardwareClick()
    controller = MouseController(
        use_hardware=False,
        hardware_click=click_device,
        delay_system=MagicMock(),
        fallback_to_software=False,
    )

    with patch(
        "src.heartopia_painter.enhanced_paint.time.sleep",
        side_effect=RuntimeError("test click failure"),
    ):
        try:
            controller.click()
        except RuntimeError:
            pass

    assert click_device.commands == ["D", "U"]


def test_enhanced_tap_releases_after_hold_error():
    click_device = FakeHardwareClick()
    delay_system = MagicMock()
    delay_system.should_micro_pause.return_value = False
    delay_system.interruptible_sleep.return_value = True
    controller = MouseController(
        use_hardware=False,
        hardware_click=click_device,
        delay_system=delay_system,
        fallback_to_software=False,
    )
    controller.move_along_curve = MagicMock()

    with patch(
        "src.heartopia_painter.enhanced_paint.time.sleep",
        side_effect=RuntimeError("test hold failure"),
    ):
        try:
            enhanced_tap(controller, (100, 200))
        except RuntimeError:
            pass

    assert click_device.commands == ["D", "U"]


def test_hardware_click_failure_does_not_fallback_to_software():
    click_device = FakeHardwareClick()
    click_device.press = MagicMock(side_effect=RuntimeError("ESP disconnected"))
    controller = MouseController(
        use_hardware=False,
        hardware_click=click_device,
        delay_system=MagicMock(),
        fallback_to_software=False,
    )

    with patch("src.heartopia_painter.enhanced_paint.pyautogui.mouseDown") as mouse_down:
        with pytest.raises(RuntimeError, match="ESP disconnected"):
            controller.press()

    mouse_down.assert_not_called()


def test_disconnected_hardware_click_is_rejected_before_press():
    click_device = FakeHardwareClick()
    click_device.connected = False
    controller = MouseController(
        use_hardware=False,
        hardware_click=click_device,
        delay_system=MagicMock(),
        fallback_to_software=False,
    )

    with patch("src.heartopia_painter.enhanced_paint.pyautogui.mouseDown") as mouse_down:
        with pytest.raises(HardwareMouseError):
            controller.press()

    mouse_down.assert_not_called()
    assert click_device.commands == []


def test_hardware_click_controller_creation_failure_is_fatal():
    options = PainterOptions(hardware_click_only=True, hardware_mouse_port="COM6")

    with patch(
        "src.heartopia_painter.delays.DelaySystem",
        side_effect=RuntimeError("test controller failure"),
    ), pytest.raises(RuntimeError, match="test controller failure"):
        _create_mouse_controller(options)


def test_hardware_click_mode_disables_click_randomness_only_for_that_mode():
    precise = PainterOptions(hardware_click_only=True)
    normal = PainterOptions(hardware_click_only=False)
    randomizer = MagicMock(return_value=(101, 201))

    assert _click_target((100, 200), precise, randomizer) == (100, 200)
    randomizer.assert_not_called()
    assert _click_target((100, 200), normal, randomizer) == (101, 201)
    randomizer.assert_called_once_with((100, 200))


def test_hardware_mouse_mode_uses_exact_ui_click_targets():
    precise = PainterOptions(use_hardware_mouse=True)
    randomizer = MagicMock(return_value=(101, 201))

    assert _click_target((100, 200), precise, randomizer) == (100, 200)
    randomizer.assert_not_called()


def test_hardware_curve_tracks_latest_relative_position():
    device = FakeHardwareMove()
    controller = make_hardware_controller(device)

    controller.move_along_curve((0, 0), (100, 0))
    controller.move_along_curve((100, 0), (100, 100))

    assert device.moves == [(100, 0), (0, 100)]
    assert controller.get_current_position() == (100, 100)


def test_enhanced_stroke_releases_after_movement_failure():
    device = FakeHardwareMove(fail_on_move=2)
    controller = make_hardware_controller(device)

    with pytest.raises(RuntimeError, match="movement failed"):
        enhanced_stroke([(10, 10), (20, 10)], controller)

    assert device.commands == ["D", "U"]


def test_main_dispatches_hardware_click_gui_override():
    with patch("main._run_gui") as run_gui:
        result = main.main(["--hardware-click", "--port", "COM6", "--baudrate", "57600"])

    assert result == 0
    run_gui.assert_called_once_with(
        hardware_click=True,
        port="COM6",
        baudrate=57600,
    )
