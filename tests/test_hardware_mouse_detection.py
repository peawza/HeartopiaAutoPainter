import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, "src")

from heartopia_painter.hardware_mouse import HardwareMouse, HardwareMouseConfig


def make_port(device, vid, pid, description="USB Serial Device", manufacturer=None):
    return SimpleNamespace(
        device=device,
        vid=vid,
        pid=pid,
        description=description,
        manufacturer=manufacturer,
    )


def test_auto_detects_spoofed_logitech_leonardo():
    port = make_port("COM6", 0x046D, 0xC07D)
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() == "COM6"


def test_auto_detects_standard_leonardo():
    port = make_port("COM7", 0x2341, 0x8036)
    mouse = HardwareMouse(HardwareMouseConfig())

    with patch("heartopia_painter.hardware_mouse.serial.tools.list_ports.comports", return_value=[port]):
        assert mouse._auto_detect_port() == "COM7"
